import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {phase,poseAt,type Pose} from './reference-patterns';

export type ReferenceMotionStudyProps={assetPrefix?:string;useReferenceText?:boolean;brand?:string};
const clamp={extrapolateLeft:'clamp' as const,extrapolateRight:'clamp' as const};
const track=(f:number,frames:number[],values:number[])=>interpolate(f,frames,values,clamp);
const blue='#1246ff';
const asset=(prefix:string,name:string)=>staticFile(`${prefix}/${name}`);
const preserve:React.CSSProperties={transformStyle:'preserve-3d'};
const full:React.CSSProperties={position:'absolute',inset:0};

const Cap:React.FC<{size?:number;color?:string}>=({size=100,color='currentColor'})=><svg viewBox='0 0 100 80' width={size} height={size*.8} fill='none'><path d='M6 25 50 7 94 25 50 44Z' fill={color}/><path d='M22 39v20c20 17 38 17 57 0V39L50 51Z' fill={color}/><path d='M90 30v30' stroke={color} strokeWidth='5'/><circle cx='90' cy='65' r='5' fill={color}/></svg>;
const Avatar:React.FC<{prefix?:string;size:number}>=({prefix,size})=>prefix?<Img src={asset(prefix,'avatar.png')} style={{width:size,height:size,borderRadius:'50%'}}/>:<div style={{width:size,height:size,borderRadius:'50%',background:blue,display:'grid',placeItems:'center',color:'white',fontSize:size*.19,fontWeight:900}}>MOTION</div>;

const DemoScreen:React.FC=()=> <div style={{...full,background:'#101821',padding:16,color:'#e5edf6',fontSize:9,borderRadius:29}}>
 <div style={{display:'flex',justifyContent:'space-between',paddingBottom:18}}>6:45 <span>▰ ▰ ▰</span></div><div style={{fontWeight:800,fontSize:13}}>motion.lab <span style={{float:'right'}}>≡</span></div>
 <div style={{display:'flex',alignItems:'center',gap:12,marginTop:18}}><Avatar size={51}/><div>Motion Lab<br/><b>53 &nbsp;&nbsp; 328 &nbsp;&nbsp; 3</b><br/>PROJETOS &nbsp; IDEIAS</div></div>
 <p style={{lineHeight:1.6}}>Um laboratório de ideias em movimento.<br/>Imagem · inteligência artificial · criação.</p><div style={{background:'#283d4d',padding:8,borderRadius:4}}>Painel de criação</div><div style={{display:'flex',gap:5,marginTop:6}}>{['Editar','Compartilhar'].map(t=><div key={t} style={{background:'#263847',flex:1,padding:5,textAlign:'center'}}>{t}</div>)}</div>
 <div style={{display:'flex',justifyContent:'space-between',marginTop:12}}>{['IDEIA','DADOS','IMAGEM','MOTION'].map(t=><div key={t} style={{textAlign:'center'}}><div style={{width:34,height:34,borderRadius:'50%',border:'1px solid #738a9b',background:'radial-gradient(circle at 30% 30%,#6782a9,#111a24)',marginBottom:5}}/>{t}</div>)}</div>
 <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:2,marginTop:24}}>{Array.from({length:9},(_,i)=><div key={i} style={{height:82,background:`linear-gradient(${i*25}deg,${['#012bff','#182e47','#605582'][i%3]},#08101e)`,display:'grid',placeItems:'center',fontWeight:900,fontSize:19}}>{['IA','3D','∞'][i%3]}</div>)}</div><div style={{position:'absolute',bottom:16,left:25,right:25,padding:8,borderRadius:20,background:'#28343ed9',fontSize:17,display:'flex',justifyContent:'space-between'}}>⌂ <span>▣</span><span>⊕</span><span>⌕</span><span>●</span></div>
</div>;

const ScreenCrop:React.FC<{prefix?:string;y:number;h:number;style?:React.CSSProperties}>=({prefix,y,h,style})=><div style={{position:'absolute',left:0,top:y,width:250,height:h,overflow:'hidden',...style}}>{prefix?<Img src={asset(prefix,'screen-rectified.png')} style={{position:'absolute',top:-y,left:0,width:250,height:550}}/>:<div style={{position:'absolute',top:-y,left:0,width:250,height:550}}><DemoScreen/></div>}</div>;

