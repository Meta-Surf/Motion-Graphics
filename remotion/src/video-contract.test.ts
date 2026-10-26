import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {safeZone, templateIds, validateVideo, type VideoCompositionProps, type VideoType, videoFormats} from './video-contract.ts';

const props = (kind: VideoType, seconds: number): VideoCompositionProps => ({
  schema_version: 1, project_id: 'unit-test', title: 'Test', video_type: kind, fps: 30,
  width: videoFormats[kind].width, height: videoFormats[kind].height, durationInFrames: seconds * 30,
  audio: 'generated/unit-test/voice.wav', scenes: [{id: 'scene-one', template_id: 'photo_essay', title: 'Test',
    fromFrame: 0, durationInFrames: seconds * 30, image: 'generated/unit-test/image.png', labels: []}],
});

test('director and compiled schemas expose exactly the renderer template registry', () => {
  for (const file of ['video-director.schema.json', 'composition.schema.json']) {
    const schema = JSON.parse(fs.readFileSync(new URL(`../../schemas/${file}`, import.meta.url), 'utf8'));
    assert.deepEqual(schema.properties.scenes.items.properties.template_id.enum, templateIds);
  }
});

test('both formats validate exact duration limits and metadata', () => {
  for (const kind of ['short_9_16', 'long_16_9'] as const) {
    const format = videoFormats[kind];
    for (const seconds of [format.minSeconds, format.maxSeconds]) {
      assert.deepEqual(validateVideo(props(kind, seconds)), {width: format.width, height: format.height, fps: 30, durationInFrames: seconds * 30});
    }
    for (const seconds of [format.minSeconds - 1, format.maxSeconds + 1]) assert.throws(() => validateVideo(props(kind, seconds)));
  }
});

test('safe zones reserve player margins and stay inside each canvas', () => {
  for (const {width, height} of Object.values(videoFormats)) {
    const safe = safeZone(width, height);
    assert.equal(safe.width + safe.left + safe.right, width);
    assert.equal(safe.height + safe.top + safe.bottom, height);
    assert.ok(safe.width > 0 && safe.height > 0 && safe.bottom > 0);
  }
});

test('rejects gaps, missing narration and unsafe paths before rendering', () => {
  let value = props('short_9_16', 15);
  value.scenes[0].fromFrame = 1;
  assert.throws(() => validateVideo(value));
  value = props('short_9_16', 15);
  value.audio = '';
  assert.throws(() => validateVideo(value));
  value.audio = 'generated/unit-test/../../secret.wav';
  assert.throws(() => validateVideo(value));
});
