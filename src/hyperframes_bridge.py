"""Compile the existing Motion composition contract to a portable local HyperFrames project.

No provider calls, model downloads, library mutations or publishing. Only reviewed
2D photo_essay/layers templates are supported; other templates stay in Remotion.
"""
from __future__ import annotations
import argparse, hashlib, html, json, math, os, re, shutil, wave
from pathlib import Path
from video_contract import ROOT, validate_composition, write_json

SUPPORTED = {'photo_essay', 'layers'}

def js(value):
    return json.dumps(value, ensure_ascii=True).replace('<', '\\u003c')

def safe_asset(public: Path, relative: str) -> Path:
    if not isinstance(relative, str) or '\\' in relative or ':' in relative:
        raise ValueError('Asset must use a relative POSIX path')
    p = (public / relative).resolve()
    if not p.is_relative_to(public.resolve()) or not p.is_file():
        raise ValueError('Missing asset or path outside the public directory: ' + relative)
    return p

def group_words(words, duration, max_words=5, pause=.15):
    groups, current, previous = [], [], -1
    for word in words:
        start, end = word['start'], word['end']
        if (not isinstance(word.get('text'), str) or len(word['text'].split()) != 1
            or not all(isinstance(t, (int,float)) and math.isfinite(t) for t in (start,end))
            or not 0 <= start < end <= duration or start < previous):
            raise ValueError('Invalid measured word timestamps')
        previous = end
        if current and (len(current) >= max_words or (len(current)>1 and start-current[-1]['end'] >= pause)
                        or re.search(r'[.!?]$',current[-1]['text'])):
            groups.append(current); current=[]
        current.append(word)
    if current: groups.append(current)
    return [dict(text=' '.join(w['text'] for w in g), start=g[0]['start'],
                 end=min(g[-1]['end']+.06, groups[i+1][0]['start'] if i+1<len(groups) else duration))
            for i,g in enumerate(groups)]