const Phone:React.FC<{frame:number;prefix?:string;inspection?:boolean;poses?:Pose[]}>=({frame,prefix,inspection=false,poses})=>{
 const p=poseAt(frame,poses),lift=phase(frame,36,49),detach=phase(frame,44,56);
 const depth=inspection?1:lift;
 const transform=inspection?'translate3d(360px,670px,0) rotateX(52deg) rotateY(-24deg) rotateZ(-24deg) scale(1.25)':`translate3d(${p.x}px,${p.y}px,0) rotateZ(${p.rz}deg) rotateY(${p.ry}deg) rotateX(${p.rx}deg) scale(${p.scale})`;
 return <div style={{position:'absolute',inset:0,perspective:1100,perspectiveOrigin:'50% 50%',...preserve}}>
  <div style={{position:'absolute',width:0,height:0,...preserve,transform}}>
   <div style={{position:'absolute',left:-132,top:-282,width:264,height:564,...preserve}}>
    {Array.from({length:10},(_,i)=><div key={i} style={{...full,borderRadius:38,background:i===0?'#8a9295':'linear-gradient(100deg,#59656a,#e2e9e6 4%,#333d46 12%,#839197 87%,#e0e5e6 97%,#565f66)',transform:`translateZ(${-i*1.2}px)`,border:'1px solid #b8c4c9',boxShadow:i===9?'0 8px 35px #b8d7ff22':undefined}}/>)}
    <div style={{...full,borderRadius:38,background:'linear-gradient(115deg,#a1aaa9,#f3f3e8 48%,#b4baba)',backfaceVisibility:'hidden',transform:'translateZ(-13px) rotateY(180deg)',border:'2px solid #ecf0ed'}}>
     <div style={{position:'absolute',left:12,top:12,width:98,height:104,borderRadius:25,background:'linear-gradient(130deg,#a3adaa,#e3e5df)',boxShadow:'2px 3px 5px #0004'}}>{[[25,25],[70,25],[25,72]].map(([x,y],i)=><div key={i} style={{position:'absolute',left:x-17,top:y-17,width:34,height:34,borderRadius:'50%',background:'radial-gradient(circle at 45% 40%,#184273,#060c13 35%,#283038 51%,#8c999a 55%,#424d51 65%,#b1bab8 73%)'}}/>)}</div><div style={{position:'absolute',top:240,left:105,fontSize:47,fontWeight:800,color:'#919b99'}}>M</div>
    </div>
    <div style={{position:'absolute',left:7,top:7,width:250,height:550,borderRadius:31,background:'#0d161e',backfaceVisibility:'hidden',transform:'translateZ(1px)',...preserve}}>
     <div style={{...full,borderRadius:31,overflow:'hidden'}}>{prefix?<Img src={asset(prefix,'screen-rectified.png')} style={{width:250,height:550}}/>:<DemoScreen/>}
      {depth>0&&<><div style={{position:'absolute',left:9,top:65,width:62,height:63,borderRadius:'50%',background:'#101a22'}}/><div style={{position:'absolute',left:12,top:192,width:228,height:68,background:'#101a22',opacity:depth}}/><div style={{position:'absolute',left:0,top:340,width:250,height:125,background:'#101a22',opacity:depth}}/></>}
     </div>
     <ScreenCrop prefix={prefix} y={193} h={36} style={{transform:`translate3d(${depth*10}px,${-depth*3}px,${depth*35}px)`,boxShadow:depth>.1?'0 8px 12px #0006':undefined}}/>
     {[0,1].map(i=><div key={i} style={{position:'absolute',left:13+i*120,top:233,width:115,height:22,...preserve,transform:`translate3d(${(i?9:-9)*depth}px,0,${(50+i*9)*depth}px)`,background:'#233644',borderRadius:3,display:'grid',placeItems:'center',color:'#e2e8ec',fontSize:8}}>{prefix?(i?'Share profile':'Edit profile'):(i?'Compartilhar':'Editar perfil')}</div>)}
     {[0,1,2].map(i=><div key={i} style={{position:'absolute',top:344,left:9+i*79,width:78,height:118,...preserve,transform:`translate3d(${(i-1)*detach*28}px,${-detach*(i===1?22:10)}px,${depth*(76+i*14)}px) rotateX(${-depth*25}deg) rotateY(${(i-1)*detach*9}deg)`,boxShadow:depth>.1?'0 10px 15px #0008':undefined,background:'#0d1520'}}>{prefix?<Img src={asset(prefix,`card-${i}.png`)} style={{width:'100%',height:'100%',objectFit:'cover'}}/>:<div style={{...full,background:`linear-gradient(${i*50}deg,#123bff,#091321)`,display:'grid',placeItems:'center',color:'white',fontSize:20,fontWeight:800}}>{['IA','3D','∞'][i]}</div>}</div>)}
     {depth>0&&<div style={{position:'absolute',left:12,top:70,transform:`translate3d(${-depth*6}px,${-depth*5}px,${depth*48}px)`,borderRadius:'50%',boxShadow:depth>.1?'0 0 30px #1648ff66':undefined}}><Avatar size={54} prefix={prefix}/></div>}
     <div style={{...full,borderRadius:31,pointerEvents:'none',border:'1px solid #eef7ff55',background:'linear-gradient(110deg,transparent 32%,#e5f5ff09 47%,transparent 55%)',transform:'translateZ(2px)'}}/>
    </div>
   </div>
  </div>
 </div>;
};

