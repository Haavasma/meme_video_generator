"""Runtime configuration loaded from environment (optionally via .env)."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from kb.constants import DEFAULT_EMBEDDING_MODEL


class Config(BaseSettings):
    """Env-backed settings. Fail fast on malformed values, but all fields have sane defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    chroma_persist_dir: Path = Field(default=Path("kb/data/chroma"))
    assets_dir: Path = Field(default=Path("assets"))
    embedding_model: str = Field(default=DEFAULT_EMBEDDING_MODEL)
    giphy_api_key: str | None = Field(default=None)

    @property
    def sounds_dir(self) -> Path:
        return self.assets_dir / "sounds"

    @property
    def templates_dir(self) -> Path:
        return self.assets_dir / "templates"
