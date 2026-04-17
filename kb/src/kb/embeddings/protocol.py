"""Embedder protocol — duck-typed interface so we can swap local/remote/fake."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Embedder(Protocol):
    """Turn a batch of text strings into equal-length float vectors."""

    def embed(self, texts: list[str]) -> list[list[float]]: ...
