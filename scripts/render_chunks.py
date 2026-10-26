#!/usr/bin/env python3
"""Render absolute frame ranges in isolated Remotion processes and stream-copy video."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from build_composition import wav_info
from video_contract import (
    ROOT, digest, executable, file_digest, probe, public_asset, read_json,
    validate_composition, write_json,
)


def frame_ranges(duration: int, fps: int, chunk_seconds: int) -> list[tuple[int, int]]:
    if any(type(v) is not int or v <= 0 for v in (duration, fps, chunk_seconds)):
        raise ValueError("Frame count, FPS and chunk duration must be positive integers")
    size = fps * chunk_seconds
    return [(start, min(start + size, duration) - 1) for start in range(0, duration, size)]


def video_signature(path: Path, props: dict, expected_frames: int, ffprobe: str, audio: bool = False) -> dict:
    meta = probe(path, ffprobe)
    videos = [s for s in meta["streams"] if s.get("codec_type") == "video"]
    audios = [s for s in meta["streams"] if s.get("codec_type") == "audio"]
    if len(videos) != 1 or (not audio and audios) or (audio and len(audios) != 1):
        raise ValueError(f"Unexpected video/audio stream layout: {path}")
    stream = videos[0]
    if (stream.get("width"), stream.get("height")) != (props["width"], props["height"]):
        raise ValueError(f"Resolution mismatch: {path}")
    if stream.get("codec_name") != "h264" or stream.get("pix_fmt") != "yuv420p":
        raise ValueError(f"Expected H.264/yuv420p, got {stream.get('codec_name')}/{stream.get('pix_fmt')}: {path}")
    if Fraction(stream["r_frame_rate"]) != props["fps"] or int(stream.get("nb_frames", -1)) != expected_frames:
        raise ValueError(f"Frame count or FPS mismatch: {path}")
    if abs(float(stream["duration"]) - expected_frames / props["fps"]) > .001:
        raise ValueError(f"Video duration mismatch: {path}")
    if audio:
        if audios[0].get("codec_name") != "aac" or abs(float(audios[0]["duration"]) - expected_frames / props["fps"]) > .05:
            raise ValueError(f"AAC audio duration mismatch: {path}")
    return {key: stream.get(key) for key in (
        "codec_name", "codec_tag_string", "profile", "level", "width", "height", "pix_fmt",
        "time_base", "r_frame_rate", "extradata_hash",
    )}


def fingerprint(props: dict, concurrency: int, browser_executable: str | None = None) -> str:
    files = {str(path.relative_to(ROOT)): file_digest(path) for path in sorted((ROOT / "remotion" / "src").rglob("*")) if path.is_file()}
    for name in ("package-lock.json", "package.json"):
        path = ROOT / "remotion" / name
        files[name] = file_digest(path)
    assets = {source: file_digest(public_asset(source)) for source in {props["audio"], *(s["image"] for s in props["scenes"])}}
    return digest({"props": props, "source": files, "assets": assets, "concurrency": concurrency,
                   "browser": browser_executable, "render_script": file_digest(Path(__file__)),
                   "encoding": "h264-crf18-medium-yuv420p-bt709-png"})


def render(props_path: Path, output: Path, chunk_seconds: int = 90, concurrency: int = 1,
           resume: bool = False, overwrite: bool = False, ffmpeg: str | None = None,
           ffprobe: str | None = None, timeout: int = 3600, browser_executable: str | None = None) -> dict:
    props = read_json(props_path)
    validate_composition(props)
    output = output.resolve()
    if output.suffix.lower() != ".mp4":
        raise ValueError("Output must have an .mp4 extension")
    if output.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {output}; use --overwrite")
    if not 60 <= chunk_seconds <= 120 or concurrency < 1 or timeout <= 0:
        raise ValueError("Use 60–120 second chunks, positive concurrency and timeout")
    ffmpeg, ffprobe = ffmpeg or executable("ffmpeg"), ffprobe or executable("ffprobe")
    audio = public_asset(props["audio"])
    (_, _, rate), samples = wav_info(audio)
    if abs(samples / rate - props["durationInFrames"] / props["fps"]) > 1 / rate:
        raise ValueError("Continuous narration WAV must match the timeline, including scene padding")
    cli = ROOT / "remotion" / "node_modules" / "@remotion" / "cli" / "remotion-cli.js"
    if not cli.is_file():
        raise ValueError("Run npm ci in remotion/ first")
    signature = fingerprint(props, concurrency, browser_executable)
    work = output.parent / ".motion-chunks" / signature
    work.mkdir(parents=True, exist_ok=True)
    lock = output.with_name(output.name + ".lock")
    # Exclusive output lock prevents competing jobs from publishing partial results.
    with lock.open("x", encoding="utf-8") as handle:
        handle.write(signature)
    temporary = output.with_name(output.stem + f".{uuid.uuid4().hex}.partial.mp4")
    try:
        # Snapshot props: callers editing their input during a long render cannot alter later chunks.
        snapshot = work / "composition.json"
        write_json(snapshot, props)
        chunks, reference = [], None
        for index, (start, end) in enumerate(frame_ranges(props["durationInFrames"], props["fps"], chunk_seconds)):
            chunk = work / f"chunk-{start:08d}-{end:08d}.mp4"
            chunk_record = chunk.with_suffix(".json")
            valid = False
            if resume and chunk.exists() and chunk_record.exists():
                try:
                    record = read_json(chunk_record)
                    valid = record.get("sha256") == file_digest(chunk)
                    if valid:
                        video_signature(chunk, props, end - start + 1, ffprobe)
                except (OSError, ValueError, subprocess.SubprocessError):
                    valid = False
            if not valid:
                partial = chunk.with_name(chunk.stem + f".{uuid.uuid4().hex}.partial.mp4")
                command = [executable("node"), str(cli), "render", "src/index.ts", "AiVideo", str(partial),
                           f"--props={snapshot}", f"--frames={start}-{end}", "--codec=h264", "--muted",
                           "--pixel-format=yuv420p", "--image-format=png", "--color-space=bt709", "--crf=18",
                           "--x264-preset=medium", "--log=warn", f"--concurrency={concurrency}"]
                if browser_executable:
                    command.append(f"--browser-executable={browser_executable}")
                print(f"Chunk {index + 1}: frames {start}–{end}", file=sys.stderr, flush=True)
                try:
                    subprocess.run(command, cwd=ROOT / "remotion", check=True, timeout=timeout, stdout=sys.stderr)
                    video_signature(partial, props, end - start + 1, ffprobe)
                    partial.replace(chunk)
                    write_json(chunk_record, {"sha256": file_digest(chunk), "fromFrame": start, "endFrame": end})
                finally:
                    partial.unlink(missing_ok=True)
            current = video_signature(chunk, props, end - start + 1, ffprobe)
            if reference is not None and current != reference:
                raise ValueError("Chunk codec parameters differ; stream-copy concatenation would be unsafe")
            reference = current
            chunks.append(chunk)
        # Controlled ASCII basenames avoid concat escaping issues with apostrophes/Unicode in workspace paths.
        concat = work / "concat.txt"
        concat.write_text("ffconcat version 1.0\n" + "".join(f"file '{p.name}'\n" for p in chunks), encoding="ascii")
        duration = props["durationInFrames"] / props["fps"]
        command = [ffmpeg, "-hide_banner", "-nostdin", "-v", "error", "-f", "concat", "-safe", "1", "-i", str(concat),
                   "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                   "-b:a", "192k", "-ar", "48000", "-af", "apad", "-t", f"{duration:.9f}", "-movflags", "+faststart", str(temporary)]
        subprocess.run(command, check=True, timeout=timeout)
        video_signature(temporary, props, props["durationInFrames"], ffprobe, audio=True)
        # Remotion's minimal FFmpeg omits wrapped_avframe, the default null-muxer encoder.
        subprocess.run([ffmpeg, "-v", "error", "-xerror", "-nostdin", "-i", str(temporary),
                        "-c:v", "rawvideo", "-c:a", "pcm_s16le", "-f", "null", "-"], check=True, timeout=timeout)
        if fingerprint(props, concurrency, browser_executable) != signature:
            raise ValueError("Source code or assets changed during rendering; rerun with a stable package")
        temporary.replace(output)
        result = {"status": "rendered", "output": str(output), "duration_seconds": duration,
                  "chunks": len(chunks), "fingerprint": signature, "work_directory": str(work),
                  "qa": {"technical": "passed", "visual": "pending", "listening": "pending"}}
        write_json(output.with_suffix(".qa.json"), result)
        return result
    finally:
        temporary.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("props", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chunk-seconds", type=int, default=90)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout in seconds per render/mux/decode process")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--ffprobe")
    parser.add_argument("--browser-executable", help="Optional Chromium/Chrome/Edge executable")
    args = parser.parse_args()
    try:
        print(json.dumps(render(args.props, args.output, args.chunk_seconds, args.concurrency, args.resume,
                                args.overwrite, args.ffmpeg, args.ffprobe, args.timeout, args.browser_executable), ensure_ascii=False))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Render failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
