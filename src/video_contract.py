"""Shared validation and media utilities for the director and render commands."""
from __future__ import annotations

import hashlib
import contextlib
import json
import math
import shutil
import subprocess
import uuid
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
VISUAL_SUFFIX = (
    "cinematic lighting, hyper-realistic materials, editorial photography, "
    "physically plausible detail, controlled filmic contrast, 8k detail aesthetic, "
    "no text, no logos, no watermarks, no flat vector illustration"
)
FORMATS = {"short_9_16": (1080, 1920, 15, 180), "long_16_9": (1920, 1080, 480, 1800)}


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def file_digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def validate_schema(value: dict, name: str) -> None:
    schema = read_json(ROOT / "schemas" / name)
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda e: str(e.json_path))
    if errors:
        raise ValueError("; ".join(f"{e.json_path}: {e.message}" for e in errors[:8]))


def validate_director(value: dict) -> None:
    validate_schema(value, "video-director.schema.json")
    ids = [s["id"] for s in value["scenes"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Scene IDs must be unique")
    # Validate every fully assembled request before either provider is called.
    for scene in value["scenes"]:
        if len(image_prompt(value, scene)) > 3000:
            raise ValueError(f"{scene['id']}: assembled image prompt exceeds the queue limit of 3000 characters")


def image_prompt(director: dict, scene: dict) -> str:
    prompt = scene["image_prompt"].strip()
    if prompt.endswith(VISUAL_SUFFIX):
        prompt = prompt[:-len(VISUAL_SUFFIX)].rstrip(" ,.;")
    art = director["art_direction"]
    guide = "; ".join(f"{key}: {art[key]}" for key in ("palette", "lighting", "camera", "continuity"))
    return f"{prompt}. Shared art direction: {guide}. {VISUAL_SUFFIX}"


def validate_composition(value: dict) -> None:
    validate_schema(value, "composition.schema.json")
    width, height, minimum, maximum = FORMATS[value["video_type"]]
    for source in [value["audio"], *(s["image"] for s in value["scenes"])]:
        if ".." in source.split("/"):
            raise ValueError("Asset paths cannot contain parent directory traversal")
    if (value["width"], value["height"]) != (width, height):
        raise ValueError("Resolution does not match video_type")
    cursor, ids = 0, set()
    for scene in value["scenes"]:
        if scene["id"] in ids or scene["fromFrame"] != cursor:
            raise ValueError("Scenes must have unique IDs and form a contiguous timeline starting at zero")
        layers = scene.get('layers', [])
        if len({layer['id'] for layer in layers}) != len(layers): raise ValueError('Duplicate layer IDs')
        for layer in layers:
            if '..' in layer['image'].split('/'): raise ValueError('Layer path traversal')
        for cue in scene.get('highlight_cues', []):
            if cue['startFrame'] >= cue['endFrame'] or cue['endFrame'] > scene['durationInFrames']:
                raise ValueError('Invalid speech cue')
        ids.add(scene["id"])
        cursor += scene["durationInFrames"]
    if cursor != value["durationInFrames"] or not minimum <= cursor / value["fps"] <= maximum:
        raise ValueError(f"Timeline must last {minimum}–{maximum} seconds for {value['video_type']}")


def public_asset(source: str) -> Path:
    public = (ROOT / "remotion" / "public").resolve()
    asset = (public / source).resolve()
    if not asset.is_relative_to(public) or not asset.is_file():
        raise ValueError(f"Missing asset or path outside remotion/public: {source}")
    return asset


def executable(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    for package in sorted((ROOT / "remotion" / "node_modules" / "@remotion").glob("compositor-*")):
        for filename in (name, name + ".exe"):
            if (package / filename).is_file():
                return str(package / filename)
    raise ValueError(f"{name} not found. Install FFmpeg/Node or pass the executable path explicitly.")


def probe(path: Path, ffprobe: str) -> dict:
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_streams", "-show_format", "-show_data_hash", "sha256", "-of", "json", str(path)],
        check=True, capture_output=True, text=True, timeout=60,
    )
    return json.loads(result.stdout)


def seconds_to_frames(seconds: float, fps: int) -> int:
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("Duration must be a finite positive number")
    return math.ceil(seconds * fps)


@contextlib.contextmanager
def exclusive_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write("Motion operation in progress\n")
    try:
        yield
    finally:
        path.unlink(missing_ok=True)
