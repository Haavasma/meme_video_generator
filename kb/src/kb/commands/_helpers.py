"""Shared helpers for command handlers: repository wiring + output rendering."""

from __future__ import annotations

import json
import os
from typing import Any

from rich.console import Console

from kb.config import Config
from kb.constants import ALL_COLLECTIONS
from kb.embeddings import Embedder, FakeEmbedder, SentenceTransformerEmbedder
from kb.store import Repository


def build_repository(config: Config | None = None) -> Repository:
    """Wire a Repository from live Config. Honors KB_USE_FAKE_EMBEDDER env toggle for tests."""
    cfg = config or Config()  # type: ignore[call-arg]
    embedder: Embedder
    if os.environ.get("KB_USE_FAKE_EMBEDDER"):
        embedder = FakeEmbedder(dim=16)
    else:
        embedder = SentenceTransformerEmbedder(model_name=cfg.embedding_model)
    return Repository.create(persist_dir=cfg.chroma_persist_dir, embedder=embedder)


def validate_collection(name: str) -> None:
    if name not in ALL_COLLECTIONS:
        raise ValueError(f"collection must be one of {ALL_COLLECTIONS}, got {name!r}")


def emit(payload: Any, *, as_json: bool, console: Console | None = None) -> None:
    """Print machine-readable JSON or human-friendly rich text depending on --json."""
    if as_json:
        # Use stdout directly to avoid rich wrapping/coloring of JSON output.
        print(json.dumps(payload, ensure_ascii=False, default=str))
        return
    c = console or Console()
    c.print(payload)
