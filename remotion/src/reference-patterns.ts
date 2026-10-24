// Frame intervals are half-open: [start, end). 30 fps, 466 decoded frames.
// Boundaries are observed; authoring transforms below are reconstruction choices.
export const REFERENCE_STUDY = {
  fps:30, width:720, height:1280, durationInFrames:466,
  blocks:[
    {id:'device-layers', start:0, end:130, evidence:'observed'},
    {id:'glowing-object', start:130, end:194, evidence:'observed'},
    {id:'kinetic-light', start:194, end:278, evidence:'observed'},
    {id:'kinetic-dark', start:278, end:393, evidence:'observed'},
    {id:'brand-resolve', start:393, end:466, evidence:'observed'},
  ],
} as const;

export type Pose={frame:number;x:number;y:number;scale:number;rx:number;ry:number;rz:number};
export const phonePoses:Pose[]=[
 {frame:0,x:360,y:640,scale:.24,rx:-24,ry:-28,rz:-37},
 {frame:7,x:360,y:640,scale:.40,rx:9,ry:174,rz:-16},
 {frame:14,x:360,y:640,scale:.50,rx:8,ry:266,rz:-12},
 {frame:24,x:360,y:647,scale:.79,rx:3,ry:348,rz:-7},
 {frame:34,x:360,y:648,scale:1,rx:0,ry:360,rz:-2},
 {frame:45,x:360,y:600,scale:1.85,rx:65,ry:349,rz:-10},
 {frame:53,x:360,y:830,scale:2.20,rx:47,ry:344,rz:-13},
 {frame:61,x:390,y:900,scale:3.2,rx:30,ry:350,rz:12},
 {frame:70,x:395,y:930,scale:3.3,rx:32,ry:350,rz:14},
 {frame:79,x:300,y:1150,scale:3.2,rx:26,ry:370,rz:-12},
 {frame:88,x:750,y:1200,scale:4.3,rx:39,ry:360,rz:-13},
 {frame:98,x:300,y:790,scale:2.7,rx:68,ry:360,rz:4},
 {frame:106,x:275,y:895,scale:2.8,rx:62,ry:345,rz:28},
 {frame:129,x:260,y:865,scale:2.8,rx:62,ry:342,rz:30},
];

export function easeInOutCubic(t:number){const x=Math.max(0,Math.min(1,t));return x<.5?4*x*x*x:1-(-2*x+2)**3/2;}
export function phase(frame:number,start:number,end:number){return easeInOutCubic((frame-start)/(end-start));}
export function poseAt(frame:number, poses:Pose[]=phonePoses):Pose {
 if(frame<=poses[0].frame)return {...poses[0],frame};
 const last=poses[poses.length-1]; if(frame>=last.frame)return {...last,frame};
 const i=poses.findIndex((p)=>p.frame>frame),a=poses[i-1],b=poses[i];
 const t=phase(frame,a.frame,b.frame);
 const mix=(k:keyof Omit<Pose,'frame'>)=>a[k]+(b[k]-a[k])*t;
 return {frame,x:mix('x'),y:mix('y'),scale:mix('scale'),rx:mix('rx'),ry:mix('ry'),rz:mix('rz')};
}

export const learnedPatterns=[
 {id:'P01',name:'Product reveal',required:['front','back','edge','light'],evidence:'inferred-reconstruction'},
 {id:'P02',name:'Exploded interface',required:['base','ui-crops','depth-stagger','camera'],evidence:'inferred-reconstruction'},
 {id:'P03',name:'Anchor to highlighted detail',required:['anchor','camera-path','focus'],evidence:'inferred-reconstruction'},
 {id:'P04',name:'Emissive badge and rings',required:['badge','rings','glow'],evidence:'inferred-reconstruction'},
 {id:'P05',name:'Rotating object and type orbit',required:['faces','parent-rig','type'],evidence:'inferred-reconstruction'},
 {id:'P06',name:'Word choreography',required:['word-cues','local-transforms','camera'],evidence:'inferred-reconstruction'},
 {id:'P07',name:'Luma and iris transition',required:['mask','background','focus-word'],evidence:'inferred-reconstruction'},
 {id:'P08',name:'Foreground bars with depth',required:['bars','text','occlusion'],evidence:'inferred-reconstruction'},
 {id:'P09',name:'Blur to brand resolve',required:['mark','blur-curve','hold'],evidence:'inferred-reconstruction'},
] as const;
