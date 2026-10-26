# Mobile em camadas: aplicação do estudo 001

O template `MobileLayeredShort` aplica o aprendizado da decomposição a uma produção original de aproximadamente 60 segundos. Os arquivos do vídeo de referência não são usados: aparelho e interface são construídos em código, e a arte é gerada pelo Cloudflare.

## Estrutura visual

- Aparelho 3D procedural com corpo, borda, frente, verso, lentes, botões e vidro. Materiais e iluminação são calculados pelo Three.js; a forma se mantém nos giros.
- Tela de 1024×2200 pixels desenhada em Canvas com texto real, independente das imagens geradas.
- Mensagens, agenda e mapas em planos 3D distintos; a entrada, a elevação e a rotação dos cartões são escalonadas.
- Tela separada do corpo para mostrar a ideia de processamento local.
- Núcleo, nuvem e emblema de privacidade como recortes independentes; imagens de café e paisagem funcionam dentro da interface ou como cartão em primeiro plano.
- Tipografia cinética e legendas curtas derivadas de timestamps da narração.

Componentes: `src/MobileDevice3D.tsx`, `src/MobileLayeredShort.tsx` e `src/mobile-timeline.ts`, dentro de `remotion`.

## Assets necessários

Coloque os assets aprovados em `remotion/public/<assetPrefix>/`. Para o piloto, o prefixo é `mobile-ai-20261024`, ignorado pelo Git.

| Arquivo | Uso |
|---|---|
| studio-empty.jpg | Ambiente de estúdio vazio |
| city-empty.jpg | Ambiente urbano desfocado |
| neural-wallpaper.jpg | Textura da tela |
| cafe-photo.jpg | Imagem dentro da interface |
| mountain-photo.jpg | Cartão de entendimento visual |
| ai-core.png | Núcleo em primeiro plano, com alpha |
| cloud-node.png | Nuvem em primeiro plano, com alpha |
| privacy-shield.png | Destaque de controle e privacidade |

No piloto, os primeiros dois fundos vieram com dispositivos embutidos. Foram rejeitados e substituídos por ambientes vazios. Não deixe o modelo do aparelho em cima de outro aparelho gerado no fundo.

Os três foregrounds foram gerados sobre preto. `scripts/prepare_mobile_assets.py`, com Pillow, cria uma máscara por contorno, preserva o interior escuro, suaviza a borda e recorta a área útil. Esse processo é adequado a esses assets revisados; não é segmentação universal. A existência do canal alpha é verificada tecnicamente e a silhueta precisa de revisão visual.

```bash
python -m pip install Pillow==12.0.0
python scripts/prepare_mobile_assets.py --base caminho/assets/original --output remotion/public/mobile-ai-20261024
```

O script de preparação do piloto espera as duas pastas de jobs `mobile-ai-layered-short-20261024` e `mobile-ai-empty-backgrounds-20261024`. Para outros episódios, adapte a seleção de arquivos; a técnica de máscara permanece reutilizável.

## Configuração de montagem

O JSON local contém `assetPrefix`, nove durações em frames e legendas globais. A soma deve ficar entre 900 e 1800 frames, a 30 fps. Legendas vazias, sobrepostas ou fora do vídeo são rejeitadas.

```json
{
  "assetPrefix": "mobile-ai-20261024",
  "durations": [180,210,240,165,339,180,141,192,153],
  "captions": [],
  "motionBlur": true
}
```

```bash
cd remotion
npx remotion render src/index.ts MobileLayeredShort renders/mobile-silent.mp4 --props=caminho/props.json --gl=angle --crf=17
```

Esse comando renderiza a imagem. Inclua a mixagem aprovada depois com `scripts/finalize_short.py`; preserve sempre voz, música e mixagem como arquivos separados.

## Voz e tempo

O piloto usa VoiceStudio GPU na porta 3901, perfil masculino aprovado, 32 passos e velocidade 1.0. Doze takes passaram pela transcrição individual. A voz ocupa 48,48 s; pausas e tempo de leitura completam a linha de 60 s. Não houve aceleração nem corte para fazer a voz caber. A última fala termina em 58,83 s, deixando margem no encerramento.

O arquivo alinhado também foi transcrito: correspondência normalizada 1.0 com o roteiro. Isso verifica o conteúdo reconhecido, não certifica timbre ou aprovação de escuta. Uma base puramente tonal, sem geradores de ruído, fica reduzida durante a voz.

## Desfoque e hardware

O teste com `HtmlInCanvasMotionBlur` falhou com o conteúdo 3D: ausência de paint record. Ele não foi usado na produção. `CameraMotionBlur`, com três amostras e shutter de 120 graus, foi testado nas partes rápidas. A diferença média nos pixels do cabeçalho estático ficou abaixo de um nível por canal no teste de comparação. Esse resultado não dispensa inspeção em outros projetos, pois a técnica pode afetar cores.

No DACOL, o Chrome confirmou Canvas, Compositing, Rasterization, WebGL e WebGPU acelerados. A RX 7800 XT foi usada pela voz e pelo renderer.

Uma amostra de quatro segundos comparou os encoders contra os mesmos frames:

| Encoder | Ajuste | Tempo de encode | SSIM |
|---|---|---:|---:|
| libx264 | slow / CRF 17 | 2,377 s | 0,994258 |
| h264_amf | quality / QP I16 P18 | 1,158 s | 0,994165 |

A diferença é pequena. O piloto selecionou libx264 pela medida ligeiramente maior; não se afirma diferença visual perceptível com base apenas nesse número. O processamento 3D permanece acelerado por GPU. O render dos 120 frames levou 12,728 s.

## Revisão antes de publicar

1. Conferir cenário e fonte de cada afirmação; separar tendências de disponibilidade presente.
2. Conferir os nove enquadramentos, entrada dos cartões, máscaras, texto e área das legendas.
3. Ouvir voz e mixagem completas, incluindo a última frase; verificar loudness e true peak.
4. Decodificar todo o MP4 e verificar 1800 frames, 1080×1920, H.264/AAC e 60 s.

O tema do piloto é a evolução de IA em smartphones: recursos atuais, ações entre aplicativos, processamento local/nuvem e controle do usuário. Interfaces são ilustrativas. A disponibilidade varia por modelo, idioma e região, sem promessa de funcionamento universal ou de prazo.
