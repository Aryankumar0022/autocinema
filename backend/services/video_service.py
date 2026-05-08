"""
AutoCinema Video Service
Ken Burns effect video clips from still images using FFmpeg.
"""

import os
import random
import subprocess
import asyncio
from functools import partial
from dotenv import load_dotenv

load_dotenv()

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "outputs")

KENBURNS_PRESETS = {
    "zoom_in": {
        "display_name": "Cinematic Zoom In",
        "description": "Slow zoom into the image center",
        "filter": "scale=4000:-1,zoompan=z=zoom+0.0015:d=144:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=1920x1080:fps=24",
    },
    "zoom_out": {
        "display_name": "Epic Zoom Out",
        "description": "Starts zoomed in, slowly reveals the frame",
        "filter": "scale=4000:-1,zoompan=z=1.5-on/144*0.5:d=144:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=1920x1080:fps=24",
    },
    "pan_left": {
        "display_name": "Smooth Pan Left",
        "description": "Gentle horizontal camera pan",
        "filter": "scale=4000:-1,zoompan=z=1.2:d=144:x=on*5:y=ih/2-(ih/zoom/2):s=1920x1080:fps=24",
    },
    "pan_up": {
        "display_name": "Vertical Pan Up",
        "description": "Slow upward camera tilt",
        "filter": "scale=4000:-1,zoompan=z=1.2:d=144:x=iw/2-(iw/zoom/2):y=ih/4+on*2:s=1920x1080:fps=24",
    },
}


class VideoService:
    @staticmethod
    async def generate_video(image_path: str, prompt: str, model_choice: str,
                             project_id: str, segment_index: int) -> dict:
        filename = f"proj_{project_id}_seg_{segment_index}_video.mp4"

        abs_image_path = image_path
        if image_path.startswith("/static/outputs/"):
            abs_image_path = os.path.join(STORAGE_DIR, os.path.basename(image_path))

        if not os.path.exists(abs_image_path):
            raise ValueError(f"Image not found: {abs_image_path}")

        preset_key = model_choice if model_choice in KENBURNS_PRESETS else "zoom_in"
        return await VideoService._generate_kenburns(abs_image_path, preset_key, filename)

    @staticmethod
    def _run_ffmpeg(cmd: list[str]) -> tuple[int, str, str]:
        """Run FFmpeg synchronously (called from thread pool)."""
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        return result.returncode, result.stdout.decode(errors="replace"), result.stderr.decode(errors="replace")

    @staticmethod
    async def _generate_kenburns(image_path: str, preset_key: str, filename: str) -> dict:
        preset = KENBURNS_PRESETS[preset_key]
        os.makedirs(STORAGE_DIR, exist_ok=True)
        output_path = os.path.join(STORAGE_DIR, filename)
        img = image_path.replace("\\", "/")

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img,
            "-vf", preset["filter"],
            "-t", "6",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-an",
            output_path,
        ]

        print(f"[VideoService] Ken Burns '{preset_key}' on {os.path.basename(image_path)}...")

        loop = asyncio.get_event_loop()
        returncode, stdout, stderr = await loop.run_in_executor(None, partial(VideoService._run_ffmpeg, cmd))

        if returncode != 0:
            err = stderr[-500:] if stderr else "Unknown FFmpeg error"
            print(f"[VideoService] FFmpeg error: {err}")
            raise RuntimeError(f"FFmpeg failed: {err}")

        if not os.path.exists(output_path):
            raise RuntimeError("FFmpeg produced no output file")

        print(f"[VideoService] Created {filename} ({os.path.getsize(output_path)} bytes)")
        return {
            "success": True,
            "model_name": f"{preset['display_name']} (Local FFmpeg)",
            "file_path": output_path,
            "url": f"/static/outputs/{filename}",
        }
