"""Template entry model — immutable Pydantic record for a static meme image template."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Static images only (user decision). GIFs/video handled via Giphy runtime.
TemplateMediaType = Literal["jpg", "jpeg", "png", "webp"]

_TAG_SEP = "||"


class Template(BaseModel):
    """A single meme-template image entry stored in the `templates` Chroma collection."""

    model_config = ConfigDict(frozen=True, validate_assignment=True, extra="forbid")

    id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    local_path: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    media_type: TemplateMediaType
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    file_size_bytes: int = Field(ge=0)

    def to_chroma_metadata(self) -> dict[str, str | int | float | bool]:
        return {
            "local_path": self.local_path,
            "source_url": self.source_url,
            "tags": _TAG_SEP.join(self.tags),
            "media_type": self.media_type,
            "width": self.width,
            "height": self.height,
            "file_size_bytes": self.file_size_bytes,
        }

    @classmethod
    def from_chroma_metadata(
        cls,
        *,
        id: str,
        description: str,
        metadata: dict[str, str | int | float | bool],
    ) -> Template:
        raw_tags = metadata.get("tags", "")
        tags = [t for t in str(raw_tags).split(_TAG_SEP) if t] if raw_tags else []
        return cls(
            id=id,
            description=description,
            local_path=str(metadata["local_path"]),
            source_url=str(metadata["source_url"]),
            tags=tags,
            media_type=str(metadata["media_type"]),  # type: ignore[arg-type]
            width=int(metadata["width"]),
            height=int(metadata["height"]),
            file_size_bytes=int(metadata["file_size_bytes"]),
        )
