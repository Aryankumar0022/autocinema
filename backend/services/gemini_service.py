"""
AutoCinema Gemini Service
Script analysis and prompt generation using Google Gemini 1.5 Flash.
"""

import os
import json
import asyncio
import re
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted, TooManyRequests

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


ANALYSIS_PROMPT = """You are a professional cinematic director and video producer specializing in vertical short-form content (9:16 aspect ratio) for Instagram Reels and TikTok.

Given the following script/narration text, perform these tasks:

1. **Split the script** into sequential segments. Each segment should be 3-8 seconds of narration when spoken aloud. Keep sentences intact where possible.
2. **For each segment**, generate:
   - `narration_text`: The exact text to be spoken in this segment.
   - `visual_prompt`: A highly detailed cinematic image prompt optimized for AI image generation. Include specific details about composition, lighting, color palette, subject positioning, camera angle, and mood. Always specify "vertical 9:16 aspect ratio" and "cinematic quality". Be extremely descriptive (50-100 words).
   - `motion_prompt`: A short description of how the camera or scene should move when this image is animated into video (e.g., "slow zoom in on subject", "gentle pan left to right", "parallax depth effect with foreground blur").
   - `duration`: Estimated duration in seconds (between 3.0 and 8.0).

Return your response as a valid JSON array. Example format:
```json
[
  {
    "narration_text": "In the heart of an ancient forest...",
    "visual_prompt": "A mystical ancient forest with towering redwood trees, volumetric god rays piercing through a dense emerald canopy, moss-covered fallen logs in the foreground, a narrow winding path disappearing into golden mist, vertical 9:16 aspect ratio, cinematic quality, Unreal Engine 5 photorealism, dramatic natural lighting",
    "motion_prompt": "Slow dolly forward along the forest path, slight upward tilt revealing the canopy",
    "duration": 5.0
  }
]
```

IMPORTANT RULES:
- Return ONLY the JSON array, no markdown formatting, no code blocks, no extra text.
- Every visual_prompt MUST include "vertical 9:16 aspect ratio" and "cinematic quality".
- Make visual prompts extremely detailed and vivid for best AI image generation results.
- Ensure narration_text segments flow naturally when read aloud sequentially.
- Target 3-8 seconds per segment based on word count (~2.5 words per second).

Here is the script to analyze:

"""


