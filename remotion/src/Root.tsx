import React from "react";
import { Composition } from "remotion";
import { ShortComposition, ShortProps } from "./ShortComposition";
import {validateShort} from "./validate-short";
import {getMotionDemoProps} from "./motion-demo";
import { getTimelineDuration } from "./timeline";
import {ReferenceMotionStudy,LayerBreakdown} from './ReferenceMotionStudy';
import {MobileLayeredShort,MOBILE_DURATIONS,validateMobile} from './MobileLayeredShort';
import {EditorialPatternDemo} from './EditorialPatterns';
import {VideoComposition} from './VideoComposition';
import {validateVideo, type VideoCompositionProps} from './video-contract';

// The director compiler supplies real assets through --props; no API calls occur inside Remotion.
const directedDefaults: VideoCompositionProps = {
  schema_version: 1, project_id: 'director-demo', title: 'Motion', video_type: 'short_9_16',
  fps: 30, width: 1080, height: 1920, durationInFrames: 450,
  audio: 'generated/director-demo/narration.wav',
  scenes: [{id: 'scene-one', template_id: 'photo_essay', title: 'Passe o JSON compilado em --props',
    fromFrame: 0, durationInFrames: 450, image: 'generated/director-demo/image.png', labels: []}],
};

const demoProps: ShortProps = {
  title: "IA transforma a criação de vídeos",
  accentColor: "#85f7d2",
  scenes: [
    { id: "hook", durationInFrames: 360, eyebrow: "CRIAR MUDOU", headline: "A IA está entrando no estúdio", accent: "no estúdio", caption: "Ferramentas novas estão mudando como vídeos são produzidos.", layout: "hero", cards: ["IDEIA", "IMAGEM", "VÍDEO"], metric: "3 etapas", visualLabel: "NOVO FLUXO CRIATIVO" },
    { id: "workflow", durationInFrames: 360, eyebrow: "DO TEXTO À CENA", headline: "Um prompt pode iniciar o processo", accent: "iniciar", caption: "O criador descreve a cena, escolhe referências e ajusta o resultado.", layout: "interface", cards: ["PROMPT", "REFERÊNCIA", "AJUSTE"], metric: "1 prompt", visualLabel: "PAINEL DE CRIAÇÃO" },
    { id: "control", durationInFrames: 360, eyebrow: "A DIREÇÃO CONTINUA HUMANA", headline: "A escolha final ainda é sua", accent: "sua", caption: "A IA acelera tarefas, mas a direção e a revisão definem o resultado.", layout: "orbit", cards: ["DIREÇÃO", "REVISÃO", "AUTORIA"], metric: "VOCÊ", visualLabel: "CONTROLE CRIATIVO" }
  ]
};

export const RemotionRoot: React.FC = () => (
  <>
  <Composition id="AiVideo" component={VideoComposition} defaultProps={directedDefaults}
    durationInFrames={450} width={1080} height={1920} fps={30}
    calculateMetadata={({props}) => validateVideo(props)}/>
  <Composition
    id="AiShort"
    component={ShortComposition}
    durationInFrames={getTimelineDuration(demoProps.scenes, 12)}
    fps={30}
    width={1080}
    height={1920}
    calculateMetadata={({props})=>({durationInFrames:validateShort(props)})}
    defaultProps={demoProps}
  />
  <Composition id="MotionLibraryDemo" component={ShortComposition} durationInFrames={validateShort(getMotionDemoProps())} fps={30} width={1080} height={1920} defaultProps={getMotionDemoProps()} calculateMetadata={({props})=>({durationInFrames:validateShort(props)})}/>
  <Composition id="ReferenceMotionStudy" component={ReferenceMotionStudy} durationInFrames={466} fps={30} width={720} height={1280} defaultProps={{useReferenceText:false,brand:'Motion'}}/>
  <Composition id="LayerBreakdown" component={LayerBreakdown} durationInFrames={240} fps={30} width={1440} height={1080} defaultProps={{}}/>
  <Composition id="MobileLayeredShort" component={MobileLayeredShort} durationInFrames={1800} fps={30} width={1080} height={1920} defaultProps={{assetPrefix:'mobile-ai-20261024',durations:MOBILE_DURATIONS,captions:[]}} calculateMetadata={({props})=>({durationInFrames:validateMobile(props)})}/>
  <Composition id="EditorialPatternDemo" component={EditorialPatternDemo} durationInFrames={1080} fps={30} width={1080} height={1920} defaultProps={{audioFile:'editorial-demo/signal.wav'}}/>
  </>
);
