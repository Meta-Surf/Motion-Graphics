import {test} from 'node:test';
import assert from 'node:assert/strict';
import {metricValue,normalizedLevels,typedText} from './editorial-motion.ts';
test('verified metric cannot render as evidence without source and date',()=>{
 assert.throws(()=>metricValue(1,{value:77,label:'itens',kind:'verified'}),/source/);
 assert.equal(metricValue(1,{value:21,label:'padrões',kind:'verified',source:'catalog.json',asOf:'2026-10-26'}),21);
 assert.equal(metricValue(5,{value:120,label:'demo',kind:'illustrative'}),120);
});
test('audio reactor stays at rest without input and rejects nonfinite levels',()=>{
 assert.deepEqual(normalizedLevels([],4),[0,0,0,0]);
 assert.deepEqual(normalizedLevels([NaN,-1,2,.5],4),[0,0,1,.5]);
});
test('typing preserves graphemes and clamps the reveal interval',()=>{
 assert.equal(typedText('e\u0301🔊',.5),'e\u0301');
 assert.equal(typedText('VOZ',3),'VOZ');
 assert.equal(typedText('VOZ',-1),'');
});