const EmissiveBadge:React.FC<{f:number;reference:boolean}>=({f,reference})=>{
 const t=phase(f,99,109),x=track(f,[99,111,129],[370,432,405]),y=track(f,[99,111,129],[630,645,640]);
 return <div style={{position:'absolute',left:x,top:y,opacity:t,transform:`translate(-50%,-50%) scale(${.1+.9*t})`}}>
  <div style={{position:'absolute',left:-245,top:-130,width:490,height:390,background:'radial-gradient(ellipse,#164dffcc,transparent 66%)',filter:'blur(20px)'}}/>
  {[0,1,2,3].map(i=><div key={i} style={{position:'absolute',left:-190,top:40-i*18,width:380,height:145,borderRadius:'50%',border:'2px solid #48c5ff',boxShadow:'0 0 12px #13a6ff,inset 0 0 17px #1689ff',transform:`rotate(${-9+Math.sin(f*.05)*2}deg)`}}/>)}
  <div style={{position:'absolute',left:-174,top:50,width:348,height:105,borderRadius:'50%',background:'#1646ffb3',color:'white',display:'grid',placeItems:'center',fontSize:50,fontWeight:900,transform:'rotate(-9deg)',textShadow:'0 0 15px #8fdbff'}}>{reference?'Slate':'MOTION'}</div>
  <div style={{position:'relative',left:-100,top:-100,width:200,height:200,borderRadius:38,background:'linear-gradient(135deg,#edf9ff,#b9d5dc)',color:blue,display:'grid',placeItems:'center',transform:'rotate(-8deg)',boxShadow:'0 0 45px #2aaaffaa'}}><Cap size={163}/></div>
 </div>;
};

const DeviceScene:React.FC<{f:number;prefix?:string;reference:boolean}>=({f,prefix,reference})=><AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 49%,#001f85 0%,#030d2b 36%,#01030a 72%,#000 100%)'}}>
 <Phone frame={f} prefix={prefix}/><EmissiveBadge f={f} reference={reference}/>
</AbsoluteFill>;

