export type Transform = {x?: number; y?: number; scale?: number; rotate?: number; opacity?: number};
export type LayerKeyframe = Transform & {frame: number; easing?: 'linear'|'easeIn'|'easeOut'|'easeInOut'};
const defaults = {x: 0, y: 0, scale: 1, rotate: 0, opacity: 1};
export type ResolvedTransform = typeof defaults;
export function sampleLayerMotion(frame: number, duration: number, from?: Transform, to?: Transform, keys?: LayerKeyframe[]): ResolvedTransform {
  const frames = keys?.length ? keys : [{frame:0,...defaults,...from},{frame:Math.max(1,duration-1),...defaults,...to}];
  let previous = -1;
  let state = {...defaults};
  const resolved = frames.map(k => {
    if (!Number.isInteger(k.frame) || k.frame < 0 || k.frame <= previous) throw new Error('Layer keyframes must have increasing non-negative integer frames');
    previous=k.frame;
    const {frame: at, easing, ...values}=k;
    for (const v of Object.values(values)) if (!Number.isFinite(v)) throw new Error('Layer transforms must be finite');
    state={...state,...values};
    return {frame:at,easing,value:{...state}};
  });
  if(frame<=resolved[0].frame) return resolved[0].value;
  for(let i=1;i<resolved.length;i++) {
    const a=resolved[i-1],b=resolved[i];
    if(frame>b.frame) continue;
    let t=(frame-a.frame)/(b.frame-a.frame);
    if(b.easing==='easeIn') t=t*t*t;
    if(b.easing==='easeOut') t=1-(1-t)**3;
    if(b.easing==='easeInOut') t=t<.5?4*t*t*t:1-(-2*t+2)**3/2;
    return Object.fromEntries(Object.keys(defaults).map(key=>{const k=key as keyof ResolvedTransform;return [k,a.value[k]+(b.value[k]-a.value[k])*t]})) as ResolvedTransform;
  }
  return resolved[resolved.length-1].value;
}
