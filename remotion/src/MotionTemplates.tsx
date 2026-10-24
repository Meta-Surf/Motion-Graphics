import React from 'react';
import {ThreeCanvas} from '@remotion/three';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
export type MotionLayout='layers'|'object3d'|'dataflow'|'cutaway'|'scale'|'compare';
export const motionLayouts:MotionLayout[]=['layers','object3d','dataflow','cutaway','scale','compare'];
const clamp={extrapolateLeft:'clamp' as const,extrapolateRight:'clamp' as const};
const ease=(f:number,a:number,b:number)=>{const t=interpolate(f,[a,b],[0,1],clamp);return 1-(1-t)**3};
const frameBox:React.CSSProperties={position:'absolute',top:710,left:72,right:72,height:730};
const Chip:React.FC<{explode:number;color:string;rotation:number}>=({explode,color,rotation})=><group rotation={[.5,rotation,.08]}>
 <mesh position={[0,-.42,0]} receiveShadow><boxGeometry args={[3.4,.16,3.4]}/><meshStandardMaterial color='#153342' metalness={.7} roughness={.32}/></mesh>
 <mesh position={[0,.0+explode,0]} castShadow><boxGeometry args={[2.1,.28,2.1]}/><meshStandardMaterial color='#bdcbd0' metalness={.85} roughness={.22}/></mesh>
 <mesh position={[0,.19+explode*2,0]} castShadow><boxGeometry args={[1.5,.12,1.5]}/><meshStandardMaterial color={color} emissive={color} emissiveIntensity={.12} metalness={.65} roughness={.25}/></mesh>
 {[-1,1].flatMap(x=>[-1,1].map(z=><mesh key={`${x}-${z}`} position={[x*1.15,.12+explode*.65,z*1.15]} castShadow><boxGeometry args={[.55,.3,.55]}/><meshStandardMaterial color='#212d36' metalness={.7} roughness={.3}/></mesh>))}
 {Array.from({length:10},(_,i)=><mesh key={i} position={[-1.4+i*.31,-.55,1.38]}><boxGeometry args={[.12,.12,.15]}/><meshStandardMaterial color='#dcaf62' metalness={.95} roughness={.2}/></mesh>)}
 </group>;
