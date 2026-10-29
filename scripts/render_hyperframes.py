"""Validate/preview/render a compiled HyperFrames project using the repository's pinned CLI."""
import argparse, json, os, subprocess, sys, re, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gpu_resources import gpu_lease
from contextlib import nullcontext

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('project',type=Path);p.add_argument('--action',choices=['check','preview','render','snapshot'],default='check')
    p.add_argument('--output',type=Path);p.add_argument('--gpu',action='store_true');p.add_argument('--workers',type=int,default=2)
    a=p.parse_args();project=a.project.resolve()
    if not (project/'index.html').is_file():p.error('Project index.html missing')
    cli=ROOT/'hyperframes/node_modules/.bin'/('hyperframes.cmd' if os.name=='nt' else 'hyperframes')
    if not cli.is_file():p.error('Run npm ci --prefix hyperframes')
    if a.action=='check':args=['check',str(project),'--json']
    elif a.action=='snapshot':args=['snapshot',str(project),'--review']
    elif a.action=='preview':args=['preview',str(project),'--background']
    else:
        if a.output is None:p.error('--output is required for render')
        if a.output.exists():p.error('Output exists; choose a new filename')
        if not 1<=a.workers<=8:p.error('workers must be between 1 and 8')
        # A failed official check must stop delivery; no automatic best-effort fallback.
        checked=subprocess.run([str(cli),'check',str(project),'--json'],check=True,capture_output=True,text=True,encoding="utf-8",errors="replace")
        if json.loads(checked.stdout).get('ok') is not True:raise RuntimeError('Official check did not pass')
        args=['render',str(project),'--quality','delivery','--workers',str(a.workers),'--strict','--no-best-effort','-o',str(a.output.resolve())]
        args+=['--gpu','--browser-gpu'] if a.gpu else ['--no-browser-gpu']
    with gpu_lease('hyperframes-render') if a.action=='render' else nullcontext():
        return execute(cli,args,a,project)

def execute(cli,args,a,project):
    start=time.perf_counter()
    code=subprocess.run([str(cli),*args]).returncode
    if code or a.action!='render':return code
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(a.output)]))
    video=next((s for s in probe['streams'] if s['codec_type']=='video'),{})
    audio=next((s for s in probe['streams'] if s['codec_type']=='audio'),{})
    source=(project/'index.html').read_text(encoding='utf-8')
    for key in ('width','height'):
        expected=re.search(r'data-'+key+r'="([0-9]+)"',source)
        if expected and video.get(key)!=int(expected[1]):raise RuntimeError('Export dimensions do not match project')
    expected_duration=re.search(r'data-duration="([0-9.]+)"',source)
    expected_fps=re.search(r'data-fps="([0-9]+)"',source)
    from fractions import Fraction
    if expected_fps and Fraction(video.get('avg_frame_rate','0/1'))!=int(expected_fps[1]):raise RuntimeError('Export FPS differs from project')
    if expected_duration:
        duration=float(expected_duration[1]);tolerance=1/int(expected_fps[1]) if expected_fps else .05
        if abs(float(video.get('duration',0))-duration)>tolerance+.001 or abs(float(audio.get('duration',0))-duration)>.05:raise RuntimeError('Export video/audio duration differs from project')
    if video.get('codec_name')!='h264' or audio.get('codec_name')!='aac':raise RuntimeError('Delivery requires H.264 and AAC')
    subprocess.run(['ffmpeg','-v','error','-i',str(a.output),'-f','null','-'],check=True)
    report=dict(output=str(a.output.resolve()),seconds=round(time.perf_counter()-start,3),requested_gpu=a.gpu,
        encoder_tag=video.get('tags',{}).get('encoder'),probe=probe,decode='passed',visual='pending',listening='pending')
    with a.output.with_suffix('.render.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    return 0
if __name__=='__main__':sys.exit(main())
