"""Sound entry model — immutable Pydantic record for a meme audio clip."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SoundFormat = Literal["mp3", "wav", "ogg", "m4a"]

# Separator used to pack/unpack list fields (tags) into Chroma metadata,
# which only accepts flat primitive values (str/int/float/bool).
_TAG_SEP = "||"


class Sound(BaseModel):
    """A single meme-soundboard entry stored in the `sounds` Chroma collection."""

    model_config = ConfigDict(frozen=True, validate_assignment=True, extra="forbid")

    id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    local_path: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    duration_sec: float = Field(ge=0.0)
    tags: list[str] = Field(default_factory=list)
    format: SoundFormat
    file_size_bytes: int = Field(ge=0)

    def to_chroma_metadata(self) -> dict[str, str | int | float | bool]:
        """Flatten to Chroma-compatible primitives. `description` and `id` are stored separately."""
        return {
            "local_path": self.local_path,
            "source_url": self.source_url,
            "duration_sec": self.duration_sec,
            "tags": _TAG_SEP.join(self.tags),
            "format": self.format,
            "file_size_bytes": self.file_size_bytes,
        }

    @classmethod
    def from_chroma_metadata(
        cls,
        *,
        id: str,
        description: str,
        metadata: dict[str, str | int | float | bool],
    ) -> Sound:
        """Rehydrate from Chroma metadata + document (description) + id."""
        raw_tags = metadata.get("tags", "")
        tags = [t for t in str(raw_tags).split(_TAG_SEP) if t] if raw_tags else []
        return cls(
            id=id,
            description=description,
            local_path=str(metadata["local_path"]),
            source_url=str(metadata["source_url"]),
            duration_sec=float(metadata["duration_sec"]),
            tags=tags,
            format=str(metadata["format"]),  # type: ignore[arg-type]
            file_size_bytes=int(metadata["file_size_bytes"]),
        )
