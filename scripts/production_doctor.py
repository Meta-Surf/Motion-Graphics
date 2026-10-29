"""Bounded technical inventory without generation, installs, model loads or secret dumps."""
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import urllib.request

ROOT=Path(__file__).resolve().parents[1]


def run(args):
    try:
        p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,errors='replace',timeout=20)
        return dict(exit_code=p.returncode,stdout=p.stdout.strip(),stderr=p.stderr.strip())
    except (OSError,subprocess.TimeoutExpired) as exc:
        return dict(exit_code=None,error=type(exc).__name__)


def inventory():
    report=dict(host=platform.node(),platform=platform.platform(),python=sys.version,
                git={key:run(['git',*args]) for key,args in dict(head=['rev-parse','HEAD'],status=['status','--short','--branch'],worktrees=['worktree','list']).items()},
                tools={name:dict(path=shutil.which(name),state='installed' if shutil.which(name) else 'absent') for name in ('node','npm','ffmpeg','ffprobe','uv')},
                storage=dict(zip(('total','used','free'),shutil.disk_usage(ROOT))))
    report['versions']={name:run(args) for name,args in dict(node=['node','--version'],ffmpeg=['ffmpeg','-version'],ffprobe=['ffprobe','-version']).items()}
    for name,cli in dict(remotion=ROOT/'remotion/node_modules/@remotion/cli/remotion-cli.js',hyperframes=ROOT/'hyperframes/node_modules/.bin'/('hyperframes.cmd' if os.name=='nt' else 'hyperframes')).items():
        report[name]=dict(state='installed' if cli.is_file() else 'absent',path=str(cli),sample='not_run')
        if cli.is_file():report[name]['version']=run(['node',str(cli),'--version'] if name=='remotion' else [str(cli),'--version'])
    try:
        with urllib.request.urlopen(os.getenv('MOTION_VOICE_URL','http://127.0.0.1:3901').rstrip('/')+'/health',timeout=5) as response:
            health=json.load(response)
        report['voice_health']={key:health.get(key) for key in ('status','device','version')}
    except Exception as exc:
        report['voice_health']=dict(error=type(exc).__name__)
    report['voice_inference']='not_run; health is not a generation test'
    if os.name=='nt':
        report['gpu']=run(['powershell.exe','-NoProfile','-Command','Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion | ConvertTo-Json'])
        report['wsl']=run(['wsl','--list','--verbose'])
        for name in ('Concat','VoiceStudio'):
            directory=Path(os.getenv('LOCALAPPDATA',str(Path.home()/'AppData/Local')))/'Programs'/name
            report[name]=dict(state='installed' if directory.is_dir() else 'absent',path=str(directory),sample='not_run')
    report['note']='Installed/version/health observations are not sampled or production approval. Inspect source media with production.py inspect. No profile, credential, media or model content is included.'
    return report

if __name__=='__main__':print(json.dumps(inventory(),ensure_ascii=False,indent=2))
