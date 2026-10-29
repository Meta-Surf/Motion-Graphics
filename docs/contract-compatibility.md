# Compatibilidade observada dos contratos

| Entrada | Saída/consumidor | Estado real |
|---|---|---|
| production-request v1 | planner offline | Coordena briefing, decisões, rotas e entrega; não é props |
| Gemini manifest | 21 aliases + texto/prompt | Plano apenas; sem tempos/voz/títulos/perfil/direção de arte completos |
| Gemini `--enqueue-images` | fila existente, ≤8 imagens/job | Publicação explícita após orçamento; default agora guarda somente plano |
| video-director v1 | build_composition | 7 IDs AiVideo, imagens, VoiceStudio PT e duração medida |
| production-plan v1 | compile_library_project | Seleções SQLite e WAVs aprovados por idioma → composition v1 |
| composition v1 | Remotion AiVideo | photo_essay, layers, object3d, dataflow, cutaway, scale, compare |
| composition v1 | HyperFrames bridge | photo_essay/layers; outros IDs e vídeo rejeitados |
| HTML HyperFrames independente | CLI fixada 0.8.211 | Check/render/snapshot nativos, sem equivalência pixel a pixel com Remotion |
| MP4/SRT/projeto nativo | Concat/editonny | Handoff local; importação/reabertura Concat deve ser comprovada |

Todos os 21 padrões do catálogo estão como `candidate`. Os nove P01–P09 têm
implementações de estudo em ReferenceMotionStudy/reference-patterns; P10–P21 têm
componentes em EditorialPatterns/editorial-motion. Isso permite estudos e demos;
não cria 21 slots disponíveis em AiVideo ou HyperFrames.

Não há conversor automático Gemini → video-director: precisam ser definidos IDs,
títulos, art_direction, voz/perfil, seed e bindings de template, além dos tempos
medidos. `titles` não vira `photo_essay`, `comparison` não vira `compare` e um padrão
3D não vira HTML por aproximação implícita. Migração: selecionar um componente útil,
portar isoladamente, fornecer fixtures, testar seek/fronteiras/áudio, comparar uma
amostra e registrar binding explícito antes de adicioná-lo ao schema suportado.

A fila de imagens é por lote imutável; artefatos de Actions expiram em sete dias.
Um job processado não garante que os bytes ainda existam. Arquive-os na biblioteca,
verifique hashes/proveniência e marque aprovação de licença/qualidade separadamente.
Não envie JSON de planejamento à pasta `jobs/pending` sem decisão de geração: o
workflow pode consumir cotas/custos quando a branch for publicada.

Os contratos atuais limitam AiVideo a 1080p 9:16/16:9 e durações específicas. Um
briefing válido não prova que todos esses renderers atendam qualquer corte, HDR,
VFR ou formato. Use a rota compatível e teste; não amplie claims por documentação.
