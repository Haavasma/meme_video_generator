"""Deterministic hashing embedder. For unit tests only — never use for real retrieval."""

from __future__ import annotations

import hashlib
import struct


class FakeEmbedder:
    """Produces stable pseudo-random unit vectors from MD5 of the input string.

    Deterministic: same text → same vector. Different text → different vector.
    Not semantic — just keeps tests fast and reproducible without loading a real model.
    """

    def __init__(self, dim: int = 16) -> None:
        if dim <= 0:
            raise ValueError("dim must be positive")
        self._dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        # Expand MD5 (16 bytes) into as many 4-byte floats as needed by re-hashing with a counter.
        vec: list[float] = []
        counter = 0
        while len(vec) < self._dim:
            digest = hashlib.md5(f"{counter}:{text}".encode()).digest()
            for i in range(0, len(digest), 4):
                if len(vec) == self._dim:
                    break
                (chunk,) = struct.unpack("<I", digest[i : i + 4])
                vec.append((chunk / 0xFFFFFFFF) * 2.0 - 1.0)
            counter += 1
        return vec
