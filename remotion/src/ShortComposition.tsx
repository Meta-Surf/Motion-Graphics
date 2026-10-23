import React from "react";
import { AbsoluteFill, Img, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export type SceneLayout = "hero" | "interface" | "timeline" | "stat" | "orbit";
export type ShortScene = {
  id: string;
  durationInFrames: number;
  image?: string;
  eyebrow: string;
  headline: string;
  accent?: string;
  caption: string;
  layout: SceneLayout;
  cards?: string[];
  metric?: string;
  visualLabel?: string;
};
export type ShortProps = { title: string; accentColor: string; scenes: ShortScene[] };
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

const Headline: React.FC<{scene: ShortScene; color: string}> = ({scene, color}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const reveal = spring({frame: f - 6, fps, config: {damping: 16, stiffness: 85}});
  const key = scene.accent || scene.headline.split(" ").slice(-2).join(" ");
  const parts = scene.headline.split(key);
  return <div style={{marginTop: 32, maxWidth: 900, fontSize: 88, lineHeight: 0.98, letterSpacing: -4, fontWeight: 900, transform: "translateY(" + interpolate(reveal, [0, 1], [72, 0]) + "px)", opacity: interpolate(f, [4, 18], [0, 1], clamp)}}>{parts.length > 1 ? <>{parts[0]}<span style={{color, textShadow: "0 0 38px " + color + "66"}}>{key}</span>{parts.slice(1).join(key)}</> : scene.headline}</div>;
};

const Foreground: React.FC<{scene: ShortScene; color: string}> = ({scene, color}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame: f - 18, fps, config: {damping: 13, stiffness: 110, mass: 0.7}});
  const lift = interpolate(pop, [0, 1], [125, 0]);
  const cards = scene.cards || [];
  const glass: React.CSSProperties = {background: "linear-gradient(135deg,rgba(19,27,44,.88),rgba(10,15,28,.74))", border: "1px solid rgba(255,255,255,.2)", boxShadow: "0 28px 90px rgba(0,0,0,.4),inset 0 1px rgba(255,255,255,.12)", backdropFilter: "blur(18px)"};
  const floating = (i: number) => ({transform: "translateY(" + (Math.sin((f + i * 11) / 10) * 8) + "px)"});

  if (scene.layout === "interface") return <div style={{position:"absolute",top:790,left:94,right:94,height:500,...glass,borderRadius:34,padding:30,transform:"translateY("+lift+"px) rotate("+interpolate(f,[0,90],[-5,2],clamp)+"deg)",opacity:pop}}>
    <div style={{display:"flex",justifyContent:"space-between",borderBottom:"1px solid rgba(255,255,255,.14)",paddingBottom:22,fontSize:19,letterSpacing:3,color:"rgba(255,255,255,.65)"}}><span>{scene.visualLabel || "WORKSPACE"}</span><span style={{color}}>● LIVE</span></div>
    <div style={{marginTop:26,height:248,borderRadius:24,background:"radial-gradient(circle at 65% 35%,"+color+"88,transparent 24%),linear-gradient(135deg,#263858,#11192c 64%,#382b53)",position:"relative",overflow:"hidden"}}>
      <div style={{position:"absolute",inset:0,background:"linear-gradient(130deg,transparent 40%,rgba(255,255,255,.2) 50%,transparent 60%)",transform:"translateX("+interpolate(f,[15,55],[-400,650],clamp)+"px)"}}/>
      <div style={{position:"absolute",left:24,bottom:20,fontSize:18,letterSpacing:2,fontWeight:800}}>SCENE PREVIEW / 09:16</div>
    </div>
    <div style={{display:"flex",gap:12,marginTop:22}}>{cards.slice(0,3).map((x,i)=><div key={x} style={{flex:1,padding:"17px 12px",borderRadius:16,background:i===1?color+"28":"rgba(255,255,255,.07)",border:"1px solid "+(i===1?color+"88":"rgba(255,255,255,.1)"),textAlign:"center",fontSize:16,letterSpacing:1.4,fontWeight:800}}>{x}</div>)}</div>
  </div>;

  if (scene.layout === "timeline") return <div style={{position:"absolute",left:70,right:70,bottom:445,height:260,...glass,borderRadius:28,padding:28,transform:"translateY("+lift+"px)",opacity:pop}}>
    <div style={{display:"flex",justifyContent:"space-between",fontSize:18,letterSpacing:2,color:"rgba(255,255,255,.68)"}}><span>{scene.visualLabel || "TIMELINE"}</span><span>00:34 / 00:45</span></div>
    <div style={{display:"flex",gap:10,height:108,marginTop:24}}>{cards.slice(0,4).map((x,i)=><div key={x} style={{flex:1,borderRadius:14,padding:12,background:"linear-gradient(145deg,"+color+(i===0?"80":"35")+",rgba(49,63,91,.8))",border:"1px solid rgba(255,255,255,.17)",...floating(i),display:"flex",alignItems:"end",fontSize:14,fontWeight:800}}>{x}</div>)}</div>
    <div style={{height:5,marginTop:20,borderRadius:5,background:"rgba(255,255,255,.15)"}}><div style={{width:interpolate(f,[20,100],[4,92],clamp)+"%",height:"100%",background:color,borderRadius:5}}/></div>
  </div>;

  if (scene.layout === "stat") return <div style={{position:"absolute",top:930,left:118,right:118,display:"flex",alignItems:"center",gap:28,transform:"translateX("+lift+"px)",opacity:pop}}>
    <div style={{width:270,height:270,borderRadius:"50%",border:"2px solid "+color+"88",display:"grid",placeItems:"center",background:"rgba(6,10,20,.68)",boxShadow:"0 0 80px "+color+"30",color,fontSize:54,fontWeight:900}}>{scene.metric || "2×"}</div>
    <div style={{flex:1,fontSize:24,lineHeight:1.35,fontWeight:800}}>{cards.slice(0,2).map(x=><div key={x} style={{borderBottom:"1px solid rgba(255,255,255,.24)",padding:"16px 0"}}>{x}<span style={{color,float:"right"}}>↗</span></div>)}</div>
  </div>;

  if (scene.layout === "orbit") return <div style={{position:"absolute",top:820,left:90,right:90,height:470,transform:"translateY("+lift+"px)",opacity:pop}}>
    <div style={{position:"absolute",left:"50%",top:"48%",width:250,height:250,margin:-125,borderRadius:"50%",display:"grid",placeItems:"center",background:"radial-gradient(circle at 40% 35%,"+color+",#26375b 65%,#12182a)",boxShadow:"0 0 100px "+color+"55",fontSize:34,fontWeight:900,zIndex:2}}>{scene.metric || "IA"}</div>
    <div style={{position:"absolute",left:"50%",top:"48%",width:440,height:270,margin:"-135px -220px",border:"1px solid "+color+"77",borderRadius:"50%",transform:"rotate("+f*0.45+"deg)"}}/>
    {cards.slice(0,3).map((x,i)=>{const angle=f*0.025+i*Math.PI*2/Math.max(1,Math.min(3,cards.length));const xPos=50+Math.cos(angle)*39;const yPos=48+Math.sin(angle)*34;return <div key={x} style={{position:"absolute",left:xPos+"%",top:yPos+"%",transform:"translate(-50%,-50%)",padding:"18px 23px",borderRadius:18,...glass,fontSize:16,fontWeight:800,whiteSpace:"nowrap"}}>{x}</div>;})}
  </div>;

  return <div style={{position:"absolute",left:80,right:80,bottom:510,height:320,transform:"translateY("+lift+"px)",opacity:pop}}>
    <div style={{position:"absolute",width:365,height:365,right:10,top:-35,borderRadius:"50%",border:"1px solid "+color+"66",transform:"rotate("+f*0.25+"deg)"}}/>
    <div style={{position:"absolute",width:250,height:250,right:65,top:22,borderRadius:"50%",background:"radial-gradient(circle at 35% 30%,"+color+"cc,#18334a 55%,rgba(15,20,38,.45))",boxShadow:"0 0 90px "+color+"66",transform:"translateY("+Math.sin(f/10)*12+"px)"}}/>
    <div style={{position:"absolute",left:0,top:28,maxWidth:490,...glass,borderRadius:24,padding:24,fontSize:22,fontWeight:800,lineHeight:1.3,transform:"rotate(-2deg) translateY("+Math.sin(f/12)*7+"px)"}}>{scene.visualLabel || "NOVAS POSSIBILIDADES"}<div style={{display:"flex",gap:10,marginTop:18}}>{cards.slice(0,3).map((x,i)=><span key={x} style={{color:i===1?color:"rgba(255,255,255,.66)",fontSize:13,letterSpacing:1}}>{x}</span>)}</div></div>
    {scene.metric && <div style={{position:"absolute",right:18,bottom:-7,color,fontSize:26,fontWeight:900,letterSpacing:3,textShadow:"0 0 30px "+color}}>{scene.metric}</div>}
  </div>;
};

