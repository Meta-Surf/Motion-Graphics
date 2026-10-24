import type {ShortProps, SceneLayout} from './ShortComposition';
export const getMotionDemoProps=():ShortProps=>({title:'Biblioteca Motion',accentColor:'#67e1dc',brandLabel:'MOTION / LAB',scenes:[
 {id:'layers',layout:'layers',eyebrow:'EXPLICAR A ESTRUTURA',headline:'Cada camada tem uma função',caption:'Separar, revelar e remontar.',cards:['BASE','CONEXÕES','MEMÓRIA','CÁLCULO','RESPOSTA']},
 {id:'object',layout:'object3d',eyebrow:'OBJETO EM DESTAQUE',headline:'Volume, luz e perspectiva',caption:'Um objeto coerente em qualquer ângulo.',cards:['MODELO 3D · ILUMINAÇÃO']},
 {id:'flow',layout:'dataflow',eyebrow:'MOSTRAR O PROCESSO',headline:'Do dado à resposta',caption:'Movimento que explica uma relação.',cards:['ENTRADA','CÁLCULO','SAÍDA']},
 {id:'cutaway',layout:'cutaway',eyebrow:'REVELAR O INTERIOR',headline:'Entender por dentro',caption:'Máscaras revelam o que importa.',cards:['COMPONENTES EM FOCO']},
 {id:'scale',layout:'scale',eyebrow:'CONECTAR AS ESCALAS',headline:'Da peça ao conjunto',caption:'Uma câmera conecta os níveis.',cards:['O COMPONENTE','O SISTEMA']},
 {id:'compare',layout:'compare',eyebrow:'MOSTRAR A MUDANÇA',headline:'Comparar para explicar',caption:'Valores reais exigem fontes e unidades.',cards:['ANTES','DEPOIS']}
].map(s=>({...s,layout:s.layout as SceneLayout,durationInFrames:180}))});
