"""Offline Gemini contract/API failure tests: no real key or paid request is used."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import image_queue
import process_image_queue
from providers import gemini_orchestrator as gemini
from google.generativeai.types import generation_types

SCRIPT = "Uma ideia ganha forma. A revisão melhora o resultado."


def manifest() -> dict:
    return {"video_type": "short_9_16", "scenes": [
        {"template_id": "titles", "narration_text": "Uma ideia ganha forma.",
         "image_prompt": "Documentary photograph of a cinema camera on an oak studio desk, dark navy walls and warm practical light."},
        {"template_id": "comparison", "narration_text": "A revisão melhora o resultado.",
         "image_prompt": "Editorial close-up of two optical lenses on the same oak desk, warm studio light and precise realistic materials."},
    ]}


def response(value: object = None, finish_reason: int = 1) -> SimpleNamespace:
    return SimpleNamespace(candidates=[SimpleNamespace(finish_reason=finish_reason)], text=json.dumps(value or manifest()))


class GeminiTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for relative in ("motion-library/catalog.json", "motion-library/orchestration-templates.json", "schemas/gemini-manifest.schema.json"):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / relative).read_bytes())
        self.enterContext(patch.object(gemini, "ROOT", self.root))
        self.enterContext(patch.object(image_queue, "ROOT", self.root))
        self.enterContext(patch.dict("os.environ", {"GEMINI_API_KEY": "test-key-never-log", "GEMINI_MODEL": "test-model"}))
        self.configure = self.enterContext(patch.object(gemini.genai, "configure"))
        self.model = Mock()
        self.model.generate_content.return_value = response()
        self.factory = self.enterContext(patch.object(gemini.genai, "GenerativeModel", return_value=self.model))
        self.sleep = self.enterContext(patch.object(gemini.time, "sleep"))

    def test_all_21_catalog_patterns_are_in_the_sdk_enum(self):
        templates = gemini.load_template_catalog()
        self.assertEqual(len(templates), 21)
        self.assertEqual({t["catalog_id"] for t in templates}, {f"P{i:02}" for i in range(1, 22)})
        schema = gemini.response_schema(templates)
        self.assertEqual(schema["properties"]["scenes"]["items"]["properties"]["template_id"]["enum"], [t["template_id"] for t in templates])
        config = gemini.genai.types.GenerationConfig(response_mime_type="application/json", response_schema=schema)
        # Exercises the real SDK's dict -> protobuf conversion without making a request.
        converted = generation_types.to_generation_config_dict(config)
        self.assertIn("response_schema", converted)

    def test_happy_path_saves_plan_and_compatible_image_jobs(self):
        result = gemini.generate_video_manifest(SCRIPT)
        self.assertEqual(result["video_type"], "short_9_16")
        self.assertTrue(all(s["image_prompt"].endswith(gemini.VISUAL_SUFFIX) for s in result["scenes"]))
        self.configure.assert_called_once_with(api_key="test-key-never-log", transport="rest")
        request = self.model.generate_content.call_args.kwargs["request_options"]
        self.assertEqual(request, {"timeout": 120, "retry": None})
        plans = list((self.root / "jobs" / "manifests").glob("*.json"))
        self.assertEqual(len(plans), 2)
        self.assertNotIn("test-key-never-log", "".join(path.read_text() for path in plans))
        jobs = list((self.root / "jobs" / "pending").glob("*.json"))
        self.assertEqual(len(jobs), 1)
        job = json.loads(jobs[0].read_text())
        self.assertEqual(set(job), {"job_id", "images"})
        self.assertEqual(len(job["images"]), 2)
        self.assertEqual((job["images"][0]["width"], job["images"][0]["height"]), (864, 1536))
        self.assertTrue(all(30 <= len(item["prompt"]) <= 3000 for item in job["images"]))
        self.assertEqual(set(result), {"video_type", "scenes"})
        self.assertTrue(all(set(s) == {"template_id", "narration_text", "image_prompt"} for s in result["scenes"]))

    def test_retries_transient_quota_and_timeout_errors_then_succeeds(self):
        for exception in (gemini.api_errors.ResourceExhausted, gemini.api_errors.DeadlineExceeded,
                          gemini.api_errors.ServiceUnavailable, gemini.request_errors.Timeout,
                          gemini.request_errors.ConnectionError):
            with self.subTest(exception=exception):
                self.model.generate_content.reset_mock()
                self.model.generate_content.side_effect = [exception("test-key-never-log"), response()]
                gemini.generate_video_manifest(SCRIPT)
                self.assertEqual(self.model.generate_content.call_count, 2)
                self.sleep.assert_called()

    def test_quota_exhaustion_is_bounded_and_preserves_existing_plan(self):
        output = self.root / "plan.json"
        output.write_text('{"previous": true}')
        self.model.generate_content.side_effect = gemini.api_errors.ResourceExhausted("test-key-never-log")
        with self.assertRaises(gemini.GeminiOrchestrationError) as caught:
            gemini.generate_video_manifest(SCRIPT, output_path=output, max_attempts=2)
        self.assertEqual(self.model.generate_content.call_count, 2)
        self.assertNotIn("test-key-never-log", str(caught.exception))
        self.assertEqual(output.read_text(), '{"previous": true}')
        self.assertFalse((self.root / "jobs").exists())

    def test_auth_errors_are_not_retried_or_published(self):
        self.model.generate_content.side_effect = gemini.api_errors.PermissionDenied("URL with test-key-never-log")
        with self.assertRaises(gemini.GeminiOrchestrationError) as caught:
            gemini.generate_video_manifest(SCRIPT)
        self.assertNotIn("test-key-never-log", str(caught.exception))
        self.assertEqual(self.model.generate_content.call_count, 1)
        self.sleep.assert_not_called()
        self.assertFalse((self.root / "jobs").exists())

    def test_blocked_truncated_empty_and_non_json_responses_are_not_published(self):
        cases = [response(finish_reason=2), response(finish_reason=3),
                 SimpleNamespace(candidates=[], text=""),
                 SimpleNamespace(candidates=[SimpleNamespace(finish_reason=1)], text="```json\n{}\n```"),
                 SimpleNamespace(candidates=[SimpleNamespace(finish_reason=1)], text="")]
        for value in cases:
            with self.subTest(value=value):
                self.model.generate_content.return_value = value
                with self.assertRaises(gemini.GeminiOrchestrationError):
                    gemini.generate_video_manifest(SCRIPT)
                self.assertFalse((self.root / "jobs").exists())

    def test_invalid_templates_extra_fields_and_changed_narration_are_rejected(self):
        changes = [lambda m: m["scenes"][0].update(template_id="P99"),
                   lambda m: m["scenes"][0].update(narration_text="Conteúdo inventado."),
                   lambda m: m.update(command="shell command"),
                   lambda m: m.update(scenes=[]),
                   lambda m: m["scenes"][0].update(image_prompt="x" * 2190)]
        for change in changes:
            value = manifest()
            change(value)
            with self.subTest(change=change):
                with self.assertRaises(gemini.GeminiOrchestrationError):
                    gemini.parse_manifest(json.dumps(value), SCRIPT)

    def test_explicit_video_type_is_preserved_and_horizontal_jobs_have_correct_dimensions(self):
        with self.assertRaises(gemini.GeminiOrchestrationError):
            gemini.generate_video_manifest(SCRIPT, video_type="long_16_9")
        value = manifest()
        value["video_type"] = "long_16_9"
        self.model.generate_content.return_value = response(value)
        result = gemini.generate_video_manifest(SCRIPT, video_type="long_16_9")
        self.assertEqual((gemini.image_requests(result)[0]["width"], gemini.image_requests(result)[0]["height"]), (1536, 864))

    def test_large_plan_uses_existing_eight_image_batch_limit(self):
        value = manifest()
        value["scenes"] = [{"template_id": "titles", "narration_text": f"Cena {i}.",
            "image_prompt": f"Editorial photograph of cinema camera number {i} in a realistic studio, with warm light and rich material texture."} for i in range(17)]
        script = " ".join(s["narration_text"] for s in value["scenes"])
        self.model.generate_content.return_value = response(value)
        gemini.generate_video_manifest(script)
        jobs = list((self.root / "jobs" / "pending").glob("*.json"))
        self.assertEqual(sorted(len(json.loads(path.read_text())["images"]) for path in jobs), [1, 8, 8])
        names = {path.name for path in jobs}
        gemini.generate_video_manifest(script)
        self.assertEqual({path.name for path in (self.root / "jobs" / "pending").glob("*.json")}, names)

    def test_existing_image_processor_consumes_generated_jobs(self):
        gemini.generate_video_manifest(SCRIPT)

        def fake_generate(prompt, output, width, height, model, seed):
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"fake image fixture")
            return output

        with patch.multiple(process_image_queue, ROOT=self.root, PENDING=self.root / "jobs" / "pending",
                            PROCESSED=self.root / "jobs" / "processed", OUTPUT=self.root / "output" / "generated"), \
                patch.object(process_image_queue, "generate", side_effect=fake_generate) as generate, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(process_image_queue.main(), 0)
        self.assertEqual(generate.call_count, 2)
        self.assertFalse(list((self.root / "jobs" / "pending").glob("*.json")))
        assets = list((self.root / "output" / "generated").glob("*/asset-manifest.json"))
        self.assertEqual(len(assets), 1)
        self.assertEqual(len(json.loads(assets[0].read_text())["assets"]), 2)

    def test_unsafe_output_and_invalid_config_fail_before_api_call(self):
        cases = [{"output_path": self.root / "jobs" / "pending" / "gemini_manifest.json"},
                 {"max_attempts": 0}, {"timeout_seconds": float("nan")}, {"video_type": "square"}]
        for kwargs in cases:
            with self.assertRaises(ValueError):
                gemini.generate_video_manifest(SCRIPT, **kwargs)
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
            with self.assertRaises(ValueError):
                gemini.generate_video_manifest(SCRIPT)
        with patch.dict("os.environ", {"GEMINI_MODEL": ""}):
            with self.assertRaises(ValueError):
                gemini.generate_video_manifest(SCRIPT)
        self.factory.assert_not_called()

    def test_duplicate_json_properties_and_catalog_drift_are_rejected(self):
        with self.assertRaises(gemini.GeminiOrchestrationError):
            gemini.parse_manifest('{"video_type":"short_9_16","video_type":"long_16_9","scenes":[]}', SCRIPT)
        path = self.root / "motion-library" / "orchestration-templates.json"
        value = json.loads(path.read_text())
        value["templates"].pop()
        path.write_text(json.dumps(value))
        with self.assertRaises(ValueError):
            gemini.generate_video_manifest(SCRIPT)
        self.factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
