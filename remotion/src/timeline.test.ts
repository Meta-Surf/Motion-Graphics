import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { getTimelineDuration, getTimelineLayout } from "./timeline.ts";

describe("Remotion scene timeline", () => {
  it("subtracts overlaps and ends at the last active scene frame", () => {
    const scenes = [{ durationInFrames: 360 }, { durationInFrames: 360 }, { durationInFrames: 360 }];
    const timeline = getTimelineLayout(scenes, 12);
    assert.deepEqual(timeline.items.map((item) => item.from), [0, 348, 696]);
    assert.equal(timeline.durationInFrames, 1056);
    assert.equal(getTimelineDuration(scenes, 12), 1056);
  });
  it("handles a single scene, no overlap, and an empty list", () => {
    assert.equal(getTimelineDuration([{ durationInFrames: 90 }], 12), 90);
    assert.equal(getTimelineDuration([{ durationInFrames: 90 }, { durationInFrames: 60 }], 0), 150);
    assert.equal(getTimelineDuration([], 12), 0);
  });
  it("rejects invalid scene lengths and overlaps", () => {
    assert.throws(() => getTimelineLayout([{ durationInFrames: 0 }]), /positive integer/);
    assert.throws(() => getTimelineLayout([{ durationInFrames: 10 }, { durationInFrames: 20 }], 10), /longer than the overlap/);
    assert.throws(() => getTimelineLayout([{ durationInFrames: 20 }], -1), /non-negative/);
  });
});
