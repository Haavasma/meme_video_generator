"""Typer CLI entry point. Registered as `kb` script via pyproject.toml."""

from __future__ import annotations

import typer

from kb.commands.delete import delete_command, reset_command
from kb.commands.giphy import giphy_command
from kb.commands.ingest import ingest_command
from kb.commands.list_entries import list_command
from kb.commands.query import query_command
from kb.commands.stats import stats_command
from kb.commands.tts import tts_app

app = typer.Typer(
    name="kb",
    help="Knowledge base for meme sounds + templates (backed by ChromaDB + MiniLM).",
    no_args_is_help=True,
)

app.command("ingest")(ingest_command)
app.command("query")(query_command)
app.command("list")(list_command)
app.command("delete")(delete_command)
app.command("reset")(reset_command)
app.command("stats")(stats_command)
app.command("giphy")(giphy_command)
app.add_typer(tts_app, name="tts")


def main() -> None:
    """Allow `python -m kb.cli` invocation in addition to the installed entry point."""
    app()


if __name__ == "__main__":
    main()
