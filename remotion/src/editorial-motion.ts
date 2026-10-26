export const editorialPatterns=[
 {id:'P10',kind:'typography',name:'Hierarquia editorial'},
 {id:'P11',kind:'comparison',name:'Painéis conectados'},
 {id:'P12',kind:'focus',name:'Correção e foco semântico'},
 {id:'P13',kind:'metric',name:'Contador com evidência'},
 {id:'P14',kind:'strike',name:'Risco e revelação'},
 {id:'P15',kind:'capabilities',name:'Funções em sequência'},
 {id:'P16',kind:'terminal',name:'Terminal digitado'},
 {id:'P17',kind:'radial',name:'Reator radial de áudio'},
 {id:'P18',kind:'portrait',name:'Retrato com waveform'},
 {id:'P19',kind:'keyword',name:'CTA por palavra-chave'},
 {id:'P20',kind:'paper',name:'Luz e papel em camadas'},
 {id:'P21',kind:'eye',name:'Olho e pausa de atenção'},
] as const;
export type EditorialKind=typeof editorialPatterns[number]['kind'];
export type MetricEvidence={value:number;label:string;kind:'illustrative'|'verified';source?:string;asOf?:string};
export const editorialPhase=(value:number,start:number,end:number)=>{
 if(end<=start)throw new Error('Motion interval must be positive');
 const t=Math.max(0,Math.min(1,(value-start)/(end-start)));return t*t*(3-2*t);
};
export function metricValue(progress:number,evidence:MetricEvidence){
 if(!Number.isFinite(evidence.value)||evidence.value<0)throw new Error('Metric value must be finite and nonnegative');
 if(evidence.kind==='verified'&&(!evidence.source?.trim()||!evidence.asOf?.trim()))throw new Error('Verified metric requires a source and observation date');
 const t=editorialPhase(progress,0,1);return Math.round(evidence.value*t);
}
export function typedText(text:string,progress:number){
 const graphemes=Array.from(new Intl.Segmenter('pt-BR',{granularity:'grapheme'}).segment(text),x=>x.segment);
 return graphemes.slice(0,Math.floor(graphemes.length*Math.max(0,Math.min(1,progress)))).join('');
}
export function normalizedLevels(values:readonly number[],count:number){
 if(!Number.isInteger(count)||count<1)throw new Error('Positive bar count required');
 return Array.from({length:count},(_,i)=>{
  const v=values[Math.min(values.length-1,Math.floor(i*values.length/count))]??0;
  return Number.isFinite(v)?Math.max(0,Math.min(1,v)):0;
 });
}
