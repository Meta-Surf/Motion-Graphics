import React,{useEffect,useMemo,useState} from 'react';
import {AbsoluteFill,Img,cancelRender,continueRender,delayRender,interpolate,staticFile,useCurrentFrame} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {CameraMotionBlur} from '@remotion/motion-blur';
import * as THREE from 'three';
import {MobileDevice,StudioEnvironment,enter,makeMobileTextures,type MobileTextures} from './MobileDevice3D';
import {mobileSceneAt,validateMobileTimeline} from './mobile-timeline';

export type MobileCue={startFrame:number;endFrame:number;text:string};
export type MobileLayeredProps={assetPrefix:string;durations:number[];captions?:MobileCue[];headlines?:string[];motionBlur?:boolean};
export const MOBILE_DURATIONS=[180,210,240,165,339,180,141,192,153];
const C={cyan:'#8ee6ef',cream:'#f1ce9d',white:'#f2f6fc',muted:'#8fa9bd'};
const clamp={extrapolateLeft:'clamp' as const,extrapolateRight:'clamp' as const};
const url=(prefix:string,name:string)=>staticFile(`${prefix}/${name}`);
const full:React.CSSProperties={position:'absolute',inset:0};
const headlines=['Seu celular vai\nagir por você.','Isso já começou.','Um pedido.\nVárias etapas.','Uma nova fase\nno seu bolso.','No aparelho.\nE na nuvem.','Da tela\nà intenção.','Não chega igual\npara todo mundo.','Você mantém\no controle.','Qual tarefa você\ndelegaria à IA?'];

function loadMobileTextures(prefix:string):Promise<MobileTextures>{
 const loader=new THREE.TextureLoader();
 return Promise.all(['neural-wallpaper.jpg','cafe-photo.jpg','mountain-photo.jpg'].map(n=>loader.loadAsync(url(prefix,n)))).then(([wall,cafe,mountain])=>{for(const t of [wall,cafe,mountain]){t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;}return makeMobileTextures(wall,cafe,mountain);});
}
const Header:React.FC<{f:number;text:string;eyebrow:string;small?:boolean}>=({f,text,eyebrow,small=false})=>{
 const t=enter(f,0,20);
 return <div style={{position:'absolute',left:76,right:76,top:173,opacity:t,transform:`translateY(${(1-t)*26}px)`,color:C.white}}><div style={{fontSize:24,fontWeight:700,letterSpacing:4.5,color:C.cyan,marginBottom:27}}>{eyebrow}</div><div style={{fontSize:small?79:91,fontWeight:750,letterSpacing:-4.8,lineHeight:1.02,whiteSpace:'pre-line',textShadow:'0 4px 26px #0007'}}>{text}</div><div style={{height:3,width:112*t,background:C.cyan,marginTop:30,opacity:.65}}/></div>;
};
const Pill:React.FC<{f:number;at:number;children:React.ReactNode;x:number;y:number;w?:number;color?:string}>=({f,at,children,x,y,w=350,color=C.cyan})=>{
 const t=enter(f,at,at+14);return <div style={{position:'absolute',left:x,top:y,width:w,padding:'22px 25px',border:'1px solid '+color+'70',borderRadius:20,background:'linear-gradient(120deg,#10314be6,#071421eb)',boxShadow:'0 20px 50px #0005',fontSize:31,lineHeight:1.25,fontWeight:650,color,opacity:t,transform:`translateY(${(1-t)*25}px) scale(${.92+.08*t})`}}>{children}</div>;
};
const FlowPath:React.FC<{f:number;from:number;d:string;color?:string}>=({f,from,d,color=C.cyan})=>{
 const t=enter(f,from,from+35),pts=(d.match(/-?\d+(?:\.\d+)?/g)??[]).map(Number),u=Math.max(0,(f-from)%65)/65;
 const cubic=(a:number,b:number,c:number,e:number)=>(1-u)**3*a+3*(1-u)**2*u*b+3*(1-u)*u*u*c+u**3*e;
 return <svg style={{...full,width:1080,height:1920,pointerEvents:'none'}} viewBox='0 0 1080 1920'><path d={d} pathLength={1} fill='none' stroke={color} strokeWidth='3' strokeLinecap='round' strokeDasharray={1} strokeDashoffset={1-t} opacity='.72'/>{pts.length===8&&<circle r='6' cx={cubic(pts[0],pts[2],pts[4],pts[6])} cy={cubic(pts[1],pts[3],pts[5],pts[7])} fill={color} opacity={t}/>}</svg>;
};

