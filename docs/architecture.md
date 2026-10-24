# Arquitetura do pipeline

## Princípio

O projeto produz Shorts independentes do tema. Cada vídeo tem um pacote próprio de roteiro, cenas, prompts, imagens, narração e render. O código reutilizável não deve carregar assets ou decisões específicas do Short anterior.

## Componentes

1. **Research**: registra assunto, data, evidências, links e ressalvas factuais.
2. **Script**: roteiro em português, CTA e estimativa de duração. A meta inicial é 35–55 segundos para deixar margem acima do mínimo de 30s.
3. **Storyboard**: cenas com `id`, `start`, `end`, `voiceover`, `visual_goal`, `image_prompt`, `motion`, `source_notes` e `asset`.
4. **Image provider**: contrato de provedor desacoplado. Deve retornar arquivos locais e metadados; nenhum token fica em JSON versionado.
5. **Voice**: gera narração no VoiceStudio/Dacol e informa duração real e parâmetros.
6. **Renderer**: o Python existente continua preservado; o Remotion (`remotion/`) oferece composição 9:16 por frame, movimento de câmera, layouts em primeiro plano e títulos/legendas cinéticos. Saída alvo 1080×1920, H.264/AAC. A escolha do renderer deve seguir o storyboard e qualidade visual.
7. **Quality checks**: valida duração, streams, resolução, arquivos ausentes, textos fora da safe area e correspondência roteiro/legenda.
8. **Final review**: handoff local opcional ao Editonny depois do render. `scripts/prepare_editonny_review.py` valida requisitos técnicos básicos, copia o MP4 e contexto selecionado para revisão e grava checklist. Não instala nem invoca Editonny e não envia mídia.

## Consistência visual e camadas

Cada vídeo define um guia de estilo antes de gerar assets: paleta, iluminação, lente/composição, nível de realismo, contraste e regras de continuidade. Gerar cenas em sequência usando referências visuais quando suportado pelo provedor. O texto legível deve ser aplicado no render, não depender de texto gerado dentro das imagens Cloudflare.

A geração atual fornece principalmente fundos de cena. A evolução visual recomendada é ampliar os manifestos para assets específicos de motion graphics: PNGs com transparência para sujeitos/objetos em primeiro plano, ícones, texturas e componentes ilustrativos. Metadados por asset devem associar prompt, modelo/provedor, dimensão, canal alpha, licença/origem, seed quando disponível, cena e camada Remotion. Isso permite animação independente e parallax sem tornar a imagem de fundo o único elemento visual.

## GPU

Priorizar RX 7800 XT para tarefas locais compatíveis, incluindo VoiceStudio e renderização local quando aceleração e qualidade forem validadas. A geração por API ocorre no provedor remoto e não usa a GPU local. O encoder deve ser configurável e a escolha entre CPU/GPU verificada em cada máquina.

## Renderers

A demo de referência está no diretório `remotion/`. Cada cena escolhe um layout narrativo e declara duração, texto, cartões e imagem opcional. O componente usa springs e interpolação por frame para animar entradas, deriva de câmera, elementos orbitais, previews de interface e legendas. Veja [o guia de renderização](remotion-renderer.md).
