"""Integration tests for the Giphy runtime client."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
import respx

from kb.giphy import GiphyClient, GiphyHit

SAMPLE_RESPONSE = {
    "data": [
        {
            "id": "abc123",
            "title": "confused cat blinking",
            "slug": "confused-cat-abc123",
            "url": "https://giphy.com/gifs/confused-cat-abc123",
            "images": {
                "original": {
                    "url": "https://media.giphy.com/original/abc123.gif",
                    "width": "480",
                    "height": "270",
                },
                "original_mp4": {
                    "mp4": "https://media.giphy.com/original/abc123.mp4",
                    "width": "480",
                    "height": "270",
                },
                "preview_gif": {
                    "url": "https://media.giphy.com/preview/abc123.gif",
                },
            },
        },
        {
            "id": "def456",
            "title": "dramatic hamster",
            "slug": "dramatic-hamster-def456",
            "url": "https://giphy.com/gifs/dramatic-hamster-def456",
            "images": {
                "original": {
                    "url": "https://media.giphy.com/original/def456.gif",
                    "width": "500",
                    "height": "375",
                },
                "original_mp4": {
                    "mp4": "https://media.giphy.com/original/def456.mp4",
                    "width": "500",
                    "height": "375",
                },
            },
        },
    ],
    "pagination": {"total_count": 2, "count": 2, "offset": 0},
    "meta": {"status": 200, "msg": "OK"},
}


class TestGiphyClient:
    @pytest.mark.integration
    def test_search_returns_hits(self, tmp_path: Path) -> None:
        with respx.mock() as mock:
            mock.get("https://api.giphy.com/v1/gifs/search").mock(
                return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
            )
            client = GiphyClient(api_key="fake-key", cache_dir=tmp_path)
            hits = client.search("confused cat", limit=5)

        assert len(hits) == 2
        assert isinstance(hits[0], GiphyHit)
        assert hits[0].id == "abc123"
        assert hits[0].title == "confused cat blinking"
        assert hits[0].mp4_url == "https://media.giphy.com/original/abc123.mp4"
        assert hits[0].gif_url == "https://media.giphy.com/original/abc123.gif"

    @pytest.mark.integration
    def test_cache_hit_avoids_second_request(self, tmp_path: Path) -> None:
        with respx.mock(assert_all_called=False) as mock:
            route = mock.get("https://api.giphy.com/v1/gifs/search").mock(
                return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
            )
            client = GiphyClient(api_key="fake-key", cache_dir=tmp_path)
            client.search("confused cat", limit=5)
            client.search("confused cat", limit=5)

        assert route.call_count == 1  # second call served from cache

    @pytest.mark.integration
    def test_cache_key_includes_limit(self, tmp_path: Path) -> None:
        """Different limits should not share cache entries."""
        with respx.mock(assert_all_called=False) as mock:
            route = mock.get("https://api.giphy.com/v1/gifs/search").mock(
                return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
            )
            client = GiphyClient(api_key="fake-key", cache_dir=tmp_path)
            client.search("x", limit=3)
            client.search("x", limit=10)

        assert route.call_count == 2

    @pytest.mark.integration
    def test_raises_on_missing_api_key(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError):
            GiphyClient(api_key="", cache_dir=tmp_path)

    @pytest.mark.integration
    def test_raises_on_rate_limit_response(self, tmp_path: Path) -> None:
        with respx.mock() as mock:
            mock.get("https://api.giphy.com/v1/gifs/search").mock(
                return_value=httpx.Response(429, json={"message": "rate limited"})
            )
            client = GiphyClient(api_key="fake-key", cache_dir=tmp_path)
            with pytest.raises(httpx.HTTPStatusError):
                client.search("x", limit=1)

    @pytest.mark.integration
    def test_hit_to_dict_serializable(self, tmp_path: Path) -> None:
        with respx.mock() as mock:
            mock.get("https://api.giphy.com/v1/gifs/search").mock(
                return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
            )
            client = GiphyClient(api_key="fake-key", cache_dir=tmp_path)
            hits = client.search("x", limit=1)
        serialized = json.dumps([h.to_dict() for h in hits])
        assert "abc123" in serialized
