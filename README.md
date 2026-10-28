# Motion Video Pipeline

Projeto independente para planejar, produzir e renderizar Shorts 9:16 de 15–180 segundos e vídeos 16:9 de 8–30 minutos com motion graphics, narração e imagens geradas por IA.

O [pipeline universal por JSON](docs/universal-video-pipeline.md) inclui schema para a IA diretora, integração com a fila Cloudflare e VoiceStudio GPU, props compiladas e renderização Remotion em blocos de 60–120 segundos. Veja o [exemplo de direção](examples/video-director.short.json), o [system prompt visual](prompts/video-director.system.txt) e o [guia de adaptação 16:9](docs/remotion-formats.md).

O [orquestrador Gemini](docs/gemini-orchestrator.md) transforma roteiros em texto simples em um plano de cenas com escolhas entre os 21 padrões catalogados e cria os lotes de imagem compatíveis com a fila existente.

> O vídeo de demonstração anterior não faz parte do repositório. Ele serviu como protótipo e evidenciou o principal ponto a melhorar: a arte vetorial simples não tem o nível visual desejado. Este repositório guarda o pipeline reutilizável, não um Short específico.

## Objetivo

Transformar um roteiro em um Short 9:16 de 15–180 s ou vídeo 16:9 de 480–1800 s com:

- cenas ilustradas por imagens de alta qualidade geradas por API;
- direção de arte consistente entre cenas;
- movimento de câmera e motion graphics sobre as imagens;
- narração via VoiceStudio no computador Dacol;
- legendas sincronizadas e exportação H.264/AAC para YouTube Shorts.

## Pipeline proposto

1. Pesquisar e validar o assunto e as fontes.
2. Escrever roteiro, estimar duração e dividir em cenas com timecodes.
3. Criar prompts visuais por cena e um guia de estilo comum.
4. Gerar imagens via provedor configurável, guardando prompt, modelo, dimensões e referência da imagem.
5. Revisar contato/seleção das imagens antes da montagem final.
6. Gerar narração pelo VoiceStudio no Dacol.
7. Montar imagens, movimentos (pan/zoom/parallax), gráficos, legendas e áudio.
8. Validar duração e resolução do formato escolhido, legibilidade, sincronização e qualidade.

## API de imagem

Integração inicial disponível: **Cloudflare Workers AI com FLUX.2 Klein 4B**. O adaptador em `src/providers/cloudflare_workers_ai.py` envia um prompt e salva o arquivo de imagem no formato retornado pela API; credenciais são lidas do ambiente e nunca devem ser versionadas. Veja [a configuração e os comandos](docs/cloudflare-workers-ai.md).

A chamada usa processamento remoto pela Cloudflare; não usa a GPU local. Revise a cota e os preços atuais antes de gerar lotes.

## Estrutura

- `docs/architecture.md` — arquitetura e decisões de qualidade.
- `docs/visual-quality-gates.md` — critérios para aprovar imagens e montagem.
- `docs/cloudflare-workers-ai.md` — configuração, uso e custos do provedor.
- `docs/github-actions-cloudflare.md` — uso dos secrets no Actions e transferência dos assets para o editor local.
- `src/providers/cloudflare_workers_ai.py` — adaptador de geração via Workers AI.
- `.env.example` — nomes de configuração sem segredos.

## Renderer opcional com Remotion

O repositório inclui um renderer alternativo em `remotion/` para composições dinâmicas: títulos cinéticos, painéis em primeiro plano, layouts narrativos, animações por frame e movimento de câmera. Ele é opcional; o adaptador Cloudflare, a fila de imagens e os workflows atuais continuam disponíveis. Consulte [o guia do Remotion](docs/remotion-renderer.md).

## Revisão final opcional

