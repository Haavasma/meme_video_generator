"""Integration tests for the imgflip meme-template scraper — mocked via respx."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import httpx
import pytest
import respx

from kb.constants import COLLECTION_TEMPLATES
from kb.ingestors.imgflip import ImgflipIngestor
from kb.store import Repository

FIXTURE = Path(__file__).parent.parent / "fixtures" / "imgflip_memetemplates.html"


def _fake_png_bytes(width: int = 10, height: int = 10) -> bytes:
    """Build a minimal valid PNG so PIL can probe dimensions for the downloaded asset."""
    def chunk(type_: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(type_ + data)
        return struct.pack(">I", len(data)) + type_ + data + struct.pack(">I", crc)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    raw = b"".join(b"\x00" + b"\xff\x00\x00" * width for _ in range(height))
    idat = chunk(b"IDAT", zlib.compress(raw))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


FAKE_JPG_BODY = _fake_png_bytes(16, 16)  # we serve this for any .jpg request — content doesn't matter, PIL can read PNG via path


@pytest.fixture
def listing_html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


class TestImgflipIngestor:
    @pytest.mark.integration
    def test_parses_listing_and_ingests_templates(
        self, tmp_path: Path, repo: Repository, listing_html: str
    ) -> None:
        download_dir = tmp_path / "downloads"
        download_dir.mkdir()

        with respx.mock(assert_all_called=False) as mock:
            mock.get("https://imgflip.com/memetemplates").mock(
                return_value=httpx.Response(200, text=listing_html)
            )
            # Any imgflip image URL returns our fake PNG bytes.
            mock.get(url__regex=r"https://i\.imgflip\.com/.*").mock(
                return_value=httpx.Response(200, content=FAKE_JPG_BODY)
            )

            ingestor = ImgflipIngestor(
                repository=repo,
                download_dir=download_dir,
                max_items=3,
                request_delay=0.0,
            )
            results = ingestor.ingest()

        assert len(results) == 3
        rows = repo.list_all(COLLECTION_TEMPLATES, limit=10)
        assert len(rows) == 3
        # Drake Hotline Bling is the first template on the page per the fixture.
        descs = {r["description"].lower() for r in rows}
        assert any("drake" in d for d in descs)
        assert any("distracted boyfriend" in d for d in descs)
        for r in rows:
            assert Path(r["metadata"]["local_path"]).exists()

    @pytest.mark.integration
    def test_respects_max_items(
        self, tmp_path: Path, repo: Repository, listing_html: str
    ) -> None:
        download_dir = tmp_path / "downloads"
        download_dir.mkdir()
        with respx.mock(assert_all_called=False) as mock:
            mock.get("https://imgflip.com/memetemplates").mock(
                return_value=httpx.Response(200, text=listing_html)
            )
            mock.get(url__regex=r"https://i\.imgflip\.com/.*").mock(
                return_value=httpx.Response(200, content=FAKE_JPG_BODY)
            )
            ingestor = ImgflipIngestor(
                repository=repo, download_dir=download_dir, max_items=1, request_delay=0.0
            )
            ingestor.ingest()
        assert repo.stats()[COLLECTION_TEMPLATES] == 1

    @pytest.mark.integration
    def test_skips_download_when_file_exists(
        self, tmp_path: Path, repo: Repository, listing_html: str
    ) -> None:
        download_dir = tmp_path / "downloads"
        download_dir.mkdir()
        # Drake filename comes from the imgflip URL path (30b1gx.jpg).
        preexisting = download_dir / "30b1gx.jpg"
        preexisting.write_bytes(FAKE_JPG_BODY)

        with respx.mock(assert_all_called=False) as mock:
            mock.get("https://imgflip.com/memetemplates").mock(
                return_value=httpx.Response(200, text=listing_html)
            )
            img_route = mock.get(url__regex=r"https://i\.imgflip\.com/.*30b1gx\.jpg").mock(
                return_value=httpx.Response(200, content=FAKE_JPG_BODY)
            )
            other = mock.get(url__regex=r"https://i\.imgflip\.com/.*").mock(
                return_value=httpx.Response(200, content=FAKE_JPG_BODY)
            )

            ingestor = ImgflipIngestor(
                repository=repo, download_dir=download_dir, max_items=1, request_delay=0.0
            )
            ingestor.ingest()

        assert img_route.call_count == 0
