# Aprendizado com referências — estudo 001

## O que foi executado

Referência enviada: `1000599486.mp4`. SHA-256:
`7970a3bf1623d939b723dbc17fe60c408c98f04e60aedee891e86e6e61e457b6`.

Foram decodificados **466 frames**, 720×1280, 30 fps, 15,533333 s de imagem.
O contêiner original tem 15,600952 s porque o áudio se estende além da imagem.

1. Extração de todos os frames, folhas de contato, luminância, bordas, fluxo óptico e transformações afins dominantes.
2. Revisão visual dos cinco blocos e de enquadramentos representativos.
3. Retificação da tela no frame 33 e separação de recortes visíveis: avatar, três cartões e assinatura final.
4. Reconstrução Remotion de 466 frames com corpo, faces, interface, cartões, avatar, anéis, tipografia e encerramento independentes.
5. Revisão e segunda versão: correção de avatar duplicado, corte da marca, escala tipográfica, enquadramentos e rotação dos cartões.
6. Render de uma variante com texto sobre criação por IA e interface procedural própria, sem os arquivos da referência. Esse teste demonstra troca de conteúdo; não equivale à aprovação de um novo Short.

Os arquivos pessoais e derivados do vídeo ficam fora do Git. O repositório contém as ferramentas, o catálogo, as medidas resumidas e os componentes.

## Evidência e hipótese

| Informação | Classificação |
|---|---|
| Frames, resolução e intervalos de cenas | Medido ou observado |
| Texto e elementos visíveis | Observado; transcrição visual revisada |
| Profundidade, curvas, câmera e desfoque do projeto original | Não recuperados |
| Hierarquia de camadas e parâmetros desta reconstrução | Hipótese de montagem |
| Equivalência visual à referência | Parcial, ainda não aprovada |
| Variante com conteúdo próprio | Render técnico concluído |

**Este aprendizado consiste em receitas, componentes e evidências persistentes. Não houve treinamento de pesos de um modelo.**

## Blocos observados

Intervalos de frames usam `[início, fim)`: o frame final não pertence ao intervalo.

| Frames | Tempo | Técnica |
|---|---|---|
| 0–129 | 0–4,333 s | Celular, giro, interface separada e aproximações |
| 130–193 | 4,333–6,467 s | Objeto azul com espessura, giro e texto ao redor |
| 194–277 | 6,467–9,267 s | Tipografia clara, reenquadramentos e íris |
| 278–392 | 9,267–13,100 s | Tipografia colorida, brilho e barras em primeiro plano |
| 393–465 | 13,100–15,533 s | Resolução do desfoque e assinatura |

O detector automático encontrou 11 picos de diferença visual na referência. Vários são movimento acelerado dentro da cena. A revisão manual, e não o limiar de pixels, definiu os cinco blocos.

## Como reproduzir o estudo

Na raiz do projeto, crie um ambiente Python separado e instale `scripts/requirements-analysis.txt`. FFmpeg e FFprobe precisam estar no PATH. Execute:

```bash
python scripts/analyze_motion_reference.py caminho/referencia.mp4 --out review/estudo-001
cd remotion
npm ci
npm run render:study
npm run render:breakdown
```

Os dois renders padrão usam interface e texto procedurais próprios e são **prévias sem áudio**. Não dependem do material enviado. Não são exportações finais de Shorts e não passam pelo finalizador que exige 30–60 s.

Para recriar a versão de estudo com os recortes, coloque os PNGs do pacote de análise em `remotion/public/reference-study-1000599486/` e forneça um JSON local:

```json
{"assetPrefix":"reference-study-1000599486","useReferenceText":true,"brand":"Slate"}
```

```bash
npx remotion render src/index.ts ReferenceMotionStudy renders/estudo-local.mp4 --props=caminho/props.json
```

Não publique esse arquivo como um Short original do canal. Ele é uma reconstrução técnica do material de referência, com recortes e texto desse material.

## Componentes reutilizáveis

`ReferenceMotionStudy.tsx` exporta:

- `LayeredDeviceRig`: recebe `frame`, `prefix` opcional e uma lista opcional de poses. Sem prefixo, desenha uma interface própria. Corpo, tela, cartões e avatar têm transformações separadas.
- `KineticWord`: recebe frame, início, posição, tamanho, cor e texto. Pode ser combinado com uma câmera de composição e cues próprios.
- `ReferenceMotionStudy`: montagem completa deste estudo, com fases fixas da referência.
- `LayerBreakdown`: visualização técnica das camadas reconstruídas.

`reference-patterns.ts` contém a sequência e as curvas **inferidas da reconstrução**, sem apresentá-las como curvas originais. O catálogo em `motion-library/studies/001.json` guarda nove técnicas candidatas e as limitações de cada uma.

## Avaliação e próximos requisitos

Foram produzidas duas iterações e comparação sincronizada. A reconstrução confirma que podemos montar e reutilizar a lógica de profundidade. **Ainda não reproduz o acabamento nem todas as trajetórias da referência.**

Faltam materiais e reflexos mais ricos, câmera calibrada por âncoras, continuidade de velocidade, desfoque temporal, oclusões mais precisas e ajuste de cada reenquadramento tipográfico. A tela usada no estudo tem aproximadamente 250 pixels de largura no frame de origem; recortá-la não cria detalhe novo.

O primeiro render tinha pouco movimento tipográfico. Isso foi corrigido em parte com zoom progressivo, letras maiores e rotação dos cartões na segunda versão. A atividade óptica continua sendo uma medida de diagnóstico, não uma nota de qualidade: brilho, área ocupada e contraste alteram seus valores.

Antes de promover uma técnica a modelo de produção:

1. Recriar assets em alta resolução; texto/interface em SVG ou HTML, objetos com recorte limpo ou geometria adequada.
2. Substituir assunto, textos e proporções; validar que a montagem não depende da marca ou dos pixels da referência.
3. Revisar enquadramento, legibilidade, oclusões e continuidade em velocidade real.
4. Em um Short narrado, travar primeiro a voz GPU, alinhar os cues e adicionar apenas efeitos sonoros necessários.
5. Revisar visual e áudio separadamente e registrar aprovação. Fluxo óptico e ASR não substituem essa revisão.

REA não foi instalado para esse estudo: o trabalho usa pixels de um MP4, sem código-fonte de animação para investigar.

## Estudo seguinte

O [estudo 002](editorial-motion-study-002.md) amplia a biblioteca com composição editorial clara, interfaces, conexões e visualização de áudio. O analisador agora registra PTS individuais e folhas paginadas; os nove padrões e a reconstrução do estudo 001 continuam disponíveis. Consulte o [catálogo consolidado](../motion-library/catalog.json).
