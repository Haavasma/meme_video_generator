"""Scrape myinstants.com search results and ingest sounds into the `sounds` collection.

Parses the rendered HTML of `/en/search/?name=QUERY[&page=N]`. Each sound row has:

  <button class="small-button"
          onclick="play('/media/sounds/FILE.mp3', 'loader-N', 'SLUG')"
          title="Play NAME sound" />
  <a href="/en/instant/SLUG/" class="instant-link link-secondary">DISPLAY NAME</a>

The slug, display name, and mp3 path are extracted. The mp3 is downloaded to
`download_dir` and the resulting Sound record is upserted via the Repository.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
from bs4 import BeautifulSoup, Tag

from kb.constants import COLLECTION_SOUNDS
from kb.ingestors.base import BaseIngestor, IngestResult
from kb.models import Sound

if TYPE_CHECKING:
    from kb.store import Repository

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.myinstants.com"
_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) meme-video-generator/0.1"
)
# Captures the three args of the inline onclick="play('...', '...', '...')"
_PLAY_RE = re.compile(r"play\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*\)")


@dataclass(frozen=True)
class _SoundRow:
    """Intermediate record parsed from one <button class="small-button"> element."""

    display_name: str
    slug: str
    mp3_path: str  # relative, e.g. /media/sounds/vine-boom.mp3

    @property
    def mp3_url(self) -> str:
        return f"{_BASE_URL}{self.mp3_path}"

    @property
    def instant_url(self) -> str:
        return f"{_BASE_URL}/en/instant/{self.slug}/"

    @property
    def filename(self) -> str:
        return Path(self.mp3_path).name


class MyInstantsIngestor(BaseIngestor):
    """Scrape + download + upsert sounds from myinstants.com.

    Politeness: sleeps `request_delay` between requests. Respects `max_items`
    to cap total downloads. Skips download if target file already on disk.
    """

    def __init__(
        self,
        *,
        repository: Repository,
        query: str,
        download_dir: Path,
        max_items: int = 50,
        request_delay: float = 1.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        if max_items <= 0:
            raise ValueError("max_items must be positive")
        if not download_dir.exists():
            download_dir.mkdir(parents=True, exist_ok=True)
        self._repo = repository
        self._query = query
        self._download_dir = download_dir
        self._max_items = max_items
        self._delay = request_delay
        self._owned_client = http_client is None
        self._client = http_client or httpx.Client(
            headers={"User-Agent": _USER_AGENT},
            timeout=30.0,
            follow_redirects=True,
        )

    def ingest(self) -> list[IngestResult]:
        try:
            rows = self._scrape_search_rows()
            results: list[IngestResult] = []
            for row in rows[: self._max_items]:
                try:
                    result = self._ingest_row(row)
                except Exception:  # noqa: BLE001 - one bad row shouldn't abort batch
                    logger.exception("Failed ingesting %s", row.slug)
                    continue
                results.append(result)
            return results
        finally:
            if self._owned_client:
                self._client.close()

    # --- internals ---------------------------------------------------------

    def _scrape_search_rows(self) -> list[_SoundRow]:
        """Walk paginated search results until we have enough rows (or run out)."""
        rows: list[_SoundRow] = []
        page = 1
        while len(rows) < self._max_items:
            html = self._fetch_search_page(page)
            new_rows = _parse_search_rows(html)
            if not new_rows:
                break
            rows.extend(new_rows)
            page += 1
            # Politeness between page fetches.
            if self._delay > 0:
                time.sleep(self._delay)
        return rows

    def _fetch_search_page(self, page: int) -> str:
        params: dict[str, str | int] = {"name": self._query}
        if page > 1:
            params["page"] = page
        resp = self._client.get(f"{_BASE_URL}/en/search/", params=params)
        resp.raise_for_status()
        return resp.text

    def _ingest_row(self, row: _SoundRow) -> IngestResult:
        dest = self._download_dir / row.filename
        if not dest.exists():
            self._download(row.mp3_url, dest)
            if self._delay > 0:
                time.sleep(self._delay)
        description = _build_description(row)
        size = dest.stat().st_size
        sound = Sound(
            id=_stable_id("snd", row.slug),
            description=description,
            local_path=str(dest.resolve()),
            source_url=row.instant_url,
            duration_sec=0.0,  # unknown without probing — downstream can enrich later
            tags=_slug_tags(row.slug),
            format="mp3",
            file_size_bytes=size,
        )
        self._repo.add_sound(sound)
        return IngestResult(
            entry_id=sound.id,
            collection=COLLECTION_SOUNDS,
            description=description,
        )

    def _download(self, url: str, dest: Path) -> None:
        with self._client.stream("GET", url) as resp:
            resp.raise_for_status()
            with dest.open("wb") as f:
                for chunk in resp.iter_bytes():
                    f.write(chunk)


# --- HTML parsing helpers --------------------------------------------------


def _parse_search_rows(html: str) -> list[_SoundRow]:
    soup = BeautifulSoup(html, "html.parser")
    rows: list[_SoundRow] = []
    for button in soup.select("button.small-button"):
        if not isinstance(button, Tag):
            continue
        onclick = button.get("onclick") or ""
        match = _PLAY_RE.search(str(onclick))
        if not match:
            continue
        mp3_path, _loader_id, slug = match.groups()
        display_name = _find_sibling_display_name(button) or slug.replace("-", " ")
        rows.append(_SoundRow(display_name=display_name, slug=slug, mp3_path=mp3_path))
    return rows


def _find_sibling_display_name(button: Tag) -> str | None:
    # Walk up to the container; find the nearest a.instant-link.
    container = button.find_parent(class_="instant")
    if container is None:
        # Fall back to the parent of small-button — search forward.
        container = button.parent
    if container is None:
        return None
    link = container.select_one("a.instant-link")
    if link is None:
        return None
    text = link.get_text(strip=True)
    return text or None


def _build_description(row: _SoundRow) -> str:
    """Rich description = display name + slug-derived keywords, joined."""
    tags = _slug_tags(row.slug)
    # De-dup while preserving order.
    seen: set[str] = set()
    parts = [row.display_name]
    for t in tags:
        if t.lower() not in row.display_name.lower() and t not in seen:
            parts.append(t)
            seen.add(t)
    return " ".join(parts).strip()


def _slug_tags(slug: str) -> list[str]:
    # Strip trailing numeric suffixes ("-34956") and split on hyphens.
    cleaned = re.sub(r"-\d+$", "", slug)
    return [w for w in cleaned.split("-") if w and not w.isdigit()]


def _stable_id(prefix: str, slug: str) -> str:
    return f"{prefix}_{slug}"