const Scene: React.FC<{scene:ShortScene;color:string;index:number}> = ({scene,color,index}) => {
  const f=useCurrentFrame();
  const {fps}=useVideoConfig();
  const opacity=interpolate(f,[0,10,scene.durationInFrames-12,scene.durationInFrames],[0,1,1,0],clamp);
  const zoom=interpolate(f,[0,scene.durationInFrames],[1.06,1.14],clamp);
  const drift=index%2===0?-24:24;
  return <AbsoluteFill style={{opacity,overflow:"hidden",backgroundColor:"#080c16",color:"#fff",fontFamily:"Arial,Helvetica,sans-serif"}}>
    {scene.image?<Img src={scene.image} style={{width:"100%",height:"100%",objectFit:"cover",transform:"scale("+zoom+") translateX("+interpolate(f,[0,scene.durationInFrames],[0,drift],clamp)+"px)",filter:"brightness(.64) saturate(.9)"}}/>:<AbsoluteFill style={{background:"radial-gradient(ellipse at "+(35+(index%3)*15)+"% 35%,"+color+"38 0%,transparent 48%),linear-gradient(145deg,#111a2c 0%,#090b13 65%,#18223a 100%)"}}/>}
    <AbsoluteFill style={{background:"linear-gradient(180deg,rgba(5,8,15,.10),rgba(5,8,15,.20) 35%,rgba(5,8,15,.92))"}}/>
    <AbsoluteFill style={{pointerEvents:"none",opacity:.2,backgroundImage:"linear-gradient("+color+"20 1px,transparent 1px),linear-gradient(90deg,"+color+"20 1px,transparent 1px)",backgroundSize:"90px 90px",maskImage:"linear-gradient(180deg,black,transparent 62%)",transform:"translateY(-"+f%90+"px)"}}/>
    <div style={{position:"absolute",top:112,left:78,right:78,display:"flex",justifyContent:"space-between",fontSize:22,letterSpacing:5,fontWeight:800,color}}><span>META / MOTION</span><span>0{index+1}</span></div>
    <div style={{position:"absolute",top:290,left:80,right:80}}>
      <div style={{display:"inline-flex",alignItems:"center",gap:12,padding:"12px 18px",border:"1px solid "+color+"88",borderRadius:999,color,background:"rgba(6,10,20,.56)",fontSize:22,fontWeight:800,letterSpacing:3,transform:"translateY("+interpolate(spring({frame:f,fps,config:{damping:18,stiffness:95}}),[0,1],[34,0])+"px)"}}><span style={{width:9,height:9,borderRadius:10,backgroundColor:color,boxShadow:"0 0 20px "+color}}/>{scene.eyebrow}</div>
      <Headline scene={scene} color={color}/>
    </div>
    <Foreground scene={scene} color={color}/>
    <div style={{position:"absolute",bottom:195,left:78,right:78,padding:"24px 28px",borderLeft:"6px solid "+color,background:"linear-gradient(90deg,rgba(5,8,15,.88),rgba(5,8,15,.42))",fontSize:31,lineHeight:1.25,fontWeight:700,textShadow:"0 2px 10px rgba(0,0,0,.8)",transform:"translateY("+interpolate(spring({frame:f-34,fps,config:{damping:15,stiffness:100}}),[0,1],[54,0])+"px)",opacity:interpolate(f,[32,44],[0,1],clamp)}}>{scene.caption}</div>
  </AbsoluteFill>;
};

export const ShortComposition: React.FC<ShortProps> = ({scenes,accentColor}) => {
  let cursor=0;
  const positioned=scenes.map(scene=>{const from=cursor;cursor+=scene.durationInFrames;return {scene,from};});
  const frame=useCurrentFrame();
  return <AbsoluteFill style={{backgroundColor:"#080c16",overflow:"hidden"}}>
    {positioned.map(({scene,from},index)=><Sequence key={scene.id} from={from} durationInFrames={scene.durationInFrames} layout="none"><Scene scene={scene} color={accentColor} index={index}/></Sequence>)}
    <div style={{position:"absolute",top:0,left:0,width:"100%",height:5,background:"rgba(255,255,255,.16)",zIndex:50}}><div style={{width:interpolate(frame,[0,cursor],[0,100],clamp)+"%",height:"100%",background:accentColor}}/></div>
  </AbsoluteFill>;
};
