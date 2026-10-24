import assert from 'node:assert/strict';
import {it} from 'node:test';
import {sampleLayerMotion} from './layer-motion.ts';
import {validateShort} from './validate-short.ts';
it('holds between staged keyframes and preserves omitted transforms',()=>{
 const keys=[{frame:0,x:100,opacity:0},{frame:10,x:0,opacity:1,easing:'easeOut' as const},{frame:50},{frame:59,opacity:0}];
 assert.equal(sampleLayerMotion(25,60,undefined,undefined,keys).x,0);
 assert.equal(sampleLayerMotion(25,60,undefined,undefined,keys).opacity,1);
 assert.equal(sampleLayerMotion(59,60,undefined,undefined,keys).opacity,0);
 assert.throws(()=>sampleLayerMotion(0,60,undefined,undefined,[{frame:10},{frame:2}]),/increasing/);
});
it('a moving layer remains opaque unless explicitly faded',()=>{assert.equal(sampleLayerMotion(20,60,{x:100},{x:0}).opacity,1)});
it('validates production props instead of inheriting the demo duration',()=>{
 assert.equal(validateShort({scenes:[{id:'long',durationInFrames:1800}]}),1800);
 assert.throws(()=>validateShort({scenes:[]}),/at least/);
 assert.throws(()=>validateShort({scenes:[{id:'x',durationInFrames:100}],audioTracks:[{id:'voice',durationInFrames:101}]}),/past the video/);
 assert.throws(()=>validateShort({scenes:[{id:'x',durationInFrames:100}],captions:[{startFrame:80,endFrame:110,text:'ends too late'}]}),/caption/);
});
