"""Factory for persistent ChromaDB clients. Isolated so tests can swap the constructor."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chromadb.api import ClientAPI


def create_persistent_client(persist_dir: Path) -> ClientAPI:
    """Create a persistent Chroma client rooted at `persist_dir`.

    Imported lazily to keep unit-test startup fast (Chroma pulls in a lot).
    """
    import chromadb
    from chromadb.config import Settings

    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(persist_dir),
        settings=Settings(anonymized_telemetry=False, allow_reset=True),
    )
