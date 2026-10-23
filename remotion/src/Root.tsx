import React from "react";
import { Composition } from "remotion";
import { ShortComposition, ShortProps } from "./ShortComposition";

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
  <Composition
    id="AiShort"
    component={ShortComposition}
    durationInFrames={demoProps.scenes.reduce((sum, scene) => sum + scene.durationInFrames, 0)}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={demoProps}
  />
);
