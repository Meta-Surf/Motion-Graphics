import React from 'react';
import {AbsoluteFill,Img,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {useAudioData,visualizeAudio} from '@remotion/media-utils';
import {editorialPatterns,editorialPhase as phase,metricValue,typedText,normalizedLevels,type EditorialKind,type MetricEvidence} from './editorial-motion';

const A='#ed4e83',INK='#0d1017',MUTED='#707781';
const card:React.CSSProperties={background:'#fff',border:'1px solid #e3e3e6',borderRadius:20,boxShadow:'0 17px 28px #15202c1c'};
const area:React.CSSProperties={position:'absolute',left:80,right:80,top:405,height:440};

export const SoftPaperStage:React.FC<{time:number;accent?:string;children:React.ReactNode}>=({time,children,accent=A})=><AbsoluteFill style={{background:'linear-gradient(135deg,#f2f3f6,#fff)',color:INK,overflow:'hidden',fontFamily:'Arial, sans-serif'}}>
 <div style={{position:'absolute',inset:0,backgroundImage:'linear-gradient(#b9bcc32b 1px,transparent 1px),linear-gradient(90deg,#b9bcc32b 1px,transparent 1px)',backgroundSize:'64px 64px'}}/>
 <div style={{position:'absolute',left:-145+Math.sin(time*.3)*20,top:-100,width:225,height:1600,background:'linear-gradient(90deg,transparent,#222a3630,transparent)',filter:'blur(28px)',transform:'rotate(-7deg)'}}/>
 <div style={{position:'absolute',left:-180,top:815+Math.sin(time*.23)*24,width:1150,height:130,background:'linear-gradient(180deg,transparent,#26313b22,transparent)',filter:'blur(26px)',transform:'rotate(-10deg)'}}/>
 <div style={{position:'absolute',left:42,top:66,fontSize:15,letterSpacing:3,color:'#7e858e'}}>BIBLIOTECA DE MOTION</div>
 <div style={{position:'absolute',inset:0}}>{children}</div>
 <div style={{position:'absolute',left:46,right:46,bottom:47,fontSize:15,display:'flex',justifyContent:'space-between',color:MUTED}}><span>Estudo 002 · modelos adaptados</span><span style={{color:accent}}>Prévia sem áudio</span></div>
</AbsoluteFill>;

export const EditorialHeader:React.FC<{time:number;kicker?:string;before:string;accent:string;after?:string}>=({time,kicker,before,accent,after})=>{
 const e=phase(time,0,.30);return <div style={{position:'absolute',left:45,right:45,top:175,textAlign:'center',opacity:e,transform:`translateY(${(1-e)*22}px)`}}>{kicker&&<div style={{fontFamily:'Georgia,serif',fontStyle:'italic',fontSize:27,color:'#656b73',marginBottom:14}}>{kicker}</div>}<div style={{fontWeight:800,fontSize:56,letterSpacing:-2.5,lineHeight:1.04}}>{before}<br/><span style={{color:A}}>{accent}</span>{after&&' '+after}</div></div>;
};

const Sticker:React.FC<{time:number;at:number;children:React.ReactNode}>=({time,at,children})=>{
 const t=phase(time,at,at+.22);return <div style={{position:'absolute',left:'50%',top:900,whiteSpace:'nowrap',background:A,color:'white',border:'3px solid white',fontSize:26,fontWeight:800,padding:'9px 17px',transform:`translateX(-50%) rotate(-4deg) scale(${.65+.35*t})`,opacity:t,boxShadow:'0 5px 0 #b82e5c22'}}>{children}</div>;
};
const Person:React.FC<{x:number;y:number;scale?:number;color?:string;opacity?:number}>=({x,y,scale=1,color='#8a8e96',opacity=1})=><g transform={`translate(${x} ${y}) scale(${scale})`} fill='none' stroke={color} strokeWidth='3' opacity={opacity}><circle cx='0' cy='-24' r='16'/><path d='M-30 27v-8C-30-15 30-15 30 19v8Z'/></g>;

export const LinkedPanelComparison:React.FC<{time:number}>=({time})=><div style={{...area,perspective:1200}}>
 {[0,1].map(i=><div key={i} style={{...card,position:'absolute',left:i?330:35,top:15,width:200,height:365,background:i?'#ffe7ef':'#111820',border:i?'2px dashed '+A:'2px solid #29313b',padding:24,transform:`rotateY(${i?-7:7}deg) rotate(${i?2:-2}deg) translateY(${(1-phase(time,.1+i*.1,.5+i*.1))*30}px)`,opacity:phase(time,.1+i*.1,.5+i*.1)}}><div style={{width:48,height:48,borderRadius:13,background:i?A:'white',margin:'0 auto 30px',display:'grid',placeItems:'center',color:i?'white':INK,fontSize:24,fontWeight:800}}>M</div>{['Texto','Camadas','Áudio','Revisão'].map((s,j)=><div key={s} style={{padding:'12px 3px',marginBottom:12,borderRadius:9,fontSize:18,textAlign:'center',background:i?(phase(time,.55+j*.22,.7+j*.22)>.5?A:'#fff8'):'#25303a',color:i?'#a42553':'white'}}>{s}</div>)}</div>)}
 <svg viewBox='0 0 560 440' style={{position:'absolute',inset:0,width:560,height:440}}>{[0,1,2].map(i=><path key={i} d={`M230 ${145+i*56} C280 ${118+i*56},280 ${170+i*56},330 ${145+i*56}`} fill='none' stroke={A} strokeWidth='3' pathLength='1' strokeDasharray='.08 .06' strokeDashoffset={-time*.15} opacity={phase(time,.55+i*.22,.8+i*.22)}/>)}</svg>
 </div>;

export const SemanticFocus:React.FC<{time:number}>=({time})=>{
 const dim=1-phase(time,1.1,1.55),focus=phase(time,1.1,1.8),cross=phase(time,.50,1.1);
 return <svg width='600' height='450' viewBox='0 0 600 450' style={{position:'absolute',left:60,top:410}}>
  <g opacity={dim}>{Array.from({length:10},(_,i)=><Person key={i} x={85+i%5*105} y={140+Math.floor(i/5)*120} scale={.85}/>)}</g>
  <path d='M55 80 545 340 M545 80 55 340' stroke={A} strokeWidth='5' fill='none' pathLength={1} strokeDasharray={1} strokeDashoffset={1-cross} opacity={1-focus}/>
  <Person x={300} y={220} scale={.8+1.5*focus} color={A} opacity={focus}/>
 </svg>;
};

export const EvidenceMetric:React.FC<{time:number;evidence:MetricEvidence}>=({time,evidence})=>{
 const value=metricValue(phase(time,.45,2.25),evidence);return <div style={{...area,top:400,textAlign:'center'}}>
  <div style={{fontSize:100,fontWeight:850,letterSpacing:-4}}>{new Intl.NumberFormat('pt-BR').format(value)}</div><div style={{fontFamily:'Georgia',fontStyle:'italic',fontSize:23,color:MUTED,marginTop:3}}>{evidence.label}</div>
  <div style={{...card,position:'relative',height:210,marginTop:35,padding:22,textAlign:'left'}}><div style={{fontSize:15,color:MUTED}}>progressão visual</div><svg width='470' height='140' viewBox='0 0 470 140'><path d='M10 120H455 M10 20V120' stroke='#e3e3e8' fill='none'/><path d='M15 117C100 115 135 104 200 92S310 62 355 43S410 25 450 8' stroke={A} fill='none' strokeWidth='4' pathLength='1' strokeDasharray={1} strokeDashoffset={1-phase(time,.45,2.25)}/></svg></div>
  <div style={{fontSize:15,color:A,marginTop:18,fontWeight:700,letterSpacing:1}}>{evidence.kind==='illustrative'?'DADOS ILUSTRATIVOS':`FONTE: ${evidence.source} · ${evidence.asOf}`}</div>
 </div>;
};

export const StrikeReveal:React.FC<{time:number;items?:string[];result?:string}>=({time,items=['Excesso de texto','Elementos sem função','Movimento sem intenção'],result='CLAREZA'})=><>
 <div style={{...area,top:420}}>{items.map((item,i)=><div key={item} style={{...card,position:'relative',padding:23,marginBottom:17,fontSize:23,fontWeight:650,opacity:1-phase(time,1.6,2.0)*.55}}>{item}<div style={{position:'absolute',left:18,top:'50%',height:3,width:`${phase(time,.35+i*.24,.65+i*.24)*92}%`,background:A,transform:'rotate(-1deg)'}}/></div>)}</div>
 <div style={{position:'absolute',top:850,left:70,right:70,textAlign:'center',fontWeight:850,fontSize:65,letterSpacing:-3,color:A,opacity:phase(time,1.55,2.0),transform:`scale(${.8+.2*phase(time,1.55,2.0)})`}}>{result}</div>
 </>;

export const CapabilityPager:React.FC<{time:number}>=({time})=>{
 const labels=['Camadas','Tipografia','Áudio','Revisão'];const active=Math.min(3,Math.floor(Math.max(0,time-.2)/.65));
 return <div style={{...area,top:410}}><div style={{display:'flex',gap:10,justifyContent:'center',marginBottom:25}}>{labels.map((s,i)=><div key={s} style={{padding:'9px 15px',borderRadius:20,fontSize:16,fontWeight:700,color:i===active?'white':MUTED,background:i===active?A:'#e5e7eb'}}>{s}</div>)}</div><div style={{...card,background:'#11161e',height:285,padding:28,transform:`perspective(1200px) rotateY(${-5+active*2}deg) rotateZ(${-2+active}deg)`}}><div style={{display:'flex',gap:6,marginBottom:30}}>{[0,1,2].map(i=><span key={i} style={{width:10,height:10,borderRadius:'50%',background:i?'#48515a':A}}/>)}</div><div style={{color:'white',fontSize:37,fontWeight:800}}>{labels[active]}</div><div style={{display:'flex',alignItems:'end',height:125,gap:10,marginTop:20}}>{Array.from({length:12},(_,i)=><div key={i} style={{height:28+((i*19+active*11)%86),flex:1,background:i%4===active?A:'#39414e',borderRadius:4}}/>)}</div></div><div style={{textAlign:'center',fontSize:20,fontWeight:700,marginTop:30}}>Uma função por enquadramento</div></div>;
};

export const TypedTerminal:React.FC<{time:number;lines?:string[]}>=({time,lines=['Preparando camadas...','Compondo o movimento...','Gerando frames...','Revisão disponível.']})=>{
 const all=lines.join('\n'),visible=typedText(all,phase(time,.3,2.4));return <><div style={{...area,...card,top:445,height:325,background:'#0d131c',padding:28,transform:`perspective(1000px) rotateY(${-3+phase(time,.3,2.4)*6}deg)`}}><div style={{display:'flex',gap:8,marginBottom:34}}>{['#eb6c73','#e5c36b','#83be94'].map(c=><div key={c} style={{width:12,height:12,borderRadius:'50%',background:c}}/>)}</div><pre style={{fontFamily:'monospace',fontSize:22,lineHeight:1.7,color:'#9ed7bb',whiteSpace:'pre-wrap',margin:0}}>{visible}<span style={{opacity:Math.floor(time*3)%2?0:1}}>▌</span></pre></div><Sticker time={time} at={2.2}>EXEMPLO VISUAL</Sticker></>;
};

export const AudioReactor:React.FC<{levels:readonly number[];radial?:boolean;portrait?:boolean}>=({levels,radial=true,portrait=false})=>{
 const bars=normalizedLevels(levels,64);
 return <div style={{position:'absolute',left:60,top:415,width:600,height:460}}>
 {radial?<svg viewBox='0 0 600 460' width='600' height='460'>{bars.map((v,i)=>{const a=(i/64)*Math.PI*2-Math.PI/2,r=151,l=8+v*65;return <line key={i} x1={300+Math.cos(a)*r} y1={220+Math.sin(a)*r} x2={300+Math.cos(a)*(r+l)} y2={220+Math.sin(a)*(r+l)} stroke={A} strokeWidth='3.2' strokeLinecap='round'/>})}<circle cx='300' cy='220' r='141' fill={INK}/><rect x='278' y='150' width='44' height='88' rx='22' fill='white'/><path d='M258 213v9a42 42 0 0 0 84 0v-9 M300 265v34 M280 299h40' stroke='white' strokeWidth='7' fill='none' strokeLinecap='round'/></svg>:<><div style={{position:'absolute',left:185,top:0,width:230,height:230,borderRadius:'50%',padding:7,border:`3px solid ${A}`,background:'#fff',boxShadow:'0 13px 25px #0002'}}><div style={{width:'100%',height:'100%',borderRadius:'50%',background:portrait?'linear-gradient(130deg,#ccd0d8,#666c79)':'#121925',display:'grid',placeItems:'center',fontSize:73,fontWeight:800,color:'white'}}>IA</div></div><svg viewBox='0 0 600 130' width='600' height='130' style={{position:'absolute',top:265}}>{bars.map((v,i)=><rect key={i} x={i*9.2+5} y={65-(5+v*95)/2} width='4.2' height={5+v*95} rx='2' fill={A}/>)}</svg></>}
 </div>;
};

export const AudioReactorFromFile:React.FC<{src:string;frame:number;fps:number;radial?:boolean}>=({src,frame,fps,radial=true})=>{
 const data=useAudioData(src);if(!data)return null;
 const durationFrames=Math.max(1,Math.floor(data.durationInSeconds*fps)),samples=visualizeAudio({audioData:data,frame:Math.max(0,frame)%durationFrames,fps,numberOfSamples:64,smoothing:true});
 return <AudioReactor levels={samples.map(v=>Math.min(1,Math.sqrt(v)*4))} radial={radial} portrait={!radial}/>;
};

export const KeywordCTA:React.FC<{time:number;keyword?:string}>=({time,keyword='CRIAR'})=>{
 const value=typedText(keyword,phase(time,.65,1.7));return <div style={{...area,top:425,textAlign:'center'}}>
 <div style={{margin:'0 auto 45px',width:100,height:100,borderRadius:29,background:INK,color:A,display:'grid',placeItems:'center',fontSize:53,fontWeight:900,boxShadow:'0 12px 20px #0002'}}>M</div><div style={{fontFamily:'Georgia',fontStyle:'italic',fontSize:30,color:'#b6446e',marginBottom:16}}>uma palavra, uma ação</div>
 <div style={{...card,border:`3px solid ${A}`,borderRadius:50,padding:'22px 34px',height:95,textAlign:'left',fontWeight:850,fontSize:41,letterSpacing:-1}}>{value}<span style={{color:A,opacity:Math.floor(time*3)%2?0:1,fontWeight:300}}>│</span><span style={{float:'right',color:A}}>➤</span></div>
 <div style={{...card,padding:'24px',margin:'30px 18px 0',textAlign:'left',opacity:phase(time,1.8,2.2),transform:`translateY(${(1-phase(time,1.8,2.2))*25}px)`}}><b style={{fontSize:23}}>Seu próximo motion</b><div style={{fontSize:19,color:MUTED,marginTop:8}}>Uma resposta clara e contextual.</div></div>
 </div>;
};

export const EyeAttention:React.FC<{time:number}>=({time})=>{
 const open=phase(time,.1,.65)*(1-.88*(phase(time,1.65,1.8)-phase(time,1.8,2.0))),shift=Math.sin(time*2)*26;
 return <svg viewBox='0 0 600 360' width='600' height='360' style={{position:'absolute',left:60,top:450}}><defs><clipPath id='editorial-eye'><path d='M55 180Q300 25 545 180Q300 335 55 180Z'/></clipPath></defs><g transform={`translate(0 ${180*(1-open)}) scale(1 ${open})`}><path d='M55 180Q300 25 545 180Q300 335 55 180Z' fill='white' stroke={INK} strokeWidth='5'/><g clipPath='url(#editorial-eye)'><circle cx={300+shift} cy='180' r='86' fill={A}/><circle cx={300+shift} cy='180' r='42' fill={INK}/><circle cx={277+shift} cy='147' r='19' fill='white'/></g></g></svg>;
};

const titles:Record<EditorialKind,{kicker:string;before:string;accent:string}>={
 typography:{kicker:'hierarquia tipográfica',before:'A palavra certa',accent:'importa.'},comparison:{kicker:'relações visuais',before:'Comparar para',accent:'explicar.'},focus:{kicker:'atenção seletiva',before:'Do grupo',accent:'ao detalhe.'},metric:{kicker:'informação verificável',before:'Dados com',accent:'contexto.'},strike:{kicker:'simplificar a leitura',before:'Corte o',accent:'excesso.'},capabilities:{kicker:'montagem modular',before:'Uma função',accent:'de cada vez.'},terminal:{kicker:'demonstração guiada',before:'Mostre o',accent:'processo.'},radial:{kicker:'sinal real de entrada',before:'O áudio',accent:'ganha forma.'},portrait:{kicker:'presença e identidade',before:'Uma voz.',accent:'Uma identidade.'},keyword:{kicker:'chamada para ação',before:'Uma ação',accent:'bem clara.'},paper:{kicker:'composição em camadas',before:'Luz que organiza',accent:'o espaço.'},eye:{kicker:'pausa visual',before:'Direcione',accent:'o olhar.'}
};

export const EditorialPatternDemo:React.FC<{audioFile?:string}>=({audioFile})=>{
 const frame=useCurrentFrame(),{fps,width}=useVideoConfig(),index=Math.min(11,Math.floor(frame/(fps*3))),local=frame-index*fps*3,time=local/fps,pattern=editorialPatterns[index],title=titles[pattern.kind];
 const opacity=Math.min(phase(time,0,.14),1-phase(time,2.85,3));
 return <AbsoluteFill style={{background:'#f5f5f7'}}><div style={{position:'absolute',left:0,top:0,width:720,height:1280,transform:`scale(${width/720})`,transformOrigin:'top left'}}><SoftPaperStage time={frame/fps}>
 <div style={{position:'absolute',inset:0,opacity}}><EditorialHeader time={time} {...title}/>
 {pattern.kind==='typography'&&<><div style={{position:'absolute',left:80,right:80,top:445,textAlign:'center',fontFamily:'Georgia',fontStyle:'italic',fontSize:64,color:INK,transform:`rotate(${-5+phase(time,.4,1.2)*5}deg)`,opacity:phase(time,.3,.7)}}>ritmo</div><div style={{position:'absolute',left:80,right:80,top:565,textAlign:'center',fontWeight:850,fontSize:75,letterSpacing:-4,color:A,transform:`scale(${.75+.25*phase(time,.75,1.15)})`,opacity:phase(time,.7,1.1)}}>INTENÇÃO</div><Sticker time={time} at={1.3}>UMA PALAVRA EM DESTAQUE</Sticker></>}
 {pattern.kind==='comparison'&&<LinkedPanelComparison time={time}/>}
 {pattern.kind==='focus'&&<SemanticFocus time={time}/>}
 {pattern.kind==='metric'&&<EvidenceMetric time={time} evidence={{value:120,label:'itens de demonstração',kind:'illustrative'}}/>}
 {pattern.kind==='strike'&&<StrikeReveal time={time}/>}
 {pattern.kind==='capabilities'&&<CapabilityPager time={time}/>}
 {pattern.kind==='terminal'&&<TypedTerminal time={time}/>}
 {(pattern.kind==='radial'||pattern.kind==='portrait')&&<>{audioFile?<AudioReactorFromFile src={staticFile(audioFile)} frame={local} fps={fps} radial={pattern.kind==='radial'}/>:<AudioReactor levels={[]} radial={pattern.kind==='radial'} portrait/>}<div style={{position:'absolute',left:80,right:80,top:950,textAlign:'center',fontSize:20,color:MUTED}}>{audioFile?'Sinal de teste analisado · saída sem áudio':'Sem fonte de áudio · barras em repouso'}</div></>}
 {pattern.kind==='keyword'&&<KeywordCTA time={time}/>}
 {pattern.kind==='paper'&&<div style={{...area,...card,top:455,height:315,padding:35,transform:`perspective(1200px) rotateY(${Math.sin(time)*5}deg)`}}>{['Título','Sujeito','Apoio'].map((t,i)=><div key={t} style={{padding:'19px 23px',marginTop:10,background:i===1?'#ffe3ed':'#f0f1f4',borderRadius:12,transform:`translateX(${i*11*phase(time,.2,1.1)}px)`,fontSize:26,fontWeight:700,color:i===1?A:INK}}>{t}</div>)}</div>}
 {pattern.kind==='eye'&&<EyeAttention time={time}/>}
 <div style={{position:'absolute',left:60,right:60,top:1090,textAlign:'center',fontSize:20,fontWeight:700,color:MUTED}}>{pattern.id} · {pattern.name}</div>
 </div></SoftPaperStage></div></AbsoluteFill>;
};
