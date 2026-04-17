#!/usr/bin/env bash
# Synthesize the 9 voiceovers for the observability-meme bespoke composition.
# All voiceovers share the `dramatic` style (en-GB-RyanNeural) per user direction —
# gives the whole video a single documentary-narrator feel.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
ROOT="$(pwd)"
KB="$ROOT/kb"
OUT="$ROOT/video/public/assets"
mkdir -p "$OUT"

STYLE="dramatic"

synth () {
  local name="$1" text="$2"
  local dest="$OUT/$name"
  if [[ -f "$dest" && -s "$dest" ]]; then
    echo "cached $name"
    return
  fi
  echo "synth  $name"
  (cd "$KB" && uv run kb tts synthesize \
    --text "$text" \
    --style "$STYLE" \
    --out "$dest" \
    --json >/dev/null)
}

synth obs_vo_title.mp3         "Traces. Logs. Metrics. One place."
synth obs_vo_problem.mp3       "Debugging. Across five tools. What could possibly go wrong."
synth obs_vo_drake_reject.mp3  "Grepping kubectl logs. For three hours."
synth obs_vo_drake_approve.mp3 "One O-Tel annotation. Done."
synth obs_vo_architecture.mp3  "Your pod speaks O-T-L-P. Alloy listens. Three signals. One dashboard."
synth obs_vo_grafana_tour.mp3  "Metrics. Logs. Traces. All in one pane of glass."
synth obs_vo_trace_view.mp3    "Click a trace. Every span. Every service. Every latency."
synth obs_vo_annotation.mp3    "One line. Full observability. Zero refactor."
synth obs_vo_multilang.mp3     "Python. Java. Node. dot-net. Go."
synth obs_vo_outro.mp3         "Happy debugging."

echo "done."
