"""`kb query` command."""

from __future__ import annotations

from typing import Annotated

import typer

from kb.commands._helpers import build_repository, emit, validate_collection


def query_command(
    collection: Annotated[str, typer.Option("--collection")],
    text: Annotated[str, typer.Option("--text", help="Query text")],
    top_k: Annotated[int, typer.Option("--top-k")] = 5,
    as_json: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    validate_collection(collection)
    repo = build_repository()
    results = repo.query(collection, query_text=text, top_k=top_k)
    payload = {
        "collection": collection,
        "query": text,
        "count": len(results),
        "results": results,
    }
    emit(payload, as_json=as_json)