const CubeScene:React.FC<{f:number;reference:boolean}>=({f,reference})=>{
 const t=f-130,enter=phase(t,0,12),s=.22+.73*enter;
 return <AbsoluteFill style={{background:'radial-gradient(ellipse at 52% 52%,#003fcb,#001955 35%,#020b1e 73%,#01040b)'}}>
  <div style={{...full,overflow:'hidden',opacity:.1,color:'transparent',WebkitTextStroke:'1px #5579bd',fontSize:250,fontWeight:900,lineHeight:.95,transform:`rotate(-12deg) translate(${-180-t*.7}px,${-160+t*.6}px)`}}>AHHH<br/>AHHH<br/>AHHH<br/>AHHH<br/>AHHH<br/>AHHH</div>
  <div style={{position:'absolute',left:110,top:400,width:500,height:500,background:'radial-gradient(circle,#0359ffb0,transparent 64%)',filter:'blur(25px)',transform:`scale(${.6+enter*.4})`}}/>
  <div style={{position:'absolute',left:360,top:640,perspective:850,...preserve,transform:`scale(${s}) rotate(${t<19?-24:Math.sin(t*.09)*18}deg)`}}>
   <div style={{position:'absolute',left:-84,top:-84,width:168,height:168,...preserve,transform:`rotateX(${17+Math.sin(t*.07)*16}deg) rotateY(${t*7-65}deg)`}}>
    {['front','back','left','right','top','bottom'].map((face,i)=><div key={face} style={{...full,display:'grid',placeItems:'center',border:'1px solid #406eff',borderRadius:face==='front'||face==='back'?14:4,background:`linear-gradient(${130+i*12}deg,${i%2?'#00145e':'#1556ff'},${i===0?'#0923bb':'#001047'})`,color:i===0?'#02091c':'#8ba6ff',fontSize:33,fontWeight:900,boxShadow:'0 0 28px #1a64ff66,inset 0 0 19px #578dff44',backfaceVisibility:'hidden',transform:[`translateZ(84px)`,`rotateY(180deg) translateZ(84px)`,`rotateY(-90deg) translateZ(84px)`,`rotateY(90deg) translateZ(84px)`,`rotateX(90deg) translateZ(84px)`,`rotateX(-90deg) translateZ(84px)`][i]}}>{i<2?(reference?'Slate':'MOTION'):<Cap size={83}/>}</div>)}
   </div>
   <div style={{position:'absolute',left:-160,top:-20,width:320,textAlign:'center',fontSize:50,color:'#78d8ff',textShadow:'0 0 8px #2676ff',transform:`translateZ(${-40+80*Math.sin(t*.1)}px) rotateY(${-t*7+65}deg)`}}>{reference?'Ahhhhhh':'IDEIAS'}</div>
  </div>
 </AbsoluteFill>;
};

const Word:React.FC<{f:number;at:number;x:number;y:number;children:React.ReactNode;color?:string;size?:number;card?:boolean}>=({f,at,x,y,children,color='#293a40',size=82,card=false})=>{
 const t=phase(f,at,at+5); if(f<at)return null;
 return <div style={{position:'absolute',left:x,top:y,whiteSpace:'nowrap',fontSize:size,lineHeight:1,fontWeight:750,letterSpacing:-5,color,background:card?'#1c262a':undefined,padding:card?'0px 12px 8px':undefined,transformOrigin:'10% 50%',transform:`translateY(${(1-t)*40}px) rotate(${(1-t)*-12}deg) scale(${.78+.22*t})`,filter:`blur(${(1-t)*3}px)`,opacity:t}}>{children}</div>;
};
const LightType:React.FC<{f:number;reference:boolean}>=({f,reference})=>{
 const t=f-194,iris=phase(t,47,50)*(1-phase(t,60,63));
 const words=reference?['yeah','she','suck','them','Dragon','Balls','Bitch','I feel like','cell']:['ideia','vira','imagem','e','ganha','vida','Com IA','criamos','mais'];
 return <AbsoluteFill style={{background:iris>.1?'#000':'radial-gradient(ellipse at 50% 52%,#c9d6d8,#9babaf 40%,#34454c 78%,#151f23)',color:'#293a40',fontFamily:'Arial, sans-serif',overflow:'hidden',textShadow:'-1.5px 0 #1389c955,1.5px 0 #e2a24444'}}>
 {t<50?<div style={{position:'absolute',left:360,top:640,transform:`translate(${track(t,[0,12,24,36,48],[35,15,-20,-260,-480])}px,${track(t,[0,20,38,48],[20,0,-70,-125])}px) rotate(${track(t,[0,15,40,48],[-30,-9,-4,1])}deg) scale(${track(t,[0,12,24,36,48],[.35,1,1.25,1.6,1.8])})`}}>
  <Word f={t} at={0} x={-140} y={-110}>{words[0]}</Word><Word f={t} at={13} x={-80} y={-25} card color='#dbe8ec'>{words[1]}</Word><Word f={t} at={23} x={-90} y={65} color='#673083' size={99}>{words[2]}</Word><Word f={t} at={32} x={150} y={70} size={99}>{words[3]}</Word><Word f={t} at={39} x={150} y={165}>{words[4]}</Word><Word f={t} at={47} x={420} y={165}>{words[5]}</Word>
 </div>:t<63?<div style={{position:'absolute',left:'50%',top:'50%',width:1000,height:300,borderRadius:'50%',background:'#d1dee1',display:'grid',placeItems:'center',transform:`translate(-50%,-50%) scale(${track(t,[50,53,62],[1.15,1,.99])})`,boxShadow:'0 0 8px #57a7ff66',fontSize:130,fontWeight:750,letterSpacing:-6,whiteSpace:'nowrap'}}>{words[4]} {words[5]}</div>:<div style={{position:'absolute',left:360,top:600,transform:`rotate(${track(t,[63,72,83],[-5,0,9])}deg) scale(${track(t,[63,75,83],[1.8,1.9,2.1])})`}}>
  <Word f={t} at={63} x={-150} y={-70}>{words[6]}</Word><Word f={t} at={70} x={-80} y={25} size={74}>{words[7]}</Word><Word f={t} at={79} x={-70} y={250} color='#c92735' size={100}>{words[8]}</Word>
 </div>}
 </AbsoluteFill>;
};

