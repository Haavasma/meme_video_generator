"""E2E tests for the `kb` CLI via Typer's CliRunner."""

from __future__ import annotations

import json
import struct
import wave
from pathlib import Path

import pytest
from typer.testing import CliRunner

from kb.cli import app


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolated Chroma + assets dir per test via env overrides + fake embedder."""
    chroma = tmp_path / "chroma"
    assets = tmp_path / "assets"
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(chroma))
    monkeypatch.setenv("ASSETS_DIR", str(assets))
    # Force FakeEmbedder so e2e tests don't download the real model.
    monkeypatch.setenv("KB_USE_FAKE_EMBEDDER", "1")
    return tmp_path


def _make_wav(path: Path, duration_sec: float = 0.2) -> None:
    rate = 16000
    n = int(rate * duration_sec)
    silence = struct.pack("<" + "h" * n, *([0] * n))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(silence)


class TestCliStatsAndIngest:
    @pytest.mark.e2e
    def test_stats_json_on_empty_store(self, env: Path, runner: CliRunner) -> None:
        result = runner.invoke(app, ["stats", "--json"])
        assert result.exit_code == 0, result.stdout
        payload = json.loads(result.stdout)
        assert payload == {"sounds": 0, "templates": 0}

    @pytest.mark.e2e
    def test_ingest_local_then_query(self, env: Path, runner: CliRunner) -> None:
        src = env / "src_sounds"
        src.mkdir()
        _make_wav(src / "vine_boom.wav")
        _make_wav(src / "sad_trombone.wav")

        ingest = runner.invoke(app, [
            "ingest",
            "--source", "local",
            "--collection", "sounds",
            "--path", str(src),
            "--json",
        ])
        assert ingest.exit_code == 0, ingest.stdout
        ingest_payload = json.loads(ingest.stdout)
        assert ingest_payload["ingested_count"] == 2

        # Query with exact description — FakeEmbedder hash matches -> distance 0.
        q = runner.invoke(app, [
            "query",
            "--collection", "sounds",
            "--text", "vine boom",
            "--top-k", "1",
            "--json",
        ])
        assert q.exit_code == 0, q.stdout
        qpayload = json.loads(q.stdout)
        assert qpayload["collection"] == "sounds"
        assert qpayload["count"] == 1
        assert "vine boom" in qpayload["results"][0]["description"].lower()

    @pytest.mark.e2e
    def test_list_returns_ingested_entries(self, env: Path, runner: CliRunner) -> None:
        src = env / "src"
        src.mkdir()
        _make_wav(src / "boom.wav")
        runner.invoke(app, [
            "ingest", "--source", "local", "--collection", "sounds",
            "--path", str(src),
        ])
        out = runner.invoke(app, ["list", "--collection", "sounds", "--json"])
        assert out.exit_code == 0, out.stdout
        payload = json.loads(out.stdout)
        assert len(payload["results"]) == 1


class TestCliDeleteReset:
    @pytest.mark.e2e
    def test_delete_removes_entry(self, env: Path, runner: CliRunner) -> None:
        src = env / "src"
        src.mkdir()
        _make_wav(src / "boom.wav")
        runner.invoke(app, [
            "ingest", "--source", "local", "--collection", "sounds", "--path", str(src),
        ])
        listed = json.loads(
            runner.invoke(app, ["list", "--collection", "sounds", "--json"]).stdout
        )
        entry_id = listed["results"][0]["id"]

        result = runner.invoke(app, [
            "delete", "--collection", "sounds", "--id", entry_id, "--json",
        ])
        assert result.exit_code == 0, result.stdout
        assert json.loads(result.stdout)["deleted"] == entry_id

        stats = json.loads(runner.invoke(app, ["stats", "--json"]).stdout)
        assert stats["sounds"] == 0

    @pytest.mark.e2e
    def test_reset_requires_confirm(self, env: Path, runner: CliRunner) -> None:
        src = env / "src"
        src.mkdir()
        _make_wav(src / "x.wav")
        runner.invoke(app, [
            "ingest", "--source", "local", "--collection", "sounds", "--path", str(src),
        ])
        # Missing --confirm → non-zero exit
        result = runner.invoke(app, ["reset", "--collection", "sounds"])
        assert result.exit_code != 0
        # Count unchanged
        stats = json.loads(runner.invoke(app, ["stats", "--json"]).stdout)
        assert stats["sounds"] == 1

    @pytest.mark.e2e
    def test_reset_with_confirm(self, env: Path, runner: CliRunner) -> None:
        src = env / "src"
        src.mkdir()
        _make_wav(src / "x.wav")
        runner.invoke(app, [
            "ingest", "--source", "local", "--collection", "sounds", "--path", str(src),
        ])
        result = runner.invoke(app, [
            "reset", "--collection", "sounds", "--confirm", "--json",
        ])
        assert result.exit_code == 0, result.stdout
        stats = json.loads(runner.invoke(app, ["stats", "--json"]).stdout)
        assert stats["sounds"] == 0
