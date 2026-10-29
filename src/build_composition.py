#!/usr/bin/env python3
"""Compile a director JSON into assets, continuous PCM narration and Remotion props."""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

from providers.cloudflare_workers_ai import DEFAULT_MODEL, generate
from providers.voicestudio import DEFAULT_URL, VoiceStudio
from image_queue import enqueue_image_jobs
from video_contract import (
    ROOT, FORMATS, digest, executable, exclusive_lock, file_digest, image_prompt, probe, read_json,
    seconds_to_frames, validate_composition, validate_director, write_json,
)


def image_requests(director: dict) -> list[dict]:
    # Exact 9:16 / 16:9, multiples of 16; independent of the 1080p render resolution.
    width, height = (864, 1536) if director["video_type"] == "short_9_16" else (1536, 864)
    requests = []
    for scene in director["scenes"]:
        request = {"prompt": image_prompt(director, scene), "width": width, "height": height,
                   "seed": scene["seed"], "model": DEFAULT_MODEL}
        key = digest(request)
        requests.append({**request, "filename": key + ".png", "asset_id": key,
                         "scene_id": scene["id"], "role": "background", "alpha": "none"})
    return requests


def enqueue(director: dict, requests: list[dict], pending: Path) -> list[str]:
    """Produce the existing queue's format, with immutable job IDs and <=8 images/job."""
    return enqueue_image_jobs(requests, pending)


def validate_image(path: Path, request: dict, ffprobe: str) -> dict:
    meta = probe(path, ffprobe)
    stream = next((s for s in meta["streams"] if s.get("codec_type") == "video"), {})
    if (stream.get("width"), stream.get("height")) != (request["width"], request["height"]):
        raise ValueError(f"Unexpected generated image dimensions: {path}")
    if stream.get("codec_name") not in ("png", "mjpeg", "webp"):
        raise ValueError(f"Expected a PNG, JPEG or WebP still image: {path}")
    return {"width": stream["width"], "height": stream["height"], "sha256": file_digest(path)}


def collect_image(request: dict, directory: Path, manifests: list[dict], ffprobe: str,
                  image_generator=generate) -> tuple[Path, dict]:
    directory.mkdir(parents=True, exist_ok=True)
    key = request["asset_id"]
    record_path = directory / (key + ".asset.json")
    if record_path.exists():
        try:
            record = read_json(record_path)
            path = directory / record.get("file", "")
            matches = all(record.get(name) == request[name] for name in ("prompt", "model", "seed", "width", "height"))
            if matches and path.parent.resolve() == directory.resolve() and path.is_file() and file_digest(path) == record.get("sha256"):
                validate_image(path, request, ffprobe)
                return path, record
        except (OSError, ValueError, subprocess.SubprocessError):
            pass  # Invalid cache records are rebuilt or reimported from the supplied batch.
    path = None
    if manifests:
        for manifest in manifests:
            for asset in manifest.get("assets", []):
                if asset.get("asset_id") != key:
                    continue
                for name in ("prompt", "model", "seed"):
                    if asset.get(name) != request[name]:
                        raise ValueError(f"Queue provenance mismatch for {key}: {name}")
                if (asset.get("requested_width"), asset.get("requested_height")) != (request["width"], request["height"]):
                    raise ValueError(f"Queue dimensions mismatch for {key}")
                source = (ROOT / asset["file"]).resolve()
                if not source.is_relative_to((ROOT / "output" / "generated").resolve()):
                    raise ValueError("Queue assets must be downloaded into output/generated")
                validate_image(source, request, ffprobe)
                path = directory / (key + source.suffix.lower())
                shutil.copyfile(source, path)
                break
            if path:
                break
        if path is None:
            raise ValueError(f"No downloaded queue asset found: {key}")
    else:
        try:
            with contextlib.redirect_stdout(sys.stderr):
                path = image_generator(request["prompt"], directory / request["filename"], request["width"],
                                       request["height"], request["model"], request["seed"])
        except SystemExit as exc:
            raise RuntimeError(f"Image provider failed: {exc}") from exc
    record = {**request, "file": path.name, **validate_image(path, request, ffprobe),
              "provider": "cloudflare-workers-ai", "visual_review": "pending"}
    write_json(record_path, record)
    return path, record


def wav_info(path: Path) -> tuple[tuple[int, int, int], int]:
    with wave.open(str(path), "rb") as audio:
        if audio.getcomptype() != "NONE" or audio.getsampwidth() != 2 or audio.getnframes() <= 0:
            raise ValueError(f"Expected non-empty signed 16-bit PCM narration: {path}")
        return (audio.getnchannels(), audio.getsampwidth(), audio.getframerate()), audio.getnframes()


def assemble_narration(takes: list[tuple[Path, int]], output: Path, fps: int) -> None:
    """Stream PCM; pad at absolute sample boundaries without accelerating/truncating speech."""
    params, _ = wav_info(takes[0][0])
    channels, width, rate = params
    temporary = output.with_suffix(".partial.wav")
    cursor_frames = samples_written = 0
    try:
        with wave.open(str(temporary), "wb") as destination:
            destination.setparams((channels, width, rate, 0, "NONE", "not compressed"))
            for path, frames in takes:
                actual, samples = wav_info(path)
                if actual != params:
                    raise ValueError("VoiceStudio returned incompatible WAV formats across scenes")
                cursor_frames += frames
                target_samples = round(cursor_frames * rate / fps)
                padding = target_samples - samples_written - samples
                if padding < 0:
                    raise ValueError(f"Narration exceeds its scene: {path}")
                with wave.open(str(path), "rb") as source:
                    while block := source.readframes(65536):
                        destination.writeframesraw(block)
                while padding:
                    count = min(padding, 65536)
                    destination.writeframesraw(b"\0" * count * channels * width)
                    padding -= count
                samples_written = target_samples
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)


