# Direção por JSON, Shorts e vídeos longos

O fluxo `AiVideo` aceita Shorts 9:16 de **15–180 s** e vídeos 16:9 de **480–1800 s**. A duração é medida nos WAVs, arredondada para frames inteiros; estimativas de palavras não decidem a duração final. As composições e estudos anteriores continuam registrados no Remotion.

## Arquivos e contratos

| Arquivo | Responsabilidade |
| --- | --- |
| `schemas/video-director.schema.json` | Contrato de entrada da IA, JSON Schema 2020-12, sem campos extras |
| `remotion/src/video-contract.ts` | Interfaces da direção, props compiladas, formatos, safe zones e validação do renderer |
| `examples/video-director.short.json` | Exemplo; substituir `voice.profile_id` pelo perfil aprovado no DACOL |
| `src/build_composition.py` | Fila ou API de imagem, VoiceStudio GPU/ASR, timeline e WAV contínuo |
| `schemas/composition.schema.json` | Contrato das props compiladas, separado do roteiro |
| `scripts/render_chunks.py` | Processos Remotion isolados, concat demuxer e validação técnica |
| `prompts/video-director.system.txt` | System prompt em inglês para a IA diretora |
| `docs/remotion-formats.md` | Adaptação de templates e enquadramento |

Fluxo: **diretor JSON → imagens + narração → composition.json + narration.wav → blocos MP4 → MP4 final + QA**. Remotion nunca chama os provedores. O roteiro não pode escolher comandos, executáveis, URLs de serviço ou caminhos arbitrários de saída.

## Preparação

Python 3.12+, Node 22+ e as dependências fixadas no lockfile:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r scripts/requirements-pipeline.txt
cd remotion
npm ci
cd ..
```

Nos comandos seguintes, `python` representa o Python com essas dependências instaladas. Ative a venv ou use `.venv\Scripts\python`. FFmpeg/ffprobe são procurados no PATH e, depois, no pacote compositor instalado pelo Remotion. `--ffmpeg` e `--ffprobe` permitem caminhos explícitos.

## 1. Validar o plano sem gerar assets

```powershell
python src/build_composition.py examples/video-director.short.json --validate-only
```

A IA deve receber o system prompt e o schema. IDs de cena são únicos; `template_id` deve existir no registro. `seed` é obrigatório. `duration_seconds` é opcional: se houver, o WAV deve caber nessa duração; a sobra recebe silêncio. Se não houver, vale a duração real arredondada para frames. Não use essa opção para inflar um roteiro curto até oito minutos.

Para um vídeo longo, use `video_type: "long_16_9"`, escreva narração suficiente para 8–30 minutos e divida-a em cenas editoriais curtas. O compilador soma a duração real e rejeita vídeos fora da faixa. `fps` pode ser 24, 25, 30 ou 60. A resolução final é 1080×1920 ou 1920×1080.

## 2. Imagens pela fila existente (padrão)

```powershell
python src/build_composition.py examples/video-director.short.json --image-mode queue
```

O comando escreve manifestos compatíveis com `src/process_image_queue.py`, divididos em lotes de até oito imagens. Retorna `status: awaiting_images` sem gerar voz nem props incompletas. Um comando local não inicia GitHub Actions: os manifestos precisam ser enviados à branch monitorada pelo workflow ou processados localmente com as credenciais de ambiente. Consulte `image-generation-queue.md`.

Depois da geração, baixe os artefatos preservando `output/generated/<job_id>/`, inclusive `asset-manifest.json`. Reexecute passando todos os manifestos de assets necessários:

```powershell
python src/build_composition.py examples/video-director.short.json --image-mode queue --image-manifest output/generated/JOB_ID/asset-manifest.json --output output/projects/meu-video/composition.json
```

Repita `--image-manifest` para múltiplos lotes. O compilador verifica identificação por hash, prompt, modelo, seed, dimensões e arquivo real; assets ausentes nunca causam geração paga automática. Jobs já processados não são reenfileirados: recupere seus artefatos. O workflow atual retém artefatos por sete dias, portanto arquive o pacote local completo.

Alternativa direta, com credenciais Cloudflare no ambiente:

```powershell
python src/build_composition.py examples/video-director.short.json --image-mode direct --output output/projects/meu-video/composition.json
```

Esse modo chama a API de imagem. Ambos os modos usam o `VoiceStudio.narrate()` existente, com GPU obrigatória, perfil explícito, cache de takes e verificação ASR. Configure `MOTION_VOICE_URL` ou passe `--voice-url http://DACOL:3901`; não é necessário disponibilizar credenciais à IA diretora. A narração atual é em português brasileiro.

## 3. Pacote compilado e continuidade

Os assets são copiados para `remotion/public/generated/<project_id>/<hash-do-diretor>/`. As props usam caminhos relativos a `public`, resolvidos com `staticFile()`. Preserve esse pacote junto com o JSON ao transferir para outra máquina.

Cada cena registra `fromFrame` e `durationInFrames`, sem sobreposição. Não há crossfade de falas. A montagem de áudio lê PCM em blocos e insere somente o padding necessário até a fronteira de cada cena, calculada em amostras absolutas. WAVs incompatíveis ou fala mais longa que a cena causam erro. A narração não é acelerada nem cortada.

As imagens são solicitadas em **864×1536** ou **1536×864**, proporções exatas e dimensões múltiplas de 16, e enquadradas em 1080p. Cada request combina prompt da cena, guia comum e sufixo fixo. O cache registra prompt completo, modelo, seed, dimensões reais e SHA-256. O manifesto inclui os hashes dos WAVs. Cache de imagem alterado é invalidado; os takes de voz mantêm a política do adaptador existente.

## 4. Render sequencial e concatenação

