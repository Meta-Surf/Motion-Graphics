"""Offline contract/timeline tests. Providers are fakes; no GPU or paid API is called."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import build_composition as builder
import video_contract as contract

spec = importlib.util.spec_from_file_location("chunks", ROOT / "scripts" / "render_chunks.py")
chunks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chunks)


def write_wav(path, seconds, rate=44100, value=b"\x01\x00"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as audio:
        audio.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        audio.writeframes(value * round(seconds * rate))


def composition(kind="short_9_16", seconds=15, fps=30):
    width, height, _, _ = contract.FORMATS[kind]
    return {"schema_version": 1, "project_id": "unit-test", "title": "Test", "video_type": kind,
            "width": width, "height": height, "fps": fps, "durationInFrames": seconds * fps,
            "audio": "generated/unit-test/voice.wav", "scenes": [{"id": "scene-one", "template_id": "photo_essay",
            "title": "Test", "fromFrame": 0, "durationInFrames": seconds * fps,
            "image": "generated/unit-test/image.png", "labels": []}]}


class ContractTest(unittest.TestCase):
    def setUp(self):
        self.director = contract.read_json(ROOT / "examples" / "video-director.short.json")

    def test_schema_rejects_unknown_template_duplicate_ids_and_command_fields(self):
        for change in (lambda d: d["scenes"][0].update(template_id="P21"),
                       lambda d: d["scenes"][1].update(id=d["scenes"][0]["id"]),
                       lambda d: d.update(command="execute something"),
                       lambda d: d.update(project_id="../outside")):
            value = copy.deepcopy(self.director)
            change(value)
            with self.assertRaises(ValueError):
                contract.validate_director(value)

    def test_duration_boundaries_for_both_formats(self):
        for kind, (_, _, minimum, maximum) in contract.FORMATS.items():
            for seconds in (minimum, maximum):
                contract.validate_composition(composition(kind, seconds))
            for seconds in (minimum - 1, maximum + 1):
                with self.assertRaises(ValueError):
                    contract.validate_composition(composition(kind, seconds))

    def test_compiled_timeline_and_path_traversal(self):
        for change in (lambda d: d["scenes"][0].update(fromFrame=1),
                       lambda d: d.update(width=1920),
                       lambda d: d.update(audio="generated/unit-test/../../outside.wav")):
            value = composition()
            change(value)
            with self.assertRaises(ValueError):
                contract.validate_composition(value)

    def test_shared_art_direction_suffix_and_queue_batch_limit(self):
        self.director["scenes"] = [copy.deepcopy(self.director["scenes"][0]) for _ in range(17)]
        for index, scene in enumerate(self.director["scenes"]):
            scene["id"] = f"scene-{index:03d}"
            scene["seed"] = index
        requests = builder.image_requests(self.director)
        self.assertTrue(all(r["prompt"].endswith(contract.VISUAL_SUFFIX) for r in requests))
        self.assertEqual(requests[0]["prompt"].count(contract.VISUAL_SUFFIX), 1)
        with tempfile.TemporaryDirectory() as temp:
            jobs = builder.enqueue(self.director, requests, Path(temp))
            self.assertEqual([len(contract.read_json(Path(p))["images"]) for p in jobs], [8, 8, 1])
            self.assertEqual(jobs, builder.enqueue(self.director, requests, Path(temp)))

    def test_wav_is_padded_on_frame_boundaries_and_never_truncated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first, second, output = root / "first.wav", root / "second.wav", root / "voice.wav"
            write_wav(first, .03)
            write_wav(second, .04)
            builder.assemble_narration([(first, 1), (second, 1)], output, 24)
            params, frames = builder.wav_info(output)
            self.assertEqual(frames, round(2 * 44100 / 24))
            self.assertEqual(params, (1, 2, 44100))
            with wave.open(str(output)) as audio:
                self.assertEqual(audio.readframes(1), b"\x01\x00")
            with self.assertRaises(ValueError):
                builder.assemble_narration([(first, 1), (second, 1)], output, 60)

    def test_absolute_ranges_cover_every_frame_once_including_partial_last_chunk(self):
        ranges = chunks.frame_ranges(1800 * 30 + 7, 30, 90)
        self.assertEqual(ranges[0], (0, 2699))
        self.assertEqual(ranges[-1], (54000, 54006))
        self.assertEqual(sum(end - start + 1 for start, end in ranges), 54007)
        self.assertTrue(all(left[1] + 1 == right[0] for left, right in zip(ranges, ranges[1:])))

    def test_build_uses_measured_audio_and_compiles_static_paths(self):
        class FakeVoice:
            def health(self):
                return {"status": "ok", "device": "cuda"}

            def narrate(self, text, output, profile, steps):
                write_wav(output, 5.01)

        def fake_image(prompt, output, width, height, model, seed):
            output.write_bytes(b"fake image for offline contract test")
            return output

        def validate_image(path, request, ffprobe):
            return {"width": request["width"], "height": request["height"], "sha256": contract.file_digest(path)}

        with tempfile.TemporaryDirectory() as temp, patch.object(builder, "ROOT", Path(temp)), patch.object(builder, "validate_image", validate_image):
            props = builder.build(self.director, FakeVoice(), "unused", image_generator=fake_image)
            self.assertEqual(props["durationInFrames"], 3 * 151)
            self.assertEqual([s["fromFrame"] for s in props["scenes"]], [0, 151, 302])
            audio = Path(temp) / "remotion" / "public" / props["audio"]
            self.assertEqual(builder.wav_info(audio)[1], round(453 * 44100 / 30))
            self.assertFalse(props["audio"].startswith("public/"))
            self.director["scenes"][0]["duration_seconds"] = 2
            with self.assertRaisesRegex(ValueError, "narration exceeds"):
                builder.build(self.director, FakeVoice(), "unused", image_generator=fake_image)

    def test_missing_queue_asset_does_not_call_paid_provider(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "No downloaded queue asset"):
                builder.collect_image(builder.image_requests(self.director)[0], Path(temp), [{"assets": []}], "unused",
                                      image_generator=lambda *args: self.fail("Unexpected paid generation"))

    def test_chunk_validation_rejects_frame_loss_audio_and_wrong_pixel_format(self):
        stream = {"codec_type": "video", "codec_name": "h264", "pix_fmt": "yuv420p", "width": 1080,
                  "height": 1920, "r_frame_rate": "30/1", "nb_frames": "450", "duration": "15.0"}
        for bad in ({**stream, "nb_frames": "449"}, {**stream, "pix_fmt": "yuvj420p"}):
            with patch.object(chunks, "probe", return_value={"streams": [bad]}):
                with self.assertRaises(ValueError):
                    chunks.video_signature(Path("chunk.mp4"), composition(), 450, "unused")
        with patch.object(chunks, "probe", return_value={"streams": [stream, {"codec_type": "audio"}]}):
            with self.assertRaises(ValueError):
                chunks.video_signature(Path("chunk.mp4"), composition(), 450, "unused")


if __name__ == "__main__":
    unittest.main()
