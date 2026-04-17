"""Text embedders. Protocol + real (sentence-transformers) + fake (deterministic, for tests)."""

from kb.embeddings.fake_embedder import FakeEmbedder
from kb.embeddings.local_embedder import SentenceTransformerEmbedder
from kb.embeddings.protocol import Embedder

__all__ = ["Embedder", "FakeEmbedder", "SentenceTransformerEmbedder"]
