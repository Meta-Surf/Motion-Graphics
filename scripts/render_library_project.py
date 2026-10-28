"""Render compiled library props with explicit ANGLE/AMF and the contract's actual WAV."""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from asset_library import Library,sha,write_json
from video_contract import read_json,validate_composition,public_asset
from build_composition import wav_info

def require_hardware_render(exit_code, diagnostic):
    import re
    clean=re.sub(r'\x1b\[[0-9;]*m','',diagnostic)
    required=('Canvas','Compositing','Rasterization','WebGL')
    if exit_code or any(not re.search(r'^'+feature+r': Hardware accelerated',clean,re.M) for feature in required):
        raise RuntimeError('Hardware rendering guard failed; inspect .gpu.json and recover acceleration before retrying')
    return clean

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('props',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--browser',type=Path);p.add_argument('--recover-silent',type=Path,help='Explicitly recover a known silent AMF render; never automatic');p.add_argument('--renderer',choices=['remotion','hyperframes'],default='remotion');p.add_argument('--public',type=Path,default=ROOT/'remotion/public');p.add_argument('--gpu',action='store_true',help='Explicit GPU mode for HyperFrames; default CPU is benchmark-backed');p.add_argument('--words',type=Path);a=p.parse_args()
    if a.renderer=='hyperframes':
        if a.recover_silent:p.error('--recover-silent is a Remotion-only recovery path')
        from hyperframes_bridge import compile_hyperframes
        project=a.output.resolve().with_suffix('.hyperframes')
        compile_hyperframes(read_json(a.props),a.public,project,ROOT/'hyperframes/node_modules/gsap/dist/gsap.min.js',words=json.loads(a.words.read_text(encoding='utf-8-sig')) if a.words else None)
        command=[sys.executable,str(ROOT/'scripts/render_hyperframes.py'),str(project),'--action','render','--output',str(a.output.resolve())]
        if a.gpu:command.append('--gpu')
        subprocess.run(command,check=True);sys.exit(0)
    props=read_json(a.props);validate_composition(props);audio=public_asset(props['audio'])
    (_,_,rate),samples=wav_info(audio)
    if abs(samples/rate-props['durationInFrames']/props['fps'])>1/rate:raise ValueError('Narration does not match scene timing')
    output=a.output.resolve()
    if output.exists():raise ValueError('Output exists; use a new version')
    output.parent.mkdir(parents=True,exist_ok=True)
    library=Library();lock=library.root/'gpu.lock';library.close()
    with lock.open('x') as f:f.write(json.dumps(dict(pid=os.getpid(),task='render-amf')))
    start=time.perf_counter();preflight=None
    browser=a.browser or Path(os.getenv('MOTION_RENDER_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
    try:
        if a.recover_silent:
            source=a.recover_silent.resolve()
            command=[sys.executable,str(ROOT/'scripts/finalize_short.py'),str(source),'--voice',str(audio),'--output',str(output),'--video-type',props['video_type']]
        else:
            if not browser.is_file():raise ValueError('Set --browser to an existing Chromium; GPU fallback is disabled')
            checked=subprocess.run(['node',str(ROOT/'remotion/node_modules/@remotion/cli/remotion-cli.js'),'gpu','--gl=angle','--browser-executable='+str(browser)],cwd=ROOT/'remotion',capture_output=True,text=True,errors='replace',timeout=60)
            import re
            preflight=re.sub(r'\x1b\[[0-9;]*m','',checked.stdout+checked.stderr)
            write_json(output.with_suffix('.gpu.json'),dict(browser=str(browser),exit_code=checked.returncode,diagnostic=preflight))
            preflight=require_hardware_render(checked.returncode,preflight)
            command=['node',str(ROOT/'remotion/render-amf.mjs'),'--composition','AiVideo','--props',str(a.props.resolve()),'--voice',str(audio),'--output',str(output),'--python',sys.executable,'--browser',str(browser)]
        with output.with_suffix('.log').open('wb') as log:subprocess.run(command,cwd=ROOT/'remotion',stdout=log,stderr=subprocess.STDOUT,check=True,timeout=3600)
        report=dict(output=str(output),sha256=sha(output),seconds=round(time.perf_counter()-start,3),encoder='h264_amf',scene_backend='chromium-angle',gpu_preflight=preflight,audio_sha256=sha(audio),props_sha256=sha(a.props),recovered_silent=str(a.recover_silent) if a.recover_silent else None,qa=dict(technical='finalizer-passed',visual='pending',listening='pending'),vram_bytes=None,ram_bytes=None)
        write_json(output.with_suffix('.production-render.json'),report);print(json.dumps(report,indent=2))
    finally:lock.unlink(missing_ok=True)
