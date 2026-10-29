"""Bridge library selections and multilingual scene plans into the existing AiVideo contract."""
import argparse
import json
import math
from pathlib import Path
from asset_library import Library, sha, write_json
from build_composition import assemble_narration, wav_info
from video_contract import ROOT, FORMATS, digest, validate_composition, validate_schema


def compile_project(plan, language, library, public, preview=False):
    validate_schema(plan, 'production-plan.schema.json')
    if language not in plan['voices']: raise ValueError('Language version has no voice approval')
    ids=[s['id'] for s in plan['scenes']]
    if len(set(ids))!=len(ids): raise ValueError('Duplicate scene IDs')
    selections_path=library.root/'projects'/plan['project_id']/'resources.json'
    selections=json.loads(selections_path.read_text(encoding='utf-8'))['scenes']
    signature=digest(dict(plan=plan, selections=selections, language=language, preview=preview))[:24]
    public=Path(public).resolve();package=public/'generated'/plan['project_id']/signature
    package.mkdir(parents=True,exist_ok=True)
    scenes=[];takes=[];cursor=0;used=[]
    for scene in plan['scenes']:
        selected=selections.get(scene['id'],{})
        if not set(scene['resources_needed']).issubset(selected): raise ValueError('Required scene resources have not been selected')
        if 'background' not in selected: raise ValueError('Scene needs a library background selection: '+scene['id'])
        narration=scene['narration'].get(language)
        if not narration: raise ValueError('Scene has no narration for '+language)
        audio=library.get(narration['asset_id'])
        if audio['category']!='audio': raise ValueError('Narration must be audio')
        if not preview and audio['approval']!='approved': raise ValueError('Narration rights/review pending')
        audio_path=library.path(audio['file'])
        if sha(audio_path)!=audio['sha256']: raise ValueError('Narration hash mismatch')
        (_,_,rate),samples=wav_info(audio_path)
        frames=math.ceil(samples*plan['fps']/rate)
        if scene.get('duration_seconds'):
            requested=math.ceil(scene['duration_seconds']*plan['fps'])
            if frames>requested: raise ValueError('Speech exceeds declared scene duration; do not truncate or speed it up')
            frames=requested
        takes.append((audio_path,frames))
        compiled=dict(id=scene['id'],title=scene['title'],template_id=scene['template_id'],fromFrame=cursor,durationInFrames=frames,labels=scene.get('labels',[]))
        layers=[]
        for name,choice in selected.items():
            if choice.get('preview') and not preview: raise ValueError('Preview selection cannot become production silently')
            asset=library.get(choice['asset_id'])
            if name == 'motion':
                reference=asset['metadata'].get('component', {})
                source=(ROOT/reference.get('source', '')).resolve()
                if not source.is_relative_to(ROOT) or not source.is_file() or sha(source)!=reference.get('source_sha256'):
                    raise ValueError('Motion source changed; refresh the component reference')
                if reference.get('template_id') not in ('layers','object3d','dataflow','cutaway','scale','compare'):
                    raise ValueError('Component is not an AiVideo template')
                if not preview and asset['approval']!='approved':raise ValueError('Motion review pending')
                compiled['template_id']=reference['template_id']
                used.append(dict(asset_id=asset['id'],scene=scene['id'],layer=name,sha256=asset['sha256'],license=asset['license'],rights=asset['rights'],approval=asset['approval']))
                continue
            if asset['category'] not in ('image','background','texture','cutout','overlay'): raise ValueError('This bridge accepts still layers only; use the existing Flow attach for video')
            path=library.export(asset['id'],public,preview)
            if name=='background': compiled['image']=path
            else:
                if asset['metadata'].get('alpha')!='transparent': raise ValueError('Foreground layer needs verified transparent pixels')
                position=scene.get('composition',{}).get(name,dict(x=.52,y=.53,width=.68,depth=1))
                layers.append(dict(id=name,image=path,**position))
            used.append(dict(asset_id=asset['id'],scene=scene['id'],layer=name,sha256=asset['sha256'],license=asset['license'],rights=asset['rights'],approval=asset['approval']))
        if layers:compiled['layers']=layers
        cues=scene.get('captions',{}).get(language,[])
        if any(c['end_seconds']>samples/rate or c['start_seconds']>=c['end_seconds'] for c in cues):raise ValueError('Caption cue outside actual audio')
        if cues:compiled['highlight_cues']=[dict(text=c['text'],startFrame=math.floor(c['start_seconds']*plan['fps']),endFrame=math.ceil(c['end_seconds']*plan['fps'])) for c in cues]
        scenes.append(compiled);cursor+=frames
        used.append(dict(asset_id=audio['id'],scene=scene['id'],layer='narration',sha256=audio['sha256'],license=audio['license'],rights=audio['rights'],approval=audio['approval']))
    width,height,_,_=FORMATS[plan['video_type']]
    props=dict(schema_version=1,project_id=plan['project_id'],title=plan['title'],video_type=plan['video_type'],fps=plan['fps'],width=width,height=height,durationInFrames=cursor,audio=(package/'narration.wav').relative_to(public).as_posix(),scenes=scenes)
    validate_composition(props)
    assemble_narration(takes,package/'narration.wav',plan['fps'])
    write_json(package/'production.json',dict(plan=plan,language=language,assets=used,preview=preview,voice=plan['voices'][language],audio_sha256=sha(package/'narration.wav'),qa=dict(technical='compiled',script='pending',visual='pending',listening='pending')))
    for item in used:
        with library.lock(),library.db:
            library.db.execute('INSERT OR IGNORE INTO usages VALUES (?,?,?,?,?)',(item['asset_id'],plan['project_id'],item['scene'],item['layer'],__import__('asset_library').now()))
    return props

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan',type=Path);p.add_argument('--language',required=True);p.add_argument('--root',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--preview',action='store_true');a=p.parse_args()
    lib=Library(a.root)
    try:result=compile_project(json.loads(a.plan.read_text(encoding='utf-8-sig')),a.language,lib,ROOT/'remotion/public',a.preview);write_json(a.output,result);print(json.dumps(dict(output=str(a.output),duration_seconds=result['durationInFrames']/result['fps'],preview=a.preview)))
    finally:lib.close()
