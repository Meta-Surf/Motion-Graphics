"""Read-only probe, run with the installed VoiceStudio WSL Python. Does not load a model."""
import json
import torch
if not torch.cuda.is_available() or not torch.version.hip:
    raise SystemExit('ROCm device unavailable; do not switch to CPU')
free,total=torch.cuda.mem_get_info()
print(json.dumps(dict(torch=torch.__version__,hip=torch.version.hip,device=torch.cuda.get_device_name(0),free_bytes=free,total_bytes=total)))
