"""
Audio stitching pipeline.

Combines intro music, all TTS dialogue lines with silence gaps,
and outro music into a single normalized podcast MP3.

CRITICAL: mix_podcast is CPU-bound and synchronous.
Always call via: await asyncio.to_thread(mix_podcast, ...)
Never call directly in a FastAPI async context — it blocks the event loop
for 10-20 seconds, causing /status polling to hang and timeout.
"""

import os
import shutil

# Ensure ffmpeg/ffprobe are on PATH before pydub imports.
# pydub uses shutil.which() at import time and in mediainfo_json(),
# so the directory must be on PATH — setting AudioSegment.converter alone
# is not enough because pydub.utils.mediainfo_json resolves ffprobe via PATH.
def _ensure_ffmpeg_on_path():
    """Add ffmpeg directory to PATH if not already available."""
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return

    ext = ".exe" if os.name == "nt" else ""
    candidates = [
        # Full ffmpeg bundle (includes ffprobe)
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "ffmpeg", "ffmpeg-master-latest-win64-gpl", "bin"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "ffmpeg", "bin"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "ffmpeg", "bin"),
        # npm ffmpeg-static (ffmpeg only, no ffprobe — fallback)
        os.path.join(os.environ.get("APPDATA", ""), "npm", "node_modules", "ffmpeg-static"),
    ]
    for d in candidates:
        if os.path.isfile(os.path.join(d, f"ffmpeg{ext}")):
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
            break

_ensure_ffmpeg_on_path()

from pydub import AudioSegment
from pydub import effects

SILENCE_BETWEEN_LINES = 500   # ms — prevents robotic, rushed feel
INTRO_FADE_DURATION = 3000    # ms — music fades under first spoken line
OUTRO_FADE_DURATION = 3000    # ms


def mix_podcast(script: list, line_audio_paths: list, output_path: str):
    """Stitch intro + dialogue lines + outro into a final podcast MP3.

    CRITICAL: This function is CPU-bound and synchronous.
    Always call via: await asyncio.to_thread(mix_podcast, script, paths, output_path)
    Never call directly inside a FastAPI async context.
    """
    intro = AudioSegment.from_mp3("static/intro.mp3")
    outro = AudioSegment.from_mp3("static/outro.mp3")
    silence = AudioSegment.silent(duration=SILENCE_BETWEEN_LINES)

    # Fade intro music out over 3 seconds for a professional feel
    podcast_audio = intro[:6000].fade_out(INTRO_FADE_DURATION)

    for audio_path in line_audio_paths:
        line_audio = AudioSegment.from_mp3(audio_path)

        # Normalize sample rate on every line before appending.
        # edge-tts voices output different sample rates (e.g. 16kHz vs 24kHz).
        # Without this, pydub stitches silently but certain lines play warped.
        line_audio = (
            line_audio
            .set_frame_rate(24000)
            .set_channels(1)
            .set_sample_width(2)
        )

        podcast_audio += line_audio + silence

        # Free RAM by explicitly deleting the in-memory pydub object.
        # CRITICAL: Do NOT use os.remove(audio_path) — that destroys the per-line
        # TTS cache. The file on disk IS the cache. Only the in-memory object
        # needs to be released to stay within Render's 512MB RAM limit.
        del line_audio

    podcast_audio += outro.fade_out(OUTRO_FADE_DURATION)

    # Normalize final track — balances volume between HOST and EXPERT voices.
    # edge-tts voice models have different natural loudness levels.
    podcast_audio = effects.normalize(podcast_audio)

    podcast_audio.export(output_path, format="mp3")
