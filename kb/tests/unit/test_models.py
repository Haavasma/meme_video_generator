"""Unit tests for Sound and Template data models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from kb.models import Sound, Template


class TestSound:
    @pytest.mark.unit
    def test_minimal_valid_sound(self) -> None:
        s = Sound(
            id="snd_abc",
            description="dramatic reveal dun dun dun",
            local_path="/tmp/dun.mp3",
            source_url="https://www.myinstants.com/x",
            duration_sec=2.1,
            tags=["dramatic", "reveal"],
            format="mp3",
            file_size_bytes=12345,
        )
        assert s.id == "snd_abc"
        assert s.duration_sec == pytest.approx(2.1)
        assert s.tags == ["dramatic", "reveal"]

    @pytest.mark.unit
    def test_sound_is_frozen(self) -> None:
        s = Sound(
            id="snd_abc",
            description="x",
            local_path="/tmp/a.mp3",
            source_url="https://x.test/a",
            duration_sec=1.0,
            tags=[],
            format="mp3",
            file_size_bytes=1,
        )
        with pytest.raises(ValidationError):
            s.id = "snd_def"  # type: ignore[misc]

    @pytest.mark.unit
    def test_negative_duration_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Sound(
                id="x",
                description="y",
                local_path="/tmp/a.mp3",
                source_url="https://x.test/a",
                duration_sec=-1.0,
                tags=[],
                format="mp3",
                file_size_bytes=1,
            )

    @pytest.mark.unit
    def test_empty_description_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Sound(
                id="x",
                description="",
                local_path="/tmp/a.mp3",
                source_url="https://x.test/a",
                duration_sec=1.0,
                tags=[],
                format="mp3",
                file_size_bytes=1,
            )

    @pytest.mark.unit
    def test_chroma_metadata_roundtrip(self) -> None:
        original = Sound(
            id="snd_abc",
            description="vine boom",
            local_path="/tmp/boom.mp3",
            source_url="https://www.myinstants.com/vine-boom",
            duration_sec=0.8,
            tags=["impact", "boom"],
            format="mp3",
            file_size_bytes=4096,
        )
        meta = original.to_chroma_metadata()
        # Chroma metadata must be flat primitives — no list values.
        for v in meta.values():
            assert isinstance(v, str | int | float | bool)
        restored = Sound.from_chroma_metadata(id=original.id, description=original.description, metadata=meta)
        assert restored == original


class TestTemplate:
    @pytest.mark.unit
    def test_minimal_valid_template(self) -> None:
        t = Template(
            id="tpl_drake",
            description="Drake hotline bling reaction — prefer/reject format",
            local_path="/tmp/drake.jpg",
            source_url="https://imgflip.com/memetemplate/drake",
            tags=["reaction", "prefer-reject"],
            media_type="jpg",
            width=1200,
            height=1200,
            file_size_bytes=98765,
        )
        assert t.media_type == "jpg"
        assert t.width == 1200

    @pytest.mark.unit
    def test_template_is_frozen(self) -> None:
        t = Template(
            id="tpl_x",
            description="d",
            local_path="/tmp/x.jpg",
            source_url="https://x.test/x",
            tags=[],
            media_type="jpg",
            width=100,
            height=100,
            file_size_bytes=1,
        )
        with pytest.raises(ValidationError):
            t.width = 200  # type: ignore[misc]

    @pytest.mark.unit
    def test_invalid_media_type_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Template(
                id="tpl_x",
                description="d",
                local_path="/tmp/x.exe",
                source_url="https://x.test/x",
                tags=[],
                media_type="exe",  # type: ignore[arg-type]
                width=100,
                height=100,
                file_size_bytes=1,
            )

    @pytest.mark.unit
    def test_non_positive_dimensions_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Template(
                id="tpl_x",
                description="d",
                local_path="/tmp/x.jpg",
                source_url="https://x.test/x",
                tags=[],
                media_type="jpg",
                width=0,
                height=100,
                file_size_bytes=1,
            )

    @pytest.mark.unit
    def test_chroma_metadata_roundtrip(self) -> None:
        original = Template(
            id="tpl_distracted_boyfriend",
            description="Distracted boyfriend — looking at new option while partner stares",
            local_path="/tmp/db.jpg",
            source_url="https://imgflip.com/memetemplate/distracted-boyfriend",
            tags=["cheating", "temptation", "classic"],
            media_type="jpg",
            width=1200,
            height=800,
            file_size_bytes=54321,
        )
        meta = original.to_chroma_metadata()
        for v in meta.values():
            assert isinstance(v, str | int | float | bool)
        restored = Template.from_chroma_metadata(
            id=original.id, description=original.description, metadata=meta
        )
        assert restored == original
