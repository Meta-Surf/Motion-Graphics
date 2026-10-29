"""Probe ROCm compute with the installed VoiceStudio WSL Python; no model or voice."""
import json
import os
from pathlib import Path

# ROCm on WSL requires DXG detection, as does the production service.
if Path('/dev/dxg').exists():
    os.environ.setdefault('HSA_ENABLE_DXG_DETECTION', '1')

import torch

report = dict(torch=torch.__version__, hip=torch.version.hip,
              cuda_api_available=torch.cuda.is_available())
if not report['cuda_api_available'] or not report['hip']:
    print(json.dumps(report))
    raise SystemExit('ROCm device unavailable; do not switch to CPU')
probe = torch.arange(1024, dtype=torch.float32, device='cuda')
result = (probe * 2).sum().item()
torch.cuda.synchronize()
if result != 1047552:
    raise SystemExit('GPU compute returned an unexpected result')
free, total = torch.cuda.mem_get_info()
report.update(device=torch.cuda.get_device_name(0), free_bytes=free,
              total_bytes=total, compute='passed', model_inference='not_run')
print(json.dumps(report))
