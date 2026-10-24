#!/usr/bin/env python3
"""Mux an AMF video with narration and reject incomplete exports."""
from __future__ import annotations
import argparse, json, shutil, subprocess
from pathlib import Path

def probe(path: Path, ffprobe='ffprobe') -> dict:
    return json.loads(subprocess.check_output([ffprobe,'-v','error','-show_streams','-show_format','-of','json',str(path)],text=True))

def check_media(metadata:dict,require_audio=True,min_seconds=30,max_seconds=60) -> list[str]:
    errors=[];streams=metadata.get('streams',[]);v=next((s for s in streams if s.get('codec_type')=='video'),{});a=next((s for s in streams if s.get('codec_type')=='audio'),{})
    d=float(metadata.get('format',{}).get('duration',0))
    if(v.get('width'),v.get('height'))!=(1080,1920):errors.append('Video must be 1080x1920')
    if v.get('codec_name')!='h264':errors.append('Video must be H.264')
    if not min_seconds<=d<=max_seconds+.05:errors.append(f'Duration {d:.3f}s outside {min_seconds}–{max_seconds}s')
    if require_audio and (not a or a.get('codec_name')!='aac'):errors.append('AAC narration track is required')
    if a and abs(float(a.get('duration',d))-d)>.15:errors.append('Audio/video duration differs by more than 150 ms')
    return errors

def finalize(video:Path,voice:Path,output:Path,ffmpeg='ffmpeg',ffprobe='ffprobe',overwrite=False):
    if output.resolve() in (video.resolve(),voice.resolve()):raise ValueError('Output must preserve the source files')
    if output.exists() and not overwrite:raise FileExistsError(output)
    vd=probe(video,ffprobe);ad=probe(voice,ffprobe);duration=float(vd['format']['duration']);spoken=float(ad['format']['duration'])
    if not any(s.get('codec_type')=='audio' for s in ad.get('streams',[])):raise ValueError('Narration has no audio stream')
    if spoken>duration+.02:raise ValueError(f'Narration ({spoken:.3f}s) exceeds video ({duration:.3f}s); extend the timeline. Audio will not be accelerated or truncated.')
    errors=check_media(vd,require_audio=False)
    if errors:raise ValueError('; '.join(errors))
    output.parent.mkdir(parents=True,exist_ok=True);temp=output.with_name(output.stem+'.partial.mp4')
    # No music/effects are added. Normalization and padding preserve the complete voice.
    subprocess.run([ffmpeg,'-hide_banner','-y','-i',str(video),'-i',str(voice),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','highpass=f=65,loudnorm=I=-16:TP=-1:LRA=7,apad','-t',str(duration),'-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(temp)],check=True)
    result=probe(temp,ffprobe);errors=check_media(result)
    if errors:raise ValueError('; '.join(errors))
    # Decode the complete result to catch truncated packets and corrupt media.
    subprocess.run([ffmpeg,'-v','error','-xerror','-i',str(temp),'-f','null','-'],check=True)
    temp.replace(output)
    result['review']={'technical':'passed','listening':'pending','visual':'pending'}
    output.with_suffix('.qa.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('video',type=Path);p.add_argument('--voice',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--ffprobe',default='ffprobe');p.add_argument('--overwrite',action='store_true');a=p.parse_args();finalize(a.video,a.voice,a.output,a.ffmpeg,a.ffprobe,a.overwrite);print(a.output)
if __name__=='__main__':main()
