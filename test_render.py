"""Test: render final video with audio mixing (no subtitles)"""
import os, subprocess, glob

storage = os.path.join("d:\\autocinema\\backend\\storage\\outputs")

# Auto-detect files — find the latest project's assets
video_files = sorted(glob.glob(os.path.join(storage, "proj_*_seg_*_video.mp4")))
voice_files = sorted(glob.glob(os.path.join(storage, "proj_*_voiceover.mp3")))

if not video_files:
    print("ERROR: No video clips found in storage. Generate videos first.")
    exit(1)
if not voice_files:
    print("ERROR: No voiceover found in storage. Generate audio first.")
    exit(1)

video = video_files[-1]
voice = voice_files[-1]
output = os.path.join(storage, "test_render_output.mp4")

print(f"Video: {video}")
print(f"Voice: {voice}")
print(f"Output: {output}")

# Simple render: combine video + voiceover (no subtitles for test)
cmd = [
    "ffmpeg", "-y",
    "-i", video,
    "-i", voice,
    "-map", "0:v", "-map", "1:a",
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    output
]

print(f"CMD: {' '.join(cmd)}")
r = subprocess.run(cmd, capture_output=True, timeout=120)
print(f"RC: {r.returncode}")
if r.returncode != 0:
    err = r.stderr.decode(errors="replace")[-800:]
    print(f"ERR: {err}")
else:
    size = os.path.getsize(output)
    print(f"OK! {size} bytes ({size / 1024 / 1024:.1f} MB)")
