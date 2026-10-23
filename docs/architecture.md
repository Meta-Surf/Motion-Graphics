# Arquitetura do pipeline

## Princípio

O projeto produz Shorts independentes do tema. Cada vídeo tem um pacote próprio de roteiro, cenas, prompts, imagens, narração e render. O código reutilizável não deve carregar assets ou decisões específicas do Short anterior.

## Componentes

1. **Research**: registra assunto, data, evidências, links e ressalvas factuais.
2. **Script**: roteiro em português, CTA e estimativa de duração. A meta inicial é 35–55 segundos para deixar margem acima do mínimo de 30s.
3. **Storyboard**: cenas com `id`, `start`, `end`, `voiceover`, `visual_goal`, `image_prompt`, `motion`, `source_notes` e `asset`.
4. **Image provider**: contrato de provedor desacoplado. Deve retornar arquivos locais e metadados; nenhum token fica em JSON versionado.
5. **Voice**: gera narração no VoiceStudio/Dacol e informa duração real e parâmetros.
6. **Renderer**: compõe imagens 9:16 com movimentos suaves, elementos gráficos, texto seguro e áudio; saída inicial 1080×1920, H.264/AAC.
7. **Quality checks**: valida duração, streams, resolução, arquivos ausentes, textos fora da safe area e correspondência roteiro/legenda.

## Consistência visual

Cada vídeo define um guia de estilo antes de gerar assets: paleta, iluminação, lente/composição, nível de realismo, contraste e regras de continuidade. Gerar cenas em sequência usando referências visuais quando suportado pelo provedor. O texto legível deve ser aplicado no render, não depender de texto gerado dentro da imagem.

## GPU

Priorizar RX 7800 XT para tarefas locais compatíveis, incluindo VoiceStudio e renderização local quando aceleração e qualidade forem validadas. A geração por API ocorre no provedor remoto e não usa a GPU local. O encoder deve ser configurável e a escolha entre CPU/GPU verificada em cada máquina.
