# Renderer opcional com Remotion

O Remotion entra como segundo renderer do projeto. Ele não substitui o pipeline Cloudflare, a fila automática nem os scripts existentes. A proposta é dar controle temporal por frame e colocar elementos gráficos em primeiro plano ligados à narrativa.

## O que a composição adiciona

- Imagem com movimento de câmera (zoom e deriva lateral).
- Títulos cinéticos com palavra destacada, entrata escalonada e legendas animadas.
- Elementos em primeiro plano que se movem independentemente do fundo.
- Cinco layouts reutilizáveis: hero, interface, timeline, stat e orbit.
- Painéis, cartões, progressos, formas orbitais e sinalização de capítulo.
- Composição vertical 1080×1920 a 30 fps com dados de storyboard por cena.
- Demo funcional com fundos abstratos para revisar hierarquia e ritmo antes de conectar imagens.

O foco é mudar a função da imagem: ela sustenta a cena enquanto painéis, relações, títulos e informações ocupam o primeiro plano. O texto legível deve ser aplicado no render, não gerado dentro das imagens Cloudflare.

## Instalar e abrir o Studio

Requer Node.js e npm. As dependências estão fixadas em remotion/package.json.

```bash
cd remotion
npm install
npm run studio
```

Abra a composição AiShort. Ela tem três cenas de demonstração e funciona sem imagens.

## Renderizar

```bash
cd remotion
npm run render:demo
```

A saída vai para remotion/renders/ai-short-demo.mp4. Essa pasta é ignorada pelo Git.

## Usar imagens e storyboard

Passe os dados de cada cena ao componente ShortComposition:

```ts
{
  title: "Título do Short",
  accentColor: "#85f7d2",
  scenes: [{
    id: "scene-01",
    durationInFrames: 120,
    image: "https://example.com/scene-01.jpg",
    eyebrow: "ABERTURA",
    headline: "Uma ideia curta e clara",
    accent: "clara",
    caption: "Texto sincronizado com a narração.",
    layout: "hero",
    cards: ["PESQUISA", "MODELO", "RESULTADO"],
    metric: "1 ideia",
    visualLabel: "FLUXO DE CRIAÇÃO"
  }]
}
```

Para assets locais, salve as imagens sob remotion/public/ e use staticFile("images/scene-01.jpg") ao montar os props. durationInFrames é por cena; a 30 fps, 120 frames equivalem a 4 segundos. A soma das cenas define a duração. Áudio e legendas com timecodes reais podem ser conectados na próxima etapa.

Use cada layout pela intenção narrativa: hero para promessa, interface para fluxo, timeline para etapas, stat para dado e orbit para relações. Um Short de 35–55 segundos normalmente precisa de 7–12 cenas breves, com algumas cenas mais limpas sem cartões.

## Renderização e licença

O Remotion produz cada frame via React e Chromium. A codificação acelerada depende do sistema e do encoder disponível; ter uma GPU não garante aceleração de todo o render. Teste qualidade e tempo na máquina final antes de fixar o encoder.

Confira os termos atuais e a elegibilidade antes de automatizar renders ou operar comercialmente: [licença oficial](https://www.remotion.dev/license) e [FAQ](https://www.remotion.dev/docs/license).
