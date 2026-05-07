"""
AutoCinema Subtitle Service
Word-level transcription using Groq Cloud API (Whisper-Large-v3-Turbo).
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class SubtitleService:
    @staticmethod
    async def transcribe(audio_path: str) -> dict:
        """
        Transcribe an audio file using Groq's Whisper endpoint.
        Returns word-level timestamps for dynamic subtitle animation.
        """
        if not GROQ_API_KEY:
            return {"success": False, "error": "GROQ_API_KEY not set", "words": []}

        if not os.path.exists(audio_path):
            return {"success": False, "error": f"Audio file not found: {audio_path}", "words": []}

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

        try:
            with open(audio_path, "rb") as f:
                files = {"file": (os.path.basename(audio_path), f, "audio/mpeg")}
                data = {
                    "model": "whisper-large-v3-turbo",
                    "response_format": "verbose_json",
                    "timestamp_granularities[]": "word",
                }
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(url, headers=headers, files=files, data=data)

            if response.status_code != 200:
                return {"success": False, "error": f"Groq returned {response.status_code}: {response.text[:300]}", "words": []}

            result = response.json()
            words = []
            for w in result.get("words", []):
                words.append({
                    "word": w.get("word", ""),
                    "start": round(w.get("start", 0), 3),
                    "end": round(w.get("end", 0), 3),
                })

            return {
                "success": True,
                "full_text": result.get("text", ""),
                "words": words,
                "duration": result.get("duration", 0),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "words": []}
