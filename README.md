# 🎬 AutoCinema

Welcome to **AutoCinema**! This is an open-source, cloud-driven AI video production platform. It allows anyone to turn a simple text script into a fully polished, vertical short-form video (9:16 aspect ratio) — perfectly suited for Instagram Reels, TikTok, and YouTube Shorts.

The best part? Your local computer doesn't need a powerful, expensive GPU. AutoCinema uses your machine simply as an **orchestrator** and delegates all the heavy AI workloads (like script writing, image generation, and voiceovers) to cloud APIs.

This guide is written for complete beginners. Follow along step-by-step to get your very own AI video generator running locally!

---

## 🛠️ Tech Stack & Architecture

AutoCinema is built using modern, popular technologies:

- **Backend (The Engine):** 
  - **Python & FastAPI**: Fast, modern Python web framework.
  - **SQLite & aiosqlite**: A lightweight, local database to store your project data.
  - **FFmpeg**: A powerful multimedia framework used to stitch the images, video, and audio together into the final MP4.
- **Frontend (The User Interface):** 
  - **React & Vite**: Extremely fast and modern way to build user interfaces.
  - **Tailwind CSS**: For styling the app with beautiful glassmorphism, gradients, and micro-animations.
  - **Zustand**: A lightweight state management tool for React.
- **AI Services (The Brains):**
  - **Script Analysis**: Google Gemini
  - **Image Generation**: Pollinations.ai (FLUX, Realism, Turbo) - *100% Free*
  - **Video Processing**: Local Ken Burns effects via FFmpeg
  - **Voiceover (TTS)**: Microsoft Edge Neural TTS - *100% Free*
  - **Background Music**: Pollinations.ai ElevenMusic - *100% Free*
  - **Subtitles**: Groq Cloud (Whisper-Large-v3-Turbo)

---

## 📁 Project Structure

Here is a quick overview of how the code is organized:

```text
autocinema/
├── backend/
│   ├── main.py              # The main entry point for the backend server
│   ├── database.py          # Code that talks to the local SQLite database
│   ├── api/
│   │   └── routes.py        # The API endpoints the frontend talks to
│   └── services/            # The core logic for AI generations
│       ├── gemini_service.py    # Analyzes your script and breaks it into scenes
│       ├── image_service.py     # Fetches AI images from Pollinations.ai
│       ├── video_service.py     # Adds camera motion (Ken Burns effect) to images
│       ├── audio_service.py     # Generates voiceovers and background music
│       ├── subtitle_service.py  # Generates word-by-word subtitle timestamps
│       └── ffmpeg_service.py    # Stitches everything into the final video
├── frontend/
│   ├── src/
│   │   ├── components/      # The UI blocks (buttons, progress bars, etc.)
│   │   ├── store/           # Where the app remembers its current state
│   │   ├── index.css        # The beautiful styles and animations
│   │   └── App.jsx          # The main screen of the application
│   └── vite.config.js       # Configuration for the frontend server
├── storage/                 # Where your generated images, audio, and videos are saved
├── .env.example             # A template file showing what API keys you need
└── requirements.txt         # The list of Python packages the backend needs
```

---

## 🚀 Step-by-Step Installation Guide

If you've never coded before, don't worry! Just follow these steps in order.

### Step 1: Install Required Software
Before we start, you need three pieces of software installed on your computer:
1. **Python (3.10 or newer)**: Download from [python.org](https://www.python.org/downloads/). 
   - *Important: When installing on Windows, make sure to check the box at the bottom that says **"Add Python to PATH"** before clicking Install.*
2. **Node.js (18 or newer)**: Download from [nodejs.org](https://nodejs.org/). This includes `npm`, which we need to run the user interface.
3. **FFmpeg**: This is required for processing the actual video and audio files. 
   - **Windows**: The easiest way is to open Command Prompt and type: `winget install ffmpeg`
   - **Mac**: Open Terminal and type: `brew install ffmpeg`
   - **Linux**: Open Terminal and type: `sudo apt install ffmpeg`

### Step 2: Download the Project
Open your terminal (Command Prompt, PowerShell, or Terminal) and run:
```bash
git clone https://github.com/Aryankumar0022/autocinema.git
cd autocinema
```

### Step 3: Set Up Your Environment Variables (API Keys)
AutoCinema uses a few free cloud AI services. You need to provide API keys so the app can communicate with them.
1. In the `autocinema` folder, find the file named `.env.example`.
2. Copy that file and rename the new copy to exactly `.env`.
3. Open `.env` in any text editor (like Notepad or VS Code).
4. Go to the following websites, sign up for a free account, and generate your API keys:
   - **Gemini API Key**: Get it from [Google AI Studio](https://aistudio.google.com/)
   - **Groq API Key**: Get it from [Groq Cloud](https://console.groq.com/)
5. Paste those keys into your `.env` file where indicated and save it. 
   - *(Note: Never share your .env file or upload it to the internet!)*

### Step 4: Start the Backend (Python)
The backend does all the heavy lifting and talks to the AI services.

1. Open a terminal inside the `autocinema` folder.
2. Create a virtual environment (this keeps the project's Python files isolated from the rest of your computer):
   - **Windows**: `python -m venv venv`
   - **Mac/Linux**: `python3 -m venv venv`
3. Activate the virtual environment:
   - **Windows**: `venv\Scripts\activate`
   - **Mac/Linux**: `source venv/bin/activate`
4. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the backend server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   *Success! Leave this terminal window open and running in the background.*

### Step 5: Start the Frontend (User Interface)
The frontend is the beautiful user interface you will interact with in your browser.

1. Open a **new, second terminal window**.
2. Navigate into the frontend folder of the project:
   ```bash
   cd path/to/autocinema/frontend
   ```
   *(Make sure to replace `path/to/autocinema` with the actual path to where you downloaded the project)*
3. Install the required Node packages:
   ```bash
   npm install
   ```
4. Start the frontend server:
   ```bash
   npm run dev
   ```

### Step 6: Create Your First Video!
1. Open your web browser (Chrome, Safari, Edge, etc.).
2. Go to the web address: **http://localhost:5173**
3. You will see the AutoCinema interface. Type in a script, click "Create Project", and follow the on-screen steps to generate images, add motion, create a voiceover, and render your final short-form video!

---

## 📝 License
This project is open-source under the MIT License. Feel free to modify and build upon it!
