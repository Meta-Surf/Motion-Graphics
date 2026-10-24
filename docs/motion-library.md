# Biblioteca de motion

As cinco cenas anteriores continuam disponíveis. Foram acrescentadas seis variantes:

| layout | Função | Técnica |
|---|---|---|
| layers | Desmontar e remontar camadas | Perspectiva CSS e profundidade independente |
| object3d | Objeto central com materiais e iluminação | Three.js + React Three Fiber + @remotion/three |
| dataflow | Explicar entrada, processamento e saída | SVG e fluxo por caminhos |
| cutaway | Revelar estrutura interna | Máscara animada |
| scale | Componente e sistema | Mudança contínua de escala |
| compare | Comparar duas situações | Colunas parametrizadas e entrada escalonada |

`MotionLibraryDemo` é uma demonstração visual de 34 s, sem narração. `npm run preview:library` gera seis quadros para revisão. Ela demonstra técnicas, não representa um Short final nem uma visualização de dados reais.

Os materiais do chip 3D são construídos com primitivas. Modelos GLB e recortes de alta qualidade podem substituir essas peças nas próximas produções, mantendo a lógica de câmera e luz. Assets precisam de origem/licença e revisão de continuidade.

## Camadas por keyframes

Além de `from`/`to`, cada camada aceita `keyframes`, com frames crescentes e transformações x/y/scale/rotate/opacity. O easing da chave de destino pode ser linear, easeIn, easeOut ou easeInOut. Valores omitidos mantêm o estado anterior. Exemplo:

```json
{"keyframes":[{"frame":0,"y":100,"opacity":0},{"frame":24,"y":0,"opacity":1,"easing":"easeOut"},{"frame":130},{"frame":149,"opacity":0}]}
```

Movimentar uma imagem não implica mais esmaecê-la durante toda a cena. Fades são explícitos.

## Tempo e texto

A duração é calculada a partir dos props recebidos, com sobreposição de 12 frames. O renderer usa TransitionSeries/fade para evitar que o fundo opaco da próxima cena encubra a anterior antes da dissolvência.

`captions` aceita `{startFrame,endFrame,text}` na timeline global; o validador rejeita sobreposição e término após o vídeo. Timecodes devem vir da locução real. `@remotion/captions` está instalado para a evolução de importação/transcrição, mas nenhuma transcrição é feita automaticamente ao renderizar.

A marca é configurável por `brandLabel`. Numeração decorativa de cena fica desativada por padrão. Títulos e diagramas continuam no código; não devem depender de texto gerado dentro de imagens.

## Qualidade

A biblioteca precisa receber assets dedicados por produção. Não reutilize todos os templates em todos os vídeos. Selecione poucos, varie planos e reserve composições mais simples para falas densas. A demo é um catálogo técnico, não um padrão visual obrigatório.
