"""E2E tests for `kb tts synthesize` and `kb tts voices`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from kb.cli import app


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _stub_edge_tts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace edge_tts.Communicate with a stub that writes a fake mp3."""
    class _Stub:
        def __init__(self, text: str, voice: str, **kwargs: object) -> None:
            self._text = text
            self._voice = voice

        async def save(self, path: str) -> None:
            Path(path).write_bytes(b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\x00" * 256)

    monkeypatch.setattr("edge_tts.Communicate", _Stub)


class TestKbTtsCli:
    @pytest.mark.e2e
    def test_synthesize_writes_mp3(
        self, tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _stub_edge_tts(monkeypatch)
        monkeypatch.setenv("ASSETS_DIR", str(tmp_path / "assets"))
        out = tmp_path / "hello.mp3"
        result = runner.invoke(app, [
            "tts", "synthesize",
            "--text", "hello world",
            "--style", "dramatic",
            "--out", str(out),
            "--json",
        ])
        assert result.exit_code == 0, result.stdout
        payload = json.loads(result.stdout)
        assert payload["style"] == "dramatic"
        assert out.exists()
        assert out.stat().st_size > 0

    @pytest.mark.e2e
    def test_voices_lists_all_presets(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        result = runner.invoke(app, ["tts", "voices", "--json"])
        assert result.exit_code == 0, result.stdout
        payload = json.loads(result.stdout)
        assert set(payload["presets"]) == {
            "narrator", "dramatic", "sarcastic", "excited", "villain"
        }

    @pytest.mark.e2e
    def test_unknown_style_falls_back_to_narrator(
        self, tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _stub_edge_tts(monkeypatch)
        monkeypatch.setenv("ASSETS_DIR", str(tmp_path / "assets"))
        out = tmp_path / "x.mp3"
        result = runner.invoke(app, [
            "tts", "synthesize",
            "--text", "x",
            "--style", "nonsense",
            "--out", str(out),
            "--json",
        ])
        assert result.exit_code == 0
        payload = json.loads(result.stdout)
        assert payload["style"] == "narrator"
