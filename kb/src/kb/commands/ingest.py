"""`kb ingest` command — dispatches to local / myinstants / imgflip ingestors."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from kb.commands._helpers import build_repository, emit, validate_collection
from kb.config import Config
from kb.constants import COLLECTION_SOUNDS, COLLECTION_TEMPLATES
from kb.ingestors import (
    ImgflipIngestor,
    IngestResult,
    LocalFileIngestor,
    MyInstantsIngestor,
)


def ingest_command(
    source: Annotated[str, typer.Option("--source", help="local | myinstants | imgflip")],
    collection: Annotated[str, typer.Option("--collection", help="sounds or templates")],
    path: Annotated[Path | None, typer.Option("--path", help="Root dir for --source=local")] = None,
    query: Annotated[str, typer.Option("--query", help="Search query for --source=myinstants")] = "meme",
    max_items: Annotated[int, typer.Option("--max", help="Cap on items fetched from scrapers")] = 50,
    request_delay: Annotated[float, typer.Option("--delay", help="Seconds between requests")] = 1.0,
    as_json: Annotated[bool, typer.Option("--json", help="Emit JSON")] = False,
) -> None:
    validate_collection(collection)
    cfg = Config()  # type: ignore[call-arg]
    repo = build_repository(cfg)

    results: list[IngestResult]
    if source == "local":
        if path is None:
            raise typer.BadParameter("--path is required when --source=local")
        results = LocalFileIngestor(
            repository=repo, collection=collection, root=path
        ).ingest()
    elif source == "myinstants":
        if collection != COLLECTION_SOUNDS:
            raise typer.BadParameter("--source=myinstants requires --collection=sounds")
        download_dir = cfg.sounds_dir
        results = MyInstantsIngestor(
            repository=repo,
            query=query,
            download_dir=download_dir,
            max_items=max_items,
            request_delay=request_delay,
        ).ingest()
    elif source == "imgflip":
        if collection != COLLECTION_TEMPLATES:
            raise typer.BadParameter("--source=imgflip requires --collection=templates")
        download_dir = cfg.templates_dir
        results = ImgflipIngestor(
            repository=repo,
            download_dir=download_dir,
            max_items=max_items,
            request_delay=request_delay,
        ).ingest()
    else:
        raise typer.BadParameter(
            f"Unknown --source={source!r}. Use one of: local, myinstants, imgflip."
        )

    payload = {
        "collection": collection,
        "source": source,
        "ingested_count": len(results),
        "entries": [{"id": r.entry_id, "description": r.description} for r in results],
    }
    emit(payload, as_json=as_json)
