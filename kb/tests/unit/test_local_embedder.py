"""Unit tests for embedders. Real SentenceTransformer test is marked `integration`."""

from __future__ import annotations

import math

import pytest

from kb.embeddings import Embedder, FakeEmbedder, SentenceTransformerEmbedder


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


class TestFakeEmbedder:
    @pytest.mark.unit
    def test_returns_configured_dim(self) -> None:
        e = FakeEmbedder(dim=8)
        out = e.embed(["x", "y"])
        assert len(out) == 2
        assert all(len(v) == 8 for v in out)

    @pytest.mark.unit
    def test_identical_text_identical_vector(self) -> None:
        e = FakeEmbedder(dim=16)
        a = e.embed(["hello"])[0]
        b = e.embed(["hello"])[0]
        assert a == b

    @pytest.mark.unit
    def test_different_text_different_vector(self) -> None:
        e = FakeEmbedder(dim=16)
        a = e.embed(["alpha"])[0]
        b = e.embed(["beta"])[0]
        assert a != b

    @pytest.mark.unit
    def test_empty_input_returns_empty(self) -> None:
        e = FakeEmbedder(dim=8)
        assert e.embed([]) == []

    @pytest.mark.unit
    def test_protocol_satisfied(self) -> None:
        embedder: Embedder = FakeEmbedder(dim=4)
        assert hasattr(embedder, "embed")


class TestSentenceTransformerEmbedder:
    """These are slow — mark integration; skipped in unit runs by default."""

    @pytest.mark.integration
    def test_real_model_similarity_ordering(self) -> None:
        e = SentenceTransformerEmbedder()
        vecs = e.embed([
            "dramatic dun dun dun reveal sound",
            "dramatic suspense sting",
            "puppy barking in park",
        ])
        # similar phrases > unrelated phrase
        assert _cosine(vecs[0], vecs[1]) > _cosine(vecs[0], vecs[2])

    @pytest.mark.integration
    def test_real_model_dim_is_384(self) -> None:
        e = SentenceTransformerEmbedder()
        vecs = e.embed(["x"])
        assert len(vecs[0]) == 384
