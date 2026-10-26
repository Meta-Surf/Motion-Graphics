#!/usr/bin/env python3
"""Prepare a local Editonny review handoff for a rendered Short.

Copies the render and optional context files into a dated, git-ignored review
folder, probes basic media properties with ffprobe, and writes a review manifest.
This does not call Editonny, upload media, modify the render, or publish anything.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "review" / "editonny"


def probe_video(path: Path) -> dict:
    command = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    raw = json.loads(result.stdout)
    return {
        "duration_seconds": round(float(raw.get("format", {}).get("duration", 0)), 3),
        "streams": raw.get("streams", []),
    }


def copy_context(value: str | None, destination: Path) -> str | None:
    if not value:
        return None
    source = Path(value).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Context file not found: {source}")
    target = destination / source.name
    shutil.copy2(source, target)
    return target.name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path, help="Rendered MP4 to review")
    parser.add_argument("--script", help="Optional script or narration transcript file")
    parser.add_argument("--captions", help="Optional SRT/VTT captions file")
    parser.add_argument("--storyboard", help="Optional storyboard JSON file")
    parser.add_argument("--video-type", choices=("short_9_16", "long_16_9"), default="short_9_16")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Review handoff directory")
    args = parser.parse_args()

    video = args.video.expanduser().resolve()
    if not video.is_file():
        parser.error(f"Video not found: {video}")

    metadata = probe_video(video)
    streams = metadata["streams"]
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    if not video_stream:
        parser.error("Input has no video stream")
    width, height, minimum, maximum = (1080, 1920, 15, 180) if args.video_type == "short_9_16" else (1920, 1080, 480, 1800)
    if (video_stream.get("width"), video_stream.get("height")) != (width, height):
        parser.error(f"Expected {width}x{height} video, got {video_stream.get('width')}x{video_stream.get('height')}")
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not audio_stream or audio_stream.get("codec_name") != "aac":
        parser.error("Final review requires an AAC audio track; silent previews are not final exports")
    if video_stream.get("codec_name") != "h264":
        parser.error("Expected H.264 video")
    if not minimum <= metadata["duration_seconds"] <= maximum + .05:
        parser.error(f"Expected {minimum}–{maximum} seconds; found {metadata['duration_seconds']}s")

    args.output.mkdir(parents=True, exist_ok=True)
    target_video = args.output / video.name
    shutil.copy2(video, target_video)
    extras = {
        "script": copy_context(args.script, args.output),
        "captions": copy_context(args.captions, args.output),
        "storyboard": copy_context(args.storyboard, args.output),
    }
    manifest = {
        "schema_version": 1,
        "video_type": args.video_type,
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "reviewer": "Editonny",
        "video": target_video.name,
        "media_probe": metadata,
        "context_files": extras,
        "checks": [
            {"id": "story_factuality", "status": "pending", "note": "Check claims against supplied sources; do not treat generated visuals as evidence."},
            {"id": "visual_story_match", "status": "pending", "note": "Check that each image and motion scene supports the narration."},
            {"id": "motion_graphics", "status": "pending", "note": "Check meaningful movement, layering, hierarchy, legibility, and safe areas."},
            {"id": "captions_timing", "status": "pending", "note": "Compare spoken words, caption text, timing, and punctuation."},
            {"id": "audio", "status": "pending", "note": "Check intelligibility, clipping, loudness changes, and music/voice balance."},
            {"id": "pace_transitions", "status": "pending", "note": "Check scene rhythm, cuts, transitions, and the opening hook."},
            {"id": "export", "status": "pending", "note": f"Confirm {width}x{height}, {minimum}–{maximum} seconds, and playable audio/video streams."},
        ],
        "decision": "pending",
        "findings": [],
        "review_notes": "",
    }
    manifest_path = args.output / "review-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Review package: {args.output}")
    print(f"Video: {target_video}")
    print(f"Manifest: {manifest_path}")
    print("Next: open the video folder in Codex and use $editonny for a review-only pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
