"""
AutoCinema API Routes
All REST endpoints for the frontend to consume.
"""

import asyncio
import random
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from backend.database import (
    create_project, get_project, list_projects, update_project, delete_project,
    create_segments, update_segment, create_asset, select_asset,
)
from backend.services.gemini_service import GeminiService
from backend.services.image_service import ImageService
from backend.services.video_service import VideoService
from backend.services.audio_service import AudioService
from backend.services.subtitle_service import SubtitleService
from backend.services.ffmpeg_service import FFmpegService

router = APIRouter(prefix="/api")


# ── Request Models ────────────────────────────────────────────

class CreateProjectReq(BaseModel):
    name: str
    script: str = ""

class UpdateProjectReq(BaseModel):
    name: str | None = None
    script: str | None = None
    voice_name: str | None = None

class SelectImageReq(BaseModel):
    asset_id: str

class GenerateVideoReq(BaseModel):
    model_choice: str = "hunyuan"  # "hunyuan" or "svd"

class GenerateAudioReq(BaseModel):
    voice_name: str = "female_warm"
    music_prompt: str = "cinematic ambient atmospheric background music, emotional, soft"


# ── Project Endpoints ─────────────────────────────────────────

@router.post("/projects")
async def api_create_project(req: CreateProjectReq):
    project = await create_project(req.name, req.script)
    return project


@router.get("/projects")
async def api_list_projects():
    return await list_projects()


@router.get("/projects/{project_id}")
async def api_get_project(project_id: str):
    project = await get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.patch("/projects/{project_id}")
async def api_update_project(project_id: str, req: UpdateProjectReq):
    updates = req.model_dump(exclude_none=True)
    project = await update_project(project_id, **updates)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.delete("/projects/{project_id}")
async def api_delete_project(project_id: str):
    await delete_project(project_id)
    return {"ok": True}


# ── Script Analysis (Gemini) ─────────────────────────────────

@router.post("/projects/{project_id}/analyze")
async def api_analyze_script(project_id: str):
    """Analyze the project's script with Gemini and create segments."""
    project = await get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if not project.get("script", "").strip():
        raise HTTPException(400, "Project has no script to analyze")

    try:
        segments_data = await GeminiService.analyze_script(project["script"])
        segments = await create_segments(project_id, segments_data)
        return {"segments": segments, "count": len(segments)}
    except Exception as e:
        raise HTTPException(500, f"Script analysis failed: {str(e)}")


# ── Image Generation ─────────────────────────────────────────

@router.post("/projects/{project_id}/segments/{seg_index}/images")
async def api_generate_images(project_id: str, seg_index: int):
    """Generate a pair of images from 2 random models for a segment."""
    project = await get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    segments = project.get("segments", [])
    segment = None
    for s in segments:
        if s["seg_index"] == seg_index:
            segment = s
            break
    if not segment:
        raise HTTPException(404, f"Segment {seg_index} not found")

    prompt = segment["visual_prompt"]
    if not prompt:
        raise HTTPException(400, "Segment has no visual prompt")

    try:
        result = await ImageService.generate_random_pair(prompt, project_id, seg_index)

        # Save assets to database
        for option_key, info in result.items():
            await create_asset(
                segment_id=segment["id"],
                asset_type="image",
                model_name=info["model_name"],
                file_path=info.get("filename", ""),
                url=info.get("url", ""),
                metadata={"option": option_key, "model_key": info["model_key"]},
            )

        await update_segment(segment["id"], status="images_ready")
        return result
    except Exception as e:
        raise HTTPException(500, f"Image generation failed: {str(e)}")


# ── Image Selection ───────────────────────────────────────────

@router.post("/projects/{project_id}/segments/{seg_index}/select-image")
async def api_select_image(project_id: str, seg_index: int, req: SelectImageReq):
    """User selects the preferred image for a segment."""
    project = await get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    segment = None
    for s in project.get("segments", []):
        if s["seg_index"] == seg_index:
            segment = s
            break
    if not segment:
        raise HTTPException(404, f"Segment {seg_index} not found")

    await select_asset(req.asset_id, segment["id"], "image")
    await update_segment(segment["id"], status="image_selected")
    return {"ok": True, "selected_asset_id": req.asset_id}


# ── Video Generation ──────────────────────────────────────────

