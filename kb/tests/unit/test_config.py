"""Unit tests for Config (env-based settings) and constants."""

from __future__ import annotations

from pathlib import Path

import pytest

from kb.config import Config
from kb.constants import COLLECTION_SOUNDS, COLLECTION_TEMPLATES, DEFAULT_EMBEDDING_MODEL


class TestConstants:
    @pytest.mark.unit
    def test_collection_names_stable(self) -> None:
        # Locked names. Changing these is a migration, not a rename.
        assert COLLECTION_SOUNDS == "sounds"
        assert COLLECTION_TEMPLATES == "templates"

    @pytest.mark.unit
    def test_default_embedding_model(self) -> None:
        assert DEFAULT_EMBEDDING_MODEL == "sentence-transformers/all-MiniLM-L6-v2"


class TestConfig:
    @pytest.mark.unit
    def test_defaults_when_env_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for var in ("CHROMA_PERSIST_DIR", "ASSETS_DIR", "EMBEDDING_MODEL", "GIPHY_API_KEY"):
            monkeypatch.delenv(var, raising=False)
        cfg = Config(_env_file=None)  # type: ignore[call-arg]
        assert cfg.chroma_persist_dir == Path("kb/data/chroma")
        assert cfg.assets_dir == Path("assets")
        assert cfg.embedding_model == DEFAULT_EMBEDDING_MODEL
        assert cfg.giphy_api_key is None

    @pytest.mark.unit
    def test_env_overrides(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CHROMA_PERSIST_DIR", "/var/chroma")
        monkeypatch.setenv("ASSETS_DIR", "/mnt/memes")
        monkeypatch.setenv("EMBEDDING_MODEL", "sentence-transformers/other-model")
        monkeypatch.setenv("GIPHY_API_KEY", "secret-key-xyz")
        cfg = Config(_env_file=None)  # type: ignore[call-arg]
        assert cfg.chroma_persist_dir == Path("/var/chroma")
        assert cfg.assets_dir == Path("/mnt/memes")
        assert cfg.embedding_model == "sentence-transformers/other-model"
        assert cfg.giphy_api_key == "secret-key-xyz"

    @pytest.mark.unit
    def test_assets_subdirs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ASSETS_DIR", "/tmp/x")
        cfg = Config(_env_file=None)  # type: ignore[call-arg]
        assert cfg.sounds_dir == Path("/tmp/x/sounds")
        assert cfg.templates_dir == Path("/tmp/x/templates")
