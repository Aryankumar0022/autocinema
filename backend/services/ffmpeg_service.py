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
        Render the final 1920x1080 MP4 by:
        1. Concatenating video clips
        2. Mixing audio (ducking music to 15% under voice)
        3. Burning word-by-word highlighted subtitles
        """
        os.makedirs(STORAGE_DIR, exist_ok=True)
        output_path = os.path.join(STORAGE_DIR, f"proj_{project_id}_final.mp4")

        try:
            # Step 1: Concatenate video clips
            print(f"[FFmpeg] Step 1: Concatenating {len(video_clips)} clips...")
            concat_path = await FFmpegService._concat_clips(project_id, video_clips)
            print(f"[FFmpeg] Step 1 done: {concat_path}")

            # Step 2: Generate ASS subtitle file from word timestamps
            sub_path = None
            if subtitle_words and len(subtitle_words) > 0:
                print(f"[FFmpeg] Step 2: Generating subtitles ({len(subtitle_words)} words)...")
                sub_path = await FFmpegService._generate_ass_subtitles(project_id, subtitle_words)
                print(f"[FFmpeg] Step 2 done: {sub_path}")
            else:
                print("[FFmpeg] Step 2: No subtitle words, skipping subtitle generation")

            # Step 3: Final render with audio mixing and subtitle burn-in
            has_music = music_path and os.path.exists(music_path)
            print(f"[FFmpeg] Step 3: Final mix (music={'yes' if has_music else 'no'}, subs={'yes' if sub_path else 'no'})...")
            await FFmpegService._final_mix(
                concat_path, voiceover_path, music_path, sub_path, output_path
            )
            print(f"[FFmpeg] Step 3 done: {output_path} ({os.path.getsize(output_path)} bytes)")

            return {
                "success": True,
                "file_path": output_path,
                "url": f"/static/outputs/proj_{project_id}_final.mp4",
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[FFmpeg] Render failed: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def _concat_clips(project_id: str, clips: list[str]) -> str:
        """Concatenate video clips using FFmpeg concat demuxer."""
        list_file = os.path.join(STORAGE_DIR, f"proj_{project_id}_concat.txt")
        concat_out = os.path.join(STORAGE_DIR, f"proj_{project_id}_concat.mp4")

        with open(list_file, "w") as f:
            for clip in clips:
                # Use absolute path with forward slashes for FFmpeg compatibility
                clip_path = os.path.abspath(clip).replace("\\", "/")
                f.write(f"file '{clip_path}'\n")

        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
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
PlayResX: 1920
PlayResY: 1080

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
                         music_path: str | None, sub_path: str | None,
                         output_path: str):
        """Mix video + voice + music (ducked) + subtitles into final output."""

        # Build the video filter chain
        vf_filters = []

        # Add subtitle burn-in if available
        if sub_path and os.path.exists(sub_path):
            # On Windows, FFmpeg filter paths need special escaping:
            # Drive letters contain ':' which conflicts with FFmpeg filter syntax.
            # Use the relative filename and run from the storage directory (cwd).
            ass_filename = os.path.basename(sub_path)
            vf_filters.append(f"ass={ass_filename}")
            print(f"[FFmpeg] ASS filter using relative path: {ass_filename}")

        has_music = music_path and os.path.exists(music_path)

        if has_music:
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
            ]
        else:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", voice_path,
                "-map", "0:v", "-map", "1:a",
            ]

        # Add video filters if any
        if vf_filters:
            cmd += ["-vf", ",".join(vf_filters)]

        cmd += [
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            output_path
        ]

        print(f"[FFmpeg] Final mix cmd: {' '.join(cmd)}")
        # Run from storage dir so relative ASS paths resolve correctly
        await FFmpegService._run(cmd, cwd=STORAGE_DIR)

    @staticmethod
    def _run_sync(cmd: list[str], cwd: str = None):
        """Run FFmpeg synchronously (called from thread pool)."""
        result = subprocess.run(cmd, capture_output=True, timeout=300, cwd=cwd)
        return result.returncode, result.stdout.decode(errors="replace"), result.stderr.decode(errors="replace")

    @staticmethod
    async def _run(cmd: list[str], cwd: str = None):
        """Run an FFmpeg command in a thread pool (Windows-safe)."""
        print(f"[FFmpeg] Running: {cmd[0]} ... {cmd[-1]}")
        loop = asyncio.get_event_loop()
        returncode, stdout, stderr = await loop.run_in_executor(
            None, lambda: FFmpegService._run_sync(cmd, cwd)
        )
        if returncode != 0:
            err_text = stderr[-800:] if stderr else "No stderr"
            print(f"[FFmpeg] FAILED (rc={returncode}): {err_text}")
            raise RuntimeError(f"FFmpeg error (rc={returncode}): {err_text}")
        else:
            print(f"[FFmpeg] OK (rc=0)")
