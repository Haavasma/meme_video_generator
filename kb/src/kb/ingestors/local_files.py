"""LocalFileIngestor — walk a directory and ingest audio or image files into the KB."""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

from kb.constants import COLLECTION_SOUNDS, COLLECTION_TEMPLATES
from kb.ingestors.base import BaseIngestor, IngestResult
from kb.models import Sound, Template

if TYPE_CHECKING:
    from kb.store import Repository

logger = logging.getLogger(__name__)

_AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".m4a"}
_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


class LocalFileIngestor(BaseIngestor):
    """Walk `root` and ingest files matching the collection's expected file types.

    - `sounds` collection: `.mp3/.wav/.ogg/.m4a`
    - `templates` collection: `.jpg/.jpeg/.png/.webp`
    """

    def __init__(self, *, repository: Repository, collection: str, root: Path) -> None:
        if collection not in (COLLECTION_SOUNDS, COLLECTION_TEMPLATES):
            raise ValueError(
                f"LocalFileIngestor supports collections "
                f"{COLLECTION_SOUNDS}/{COLLECTION_TEMPLATES}, got {collection!r}."
            )
        if not root.exists() or not root.is_dir():
            raise FileNotFoundError(f"root must be an existing directory: {root}")
        self._repo = repository
        self._collection = collection
        self._root = root

    def ingest(self) -> list[IngestResult]:
        results: list[IngestResult] = []
        extensions = _AUDIO_EXTS if self._collection == COLLECTION_SOUNDS else _IMAGE_EXTS
        for path in sorted(self._root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in extensions:
                continue
            try:
                result = self._ingest_one(path)
            except Exception:
                logger.exception("Failed to ingest %s", path)
                continue
            results.append(result)
        return results

    # --- internals ----------------------------------------------------------

    def _ingest_one(self, path: Path) -> IngestResult:
        description = _filename_to_description(path.stem)
        # Stable ID from absolute path — reingest of same file is an upsert, not dup.
        entry_id = _stable_id(prefix=self._collection[:3], text=str(path.resolve()))
        size = path.stat().st_size
        source_url = path.resolve().as_uri()

        if self._collection == COLLECTION_SOUNDS:
            audio_fmt = path.suffix.lower().lstrip(".")
            self._repo.add_sound(
                Sound(
                    id=entry_id,
                    description=description,
                    local_path=str(path.resolve()),
                    source_url=source_url,
                    duration_sec=_probe_audio_duration(path),
                    tags=_tags_from_stem(path.stem),
                    format=audio_fmt,  # type: ignore[arg-type]  # validated by Pydantic
                    file_size_bytes=size,
                )
            )
        else:
            img_fmt = path.suffix.lower().lstrip(".")
            width, height = _probe_image_dims(path)
            self._repo.add_template(
                Template(
                    id=entry_id,
                    description=description,
                    local_path=str(path.resolve()),
                    source_url=source_url,
                    tags=_tags_from_stem(path.stem),
                    media_type=img_fmt,  # type: ignore[arg-type]
                    width=width,
                    height=height,
                    file_size_bytes=size,
                )
            )
        return IngestResult(entry_id=entry_id, collection=self._collection, description=description)


# --- helpers ---------------------------------------------------------------


def _filename_to_description(stem: str) -> str:
    """Turn `vine_boom-v2` → "vine boom v2". Good-enough default; callers can override."""
    cleaned = re.sub(r"[_\-.]+", " ", stem).strip()
    return cleaned or stem


def _tags_from_stem(stem: str) -> list[str]:
    """Best-effort tag extraction — each word in the cleaned stem becomes a tag."""
    return [w for w in re.split(r"[_\-.\s]+", stem.lower()) if w]


def _stable_id(*, prefix: str, text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8"), usedforsecurity=False).hexdigest()
    return f"{prefix}_{digest[:16]}"


def _probe_audio_duration(path: Path) -> float:
    """Return duration in seconds. Uses mutagen for mp3/ogg/m4a; wave stdlib for .wav."""
    suffix = path.suffix.lower()
    if suffix == ".wav":
        import wave

        with wave.open(str(path), "rb") as w:
            frames = w.getnframes()
            rate = w.getframerate()
            return frames / float(rate) if rate else 0.0
    # mutagen covers mp3/ogg/m4a
    from mutagen import File as MutagenFile

    audio = MutagenFile(str(path))
    if audio is None or audio.info is None:
        return 0.0
    return float(getattr(audio.info, "length", 0.0))


def _probe_image_dims(path: Path) -> tuple[int, int]:
    from PIL import Image

    with Image.open(path) as img:
        return img.size  # (width, height)
