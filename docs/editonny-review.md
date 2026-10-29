# Revisão final opcional com Editonny

[Editonny](https://github.com/soumatheusgomes/editonny) é uma skill local para Codex e Claude Code que edita vídeos e também organiza inspeção, amostra e validação de exportação. Ela complementa o Remotion como etapa humana/agentiva pós-render; não é uma API HTTP nem uma ação de GitHub Actions. O processo e renderização rodam na máquina onde a skill está instalada. A integração aqui prepara o handoff, sem instalar Editonny, enviar mídia ou alterar o Short automaticamente.

## Fluxo

1. Renderize o Short com Remotion ou com o renderer Python existente.
2. Prepare uma cópia isolada para revisão. O script confere via FFprobe que o arquivo tem vídeo, confere dimensões, duração e streams do formato escolhido (Short 15–180 s ou 16:9 480–1800 s).
3. Inclua roteiro/transcrição, legendas e storyboard se estiverem disponíveis.
4. Abra a pasta gerada no computador com Editonny instalado e peça uma **revisão**. Preserve a exportação original.
5. Registre os achados e decisão em `review-manifest.json`. Se o Editonny propuser cortes, tratamento de áudio, legendas ou reenquadramento, aplique somente após revisar a proposta e aprove uma amostra; mantenha a composição Remotion original como base e compare a nova exportação.
6. Execute novamente as verificações técnicas no arquivo final e marque a decisão como `approved` somente quando os bloqueios forem resolvidos.

Para cada nova edição: inspecione, apresente o cartão completo de configurações e aguarde uma resposta explícita posterior antes de criar o workspace. O pedido inicial nunca aprova seu próprio cartão. Consulte a skill física instalada e o [procedimento operacional](production-procedure.md). O Editonny exige confirmação das configurações antes de editar. Portanto, comece com solicitação de revisão somente; não autorize cortes ou re-render automático por inferência.

## Preparar pacote

Requisitos locais: Python 3.10+ e FFprobe disponível no PATH.

```bash
python3 scripts/prepare_editonny_review.py /caminho/short.mp4 \
  --script /caminho/roteiro.txt \
  --captions /caminho/legendas.srt \
  --storyboard /caminho/storyboard.json
```

Sem opções, o pacote é criado em `review/editonny/`. Informe `--output` para outro destino. A pasta `review/` é ignorada pelo Git: renders, roteiro e áudio do Short não entram no repositório.

Depois, no computador que tem a skill instalada, abra a pasta do pacote e use `$editonny` no Codex. Peça uma análise quadro a quadro de ritmo, correspondência entre fala e imagem, motion graphics, área segura, legendas, áudio e problemas de exportação. O pacote não invoca o Editonny por conta própria.

## Critérios da revisão

- **História e precisão:** afirmações correspondem às fontes registradas; imagens geradas são ilustração, não evidência.
- **Imagem e fala:** cada imagem tem motivo narrativo, continuidade de estilo, enquadramento e composição adequados.
- **Motion graphics:** elementos de foreground se movem com intenção; cartões, gráficos e destaques explicam a fala e não competem com ela.
- **Camadas visuais futuras:** além do fundo, planejar assets dedicados para os próprios elementos gráficos: recortes transparentes de sujeitos/objetos, ícones e texturas. Animá-los em camadas separadas (parallax, entrada/saída, escala e trajetória), sem gerar texto legível na imagem. O roteiro do asset registra prompt, provedor/modelo, seed quando houver, dimensão, transparência e cena de destino.
- **Texto:** legendas sincronizadas e legíveis em tela de celular, dentro da safe area, sem cobrir o assunto principal.
- **Áudio:** narração inteligível, sem clipping, sincronizada e equilibrada com música/efeitos.
- **Ritmo:** abertura prende nos primeiros segundos; mudanças visuais sustentam o vídeo de pelo menos 30s; fim não corta a fala.
- **Exportação:** 9:16, 1080×1920, H.264/AAC quando aplicável, streams reproduzíveis e duração validada.

## Limites e segurança operacional

Editonny é um editor/revisor local generalista, não um validador factual automático nem uma integração nativa do Remotion. Não envie mídia a serviços externos nem autorize serviços pagos sem decisão explícita. O workflow atual de GitHub Actions continua restrito à geração de imagens; a revisão permanece local porque vídeo/narração são assets específicos do Short.

Consulte o [guia oficial do Editonny](https://github.com/soumatheusgomes/editonny/blob/main/README.pt-BR.md) para instalação, requisitos e uso atual. Instalação e atualização na máquina Dacol são passos separados deste repositório.
