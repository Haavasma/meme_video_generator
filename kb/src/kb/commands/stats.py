"""`kb stats` command."""

from __future__ import annotations

from typing import Annotated

import typer

from kb.commands._helpers import build_repository, emit


def stats_command(
    as_json: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    repo = build_repository()
    emit(repo.stats(), as_json=as_json)
