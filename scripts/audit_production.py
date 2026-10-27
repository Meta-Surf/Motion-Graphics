"""Read-only local audit; private details stay in the local report, never print secrets."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from asset_library import Library, write_json

def command(args, cwd=ROOT, timeout=30):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, errors='replace', timeout=timeout)
        return dict(exit_code=r.returncode, output=r.stdout.strip(), error=r.stderr.strip())
    except (OSError, subprocess.TimeoutExpired) as e: return dict(error=str(e), exit_code=None)

def http(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r: return dict(status=r.status, response=json.load(r))
    except Exception as e: return dict(error=str(e))

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'output/maintenance/audit-20261027/current.json');a=p.parse_args()
    report=dict(observed_at=datetime.now(timezone.utc).isoformat(), machine=os.environ.get('COMPUTERNAME') or os.uname().nodename)
    report['git']={name:command(args) for name,args in {
      'status':['git','status','--porcelain=v1','--untracked-files=normal'], 'head':['git','rev-parse','HEAD'],
      'branches':['git','branch','-vv'], 'remote_heads':['git','ls-remote','--heads','origin'],
      'worktrees':['git','worktree','list'], 'tracked_files':['git','ls-files']}.items()}
    report['voice']=http('http://127.0.0.1:3901/health')
    report['voice_profiles']=http('http://127.0.0.1:3901/profiles')
    report['cloudflare']=dict(account_configured=bool(os.getenv('CLOUDFLARE_ACCOUNT_ID')),token_configured=bool(os.getenv('CLOUDFLARE_API_TOKEN')),live_generation_tested=False,reason='No generation or quota consumption during audit')
    report['tools']={n:shutil.which(n) for n in ('python','node','npm','ffmpeg','ffprobe','gh','editonny','concat','uv')}
    report['versions']={n:command(args) for n,args in {'python':[sys.executable,'--version'],'node':['node','--version'],'ffmpeg':['ffmpeg','-version'],'ffprobe':['ffprobe','-version']}.items()}
    if os.name=='nt':
        report['gpu']=command(['powershell','-NoProfile','-Command','Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion | ConvertTo-Json'])
        report['processes']=command(['powershell','-NoProfile','-Command',"Get-Process | Where-Object ProcessName -match 'concat|editonny|voice|ffmpeg' | Select-Object ProcessName,Id | ConvertTo-Json"])
        report['wsl']=command(['wsl','--list','--verbose'])
    paths=[ROOT/'remotion/public',ROOT/'output',Path.home()/'Videos/CanalVideos',Path.home()/'Videos/Artificial Curiosity']
    report['media_roots']=[]
    for path in paths:
        counts=Counter();size=0
        if path.exists():
            for file in path.rglob('*'):
                if file.is_file():
                    counts[file.suffix.lower()]+=1;size+=file.stat().st_size
        report['media_roots'].append(dict(path=str(path),exists=path.exists(),files_by_extension=dict(counts),bytes=size))
    lib=Library()
    try:
        report['library']=lib.verify()
        report['assets']=[dict(id=x['id'],description=x['description'],category=x['category'],alpha=x['metadata'].get('alpha'),duration=x['metadata'].get('duration'),originals=[s['original'] for s in x['sources']]) for x in lib.search(limit=1000)]
    finally:lib.close()
    write_json(a.output,report)
    print(json.dumps(dict(report=str(a.output),machine=report['machine'],voice=report['voice'],library=report['library'],assets=[{k:v for k,v in x.items() if k!='originals'} for x in report['assets']]),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
