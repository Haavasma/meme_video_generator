"""`kb giphy` command — runtime search against Giphy API for reaction GIFs."""

from __future__ import annotations

from typing import Annotated

import typer

from kb.commands._helpers import emit
from kb.config import Config
from kb.giphy import GiphyClient


def giphy_command(
    query: Annotated[str, typer.Option("--query", help="Search phrase")],
    limit: Annotated[int, typer.Option("--limit")] = 5,
    as_json: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    cfg = Config()  # type: ignore[call-arg]
    if not cfg.giphy_api_key:
        raise typer.BadParameter("GIPHY_API_KEY not set in env/.env")
    cache_dir = cfg.assets_dir / ".giphy_cache"
    client = GiphyClient(api_key=cfg.giphy_api_key, cache_dir=cache_dir)
    try:
        hits = client.search(query, limit=limit)
    finally:
        client.close()

    payload = {
        "query": query,
        "count": len(hits),
        "results": [h.to_dict() for h in hits],
    }
    emit(payload, as_json=as_json)
