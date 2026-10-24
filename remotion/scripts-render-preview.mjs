import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs/promises';
const root=process.cwd(),output=path.resolve(root,'../review/motion-library');
await fs.mkdir(output,{recursive:true});
const browserExecutable=process.platform==='win32'?'C:/Program Files/Google/Chrome/Application/chrome.exe':undefined;
const chromiumOptions={gl:'angle'};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts')});
const composition=await selectComposition({serveUrl,id:'MotionLibraryDemo',browserExecutable,chromiumOptions});
for(const frame of [90,258,426,594,762,930]) {
 const file=path.join(output,`motion-${frame}.png`);
 await renderStill({composition,serveUrl,output:file,frame,browserExecutable,chromiumOptions});
 console.log(file);
}
console.log(JSON.stringify({durationInFrames:composition.durationInFrames,fps:composition.fps,width:composition.width,height:composition.height}));
