"""Module-level constants — stable identifiers used across the kb package."""

from __future__ import annotations

from typing import Final

COLLECTION_SOUNDS: Final[str] = "sounds"
COLLECTION_TEMPLATES: Final[str] = "templates"

ALL_COLLECTIONS: Final[tuple[str, ...]] = (COLLECTION_SOUNDS, COLLECTION_TEMPLATES)

DEFAULT_EMBEDDING_MODEL: Final[str] = "sentence-transformers/all-MiniLM-L6-v2"
