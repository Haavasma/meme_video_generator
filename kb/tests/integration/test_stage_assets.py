"""Integration test for scripts/stage_assets.py voiceover + media handling.

Runs the script as a subprocess with a stubbed kb tts command so the test
doesn't touch edge-tts / network.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STAGE_SCRIPT = PROJECT_ROOT / "scripts" / "stage_assets.py"


def _write_wav(path: Path, duration_sec: float = 0.2) -> None:
    import struct
    import wave

    rate = 16000
    n = int(rate * duration_sec)
    silence = struct.pack("<" + "h" * n, *([0] * n))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(silence)


@pytest.fixture
def fake_uv_bin(tmp_path: Path) -> Path:
    """Create a fake `uv` executable earlier on PATH that writes a dummy mp3 for tts synthesize."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "uv"
    fake.write_text(
        "#!/usr/bin/env bash\n"
        # args: `uv run kb tts synthesize --text X --style Y --out Z --json [--voice V]`
        "set -e\n"
        "out=\"\"\n"
        "while [[ $# -gt 0 ]]; do\n"
        "  case \"$1\" in\n"
        "    --out) out=\"$2\"; shift 2 ;;\n"
        "    *) shift ;;\n"
        "  esac\n"
        "done\n"
        "if [[ -z \"$out\" ]]; then echo 'missing --out' >&2; exit 2; fi\n"
        "mkdir -p \"$(dirname \"$out\")\"\n"
        # Fake mp3 header
        "printf 'ID3\\x03\\x00\\x00\\x00\\x00\\x00\\x00' > \"$out\"\n"
        "printf '\\x00%.0s' {1..128} >> \"$out\"\n"
        'echo \'{"ok":true}\'\n'
    )
    fake.chmod(0o755)
    return bin_dir


class TestStageAssets:
    @pytest.mark.integration
    def test_voiceover_layer_replaced_with_audio(
        self, tmp_path: Path, fake_uv_bin: Path
    ) -> None:
        spec = {
            "meta": {
                "title": "vo test",
                "fps": 30,
                "width": 1920,
                "height": 1080,
                "backgroundColor": "#000000",
            },
            "scenes": [
                {
                    "type": "caption_only",
                    "startSec": 0,
                    "durationSec": 2,
                    "layers": [
                        {"layerType": "caption", "text": "hi", "position": "bottom",
                         "style": "impact", "fontSize": 64, "color": "#fff",
                         "strokeColor": "#000", "fadeInFrames": 6},
                        {"layerType": "voiceover", "text": "it was so simple",
                         "style": "dramatic", "volume": 0.8, "startOffsetSec": 0},
                    ],
                }
            ],
        }
        in_path = tmp_path / "in.json"
        out_path = tmp_path / "out.json"
        in_path.write_text(json.dumps(spec), encoding="utf-8")

        env = os.environ.copy()
        env["PATH"] = f"{fake_uv_bin}:{env['PATH']}"
        result = subprocess.run(
            [sys.executable, str(STAGE_SCRIPT), str(in_path), str(out_path)],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, result.stderr

        staged = json.loads(out_path.read_text(encoding="utf-8"))
        layers = staged["scenes"][0]["layers"]
        assert layers[0]["layerType"] == "caption"
        # Voiceover must be rewritten as an audio layer with a relative asset path.
        assert layers[1]["layerType"] == "audio"
        assert layers[1]["localPath"].startswith("assets/voiceover_")
        assert layers[1]["volume"] == 0.8

        # The mp3 file must actually exist in video/public/assets/.
        mp3_rel = layers[1]["localPath"]
        mp3_abs = PROJECT_ROOT / "video" / "public" / mp3_rel
        assert mp3_abs.exists()
        mp3_abs.unlink()  # cleanup the side effect

    @pytest.mark.integration
    def test_absolute_localpath_copied_to_public(
        self, tmp_path: Path, fake_uv_bin: Path
    ) -> None:
        src_wav = tmp_path / "my_sound.wav"
        _write_wav(src_wav)
        spec = {
            "meta": {"title": "t", "fps": 30, "width": 1920, "height": 1080, "backgroundColor": "#000"},
            "scenes": [
                {
                    "type": "caption_only",
                    "startSec": 0,
                    "durationSec": 1,
                    "layers": [
                        {"layerType": "audio", "localPath": str(src_wav),
                         "volume": 1, "startOffsetSec": 0},
                    ],
                }
            ],
        }
        in_path = tmp_path / "in.json"
        out_path = tmp_path / "out.json"
        in_path.write_text(json.dumps(spec), encoding="utf-8")

        env = os.environ.copy()
        env["PATH"] = f"{fake_uv_bin}:{env['PATH']}"
        result = subprocess.run(
            [sys.executable, str(STAGE_SCRIPT), str(in_path), str(out_path)],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, result.stderr

        staged = json.loads(out_path.read_text(encoding="utf-8"))
        layer = staged["scenes"][0]["layers"][0]
        assert layer["localPath"] == "assets/my_sound.wav"

        staged_file = PROJECT_ROOT / "video" / "public" / layer["localPath"]
        assert staged_file.exists()
        staged_file.unlink()  # cleanup

    @pytest.mark.integration
    def test_voiceover_missing_text_rejected(
        self, tmp_path: Path, fake_uv_bin: Path
    ) -> None:
        spec = {
            "meta": {"title": "t", "fps": 30, "width": 1920, "height": 1080, "backgroundColor": "#000"},
            "scenes": [
                {
                    "type": "caption_only",
                    "startSec": 0,
                    "durationSec": 1,
                    "layers": [
                        {"layerType": "voiceover", "text": "   ", "style": "narrator"},
                    ],
                }
            ],
        }
        in_path = tmp_path / "in.json"
        out_path = tmp_path / "out.json"
        in_path.write_text(json.dumps(spec), encoding="utf-8")

        env = os.environ.copy()
        env["PATH"] = f"{fake_uv_bin}:{env['PATH']}"
        result = subprocess.run(
            [sys.executable, str(STAGE_SCRIPT), str(in_path), str(out_path)],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode != 0
