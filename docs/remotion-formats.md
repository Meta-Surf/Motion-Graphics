# Adaptar motion graphics para 9:16 e 16:9

O novo `AiVideo` registra uma composição única; `calculateMetadata` escolhe dimensões, FPS e duração a partir das props compiladas. `VideoComposition.tsx` implementa os layouts responsivos, e `video-contract.ts` concentra as margens. Duas cópias integrais de cada template tendem a divergir; prefira componentes comuns com diferenças de layout explícitas.

## Composição e canvas

O registro real está em `Root.tsx`:

```tsx
<Composition
  id="AiVideo"
  component={VideoComposition}
  defaultProps={directedDefaults}
  durationInFrames={450}
  width={1080}
  height={1920}
  fps={30}
  calculateMetadata={({props}) => validateVideo(props)}
/>
```

`validateVideo` retorna `{width, height, fps, durationInFrames}`. Assim, o JSON horizontal produz 1920×1080 sem herdar dimensões ou duração da demo. O default serve como indicação para fornecer `--props`; seus caminhos de assets precisam ser substituídos pelo pacote compilado.

## Safe zones e AbsoluteFill

```tsx
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {safeZone} from './video-contract';

const SafeContent: React.FC<React.PropsWithChildren> = ({children}) => {
  const {width, height} = useVideoConfig();
  const safe = safeZone(width, height);
  return <AbsoluteFill style={{overflow: 'hidden'}}>
    {/* Fundo e iluminação podem alcançar as bordas do canvas. */}
    <AbsoluteFill style={{left: safe.left, top: safe.top,
      width: safe.width, height: safe.height}}>
      {children}
    </AbsoluteFill>
  </AbsoluteFill>;
};
```

As margens editoriais atuais são: vertical, 7% à esquerda, 15% à direita, 8% acima e 18% abaixo; horizontal, 5% nas laterais, 6% acima e 10% abaixo. São escolhas conservadoras do projeto, não limites oficiais imutáveis das plataformas. Confira a UI do player/dispositivo de destino. Títulos, rostos essenciais e dados devem ficar na área segura.

`AbsoluteFill` ocupa o pai posicionado mais próximo. Para uma área segura, defina `left`, `top`, `width` e `height` juntos, substituindo os 100% padrão; mudar apenas `left/top` desloca o retângulo inteiro e pode ultrapassar o canvas. Imagens de fundo usam `width/height: '100%'` e `objectFit: 'cover'`; ajuste `objectPosition` conforme a posição do sujeito. Assets que precisam aparecer inteiros usam `contain`.

## Refluir o conteúdo

```tsx
const {width, height} = useVideoConfig();
const horizontal = width > height;
const safe = safeZone(width, height);
const titleWidth = horizontal ? safe.width * .43 : safe.width;
const panelWidth = horizontal ? safe.width * .53 : safe.width;
const panelHeight = horizontal ? safe.height : safe.height * .57;
```

Em 9:16, título acima e conteúdo abaixo. Em 16:9, título à esquerda e imagem/painel à direita. Ajuste quebras de linha, tamanho de fonte, extensão dos percursos e hierarquia; esticar 1080×1920 até 1920×1080 deforma a arte e compromete a leitura. O componente atual mantém a imagem ao fundo e movimenta a câmera sutilmente durante toda a cena.

## Migrar um padrão existente

Para um template novo, extraia a animação e os parâmetros semânticos para um componente compartilhado. Se a direção visual exigir dois arquivos, mantenha wrappers pequenos:

```tsx
type PatternProps = {title: string; labels: string[]};
const PatternPortrait: React.FC<PatternProps> = props =>
  <SharedPattern {...props} arrangement="stack"/>;
const PatternLandscape: React.FC<PatternProps> = props =>
  <SharedPattern {...props} arrangement="columns"/>;
const ResponsivePattern: React.FC<PatternProps> = props => {
  const {width, height} = useVideoConfig();
  return width > height ? <PatternLandscape {...props}/> : <PatternPortrait {...props}/>;
};
```

`SharedPattern` é o componente que você extrai do padrão, com a prop `arrangement` controlando a disposição. Não copie textos demonstrativos, contadores ou fontes fictícias. O estudo editorial tem conteúdo de exemplo embutido; P10–P21 precisam de props de conteúdo antes de entrarem no contrato universal.

Os seis `MotionTemplate` já reutilizados têm coordenadas internas fixas. `MotionPanel` aplica um canvas local 936×900 e `scale = min(panelWidth / 936, panelHeight / 900)`, com origem no canto superior esquerdo e reposicionamento do desenho original. Isso preserva proporções e o código atual. Para composição mais rica, substitua esse adaptador por coordenadas normalizadas por template. Em 3D, atualize também as dimensões reais de `ThreeCanvas`, o aspect ratio e a câmera quando alterar o canvas interno; escalar apenas CSS mantém a resolução interna anterior.

Ao registrar outro template, atualize os dois schemas, `templateIds`, o renderer e o system prompt. Rode os testes de contrato e faça prévias verticais/horizontais no início, meio e fim da cena. Para edição longa, teste também os frames imediatamente antes/depois de um limite de bloco: a animação deve continuar sem reiniciar.
