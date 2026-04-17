"""ChromaDB storage layer — client factory and Repository pattern over collections."""

from kb.store.chroma_client import create_persistent_client
from kb.store.repository import Repository

__all__ = ["Repository", "create_persistent_client"]