O [Editonny](https://github.com/soumatheusgomes/editonny) pode apoiar a revisão local pós-render e ajustes editoriais com confirmação. Adicionamos um handoff que valida o arquivo e cria um manifesto/checklist sem chamar serviços externos nem modificar a exportação original. Veja [integração e fluxo de revisão](docs/editonny-review.md).

## Execução

O fluxo `AiVideo` compila um roteiro JSON em assets, narração contínua e props renderizáveis. A geração de assets exige os serviços configurados; aprovação visual e escuta continuam sendo etapas explícitas de revisão. O adaptador de imagem também pode ser usado isoladamente.

## Geração automática sem iniciar o workflow manualmente

O workflow `.github/workflows/cloudflare-image-queue.yml` aceita manifestos JSON em `jobs/pending/`. Uma atualização da fila tenta iniciar a geração automaticamente; há também uma verificação horária como recuperação. Imagens geradas são publicadas como artefatos do GitHub Actions por 7 dias e o manifesto concluído é movido para `jobs/processed/`.

Use `src/process_image_queue.py` para validar e processar os pedidos. Cada manifesto pode solicitar de 1 a 8 imagens, com prompts de até 3.000 caracteres. As credenciais continuam somente nos secrets do repositório. Consulte `docs/image-generation-queue.md` para o formato do pedido e limites, e [o guia de credenciais e fluxo Actions → editor local](docs/github-actions-cloudflare.md).

## Motion por camadas e áudio sincronizado

O Remotion aceita múltiplos assets com movimento independente e faixas temporizadas de voz, música e efeitos, com fades e ducking em janelas marcadas. O cálculo de duração é compartilhado com a timeline para evitar frames vazios no fechamento. Consulte a documentação em docs/remotion-renderer.md, o exemplo examples/remotion-layers.example.json e execute os testes e typecheck no diretório remotion.

## Atualização de qualidade e DACOL

- [Voz GPU, inicialização e fluxo no DACOL](docs/dacol-gpu-and-production.md).
- [Biblioteca de seis novos motions e keyframes](docs/motion-library.md).
- Voz por GPU: `python src/providers/voicestudio.py --health` (porta 3901, sem fallback CPU).
- No diretório `remotion`, use `npm ci`, `npm test`, `npm run typecheck` e `npm run preview:library`.
- `npm run render:amf` exige `--voice` para uma exportação final ou `--silent-preview` para uma prévia explicitamente sem som.
- `scripts/finalize_short.py` inclui a narração e valida o MP4; o handoff Editonny agora rejeita arquivos finais sem áudio.

O desktop Windows do VoiceStudio (3900) e o serviço AMD ROCm no WSL (3901) são instalações diferentes. A produção no DACOL usa a segunda. Consulte o diagnóstico antes de reinstalar modelos.

## Estudos de referências e padrões

O primeiro estudo adiciona decomposição por frames, medidas de movimento e uma reconstrução editável com camadas independentes. Consulte [o processo e suas limitações](docs/reference-learning.md) e [o catálogo do estudo 001](motion-library/studies/001.json). Os renders `render:study` e `render:breakdown` são prévias técnicas sem áudio; os fluxos existentes de Shorts, Cloudflare e VoiceStudio permanecem disponíveis.

O [template de mobile em camadas](docs/mobile-layered-short.md) aplica esse aprendizado com aparelho 3D procedural, interface nítida, cartões independentes, arte Cloudflare em primeiro plano e narração GPU sincronizada.

O [estudo 002 — explicador editorial](docs/editorial-motion-study-002.md) adiciona 12 padrões implementados: títulos, comparação por painéis, foco semântico, contadores, listas riscadas, funções em sequência, terminal, visualização de áudio, retrato, CTA, papel iluminado e olho. O [catálogo consolidado](motion-library/catalog.json) reúne 21 padrões em dois estudos. Em `remotion`, `npm run render:editorial` gera uma prévia técnica de 36 s sem som e sem depender das imagens da referência. Os novos modelos aguardam revisão por conteúdo antes de promoção a produção.

## Biblioteca permanente

A [biblioteca SQLite/FTS5](docs/asset-library.md) importa recursos sem mover os originais, oferece busca local e salva seleções por cena. Os assets aprovados alimentam os renderers pelo mesmo contrato de composição.

## HyperFrames local

O renderer [HyperFrames](docs/hyperframes.md) compartilha o contrato de composição e os assets da biblioteca local. Inclui CLI 0.8.211 fixada, perfil visual, legendas por timestamps, modelos locais verificados e seleção explícita --renderer hyperframes. Remotion e VoiceStudio permanecem disponíveis. Veja a [validação reproduzível](docs/hyperframes-validation.md).
