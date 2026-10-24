import React from "react";
import { Audio, Img, interpolate, useCurrentFrame } from "remotion";
import { calculateAudioVolumeAtFrame, type AudioEnvelope } from "./audio-envelope";

export type LayerTransform = { x?: number; y?: number; scale?: number; rotate?: number; opacity?: number };
export type SceneLayer = {
  id: string;
  src: string;
  role?: "background" | "foreground" | "overlay";
  startFrame?: number;
  durationInFrames?: number;
  fit?: "cover" | "contain";
  bounds?: { left?: string | number; top?: string | number; width?: string | number; height?: string | number; objectPosition?: string };
  from?: LayerTransform;
  to?: LayerTransform;
  zIndex?: number;
};
export type AudioTrack = AudioEnvelope & {
  id: string;
  src: string;
  kind: "voice" | "music" | "sfx";
  fromFrame?: number;
  startFrom?: number;
};

const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

export const SceneLayerImage: React.FC<{
  layer: SceneLayer;
  sceneDuration: number;
  opacityMultiplier?: number;
}> = ({ layer, sceneDuration, opacityMultiplier = 1 }) => {
  const frame = useCurrentFrame();
  const start = Math.max(0, layer.startFrame ?? 0);
  const duration = Math.max(1, layer.durationInFrames ?? sceneDuration);
  const localFrame = frame - start;
  const hasMotion = Boolean(layer.from || layer.to);
  const from = {
    x: layer.from?.x ?? 0,
    y: layer.from?.y ?? 0,
    scale: layer.from?.scale ?? 1,
    rotate: layer.from?.rotate ?? 0,
    opacity: layer.from?.opacity ?? (hasMotion ? 0 : 1),
  };
  const to = {
    x: layer.to?.x ?? 0,
    y: layer.to?.y ?? 0,
    scale: layer.to?.scale ?? 1,
    rotate: layer.to?.rotate ?? 0,
    opacity: layer.to?.opacity ?? 1,
  };
  const value = (key: keyof typeof from) => interpolate(localFrame, [0, duration], [from[key], to[key]], clamp);
  const active = localFrame >= 0 && localFrame < duration;
  const defaultZ = layer.role === "background" ? 0 : layer.role === "overlay" ? 6 : 3;
  return <Img
    src={layer.src}
    style={{
      position: "absolute",
      left: layer.bounds?.left ?? 0,
      top: layer.bounds?.top ?? 0,
      width: layer.bounds?.width ?? "100%",
      height: layer.bounds?.height ?? "100%",
      objectFit: layer.fit ?? (layer.role === "background" ? "cover" : "contain"),
      objectPosition: layer.bounds?.objectPosition ?? "center",
      transform: "translate(" + value("x") + "px," + value("y") + "px) scale(" + value("scale") + ") rotate(" + value("rotate") + "deg)",
      opacity: active ? Math.max(0, Math.min(1, value("opacity") * opacityMultiplier)) : 0,
      zIndex: layer.zIndex ?? defaultZ,
    }}
  />;
};

export const AudioTrackPlayer: React.FC<{ track: AudioTrack }> = ({ track }) => (
  <Audio
    src={track.src}
    startFrom={track.startFrom ?? 0}
    volume={(frame) => calculateAudioVolumeAtFrame(track, frame)}
  />
);
