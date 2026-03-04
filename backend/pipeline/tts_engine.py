"""
Async TTS engine with per-line caching and retry logic.

Uses edge-tts (Microsoft Edge's free TTS API) with two distinct voices:
- HOST (Alex): en-US-GuyNeural — deeper, authoritative tone
- EXPERT (Maya): en-US-JennyNeural — warm, expressive tone

Per-line cache rationale: During audio tuning, you'll re-run the stitching
pipeline constantly. Without this cache, all 18 TTS lines regenerate every run.
With it, only changed lines regenerate. Iteration becomes near-instant.
"""

import hashlib
import os

import edge_tts
from tenacity import retry, stop_after_attempt, wait_exponential

VOICE_MAP = {
    "HOST": "en-US-GuyNeural",
    "EXPERT": "en-US-JennyNeural",
}

TTS_CACHE_DIR = "cache/tts_lines"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
async def generate_line_audio(speaker: str, line: str) -> str:
    """Generate TTS for a single script line.

    Checks per-line cache first — only calls edge-tts on a cache miss.
    Returns the path to the generated .mp3 file.
    tenacity handles edge-tts connection drops (3 attempts, exponential backoff).
    """
    cache_key = hashlib.md5(f"{speaker}:{line}".encode()).hexdigest()
    output_path = f"{TTS_CACHE_DIR}/{cache_key}.mp3"

    if os.path.exists(output_path):
        return output_path  # Cache hit — skip edge-tts entirely

    voice = VOICE_MAP[speaker]
    communicate = edge_tts.Communicate(line, voice)
    await communicate.save(output_path)
    return output_path
