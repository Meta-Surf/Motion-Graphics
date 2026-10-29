# HyperFrames local integration

> Para novos pedidos, siga primeiro [o procedimento operacional](production-procedure.md).
> Este guia descreve uma rota específica; suporte, aprovação e escolha de ferramenta
> são definidos pelo briefing e pela [matriz de compatibilidade](contract-compatibility.md).


HyperFrames is an additional renderer for the existing Motion composition contract
and SQLite media library. Remotion remains the default. VoiceStudio remains the
narrator; no new paid generation, cloud rendering or publishing is enabled.

## Versions and installation

Node >=22, FFmpeg/FFprobe in PATH, Python >=3.12. The independent npm package pins
**HyperFrames 0.8.211**, **GSAP 3.14.2**, and optional **onnxruntime-node 1.21.1**.
`hyperframes/package-lock.json` is authoritative. The previous V5 lab used 0.8.210;
that lab and its media were not upgraded in place.

PowerShell, from the repository root:

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r scripts/requirements-pipeline.txt
npm.cmd ci --prefix hyperframes
npm.cmd --prefix hyperframes run doctor
npm.cmd --prefix hyperframes run skills:update
```

For local cutouts only:

```powershell
& .\.venv\Scripts\python.exe -m pip install -r hyperframes/requirements-media.txt
```

Core skills plus `remotion-to-hyperframes` are refreshed by the explicit command;
Figma/slideshow stay on demand. Models never download during npm installation or
CI. Nothing changes VoiceStudio, the existing Remotion dependency tree or billing.

The project CLI reads ignored `hyperframes/local.json`. Copy
`hyperframes/local.example.json`, set the installed whisper.cpp path, then run the
project doctor again. Explicit HYPERFRAMES_WHISPER_PATH takes precedence. The
wrapper blocks cloud/lambda/cloudrun/publish commands in this local integration.
The local JSON and the environment are never committed or printed.

## Shared library and renderer selection

Continue selecting/approving assets in the existing `asset_library.py` SQLite/FTS5
library and compiling the production plan with `compile_library_project.py`.
The resulting composition JSON is the same input for either renderer:

```powershell
& .\.venv\Scripts\python.exe scripts/render_library_project.py props.json --renderer hyperframes --output output/new-version.mp4
```

The adapter creates `output/new-version.hyperframes/` next to the MP4, then runs
the official check, strict render, FFprobe and full decode. Destination existence
is an error. `--gpu` explicitly selects browser GPU and GPU encoding; the default
is software capture/CPU based on the DACOL benchmark, not an assumption that AMF
is always faster. Reports record requested GPU mode and observed encoder metadata.
Omitting `--renderer` keeps the existing Remotion/AMF path.

`--public` selects the asset root when compiling props exported by another
worktree. Defaults to this checkout's `remotion/public`. All referenced paths are
resolved below that root, including symlinks. Asset bytes are deduplicated by
SHA-256 inside each project and hardlinked when supported; save a new file before
editing linked media. No new SQLite database or silent rights approval is created.

Supported bridge templates: `photo_essay`, `layers`. They preserve content,
frame timing and selected asset positions in a native layout; they do not promise
Remotion pixel parity. Other motion/3D/video templates fail explicitly and stay in
Remotion until a matching native/hosted adapter is validated. The pinned CLI can
still author/render arbitrary independently validated HyperFrames compositions.

Standalone compilation and editing:

```powershell
& .\.venv\Scripts\python.exe src/hyperframes_bridge.py props.json --output output/editable-project
& .\.venv\Scripts\python.exe scripts/render_hyperframes.py output/editable-project --action preview
& .\.venv\Scripts\python.exe scripts/render_hyperframes.py output/editable-project --action snapshot
& .\.venv\Scripts\python.exe scripts/render_hyperframes.py output/editable-project --action render --output output/new-render.mp4
```

The compiler rejects a WAV/timeline mismatch greater than one frame. Titles are
escaped, unsupported templates are not approximated silently, and foregrounds are
contained above a dedicated caption region. Foreground boxes outside that region are rejected;
images use object-fit:contain so their silhouettes are not cropped. Native timed cues come from existing
`highlight_cues`; pass `--words transcript.json` to use measured ASR words instead.
The caption compiler groups by pauses, punctuation and maximum word count. It
rejects non-finite, reversed, overlapping or out-of-range timestamps. It does not
invent speech timings. See `hyperframes/frame.md` and the profile JSON.

## Models and audio

`hyperframes/models.json` pins download URL, size, SHA-256 and purpose. Binaries
live outside Git, by default in `~/.cache/motion-graphics/models`. Reuse local
verified files without another download:

```powershell
& .\.venv\Scripts\python.exe scripts/hyperframes_models.py whisper-base.en --from-file PATH_TO_EXISTING_GGML_BASE_EN
& .\.venv\Scripts\python.exe scripts/hyperframes_models.py u2netp --from-file PATH_TO_EXISTING_U2NETP
```

Or explicitly add `--download` instead of `--from-file`. Corrupt existing cache
files are rejected without overwrite. `--check` verifies a cached model.

- Whisper base.en: 147,964,211 bytes, local English transcription; whisper.cpp
  executable required. The DACOL test uses the existing portable 1.7.6 x64 runtime.
- U2-NetP: 4,574,861 bytes, CPU inference using the pinned Node runtime. It passed
  controlled silhouettes but failed details/complex photos in the prior lab;
  every new cutout needs review. The human-only native model is not a hardware default.
- Parakeet and Kokoro remain optional; no large model or replacement narrator is
  installed merely to expand a dependency list. Preserve upstream model terms.

```powershell
& .\.venv\Scripts\python.exe scripts/hyperframes_media.py transcribe narration.wav --model PATH_TO_VERIFIED_BASE_EN --whisper PATH_TO_WHISPER_CLI --output output/transcript.json
& .\.venv\Scripts\python.exe scripts/hyperframes_media.py cutout hardware.jpg --model PATH_TO_VERIFIED_U2NETP --output output/hardware-cutout.png
```

ASR uses the native HyperFrames CLI with English base.en and no runtime auto-install.
It reuses verified model bytes in the native HyperFrames model cache. It treats
`ok:false`/skipped as failure even if the CLI exits zero. Review recognized words
against the narration before using captions. Cutouts write a QA sidecar with
`approval: pending`; inspect light, dark and contrasting backgrounds and reject
missing parts, halos or incomplete contours. No automatic import/approval happens.

VoiceStudio exports a WAV through the existing adapter. This integration does not
change its voice identity, speech speed or locale settings. The existing adapter's
Portuguese default is not silently reused to generate English speech. Editonny and
Concat receive ordinary local MP4/SRT files; no undocumented API is assumed.

## Reproducible validation

```powershell
& .\.venv\Scripts\python.exe scripts/test_hyperframes.py
& .\.venv\Scripts\python.exe scripts/test_asset_library.py
& .\.venv\Scripts\python.exe scripts/test_library_project.py
& .\.venv\Scripts\python.exe scripts/make_hyperframes_smoke.py --output output/hf-smoke-new
& .\.venv\Scripts\python.exe scripts/render_hyperframes.py output/hf-smoke-new/project --action render --output output/hf-smoke-new/validation.mp4
```

Add `--layers` to the diagnostic command to exercise a transparent foreground.
The diagnostic uses a generated SVG, quiet tone and authored timed labels, not a
fake voice or measured ASR transcript. The CI workflow runs offline contract tests,
not media generation or model downloads. Actual render/ASR/cutout results are
recorded in `docs/hyperframes-validation.md`; do not infer visual approval from CI.

## Updating and rollback

Update only in a new branch/worktree: inspect official release docs, change the
pin with npm, commit the new lockfile, run contract/library tests and the real
render/check/snapshot again. Verify models by registry hash. Do not commit private
media, local profiles, voice takes, model binaries or renders. The old V5 lab and
existing production worktree remain rollback points; changing renderer is explicit.

Sources: https://github.com/heygen-com/hyperframes ,
https://github.com/ggml-org/whisper.cpp , https://github.com/danielgatis/rembg .
