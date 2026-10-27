"""Local review pilot: existing media, approved historical voice, zero provider calls.
Run explicitly; TTS uses the existing GPU service. Imported rights remain pending.
"""
import json
import argparse
import os
import sys
import time
import wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from asset_library import Library,write_json,now
from providers.voicestudio import VoiceStudio
from compile_library_project import compile_project

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--profile-id',required=True);parser.add_argument('--profile-evidence',required=True);args=parser.parse_args()
    home=ROOT/'output/library-pilot-v001';home.mkdir(parents=True,exist_ok=True)
    library=Library()
    def choose(description):
        found=[a for a in library.search(description) if a['description']==description]
        if len(found)!=1:raise ValueError('Select a unique existing library resource: '+description)
        return found[0]
    background=choose('studio-empty');cutout=choose('ai-core')
    if cutout['metadata']['alpha']!='transparent':raise ValueError('Cutout has no transparent pixels')
    profile=args.profile_id
    texts=[
      'Antes de gerar uma nova imagem, buscamos os recursos que já existem na biblioteca. O original permanece preservado, e cada cópia recebe uma identificação verificável.',
      'O recorte fica em uma camada independente. Assim, podemos mover o objeto sem mover o fundo. A montagem acompanha a duração real da narração.'
    ]
    plan=dict(schema_version=1,project_id='library-pilot',title='Pesquisar, preservar e reutilizar',video_type='short_9_16',fps=30,voices={'pt-BR':dict(profile_id=profile,approval_evidence=args.profile_evidence)},scenes=[])
    lock=library.root/'gpu.lock'
    with lock.open('x') as f:f.write(json.dumps(dict(pid=os.getpid(),task='library-pilot-tts',at=now())))
    started=time.perf_counter()
    try:
        client=VoiceStudio();health=client.health();takes=[]
        for index,text in enumerate(texts):
            output=home/f'scene-{index+1}.wav'
            meta=client.narrate(text,output,profile)
            asset=library.import_file(output,dict(description=f'library-pilot voice {index+1}',provider='voicestudio',model='omnivoice',parameters=dict(profile_id=profile,speed=1.0,steps=32),origin='Local GPU take with existing historical profile',license='existing-local-voice-profile-review-pending',rights='Local technical review only; do not redistribute reference audio',voice_metadata=meta),category='audio')
            scene=f'scene-{index+1}'
            library.apply(background['id'],'library-pilot',scene,'background',preview=True)
            if index==1:library.apply(cutout['id'],'library-pilot',scene,'object',preview=True)
            captions=[];offset=0
            for take in meta['takes']:
                captions.append(dict(text=take['text'],start_seconds=offset,end_seconds=offset+take['duration_seconds']))
                offset+=take['duration_seconds']+.14
            # Each short phrase cue uses the measured take boundary, not guessed word timing.
            plan['scenes'].append(dict(id=scene,title='Pesquisar antes de gerar' if index==0 else 'Separar para explicar',objective='Demonstrar reutilização e preservação' if index==0 else 'Mostrar movimento independente do recorte',template_id='layers' if index==0 else 'photo_essay',labels=['ORIGINAL','CÓPIA','CATÁLOGO','CENA','REUSO'] if index==0 else [],narration={'pt-BR':dict(text=text,asset_id=asset['id'])},resources_needed=['background'] if index==0 else ['background','object'],new_generation_reason='',composition={'object':dict(x=.49,y=.53,width=.68,depth=1.5)},captions={'pt-BR':captions}))
            takes.append(meta)
        write_json(home/'plan.json',plan)
        props=compile_project(plan,'pt-BR',library,ROOT/'remotion/public',preview=True)
        write_json(home/'composition.json',props)
        report=dict(health=health,voice_profile=profile,takes=takes,seconds=round(time.perf_counter()-started,3),duration_seconds=props['durationInFrames']/props['fps'],provider_generations=0,credits_consumed=0,additional_cost=0,flow_used=False,flow_reason='Existing stills and cutout explain the narrative; no new clip needed',qa=dict(visual='pending',listening='pending',rights='pending; local technical review'))
        write_json(home/'pilot-report.json',report)
        print(json.dumps({k:v for k,v in report.items() if k!='takes'},ensure_ascii=False,indent=2))
    finally:lock.unlink(missing_ok=True);library.close()
