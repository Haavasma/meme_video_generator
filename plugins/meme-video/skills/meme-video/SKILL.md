---
name: meme-video
description: Generate a meme video (.mp4) from context input. Bootstraps from a template repo, creates bespoke Remotion TSX compositions with full creative control — spring animations, typewriter text, flow diagrams, screen mockups, voiceover, sound effects, meme templates.
---

# meme-video skill

Turn context into a rendered meme video via bespoke Remotion TSX compositions.

Every video gets its own composition folder with full creative freedom — custom scenes, animations, layout, timing. No rigid templates. Claude writes the TSX.

## Template

This skill is distributed as a Claude Code plugin. The plugin install directory contains the **base template** — a complete Remotion project scaffold with primitives, KB CLI, and an example composition.

**CRITICAL: Never edit the plugin's own files.** The template is read-only. Every invocation works in a **separate working copy**.

The template source repo: `https://github.com/haavasma/meme-video-generator`

## Inputs

Ask concisely for:

1. **Context** — required. Inline text, `.md` spec path, or video script path.
2. **Duration target** — optional. Soft target; actual duration driven by scene count.
3. **Output directory** — optional. Default CWD or user-specified path.
4. **Resolution** — optional. Default 1920x1080 @ 30fps (16:9 landscape).

Do not ask for asset IDs — resolve via KB + Giphy.

---

## Script planning

