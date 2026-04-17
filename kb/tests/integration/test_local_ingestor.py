"""Integration tests for LocalFileIngestor against a Repository with FakeEmbedder."""

from __future__ import annotations

import struct
import wave
from pathlib import Path

import pytest
from PIL import Image

from kb.constants import COLLECTION_SOUNDS, COLLECTION_TEMPLATES
from kb.ingestors import LocalFileIngestor
from kb.store import Repository


def _write_silent_wav(path: Path, duration_sec: float = 0.5, rate: int = 16000) -> None:
    n_frames = int(rate * duration_sec)
    silence = struct.pack("<" + "h" * n_frames, *([0] * n_frames))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(silence)


def _write_png(path: Path, size: tuple[int, int] = (64, 48)) -> None:
    Image.new("RGB", size, color=(128, 64, 200)).save(path, "PNG")


class TestLocalFileIngestorSounds:
    @pytest.mark.integration
    def test_ingests_wav_files_into_sounds_collection(
        self, tmp_path: Path, repo: Repository
    ) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _write_silent_wav(src / "vine_boom.wav")
        _write_silent_wav(src / "sad_trombone.wav")

        ingestor = LocalFileIngestor(
            repository=repo,
            collection=COLLECTION_SOUNDS,
            root=src,
        )
        ingested = ingestor.ingest()

        assert len(ingested) == 2
        rows = repo.list_all(COLLECTION_SOUNDS, limit=10)
        ids = {r["id"] for r in rows}
        assert len(ids) == 2
        descriptions = {r["description"] for r in rows}
        # Filename stems used as default description source.
        assert any("vine boom" in d.lower() for d in descriptions)
        assert any("sad trombone" in d.lower() for d in descriptions)

    @pytest.mark.integration
    def test_ignores_non_audio_files(self, tmp_path: Path, repo: Repository) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _write_silent_wav(src / "ok.wav")
        (src / "notes.txt").write_text("not audio")
        ingestor = LocalFileIngestor(
            repository=repo, collection=COLLECTION_SOUNDS, root=src
        )
        ingestor.ingest()
        assert repo.stats()[COLLECTION_SOUNDS] == 1

    @pytest.mark.integration
    def test_idempotent_reingest(self, tmp_path: Path, repo: Repository) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _write_silent_wav(src / "boom.wav")
        ingestor = LocalFileIngestor(
            repository=repo, collection=COLLECTION_SOUNDS, root=src
        )
        ingestor.ingest()
        ingestor.ingest()  # second run must not duplicate
        assert repo.stats()[COLLECTION_SOUNDS] == 1


class TestLocalFileIngestorTemplates:
    @pytest.mark.integration
    def test_ingests_png_files_into_templates_collection(
        self, tmp_path: Path, repo: Repository
    ) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _write_png(src / "distracted_boyfriend.png", size=(100, 50))
        _write_png(src / "drake_hotline.png", size=(200, 200))

        ingestor = LocalFileIngestor(
            repository=repo, collection=COLLECTION_TEMPLATES, root=src
        )
        ingestor.ingest()

        rows = repo.list_all(COLLECTION_TEMPLATES, limit=10)
        assert len(rows) == 2
        by_desc = {r["description"]: r["metadata"] for r in rows}
        # Dimensions captured.
        drake = next(m for d, m in by_desc.items() if "drake hotline" in d.lower())
        assert drake["width"] == 200
        assert drake["height"] == 200

    @pytest.mark.integration
    def test_ignores_audio_in_templates_collection(
        self, tmp_path: Path, repo: Repository
    ) -> None:
        src = tmp_path / "src"
        src.mkdir()
        _write_silent_wav(src / "not_a_template.wav")
        _write_png(src / "real_template.png")
        ingestor = LocalFileIngestor(
            repository=repo, collection=COLLECTION_TEMPLATES, root=src
        )
        ingestor.ingest()
        assert repo.stats()[COLLECTION_TEMPLATES] == 1
