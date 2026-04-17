# meme-video-generator

Claude Code plugin that turns context into rendered meme videos (.mp4) via bespoke Remotion TSX compositions.

Full creative control — spring animations, typewriter text, flow diagrams, screen mockups, voiceover, sound effects, meme templates.

## Install as Claude Code plugin

```bash
/plugin marketplace add haavasma/meme_video_generator
/plugin install meme-video@meme-video-generator
```

Then bootstrap the template once (installs deps + seeds KB):

```bash
cd <plugin-install-dir>
make bootstrap
```

Use with `/meme-video` from any project.

## What's inside

| Directory | What |
|-----------|------|
| `video/` | Remotion project — primitives library, composition scaffold, render pipeline |
| `kb/` | Python CLI (ChromaDB + sentence-transformers) — sound effects, meme templates, TTS voiceover |
| `plugins/meme-video/` | Claude Code skill definition |
| `video/src/compositions/example-observability/` | Reference 8-scene composition |

## Manual setup (without plugin)

```bash
git clone https://github.com/haavasma/meme_video_generator
cd meme_video_generator
make bootstrap
```

## Requirements

- Python 3.11+
- Node 20+
- `ffmpeg` on PATH (Remotion render)
- [`uv`](https://docs.astral.sh/uv/)

## Environment

Copy `.env.example` to `.env`. Add `GIPHY_API_KEY` ([developers.giphy.com](https://developers.giphy.com)) for reaction GIF support.

## Makefile targets

| Target | What |
|--------|------|
| `make bootstrap` | Full first-time setup (install + ingest KB) |
| `make render ID=...` | Render composition by id |
| `make studio` | Open Remotion Studio for preview |
| `make kb-test` | Run KB test suite |
| `make video-test` | Run Remotion tests |
| `make clean` | Remove caches |