const DarkType:React.FC<{f:number;reference:boolean}>=({f,reference})=>{
 const t=f-278;
 const yellow='#b9c536',cyan='#199fd4',red='#df152d';
 const glow=(color:string)=>`0 0 11px ${color}b0,0 0 32px ${color}50`;
 const words=reference?['cell',"And I’m",'schizophrenic','might do','DAMAGE','life is','cell']:['mais','Com IA','damos forma','às nossas','IDEIAS','criar é','mover'];
 return <AbsoluteFill style={{background:'#000',fontFamily:'Arial, sans-serif',overflow:'hidden'}}>
 {t<18?<div style={{position:'absolute',left:360,top:640,color:red,fontSize:110,fontWeight:800,letterSpacing:-7,textShadow:glow(red),transform:`translate(-50%,-50%) rotate(${track(t,[0,7,17],[9,0,0])}deg) scale(${track(t,[0,5,17],[1.35,1,.95])})`,filter:`blur(${track(t,[0,5,17],[3,0,0])}px)`}}>{words[0]}</div>:t<77?<div style={{position:'absolute',left:360,top:640,transform:`translate(${track(t,[18,39,51,64,76],[0,0,-70,-270,-390])}px,${track(t,[18,39,51,64,76],[0,0,-40,-90,-90])}px) rotate(${track(t,[18,39,64,76],[0,0,7,0])}deg)`}}>
  <div style={{textShadow:glow(yellow)}}><Word f={t} at={18} x={-190} y={-80} color={yellow} size={90}>{words[1]}</Word></div>
  <div style={{textShadow:glow(cyan)}}><Word f={t} at={25} x={-190} y={9} color={cyan} size={reference?62:76}>{words[2]}</Word></div>
  <div style={{textShadow:glow('#9bb6c0')}}><Word f={t} at={48} x={60} y={78} color='#bbcdd3' size={72}>{words[3]}</Word></div>
  <div style={{textShadow:glow(red)}}><Word f={t} at={58} x={260} y={142} color={red} size={101}>{words[4]}</Word></div>
 </div>:<div style={{position:'absolute',left:360,top:640,transform:`translate(-50%,-50%) scale(${track(t,[77,88,114],[.95,1,1])})`,whiteSpace:'nowrap',color:red,fontWeight:800,fontSize:80,letterSpacing:-5,textShadow:glow(red)}}>{words[5]} {t>=90?words[6]:''}</div>}
 {t>=96&&Array.from({length:5},(_,i)=><div key={i} style={{position:'absolute',left:74+i*139+Math.sin(i*1.8+t*.2)*7,top:280,width:18,height:760,borderRadius:'50%',background:'linear-gradient(90deg,#090a0c,#263038 32%,#7b919e66 48%,#171b20 65%,#050608)',filter:`blur(${1+Math.abs(i-2)*.35}px)`,transform:`scaleX(${phase(t,96,103)}) rotate(${(i-2)*1.4}deg)`}}/>)}
 </AbsoluteFill>;
};

