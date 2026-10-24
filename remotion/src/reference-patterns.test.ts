import {test} from 'node:test';
import assert from 'node:assert/strict';
import {REFERENCE_STUDY,phonePoses,poseAt} from './reference-patterns.ts';

test('reference blocks cover every decoded frame once, including the last frame',()=>{
 const {blocks,durationInFrames}=REFERENCE_STUDY;
 assert.equal(blocks[0].start,0);assert.equal(blocks.at(-1)?.end,durationInFrames);
 const counts=new Uint8Array(durationInFrames);
 for(const b of blocks)for(let f=b.start;f<b.end;f++)counts[f]++;
 assert.ok(counts.every(n=>n===1));
});

test('phone rig produces finite positive scale through spins and fractional subframes',()=>{
 for(let f=-1;f<=130;f+=.25){
  const p=poseAt(f);
  assert.ok(Object.values(p).every(Number.isFinite));
  assert.ok(p.scale>0);
 }
 assert.equal(poseAt(34).scale,1);
 assert.equal(poseAt(7).ry,174);
 assert.equal(poseAt(150).scale,phonePoses.at(-1)?.scale);
});
