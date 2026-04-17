# kb

ChromaDB-backed vector store and CLI for meme sounds + meme templates.

Two collections:

- `sounds` — short audio clips (mp3/wav) scraped from myinstants.com
- `templates` — static meme template images scraped from imgflip.com

Embedder: `sentence-transformers/all-MiniLM-L6-v2` on rich text descriptions (title + tags + blurb).

## Commands

```bash
uv run kb ingest   --source {local,myinstants,imgflip}   --collection {sounds,templates}   [--path ...] [--max N]
uv run kb query    --collection {sounds,templates}       --text "..." [--top-k 5] [--json]
uv run kb list     --collection {sounds,templates}       [--limit 20] [--json]
uv run kb delete   --collection {sounds,templates}       --id <entry_id>
uv run kb reset    --collection {sounds,templates}       --confirm
uv run kb stats    [--json]
```

All commands accept `--json` for machine-readable output (used by the Claude skill orchestrator).

## Dev

```bash
uv sync
uv run pytest --cov=kb --cov-report=term-missing
uv run ruff check .
uv run mypy src
```
