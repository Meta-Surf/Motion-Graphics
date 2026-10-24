# Critérios de qualidade visual

## Antes de renderizar

- Cada cena tem uma imagem própria, nítida e pertinente à fala.
- Imagens mantêm paleta, iluminação e linguagem visual coerentes.
- Evitar cartões genéricos, ícones simples ou a mesma tela repetida como substitutos de imagens.
- Aprovar uma folha de contato/preview das cenas antes do render integral.
- Usar títulos curtos; evitar números ou rótulos decorativos sem função narrativa.

## Movimento e composição

- 9:16 com área segura para interface do Shorts e legendas.
- Pan/zoom/parallax sutis, sem aparência de slideshow parado.
- Usar motion graphics em primeiro plano para reforçar a narração: títulos, relações, dados, interfaces ou etapas.
- Alternar cenas com e sem overlays para evitar excesso de cartões e interfaces.
- Alternar planos e composição para sustentar ritmo sem transições excessivas.
- Legendas com contraste alto e no máximo 2–3 linhas legíveis em telefone.
- Não cobrir detalhes visuais importantes com legendas ou UI.

## Revisão final

- Conferir abertura, transições de cena, cenas com texto e fechamento.
- Confirmar que toda afirmação acompanha a narração e fontes revisadas.
- Duração mínima: 30 segundos; alvo recomendado: 35–55 segundos.
- Verificar 1080×1920, H.264/AAC, áudio audível e ausência de quadros pretos ou imagens quebradas.


## Assets em camadas e áudio

- Cada imagem deve declarar sua função (fundo, foreground ou overlay) e manter prompt, provedor/modelo, dimensão, seed quando houver, cena, licença/origem e expectativa de alpha no manifesto.
- Confirme o canal alpha no arquivo final; a solicitação por prompt não garante transparência.
- Mapeie mudanças visuais e palavras destacadas aos timecodes da narração. Use faixas separadas para voz, música e efeitos; marque as janelas de ducking no roteiro.
- Confira o último frame, a última fala e o fim das faixas para evitar composição vazia ou áudio cortado.
- Meça render FPS, duração, CPU/GPU e encoder no Dacol. Aceleração do encoder não prova que o Chromium renderizou os frames na GPU.
