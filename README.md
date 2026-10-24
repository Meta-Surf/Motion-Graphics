# Shorts Motion Pipeline

Projeto independente para planejar, produzir e renderizar Shorts verticais com motion graphics, narração e imagens geradas por IA.

> O vídeo de demonstração anterior não faz parte do repositório. Ele serviu como protótipo e evidenciou o principal ponto a melhorar: a arte vetorial simples não tem o nível visual desejado. Este repositório guarda o pipeline reutilizável, não um Short específico.

## Objetivo

Transformar um roteiro de pelo menos 30 segundos em um Short 9:16 com:

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
8. Validar duração mínima de 30s, enquadramento 9:16, legibilidade e qualidade.

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

O pipeline completo de storyboard, narração e render ainda está em desenvolvimento. O adaptador de imagem pode ser usado isoladamente conforme a documentação do provedor.

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
