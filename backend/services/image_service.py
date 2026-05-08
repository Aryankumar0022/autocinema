"""
AutoCinema Image Service
Generates images using Pollinations.ai (100% free, no API key required).
Uses FLUX models under the hood via different model variants and seeds.
"""

import os
import random
import asyncio
import urllib.parse
import httpx

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "outputs")

# Pollinations.ai model variants — all free, no API key
MODEL_INFO = {
    "flux": {
        "display_name": "FLUX",
        "provider": "Pollinations.ai",
        "model_param": "flux",
    },
    "flux-realism": {
        "display_name": "FLUX Realism",
        "provider": "Pollinations.ai",
        "model_param": "flux-realism",
    },
    "turbo": {
        "display_name": "Turbo",
        "provider": "Pollinations.ai",
        "model_param": "turbo",
    },
}


class ImageService:
    @staticmethod
    async def generate_random_pair(prompt: str, project_id: str, segment_index: int) -> dict:
        """
        Selects exactly 2 random models from the pool.
        Generates exactly 1 image from each — sequentially to avoid 429 rate limits.
        Returns dict with option_1 and option_2.
        """
        model_pool = list(MODEL_INFO.keys())
        selected_models = random.sample(model_pool, 2)

        results = {}
        for idx, model_key in enumerate(selected_models):
            option_key = f"option_{idx + 1}"
            filename = f"proj_{project_id}_seg_{segment_index}_opt{idx + 1}.jpg"
            info = MODEL_INFO[model_key]

            try:
                url = await ImageService._generate_pollinations(
                    prompt, filename, info["model_param"]
                )
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

            # Small delay between the two images in a pair to reduce rate limiting
            if idx == 0:
                await asyncio.sleep(2)

        return results

    # ── Pollinations.ai Image Generation ──────────────────────

    @staticmethod
    async def _generate_pollinations(prompt: str, filename: str, model: str = "flux") -> str:
        """
        Generate an image using Pollinations.ai (free, no API key).
        Includes retry logic with exponential backoff for 429 rate limits.
        """
        seed = random.randint(1, 999999)
        encoded_prompt = urllib.parse.quote(prompt)
        api_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width=1024&height=1024&model={model}&seed={seed}&nologo=true"
        )

        print(f"[ImageService] Generating with {model} (seed={seed})...")

        max_retries = 4
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
                    response = await client.get(api_url)

                    if response.status_code == 200 and len(response.content) > 1000:
                        return await ImageService._save_bytes(response.content, filename)
                    elif response.status_code == 429:
                        # Rate limited — wait and retry with increasing backoff
                        wait_time = (attempt + 1) * 5  # 5s, 10s, 15s, 20s
                        print(f"[ImageService] Rate limited (429). Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        # Use a new seed on retry
                        seed = random.randint(1, 999999)
                        api_url = (
                            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                            f"?width=1024&height=1024&model={model}&seed={seed}&nologo=true"
                        )
                        continue
                    else:
                        raise ValueError(
                            f"Pollinations returned status {response.status_code}, "
                            f"body size {len(response.content)} bytes"
                        )
            except httpx.TimeoutException:
                wait_time = (attempt + 1) * 3
                print(f"[ImageService] Timeout. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
                continue

        raise ValueError(f"Failed after {max_retries} retries (rate limited by Pollinations.ai)")

    # ── File helpers ───────────────────────────────────────────

    @staticmethod
    async def _save_bytes(data: bytes, filename: str) -> str:
        """Save raw image bytes to storage."""
        os.makedirs(STORAGE_DIR, exist_ok=True)
        filepath = os.path.join(STORAGE_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(data)
        return f"/static/outputs/{filename}"
