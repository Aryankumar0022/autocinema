"""
AutoCinema Video Service
Image-to-video generation using HunyuanVideo and Stable Video Diffusion.
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "outputs")


class VideoService:
    @staticmethod
    async def generate_video(image_path: str, prompt: str, model_choice: str,
                             project_id: str, segment_index: int) -> dict:
        filename = f"proj_{project_id}_seg_{segment_index}_video.mp4"
        try:
            if model_choice == "hunyuan":
                video_bytes = await VideoService._generate_hunyuan(image_path, prompt)
                model_name = "HunyuanVideo"
            else:
                video_bytes = await VideoService._generate_svd(image_path)
                model_name = "Stable Video Diffusion"
            if video_bytes:
                saved = await VideoService._save_video(video_bytes, filename)
                return {"success": True, "model_name": model_name,
                        "file_path": saved, "url": f"/static/outputs/{filename}"}
        except Exception as e:
            print(f"[VideoService] {model_choice} failed: {e}")
        # Fallback
        try:
            if model_choice == "hunyuan":
                video_bytes = await VideoService._generate_svd(image_path)
                model_name = "SVD (Fallback)"
            else:
                video_bytes = await VideoService._generate_hunyuan(image_path, prompt)
                model_name = "Hunyuan (Fallback)"
            if video_bytes:
                saved = await VideoService._save_video(video_bytes, filename)
                return {"success": True, "model_name": model_name,
                        "file_path": saved, "url": f"/static/outputs/{filename}"}
        except Exception as e2:
            print(f"[VideoService] Fallback failed: {e2}")
        return {"success": False, "model_name": "", "file_path": "", "url": ""}

    @staticmethod
    async def _generate_hunyuan(image_path: str, prompt: str) -> bytes | None:
        if not HF_API_KEY:
            raise ValueError("HF_API_KEY not set")
        url = "https://api-inference.huggingface.co/models/tencent/HunyuanVideo"
        headers = {"Authorization": f"Bearer {HF_API_KEY}", "Content-Type": "application/json"}
        payload = {"inputs": prompt, "parameters": {"image": image_path, "width": 576, "height": 1024, "num_frames": 61}}
        async with httpx.AsyncClient(timeout=300.0) as client:
            r = await client.post(url, json=payload, headers=headers)
            if r.status_code == 200:
                return r.content
            raise ValueError(f"Hunyuan {r.status_code}: {r.text[:200]}")

    @staticmethod
    async def _generate_svd(image_path: str) -> bytes | None:
        if not HF_API_KEY:
            raise ValueError("HF_API_KEY not set")
        url = "https://api-inference.huggingface.co/models/stabilityai/stable-video-diffusion-img2vid-xt"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        abs_path = image_path
        if image_path.startswith("/static/outputs/"):
            abs_path = os.path.join(STORAGE_DIR, os.path.basename(image_path))
        if os.path.exists(abs_path):
            with open(abs_path, "rb") as f:
                image_bytes = f.read()
        else:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(image_path)
                image_bytes = resp.content
        async with httpx.AsyncClient(timeout=300.0) as client:
            r = await client.post(url, content=image_bytes, headers=headers)
            if r.status_code == 200:
                return r.content
            raise ValueError(f"SVD {r.status_code}: {r.text[:200]}")

    @staticmethod
    async def _save_video(data: bytes, filename: str) -> str:
        os.makedirs(STORAGE_DIR, exist_ok=True)
        filepath = os.path.join(STORAGE_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(data)
        return filepath
