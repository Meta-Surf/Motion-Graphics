import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { calculateAudioVolumeAtFrame } from "./audio-envelope.ts";

describe("audio track envelope", () => {
  it("fades in and out", () => {
    const track = { durationInFrames: 100, volume: 0.8, fadeInFrames: 10, fadeOutFrames: 20 };
    assert.equal(calculateAudioVolumeAtFrame(track, 0), 0);
    assert.equal(calculateAudioVolumeAtFrame(track, 5), 0.4);
    assert.equal(calculateAudioVolumeAtFrame(track, 90), 0.4);
    assert.equal(calculateAudioVolumeAtFrame(track, 100), 0);
  });
  it("ducks music in marked speech windows", () => {
    const track = { durationInFrames: 120, volume: 0.8, ducking: [{ startFrame: 30, endFrame: 90, gain: 0.25 }] };
    assert.equal(calculateAudioVolumeAtFrame(track, 29), 0.8);
    assert.equal(calculateAudioVolumeAtFrame(track, 30), 0.2);
    assert.equal(calculateAudioVolumeAtFrame(track, 90), 0.8);
  });
  it("clamps ducking gain and returns silence outside the track", () => {
    const track = { durationInFrames: 20, volume: 1, ducking: [{ startFrame: 0, endFrame: 3, gain: -1 }] };
    assert.equal(calculateAudioVolumeAtFrame(track, 1), 0);
    assert.equal(calculateAudioVolumeAtFrame(track, -1), 0);
    assert.equal(calculateAudioVolumeAtFrame(track, 20), 0);
  });
});
