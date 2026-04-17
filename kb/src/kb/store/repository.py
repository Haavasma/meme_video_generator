"""Repository pattern over ChromaDB collections for sounds + templates."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from kb.constants import ALL_COLLECTIONS, COLLECTION_SOUNDS, COLLECTION_TEMPLATES
from kb.embeddings import Embedder
from kb.models import Sound, Template
from kb.store.chroma_client import create_persistent_client

if TYPE_CHECKING:
    from chromadb.api import ClientAPI
    from chromadb.api.models.Collection import Collection

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QueryResult:
    """Flattened query hit. Returned as dict from Repository.query for easy JSON serialization."""

    id: str
    description: str
    metadata: dict[str, Any]
    distance: float


class Repository:
    """Thin wrapper around a Chroma client exposing domain-aware add/query/list/delete/stats."""

    def __init__(self, client: ClientAPI, embedder: Embedder) -> None:
        self._client = client
        self._embedder = embedder
        # Eagerly create both collections so counts are always defined.
        self._collections: dict[str, Collection] = {
            name: client.get_or_create_collection(name) for name in ALL_COLLECTIONS
        }

    # --- construction -------------------------------------------------------

    @classmethod
    def create(cls, *, persist_dir: Path, embedder: Embedder) -> Repository:
        return cls(client=create_persistent_client(persist_dir), embedder=embedder)

    # --- domain adds --------------------------------------------------------

    def add_sound(self, sound: Sound) -> None:
        self._upsert(
            COLLECTION_SOUNDS,
            id=sound.id,
            document=sound.description,
            metadata=dict(sound.to_chroma_metadata()),
        )

    def add_template(self, template: Template) -> None:
        self._upsert(
            COLLECTION_TEMPLATES,
            id=template.id,
            document=template.description,
            metadata=dict(template.to_chroma_metadata()),
        )

    # --- queries ------------------------------------------------------------

    def query(
        self, collection: str, *, query_text: str, top_k: int = 5
    ) -> list[dict[str, Any]]:
        coll = self._require_collection(collection)
        (embedding,) = self._embedder.embed([query_text])
        raw = coll.query(query_embeddings=[embedding], n_results=top_k)
        return _flatten_query_result(raw)

    def list_all(
        self, collection: str, *, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        coll = self._require_collection(collection)
        raw = coll.get(limit=limit, offset=offset)
        return _flatten_get_result(raw)

    def delete(self, collection: str, entry_id: str) -> None:
        coll = self._require_collection(collection)
        coll.delete(ids=[entry_id])

    def reset(self, collection: str) -> None:
        """Drop all entries in `collection` but keep the collection itself."""
        self._require_collection(collection)  # validate name
        self._client.delete_collection(collection)
        self._collections[collection] = self._client.get_or_create_collection(collection)

    def stats(self) -> dict[str, int]:
        return {name: coll.count() for name, coll in self._collections.items()}

    # --- internal -----------------------------------------------------------

    def _require_collection(self, name: str) -> Collection:
        if name not in self._collections:
            raise ValueError(
                f"Unknown collection: {name!r}. Expected one of {ALL_COLLECTIONS}."
            )
        return self._collections[name]

    def _upsert(
        self,
        collection: str,
        *,
        id: str,
        document: str,
        metadata: dict[str, Any],
    ) -> None:
        coll = self._require_collection(collection)
        (embedding,) = self._embedder.embed([document])
        coll.upsert(
            ids=[id],
            documents=[document],
            metadatas=[metadata],
            embeddings=[embedding],
        )


# --- helpers to normalize Chroma's response shape ---------------------------


def _flatten_query_result(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Chroma returns parallel lists keyed by result row. We took one query, so index [0]."""
    ids = (raw.get("ids") or [[]])[0]
    docs = (raw.get("documents") or [[]])[0]
    metas = (raw.get("metadatas") or [[]])[0]
    dists = (raw.get("distances") or [[]])[0]
    out: list[dict[str, Any]] = []
    for i, entry_id in enumerate(ids):
        out.append({
            "id": entry_id,
            "description": docs[i] if i < len(docs) else "",
            "metadata": dict(metas[i]) if i < len(metas) and metas[i] else {},
            "distance": float(dists[i]) if i < len(dists) else 0.0,
        })
    return out


def _flatten_get_result(raw: dict[str, Any]) -> list[dict[str, Any]]:
    ids = raw.get("ids") or []
    docs = raw.get("documents") or []
    metas = raw.get("metadatas") or []
    out: list[dict[str, Any]] = []
    for i, entry_id in enumerate(ids):
        out.append({
            "id": entry_id,
            "description": docs[i] if i < len(docs) else "",
            "metadata": dict(metas[i]) if i < len(metas) and metas[i] else {},
        })
    return out