const SceneOverlay:React.FC<{shot:number;f:number;duration:number;prefix:string}>=({shot,f,duration,prefix})=>{
 const p=f/duration;
 if(shot===0)return <><div style={{position:'absolute',left:100,top:1490,color:C.cyan,fontSize:42,fontWeight:700,letterSpacing:-1,opacity:enter(f,95,125),transform:`translateY(${(1-enter(f,95,125))*20}px)`}}>O próximo passo já começou.</div><div style={{position:'absolute',left:130,top:1445,width:820,height:120,borderRadius:'50%',background:'radial-gradient(ellipse,#4cbaff24,transparent 70%)',filter:'blur(20px)'}}/></>;
 if(shot===1)return <><Pill f={f} at={16} x={74} y={670} w={300}>Resumir</Pill><Pill f={f} at={55} x={694} y={1090} w={280}>Reescrever</Pill><div style={{position:'absolute',left:85,top:1255,width:355,height:330,overflow:'hidden',borderRadius:24,border:'1px solid #7fd8e577',boxShadow:'0 20px 60px #0008',opacity:enter(f,98,122),transform:`translateY(${(1-enter(f,98,122))*40}px) rotate(-4deg)`}}><Img src={url(prefix,'mountain-photo.jpg')} style={{width:355,height:264,objectFit:'cover'}}/><div style={{height:68,padding:'18px 20px',fontSize:27,fontWeight:650,color:C.cyan,background:'#102b3f'}}>Entender imagens</div><div style={{position:'absolute',left:0,top:264*enter(f,120,180),height:2,width:355,background:'#7feaff',boxShadow:'0 0 18px #6cecff'}}/></div></>;
 if(shot===2)return <><div style={{position:'absolute',left:100,top:1520,color:C.white,fontSize:40,letterSpacing:-1,opacity:enter(f,130,160)}}>Contexto → plano → ação</div><FlowPath f={f} from={70} d='M180 825 C75 1200 870 1190 835 1410'/></>;
 if(shot===3)return <><Pill f={f} at={15} x={610} y={740} w={357}>Gemini<br/><span style={{fontSize:24,color:C.muted}}>Android</span></Pill><Pill f={f} at={48} x={610} y={1040} w={357} color={C.cream}>Apple<br/>Intelligence</Pill><div style={{position:'absolute',left:590,top:1330,width:380,color:'#c0d2df',fontSize:29,lineHeight:1.4,opacity:enter(f,75,100)}}>Em aparelhos<br/>compatíveis.</div></>;
 if(shot===4){const core=enter(f,15,42),cloud=enter(f,94,120);return <><div style={{position:'absolute',left:60,top:590,width:415,height:420,opacity:core,transform:`translateY(${(1-core)*40+Math.sin(f*.025)*8}px) scale(${.82+.18*core})`}}><Img src={url(prefix,'ai-core.png')} style={{width:'100%',height:'100%',objectFit:'contain',filter:'drop-shadow(0 0 24px #38dfff33)'}}/></div><div style={{position:'absolute',left:626,top:560,width:362,height:422,opacity:cloud,transform:`translateY(${(1-cloud)*40+Math.sin(f*.022+1)*7}px)`}}><Img src={url(prefix,'cloud-node.png')} style={{width:'100%',height:'100%',objectFit:'contain'}}/></div><Pill f={f} at={22} x={65} y={1020} w={352}>No aparelho</Pill><Pill f={f} at={105} x={650} y={1020} w={320} color={C.cream}>Na nuvem</Pill><FlowPath f={f} from={115} d='M460 810 C540 710 550 710 647 810' color={C.cream}/><div style={{position:'absolute',left:100,top:1530,color:C.white,fontSize:36,opacity:enter(f,190,220)}}>Chips especializados em IA</div></>}
 if(shot===5)return <div style={{position:'absolute',inset:0,perspective:1400}}>
  {[{at:5,y:560,t:'MENOS TELAS',c:C.cyan,r:-6},{at:55,y:820,t:'MAIS INTENÇÃO',c:C.cream,r:3},{at:105,y:1080,t:'UMA CONVERSA',c:C.white,r:-2}].map(({at,y,t,c,r},i)=>{const a=enter(f,at,at+20);return <div key={t} style={{position:'absolute',left:90,top:y,color:c,fontSize:i===1?91:100,fontWeight:800,letterSpacing:-5,lineHeight:1.05,opacity:a,transform:`translate3d(${(1-a)*100}px,0,${a*40}px) rotate(${r*a}deg) scale(${.8+.2*a})`,textShadow:'0 0 35px '+c+'20'}}>{t}</div>})}
 </div>;
 if(shot===6)return <>{['MODELO','IDIOMA','REGIÃO'].map((v,i)=><Pill key={v} f={f} at={12+i*25} x={610-i*15} y={770+i*205} w={350} color={i===1?C.cream:C.cyan}>{v}</Pill>)}</>;
 if(shot===7){const a=enter(f,6,35);return <><div style={{position:'absolute',left:586,top:730,width:394,height:457,opacity:a,transform:`translateY(${(1-a)*55+Math.sin(f*.025)*6}px) rotate(${-5+Math.sin(p*2)*3}deg)`,filter:'drop-shadow(0 0 38px #3ad3e744)'}}><Img src={url(prefix,'privacy-shield.png')} style={{width:'100%',height:'100%',objectFit:'contain'}}/></div><div style={{position:'absolute',left:565,top:1127,width:425,height:123,borderRadius:'50%',border:'2px solid #59cfff66',boxShadow:'0 0 35px #0cbaff33',opacity:a}}/>{['Permissões claras','Revisar a ação','Confirmar'].map((v,i)=><Pill key={v} f={f} at={35+i*34} x={78} y={800+i*225} w={440} color={i===2?C.cream:C.cyan}><span style={{marginRight:15,color:i===2?C.cream:C.cyan}}>✓</span>{v}</Pill>)}</>}
 return <><div style={{position:'absolute',left:85,top:650,width:530,color:C.cyan,fontSize:35,opacity:enter(f,8,30)}}>Conte nos comentários.</div>{['Mensagens','Agenda','Rotina'].map((v,i)=><Pill key={v} f={f} at={15+i*22} x={85+i*12} y={820+i*190} w={370} color={i===1?C.cream:C.cyan}>{v}</Pill>)}</>;
};

