"""
EchoChamber — FastAPI backend entry point.

Responsibilities:
1. CORS middleware (Vercel ↔ Render communication)
2. Startup directory initialization
3. Health check endpoint (Render cold start UX)
4. Static file serving for generated audio
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers.podcast import router as podcast_router

load_dotenv()

app = FastAPI(title="EchoChamber", version="1.0.0")

# --- CORS Middleware ---
# Required for Vercel frontend ↔ Render backend communication.
# Without this, browsers silently block all cross-origin requests.
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        allowed_origins,
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Create required directories if they don't exist.
    These are gitignored and won't exist on a fresh clone or Render deploy."""
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("cache/scripts", exist_ok=True)
    os.makedirs("cache/tts_lines", exist_ok=True)


@app.get("/health")
async def health():
    """Health check endpoint.
    The React frontend pings this before starting generation.
    If Render has been idle 15+ minutes, the instance needs 30-50s to boot.
    The frontend detects a slow/failed health check and shows a
    'Backend waking up...' message instead of silently hanging."""
    return {"status": "ok"}


# Serve generated podcast files at /audio/<filename>.mp3
app.mount("/audio", StaticFiles(directory="outputs"), name="audio")

# Register podcast generation routes
app.include_router(podcast_router)