def build(director: dict, voice: VoiceStudio, ffprobe: str, manifests: list[dict] | None = None,
          image_generator=generate) -> dict:
    validate_director(director)
    voice.health()
    public = ROOT / "remotion" / "public"
    # A changed script produces a separate package, preserving earlier props and assets.
    package = public / "generated" / director["project_id"] / digest(director)[:24]
    package.mkdir(parents=True, exist_ok=True)
    width, height, _, _ = FORMATS[director["video_type"]]
    fps, cursor, scenes, takes, assets = director["fps"], 0, [], [], []
    for scene, request in zip(director["scenes"], image_requests(director), strict=True):
        print(f"Building scene {scene['id']}", file=sys.stderr)
        cached_image, record = collect_image(request, ROOT / 'output/asset-cache/images', manifests or [], ffprobe, image_generator)
        image = package / 'images' / cached_image.name
        image.parent.mkdir(parents=True, exist_ok=True)
        if not image.exists() or file_digest(image) != record['sha256']:
            shutil.copyfile(cached_image, image)
        audio = package / (scene["id"] + ".wav")
        voice.narrate(scene["narration_text"], audio, director["voice"]["profile_id"], director["voice"].get("steps", 32))
        (_, _, rate), samples = wav_info(audio)
        frames = (samples * fps + rate - 1) // rate
        if "duration_seconds" in scene:
            requested = seconds_to_frames(scene["duration_seconds"], fps)
            if frames > requested:
                raise ValueError(f"{scene['id']}: narration exceeds duration_seconds; extend the scene or shorten its text")
            frames = requested
        takes.append((audio, frames))
        scenes.append({"id": scene["id"], "template_id": scene["template_id"], "title": scene["title"],
                       "fromFrame": cursor, "durationInFrames": frames,
                       "image": image.relative_to(public).as_posix(), "labels": scene.get("labels", [])})
        cursor += frames
        assets.append({**record, "scene_id": scene["id"], "file": image.relative_to(public).as_posix(),
                       "narration": audio.relative_to(public).as_posix(), "narration_sha256": file_digest(audio)})
    composition = {"schema_version": 1, "project_id": director["project_id"], "title": director["title"],
                   "video_type": director["video_type"], "fps": fps, "width": width, "height": height,
                   "durationInFrames": cursor, "audio": (package / "narration.wav").relative_to(public).as_posix(),
                   "scenes": scenes}
    validate_composition(composition)
    assemble_narration(takes, package / "narration.wav", fps)
    write_json(package / "asset-manifest.json", {"assets": assets, "director_sha256": digest(director),
               "narration_sha256": file_digest(package / "narration.wav"),
               "review": {"visual": "pending", "listening": "pending"}})
    return composition


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("director", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--image-mode", choices=("direct", "queue"), default="queue")
    parser.add_argument("--image-manifest", type=Path, action="append", default=[])
    parser.add_argument("--voice-url", default=os.getenv("MOTION_VOICE_URL", DEFAULT_URL))
    parser.add_argument("--ffprobe")
    args = parser.parse_args()
    try:
        director = read_json(args.director)
        validate_director(director)
        if args.validate_only:
            print(json_output({"status": "valid", "scenes": len(director["scenes"])}))
            return 0
        if args.image_mode == "direct" and args.image_manifest:
            raise ValueError("--image-manifest requires --image-mode queue")
        if args.image_mode == "queue" and not args.image_manifest:
            jobs = enqueue(director, image_requests(director), ROOT / "jobs" / "pending")
            print(json_output({"status": "awaiting_images", "jobs": jobs,
                               "next": "Process/download queue artifacts, then pass every --image-manifest"}))
            return 0
        ffprobe = args.ffprobe or executable("ffprobe")
        manifests = [read_json(path) for path in args.image_manifest]
        output = args.output or ROOT / "output" / "projects" / director["project_id"] / "composition.json"
        if output.resolve() == args.director.resolve():
            raise ValueError("Output must preserve the director input file")
        with exclusive_lock(ROOT / "output" / "projects" / director["project_id"] / "build.lock"):
            # Validate the complete imported batch before starting GPU narration.
            if manifests:
                staging = ROOT / "remotion" / "public" / "generated" / director["project_id"] / digest(director)[:24] / "images"
                for request in image_requests(director):
                    collect_image(request, staging, manifests, ffprobe)
            props = build(director, VoiceStudio(args.voice_url), ffprobe, manifests)
            write_json(output, props)
        print(json_output({"status": "ready", "props": str(output.resolve()),
                           "duration_seconds": props["durationInFrames"] / props["fps"]}))
        return 0
    except (OSError, ValueError, RuntimeError, wave.Error, subprocess.SubprocessError) as exc:
        print(f"Composition failed: {exc}", file=sys.stderr)
        return 1


def json_output(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False)


if __name__ == "__main__":
    raise SystemExit(main())
