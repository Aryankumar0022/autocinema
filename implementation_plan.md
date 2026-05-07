# AutoCinema — Implementation Plan

## Overview
Cloud-driven video production platform where the local machine acts purely as an orchestrator. All heavy AI computations (image gen, video gen, TTS, music gen, transcription) are offloaded to cloud APIs.

---

## Phase 1: Backend Foundation
**Goal:** FastAPI server with all service modules, SQLite database, and API routes.

### 1.1 Project Scaffolding
- Create directory structure under `d:\autocinema`
- `requirements.txt` with all dependencies
- `.env.example` with placeholder API keys
- `backend/main.py` — FastAPI app with CORS, static file mounting, lifespan

### 1.2 Database Layer (`backend/database.py`)
- SQLite via `aiosqlite`
- Tables: `projects`, `segments`, `assets`
- CRUD operations for project state persistence

### 1.3 Service Modules
| Service | File | Cloud Provider | Model |
|---------|------|----------------|-------|
| Script Analysis | `gemini_service.py` | Google AI Studio | Gemini 1.5 Flash |
| Image Generation | `image_service.py` | Together AI + HF | FLUX.1 / SD 3.5 / SDXL |
| Video Generation | `video_service.py` | HF / Replicate | Hunyuan / SVD |
| Voiceover | `audio_service.py` | Microsoft Edge TTS | Neural voices |
| Background Music | `audio_service.py` | HF Inference | MusicGen-Melody |
| Subtitles | `subtitle_service.py` | Groq Cloud | Whisper-Large-v3-Turbo |
| Final Render | `ffmpeg_service.py` | Local FFmpeg | CPU stitching |

### 1.4 API Routes (`backend/api/routes.py`)
- `POST /api/projects` — Create new project
- `GET /api/projects` — List all projects
- `GET /api/projects/{id}` — Get project details
- `POST /api/projects/{id}/analyze` — Analyze script with Gemini
- `POST /api/projects/{id}/segments/{seg}/images` — Generate image pair
- `POST /api/projects/{id}/segments/{seg}/select-image` — Select preferred image
- `POST /api/projects/{id}/segments/{seg}/video` — Generate video
- `POST /api/projects/{id}/audio` — Generate voiceover + music
- `POST /api/projects/{id}/subtitles` — Generate word-level subtitles
- `POST /api/projects/{id}/render` — Final FFmpeg render
- `GET /api/projects/{id}/status` — Poll project status
- WebSocket `/ws/projects/{id}` — Real-time progress updates

---

## Phase 2: Frontend (React + Vite + Tailwind + shadcn/ui)
**Goal:** Premium single-page workspace with step-by-step wizard flow.

### 2.1 Scaffolding
- Vite + React + TypeScript
- Tailwind CSS v4
- shadcn/ui components
- Zustand for state management

### 2.2 Core Components
| Component | Purpose |
|-----------|---------|
| `Dashboard.jsx` | Project list + new project creation |
| `Workspace.jsx` | Main orchestration view (step wizard) |
| `ScriptEditor.jsx` | Paste/edit script, trigger analysis |
| `SegmentViewer.jsx` | View analyzed segments with prompts |
| `ImagePicker.jsx` | Side-by-side image comparison (2 options) |
| `VideoGenerator.jsx` | Model selection + 30s countdown timer |
| `AudioPanel.jsx` | Voice selection + music preview |
| `RenderProgress.jsx` | Final render progress with live logs |
| `ProjectLoader.jsx` | Save & resume projects |

### 2.3 Design System
- Dark mode default with glassmorphism cards
- Purple/cyan gradient accent palette
- Smooth micro-animations (Framer Motion)
- 9:16 aspect ratio previews throughout

---

## Phase 3: Integration & WebSocket
- Real-time progress updates via WebSocket
- Error handling with retry logic
- Auto-timeout (30s) for video model selection

---

## Phase 4: Polish
- Loading skeletons
- Toast notifications
- Keyboard shortcuts
- Mobile-responsive layout

---

## Phase 5: Testing & Documentation
- API endpoint testing
- README with setup instructions
