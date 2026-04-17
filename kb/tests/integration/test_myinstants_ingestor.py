"""Integration tests for the myinstants scraper ingestor — all network calls mocked via respx."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

from kb.constants import COLLECTION_SOUNDS
from kb.ingestors.myinstants import MyInstantsIngestor
from kb.store import Repository

FIXTURE = Path(__file__).parent.parent / "fixtures" / "myinstants_search.html"
FAKE_MP3 = b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\x00" * 128  # minimal mp3 header


@pytest.fixture
def search_html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


class TestMyInstantsIngestor:
    @pytest.mark.integration
    def test_parses_search_page_and_ingests_sounds(
        self,
        tmp_path: Path,
        repo: Repository,
        search_html: str,
    ) -> None:
        download_dir = tmp_path / "downloads"
        download_dir.mkdir()

        with respx.mock(assert_all_called=False) as mock:
            mock.get("https://www.myinstants.com/en/search/").mock(
                return_value=httpx.Response(200, text=search_html)
            )
            # All mp3 downloads served the same fake body — scraper shouldn't care about content.
            mock.get(url__regex=r"https://www\.myinstants\.com/media/sounds/.*\.mp3").mock(
                return_value=httpx.Response(200, content=FAKE_MP3)
            )

            ingestor = MyInstantsIngestor(
                repository=repo,
                query="meme",
                download_dir=download_dir,
                max_items=3,
                request_delay=0.0,
            )
            results = ingestor.ingest()

        assert len(results) == 3
        rows = repo.list_all(COLLECTION_SOUNDS, limit=10)
        assert len(rows) == 3
        # Display names were captured from anchor text.
        descriptions = {r["description"] for r in rows}
        assert any("meme" in d.lower() for d in descriptions)
        # Downloaded mp3 files exist on disk.
        for r in rows:
            assert Path(r["metadata"]["local_path"]).exists()
            assert r["metadata"]["format"] == "mp3"

    @pytest.mark.integration
    def test_respects_max_items(
        self,
        tmp_path: Path,
        repo: Repository,
        search_html: str,
    ) -> None:
        download_dir = tmp_path / "downloads"
        download_dir.mkdir()
        with respx.mock(assert_all_called=False) as mock:
            mock.get("https://www.myinstants.com/en/search/").mock(
                return_value=httpx.Response(200, text=search_html)
            )
            mock.get(url__regex=r"https://www\.myinstants\.com/media/sounds/.*\.mp3").mock(
                return_value=httpx.Response(200, content=FAKE_MP3)
            )

            ingestor = MyInstantsIngestor(
                repository=repo,
                query="meme",
                download_dir=download_dir,
                max_items=1,
                request_delay=0.0,
            )
            ingestor.ingest()

        assert repo.stats()[COLLECTION_SOUNDS] == 1

    @pytest.mark.integration
    def test_skips_download_when_file_exists(
        self,
        tmp_path: Path,
        repo: Repository,
        search_html: str,
    ) -> None:
        download_dir = tmp_path / "downloads"
        download_dir.mkdir()
        # Pre-existing file with same name the scraper would write.
        preexisting = download_dir / "are-you-out-of-your-mind-greenscreen-change-quality-and-end-wont-cut-off_2.mp3"
        preexisting.write_bytes(FAKE_MP3 + b"existing")

        with respx.mock(assert_all_called=False) as mock:
            mock.get("https://www.myinstants.com/en/search/").mock(
                return_value=httpx.Response(200, text=search_html)
            )
            mp3_route = mock.get(url__regex=r"https://www\.myinstants\.com/media/sounds/.*\.mp3").mock(
                return_value=httpx.Response(200, content=FAKE_MP3)
            )

            ingestor = MyInstantsIngestor(
                repository=repo,
                query="meme",
                download_dir=download_dir,
                max_items=1,
                request_delay=0.0,
            )
            ingestor.ingest()

        # The first (pre-existing) should be reused; confirm by content length unchanged.
        assert preexisting.stat().st_size == len(FAKE_MP3) + len(b"existing")
        # First mp3 download was skipped (scraper saw file exists).
        assert mp3_route.call_count == 0
