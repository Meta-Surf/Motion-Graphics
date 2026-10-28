# HyperFrames integration — validation on DACOL, 2026-10-28

The integration pins HyperFrames **0.8.211**, upgraded from the isolated V5 lab's
0.8.210. That lab was not modified. The implementation was tested in a separate
worktree, with Python dependencies in its own virtual environment.

## Automated checks

| Check | Observed result |
|---|---|
| HyperFrames adapter/model/local-CLI regression tests | 16 passed |
| Existing asset-library tests | 7 passed |
| Existing library-project compiler tests | 5 passed |
| Remotion unit tests | 20 passed |
| Remotion TypeScript typecheck | Passed |
| Python source compilation | Passed |
| Official check before each diagnostic render | Passed |
| H.264/AAC, dimensions and full FFmpeg decode | Passed for diagnostic outputs |

The tests cover path containment, title escaping, content deduplication, immutable
destinations, WAV/timeline matching, caption ordering/overlap, foreground safe
bounds, explicit unsupported-template rejection, model checksums and local-only
deployment commands. They make no paid provider calls.

## Actual local execution

- CPU render through the standalone adapter: generated a 15-second 1080×1920,
  24 fps diagnostic with SVG, quiet tone and authored timed captions. The tone
  is a diagnostic, not generated speech or an ASR accuracy test.
- Render through the existing library entrypoint with --renderer hyperframes
  --gpu: H.264 AMF confirmed by encoder tag
  `Lavc63.1.102 h264_amf`, hardware browser capture, 18.6 seconds reported by the
  renderer; 21.416 seconds including wrapper verification.
- Final foreground-layer diagnostic: CPU/libx264, 15 seconds, 1080×1920/24 fps,
  19.6 seconds reported by renderer, 22.061 seconds including wrapper verification.
  Transparent foreground, title and caption zone were inspected.
- The native snapshot tool produced frames at 1, 7.5, 14.9 seconds and an extra
  tail sample. A backward-seek snapshot showed an inconsistent position; actual
  MP4 frames at 1, 7.5 and 14.75 seconds had the same foreground bounds
  [256, 676, 769, 913] before and after using explicit anchor coordinates.
  Therefore the snapshot anomaly is not claimed as a defect in the delivered
  MP4. Final layout avoids percentage transforms for foreground anchors.
- Native transcription through the new media adapter: 13 word timestamps from
  a real existing English VoiceStudio take; no runtime auto-install or paid API.
- U2-NetP inference through the new media adapter: real archive macro image
  produced PNG alpha and a QA sidecar with approval=pending and edge_contact=true.
  Successful inference is not approval of the matte.
- Model registry reuse: Whisper base.en (147,964,211 bytes) and U2-NetP
  (4,574,861 bytes), both verified against pinned SHA-256. Existing local bytes
  were reused. Neither binary is stored in Git.
- Project doctor recognizes HyperFrames 0.8.211 and the configured portable
  whisper.cpp executable via ignored local configuration. Docker/Kokoro remain
  optional and absent; no claims of their installation or operation are made.

These are integration/capability measurements, not a controlled performance
ranking between CPU and GPU. There was no new 3D conversion benchmark, voice
replacement, Kokoro listening comparison or GUI automation of Editonny/Concat.

## Reproduce

Follow docs/hyperframes.md. Generate a fresh diagnostic directory; existing
outputs are intentionally rejected:

```powershell
& .\.venv\Scripts\python.exe scripts/test_hyperframes.py
& .\.venv\Scripts\python.exe scripts/make_hyperframes_smoke.py --layers --output output/hf-new
& .\.venv\Scripts\python.exe scripts/render_hyperframes.py output/hf-new/project --action render --output output/hf-new/validation.mp4
& .\.venv\Scripts\python.exe scripts/render_hyperframes.py output/hf-new/project --action snapshot
```

Private evidence is under output/hyperframes-validation and the diagnostic
directories in the integration worktree. Media, local runtime paths and model
weights are ignored. The source repository contains the reproduction code,
lockfile, registry, profile and this sanitized summary.

## Scope and preservation

The branch includes the two existing library commits (persistent SQLite library
and library compiler) as prerequisites, then
the HyperFrames integration. It excludes the unrelated unpublished Flow/study
and current production edits from the original worktree.

Remotion stays the default. The native bridge supports photo_essay and layers;
other templates and video stay explicitly on Remotion until their adapters have
been validated. VoiceStudio remains the primary narration source. No main-branch
merge, production publication or production database migration was performed.
