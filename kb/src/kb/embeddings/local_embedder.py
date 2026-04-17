"""SentenceTransformer-backed embedder. Lazy-loads the model on first `embed()` call."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kb.constants import DEFAULT_EMBEDDING_MODEL

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbedder:
    """Thin wrapper around sentence-transformers. 384-dim for default `all-MiniLM-L6-v2`."""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL) -> None:
        self._model_name = model_name
        self._model: SentenceTransformer | None = None

    def _ensure_loaded(self) -> SentenceTransformer:
        if self._model is None:
            # Import locally so unit tests never pay the ~5s + torch import cost.
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._ensure_loaded()
        vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return [v.tolist() for v in vectors]