const Resolve:React.FC<{f:number;prefix?:string;brand:string}>=({f,prefix,brand})=>{
 const t=f-393;
 return <AbsoluteFill style={{background:'#000',color:'white',display:'flex',alignItems:'center',justifyContent:'center'}}><div style={{width:600,textAlign:'center',filter:`blur(${track(t,[0,5,11,73],[13,3,0,0])}px)`,opacity:phase(t,0,8),transform:`scale(${track(t,[0,12,73],[.8,1,1.015])})`,textShadow:'0 0 18px #eaf6ff99,0 0 45px #cce7ff66'}}>
 {prefix?<Img src={asset(prefix,'reference-mark.png')} style={{width:600,height:255,objectFit:'contain',transform:'translateY(50px)'}}/>:<><div style={{fontFamily:'Georgia,serif',fontSize:110,fontWeight:800,letterSpacing:-4}}>{brand}</div><div style={{fontFamily:'Arial',letterSpacing:22,fontSize:20,marginLeft:20}}>MOTION LAB</div></>}
 </div></AbsoluteFill>;
};

export const ReferenceMotionStudy:React.FC<ReferenceMotionStudyProps>=({assetPrefix,useReferenceText=false,brand='Motion'})=>{
 const f=useCurrentFrame();
 return <AbsoluteFill style={{background:'#000',overflow:'hidden'}}>{f<130?<DeviceScene f={f} prefix={assetPrefix} reference={useReferenceText}/>:f<194?<CubeScene f={f} reference={useReferenceText}/>:f<278?<LightType f={f} reference={useReferenceText}/>:f<393?<DarkType f={f} reference={useReferenceText}/>:<Resolve f={f} prefix={assetPrefix} brand={brand}/>}</AbsoluteFill>;
};

export const LayerBreakdown:React.FC<{assetPrefix?:string}>=({assetPrefix})=>{
 const f=useCurrentFrame(),settle=phase(f,0,45);
 const layers=[['01','Corpo e borda','estrutura independente'],['02','Tela base','textura retificada do frame 33'],['03','Painel e botões','recortes com elevação própria'],['04','Três cartões','profundidade e atraso por item'],['05','Avatar e destaque','âncora visual da aproximação'],['06','Rings / brilho','composição aditiva estimada'],['07','Câmera comum','rota, enquadramento e escala']];
 return <AbsoluteFill style={{background:'radial-gradient(ellipse at 25% 50%,#0c2862,#040b19 65%)',color:'white',fontFamily:'Arial'}}>
 <div style={{position:'absolute',left:40,top:30,color:'#67c9ff',letterSpacing:5,fontSize:18}}>ESTUDO 001 · CAMADAS RECONSTRUÍDAS</div>
 <div style={{position:'absolute',left:20,top:80,width:650,height:1000,transform:'scale(.85)',transformOrigin:'top left'}}><Phone frame={45} prefix={assetPrefix} inspection/></div>
 <div style={{position:'absolute',left:660,top:120,width:680}}><div style={{fontSize:45,fontWeight:750,letterSpacing:-2,marginBottom:30}}>Uma câmera.<br/>Elementos independentes.</div>{layers.map(([id,title,sub],i)=><div key={id} style={{display:'flex',gap:22,marginBottom:24,opacity:phase(f,i*4,i*4+15)*settle,transform:`translateX(${(1-phase(f,i*4,i*4+15))*30}px)`}}><div style={{color:'#5dc8ff',fontSize:26,fontFamily:'monospace'}}>{id}</div><div><div style={{fontSize:27,fontWeight:700}}>{title}</div><div style={{fontSize:18,color:'#92a8c3',marginTop:5}}>{sub}</div></div></div>)}<div style={{fontSize:17,lineHeight:1.5,color:'#8298b6',marginTop:35}}>Modelo 2,5D editável. As camadas e curvas originais<br/>não estão disponíveis no MP4; esta é uma reconstrução.</div></div>
 </AbsoluteFill>;
};

// Building blocks for new scenes; the complete study remains a reference-specific demo.
export {Phone as LayeredDeviceRig,Word as KineticWord};
