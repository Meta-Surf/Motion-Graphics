# Estudo 002 — explicador editorial em camadas

Referência: `Os caras clonaram o ElevenLabs (VoiceStudio).mp4`. Este estudo amplia a biblioteca com uma família visual clara, tipográfica e orientada a interfaces. Os nove padrões do estudo 001 continuam disponíveis.

## Resultado registrado

- 3.281 frames decodificados e respectivos timestamps conferidos; 720×1280, 60 fps.
- 54,683333 s de imagem; contêiner de 54,769320 s. O primeiro PTS de vídeo é 0,016667 s.
- 16 blocos semânticos anotados e 12 padrões novos, P10–P21.
- Catálogo consolidado: **21 padrões em dois estudos**.
- Protótipo original de 36 s, 1080×1920 a 30 fps, sem áudio de saída: `EditorialPatternDemo`.
- Typecheck, 16 testes TypeScript, quatro testes de pipeline e decodificação integral da prévia concluídos.

Fonte, hash, evidências e limitações: [estudo 002](../motion-library/studies/002.json). Índice: [catálogo](../motion-library/catalog.json). Frames, áudio e rostos da referência ficam fora do Git.

**Aprendizado aqui significa receitas e componentes persistentes, com evidências. Não houve treinamento de pesos, recuperação do projeto original nem aprovação de equivalência visual.**

## Como a montagem conduz o olhar

A base persiste entre as cenas: papel claro, grade fina e faixas de sombra suaves. Ela dá continuidade enquanto a informação muda. O título tem uma frase curta em sans pesada, uma palavra coral e um apoio em serifada itálica. O elemento central entra depois: diagrama, cartão, gráfico, terminal ou símbolo. Etiquetas completam a ideia com atraso.

As técnicas mais úteis são a troca do grupo por um indivíduo, as conexões entre painéis, o risco progressivo sobre uma lista e a alternância de interfaces no mesmo eixo. A profundidade vem de sombras e perspectiva moderada; os pixels não permitem concluir que houve modelagem 3D ou identificar o aplicativo usado.

## Decomposição temporal

Frames usam `[início, fim)`, relativos ao primeiro frame visual. Tempos arredondados; os limites são anotações semânticas com incerteza estimada de ±6 frames (0,1 s), não cortes ou keyframes recuperados.

| Bloco | Frames | Tempo em segundos | Construção observada |
|---|---|---|---|
| B01 | 0–314 | 0,00–5,23 | Título, dois painéis, conexões e preenchimento de linhas |
| B02 | 314–430 | 5,23–7,17 | Grupo de pessoas recebe um X progressivo |
| B03 | 430–606 | 7,17–10,10 | Um indivíduo ganha escala e cor; grupo perde presença |
| B04 | 606–862 | 10,10–14,37 | Contador, símbolo e traçado de gráfico |
| B05 | 862–1033 | 14,37–17,22 | Produto em notebook, selo e legenda |
| B06 | 1033–1266 | 17,22–21,10 | Linhas de custo riscadas e revelação de valor |
| B07 | 1266–1443 | 21,10–24,05 | Dois cartões de produto e sinal de relação |
| B08 | 1443–1520 | 24,05–25,33 | Primeira função e interface escura |
| B09 | 1520–1662 | 25,33–27,70 | Segunda função, interface e pílulas de idioma |
| B10 | 1662–1746 | 27,70–29,10 | Livro, waveform e legenda |
| B11 | 1746–2067 | 29,10–34,45 | Número crescente e grade de motores |
| B12 | 2067–2431 | 34,45–40,52 | Terminal com digitação e etiqueta de conclusão |
| B13 | 2431–2561 | 40,52–42,68 | Olho, íris e pausa de atenção |
| B14 | 2561–2767 | 42,68–46,12 | Microfone, barras radiais e selo |
| B15 | 2767–3000 | 46,12–50,00 | Retrato circular, waveform e identificação |
| B16 | 3000–3281 | 50,00–54,68 | Campo com palavra digitada, seta e comentário |

## Pilha de camadas reconstruída

| Ordem, do fundo à frente | Responsabilidade | Tratamento reutilizável |
|---|---|---|
| 1. Papel | Cor e textura discretas | CSS; textura raster opcional |
| 2. Grade | Estrutura espacial sutil | Gradientes ou SVG, sem imagem com texto |
| 3. Luz e sombra | Volume e continuidade | Faixas desfocadas com movimento lento |
| 4. Título | Ideia principal e palavra-chave | HTML/SVG; entrada curta e pausa de leitura |
| 5. Sujeito | Interface, diagrama, símbolo ou objeto | Grupo com transformações próprias |
| 6. Apoio | Selo, contador, conexão ou legenda | Entrada atrasada e movimento localizado |
| 7. Identificação | Fonte, contexto e chamada | Contraste e área segura revisados no destino |

Evitar mover toda a composição continuamente. O próximo elemento deve entrar quando acrescenta uma informação. O fundo pode permanecer estável durante uma troca de conteúdo; isso preserva orientação e reduz o custo de render.

## Receitas implementadas

Tempos abaixo são **decisões do protótipo**, em segundos locais, e não medidas das curvas originais. O demonstrador reserva 3 s por padrão; um Short narrado deve usar os tempos da voz. `editorialPhase` usa smoothstep limitado ao intervalo. Não converter frames de 60 fps diretamente em frames de 30 fps: preservar segundos.

