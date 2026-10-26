"""Publish immutable image batches in the existing Cloudflare queue format."""
from __future__ import annotations

import re
from pathlib import Path

from video_contract import ROOT, digest, exclusive_lock, read_json, write_json


def enqueue_image_jobs(requests: list[dict], pending: Path, prefix: str = "director") -> list[str]:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,15}", prefix):
        raise ValueError("Invalid queue job prefix")
    requests = list({request["asset_id"]: request for request in requests}.values())
    paths = []
    for start in range(0, len(requests), 8):
        batch = requests[start:start + 8]
        job_id = prefix + "-" + digest(batch)[:40]
        path = pending / (job_id + ".json")
        job = {"job_id": job_id, "images": batch}
        with exclusive_lock(path.with_suffix(".lock")):
            if path.exists() and read_json(path) != job:
                raise ValueError(f"Conflicting queue manifest: {path}")
            if not (ROOT / "jobs" / "processed" / path.name).exists():
                write_json(path, job)
        paths.append(str(path))
    return paths
