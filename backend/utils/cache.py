"""
Script-level caching.

Caches generated JSON scripts keyed by MD5 hash of the input text.
Saves Gemini API quota during development — re-running the same article
skips the LLM call entirely. Essential for conserving the 1500 req/day free tier.
"""

import hashlib
import json
import os

SCRIPT_CACHE_DIR = "cache/scripts"


def get_cache_key(text: str) -> str:
    """Generate an MD5 hash key from the input text."""
    return hashlib.md5(text.encode()).hexdigest()


def get_cached_script(text: str):
    """Returns cached script JSON if it exists, else None."""
    path = f"{SCRIPT_CACHE_DIR}/{get_cache_key(text)}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def save_script_cache(text: str, script: list):
    """Saves generated script JSON keyed by content hash."""
    os.makedirs(SCRIPT_CACHE_DIR, exist_ok=True)
    with open(f"{SCRIPT_CACHE_DIR}/{get_cache_key(text)}.json", "w") as f:
        json.dump(script, f)
