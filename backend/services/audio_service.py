"""
AutoCinema Audio Service
Cloud voiceover (Edge TTS) and background music (FFmpeg local).
"""

import os
import asyncio
import edge_tts
from dotenv import load_dotenv

load_dotenv()

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
        """Generate background music using FFmpeg ambient drone pad (instant, no network)."""
        filename = f"proj_{project_id}_music.mp3"
        output_path = os.path.join(STORAGE_DIR, filename)
        os.makedirs(STORAGE_DIR, exist_ok=True)
        dur = max(int(min(duration_seconds, 120)), 5)  # At least 5 seconds

        print(f"[Audio] Generating {dur}s ambient music via FFmpeg...")
        try:
            fade_out_start = max(dur - 3, 1)
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"sine=frequency=220:duration={dur}",
                "-f", "lavfi", "-i", f"sine=frequency=330:duration={dur}",
                "-f", "lavfi", "-i", f"sine=frequency=440:duration={dur}",
                "-f", "lavfi", "-i", f"anoisesrc=d={dur}:c=pink:r=44100:a=0.008",
                "-filter_complex",
                f"[0][1][2][3]amix=inputs=4:duration=longest,volume=0.15,afade=t=in:st=0:d=3,afade=t=out:st={fade_out_start}:d=3",
                "-c:a", "libmp3lame", "-b:a", "128k",
                output_path,
            ]
            print(f"[Audio] CMD: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0 and os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"[Audio] ✓ Music created: {size} bytes")
                return {
                    "success": True,
                    "file_path": output_path,
                    "url": f"/static/outputs/{filename}",
                    "source": "Ambient Pad",
                }
            else:
                err_msg = stderr.decode(errors='replace')[-500:] if stderr else 'Unknown'
                print(f"[Audio] ✗ FFmpeg failed (rc={process.returncode}): {err_msg}")
                return {"success": False, "error": f"FFmpeg failed: {err_msg}"}
        except Exception as e:
            print(f"[Audio] ✗ Exception: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def list_voices() -> list[dict]:
        """Return available voice options."""
        return [
            {"id": k, "name": k.replace("_", " ").title(), "voice_id": v}
            for k, v in VOICE_MAP.items()
        ]
