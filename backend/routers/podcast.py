"""
Podcast API endpoints.

POST /generate — accepts input, fires async pipeline, returns job_id immediately.
GET /status/{job_id} — returns current job state for frontend polling.
"""

import asyncio
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pipeline.extractor import extract_text
from pipeline.chunker import chunk_and_summarize
from pipeline.script_generator import generate_script
from pipeline.tts_engine import generate_line_audio
from pipeline.audio_mixer import mix_podcast
from utils.cache import get_cached_script, save_script_cache
from utils.job_store import create_job, update_job, complete_job, fail_job, get_job

router = APIRouter()


class GenerateRequest(BaseModel):
    input: str


@router.post("/generate")
async def generate_podcast(request: GenerateRequest):
    """Start podcast generation as a background task.
    Returns job_id immediately so the frontend can poll for progress."""
    job_id = str(uuid.uuid4())
    create_job(job_id)

    # Fire background task — never blocks the response
    asyncio.create_task(run_pipeline(job_id, request.input))

    return {"job_id": job_id}


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Return current job state for frontend polling (every 2 seconds)."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


async def run_pipeline(job_id: str, user_input: str):
    """Full podcast generation pipeline — runs as an async background task.

    Emits progress messages at each stage so the frontend ProgressTracker
    can show a glass-box view of pipeline state.
    """
    try:
        # Stage 1: Detect input type
        update_job(job_id, "Detecting input type...")

        # Stage 2: Extract text
        update_job(job_id, "Extracting text...")
        text = await asyncio.to_thread(extract_text, user_input)

        # Stage 3: Chunk and summarize
        update_job(job_id, "Chunking and summarizing content...")
        summarized = await asyncio.to_thread(chunk_and_summarize, text)

        # Stage 4: Check script cache
        update_job(job_id, "Checking script cache...")
        script = get_cached_script(summarized)

        if script is None:
            # Stage 5: Generate script via Gemini
            update_job(job_id, "Agents debating (Gemini Flash)...")
            script = await asyncio.to_thread(generate_script, summarized)
            save_script_cache(summarized, script)

        # Stage 6: Synthesize audio line by line
        line_audio_paths = []
        total_lines = len(script)

        for i, entry in enumerate(script):
            update_job(
                job_id,
                f"Synthesizing audio (Line {i + 1} of {total_lines})...",
            )
            path = await generate_line_audio(entry["speaker"], entry["line"])
            line_audio_paths.append(path)

        # Stage 7: Mix and master
        update_job(job_id, "Mixing and mastering audio...")
        output_filename = f"{job_id}.mp3"
        output_path = f"outputs/{output_filename}"

        # CRITICAL: mix_podcast is CPU-bound — offload to thread pool
        # to keep the FastAPI event loop responsive for /status polling.
        await asyncio.to_thread(mix_podcast, script, line_audio_paths, output_path)

        # Stage 8: Complete
        audio_url = f"/audio/{output_filename}"
        complete_job(job_id, audio_url, script)

    except Exception as e:
        fail_job(job_id, str(e))
