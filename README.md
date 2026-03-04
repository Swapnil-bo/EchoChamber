<div align="center">

# EchoChamber

**Transform any URL, PDF, or Wikipedia page into a 5-minute AI podcast**

Two AI hosts — a skeptic and an expert — debate your content, producing a fully stitched audio podcast with intro/outro music, served through a real-time progress UI.

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Gemini](https://img.shields.io/badge/Gemini_Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

</div>

---

## How It Works

Paste a link. Get a podcast. The pipeline runs eight stages end-to-end:

```
                          EchoChamber Pipeline
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  USER INPUT                         FRONTEND (React + Vite)
  ┌─────────┐    POST /generate      ┌──────────────────────┐
  │ URL     │ ──────────────────────► │  InputForm.jsx       │
  │ PDF     │                         │  ProgressTracker.jsx │◄─── polls
  │ Wiki    │                         │  AudioPlayer.jsx     │     /status
  │ Text    │                         │  Transcript.jsx      │     every 2s
  └─────────┘                         └──────────────────────┘
                                               │
                    ┌──────────────────────────┘
                    ▼
  BACKEND (FastAPI + asyncio)
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │  Stage 1 ► Detect input type (URL / PDF / Wiki / text)  │
  │       │                                                 │
  │  Stage 2 ► Extract text                                 │
  │       │    BeautifulSoup │ PyMuPDF │ wikipedia-api       │
  │       │                                                 │
  │  Stage 3 ► Chunk & summarize (LangChain, ≤1500 words)  │
  │       │                                                 │
  │  Stage 4 ► Check script cache (MD5 hash lookup)         │
  │       │                                                 │
  │  Stage 5 ► Generate debate script (Gemini Flash)        │
  │       │    HOST (skeptic) vs EXPERT (enthusiast)         │
  │       │    16-20 turns, strict JSON output               │
  │       │                                                 │
  │  Stage 6 ► Synthesize TTS per line (edge-tts)           │
  │       │    Guy Neural ↔ Jenny Neural                     │
  │       │    Per-line cache + tenacity retry               │
  │       │                                                 │
  │  Stage 7 ► Mix & master audio (pydub + ffmpeg)          │
  │       │    Intro fade + dialogue + outro fade            │
  │       │    Sample rate normalization + volume balance    │
  │       │                                                 │
  │  Stage 8 ► Podcast ready! Serve MP3 + transcript        │
  │                                                         │
  └─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **LLM** | Gemini 2.0 Flash | Script generation (single structured call) |
| **TTS** | edge-tts | Two async voices — GuyNeural (host), JennyNeural (expert) |
| **Audio** | pydub + ffmpeg | Stitching, normalization, fade effects |
| **Text Extraction** | BeautifulSoup4, PyMuPDF, wikipedia-api | URL, PDF, and Wikipedia parsing |
| **Chunking** | LangChain text splitters + map_reduce | Summarize to 1500-word cap |
| **Backend** | FastAPI + asyncio | Async job pipeline with polling status |
| **Frontend** | React 18 + Vite + TailwindCSS | Real-time progress tracker UI |
| **Retry Logic** | tenacity | 3 attempts, exponential backoff for TTS |
| **Caching** | Dual-layer (script JSON + per-line TTS) | Saves API quota, instant re-runs |
| **Deploy** | Render (backend) + Vercel (frontend) | Free tier compatible |

---

## Project Structure

```
echochamber/
├── backend/
│   ├── main.py                  # FastAPI app, CORS, startup hooks, health endpoint
│   ├── routers/
│   │   └── podcast.py           # /generate and /status/{job_id} endpoints
│   ├── pipeline/
│   │   ├── extractor.py         # Auto-detect and extract text (URL/PDF/Wiki)
│   │   ├── chunker.py           # LangChain chunking + summarization
│   │   ├── script_generator.py  # Gemini Flash debate script generation
│   │   ├── tts_engine.py        # edge-tts with per-line cache + retry
│   │   └── audio_mixer.py       # pydub stitching, normalization, fades
│   ├── utils/
│   │   ├── cache.py             # Script-level JSON cache
│   │   └── job_store.py         # In-memory job status store
│   ├── static/
│   │   ├── intro.mp3            # Royalty-free intro music
│   │   └── outro.mp3            # Royalty-free outro music
│   ├── outputs/                 # Generated podcasts (gitignored)
│   ├── cache/                   # Cached scripts + TTS lines (gitignored)
│   ├── requirements.txt
│   └── build.sh                 # Render deployment script
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # App state: input → loading → result
│   │   ├── components/
│   │   │   ├── InputForm.jsx        # URL/PDF/Wiki input with example chips
│   │   │   ├── ProgressTracker.jsx  # Glass-box live pipeline status
│   │   │   ├── AudioPlayer.jsx      # HTML5 audio + error handling
│   │   │   └── Transcript.jsx       # HOST/EXPERT script preview
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── CLAUDE.md
```

---

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- ffmpeg ([install guide](https://ffmpeg.org/download.html)) — on Windows: `winget install Gyan.FFmpeg`
- A [Gemini API key](https://aistudio.google.com/apikey) (free tier: 1500 req/day)

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env            # Then edit with your API key (see below)

# Run the server
uvicorn main:app --reload --port 8000
```

The startup hook automatically creates `outputs/`, `cache/scripts/`, and `cache/tts_lines/` directories on first run.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

The frontend starts at `http://localhost:5173` and proxies API calls to the backend at `http://localhost:8000`.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `GEMINI_MODEL` | No | Model name (default: `gemini-2.5-flash-lite`) |
| `OUTPUT_DIR` | No | Directory for generated MP3s (default: `outputs`) |
| `CACHE_DIR` | No | Directory for cached data (default: `cache`) |
| `ALLOWED_ORIGINS` | No | CORS origins (default: `http://localhost:5173`) |

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
OUTPUT_DIR=outputs
CACHE_DIR=cache
ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (Vercel dashboard or `.env`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_BASE_URL` | Yes | Backend URL (default: `http://localhost:8000`) |

---

## The 8-Stage Pipeline

### Stage 1 — Input Detection
The backend auto-detects what the user submitted. No configuration needed — just paste and go.
- `.pdf` extension → PDF parser
- `wikipedia.org` in URL → Wikipedia API
- `http://` or `https://` → Web scraper
- Anything else → treated as raw text

### Stage 2 — Text Extraction
Each input type has a dedicated extractor:
- **URLs**: `requests` + BeautifulSoup — extracts `<p>` tags, strips nav/footer/scripts
- **PDFs**: PyMuPDF (`fitz`) — loops all pages, extracts text blocks
- **Wikipedia**: `wikipedia-api` with a proper User-Agent header (required or Wikipedia returns 403)

### Stage 3 — Chunking & Summarization
LangChain's `RecursiveCharacterTextSplitter` breaks the text into chunks. If the total exceeds 1500 words, a Gemini-powered map_reduce chain compresses it down. This prevents context window overruns on long documents like 50-page PDFs.

### Stage 4 — Cache Check
An MD5 hash of the processed text is compared against cached scripts in `cache/scripts/`. On a cache hit, the pipeline skips the LLM call entirely — saving API quota and returning instantly.

### Stage 5 — Script Generation
A single Gemini Flash call generates the full debate script. Two personas argue:
- **Alex (HOST)**: Skeptical, analytical, devil's advocate
- **Maya (EXPERT)**: Enthusiastic, deeply knowledgeable

The prompt enforces 16–20 alternating turns, natural spoken language, TTS-safe formatting (dashed acronyms like `L-L-M`, numbers as words), and strict JSON output. Safety settings use `BLOCK_ONLY_HIGH` — permissive enough for controversial articles, strict enough for production.

### Stage 6 — TTS Synthesis
Each script line is synthesized individually using Microsoft Edge's free TTS API:
- HOST → `en-US-GuyNeural` (deeper, authoritative tone)
- EXPERT → `en-US-JennyNeural` (warm, expressive tone)

Every line is cached by `MD5(speaker:line)` — re-runs only regenerate changed lines. `tenacity` handles connection drops with 3 retries and exponential backoff. The frontend shows live progress: *"Synthesizing audio (Line 4 of 18)..."*

### Stage 7 — Mix & Master
pydub stitches the final podcast:
1. Intro music with 3-second fade-out
2. All dialogue lines with 500ms silence between turns
3. Outro music with 3-second fade-out

Every line is normalized to 24kHz/mono/16-bit before appending (edge-tts outputs varying sample rates). Final volume is balanced with `pydub.effects.normalize()`. The mixer runs via `asyncio.to_thread()` to avoid blocking the FastAPI event loop.

### Stage 8 — Delivery
The final MP3 is served at `/audio/{job_id}.mp3`. The frontend receives both the audio URL and the full script JSON, rendering an audio player with the transcript below it.

---

## Deployment

### Backend → Render

- Free tier (512MB RAM) — the audio mixer explicitly releases memory after each line to stay within limits
- ffmpeg is pre-installed on Render's native Python environment
- Set all env vars in the Render dashboard
- `outputs/` and `cache/` are ephemeral (wiped on spin-down) — the frontend handles this gracefully

### Frontend → Vercel

- Set `VITE_API_BASE_URL` to your Render backend URL
- Standard Vite + React deploy, no special config needed
- The `/health` pre-flight check shows a "Backend waking up..." banner during Render cold starts (30–50s after 15min idle)

---

## Architecture Decisions

| Decision | Rationale |
|---|---|
| **Single Gemini call** (not two agents) | 50% less API quota, more coherent dialogue, simpler error handling |
| **`BLOCK_ONLY_HIGH`** safety setting | Handles controversial articles without blocking valid inputs |
| **Dual-layer caching** | Script cache saves LLM quota; TTS cache saves synthesis time |
| **`asyncio.to_thread`** for audio mixing | Prevents CPU-bound pydub from blocking the async event loop |
| **`del line_audio`** after each append | Keeps RAM at O(1) instead of O(n) — critical for 512MB Render limit |
| **Native HTML5 `<audio>`** over wavesurfer.js | Zero bundle cost, no backend preprocessing needed |
| **`/health` endpoint** | Turns a confusing 50-second hang into a transparent "waking up" message |
| **Per-line TTS cache on disk** | Makes audio iteration near-instant — only changed lines regenerate |

---

<div align="center">

Built as a portfolio project for AI/ML Product Management roles.

</div>
