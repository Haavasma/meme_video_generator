"""Text-to-speech synthesis for meme voiceovers.

Uses Microsoft Edge's TTS via the `edge-tts` package (free, no API key). Runs
synchronously around edge-tts's async API. Results cached to disk keyed by
sha256(text, style, voice, rate, pitch) — reruns never re-synthesize.

Five style presets shape voice + prosody; callers may also override `voice`
directly for total control.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TtsStyle:
    """Voice + prosody bundle for a single delivery style."""

    voice: str
    rate: str  # e.g. "+0%", "-20%"
    pitch: str  # e.g. "+0Hz", "-3Hz"


# Picked to contrast cleanly for meme delivery. All voices verified available
# on the Edge TTS service as of 2026-04-15. Callers may override voice.
STYLE_PRESETS: dict[str, TtsStyle] = {
    "narrator": TtsStyle(voice="en-US-GuyNeural", rate="+0%", pitch="+0Hz"),
    # Dramatic: British narrator, near-neutral pace. Earlier -20% felt sluggish
    # in montage-style videos; callers who want a slower read can pass --rate.
    "dramatic": TtsStyle(voice="en-GB-RyanNeural", rate="+0%", pitch="-2Hz"),
    "sarcastic": TtsStyle(voice="en-US-EricNeural", rate="+10%", pitch="+0Hz"),
    "excited": TtsStyle(voice="en-US-AnaNeural", rate="+15%", pitch="+3Hz"),
    "villain": TtsStyle(voice="en-GB-ThomasNeural", rate="-15%", pitch="-5Hz"),
}

DEFAULT_STYLE = "narrator"


def resolve_style(name: str | None) -> TtsStyle:
    """Return the style named by `name`, falling back to the default narrator style."""
    if not name or name not in STYLE_PRESETS:
        return STYLE_PRESETS[DEFAULT_STYLE]
    return STYLE_PRESETS[name]


@runtime_checkable
class TtsSynthesizer(Protocol):
    """Produce an mp3 at `output_path` narrating `text` in the chosen style."""

    def synthesize(
        self,
        *,
        text: str,
        style: str,
        output_path: Path,
        voice: str | None = None,
        rate: str | None = None,
        pitch: str | None = None,
    ) -> Path: ...


class EdgeTtsSynthesizer:
    """Edge-TTS-backed synthesizer with disk cache."""

    def __init__(self, *, cache_dir: Path) -> None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_dir = cache_dir

    def synthesize(
        self,
        *,
        text: str,
        style: str,
        output_path: Path,
        voice: str | None = None,
        rate: str | None = None,
        pitch: str | None = None,
    ) -> Path:
        if not text.strip():
            raise ValueError("text must be non-empty")

        resolved = resolve_style(style)
        effective_voice = voice or resolved.voice
        effective_rate = rate or resolved.rate
        effective_pitch = pitch or resolved.pitch
        cache_path = self._cache_path(
            text=text,
            voice=effective_voice,
            rate=effective_rate,
            pitch=effective_pitch,
        )

        if not cache_path.exists():
            self._synthesize_to_cache(
                text=text,
                voice=effective_voice,
                rate=effective_rate,
                pitch=effective_pitch,
                cache_path=cache_path,
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(cache_path, output_path)
        return output_path

    # --- internals ---------------------------------------------------------

    def _cache_path(self, *, text: str, voice: str, rate: str, pitch: str) -> Path:
        key = hashlib.sha256(
            f"{text}|{voice}|{rate}|{pitch}".encode("utf-8")
        ).hexdigest()[:32]
        return self._cache_dir / f"{key}.mp3"

    def _synthesize_to_cache(
        self,
        *,
        text: str,
        voice: str,
        rate: str,
        pitch: str,
        cache_path: Path,
    ) -> None:
        import edge_tts

        async def _run() -> None:
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(str(cache_path))

        try:
            asyncio.run(_run())
        except RuntimeError:
            # Nested loop (e.g. in pytest-asyncio context) — fall back to a fresh loop.
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_run())
            finally:
                loop.close()
        # Edge-TTS sometimes returns a 0-byte file on transient failures without
        # raising. Treat empty output as a hard failure so callers don't silently
        # ship a broken mp3.
        if not cache_path.exists() or cache_path.stat().st_size == 0:
            if cache_path.exists():
                cache_path.unlink()
            raise RuntimeError(
                f"edge-tts produced no audio for voice={voice!r} text={text[:40]!r}"
            )
