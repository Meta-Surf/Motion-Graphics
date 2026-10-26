import React,{useLayoutEffect,useMemo} from 'react';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';

export type MobileTextures={wallpaper:THREE.Texture;cafe:THREE.Texture;mountain:THREE.Texture;screen:THREE.Texture;message:THREE.Texture;agenda:THREE.Texture;map:THREE.Texture};
export const smooth=(x:number)=>{const t=Math.max(0,Math.min(1,x));return t*t*(3-2*t)};
export const enter=(f:number,a:number,b:number)=>smooth((f-a)/(b-a));

function roundedShape(w:number,h:number,r:number){
 const s=new THREE.Shape(),x=-w/2,y=-h/2;
 s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);return s;
}
function roundedPlane(w:number,h:number,r:number){
 const g=new THREE.ShapeGeometry(roundedShape(w,h,r),32),pos=g.attributes.position,uv=g.attributes.uv;
 for(let i=0;i<pos.count;i++)uv.setXY(i,pos.getX(i)/w+.5,pos.getY(i)/h+.5);
 return g;
}
function roundedBox(w:number,h:number,depth:number,r:number){
 const g=new THREE.ExtrudeGeometry(roundedShape(w,h,r),{depth,bevelEnabled:true,bevelThickness:.028,bevelSize:.025,bevelSegments:4,steps:1,curveSegments:32});g.translate(0,0,-depth/2);return g;
}
export const StudioEnvironment:React.FC=()=>{
 const {gl,scene,invalidate}=useThree();
 useLayoutEffect(()=>{const pmrem=new THREE.PMREMGenerator(gl),room=new RoomEnvironment(),target=pmrem.fromScene(room,.035),prior=scene.environment;scene.environment=target.texture;scene.environmentIntensity=.85;invalidate();return()=>{scene.environment=prior;target.dispose();room.dispose();pmrem.dispose()};},[gl,scene,invalidate]);
 return <><ambientLight intensity={.55}/><directionalLight position={[3,5,6]} intensity={3.5} color='#edf6ff'/><pointLight position={[-4,2,3]} color='#3fcfff' intensity={22}/><pointLight position={[4,-3,-3]} color='#ffcf8f' intensity={16}/></>;
};

const InterfacePlane:React.FC<{texture:THREE.Texture;position:[number,number,number];rotation?:[number,number,number];w:number;h:number;opacity?:number}>=({texture,position,rotation=[0,0,0],w,h,opacity=1})=>{
 const geo=useMemo(()=>roundedPlane(w,h,.10),[w,h]);
 return <group position={position} rotation={rotation}><mesh geometry={geo} position={[0,-.025,-.025]}><meshStandardMaterial color='#071b2e' metalness={.4} roughness={.35} transparent opacity={opacity}/></mesh><mesh geometry={geo}><meshBasicMaterial map={texture} transparent opacity={opacity} side={THREE.DoubleSide} toneMapped={false}/></mesh></group>;
};