class GeminiService:
    @staticmethod
    def _fallback_basic_segments(script: str) -> list[dict]:
        """
        Offline fallback when Gemini quota is unavailable.
        Splits text into ~3-8s chunks (≈2.5 words/sec) and generates simple prompts.
        """
        text = " ".join((script or "").strip().split())
        if not text:
            return []

        # Rough sentence split with punctuation preservation.
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if not sentences:
            sentences = [text]

        target_words_min = 8   # ~3s
        target_words_max = 20  # ~8s

        segments: list[str] = []
        cur: list[str] = []
        cur_words = 0

        def flush():
            nonlocal cur, cur_words
            if cur:
                segments.append(" ".join(cur).strip())
            cur = []
            cur_words = 0

        for s in sentences:
            words = s.split()
            w = len(words)
            # If a single sentence is very long, chunk by words.
            if w > target_words_max * 2:
                for i in range(0, w, target_words_max):
                    chunk = " ".join(words[i : i + target_words_max]).strip()
                    if chunk:
                        if cur_words >= target_words_min:
                            flush()
                        segments.append(chunk)
                continue

            if cur_words and (cur_words + w) > target_words_max:
                flush()
            cur.append(s)
            cur_words += w
            if cur_words >= target_words_min:
                flush()

        flush()

        validated: list[dict] = []
        for seg in segments:
            wc = len(seg.split())
            duration = max(3.0, min(8.0, round(wc / 2.5, 1)))
            validated.append(
                {
                    "narration_text": seg,
                    "visual_prompt": (
                        "Cinematic vertical short-form scene illustrating the narration, "
                        "vertical 9:16 aspect ratio, cinematic quality, dramatic lighting, "
                        "sharp subject focus, rich color grading, highly detailed composition"
                    ),
                    "motion_prompt": "Slow cinematic push-in with gentle parallax depth.",
                    "duration": duration,
                }
            )
        return validated

    @staticmethod
    def _extract_retry_delay_seconds(message: str) -> float | None:
        """
        Extracts 'retry in 14.01s' / 'retry_delay { seconds: 14 }' style hints.
        """
        if not message:
            return None
        m = re.search(r"retry in\s+(\d+(?:\.\d+)?)s", message, flags=re.IGNORECASE)
        if m:
            return float(m.group(1))
        m = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)\s*\}", message, flags=re.IGNORECASE)
        if m:
            return float(m.group(1))
        return None

    @staticmethod
    async def analyze_script(script: str) -> list[dict]:
        """
        Analyze a script using Gemini (configurable model).
        Returns a list of segment dictionaries.
        """
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured. Please set it in your .env file.")

        model = genai.GenerativeModel(GEMINI_MODEL)

        full_prompt = ANALYSIS_PROMPT + script.strip()

        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=8192,
        )

        # google-generativeai's `generate_content` is blocking; keep FastAPI's event loop responsive.
        # Retry briefly on 429s (Gemini often returns a short retry delay), then fall back offline.
        last_err: Exception | None = None
        for attempt in range(3):
            try:
                response = await asyncio.to_thread(
                    model.generate_content,
                    full_prompt,
                    generation_config=generation_config,
                )
                break
            except (ResourceExhausted, TooManyRequests) as e:
                last_err = e
                msg = str(e)
                delay = GeminiService._extract_retry_delay_seconds(msg)
                # If quota is effectively disabled (limit: 0), don't spin retries.
                if "limit: 0" in msg or "Quota exceeded" in msg:
                    return GeminiService._fallback_basic_segments(script)
                if attempt < 2:
                    sleep_s = delay if delay is not None else (1.0 + attempt)
                    await asyncio.sleep(min(15.0, max(0.5, float(sleep_s))))
                    continue
                return GeminiService._fallback_basic_segments(script)
            except Exception as e:
                last_err = e
                # Unknown Gemini SDK error — fall back so the UX stays unblocked.
                return GeminiService._fallback_basic_segments(script)
        else:
            # Shouldn't happen, but keep mypy happy.
            if last_err:
                return GeminiService._fallback_basic_segments(script)
            return GeminiService._fallback_basic_segments(script)

        try:
            raw_text = (response.text or "").strip()
        except Exception:
            # In some cases (e.g., safety blocks) the SDK raises when accessing `.text`.
            raw_text = ""

        if not raw_text:
            raise ValueError(f"Gemini returned an empty response. Raw response: {response!r}")

        # Clean up the response - strip markdown code fences if present
        if raw_text.startswith("```"):
            lines = raw_text.split("\n")
            # Remove first and last lines (code fences)
            lines = [l for l in lines if not l.strip().startswith("```")]
            raw_text = "\n".join(lines)

        try:
            segments = json.loads(raw_text)
        except json.JSONDecodeError as e:
            # Try to extract JSON from the response
            start = raw_text.find("[")
            end = raw_text.rfind("]") + 1
            if start >= 0 and end > start:
                segments = json.loads(raw_text[start:end])
            else:
                raise ValueError(f"Gemini returned invalid JSON: {e}\nRaw: {raw_text[:500]}")

        if not isinstance(segments, list):
            raise ValueError("Gemini did not return a JSON array")

        # Validate and normalize each segment
        validated = []
        for i, seg in enumerate(segments):
            validated.append({
                "narration_text": seg.get("narration_text", "").strip(),
                "visual_prompt": seg.get("visual_prompt", "").strip(),
                "motion_prompt": seg.get("motion_prompt", "").strip(),
                "duration": max(3.0, min(8.0, float(seg.get("duration", 5.0))))
            })

        return validated