```powershell
python scripts/render_chunks.py output/projects/meu-video/composition.json --output renders/meu-video.mp4 --chunk-seconds 90 --concurrency 1 --resume
```

Use blocos entre 60 e 120 segundos. Um Short menor usa um único bloco. Cada processo recebe **as mesmas props completas** e um intervalo inclusivo `--frames=0-2699`, `--frames=2700-5399` etc. Isso conserva tempo global, offsets das cenas e estado das animações, mesmo quando um bloco termina no meio de uma cena. Somente sequências ativas são montadas pelo Remotion.

Cada bloco é H.264/yuv420p, BT.709, CRF 18, preset medium, sem áudio. O comando pede frames PNG, evitando compressão JPEG intermediária quando o renderer usa captura por imagem. O script confere número de frames, resolução, FPS, duração e compatibilidade dos parâmetros de codec/time base/extradata. O FFmpeg usa concat demuxer com `-c:v copy`: **não há nova compressão do vídeo na união**. A codificação H.264 inicial continua sendo com perdas. O WAV completo é codificado em AAC uma única vez no mux final, evitando padding AAC em cada emenda.

`--resume` reutiliza apenas blocos validados com SHA-256 correspondente; o fingerprint considera props, código Remotion, lockfile, assets e configurações do render. Arquivos incompletos são refeitos. Saídas intermediárias ficam em `.motion-chunks/`, junto à saída, para diagnóstico/retomada. O MP4 final só é publicado após validação de streams e decodificação integral. Um arquivo existente exige `--overwrite`.

`--timeout 3600` limita cada processo. `--browser-executable "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"` permite usar um Chromium instalado; sem essa opção, vale a descoberta/download padrão do Remotion. Em interrupção abrupta, pode restar `<video>.mp4.lock` ou `output/projects/<project_id>/build.lock`: confirme que o processo terminou antes de remover apenas esse lock.

Chunking limita o trabalho de cada processo e recupera memória entre processos; **não garante** ausência de OOM. Texturas grandes, 3D e concorrência ainda podem exceder memória dentro de um bloco. Comece com concorrência 1, monitore RAM/VRAM e reduza a complexidade dos assets quando necessário. O encoder desse caminho é libx264; o render AMF anterior continua disponível separadamente.

## 5. Qualidade e templates

IDs disponíveis: `photo_essay` (imagem e título) e os seis componentes existentes `layers`, `object3d`, `dataflow`, `cutaway`, `scale`, `compare`. Os seis preservam seus desenhos com um adaptador de painel proporcional, dentro de uma composição responsiva. Alguns possuem rótulos ilustrativos próprios; use-os somente quando combinarem com a narrativa. Não confunda os IDs P01–P21 do catálogo de estudos com templates prontos para este contrato: sua migração editorial exige parametrizar o conteúdo e revisar o enquadramento.

O novo fluxo não gera legendas palavra a palavra nem música/SFX. Os estudos e o renderer anterior mantêm essas funcionalidades quando existentes; uma extensão do contrato deverá incluir cues alinhados ao WAV antes de adicioná-las ao `AiVideo`.

O system prompt orienta fotografia cinematográfica e continuidade, e o compilador reaplica a direção comum a cada request. “8k detail aesthetic” descreve estilo, não resolução real. Seed e prompt não asseguram identidade de personagens por 30 minutos; o adaptador atual é text-to-image. Revise uma folha de contato e prévias de movimento; reutilize assets aprovados ou adicione suporte explícito a referências visuais quando a identidade precisar ser exata.

O `.qa.json` marca apenas checagem técnica como aprovada. Revisão visual e escuta permanecem pendentes. Consulte `visual-quality-gates.md`. `finalize_short.py` e o handoff Editonny também aceitam `--video-type long_16_9`; o padrão é `short_9_16` com limites de 15–180 s.

## Verificação sem serviços externos

```powershell
python scripts/test_pipeline.py
python scripts/test_orchestration.py
cd remotion
npm test
npm run typecheck
```

Os testes Python usam provedores falsos e WAVs locais. Exercitam schemas, limites dos dois formatos, IDs, paths, cache/fila, soma de áudio, padding e intervalos inclusivos. Os testes TypeScript verificam metadata, safe zones, registro de templates e compatibilidade dos contratos. O workflow `remotion-check.yml` executa essas verificações sem credenciais.

Verificação local em 26/10/2026: 14 testes Python e 20 testes TypeScript passaram, com typecheck aprovado. Foram renderizados dois blocos sintéticos de 60 s + 1 s, concatenados com stream copy e validados com 1464 frames a 24 fps, AAC e decodificação integral. O fluxo final corrigido também gerou um Short de 15 s com QA técnica aprovada. Prévias 1080×1920 e 1920×1080 foram inspecionadas. As correções de integração incluíram BT.709/PNG, alinhamento de Zod 4.5.4 e seleção explícita de `rawvideo`/`pcm_s16le` na checagem de decode, compatível com o FFmpeg mínimo do Remotion.

Esses ensaios usam imagens e silêncio sintéticos. Não comprovam qualidade de imagens geradas, inteligibilidade de voz, consumo de memória durante 30 minutos ou acesso aos serviços reais. A faixa de 8–30 min foi verificada nos contratos e na divisão de frames; não foi realizado um render integral de 30 min nesta validação.

Referências oficiais usadas na implementação: [render CLI e intervalos de frames](https://www.remotion.dev/docs/cli/render), [calculateMetadata](https://www.remotion.dev/docs/calculate-metadata), [concat demuxer](https://ffmpeg.org/ffmpeg-formats.html#concat), [FLUX.2 Klein 4B](https://developers.cloudflare.com/workers-ai/models/flux-2-klein-4b/).