If the user provides a **full video script** (`.md` spec with scene-by-scene directions, narration cues, timing), skip this phase and proceed to [Project lifecycle](#project-lifecycle).

If the user provides **raw context** (a topic, a sentence, an idea), plan a script first:

### 1. Draft a video script

Present a concise scene-by-scene outline:

```
## Video Script: <title>
Duration: ~Xs (N scenes @ 30fps)

### Scene 1 — Title (Xs)
Visual: <what's on screen>
Text: "<caption or title>"
VO: "<narration>" [style]
SFX: <sound effect>

### Scene 2 — <beat name> (Xs)
Visual: ...
Text: ...
...
```

Include for each scene:
- **Visual** — what the viewer sees (meme template, code block, diagram, screen mockup, etc.)
- **Text** — on-screen captions/titles
- **VO** — voiceover narration with style tag (narrator/dramatic/sarcastic/excited/villain)
- **SFX** — sound effects at key moments
- **Timing** — approximate duration

### 2. Wait for user feedback

**Do not generate code until the user approves the script.** They may want to:
- Add/remove/reorder scenes
- Change tone or pacing
- Swap visuals or meme references
- Adjust narration style
- Change duration

Iterate on the script until the user confirms. Then proceed to project lifecycle + authoring.

---

## Project lifecycle

### Locate the template

The base template lives in the plugin install directory. Find it by locating this skill's own path and navigating to the plugin root (the directory containing `video/`, `kb/`, `Makefile`).

### Detect existing working copy

Look for `video/package.json` + `kb/pyproject.toml` in CWD or parent dirs.

- **Found** → set `PROJECT_ROOT` to that directory. Skip to [Verify KB](#verify-kb).
- **Not found** → create a new working copy.

### Bootstrap the template (once)

The template itself should be bootstrapped **once** — deps installed, KB ingested. After that, every working copy inherits the full state (node_modules, KB data, venv, everything).

If the template is not yet bootstrapped (check: `kb/data/` missing or `video/node_modules/` missing), run from the template root:

```bash
make bootstrap
```

This runs `uv sync`, `npm install`, KB ingest (sounds + templates), and creates `.env`. Only needs to happen once per template install.

### Create working copy (per video project)

Copy the **bootstrapped** template into a fresh directory. Everything is already installed.

```bash
cp -r <plugin-template-root> <target-dir>
cd <target-dir>
git init
```

No further setup needed — deps, KB, and assets are all inherited from the template copy.

If no local template available (skill shared without plugin), fall back to GitHub:

```bash
git clone https://github.com/haavasma/meme-video-generator <target-dir>
cd <target-dir> && make bootstrap
```

### Verify KB

```bash
cd $PROJECT_ROOT/kb && uv run kb stats --json
```

If `sounds` or `templates` count is 0 → template wasn't bootstrapped. Run `make bootstrap` on the template first, then re-copy.

---

## Authoring — bespoke Remotion TSX

### Primitives library

Import from `video/src/lib/primitives/`:

| Primitive | Props | Use for |
|-----------|-------|---------|
| `SpringIn` | `at`, `damping`, `stiffness`, `fromScale`, `fromY`, `style` | Spring pop-in (scale + rise + fade). Default entry animation for any element. |
| `Typewriter` | `text`, `at`, `cps`, `caret`, `style` | Char-by-char text reveal. Code, terminal, dramatic reveals. |
| `StaggerGroup` | `offset`, `startAt`, `style` | Stagger children entry — each pops in `offset` frames after previous. |
| `AnimatedArrow` | `from`, `to`, `at`, `duration`, `color`, `strokeWidth`, `head`, `dash` | SVG arrow that draws itself. Flow diagrams, architecture visuals. |
| `CodeBlock` | `code`, `at`, `language`, `cps`, `highlight`, `instant`, `style` | IDE window with line numbers, typewriter reveal, glow highlight on specific lines. |
| `ScreenMockup` | `kind: "browser" \| "terminal"`, `title`, `style` | Window frame with traffic-light chrome. Wrap screenshots, Grafana tours, terminal demos. |

Also use Remotion directly: `AbsoluteFill`, `Sequence`, `Audio`, `Img`, `OffthreadVideo`, `useCurrentFrame`, `useVideoConfig`, `interpolate`, `spring`, `staticFile`.

**Extend freely.** Create new primitives in `video/src/lib/primitives/` when the video needs animation patterns not covered above. Re-export from `index.ts`.

### Composition structure

Create a folder per video:

```
video/src/compositions/
  <slug>/
    index.tsx          # exports BespokeComposition object
    scenes/
      Scene01Title.tsx
      Scene02Body.tsx
      ...
```

The `index.tsx` exports:

```ts
import type { BespokeComposition } from "../index";

export const mySlug: BespokeComposition = {
  id: "MySlug",               // used by: npx remotion render MySlug
  component: MySlugComponent,
  durationInFrames: TOTAL,
  fps: 30,
  width: 1920,
  height: 1080,
};
```

Register in `video/src/compositions/index.ts`:

```ts
import { mySlug } from "./my-slug";
export const COMPOSITIONS: readonly BespokeComposition[] = [...existing, mySlug];
```

### Scene structure

Each scene: function component returning `<AbsoluteFill>` with background + content.

Composition root stitches scenes via `<Sequence from={N} durationInFrames={D}>`. Each scene uses `useCurrentFrame()` which starts at 0 within its Sequence.

Put per-scene `<Audio>` inside the same `<Sequence>` so audio auto-clips to the scene window.

```tsx
// scenes/Scene01Title.tsx
import { AbsoluteFill, Audio, staticFile, useCurrentFrame } from "remotion";
import { SpringIn, Typewriter } from "../../../lib/primitives";

export function Scene01Title() {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0e14", justifyContent: "center", alignItems: "center" }}>
      <SpringIn at={10}>
        <h1 style={{ color: "#fff", fontSize: 96 }}>TITLE HERE</h1>
      </SpringIn>
      <Audio src={staticFile("assets/some-sound.mp3")} volume={0.5} />
    </AbsoluteFill>
  );
}
```

---

## Asset resolution

### Meme templates (KB)

```bash
cd $PROJECT_ROOT/kb && uv run kb query --collection templates --text "<description>" --top-k 3 --json
```

Returns `metadata.local_path` (absolute). Copy into `video/public/assets/` → reference via `staticFile("assets/<filename>")`.

### Sound effects (KB)

```bash
cd $PROJECT_ROOT/kb && uv run kb query --collection sounds --text "<description>" --top-k 3 --json
```

Same pattern — copy `local_path` into `video/public/assets/`.

### Reaction GIFs (Giphy)

```bash
cd $PROJECT_ROOT/kb && uv run kb giphy --query "<phrase>" --limit 5 --json
```

Returns `mp4_url`. Use directly as `<OffthreadVideo src={url}>` — no local copy needed. Requires `GIPHY_API_KEY` in `.env`.

### Web images

Fetch any URL directly into assets:

```bash
curl -o $PROJECT_ROOT/video/public/assets/<filename> "<url>"
```

Reference via `staticFile("assets/<filename>")`.

### Voiceover (edge-tts)

```bash
cd $PROJECT_ROOT/kb && uv run kb tts synthesize --text "<narration>" --style <preset> --out $PROJECT_ROOT/video/public/assets/<slug>_vo_<n>.mp3
```

**Style presets:**

| style | mood | voice |
|-------|------|-------|
| `narrator` (default) | neutral | en-US-GuyNeural |
| `dramatic` | slow, serious | en-GB-RyanNeural |
| `sarcastic` | flat, mocking | en-US-BrandonNeural |
| `excited` | hyper | en-US-AnaNeural |
| `villain` | deep, ominous | en-US-DavisNeural |

Override with `--voice "en-GB-LibbyNeural"` for any Edge-TTS voice.

**Mixing:** VO volume ~0.9, background SFX ~0.3–0.5.

**Parsing .md scripts for narration cues:**
- `[narrator]:` / `[voiceover]:` → narrator style
- `[dramatic]:`, `[sarcastic]:`, `[excited]:`, `[villain]:` → that preset
- `*italics on own line*` → dramatic
- `> quote blocks` → narrator

---

## Extending the KB

### Add more sounds

```bash
cd $PROJECT_ROOT/kb
uv run kb ingest --source myinstants --collection sounds --query "<search term>" --max 50 --delay 1
```

### Add more templates

```bash
cd $PROJECT_ROOT/kb
uv run kb ingest --source imgflip --collection templates --max 50 --delay 1
```

### Custom assets

Drop files directly into `$PROJECT_ROOT/video/public/assets/`. Reference via `staticFile("assets/<filename>")`. These are gitignored — the KB is the reproducible source; `public/assets/` is the staging area.

---

## Render

```bash
cd $PROJECT_ROOT/video && npx remotion render <CompositionId> --output ../output/<slug>.mp4
```

Preview in Remotion Studio:

```bash
cd $PROJECT_ROOT/video && npx remotion studio
```

## Report

Give the user:
- Final `.mp4` absolute path
- Duration
- Brief scene list (one-liners: what plays when)

---

## Reference example

See `video/src/compositions/example-observability/` — 8-scene narrative video with:
- Animated SVG flow diagram (pods → collectors → backends → Grafana) with traveling signal dot
- Typewriter code blocks with line-highlight
- Screen mockups (Grafana dashboard tour)
- 5 voiceovers across all style presets
- Drake meme + "Always Has Been" templates with spring-in captions
- Sound effects (vine boom, bruh, etc.)

Study this for patterns, then build something new.

---

## Failure modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `kb query` returns 0 hits | KB empty or query too niche | Run ingest; broaden query |
| `kb giphy` fails "API key not set" | Missing `.env` | Add `GIPHY_API_KEY` |
| `kb giphy` 429 | Rate limit | Fall back to KB template |
| Remotion render fails | Bad TSX or missing asset | Check composition compiles; verify assets in `video/public/assets/` |
| `staticFile` not found | Asset not staged | Copy from KB `local_path` into `video/public/assets/` |
| `uv` not found | Python tooling missing | Install: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `npx remotion` not found | Node deps missing | `cd video && npm install` |

## Do-not

- Do **not** ingest Giphy into KB — runtime-only by design.
- Do **not** hardcode absolute paths in TSX — always `staticFile("assets/...")` for local, URLs for remote.
- Do **not** change resolution mid-composition.
- Do **not** hand-write asset paths — use `kb query` output or stage manually.
