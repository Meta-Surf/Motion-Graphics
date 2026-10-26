export type MobileCaption={startFrame:number;endFrame:number;text:string};

export function validateMobileTimeline(durations:number[],captions:MobileCaption[]=[]):number{
 if(durations.length!==9||durations.some(x=>!Number.isInteger(x)||x<=0))throw new Error('Nine positive integer scene durations are required.');
 const total=durations.reduce((a,b)=>a+b,0);
 if(total<900||total>1800)throw new Error('Mobile Short duration must be 30–60s at 30fps.');
 let previousEnd=0;
 for(const cue of captions){
  if(!Number.isInteger(cue.startFrame)||!Number.isInteger(cue.endFrame)||cue.startFrame<previousEnd||cue.endFrame<=cue.startFrame||cue.endFrame>total||!cue.text.trim())throw new Error('Captions must be ordered, nonempty, nonoverlapping and inside the video.');
  previousEnd=cue.endFrame;
 }
 return total;
}

export function mobileSceneAt(frame:number,durations:number[]){
 const total=durations.reduce((a,b)=>a+b,0),f=Math.max(0,Math.min(total-.0001,frame));
 let start=0;
 for(let i=0;i<durations.length;i++){
  if(f<start+durations[i])return {index:i,start,frame:f-start,duration:durations[i]};
  start+=durations[i];
 }
 throw new Error('No mobile scene');
}
