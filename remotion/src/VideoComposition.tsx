import {ReusableLayers} from './ReusableLayers';
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {MotionTemplate} from './MotionTemplates';
import {safeZone, type CompiledScene, type VideoCompositionProps} from './video-contract';

/** Fit existing 936x900 motion artwork into a responsive panel, retaining its proportions. */
const MotionPanel: React.FC<{scene: CompiledScene; width: number; height: number}> = ({scene, width, height}) => {
  if (scene.template_id === 'photo_essay') return null;
  const scale = Math.min(width / 936, height / 900);
  return <div style={{width, height, overflow: 'hidden', position: 'relative'}}>
    <div style={{position: 'absolute', left: (width - 936 * scale) / 2, top: (height - 900 * scale) / 2,
      width: 936, height: 900, transform: `scale(${scale})`, transformOrigin: 'top left'}}>
      <div style={{position: 'absolute', width: 1080, height: 1920, left: -72, top: -650}}>
        <MotionTemplate layout={scene.template_id} color="#85f7d2" labels={scene.labels} duration={scene.durationInFrames}/>
      </div>
    </div>
  </div>;
};

const DirectedScene: React.FC<{scene: CompiledScene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const {width, height, fps} = useVideoConfig();
  const safe = safeZone(width, height);
  const horizontal = width > height;
  const phase = frame / Math.max(1, scene.durationInFrames - 1);
  const reveal = interpolate(frame, [0, Math.max(1, Math.min(fps * .4, scene.durationInFrames - 1))], [0, 1], {extrapolateRight: 'clamp'});
  const textWidth = horizontal ? safe.width * .43 : safe.width;
  const panelWidth = horizontal ? safe.width * .53 : safe.width;
  const panelHeight = horizontal ? safe.height : safe.height * .57;
  return <AbsoluteFill style={{overflow: 'hidden', background: '#080c16', color: 'white', fontFamily: 'Arial, sans-serif'}}>
    <Img src={staticFile(scene.image)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${1.02 + phase * .045})`}}/>
    <AbsoluteFill style={{background: horizontal
      ? 'linear-gradient(90deg, #040a12f2 5%, #040a12c9 42%, #040a1240 80%)'
      : 'linear-gradient(180deg, #040a12bd, #040a1240 50%, #040a12de)'}}/>
    <AbsoluteFill style={{left: safe.left, top: safe.top, width: safe.width, height: safe.height}}>
      <div style={{position: 'absolute', left: 0, top: horizontal ? safe.height * .18 : 0,
        width: textWidth, opacity: reveal, transform: `translateY(${(1 - reveal) * 24}px)`}}>
        <div style={{color: '#85f7d2', fontSize: horizontal ? 20 : 24, letterSpacing: 3, marginBottom: 26}}>MOTION</div>
        <div style={{fontSize: horizontal ? 64 : 76, fontWeight: 800, lineHeight: 1.08, overflowWrap: 'anywhere'}}>{scene.title}</div>
      </div>
      <div style={{position: 'absolute', right: 0, bottom: 0}}>
        <MotionPanel scene={scene} width={panelWidth} height={panelHeight}/>
      </div>
    </AbsoluteFill>
    <ReusableLayers scene={scene}/>
  </AbsoluteFill>;
};

export const VideoComposition: React.FC<VideoCompositionProps> = ({scenes, audio}) => <AbsoluteFill>
  {scenes.map(scene => <Sequence key={scene.id} from={scene.fromFrame} durationInFrames={scene.durationInFrames}>
    <DirectedScene scene={scene}/>
  </Sequence>)}
  <Audio src={staticFile(audio)}/>
</AbsoluteFill>;
