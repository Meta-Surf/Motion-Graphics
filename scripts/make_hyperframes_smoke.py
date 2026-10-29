"""Generate an offline diagnostic with SVG, quiet tone and timed captions; no stock or private media."""
from pathlib import Path
import argparse,json,math,struct,sys,wave
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from hyperframes_bridge import compile_hyperframes
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--layers',action='store_true');a=p.parse_args()
    if a.output.exists():p.error('Choose a new diagnostic directory')
    a.output.mkdir(parents=True);public=a.output/'public';media=public/'generated/hf-smoke';media.mkdir(parents=True)
    (media/'background.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920"><defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="#03101c"/><stop offset="1" stop-color="#124355"/></linearGradient></defs><rect width="1080" height="1920" fill="url(#g)"/><circle cx="500" cy="700" r="200" fill="#76f0ce" opacity=".25"/></svg>')
    with wave.open(str(media/'tone.wav'),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000)
        w.writeframes(b''.join(struct.pack('<h',int(700*math.sin(2*math.pi*220*i/16000))) for i in range(16000*15)))
    props=dict(schema_version=1,project_id='hf-smoke',title='Local diagnostic',video_type='short_9_16',fps=24,width=1080,height=1920,durationInFrames=360,audio='generated/hf-smoke/tone.wav',scenes=[dict(id='diagnostic-one',template_id='photo_essay',title='HYPERFRAMES / LOCAL',fromFrame=0,durationInFrames=360,image='generated/hf-smoke/background.svg',labels=[],highlight_cues=[dict(text='LOCAL PIPELINE VALIDATION',startFrame=24,endFrame=300)])])
    if a.layers:
        (media/'foreground.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300"><rect x="20" y="20" width="560" height="260" rx="25" fill="#76f0ce"/><rect x="100" y="70" width="400" height="160" fill="#124355"/></svg>')
        props['scenes'][0].update(template_id='layers',layers=[dict(id='foreground',image='generated/hf-smoke/foreground.svg',x=.5,y=.5,width=.68,depth=1)])
    (a.output/'props.json').write_text(json.dumps(props,indent=2))
    print(json.dumps(compile_hyperframes(props,public,a.output/'project',ROOT/'hyperframes/node_modules/gsap/dist/gsap.min.js')))
