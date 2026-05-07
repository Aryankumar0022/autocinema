"""
AutoCinema Audio Service
Cloud voiceover (Edge TTS) and background music (MusicGen via HF).
"""

import os
import edge_tts
import httpx
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "outputs")

VOICE_MAP = {
    "female_warm": "en-US-JennyNeural",
    "female_professional": "en-US-AriaNeural",
    "male_deep": "en-US-GuyNeural",
    "male_news": "en-US-ChristopherNeural",
    "female_friendly": "en-US-SaraNeural",
    "male_casual": "en-US-DavisNeural",
}


class AudioService:
    @staticmethod
    async def generate_voiceover(text: str, voice_name: str, project_id: str) -> dict:
        """Generate voiceover MP3 via Microsoft Edge Neural TTS cloud."""
        selected_voice = VOICE_MAP.get(voice_name, "en-US-JennyNeural")
        filename = f"proj_{project_id}_voiceover.mp3"
        output_path = os.path.join(STORAGE_DIR, filename)
        os.makedirs(STORAGE_DIR, exist_ok=True)

        communicate = edge_tts.Communicate(text, selected_voice)
        await communicate.save(output_path)

        return {
            "success": True,
            "voice": selected_voice,
            "file_path": output_path,
            "url": f"/static/outputs/{filename}",
        }

    @staticmethod
    async def generate_music(mood_prompt: str, project_id: str, duration_seconds: float = 30.0) -> dict:
        """Generate background music using MusicGen-Melody via HF Inference API."""
        if not HF_API_KEY:
            return {"success": False, "error": "HF_API_KEY not set"}

        filename = f"proj_{project_id}_music.wav"
        output_path = os.path.join(STORAGE_DIR, filename)
        os.makedirs(STORAGE_DIR, exist_ok=True)

        url = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {
            "inputs": mood_prompt,
            "parameters": {"max_new_tokens": int(duration_seconds * 50)},
        }

        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    return {
                        "success": True,
                        "file_path": output_path,
                        "url": f"/static/outputs/{filename}",
                    }
                else:
                    return {"success": False, "error": f"HF returned {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def list_voices() -> list[dict]:
        """Return available voice options."""
        return [
            {"id": k, "name": k.replace("_", " ").title(), "voice_id": v}
            for k, v in VOICE_MAP.items()
        ]
