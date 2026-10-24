# Camadas de motion, continuidade e áudio

Este guia amplia as possibilidades sem fixar um estilo visual. Planeje camadas e movimento conforme a história de cada Short.

## Planejamento

1. Divida a narração em beats semânticos e registre timecodes por frase e palavra-chave.
2. Defina paleta, iluminação, contraste, tipografia, materiais e regras de continuidade.
3. Para cada beat, escolha o papel do asset: fundo, sujeito/objeto isolado, textura ou overlay.
4. Revise uma folha de contato dos fundos e uma prévia composta dos recortes antes do render integral.
5. Mantenha títulos, números, logos e diagramas como elementos vetoriais/HTML do renderer; não dependa de texto gerado na imagem.

## Continuidade e geração

- Gere fundo e foreground como pedidos separados, com composição e iluminação compatíveis.
- Reuse o asset aprovado do sujeito principal. Para movimentos 3D e ângulos consistentes, prefira um modelo 3D licenciado e reutilizável a várias imagens independentes.
- Registre prompt, provedor/modelo, dimensões, seed, cena, função e origem/licença no manifesto.
- Inspecione o canal alpha real. Transparência no prompt não é garantia técnica.
- Use SVG/CSS para curvas, pontos, linhas, setas e gráficos; ficam nítidos e animáveis.

## Movimento

O tipo layers em ShortScene aceita assets com papel, intervalo da cena, caixa de enquadramento, transformação inicial/final e z-index. x/y são pixels no canvas 1080x1920. Recortes transparentes permitem parallax e movimento independente. Defina opacidade inicial/final para criar entradas e saídas. Cada animação deve reforçar uma fala ou relação visual.

## Narração e desenho de som

audioTracks aceita voice, music e sfx. fromFrame e durationInFrames posicionam a faixa no vídeo; startFrom seleciona o início da fonte; fades e ducking são medidos em frames relativos à faixa. Os intervalos de ducking devem corresponder aos timecodes da fala; o sistema não detecta fala automaticamente.

Priorize voz clara no alto-falante do celular, música discreta e efeitos curtos que não mascarem a fala. Confira em fones e mono, loudness integrado, true peak, clipping e término da última palavra.

## Render e desempenho

- Use 30 fps como padrão; teste 60 fps quando o ganho de fluidez justificar o custo.
- Faça um render de 3–5 segundos antes do vídeo completo.
- Meça duração, render FPS, CPU/GPU e encoder na máquina final.
- O Chromium renderiza os frames; encoder GPU pode acelerar a codificação sem acelerar a criação de todos os frames.
- Execute npm test e npm run typecheck para validar timeline, duração, fades e ducking.

## Exemplo

Consulte examples/remotion-layers.example.json.
