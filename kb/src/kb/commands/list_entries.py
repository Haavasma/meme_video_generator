"""`kb list` command."""

from __future__ import annotations

from typing import Annotated

import typer

from kb.commands._helpers import build_repository, emit, validate_collection


def list_command(
    collection: Annotated[str, typer.Option("--collection")],
    limit: Annotated[int, typer.Option("--limit")] = 20,
    offset: Annotated[int, typer.Option("--offset")] = 0,
    as_json: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    validate_collection(collection)
    repo = build_repository()
    rows = repo.list_all(collection, limit=limit, offset=offset)
    payload = {"collection": collection, "count": len(rows), "results": rows}
    emit(payload, as_json=as_json)
