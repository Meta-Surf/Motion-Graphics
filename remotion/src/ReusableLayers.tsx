import React from 'react';
import {Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import type {CompiledScene} from './video-contract';

/** Independent cutouts and measured speech cues. No fabricated back surface or 3D geometry. */
export const ReusableLayers: React.FC<{scene: CompiledScene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const phase = frame / Math.max(1, scene.durationInFrames - 1);
  const enter = interpolate(frame, [0, 15], [0, 1], {extrapolateRight: 'clamp'});
  const cue = scene.highlight_cues?.find(c => frame >= c.startFrame && frame < c.endFrame);
  return <>
    {scene.layers?.map(layer => <Img key={layer.id} src={staticFile(layer.image)} style={{
      position: 'absolute', left: `${layer.x * 100}%`, top: `${layer.y * 100}%`,
      width: `${layer.width * 100}%`, height: 'auto', objectFit: 'contain', opacity: enter,
      transform: `translate(-50%, -50%) translateY(${(1 - enter) * 35 - phase * layer.depth * 18}px) scale(${1 + phase * layer.depth * .025})`,
      filter: 'drop-shadow(0 22px 24px #0009)',
    }}/>)}
    {cue && <div style={{position: 'absolute', bottom: '19%', left: '7%', right: '15%',
      color: '#fff', background: '#08101de8', borderLeft: '5px solid #85f7d2', padding: '18px 22px',
      fontSize: 36, fontWeight: 700, lineHeight: 1.25, textShadow: '0 2px 4px #000'}}>{cue.text}</div>}
  </>;
};
