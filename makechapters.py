#!/usr/bin/env python3
# Inspired by https://ikyle.me/blog/2020/add-mp4-chapters-ffmpeg, this Python
# script automates the process of adding chapters to an MP4 file using FFmpeg.
# It handles backup creation, metadata extraction, chapter parsing, and final
# muxing in a structured way.

import re
import subprocess
import sys
import os
from pathlib import Path

# --- Configuration ---
BACKUP_FOLDER = Path("./originals")
HEADERS_FOLDER = Path("./headers")
HEADERS_PREFIX = "FFMETA-MHV"
OUT_FOLDER = Path("./mhv")
CHAPTERS_SOURCE = "chapters.txt"
# The CHAPTERS_SOURCE file should have one chapter on each line, in the format:
# h:mm:ss Chapter Title
# (for example, "0:00:00 Opening Credits", or "1:23:45 Closing Credits")
# The final line in the file must be set to the length of the video and
# given the chapter title "END".


def run_ffmpeg(args):
    """Helper to run ffmpeg commands."""
    try:
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error"] + args, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        sys.exit(1)


def extract_episode_id(filename):
    """Extracts S01E123 pattern from the filename."""
    match = re.search(r"([Ss]\d+[Ee]\d+)", filename)
    return match.group(1).upper() if match else None


def main():
    # 1. Argument and Episode Validation
    if len(sys.argv) < 2:
        print("Usage: ./makechapters.py <video_file> [optional_episode_id]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    # Use provided ID or extract from filename
    episode = sys.argv[2] if len(sys.argv) > 2 else extract_episode_id(input_path.name)

    if not episode:
        print(
            (
                f"Could not determine episode ID from '{input_path.name}'. "
                "Please provide it as an argument."
            )
        )
        sys.exit(1)

    print(f"Processing {input_path.name} as {episode}...")

    # 2. Setup Directory Structure
    for folder in [BACKUP_FOLDER, HEADERS_FOLDER, OUT_FOLDER]:
        folder.mkdir(parents=True, exist_ok=True)

    backup_path = BACKUP_FOLDER / f"MHV-{episode}-nochapters.m4v"
    header_file = HEADERS_FOLDER / f"{HEADERS_PREFIX}-{episode}.txt"
    output_path = OUT_FOLDER / input_path.name

    # 3. Backup and Metadata Extraction [cite: 1]
    input_path.rename(backup_path)
    run_ffmpeg(["-i", str(backup_path), "-f", "ffmetadata", str(header_file), "-y"])

    # 4. Parse Chapters [cite: 2, 3]
    chapters = []
    # This regex handles the '' prefix in your text file
    time_regex = re.compile(r"(\d):(\d{2}):(\d{2})\s+(.*)")

    if not os.path.exists(CHAPTERS_SOURCE):
        print(f"Error: {CHAPTERS_SOURCE} not found.")
        sys.exit(1)

    with open(CHAPTERS_SOURCE, "r") as f:
        for line in f:
            match = time_regex.search(line)
            if match:
                h, m, s, title = match.groups()
                # Calculate milliseconds for FFMETADATA format
                timestamp_ms = ((int(h) * 3600) + (int(m) * 60) + int(s)) * 1000
                chapters.append({"title": title.strip(), "start": timestamp_ms})

    # 5. Generate Metadata String [cite: 3]
    metadata_output = ""
    for i in range(len(chapters) - 1):
        if chapters[i]["title"].upper() == "END":
            continue

        start = chapters[i]["start"]
        end = chapters[i + 1]["start"] - 1
        metadata_output += (
            "\n[CHAPTER]\n"
            "TIMEBASE=1/1000\n"
            f"START={start}\n"
            f"END={end}\n"
            f"title={chapters[i]['title']}\n"
        )

    # Append to extracted metadata
    with open(header_file, "a") as f:
        f.write(metadata_output)

    # 6. Final Mux [cite: 1]
    print("Writing final file with chapters...")
    run_ffmpeg(
        [
            "-i",
            str(header_file),
            "-i",
            str(backup_path),
            "-map_metadata",
            "0",
            "-codec",
            "copy",
            str(output_path),
            "-y",
        ]
    )

    print(f"Done! Saved to: {output_path}")


if __name__ == "__main__":
    main()
