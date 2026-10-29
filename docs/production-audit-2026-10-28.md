# Validação do procedimento — 28 de outubro de 2026

Este resumo público contém somente comportamento do código e resultados da
fixture sintética. Inventário de máquina, caminhos locais, branches de produção,
fontes, perfis e detalhes de mídia ficam no relatório privado em `output/maintenance`.
Nenhuma chamada de geração paga foi realizada nesta validação.

## Mudanças verificadas

- Briefing com seis tipos de pedido, decisões ausentes, origem/licença/hash dos
  assets e seleção justificada de rota. Aceites se vinculam ao hash das entradas;
  revisões finais se vinculam ao hash dos bytes entregues.
- HyperFrames preferido para novos motions com binding suportado; composições
  existentes e recursos especializados preservados em Remotion. IDs Gemini
  continuam sendo planejamento, sem conversão automática dos 21 padrões.
- Planejamento Gemini não publica jobs de imagem por padrão. A publicação exige
  `--enqueue-images` e o procedimento exige provedor/orçamento aprovados.
- Reserva cooperativa comum de GPU, cache de imagem por request, cache de voz por
  perfil/versão/payload e revisão ASR associada ao hash do áudio.
- Retomada de vídeo por dependências do intervalo; narração é muxada depois.
  Sem cache incremental prometido para o renderer HyperFrames nativo.
- Verificador confere streams, codec, resolução, FPS, duração, decode e hash;
  a entrega segue bloqueada quando faltam revisões editoriais.

## Amostra sintética em Windows

Fixture `make_hyperframes_smoke.py --layers`: SVGs, camada independente, tom de
220 Hz e rótulo temporizado; nenhum material privado ou perfil de voz.

| Medição | Resultado |
|---|---|
| Formato | 1080×1920, 24 FPS, 360 frames, 15,0 s |
| Encoder observado | H.264 AMF; áudio AAC |
| Tamanho | 1.727.153 bytes |
| SHA-256 | `9c2b82daf8ee32f09cadaea00c3c22c934cc7663f6e18a99f7be4008e0bc4212` |
| Tempo do renderer | 18,4 s |
| Wrapper com verificações | 21,309 s |
| Janela externa de medição | 27,2 s, incluindo amostragem/finalização |
| CPU do sistema | média 35,58%, pico 68% |
| Pico por engine GPU amostrado | 23% |
| Memória dedicada agregada amostrada | 4,776–5,044 GB |
| Tom (volumedetect) | média -36,4 dB, pico amostral -33,3 dB |
| Check oficial, formato/FPS/duração/áudio e decode | Passaram |

Contadores do sistema incluem outras aplicações; não atribuem consumo somente ao
renderer e não constituem comparação de qualidade CPU/GPU. O monitor inicial
registrou exit_code null; o wrapper e os bytes comprovaram sucesso. O monitor foi
corrigido para reter o handle, e teste posterior confirmou exit_code=0.

O frame do meio foi inspecionado para título, foreground e rótulo. Isso não prova
reprodução completa, escuta ou sincronismo de fala. Não há fala nesta fixture.
O novo verificador devolveu `technical=passed`, `delivery=blocked` e revisões
pendentes, preservando a diferença entre diagnóstico e aprovação editorial.
O pacote mantém props, HTML, SVGs, WAV e captions.json para edição e retomada.

A mesma fixture foi exportada via AiVideo/Remotion em perfil libx264 explícito.
Uma segunda exportação com `--resume` manteve o fingerprint e executou zero renders
de bloco, contra um na primeira. Ambas passaram validação e decode. Testes de
invalidação cobrem mudança de cena fora do intervalo, imagem dentro do intervalo
e áudio separado do cache de vídeo. Não se usou esse teste como ranking visual
entre renderers, que têm layouts diferentes.

## Suites e reprodução

Suites Python: procedimento (15), orquestração (9), Gemini offline (13), pipeline
(5), biblioteca (7), compilador (5) e HyperFrames (16): **70 verificações**.
Remotion no Windows: **20 testes e typecheck**. A suite de procedimento gera um
arquivo FFmpeg real e valida decode; o teste Gemini usa SDK real com rede mockada.
CI novo não usa chaves ou provedores de geração.

Siga `production-procedure.md` para doctor, inspeção de fontes, briefing, planner,
amostra medida e verificação. A integração prévia foi reaproveitada; este é o relatório de validação atual. As dependências e os modelos seguem seus pins;
nenhum modelo privado ou binário de produção é incluído no Git.

## Limites e promoção

O probe ROCm foi repetido com a mesma detecção DXG usada pelo serviço. PyTorch
confirmou o dispositivo AMD e executou um cálculo de tensor na GPU com resultado
verificado. A falha do processo isolado anterior era de configuração do probe;
`HSA_ENABLE_DXG_DETECTION=1` agora é aplicado em WSL antes de importar PyTorch.
Isso comprova computação GPU, não um novo take de voz. Saúde HTTP não comprova
inferência: perfil aprovado e amostra/ASR ainda são necessários antes de narrar.
Nenhuma nova narração foi gerada nesta validação.

Concat permanece handoff local até haver teste de importação, salvamento e
reabertura; não é anunciado como encoder final. editonny mantém o preflight e a
regra de inspeção, cartão e resposta posterior antes de uma nova edição. Nenhum
workspace editorial foi criado por esta auditoria.

A versão foi validada primeiro em checkout isolado. A consolidação autorizada
usa `main` como única referência operacional, após testes e reconciliação dos
arquivos locais. Fontes de produções anteriores ficam preservadas como projetos
privados, sem manter outra versão ativa do pipeline.
