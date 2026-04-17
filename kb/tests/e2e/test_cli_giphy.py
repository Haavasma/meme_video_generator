"""E2E test for `kb giphy` subcommand."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
import respx
from typer.testing import CliRunner

from kb.cli import app

SAMPLE_RESPONSE = {
    "data": [
        {
            "id": "abc",
            "title": "funny cat",
            "slug": "funny-cat-abc",
            "url": "https://giphy.com/gifs/funny-cat-abc",
            "images": {
                "original": {
                    "url": "https://media.giphy.com/orig/abc.gif",
                    "width": "480",
                    "height": "270",
                },
                "original_mp4": {"mp4": "https://media.giphy.com/orig/abc.mp4"},
            },
        }
    ],
    "meta": {"status": 200},
}


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestGiphyCli:
    @pytest.mark.e2e
    def test_requires_api_key(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
    ) -> None:
        monkeypatch.setenv("ASSETS_DIR", str(tmp_path / "assets"))
        monkeypatch.delenv("GIPHY_API_KEY", raising=False)
        result = runner.invoke(app, ["giphy", "--query", "x"])
        assert result.exit_code != 0

    @pytest.mark.e2e
    def test_returns_json_hits(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runner: CliRunner
    ) -> None:
        monkeypatch.setenv("ASSETS_DIR", str(tmp_path / "assets"))
        monkeypatch.setenv("GIPHY_API_KEY", "test-key")

        with respx.mock(assert_all_called=False) as mock:
            mock.get("https://api.giphy.com/v1/gifs/search").mock(
                return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
            )
            result = runner.invoke(app, [
                "giphy", "--query", "funny cat", "--limit", "1", "--json",
            ])
        assert result.exit_code == 0, result.stdout
        payload = json.loads(result.stdout)
        assert payload["count"] == 1
        assert payload["results"][0]["id"] == "abc"
