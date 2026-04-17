.PHONY: help bootstrap kb-install kb-ingest kb-test kb-lint video-install video-test render studio clean

help:
	@echo "Targets:"
	@echo "  bootstrap       full first-time setup (install + ingest KB)"
	@echo "  kb-install      install Python kb package via uv"
	@echo "  kb-ingest       seed KB with sounds + templates"
	@echo "  kb-test         run kb test suite with coverage"
	@echo "  kb-lint         ruff + mypy on kb"
	@echo "  video-install   install Remotion video project"
	@echo "  video-test      run video unit tests"
	@echo "  render ID=...   render bespoke composition by id"
	@echo "  studio          open Remotion Studio for preview"
	@echo "  clean           remove caches"

bootstrap: kb-install video-install kb-ingest
	@test -f .env || cp .env.example .env
	@echo "Bootstrap done. Add GIPHY_API_KEY to .env for Giphy support."

kb-install:
	cd kb && uv sync

kb-ingest:
	cd kb && uv run kb ingest --source myinstants --collection sounds --query meme --max 200 --delay 1
	cd kb && uv run kb ingest --source imgflip --collection templates --max 100 --delay 1

kb-test:
	cd kb && uv run pytest --cov=kb --cov-report=term-missing

kb-lint:
	cd kb && uv run ruff check . && uv run mypy src

video-install:
	cd video && npm install

video-test:
	cd video && npx vitest run

render:
	@test -n "$(ID)" || (echo "Usage: make render ID=MyCompositionId" && exit 1)
	cd video && npx remotion render $(ID) --output ../output/$(ID).mp4

studio:
	cd video && npx remotion studio

clean:
	rm -rf kb/.pytest_cache kb/.ruff_cache kb/.mypy_cache kb/htmlcov kb/.coverage
	rm -rf video/node_modules/.cache
