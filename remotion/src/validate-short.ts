import {getTimelineDuration} from './timeline.ts';
export type CaptionCue={startFrame:number;endFrame:number;text:string};
export function validateShort(props:{scenes:readonly {id:string;durationInFrames:number}[];audioTracks?:readonly {id:string;fromFrame?:number;durationInFrames:number}[];captions?:readonly CaptionCue[]}):number {
  if(!props.scenes.length) throw new Error('A Short needs at least one scene');
  const ids=new Set<string>();
  for(const s of props.scenes){if(!s.id||ids.has(s.id))throw new Error('Scene IDs must be unique and non-empty');ids.add(s.id);}
  const duration=getTimelineDuration(props.scenes,12);
  for(const t of props.audioTracks??[]) {
    if(!Number.isInteger(t.fromFrame??0)||(t.fromFrame??0)<0||!Number.isInteger(t.durationInFrames)||t.durationInFrames<=0) throw new Error('Invalid audio timing');
    if((t.fromFrame??0)+t.durationInFrames>duration)throw new Error('Audio extends past the video; extend the scene timeline');
  }
  let end=0;
  for(const c of props.captions??[]){
    if(!Number.isInteger(c.startFrame)||!Number.isInteger(c.endFrame)||c.startFrame<end||c.endFrame<=c.startFrame||c.endFrame>duration||!c.text.trim())throw new Error('Invalid or overlapping caption cue');
    end=c.endFrame;
  }
  return duration;
}
