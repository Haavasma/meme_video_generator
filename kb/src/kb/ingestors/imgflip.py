"""Scrape imgflip.com/memetemplates and ingest static meme templates.

Listing structure (one template per `.mt-box`):

  <div class="mt-box">
    <h3 class="mt-title">
      <a title="Drake Hotline Bling Meme" href="/meme/Drake-Hotline-Bling">Drake Hotline Bling</a>
    </h3>
    <div class="mt-img-wrap">
      <a href="/meme/Drake-Hotline-Bling">
        <img class="shadow" src="//i.imgflip.com/4/30b1gx.jpg" alt="Drake Hotline Bling Meme Template"/>
      </a>
    </div>
  </div>

Image URLs are protocol-relative — we coerce to https. The thumbnail on the listing
page is only 150px tall; for v1 that's enough (templates are small anyway), but a
follow-up can fetch the detail page for higher-res + description blurb.
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
from PIL import Image

from kb.constants import COLLECTION_TEMPLATES
from kb.ingestors.base import BaseIngestor, IngestResult
from kb.models import Template

if TYPE_CHECKING:
    from kb.store import Repository

logger = logging.getLogger(__name__)

_BASE_URL = "https://imgflip.com"
_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) meme-video-generator/0.1"
)

_SUPPORTED_IMG_EXTS = {"jpg", "jpeg", "png", "webp"}


@dataclass(frozen=True)
class _TemplateRow:
    """One template parsed from a `.mt-box` element."""

    display_name: str
    slug: str  # URL-style, e.g. Drake-Hotline-Bling
    image_url: str
    detail_url: str

    @property
    def filename(self) -> str:
        return Path(self.image_url).name


class ImgflipIngestor(BaseIngestor):
    """Scrape + download + upsert meme templates from imgflip.com."""

    def __init__(
        self,
        *,
        repository: Repository,
        download_dir: Path,
        max_items: int = 50,
        request_delay: float = 1.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        if max_items <= 0:
            raise ValueError("max_items must be positive")
        download_dir.mkdir(parents=True, exist_ok=True)
        self._repo = repository
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
            rows = self._scrape_listing_rows()
            results: list[IngestResult] = []
            for row in rows[: self._max_items]:
                try:
                    results.append(self._ingest_row(row))
                except Exception:  # noqa: BLE001 - one bad row shouldn't abort batch
                    logger.exception("Failed ingesting %s", row.slug)
                    continue
            return results
        finally:
            if self._owned_client:
                self._client.close()

    # --- internals ---------------------------------------------------------

    def _scrape_listing_rows(self) -> list[_TemplateRow]:
        rows: list[_TemplateRow] = []
        page = 1
        while len(rows) < self._max_items:
            html = self._fetch_listing_page(page)
            new_rows = _parse_listing_rows(html)
            if not new_rows:
                break
            rows.extend(new_rows)
            page += 1
            if self._delay > 0:
                time.sleep(self._delay)
        return rows

    def _fetch_listing_page(self, page: int) -> str:
        url = f"{_BASE_URL}/memetemplates"
        params: dict[str, str | int] = {}
        if page > 1:
            params["page"] = page
        resp = self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.text

    def _ingest_row(self, row: _TemplateRow) -> IngestResult:
        dest = self._download_dir / row.filename
        if not dest.exists():
            self._download(row.image_url, dest)
            if self._delay > 0:
                time.sleep(self._delay)
        width, height = _probe_image(dest)
        size = dest.stat().st_size
        ext = Path(dest).suffix.lower().lstrip(".")
        if ext not in _SUPPORTED_IMG_EXTS:
            raise ValueError(f"unsupported image extension: {ext}")
        description = row.display_name
        template = Template(
            id=f"tpl_{row.slug}",
            description=description,
            local_path=str(dest.resolve()),
            source_url=row.detail_url,
            tags=_slug_tags(row.slug),
            media_type=ext,  # type: ignore[arg-type]
            width=width,
            height=height,
            file_size_bytes=size,
        )
        self._repo.add_template(template)
        return IngestResult(
            entry_id=template.id,
            collection=COLLECTION_TEMPLATES,
            description=description,
        )

    def _download(self, url: str, dest: Path) -> None:
        with self._client.stream("GET", url) as resp:
            resp.raise_for_status()
            with dest.open("wb") as f:
                for chunk in resp.iter_bytes():
                    f.write(chunk)


# --- parsing helpers -------------------------------------------------------


def _parse_listing_rows(html: str) -> list[_TemplateRow]:
    soup = BeautifulSoup(html, "html.parser")
    rows: list[_TemplateRow] = []
    for box in soup.select("div.mt-box"):
        if not isinstance(box, Tag):
            continue
        title_anchor = box.select_one("h3.mt-title a")
        img = box.select_one("img")
        if not isinstance(title_anchor, Tag) or not isinstance(img, Tag):
            continue
        href = str(title_anchor.get("href") or "")
        display_name = title_anchor.get_text(strip=True)
        img_src = str(img.get("src") or "")
        if not (href and display_name and img_src):
            continue
        slug = href.rsplit("/", 1)[-1]
        image_url = _coerce_scheme(img_src)
        detail_url = f"{_BASE_URL}{href}" if href.startswith("/") else href
        rows.append(
            _TemplateRow(
                display_name=display_name,
                slug=slug,
                image_url=image_url,
                detail_url=detail_url,
            )
        )
    return rows


def _coerce_scheme(url: str) -> str:
    if url.startswith("//"):
        return f"https:{url}"
    if url.startswith("http"):
        return url
    return f"{_BASE_URL}{url}"


def _slug_tags(slug: str) -> list[str]:
    return [w.lower() for w in re.split(r"[-_]+", slug) if w]


def _probe_image(path: Path) -> tuple[int, int]:
    with Image.open(path) as img:
        return img.size
