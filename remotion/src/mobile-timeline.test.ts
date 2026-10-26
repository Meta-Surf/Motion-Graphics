import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mobileSceneAt,validateMobileTimeline} from './mobile-timeline.ts';
const durations=[180,210,240,165,339,180,141,192,153];
test('mobile timeline places fractional blur samples at the correct scene boundary',()=>{
 assert.equal(mobileSceneAt(179.9,durations).index,0);
 assert.equal(mobileSceneAt(180,durations).index,1);
 assert.equal(mobileSceneAt(1800,durations).index,8);
 assert.equal(mobileSceneAt(-.5,durations).index,0);
 assert.equal(validateMobileTimeline(durations),1800);
});
test('mobile export rejects captions beyond the video or over another caption',()=>{
 assert.throws(()=>validateMobileTimeline(durations,[{startFrame:1790,endFrame:1801,text:'fim'}]),/Captions/);
 assert.throws(()=>validateMobileTimeline(durations,[{startFrame:0,endFrame:30,text:'um'},{startFrame:29,endFrame:60,text:'dois'}]),/Captions/);
 assert.throws(()=>validateMobileTimeline([180,210]),/Nine/);
});
