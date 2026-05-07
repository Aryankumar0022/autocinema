"""
AutoCinema Image Service
Generates images using a random pair of cloud AI models.
Pool: FLUX.1-schnell (Together AI), SD 3.5 Large (HF), SDXL 1.0 (HF)
"""

import os
import random
import httpx
from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "outputs")


MODEL_INFO = {
    "flux-schnell": {
        "display_name": "FLUX.1 Schnell",
        "provider": "Together AI",
    },
    "sd35-large": {
        "display_name": "Stable Diffusion 3.5 Large",
        "provider": "Hugging Face",
    },
    "sdxl": {
        "display_name": "SDXL 1.0",
        "provider": "Hugging Face",
    },
}


class ImageService:
    @staticmethod
    async def generate_random_pair(prompt: str, project_id: str, segment_index: int) -> dict:
        """
        Selects exactly 2 random models from the pool.
        Generates exactly 1 image from each.
        Returns dict with option_1 and option_2.
        """
        model_pool = list(MODEL_INFO.keys())
        selected_models = random.sample(model_pool, 2)

        results = {}
        for idx, model_key in enumerate(selected_models):
            option_key = f"option_{idx + 1}"
            filename = f"proj_{project_id}_seg_{segment_index}_opt{idx + 1}.png"
            info = MODEL_INFO[model_key]

            try:
                if model_key == "flux-schnell":
                    url = await ImageService._generate_flux(prompt, filename)
                elif model_key == "sd35-large":
                    url = await ImageService._generate_sd35(prompt, filename)
                elif model_key == "sdxl":
                    url = await ImageService._generate_sdxl(prompt, filename)
                else:
                    url = ""
            except Exception as e:
                print(f"[ImageService] {info['display_name']} failed: {e}")
                url = ""

            results[option_key] = {
                "model_key": model_key,
                "model_name": f"{info['display_name']} ({info['provider']})",
                "url": url,
                "filename": filename,
                "success": bool(url),
            }

        return results

    # ── FLUX.1 Schnell via Together AI ─────────────────────────

    @staticmethod
    async def _generate_flux(prompt: str, filename: str) -> str:
        """Generate an image using FLUX.1-schnell via Together AI API."""
        if not TOGETHER_API_KEY:
            raise ValueError("TOGETHER_API_KEY not set")

        url = "https://api.together.xyz/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell-Free",
            "prompt": prompt,
            "width": 576,
            "height": 1024,
            "steps": 4,
            "n": 1,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            image_url = data["data"][0].get("url", "")
            if not image_url:
                # Some responses return base64 instead
                import base64
                b64 = data["data"][0].get("b64_json", "")
                if b64:
                    return await ImageService._save_b64(b64, filename)
                raise ValueError("No image URL or b64 in response")

            # Download and save locally
            return await ImageService._download_and_save(image_url, filename)

    # ── Stable Diffusion 3.5 Large via Hugging Face ────────────

    @staticmethod
    async def _generate_sd35(prompt: str, filename: str) -> str:
        """Generate an image using SD 3.5 Large via HF Inference API."""
        if not HF_API_KEY:
            raise ValueError("HF_API_KEY not set")

        url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {
            "inputs": prompt,
            "parameters": {"width": 576, "height": 1024},
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
                return await ImageService._save_bytes(response.content, filename)
            elif response.status_code == 503:
                raise ValueError("Model is loading, please retry in a moment")
            else:
                raise ValueError(f"HF returned {response.status_code}: {response.text[:200]}")

    # ── SDXL 1.0 via Hugging Face ─────────────────────────────

    @staticmethod
    async def _generate_sdxl(prompt: str, filename: str) -> str:
        """Generate an image using SDXL 1.0 via HF Inference API."""
        if not HF_API_KEY:
            raise ValueError("HF_API_KEY not set")

        url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": prompt}

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
                return await ImageService._save_bytes(response.content, filename)
            elif response.status_code == 503:
                raise ValueError("Model is loading, please retry in a moment")
            else:
                raise ValueError(f"HF returned {response.status_code}: {response.text[:200]}")

    # ── File helpers ───────────────────────────────────────────

    @staticmethod
    async def _download_and_save(image_url: str, filename: str) -> str:
        """Download an image from URL and save locally."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(image_url)
            resp.raise_for_status()
            return await ImageService._save_bytes(resp.content, filename)

    @staticmethod
    async def _save_bytes(data: bytes, filename: str) -> str:
        """Save raw image bytes to storage."""
        os.makedirs(STORAGE_DIR, exist_ok=True)
        filepath = os.path.join(STORAGE_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(data)
        return f"/static/outputs/{filename}"

    @staticmethod
    async def _save_b64(b64_string: str, filename: str) -> str:
        """Decode base64 and save to storage."""
        import base64
        data = base64.b64decode(b64_string)
        return await ImageService._save_bytes(data, filename)
