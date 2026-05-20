"""
Trim a video clip to a frame range and overwrite the file.

Usage:
  python trim.py <file> <start_frame> <end_frame>

Example:
  python trim.py videos/kickflip/chrischann.mp4 42 180

Requires ffmpeg and ffprobe on PATH.
"""

import sys
import os
import json
import subprocess


def get_fps(path):
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_streams", path,
        ],
        capture_output=True, text=True,
    )
    data = json.loads(result.stdout)
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            # r_frame_rate is a fraction string like "30/1" or "2997/100"
            num, den = stream["r_frame_rate"].split("/")
            return int(num) / int(den)
    raise ValueError("No video stream found in file.")


def main():
    if len(sys.argv) not in (3, 4):
        print("Usage: python trim.py <file> <start_frame> [end_frame]")
        print("  If end_frame is omitted, trims start_frame frames from the start.")
        sys.exit(1)

    path        = sys.argv[1]
    start_frame = int(sys.argv[2])
    end_frame   = int(sys.argv[3]) if len(sys.argv) == 4 else None

    if not os.path.isfile(path):
        print(f"File not found: {path}")
        sys.exit(1)

    if start_frame < 0:
        print("start_frame must be >= 0.")
        sys.exit(1)

    if end_frame is not None and end_frame <= start_frame:
        print("end_frame must be greater than start_frame.")
        sys.exit(1)

    fps       = get_fps(path)
    start_sec = start_frame / fps
    end_sec   = end_frame / fps if end_frame is not None else None

    print(f"FPS detected: {fps:.4f}")
    if end_sec is not None:
        print(f"Trimming frames {start_frame}–{end_frame} ({start_sec:.4f}s – {end_sec:.4f}s)")
    else:
        print(f"Trimming first {start_frame} frames ({start_sec:.4f}s) from start")

    tmp = path + ".tmp.mp4"

    cmd = ["ffmpeg", "-y", "-ss", str(start_sec)]
    if end_sec is not None:
        cmd += ["-to", str(end_sec)]
    cmd += ["-i", path, "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", tmp]

    subprocess.run(cmd, check=True)

    os.replace(tmp, path)
    print(f"Done: {path}")


if __name__ == "__main__":
    interactive = len(sys.argv) == 1

    if not interactive:
        try:
            main()
        except Exception as e:
            print(f"\nError: {e}")
            sys.exit(1)
    else:
        print("trim.py — trim a video clip to a frame range")
        while True:
            print()
            path        = input("File path: ").strip().strip('"')
            start_frame = int(input("Start frame (frames to trim from start): ").strip())
            end_str     = input("End frame (leave blank to keep rest of clip): ").strip()

            sys.argv = [sys.argv[0], path, str(start_frame)]
            if end_str:
                sys.argv.append(end_str)

            print()
            try:
                main()
            except Exception as e:
                print(f"\nError: {e}")

            again = input("\nPress Enter to trim another clip, or type q to quit: ").strip().lower()
            if again == "q":
                break
