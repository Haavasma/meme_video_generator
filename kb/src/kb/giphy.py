"""Runtime client for the Giphy Search API.

The meme-video skill calls this at render time (not at ingest time) to fetch
reaction GIFs dynamically. Responses are cached to a per-query JSON file so
repeated invocations don't burn the free-tier rate budget (42 req/hr).
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.giphy.com/v1/gifs/search"
_USER_AGENT = "meme-video-generator/0.1 (Giphy runtime client)"


@dataclass(frozen=True)
class GiphyHit:
    """A single Giphy search result — just the fields the skill needs."""

    id: str
    title: str
    slug: str
    page_url: str
    gif_url: str
    mp4_url: str | None
    preview_url: str | None
    width: int
    height: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GiphyClient:
    """Tiny caching wrapper around the Giphy Search API."""

    def __init__(
        self,
        *,
        api_key: str,
        cache_dir: Path,
        http_client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("Giphy API key is required (set GIPHY_API_KEY in .env)")
        cache_dir.mkdir(parents=True, exist_ok=True)
        self._api_key = api_key
        self._cache_dir = cache_dir
        self._owned_client = http_client is None
        self._client = http_client or httpx.Client(
            headers={"User-Agent": _USER_AGENT},
            timeout=30.0,
        )

    def search(self, query: str, *, limit: int = 5) -> list[GiphyHit]:
        """Return up to `limit` hits for `query`. Cached per (query, limit)."""
        cached = self._read_cache(query, limit)
        if cached is not None:
            return cached

        resp = self._client.get(
            _BASE_URL,
            params={
                "api_key": self._api_key,
                "q": query,
                "limit": limit,
                "rating": "pg-13",
                "lang": "en",
            },
        )
        resp.raise_for_status()
        payload = resp.json()
        hits = [_parse_hit(d) for d in payload.get("data", [])]
        self._write_cache(query, limit, hits)
        return hits

    def close(self) -> None:
        if self._owned_client:
            self._client.close()

    # --- caching -----------------------------------------------------------

    def _cache_key(self, query: str, limit: int) -> str:
        return hashlib.sha1(
            f"{query.strip().lower()}|{limit}".encode("utf-8"),
            usedforsecurity=False,
        ).hexdigest()[:16]

    def _cache_path(self, query: str, limit: int) -> Path:
        return self._cache_dir / f"{self._cache_key(query, limit)}.json"

    def _read_cache(self, query: str, limit: int) -> list[GiphyHit] | None:
        path = self._cache_path(query, limit)
        if not path.exists():
            return None
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            return [GiphyHit(**entry) for entry in raw]
        except (json.JSONDecodeError, TypeError):
            logger.warning("Corrupt Giphy cache at %s; ignoring", path)
            return None

    def _write_cache(self, query: str, limit: int, hits: list[GiphyHit]) -> None:
        self._cache_path(query, limit).write_text(
            json.dumps([h.to_dict() for h in hits], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _parse_hit(raw: dict[str, Any]) -> GiphyHit:
    images = raw.get("images", {}) or {}
    original = images.get("original", {}) or {}
    mp4 = images.get("original_mp4", {}) or {}
    preview = images.get("preview_gif", {}) or {}
    return GiphyHit(
        id=str(raw.get("id", "")),
        title=str(raw.get("title", "")).strip(),
        slug=str(raw.get("slug", "")),
        page_url=str(raw.get("url", "")),
        gif_url=str(original.get("url", "")),
        mp4_url=(mp4.get("mp4") or None),
        preview_url=(preview.get("url") or None),
        width=_to_int(original.get("width")),
        height=_to_int(original.get("height")),
    )


def _to_int(v: Any) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0
