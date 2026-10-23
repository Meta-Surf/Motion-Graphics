#!/usr/bin/env python3
"""Process queued Cloudflare image-generation jobs.

Jobs are JSON manifests under jobs/pending. Completed manifests are moved to
jobs/processed only after every requested image was generated successfully.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from providers.cloudflare_workers_ai import DEFAULT_MODEL, generate  # noqa: E402

PENDING = ROOT / "jobs" / "pending"
PROCESSED = ROOT / "jobs" / "processed"
OUTPUT = ROOT / "output" / "generated"
SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SAFE_FILE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,100}$")


def main() -> int:
    PENDING.mkdir(parents=True, exist_ok=True)
    jobs = sorted(PENDING.glob("*.json"))
    if not jobs:
        print("Fila vazia; nenhuma chamada à Cloudflare.")
        return 0

    for manifest in jobs:
        job = json.loads(manifest.read_text(encoding="utf-8"))
        job_id = job.get("job_id", "")
        images = job.get("images")
        if not SAFE_ID.fullmatch(job_id) or not isinstance(images, list) or not 1 <= len(images) <= 8:
            raise SystemExit(f"Manifesto inválido: {manifest.name}")
        print(f"Processando job {job_id}: {len(images)} imagens.")
        for item in images:
            filename = item.get("filename", "")
            prompt = item.get("prompt", "")
            width = item.get("width", 1024)
            height = item.get("height", 1792)
            seed = item.get("seed")
            if not SAFE_FILE.fullmatch(filename) or not filename.lower().endswith((".png", ".jpg", ".webp")):
                raise SystemExit(f"Nome de arquivo inválido no job {job_id}.")
            if not isinstance(prompt, str) or not 30 <= len(prompt) <= 3000:
                raise SystemExit(f"Prompt inválido no job {job_id}, arquivo {filename}.")
            if not isinstance(width, int) or not isinstance(height, int):
                raise SystemExit(f"Dimensões inválidas no job {job_id}.")
            if seed is not None and (not isinstance(seed, int) or seed < 0):
                raise SystemExit(f"Seed inválido no job {job_id}.")
            print(f"Gerando {filename}...")
            generate(prompt, OUTPUT / job_id / filename, width, height, DEFAULT_MODEL, seed)
        PROCESSED.mkdir(parents=True, exist_ok=True)
        destination = PROCESSED / manifest.name
        if destination.exists():
            raise SystemExit(f"Job já processado: {manifest.name}")
        shutil.move(str(manifest), str(destination))
        print(f"Job concluído: {job_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