export function validateMobile(props:MobileLayeredProps){
 return validateMobileTimeline(props.durations,props.captions);
}

const MobileLayeredContent:React.FC<MobileLayeredProps>=({assetPrefix,durations=MOBILE_DURATIONS,captions=[],headlines:customHeadlines})=>{
 const frame=useCurrentFrame();
 const [handle]=useState(()=>delayRender('Load approved mobile artwork'));
 const [textures,setTextures]=useState<MobileTextures|null>(null);
 useEffect(()=>{let active=true;loadMobileTextures(assetPrefix).then(t=>{if(active)setTextures(t)}).catch(e=>cancelRender(e));return()=>{active=false}},[assetPrefix]);
 useEffect(()=>{if(textures)continueRender(handle)},[textures,handle]);
 const starts=useMemo(()=>durations.map((_,i)=>durations.slice(0,i).reduce((a,b)=>a+b,0)),[durations]);
 const scene=mobileSceneAt(frame,durations),shot=scene.index,f=scene.frame,duration=scene.duration;
 const alpha=Math.min(enter(f,0,8),1-enter(f,duration-8,duration));
 const bg=shot===1||shot===2||shot===5?'city-empty.jpg':'studio-empty.jpg';
 const cue=captions.find(x=>frame>=x.startFrame&&frame<x.endFrame);
 const eyebrows=['IA NO BOLSO','O QUE JÁ MUDOU','AGENTES ENTRE APLICATIVOS','GOOGLE + APPLE','PROCESSAMENTO HÍBRIDO','O QUE VEM PELA FRENTE','DISPONIBILIDADE','AUTONOMIA COM CONTROLE','E VOCÊ?'];
 return <AbsoluteFill style={{background:'#030814',fontFamily:'Arial, sans-serif',overflow:'hidden'}}>
  <Img src={url(assetPrefix,bg)} style={{...full,width:1080,height:1920,objectFit:'cover',opacity:shot===5?.48:.68,transform:`scale(${1.04+f/duration*.04}) translateX(${Math.sin(f*.006)*8}px)`}}/>
  <div style={{...full,background:'linear-gradient(180deg,#020711dd 0%,#03101c44 46%,#02081211 65%,#020711dd 100%)'}}/>
  <div style={{...full,opacity:alpha}}>
   {textures&&<ThreeCanvas width={1080} height={1920} camera={{position:[0,0,10],fov:38,near:.1,far:70}} gl={{alpha:true,antialias:true,powerPreference:'high-performance'}} dpr={1} style={{...full,width:1080,height:1920}}><StudioEnvironment/><MobileDevice f={f} shot={shot} duration={duration} textures={textures}/></ThreeCanvas>}
   {shot!==5?<Header f={f} eyebrow={eyebrows[shot]} text={customHeadlines?.[shot]??headlines[shot]} small={shot===6||shot===8}/>:<div style={{position:'absolute',left:84,top:210,fontSize:27,color:C.cyan,letterSpacing:4}}>O QUE VEM PELA FRENTE</div>}
   <SceneOverlay f={f} shot={shot} duration={duration} prefix={assetPrefix}/>
  </div>
  <div style={{position:'absolute',left:76,top:95,fontSize:18,fontWeight:600,letterSpacing:3,color:'#a0bed08c'}}>INTELIGÊNCIA ARTIFICIAL</div>
  {cue&&<div style={{position:'absolute',left:100,right:100,bottom:128,textAlign:'center',fontSize:35,lineHeight:1.3,fontWeight:600,color:'#e9f3fb',textShadow:'0 3px 10px #000,0 2px 30px #000',background:'#03101aab',padding:'13px 20px',borderRadius:12}}>{cue.text}</div>}
  <div style={{position:'absolute',left:76,bottom:76,color:'#86a1b8',fontSize:18,letterSpacing:.5}}>Interfaces ilustrativas</div>
 </AbsoluteFill>;
};

export const MobileLayeredShort:React.FC<MobileLayeredProps>=(props)=>{
 const frame=useCurrentFrame(),starts=props.durations.map((_,i)=>props.durations.slice(0,i).reduce((a,b)=>a+b,0));
 const fast=frame<80||starts.some(s=>frame>=s&&frame<s+55)||(frame>=starts[5]&&frame<starts[6]);
 return props.motionBlur?<AbsoluteFill><CameraMotionBlur shutterAngle={120} samples={fast?3:1}><MobileLayeredContent {...props}/></CameraMotionBlur></AbsoluteFill>:<MobileLayeredContent {...props}/>;
};
