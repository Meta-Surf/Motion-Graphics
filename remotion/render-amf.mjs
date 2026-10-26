import {bundle} from '@remotion/bundler';
import {selectComposition,renderFrames} from '@remotion/renderer';
import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const args=process.argv.slice(2);
const option=(name)=>{const i=args.indexOf(name);return i>=0?args[i+1]:undefined};
const id=option('--composition')??'AiShort';
const voice=option('--voice');
const preview=args.includes('--silent-preview');
if(!voice&&!preview)throw new Error('Pass --voice narration.wav for a final export, or --silent-preview for a visual review.');
const output=path.resolve(option('--output')??`renders/${id}${preview?'-silent-preview':''}.mp4`);
await fs.mkdir(path.dirname(output),{recursive:true});
try{await fs.access(output);throw new Error('Output already exists; choose a new versioned filename')}catch(e){if(e.code!=='ENOENT')throw e}
const raw=option('--props');
const inputProps=raw?JSON.parse(await fs.readFile(raw,'utf8')):{};
const browserExecutable=option('--browser')??(process.platform==='win32'?'C:/Program Files/Google/Chrome/Application/chrome.exe':undefined);
const chromiumOptions={gl:'angle'};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts')});
const composition=await selectComposition({serveUrl,id,inputProps,browserExecutable,chromiumOptions});
await fs.mkdir(path.resolve('renders'),{recursive:true});
const frameDir=await fs.mkdtemp(path.resolve('renders/frames-'));
const started=Date.now();
await renderFrames({serveUrl,composition,inputProps,outputDir:frameDir,imageFormat:'jpeg',browserExecutable,chromiumOptions,concurrency:2});
const frames=(await fs.readdir(frameDir)).filter(x=>/^element-\d+\.jpeg$/.test(x)).sort();
if(frames.length!==composition.durationInFrames)throw new Error(`Incomplete frame sequence; retained ${frameDir}`);
const digits=frames[0].match(/element-(\d+)/)[1].length;
const ffmpeg=option('--ffmpeg')??'ffmpeg';const ffprobe=option('--ffprobe')??'ffprobe';
function run(exe,params){const r=spawnSync(exe,params,{stdio:'inherit'});if(r.error)throw r.error;if(r.status!==0)throw new Error(`${exe} failed (${r.status}); frames retained at ${frameDir}`)}
const silent=preview?output:output.replace(/\.mp4$/i,'.silent.mp4');
if(silent===output&&!preview)throw new Error('Output filename must end in .mp4');
run(ffmpeg,['-hide_banner','-n','-framerate',String(composition.fps),'-i',path.join(frameDir,`element-%0${digits}d.jpeg`),'-c:v','h264_amf','-quality','quality','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-pix_fmt','yuv420p','-b:v','12M','-movflags','+faststart',silent]);
if(!preview)run(option('--python')??'python',[path.resolve('../scripts/finalize_short.py'),silent,'--voice',path.resolve(voice),'--output',output,'--ffmpeg',ffmpeg,'--ffprobe',ffprobe,'--video-type',inputProps.video_type??'short_9_16']);
await fs.writeFile(output.replace(/\.mp4$/i,'.render.json'),JSON.stringify({composition:id,durationInFrames:composition.durationInFrames,fps:composition.fps,seconds:(Date.now()-started)/1000,encoder:'h264_amf',gl:'angle',silentPreview:preview},null,2));
// Retain source frames until final review; cleanup is an explicit user operation.
console.log(`Output: ${output}\nFrames: ${frameDir}`);
