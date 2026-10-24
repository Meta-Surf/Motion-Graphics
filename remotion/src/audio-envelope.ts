export type DuckingWindow = {
  startFrame: number;
  endFrame: number;
  gain: number;
};

export type AudioEnvelope = {
  durationInFrames: number;
  volume?: number;
  fadeInFrames?: number;
  fadeOutFrames?: number;
  ducking?: DuckingWindow[];
};

export const calculateAudioVolumeAtFrame = (track: AudioEnvelope, frame: number): number => {
  const duration = Math.max(0, Math.floor(track.durationInFrames));
  if (duration === 0 || frame < 0 || frame >= duration) return 0;
  let volume = Math.max(0, track.volume ?? 1);
  const fadeIn = Math.min(duration, Math.max(0, track.fadeInFrames ?? 0));
  const fadeOut = Math.min(duration, Math.max(0, track.fadeOutFrames ?? 0));
  if (fadeIn > 0) volume *= Math.min(1, frame / fadeIn);
  if (fadeOut > 0) volume *= Math.min(1, (duration - frame) / fadeOut);
  for (const window of track.ducking ?? []) {
    if (frame >= window.startFrame && frame < window.endFrame) {
      volume *= Math.max(0, Math.min(1, window.gain));
    }
  }
  return volume;
};