export const MotionTemplate:React.FC<{layout:MotionLayout;color:string;labels:string[];duration:number}>=({layout,color,labels,duration})=>{
 const f=useCurrentFrame(),{fps}=useVideoConfig();
 const phase=f/Math.max(1,duration-1),enter=ease(f,5,45);
 const label=(i:number,fallback:string)=>labels[i]??fallback;
 const panel={background:'linear-gradient(130deg,#102333f2,#07101bf5)',border:`2px solid ${color}90`,boxShadow:'0 28px 80px #0008',borderRadius:20};
 if(layout==='object3d')return <div style={{...frameBox,top:650,height:850}}>
  <ThreeCanvas width={936} height={850} camera={{position:[4.6,4.4,5.8],fov:42}} shadows>
   <ambientLight intensity={.6}/><directionalLight position={[4,6,3]} intensity={3} castShadow/><pointLight position={[-4,2,-2]} color={color} intensity={12}/>
   <Chip color={color} rotation={-.8+phase*1.8} explode={Math.sin(Math.PI*phase)*.45}/>
  </ThreeCanvas>
  <div style={{position:'absolute',bottom:55,left:24,fontSize:22,letterSpacing:3,color}}>{label(0,'OBJETO · MATERIAIS · PROFUNDIDADE')}</div>
 </div>;
 if(layout==='layers')return <div style={{...frameBox,perspective:1300}}>
  <div style={{position:'absolute',left:185,top:120,width:560,height:440,transformStyle:'preserve-3d',transform:`rotateX(53deg) rotateZ(${-28+phase*12}deg)`}}>
  {[0,1,2,3,4].map(i=>{const lift=ease(f,12+i*5,65+i*5)*(1-ease(f,duration-55,duration-8));return <div key={i} style={{position:'absolute',inset:0,...panel,background:`linear-gradient(135deg,${i%2?'#244657':'#0d2438'},#07101b)`,borderColor:i===4?'#ffc576':color,transform:`translateZ(${i*(20+lift*70)}px)`,display:'grid',placeItems:'center',fontSize:34,fontWeight:800,letterSpacing:3}}>{label(i,`CAMADA ${i+1}`)}</div>})}
  </div>
 </div>;
 if(layout==='dataflow')return <div style={frameBox}><svg viewBox='0 0 936 730' width='100%' height='100%'>
  <defs><linearGradient id='flow'><stop stopColor={color}/><stop offset='1' stopColor='#ffc576'/></linearGradient></defs>
  {[0,1,2].map(i=><g key={i}><path d={`M170 365 C330 ${80+i*260} 570 ${80+i*260} 760 365`} fill='none' stroke='url(#flow)' strokeWidth='5' opacity='.7' strokeDasharray='12 14' strokeDashoffset={-f*5}/></g>)}
  {[{x:40,t:label(0,'DADOS')},{x:350,t:label(1,'PROCESSAMENTO')},{x:660,t:label(2,'RESPOSTA')}].map((n,i)=><g key={i} transform={`translate(${n.x} 290)`}><rect width='235' height='150' rx='24' fill='#091a2b' stroke={i===2?'#ffc576':color} strokeWidth='3'/><text x='117' y='85' textAnchor='middle' fill='white' fontFamily='Arial' fontWeight='800' fontSize='21'>{n.t}</text></g>)}
  </svg></div>;
 if(layout==='cutaway')return <div style={frameBox}>
  <div style={{position:'absolute',left:170,top:65,width:580,height:580,...panel,borderRadius:60,display:'grid',placeItems:'center',fontSize:90,color:'#456778',transform:`rotate(${-4+phase*8}deg)`}}>IA</div>
  <div style={{position:'absolute',left:170,top:65,width:580,height:580,overflow:'hidden',clipPath:`inset(0 ${100*(1-ease(f,35,110))}% 0 0 round 60px)`}}><div style={{height:'100%',display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:14,padding:35,background:'#07121e',border:`3px solid ${color}`,borderRadius:60}}>{Array.from({length:16},(_,i)=><div key={i} style={{background:i%3===0?color:'#153f55',borderRadius:13,opacity:.5+.5*Math.sin(f*.05+i)**2}}/>)}</div></div>
  <div style={{position:'absolute',left:30,bottom:10,fontSize:27,color}}>{label(0,'REVELAR PARA EXPLICAR')}</div>
 </div>;
 if(layout==='scale')return <div style={{...frameBox,overflow:'hidden',...panel}}><div style={{position:'absolute',inset:0,transform:`scale(${interpolate(f,[0,duration],[2.6,.95],clamp)})`,display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:25,padding:45}}>{Array.from({length:12},(_,i)=><div key={i} style={{...panel,background:i===5?color+'55':'#102535',display:'grid',placeItems:'center'}}><div style={{width:70,height:70,background:color+'30',border:`2px solid ${color}`,boxShadow:i===5?`0 0 40px ${color}`:undefined}}/></div>)}</div><div style={{position:'absolute',bottom:25,left:25,fontSize:28,fontWeight:800}}>{phase<.45?label(0,'DO COMPONENTE'):label(1,'AO SISTEMA')}</div></div>;
 return <div style={frameBox}>{[0,1].map(i=><div key={i} style={{...panel,position:'absolute',left:i*470,top:70,width:440,height:560,padding:36,transform:`translateY(${(1-ease(f,10+i*15,55+i*15))*100}px)`}}><div style={{fontSize:25,letterSpacing:3,color:i?'#ffc576':color}}>{label(i,i?'DEPOIS':'ANTES')}</div><div style={{display:'flex',alignItems:'end',gap:16,height:320,paddingBottom:15}}>{[0,1,2,3].map(j=><div key={j} style={{flex:1,height:(80+j*42)*(i?1.25:.75)*enter,background:i?'#ffc576':color,borderRadius:10,opacity:.45+j*.16}}/>)}</div><div style={{fontSize:20,color:'#b7c5d1'}}>ILUSTRAÇÃO · SEM ESCALA NUMÉRICA</div></div>)}</div>;
};
