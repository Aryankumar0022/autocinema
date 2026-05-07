"""
AutoCinema FFmpeg Service
Local CPU-only video stitching, audio mixing, and subtitle burn-in.
"""

import os
import json
import subprocess
import asyncio

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "outputs")


class FFmpegService:
    @staticmethod
    async def render_final(project_id: str, video_clips: list[str],
                           voiceover_path: str, music_path: str | None,
                           subtitle_words: list[dict]) -> dict:
        """
        Render the final 1080x1920 MP4 by:
        1. Concatenating video clips
        2. Mixing audio (ducking music to 15% under voice)
        3. Burning word-by-word highlighted subtitles
        """
        os.makedirs(STORAGE_DIR, exist_ok=True)
        output_path = os.path.join(STORAGE_DIR, f"proj_{project_id}_final.mp4")

        try:
            # Step 1: Concatenate video clips
            concat_path = await FFmpegService._concat_clips(project_id, video_clips)

            # Step 2: Generate ASS subtitle file from word timestamps
            sub_path = await FFmpegService._generate_ass_subtitles(project_id, subtitle_words)

            # Step 3: Final render with audio mixing and subtitle burn-in
            await FFmpegService._final_mix(
                concat_path, voiceover_path, music_path, sub_path, output_path
            )

            return {
                "success": True,
                "file_path": output_path,
                "url": f"/static/outputs/proj_{project_id}_final.mp4",
            }
        except Exception as e:
            print(f"[FFmpeg] Render failed: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def _concat_clips(project_id: str, clips: list[str]) -> str:
        """Concatenate video clips using FFmpeg concat demuxer."""
        list_file = os.path.join(STORAGE_DIR, f"proj_{project_id}_concat.txt")
        concat_out = os.path.join(STORAGE_DIR, f"proj_{project_id}_concat.mp4")

        with open(list_file, "w") as f:
            for clip in clips:
                # Normalize path separators for FFmpeg
                clip_path = clip.replace("\\", "/")
                f.write(f"file '{clip_path}'\n")

        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-r", "24", "-pix_fmt", "yuv420p",
            "-an", concat_out
        ]
        await FFmpegService._run(cmd)
        return concat_out

    @staticmethod
    async def _generate_ass_subtitles(project_id: str, words: list[dict]) -> str:
        """Generate an ASS subtitle file with word-by-word highlighting."""
        ass_path = os.path.join(STORAGE_DIR, f"proj_{project_id}_subs.ass")

        header = """[Script Info]
Title: AutoCinema Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,72,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,40,40,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        def format_time(seconds: float) -> str:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            cs = int((seconds % 1) * 100)
            return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

        events = []
        # Group words into chunks of ~5 for readable display
        chunk_size = 5
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            if not chunk:
                continue
            start = chunk[0].get("start", 0)
            end = chunk[-1].get("end", start + 1)
            text = " ".join(w.get("word", "") for w in chunk)
            start_str = format_time(start)
            end_str = format_time(end)
            events.append(
                f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}"
            )

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(header)
            f.write("\n".join(events))

        return ass_path

    @staticmethod
    async def _final_mix(video_path: str, voice_path: str,
                         music_path: str | None, sub_path: str,
                         output_path: str):
        """Mix video + voice + music (ducked) + subtitles into final output."""
        if music_path and os.path.exists(music_path):
            # Mix voice at full volume, music at 15%
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", voice_path,
                "-i", music_path,
                "-filter_complex",
                "[1:a]volume=1.0[voice];[2:a]volume=0.15[music];[voice][music]amix=inputs=2:duration=first[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-vf", f"ass='{sub_path.replace(os.sep, '/')}'",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                output_path
            ]
        else:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", voice_path,
                "-map", "0:v", "-map", "1:a",
                "-vf", f"ass='{sub_path.replace(os.sep, '/')}'",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                output_path
            ]
        await FFmpegService._run(cmd)

    @staticmethod
    async def _run(cmd: list[str]):
        """Run an FFmpeg command asynchronously."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {stderr.decode()[-500:]}")