export const MobileDevice:React.FC<{f:number;shot:number;duration:number;textures:MobileTextures}>=({f,shot,duration,textures})=>{
 const p=f/Math.max(1,duration-1),t=enter(f,5,38);
 const geo=useMemo(()=>({body:roundedBox(2.30,4.92,.17,.28),back:roundedPlane(2.23,4.85,.265),glass:roundedPlane(2.20,4.78,.245),screen:roundedPlane(2.13,4.69,.225),island:roundedPlane(.53,.13,.065),board:roundedPlane(1.94,4.47,.17)}),[]);
 let x=0,y=-.45,z=0,s=.86,rx=.10,ry=-.22,rz=-.07;
 if(shot===0){s=.43+.42*enter(f,0,58);ry=2.9*(1-enter(f,7,60))+.14*Math.sin(p*3);rx=.16;rz=-.12+.16*enter(f,0,50);y=-.45;}
 if(shot===1){s=.83+.12*enter(f,20,130);rx=.13+.06*p;ry=-.18-.16*p;rz=.04;y=-.55+.20*enter(f,25,145);}
 if(shot===2){s=.80+.21*enter(f,20,175);rx=.75-.25*p;ry=.35-.30*p;rz=-.19; y=-.6;}
 if(shot===3){x=-.8;y=-.45;s=.74;rx=.09;ry=.48;rz=-.11;}
 if(shot===4){s=.81;rx=.61;ry=-.38+.20*p;rz=-.19;x=-.24;y=-.63;}
 if(shot===5){s=.51;x=1.1;y=-1.4;ry=.4;rz=.17;}
 if(shot===6){s=.72;x=-.73;y=-.57;rx=.17;ry=.60;rz=-.11;}
 if(shot===7){s=.78;x=.18;y=-.65;rx=.23;ry=-.36+.1*p;rz=.10;}
 if(shot===8){s=.65;x=.79;y=-1.1;rx=.1;ry=-.3+.35*p;rz=.07;}
 const float=Math.sin(f*.026)*.035;
 const explode=shot===4?enter(f,65,115)*(1-.22*enter(f,duration-45,duration-10)):0;
 const cards=shot===2?enter(f,15,58):0;
 const shellMat=<meshPhysicalMaterial color='#6f7b88' metalness={.97} roughness={.23} clearcoat={1} clearcoatRoughness={.15} envMapIntensity={1.3}/>;
 return <group position={[x,y+float,z]} rotation={[rx,ry,rz]} scale={s}>
  <mesh geometry={geo.body}>{shellMat}</mesh>
  <mesh geometry={geo.back} position={[0,0,-.113]} rotation={[0,Math.PI,0]}><meshPhysicalMaterial color='#111b2c' metalness={.35} roughness={.17} clearcoat={1} envMapIntensity={1.4}/></mesh>
  <group position={[-.64,1.47,-.135]} rotation={[0,Math.PI,0]}>
   <mesh position={[0,0,.035]}><boxGeometry args={[.88,1.12,.075]}/><meshPhysicalMaterial color='#26374a' roughness={.22} metalness={.8}/></mesh>
   {[[0,.28],[-.22,-.22],[.24,-.22]].map(([lx,ly],i)=><group key={i} position={[lx,ly,.14]}><mesh rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[.185,.19,.105,48]}/><meshStandardMaterial color='#98a8b6' metalness={1} roughness={.17}/></mesh><mesh position={[0,0,.06]}><circleGeometry args={[.145,48]}/><meshPhysicalMaterial color='#071c34' metalness={.6} roughness={.07} clearcoat={1}/></mesh><mesh position={[-.035,.04,.068]}><circleGeometry args={[.037,24]}/><meshBasicMaterial color='#8edfff' transparent opacity={.6}/></mesh></group>)}
  </group>
  {[-1,1].map(side=><mesh key={side} position={[side*1.17,.65*side,0]}><boxGeometry args={[.045,side===1?.42:.65,.095]}/><meshStandardMaterial color='#9cabb7' metalness={1} roughness={.24}/></mesh>)}
  {explode>.01&&<group position={[0,0,.15]}>
   <mesh geometry={geo.board}><meshStandardMaterial color='#0e2832' metalness={.5} roughness={.42}/></mesh>
   {Array.from({length:12},(_,i)=><mesh key={i} position={[-.78+(i%3)*.78,-1.8+Math.floor(i/3)*1.18,.04]}><boxGeometry args={[.44,.57,.07]}/><meshStandardMaterial color={i===7?'#26c6dc':'#203946'} metalness={.8} roughness={.35}/></mesh>)}
   <mesh position={[0,.2,.12+explode*.12]}><boxGeometry args={[.94,.96,.12]}/><meshPhysicalMaterial color='#082d3c' metalness={.7} roughness={.2} emissive='#10b9d6' emissiveIntensity={.28}/></mesh>
   {Array.from({length:15},(_,i)=><mesh key={i} position={[-.85+(i%5)*.42,-1.8+Math.floor(i/5)*1.8,.09]}><boxGeometry args={[.035,.60,.015]}/><meshBasicMaterial color='#3bd4da'/></mesh>)}
  </group>}
  <group position={[0,0,.13+explode*.76]}>
   <mesh geometry={geo.glass}><meshPhysicalMaterial color='#01040c' roughness={.05} metalness={.35} clearcoat={1} envMapIntensity={1.1}/></mesh>
   <mesh geometry={geo.screen} position={[0,0,.012]}><meshBasicMaterial map={textures.screen} toneMapped={false}/></mesh>
   <mesh geometry={geo.island} position={[0,2.135,.022]}><meshBasicMaterial color='#02050a'/></mesh>
   <mesh geometry={geo.screen} position={[0,0,.019]}><meshPhysicalMaterial color='#cfe7ff' transparent opacity={.035} roughness={.06} metalness={.3} clearcoat={1} depthWrite={false}/></mesh>
  </group>
  {cards>0&&<>
   <InterfacePlane texture={textures.message} position={[-.20*enter(f,15,48),.78,.18+enter(f,15,48)*.50]} rotation={[-.09*cards,-.08*cards,.025*cards]} w={1.94} h={.92} opacity={enter(f,15,38)}/>
   <InterfacePlane texture={textures.agenda} position={[.15*enter(f,26,60),-.32,.19+enter(f,26,60)*.80]} rotation={[-.12*cards,.05*cards,-.035*cards]} w={1.96} h={.94} opacity={enter(f,26,50)}/>
   <InterfacePlane texture={textures.map} position={[-.14*enter(f,38,75),-1.15,.20+enter(f,38,75)*1.06]} rotation={[-.18*cards,-.05*cards,.025*cards]} w={1.98} h={1.12} opacity={enter(f,38,63)}/>
  </>}
 </group>;
};

function panel(ctx:CanvasRenderingContext2D,x:number,y:number,w:number,h:number,r:number,fill:string,stroke?:string){ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fillStyle=fill;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=2;ctx.stroke();}}
function text(ctx:CanvasRenderingContext2D,t:string,x:number,y:number,size:number,color='#f3f8ff',weight=600){ctx.font=`${weight} ${size}px Arial`;ctx.fillStyle=color;ctx.fillText(t,x,y);}
function textureFromCanvas(canvas:HTMLCanvasElement){const t=new THREE.CanvasTexture(canvas);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;return t;}