def compile_hyperframes(props, public, destination, gsap, profile=None, words=None):
    validate_composition(props)
    public, destination, gsap = Path(public).resolve(), Path(destination).resolve(), Path(gsap).resolve()
    if destination.exists(): raise ValueError('Destination exists; choose a new project directory')
    if not gsap.is_file(): raise ValueError('Install pinned hyperframes dependencies with npm ci first')
    profile = profile or json.loads((ROOT/'hyperframes/profiles/artificial-curiosity.json').read_text(encoding='utf-8'))
    width, height, fps = props['width'], props['height'], props['fps']
    duration = props['durationInFrames']/fps
    for scene in props['scenes']:
        if scene['template_id'] not in SUPPORTED:
            raise ValueError('Template '+scene['template_id']+' requires Remotion; no silent 3D/motion conversion')
        if scene.get('video'): raise ValueError('Video scenes require Remotion until the media adapter is validated')
        for layer in scene.get('layers',[]):
            if layer['x']-layer['width']/2 < 0 or layer['x']+layer['width']/2 > 1 or not .35 <= layer['y'] <= .65:
                raise ValueError('Foreground box exceeds the protected hero stage; revise its position/width')
    # Preflight every reference before creating any output, including symlink resolution.
    sources = [props['audio']] + [s['image'] for s in props['scenes']] + [l['image'] for s in props['scenes'] for l in s.get('layers',[])]
    resolved = {s:safe_asset(public,s) for s in sources}
    with wave.open(str(resolved[props['audio']]), 'rb') as voice:
        audio_seconds=voice.getnframes()/voice.getframerate()
    if abs(audio_seconds-duration) > 1/fps + 1e-6:
        raise ValueError('Timeline must match measured WAV duration within one frame; do not retime speech')
    cues = group_words(words,duration,profile['captions']['maxWords'],profile['captions']['pauseSeconds']) if words is not None else None
    if cues is None:
        cues = [dict(text=c['text'], start=(s['fromFrame']+c['startFrame'])/fps,
                     end=(s['fromFrame']+c['endFrame'])/fps)
                for s in props['scenes'] for c in s.get('highlight_cues',[])]
    for i,c in enumerate(cues):
        if c['start'] >= c['end'] or (i and c['start'] < cues[i-1]['end']-1e-6):
            raise ValueError('Caption cues overlap or have no visible duration')
    layout = profile['portrait' if height>width else 'landscape']
    def n(key): return layout[key]
    destination.mkdir(parents=True);(destination/'assets').mkdir();(destination/'compositions').mkdir()
    shutil.copyfile(gsap,destination/'assets/gsap.min.js')
    ledger={}; indexed={}
    def asset(source):
        p=resolved[source]; digest=hashlib.sha256(p.read_bytes()).hexdigest();relative='assets/'+digest+p.suffix.lower()
        target=destination/relative
        if not target.exists():
            try: os.link(p,target)
            except OSError: shutil.copyfile(p,target)
        ledger[source]=dict(path=relative,sha256=digest,origin=str(p));indexed[digest]=relative
        return relative
    audio=asset(props['audio']);hosts=[]
    for i,s in enumerate(props['scenes']):
        ident=f'scene-{i:03}';length=s['durationInFrames']/fps;start=s['fromFrame']/fps
        bg=asset(s['image']);layers=[];motion=[]
        for k,l in enumerate(s.get('layers',[])):
            left=n('heroX')+l.get('x',.5)*n('heroWidth');top=n('heroY')+l.get('y',.5)*n('heroHeight')
            size=l.get('width',.68)*n('heroWidth')
            lid=f'layer-{k}'
            # A contained stage protects captions even during oversized parallax.
            layers.append(f'<div class="layer-anchor" style="left:{left-n("heroX")-size/2}px;top:{top-n("heroY")-n("heroHeight")*.35}px;width:{size}px;height:{n("heroHeight")*.7}px;z-index:{round(l["depth"]*100)}"><img id="{lid}" src="{asset(l["image"])}" style="width:100%;height:100%;object-fit:contain;display:block"></div>')
            motion.append(f'tl.fromTo("#{lid}",{{opacity:0}},{{opacity:1,duration:.45,ease:"power2.out"}},.1);')
        markup=f'''<template><style>*{{box-sizing:border-box}}#root{{position:absolute;inset:0;overflow:hidden;background:{profile['colors']['background']};color:{profile['colors']['text']};font-family:{profile['font']},Arial,sans-serif}}.photo{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}.scrim{{position:absolute;inset:0;background:linear-gradient(180deg,#03101c88,#03101c33 40%,#03101c 76%)}}.title{{position:absolute;left:{n('titleX')}px;top:{n('titleY')}px;width:{n('titleWidth')}px;font-size:{n('titleSize')}px;line-height:1.05;font-weight:800;overflow-wrap:anywhere}}.stage{{position:absolute;left:{n('heroX')}px;top:{n('heroY')}px;width:{n('heroWidth')}px;height:{n('heroHeight')}px;overflow:hidden}}.layer-anchor{{position:absolute}}</style><div id="root" data-composition-id="{ident}" data-width="{width}" data-height="{height}"><img id="photo" class="photo" data-layout-allow-overflow src="{bg}"><div class="scrim"></div><div class="title">{html.escape(s['title'])}</div><div class="stage">{''.join(layers)}</div></div><script>(()=>{{const tl=gsap.timeline({{paused:true}});tl.fromTo("#photo",{{scale:1.06}},{{scale:1,duration:{length},ease:"none"}},0);{''.join(motion)}window.__timelines=window.__timelines||{{}};window.__timelines[{js(ident)}]=tl;}})();</script></template>'''
        (destination/f'compositions/{ident}.html').write_text(markup,encoding='utf-8')
        hosts.append(f'<div id="host-{i}" data-composition-id="{ident}" data-composition-src="compositions/{ident}.html" data-start="{start}" data-duration="{length}" data-width="{width}" data-height="{height}" data-track-index="{i}" data-track-kind="graphics"></div>')
    # Captions have a separate protected host and animate children, never timed wrappers.
    caption_markup=[];caption_js=[]
    for i,c in enumerate(cues):
        caption_markup.append(f'<div id="cue-{i}" class="cue clip" data-start="{c["start"]}" data-duration="{c["end"]-c["start"]}" data-track-index="0"><span>{html.escape(c["text"])}</span></div>')
        caption_js.append(f'tl.fromTo("#cue-{i} span",{{opacity:0,y:7}},{{opacity:1,y:0,duration:.09}},{c["start"]});tl.set("#cue-{i} span",{{opacity:0}},{c["end"]});')
    captions=f'''<template><style>*{{box-sizing:border-box}}#root{{position:absolute;inset:0;pointer-events:none;font-family:{profile['font']},Arial,sans-serif;color:white}}.cue{{position:absolute;left:{n('captionX')}px;top:{n('captionY')}px;width:{n('captionWidth')}px;height:{n('captionHeight')}px;display:flex;justify-content:center;align-items:center}}.cue span{{opacity:0;max-width:100%;padding:16px 22px;background:#03101cdd;border-radius:10px;font-size:{n('captionSize')}px;line-height:1.18;font-weight:800;text-align:center;overflow-wrap:anywhere}}</style><div id="root" data-composition-id="captions" data-width="{width}" data-height="{height}">{''.join(caption_markup)}</div><script>(()=>{{const tl=gsap.timeline({{paused:true}});{''.join(caption_js)}window.__timelines=window.__timelines||{{}};window.__timelines.captions=tl;}})();</script></template>'''
    (destination/'compositions/captions.html').write_text(captions,encoding='utf-8')
    root=f'''<!doctype html><html><head><meta charset="utf-8"><script src="assets/gsap.min.js"></script><style>*{{box-sizing:border-box}}body{{margin:0;background:#03101c}}#root{{position:relative;width:{width}px;height:{height}px;overflow:hidden}}</style></head><body><div id="root" data-composition-id="main" data-width="{width}" data-height="{height}" data-fps="{fps}" data-duration="{duration}">{''.join(hosts)}<div id="caption-host" class="clip" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{duration}" data-width="{width}" data-height="{height}" data-track-index="1000" data-track-kind="captions" style="position:absolute;inset:0;z-index:100"></div><audio id="narration" class="clip" src="{audio}" data-start="0" data-duration="{duration}" data-volume="1" data-track-index="1001"></audio></div><script>window.__timelines=window.__timelines||{{}};window.__timelines.main=gsap.timeline({{paused:true}});</script></body></html>'''
    (destination/'index.html').write_text(root,encoding='utf-8')
    write_json(destination/'production.json',dict(renderer='hyperframes',version='0.8.211',project_id=props['project_id'],assets=ledger,unique_assets=len(indexed),qa=dict(technical='compiled',visual='pending',listening='pending'),profile=profile['id']))
    write_json(destination/'captions.json',cues)
    return dict(project=str(destination),duration_seconds=duration,scenes=len(props['scenes']),captions=len(cues))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('composition',type=Path);p.add_argument('--public',type=Path,default=ROOT/'remotion/public');p.add_argument('--output',type=Path,required=True);p.add_argument('--words',type=Path);p.add_argument('--profile',type=Path);a=p.parse_args()
    print(json.dumps(compile_hyperframes(json.loads(a.composition.read_text(encoding='utf-8-sig')),a.public,a.output,ROOT/'hyperframes/node_modules/gsap/dist/gsap.min.js',profile=json.loads(a.profile.read_text(encoding='utf-8-sig')) if a.profile else None,words=json.loads(a.words.read_text(encoding='utf-8-sig')) if a.words else None)))
