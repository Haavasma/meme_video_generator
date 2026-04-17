"""E2E test of `kb ingest --source myinstants/imgflip` via CliRunner + respx."""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

import httpx
import pytest
import respx
from typer.testing import CliRunner

from kb.cli import app

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"
FAKE_MP3 = b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\x00" * 128


def _fake_png(width: int = 10, height: int = 10) -> bytes:
    def chunk(type_: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(type_ + data)
        return struct.pack(">I", len(data)) + type_ + data + struct.pack(">I", crc)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    raw = b"".join(b"\x00" + b"\xff\x00\x00" * width for _ in range(height))
    idat = chunk(b"IDAT", zlib.compress(raw))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("ASSETS_DIR", str(tmp_path / "assets"))
    monkeypatch.setenv("KB_USE_FAKE_EMBEDDER", "1")
    return tmp_path


class TestCliScrapers:
    @pytest.mark.e2e
    def test_myinstants_source_end_to_end(
        self, env: Path, runner: CliRunner
    ) -> None:
        html = (FIXTURE_DIR / "myinstants_search.html").read_text(encoding="utf-8")
        with respx.mock(assert_all_called=False) as mock:
            mock.get("https://www.myinstants.com/en/search/").mock(
                return_value=httpx.Response(200, text=html)
            )
            mock.get(url__regex=r"https://www\.myinstants\.com/media/sounds/.*\.mp3").mock(
                return_value=httpx.Response(200, content=FAKE_MP3)
            )
            result = runner.invoke(app, [
                "ingest",
                "--source", "myinstants",
                "--collection", "sounds",
                "--query", "meme",
                "--max", "2",
                "--delay", "0",
                "--json",
            ])

        assert result.exit_code == 0, result.stdout
        payload = json.loads(result.stdout)
        assert payload["source"] == "myinstants"
        assert payload["ingested_count"] == 2

    @pytest.mark.e2e
    def test_imgflip_source_end_to_end(
        self, env: Path, runner: CliRunner
    ) -> None:
        html = (FIXTURE_DIR / "imgflip_memetemplates.html").read_text(encoding="utf-8")
        with respx.mock(assert_all_called=False) as mock:
            mock.get("https://imgflip.com/memetemplates").mock(
                return_value=httpx.Response(200, text=html)
            )
            mock.get(url__regex=r"https://i\.imgflip\.com/.*").mock(
                return_value=httpx.Response(200, content=_fake_png())
            )
            result = runner.invoke(app, [
                "ingest",
                "--source", "imgflip",
                "--collection", "templates",
                "--max", "2",
                "--delay", "0",
                "--json",
            ])

        assert result.exit_code == 0, result.stdout
        payload = json.loads(result.stdout)
        assert payload["ingested_count"] == 2

    @pytest.mark.e2e
    def test_myinstants_rejects_templates_collection(
        self, env: Path, runner: CliRunner
    ) -> None:
        result = runner.invoke(app, [
            "ingest", "--source", "myinstants",
            "--collection", "templates",
            "--max", "1",
        ])
        assert result.exit_code != 0

    @pytest.mark.e2e
    def test_unknown_source_rejected(
        self, env: Path, runner: CliRunner
    ) -> None:
        result = runner.invoke(app, [
            "ingest", "--source", "bogus", "--collection", "sounds",
        ])
        assert result.exit_code != 0
