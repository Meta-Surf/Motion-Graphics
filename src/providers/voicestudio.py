#!/usr/bin/env python3
"""VoiceStudio GPU narration: explicit voice, short cached takes, no tempo changes."""
from __future__ import annotations
import argparse, hashlib, json, os, re, time, urllib.request, wave
from pathlib import Path
DEFAULT_URL = 'http://127.0.0.1:3901'

def require_gpu(health: dict) -> None:
    device = str(health.get('device', '')).lower()
    if health.get('status') != 'ok' or not any(x in device for x in ('cuda', 'rocm', 'hip', 'mps', 'vulkan')) or 'cpu' in device:
        raise RuntimeError(f'GPU voice service required; reported device: {device!r}. Start the WSL GPU service on port 3901. CPU fallback is disabled.')

def split_text(text: str, limit: int = 220) -> list[str]:
    if limit < 40: raise ValueError('Chunk limit must be at least 40 characters')
    chunks, current = [], ''
    for sentence in re.split(r'(?<=[.!?])\s+|\n+', text.strip()):
        for word in sentence.split():
            if len(word)>limit: raise ValueError('A single token exceeds the chunk limit')
            if current and len(current)+len(word)+1>limit:
                chunks.append(current); current=''
            current=(current+' '+word).strip()
        if current: chunks.append(current); current=''
    return chunks

def merge_wavs(paths: list[Path], output: Path, pause_ms: int = 140) -> float:
    if not paths: raise ValueError('No narration chunks')
    audio=[]; params=None
    for p in paths:
        with wave.open(str(p)) as w:
            actual=(w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getcomptype())
            if params is not None and actual!=params: raise ValueError('Incompatible narration WAV formats')
            params=actual; audio.append(w.readframes(w.getnframes()))
    assert params is not None
    channels,width,rate,compression=params
    if width!=2 or compression!='NONE': raise ValueError('Expected signed 16-bit PCM WAV')
    silence=b'\0'*(int(rate*pause_ms/1000)*channels*width)
    output.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(output),'wb') as w:
        w.setnchannels(channels);w.setsampwidth(width);w.setframerate(rate)
        w.writeframes(silence.join(audio))
    return (sum(map(len,audio))+len(silence)*(len(audio)-1))/(rate*channels*width)

class VoiceStudio:
    def __init__(self,url: str = DEFAULT_URL): self.url=url.rstrip('/')
    def health(self):
        with urllib.request.urlopen(self.url+'/health',timeout=15) as r: health=json.load(r)
        require_gpu(health);return health
    def narrate(self,text: str,output: Path,profile: str,steps: int=32) -> dict:
        health=self.health()
        if not profile.strip(): raise ValueError('An approved profile ID is required')
        output=output.resolve();cache=output.parent/'voice-cache';cache.mkdir(parents=True,exist_ok=True)
        with urllib.request.urlopen(self.url+'/profiles/'+profile,timeout=15) as response: profile_state=json.load(response)
        chunks=split_text(text);paths=[];takes=[]
        for chunk in chunks:
            # Recheck before each new take; a restart must never silently select CPU.
            self.health()
            payload={'model':'omnivoice','input':chunk,'voice':profile,'language':'pt','response_format':'wav','num_step':steps,'speed':1.0,'seed':42}
            signature=json.dumps({'request':payload,'server':self.url,'version':health.get('version'),'profile':profile_state},sort_keys=True).encode()
            key=hashlib.sha256(signature).hexdigest();p=cache/(key+'.wav');started=time.perf_counter();cached=p.exists()
            if not cached:
                request=urllib.request.Request(self.url+'/v1/audio/speech',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(request,timeout=240) as response: data=response.read()
                if not data.startswith(b'RIFF'): raise RuntimeError('VoiceStudio returned non-WAV data')
                temp=p.with_suffix('.tmp');temp.write_bytes(data)
                with wave.open(str(temp)) as w:
                    if w.getnframes()<=0: raise RuntimeError('Empty narration')
                temp.replace(p)
            with wave.open(str(p)) as w: seconds=w.getnframes()/w.getframerate()
            paths.append(p);takes.append({'text':chunk,'cache_key':key,'duration_seconds':seconds,'generation_seconds':round(time.perf_counter()-started,3),'cached':cached})
        duration=merge_wavs(paths,output)
        meta={'provider':'voicestudio','url':self.url,'health':health,'profile_id':profile,'steps':steps,'speed':1.0,'duration_seconds':duration,'takes':takes}
        output.with_suffix('.voice.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return meta

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--health',action='store_true');p.add_argument('--url',default=os.getenv('MOTION_VOICE_URL',DEFAULT_URL));p.add_argument('--script',type=Path);p.add_argument('--output',type=Path);p.add_argument('--profile-id');p.add_argument('--steps',type=int,choices=[16,32],default=32);a=p.parse_args();client=VoiceStudio(a.url)
    if a.health: print(json.dumps(client.health()));return
    if not all((a.script,a.output,a.profile_id)):p.error('--script, --output and --profile-id are required')
    print(json.dumps(client.narrate(a.script.read_text(encoding='utf-8-sig'),a.output,a.profile_id,a.steps),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
