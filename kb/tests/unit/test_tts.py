"""Unit tests for TTS styles + EdgeTtsSynthesizer (with mocked edge_tts)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from kb.tts import (
    DEFAULT_STYLE,
    STYLE_PRESETS,
    EdgeTtsSynthesizer,
    TtsStyle,
    resolve_style,
)


class TestStylePresets:
    @pytest.mark.unit
    def test_five_presets_exist(self) -> None:
        assert set(STYLE_PRESETS) == {
            "narrator",
            "dramatic",
            "sarcastic",
            "excited",
            "villain",
        }

    @pytest.mark.unit
    def test_default_is_narrator(self) -> None:
        assert DEFAULT_STYLE == "narrator"

    @pytest.mark.unit
    def test_resolve_known_style(self) -> None:
        s = resolve_style("dramatic")
        assert isinstance(s, TtsStyle)
        assert s.voice.startswith("en-")
        assert "%" in s.rate  # e.g. "-20%"

    @pytest.mark.unit
    def test_resolve_unknown_falls_back_to_default(self) -> None:
        s = resolve_style("nonsense-style")
        assert s == STYLE_PRESETS[DEFAULT_STYLE]

    @pytest.mark.unit
    def test_resolve_empty_uses_default(self) -> None:
        assert resolve_style(None) == STYLE_PRESETS[DEFAULT_STYLE]


class TestEdgeTtsSynthesizer:
    @pytest.mark.unit
    def test_synthesize_writes_mp3(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        save_mock = AsyncMock()
        comm_instance = MagicMock()
        comm_instance.save = save_mock

        def _fake_communicate(text: str, voice: str, **kwargs: object) -> MagicMock:
            # Echo back into a tiny mp3 on disk so downstream code sees a real file.
            captured_path = {"path": None}

            async def _save(path: str) -> None:
                captured_path["path"] = path
                Path(path).write_bytes(b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\x00" * 64)

            comm_instance.save = _save
            comm_instance.args = (text, voice, kwargs)
            return comm_instance

        monkeypatch.setattr("edge_tts.Communicate", _fake_communicate)

        synth = EdgeTtsSynthesizer(cache_dir=tmp_path / "cache")
        out = synth.synthesize(
            text="dramatic reveal",
            style="dramatic",
            output_path=tmp_path / "out.mp3",
        )
        assert out == tmp_path / "out.mp3"
        assert out.exists()
        assert out.stat().st_size > 0

    @pytest.mark.unit
    def test_synthesize_uses_cache_for_identical_input(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        call_count = {"n": 0}

        def _fake_communicate(text: str, voice: str, **kwargs: object) -> MagicMock:
            call_count["n"] += 1
            comm = MagicMock()

            async def _save(path: str) -> None:
                Path(path).write_bytes(b"\x00" * 128)

            comm.save = _save
            return comm

        monkeypatch.setattr("edge_tts.Communicate", _fake_communicate)

        synth = EdgeTtsSynthesizer(cache_dir=tmp_path / "cache")
        synth.synthesize(text="hi", style="narrator", output_path=tmp_path / "a.mp3")
        synth.synthesize(text="hi", style="narrator", output_path=tmp_path / "b.mp3")

        assert call_count["n"] == 1  # second call served from cache
        assert (tmp_path / "a.mp3").read_bytes() == (tmp_path / "b.mp3").read_bytes()

    @pytest.mark.unit
    def test_cache_key_differs_per_style(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        call_count = {"n": 0}

        def _fake_communicate(text: str, voice: str, **kwargs: object) -> MagicMock:
            call_count["n"] += 1
            comm = MagicMock()

            async def _save(path: str) -> None:
                Path(path).write_bytes(b"\x00" * 32)

            comm.save = _save
            return comm

        monkeypatch.setattr("edge_tts.Communicate", _fake_communicate)

        synth = EdgeTtsSynthesizer(cache_dir=tmp_path / "cache")
        synth.synthesize(text="hi", style="narrator", output_path=tmp_path / "a.mp3")
        synth.synthesize(text="hi", style="dramatic", output_path=tmp_path / "b.mp3")
        assert call_count["n"] == 2

    @pytest.mark.unit
    def test_explicit_voice_overrides_style(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured = {}

        def _fake_communicate(text: str, voice: str, **kwargs: object) -> MagicMock:
            captured["voice"] = voice
            comm = MagicMock()

            async def _save(path: str) -> None:
                Path(path).write_bytes(b"\x00")

            comm.save = _save
            return comm

        monkeypatch.setattr("edge_tts.Communicate", _fake_communicate)

        synth = EdgeTtsSynthesizer(cache_dir=tmp_path / "cache")
        synth.synthesize(
            text="x",
            style="narrator",
            voice="en-GB-LibbyNeural",
            output_path=tmp_path / "a.mp3",
        )
        assert captured["voice"] == "en-GB-LibbyNeural"

    @pytest.mark.unit
    def test_rejects_empty_text(self, tmp_path: Path) -> None:
        synth = EdgeTtsSynthesizer(cache_dir=tmp_path / "cache")
        with pytest.raises(ValueError):
            synth.synthesize(text="", style="narrator", output_path=tmp_path / "a.mp3")
