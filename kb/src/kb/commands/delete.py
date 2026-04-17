"""`kb delete` and `kb reset` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from kb.commands._helpers import build_repository, emit, validate_collection


def delete_command(
    collection: Annotated[str, typer.Option("--collection")],
    entry_id: Annotated[str, typer.Option("--id", help="ID to delete")],
    as_json: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    validate_collection(collection)
    repo = build_repository()
    repo.delete(collection, entry_id)
    emit({"collection": collection, "deleted": entry_id}, as_json=as_json)


def reset_command(
    collection: Annotated[str, typer.Option("--collection")],
    confirm: Annotated[bool, typer.Option("--confirm", help="Required — reset is destructive")] = False,
    as_json: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    validate_collection(collection)
    if not confirm:
        raise typer.BadParameter(
            f"reset is destructive; pass --confirm to wipe the {collection!r} collection."
        )
    repo = build_repository()
    repo.reset(collection)
    emit({"collection": collection, "reset": True}, as_json=as_json)
