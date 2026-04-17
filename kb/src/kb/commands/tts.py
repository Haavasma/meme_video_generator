"""`kb tts synthesize` — render narration to an mp3 via edge-tts."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from kb.commands._helpers import emit
from kb.config import Config
from kb.tts import DEFAULT_STYLE, STYLE_PRESETS, EdgeTtsSynthesizer

tts_app = typer.Typer(
    name="tts",
    help="Text-to-speech synthesis for meme voiceovers (edge-tts).",
    no_args_is_help=True,
)


@tts_app.command("synthesize")
def synthesize_command(
    text: Annotated[str, typer.Option("--text", help="Narration text")],
    out: Annotated[Path, typer.Option("--out", help="Output mp3 path")],
    style: Annotated[
        str,
        typer.Option(
            "--style",
            help=f"Style preset: one of {', '.join(STYLE_PRESETS)}",
        ),
    ] = DEFAULT_STYLE,
    voice: Annotated[
        str | None,
        typer.Option("--voice", help="Override voice (e.g. en-GB-LibbyNeural)"),
    ] = None,
    rate: Annotated[
        str | None,
        typer.Option("--rate", help="Override rate, e.g. '+10%' or '-15%'"),
    ] = None,
    pitch: Annotated[
        str | None,
        typer.Option("--pitch", help="Override pitch, e.g. '+3Hz' or '-5Hz'"),
    ] = None,
    as_json: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    cfg = Config()  # type: ignore[call-arg]
    cache_dir = cfg.assets_dir / ".tts_cache"
    synth = EdgeTtsSynthesizer(cache_dir=cache_dir)
    resolved = synth.synthesize(
        text=text, style=style, output_path=out, voice=voice, rate=rate, pitch=pitch,
    )

    preset = STYLE_PRESETS.get(style, STYLE_PRESETS[DEFAULT_STYLE])
    payload = {
        "text": text,
        "style": style if style in STYLE_PRESETS else DEFAULT_STYLE,
        "voice": voice or preset.voice,
        "rate": rate or preset.rate,
        "pitch": pitch or preset.pitch,
        "output_path": str(resolved.resolve()),
        "file_size_bytes": resolved.stat().st_size,
    }
    emit(payload, as_json=as_json)


@tts_app.command("voices")
def voices_command(
    as_json: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """List the 5 style presets and their voice/rate/pitch mapping."""
    payload = {
        "default_style": DEFAULT_STYLE,
        "presets": {
            name: {"voice": s.voice, "rate": s.rate, "pitch": s.pitch}
            for name, s in STYLE_PRESETS.items()
        },
    }
    emit(payload, as_json=as_json)
