"""Shared pytest fixtures for kb tests."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from kb.constants import COLLECTION_SOUNDS, COLLECTION_TEMPLATES
from kb.embeddings import FakeEmbedder
from kb.store import Repository


@pytest.fixture
def fake_embedder() -> FakeEmbedder:
    return FakeEmbedder(dim=16)


@pytest.fixture
def repo(tmp_path: Path, fake_embedder: FakeEmbedder) -> Iterator[Repository]:
    """Fresh in-memory-equivalent persistent Chroma repository scoped to a tmp dir."""
    r = Repository.create(persist_dir=tmp_path / "chroma", embedder=fake_embedder)
    try:
        yield r
    finally:
        r.reset(COLLECTION_SOUNDS)
        r.reset(COLLECTION_TEMPLATES)