| ID | Componente / receita | Uso e limites |
|---|---|---|
| P10 | `EditorialHeader`: entrada em 0–0,30 s; palavra coral, apoio itálico e selo | Hierarquia. Fonte original não identificada; o protótipo usa Arial/Georgia |
| P11 | `LinkedPanelComparison`: painéis separados, curvas pontilhadas e linhas em sequência | Explicar relações; não afirmar equivalência de produtos sem pesquisa |
| P12 | `SemanticFocus`: grupo, X desenhado, grupo atenuado e indivíduo ampliado | Correção narrativa; preservar o referente entre os estados |
| P13 | `EvidenceMetric`: contador e linha desenhada em 0,45–2,25 s | Demonstração marcada como ilustrativa; dado verificado exige fonte e data. A curva de exemplo não representa uma série factual |
| P14 | `StrikeReveal`: riscos com atraso de 0,24 s; resultado em 1,55–2 s | Simplificar uma lista; o exemplo termina em CLAREZA, sem herdar alegações de preço |
| P15 | `CapabilityPager`: quatro estados a cada 0,65 s no demo | Uma função por enquadramento. Na produção, trocar rótulos, conteúdo e duração conforme a narração |
| P16 | `TypedTerminal`: texto em 0,30–2,40 s; selo após 2,20 s | Mostrar um processo. Apenas desenha texto; não executa comandos |
| P17 | `AudioReactorFromFile`, radial: 64 barras, ganho e suavização | Entrada de áudio real via `useAudioData`/`visualizeAudio`; ausência de entrada mantém níveis em repouso |
| P18 | `AudioReactor`, linear: avatar circular e 64 barras | O demo usa avatar IA; não reutiliza rosto nem voz da referência. Uma foto real exige um asset próprio |
| P19 | `KeywordCTA`: digitação em 0,65–1,70 s; resposta em 1,80–2,20 s | Uma ação explícita. Não configura DM nem entrega automática |
| P20 | `SoftPaperStage`: grade, sombras lentas e conteúdo independente | Profundidade 2,5D econômica; reduzir sombras se perderem contraste |
| P21 | `EyeAttention`: abertura em 0,10–0,65 s, breve piscar e deslocamento de íris | Pausa antes de uma revelação; manter breve |

As barras possuem um comprimento mínimo gráfico em repouso. Esse traço de base não significa que exista sinal. O wrapper de áudio repete o arquivo no demonstrador; numa produção narrada, sincronizar a faixa local e impedir repetição além do trecho correspondente.

## Áudio: o que foi e não foi determinado

Foi extraída uma transcrição automática de 146 palavras, com timestamps, usando faster-whisper small int8. Ela apoia a localização dos blocos e precisa de revisão antes de virar legenda final. As marcas visíveis ajudam a corrigir nomes que o ASR transcreveu de forma imprecisa.

Na janela radial de 43,2–45,8 s, a correlação entre área rosa das barras e RMS de áudio foi aproximadamente 0,30 sem deslocamento, chegando a 0,45 em um deslocamento de cinco frames. É associação moderada: não revela o analisador, suavização, atraso ou sinal original. Não foi isolada uma trilha de efeitos sonoros confiável.

Nos nossos Shorts: finalizar a voz GPU primeiro, alinhar frases sem aceleração para caber, derivar o movimento dessa mesma faixa e acrescentar efeitos pontuais somente após ouvir a montagem. A prévia dos padrões usa um sinal de teste determinístico para analisar movimento e é exportada **sem som**. Não contém dublagem ou voz clonada.

## Geração de imagens e integração

- **Código:** títulos, palavras, números, gráficos, conexões, barras, ícones geométricos e interfaces nítidas. Texto gerado dentro de imagem dificulta correções e animação por camada.
- **Cloudflare, quando útil:** retratos ilustrativos, objetos, texturas e elementos orgânicos. Gerar fundo e sujeito separadamente quando precisarem de movimento independente; revisar bordas, recorte e consistência antes de compor.
- **Profundidade:** combinar essas camadas editoriais com o rig 3D do estudo 001 quando o assunto pedir objeto físico. Não repetir uma rotação de celular em todos os blocos.
- **Áudio:** manter o VoiceStudio GPU como fluxo existente; o estudo não altera sua instalação nem exige reinstalação.

## Executar e integrar

Na raiz do projeto, com FFmpeg/FFprobe e as dependências de `scripts/requirements-analysis.txt`:

```bash
python scripts/analyze_motion_reference.py referencia.mp4 --out review/estudo-002 --contact-step 0.25
```

O analisador v2 usa os PTS de cada frame, registra frames semelhantes e gera folhas de contato paginadas. `--no-frame-files` evita gravar cada JPEG quando apenas medidas e folhas forem necessárias. Picos de diferença são candidatos a mudanças visuais, não cortes garantidos.

No diretório `remotion`:

```bash
npm ci
npm test
npm run typecheck
npm run render:editorial
```

O último comando gera o pequeno sinal de teste local e renderiza `renders/editorial-patterns.mp4`. Nenhuma mídia da referência é necessária. No Studio, selecionar `EditorialPatternDemo` para inspecionar os 12 exemplos. Os componentes recebem tempo local; `AudioReactorFromFile` também recebe a faixa, frame e fps.

## Avaliação e promoção

O render de 36 s foi concluído e as 12 imagens representativas foram revisadas: não foram observados cortes de texto ou sobreposições graves nesses enquadramentos. A decodificação integral confirmou 1.080 frames a 30 fps. Isso valida o protótipo; não é uma nota de semelhança nem revisão de áudio final.

Os padrões permanecem `candidate-prototype`. Antes de usá-los num Short: trocar conteúdo, ajustar tempo à narração, revisar todas as transições em reprodução, verificar área segura do YouTube e ouvir a exportação completa. A combinação original de fonte, easing, sombras e materiais continua desconhecida. Alegações do vídeo sobre estrelas, idiomas, gratuidade e recursos não foram verificadas nem adotadas como fatos do projeto.