export function makeMobileTextures(wallpaper:THREE.Texture,cafe:THREE.Texture,mountain:THREE.Texture):MobileTextures{
 const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=2200;const ctx=canvas.getContext('2d')!;
 ctx.drawImage(wallpaper.image as CanvasImageSource,0,0,1024,2200);ctx.fillStyle='#03101dc9';ctx.fillRect(0,0,1024,2200);
 text(ctx,'9:41',65,95,38,'#f4f9ff',700);text(ctx,'▰  ▰  ▰',804,95,32);
 text(ctx,'Seu assistente',65,285,72,'#f1f8ff',700);text(ctx,'Ideias que viram ações.',68,351,33,'#97b6cc',400);
 panel(ctx,55,425,914,235,42,'#10354edb','#3c7b9f');text(ctx,'Como posso ajudar?',95,505,47,'#f4faff',700);text(ctx,'Organizar minha tarde',95,575,37,'#86d9eb');
 text(ctx,'CONTEXTO DO SEU DIA',68,745,28,'#6b9eb8',700);
 panel(ctx,55,790,914,270,35,'#0d2234f2','#28475e');text(ctx,'MENSAGENS',97,849,26,'#56d6e8');text(ctx,'Um resumo do que importa.',97,919,43);text(ctx,'Você revisa antes de enviar.',97,990,31,'#8ca5bb',400);
 panel(ctx,55,1100,914,275,35,'#0d2234f2','#28475e');text(ctx,'AGENDA',97,1164,26,'#f4c387');text(ctx,'Seu próximo compromisso',97,1234,43);text(ctx,'Hoje, às 15h  •  preparar lembrete',97,1302,31,'#a4b4c4',400);
 ctx.save();ctx.beginPath();ctx.roundRect(55,1420,914,395,35);ctx.clip();ctx.drawImage(cafe.image as CanvasImageSource,0,240,1024,580,55,1420,914,395);const grad=ctx.createLinearGradient(0,1580,0,1820);grad.addColorStop(0,'#06121b00');grad.addColorStop(1,'#06121bf2');ctx.fillStyle=grad;ctx.fillRect(55,1420,914,395);ctx.restore();text(ctx,'Uma pausa no caminho',97,1742,44,'#f5f9ff',700);
 panel(ctx,55,1880,914,152,55,'#15485bec','#49bdd0');text(ctx,'Pergunte, revise e confirme.',100,1973,37,'#dff9ff',600);panel(ctx,338,2120,348,12,6,'#f0f7ff');
 const message=document.createElement('canvas');message.width=1000;message.height=480;const m=message.getContext('2d')!;panel(m,5,5,990,470,50,'#102e43','#4e8ca5');text(m,'MENSAGENS',54,82,29,'#66dded');text(m,'Seu resumo está pronto.',54,173,56);text(m,'Dois pontos. Uma próxima ação.',54,243,35,'#a6bed0',400);panel(m,52,301,888,116,30,'#1c5366');text(m,'Revisar mensagem',92,374,41,'#e0fbff');
 const agenda=document.createElement('canvas');agenda.width=1000;agenda.height=480;const a=agenda.getContext('2d')!;panel(a,5,5,990,470,50,'#132e42','#658ca6');text(a,'AGENDA',54,82,29,'#f4c586');text(a,'Hoje • 15:00',54,172,62);text(a,'Preparar o próximo compromisso',54,246,36,'#b2c7d9');panel(a,53,300,888,116,30,'#294c61');text(a,'Criar lembrete',92,374,41,'#eff8ff');
 const map=document.createElement('canvas');map.width=1000;map.height=570;const g=map.getContext('2d')!;panel(g,5,5,990,560,50,'#102a3a','#5e90a3');g.save();g.beginPath();g.roundRect(24,21,952,526,40);g.clip();g.strokeStyle='#35556c';g.lineWidth=25;for(let i=0;i<7;i++){g.beginPath();g.moveTo(i*170-100,0);g.lineTo(i*170+140,570);g.stroke();g.beginPath();g.moveTo(0,i*115-50);g.lineTo(1000,i*115+160);g.stroke();}g.strokeStyle='#56dcea';g.lineWidth=18;g.lineCap='round';g.beginPath();g.moveTo(180,400);g.lineTo(380,340);g.lineTo(510,200);g.lineTo(770,150);g.stroke();g.fillStyle='#f6c991';g.beginPath();g.arc(770,150,35,0,Math.PI*2);g.fill();g.restore();panel(g,45,405,910,118,30,'#071d2be8');text(g,'MAPAS  •  próxima etapa',80,482,40,'#d4f9ff');
 return {wallpaper,cafe,mountain,screen:textureFromCanvas(canvas),message:textureFromCanvas(message),agenda:textureFromCanvas(agenda),map:textureFromCanvas(map)};
}
