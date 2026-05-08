# 🎬 AutoCinema

Cloud-driven AI video production platform. Turn any script into a polished vertical short-form video (9:16) — ready for Instagram Reels, TikTok, and YouTube Shorts.

Your local machine acts purely as an **orchestrator**; all heavy AI workloads are offloaded to cloud APIs.

---

## ✨ Features

| Capability | Cloud Provider | Model |
|---|---|---|
| Script Analysis | Google AI Studio | Gemini 1.5 Flash |
| Image Generation | Together AI / HF | FLUX.1 / SD 3.5 / SDXL |
| Video Generation | Hugging Face | Hunyuan / SVD |
| Voiceover (TTS) | Microsoft Edge TTS | Neural voices |
| Background Music | Hugging Face | MusicGen |
| Subtitles | Groq Cloud | Whisper-Large-v3-Turbo |
| Final Render | Local FFmpeg | CPU stitching |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **FFmpeg** installed and on your system PATH

### 1. Clone & configure

```bash
git clone <your-repo-url>
cd autocinema
cp .env.example .env
# Fill in your API keys in .env
```

### 2. Backend setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd frontend
npm install
cd ..
```

### 4. Run the app

Open **two terminals**:

```bash
# Terminal 1 — Backend (port 8000)
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend (port 5173)
cd frontend && npm run dev
```

Open **http://localhost:5173** in your browser.

---

## 🔑 API Keys

Create a `.env` file at the project root (see `.env.example`):

| Key | Where to get it (free) |
|---|---|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) |
| `TOGETHER_API_KEY` | [Together AI](https://www.together.ai/) ($25 free credits) |
| `HF_API_KEY` | [Hugging Face](https://huggingface.co/settings/tokens) |
| `GROQ_API_KEY` | [Groq Cloud](https://console.groq.com/) |

---

## 📁 Project Structure

```
autocinema/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLite async database layer
│   ├── api/
│   │   └── routes.py        # All REST endpoints
│   └── services/
│       ├── gemini_service.py    # Script analysis (Gemini)
│       ├── image_service.py     # Image generation (FLUX/SD/SDXL)
│       ├── video_service.py     # Video generation (Hunyuan/SVD)
│       ├── audio_service.py     # TTS + music generation
│       ├── subtitle_service.py  # Whisper transcription (Groq)
│       └── ffmpeg_service.py    # Final video rendering
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css            # Design system
│   │   ├── store/projectStore.js
│   │   └── components/          # React UI components
│   └── vite.config.js
├── storage/                 # Generated assets (gitignored)
├── .env.example             # API key template
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🛠️ Tech Stack

- **Backend:** FastAPI · Python · aiosqlite · SQLite
- **Frontend:** React · Vite · Tailwind CSS v4 · Zustand
- **Design:** Glassmorphism · Purple/cyan gradients · Micro-animations

---

## 📝 License

MIT
