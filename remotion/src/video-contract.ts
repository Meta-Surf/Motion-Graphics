/** Authoring contract: runtime source of truth is schemas/video-director.schema.json. */
export type VideoType = 'short_9_16' | 'long_16_9';
export const templateIds = ['photo_essay', 'layers', 'object3d', 'dataflow', 'cutaway', 'scale', 'compare'] as const;
export type TemplateId = typeof templateIds[number];
export interface DirectorScene {
  id: string;
  template_id: TemplateId;
  title: string;
  narration_text: string;
  image_prompt: string;
  seed: number;
  duration_seconds?: number;
  labels?: string[];
}
export interface VideoDirector {
  schema_version: 1;
  project_id: string;
  title: string;
  video_type: VideoType;
  fps: 24 | 25 | 30 | 60;
  voice: {profile_id: string; steps?: 16 | 32};
  art_direction: {palette: string; lighting: string; camera: string; continuity: string};
  scenes: DirectorScene[];
}
export interface CompiledScene {
  layers?: Array<{id: string; image: string; x: number; y: number; width: number; depth: number}>;
  highlight_cues?: Array<{text: string; startFrame: number; endFrame: number}>;
  id: string;
  template_id: TemplateId;
  title: string;
  fromFrame: number;
  durationInFrames: number;
  image: string;
  labels: string[];
}
export type VideoCompositionProps = {
  schema_version: 1;
  project_id: string;
  title: string;
  video_type: VideoType;
  fps: 24 | 25 | 30 | 60;
  width: number;
  height: number;
  durationInFrames: number;
  audio: string;
  scenes: CompiledScene[];
};

export const videoFormats = {
  short_9_16: {width: 1080, height: 1920, minSeconds: 15, maxSeconds: 180},
  long_16_9: {width: 1920, height: 1080, minSeconds: 480, maxSeconds: 1800},
} as const;

export function safeZone(width: number, height: number) {
  const vertical = height > width;
  // Editorial margins, adjustable after checking the destination player's UI.
  const left = Math.round(width * (vertical ? .07 : .05));
  const right = Math.round(width * (vertical ? .15 : .05));
  const top = Math.round(height * (vertical ? .08 : .06));
  const bottom = Math.round(height * (vertical ? .18 : .10));
  return {left, right, top, bottom, width: width - left - right, height: height - top - bottom};
}

export function validateVideo(props: VideoCompositionProps) {
  const format = videoFormats[props.video_type];
  if (!format || props.schema_version !== 1 || ![24, 25, 30, 60].includes(props.fps)
      || props.width !== format.width || props.height !== format.height) {
    throw new Error('Invalid video format or schema version');
  }
  const assetPattern = /^generated\/[a-z0-9-]+\/[a-zA-Z0-9/_.-]+$/;
  const validAsset = (path: string) => typeof path === 'string' && assetPattern.test(path) && !path.split('/').includes('..');
  if (!validAsset(props.audio) || !Array.isArray(props.scenes) || !props.scenes.length) throw new Error('Missing narration or scenes');
  const ids = new Set<string>();
  let cursor = 0;
  for (const scene of props.scenes) {
    if (!/^[a-z0-9][a-z0-9-]{2,63}$/.test(scene.id) || ids.has(scene.id)
        || scene.fromFrame !== cursor || !Number.isSafeInteger(scene.durationInFrames) || scene.durationInFrames < 1
        || !templateIds.includes(scene.template_id) || !validAsset(scene.image)
        || typeof scene.title !== 'string' || !scene.title.trim() || scene.title.length > 70
        || !Array.isArray(scene.labels) || scene.labels.length > 5 || scene.labels.some(label => typeof label !== 'string' || !label.trim() || label.length > 28)) {
      throw new Error('Invalid scene, template, asset or discontinuous timeline');
    }
    if (scene.layers && (!Array.isArray(scene.layers) || scene.layers.length > 16 || new Set(scene.layers.map(l => l.id)).size !== scene.layers.length || scene.layers.some(l =>
      !/^[a-z0-9][a-z0-9_-]{0,63}$/.test(l.id) || !validAsset(l.image) || ![l.x,l.y,l.width,l.depth].every(Number.isFinite)
      || l.x < 0 || l.x > 1 || l.y < 0 || l.y > 1 || l.width <= 0 || l.width > 2 || l.depth < 0 || l.depth > 3))) throw new Error('Invalid reusable layer');
    if (scene.highlight_cues && (!Array.isArray(scene.highlight_cues) || scene.highlight_cues.length > 1000 || scene.highlight_cues.some(c =>
      !Number.isSafeInteger(c.startFrame) || !Number.isSafeInteger(c.endFrame) || c.startFrame < 0 || c.endFrame <= c.startFrame
      || c.endFrame > scene.durationInFrames || typeof c.text !== 'string' || !c.text.trim() || c.text.length > 180))) throw new Error('Invalid speech cue');
    ids.add(scene.id);
    cursor += scene.durationInFrames;
  }
  if (cursor !== props.durationInFrames || cursor / props.fps < format.minSeconds || cursor / props.fps > format.maxSeconds) {
    throw new Error(`Duration outside ${format.minSeconds}–${format.maxSeconds} seconds`);
  }
  return {durationInFrames: cursor, width: format.width, height: format.height, fps: props.fps};
}