@router.post("/projects/{project_id}/segments/{seg_index}/video")
async def api_generate_video(project_id: str, seg_index: int, req: GenerateVideoReq):
    """Generate video from the selected image for a segment."""
    project = await get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    segment = None
    for s in project.get("segments", []):
        if s["seg_index"] == seg_index:
            segment = s
            break
    if not segment:
        raise HTTPException(404, f"Segment {seg_index} not found")

    # Find selected image
    selected_image = None
    for asset in segment.get("assets", []):
        if asset["asset_type"] == "image" and asset["selected"]:
            selected_image = asset
            break

    if not selected_image:
        raise HTTPException(400, "No image selected for this segment")

    image_path = selected_image.get("url", "") or selected_image.get("file_path", "")

    try:
        result = await VideoService.generate_video(
            image_path=image_path,
            prompt=segment.get("motion_prompt", ""),
            model_choice=req.model_choice,
            project_id=project_id,
            segment_index=seg_index,
        )

        if result["success"]:
            await create_asset(
                segment_id=segment["id"],
                asset_type="video",
                model_name=result["model_name"],
                file_path=result["file_path"],
                url=result["url"],
                selected=True,
            )
            await update_segment(segment["id"], status="video_ready")

        return result
    except Exception as e:
        raise HTTPException(500, f"Video generation failed: {str(e)}")


# ── Audio Generation ──────────────────────────────────────────

@router.post("/projects/{project_id}/audio")
async def api_generate_audio(project_id: str, req: GenerateAudioReq):
    """Generate voiceover and background music for the entire project."""
    project = await get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    # Combine all segment narration texts
    full_narration = " ".join(
        s.get("narration_text", "") for s in project.get("segments", [])
    ).strip()

    if not full_narration:
        raise HTTPException(400, "No narration text available")

    # Run voiceover and music generation in parallel
    voice_task = AudioService.generate_voiceover(full_narration, req.voice_name, project_id)
    music_task = AudioService.generate_music(req.music_prompt, project_id)

    voice_result, music_result = await asyncio.gather(voice_task, music_task)

    await update_project(project_id, status="audio_ready")

    return {"voiceover": voice_result, "music": music_result}


# ── Subtitle Generation ──────────────────────────────────────

@router.post("/projects/{project_id}/subtitles")
async def api_generate_subtitles(project_id: str):
    """Transcribe voiceover to get word-level timestamps."""
    project = await get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    import os
    storage = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "outputs")
    voiceover_path = os.path.join(storage, f"proj_{project_id}_voiceover.mp3")

    if not os.path.exists(voiceover_path):
        raise HTTPException(400, "Voiceover file not found. Generate audio first.")

    result = await SubtitleService.transcribe(voiceover_path)
    return result


# ── Final Render ──────────────────────────────────────────────

@router.post("/projects/{project_id}/render")
async def api_render_final(project_id: str):
    """Run FFmpeg to produce the final MP4."""
    project = await get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    import os
    storage = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "outputs")

    # Collect video clips in order
    video_clips = []
    for seg in sorted(project.get("segments", []), key=lambda s: s["seg_index"]):
        for asset in seg.get("assets", []):
            if asset["asset_type"] == "video" and asset["selected"]:
                video_clips.append(asset["file_path"])

    if not video_clips:
        raise HTTPException(400, "No video clips available. Generate videos first.")

    voiceover_path = os.path.join(storage, f"proj_{project_id}_voiceover.mp3")
    music_path = os.path.join(storage, f"proj_{project_id}_music.wav")

    if not os.path.exists(voiceover_path):
        raise HTTPException(400, "Voiceover not found. Generate audio first.")

    # Get subtitle words
    subtitle_result = await SubtitleService.transcribe(voiceover_path)
    words = subtitle_result.get("words", [])

    music = music_path if os.path.exists(music_path) else None

    await update_project(project_id, status="rendering")
    result = await FFmpegService.render_final(
        project_id, video_clips, voiceover_path, music, words
    )

    if result["success"]:
        await update_project(project_id, status="complete")
    else:
        await update_project(project_id, status="render_failed")

    return result


# ── Utility Endpoints ─────────────────────────────────────────

@router.get("/voices")
async def api_list_voices():
    return AudioService.list_voices()


@router.get("/health")
async def health_check():
    import os
    return {
        "status": "ok",
        "keys": {
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "together": bool(os.getenv("TOGETHER_API_KEY")),
            "huggingface": bool(os.getenv("HF_API_KEY")),
            "groq": bool(os.getenv("GROQ_API_KEY")),
        },
    }
