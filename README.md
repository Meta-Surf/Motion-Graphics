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

A API ainda não está escolhida nem conectada. A arquitetura deve isolar o provedor em `src/providers/`, sem credenciais no código ou no Git. A integração deve permitir gerar e regenerar uma imagem por cena, mantendo versão do modelo e prompt. O provedor e a cobrança serão decididos antes de habilitar chamadas pagas.

## Estrutura

- `docs/architecture.md` — arquitetura e decisões de qualidade.
- `docs/visual-quality-gates.md` — critérios para aprovar imagens e montagem.
- `src/providers/` — adaptadores futuros de geração de imagem.
- `config.example.env` — nomes de configuração sem segredos.

## Execução

O pipeline final ainda está em desenvolvimento. O pacote contém apenas a estrutura reutilizável do projeto; não inclui nenhum Short finalizado ou conteúdo específico do vídeo anterior.
