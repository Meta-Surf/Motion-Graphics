# Procedimento operacional para qualquer pedido de vídeo

Este é o ponto de partida. Os guias de renderer detalham implementações específicas;
as decisões de trabalho ficam no manifesto `production-request.schema.json`.
Use `examples/production-request.synthetic.json` como modelo e mantenha os manifestos
reais em `output/projects/<id>/v001/`, fora do Git. Nunca fabrique uma aprovação.

## Entrada e inspeção automática

`python scripts/production.py classify "pedido"` sugere uma das seis classes:
criação completa, edição de fontes, corte, motion, revisão, atualização. A classe
explícita do manifesto prevalece; pedidos mistos podem requerer etapas diferentes.
Para edição/corte/revisão, primeiro localize os arquivos pedidos. Inspecione
resolução, duração, FPS racional/VFR, rotação, streams, cor/HDR, áudio e hashes com
FFprobe. Leia Git status, HEAD e worktrees. Não transcreva todo o material para
simplesmente descobrir as configurações. Na skill editonny, observe os limites de
amostragem pré-confirmação (até 30 s por fonte, até três fontes, modelos em cache).

Preencha os campos conhecidos e use `null` para decisões ausentes. Valores false,
lista vazia ou `none` são decisões conhecidas, não perguntas. Pergunte apenas os
campos retornados por `production.py plan`, agrupados em linguagem do usuário:
finalidade/público; fontes e direitos; idioma; formato/duração; perfil de voz
quando houver narração; legendas; música/efeitos; prazo; orçamento/provedores e
transmissão externa; arquivos e destino de entrega. Referências visuais são
preferências: lista vazia significa que não foram fornecidas. Não invente fontes,
resultados, métricas factuais, locale ou consentimento de voz.

O campo `format` registra o contrato solicitado, inclusive racional como
30000/1001. Isso não amplia os renderers atuais: AiVideo aceita somente 1080p,
24/25/30/60 FPS, Shorts 15–180 s ou 16:9 480–1800 s. Outros formatos/cortes podem
usar a rota editonny/FFmpeg após inspeção e aceitação; nunca converter HDR, FPS,
cor, geometria ou voz silenciosamente para satisfazer AiVideo.

## Plano antes da produção

Prepare roteiro, fontes/afirmações verificadas, mapa de cenas com objetivos e
texto, assets por cena, narração medida, música/efeitos explicitamente pedidos,
legendas, ferramentas e critérios. Registre em cada asset: origem, licença/direito,
SHA-256 dos bytes, modelo/prompt (null para mídia real), destino e revisão. IDs
referenciam esse ledger; a biblioteca SQLite fornece importação, pesquisa,
seleção por cena e aprovação de direitos/qualidade (`docs/asset-library.md`).

Uma decisão de novo asset deve comparar reutilização, geração local e provedor
externo por adequação, licença, privacidade, disponibilidade e custo. Declare
`asset_strategy` e `new_asset_reason`. `external.allowed` não autoriza qualquer
serviço: registre providers, teto monetário, moeda e private_upload. Estime custo
por chamada/lote antes de executar; se a cota/preço não puder ser comprovado, pare
apenas essa etapa. Chamadas de planejamento Gemini também podem custar.

```powershell
python scripts/production.py plan output/projects/meu-video/v001/request.json --capabilities output/maintenance/capabilities.json
```

O arquivo de capacidades é uma observação local por ferramenta, com `state` e
`evidence`. Estados: `absent`, `installed`, `functional`, `sampled`, `production`.
Use o exemplo `examples/capabilities.example.json` como estrutura, não como prova.
`functional` exige comando real funcionando; `sampled` exige uma amostra medida;
`production` exige aprovação para aquele perfil/trabalho. Uma instalação em outro
worktree não configura automaticamente o checkout atual. Revise observações a cada
sessão e após mudança de versão/driver. O planner não executa produção nem substitui
o preflight: aprovação de roteiro e amostra são gates registrados por quem revisou.

## Hierarquia por etapa

| Etapa | Preferência | Exceção e comprovação |
|---|---|---|
| Fontes/arte | Mídia real e assets aprovados adequados | Nova geração só com motivo, direitos e amostra |
| Novo motion | HyperFrames, biblioteca e check oficial | Remotion quando falta binding/recurso ou ganha em amostra representativa |
| Vídeo existente | Preservar projeto, takes e renderer | Migrar componente útil em projeto separado e comparar movimento/frames |
| Narração | VoiceStudio ROCm no DACOL, perfil autorizado | Indisponibilidade bloqueia voz; mudança exige decisão explícita |
| Edição/cortes/revisão | editonny conforme a tarefa | Preflight e confirmação obrigatórios; FFmpeg em rota suportada |
| Timeline editável | Concat se importar e reabrir corretamente | Entregar projeto nativo HyperFrames/Remotion e assets; não simular Concat |
| Imagem/áudio/vídeo gerado | Reuso → comparação local/external | Escolher por requisito/qualidade/custo, sem tentativas pagas cegas |
| União de blocos | FFmpeg stream copy se assinaturas forem compatíveis | Codec/timebase/extradata divergentes exigem decisão e nova amostra |

O planner preserva Remotion por padrão em atualização de composição existente;
confirme a origem se o projeto anterior era HyperFrames/outro editor. Ele lista
rotas, justificativas e bloqueios; não tenta converter 21 receitas em componentes.
Veja `docs/contract-compatibility.md` para os contratos e as lacunas reais.

## Regra editonny

Leia a skill física instalada e execute doctor, verifique caches/capacidades e
consulte o repositório oficial para atualizações sem atualizar automaticamente.
Nova edição: **inspecionar → cartão completo → resposta explícita posterior →
workspace init**. O cartão cobre objetivo, fontes/ordem, imagem/cor, formato,
idiomas distintos, legendas, limpeza, som, visuais e revisão/destino. Identifique
valores pedidos, observados e sugeridos. Guarde o cartão exato, hora real, reply
posterior e identificador real da mensagem. O schema verifica ordem das datas,
mas não autentica o usuário: o agente deve obter a resposta na conversa.

Antes da resposta, apenas inspeções permitidas e temporárias; sem workspace,
transcrição completa, tratamento, upload ou render editorial. Música e efeitos
são opt-in; dinâmica visual não autoriza áudio adicional. Alterações posteriores
pedem cartão revisado e nova resposta. A regra completa da skill instalada prevalece
para executar editonny; `prepare_editonny_review.py` é apenas handoff, não execução.

## Amostra e recursos no DACOL

Confirme health do VoiceStudio na porta 3901 e o nome do dispositivo; a indicação
`cuda` pode ser a API PyTorch sobre AMD/ROCm. Verifique WSL/PyTorch HIP separadamente.
O desktop 3900 é outra instalação. Não suponha VRAM a partir de AdapterRAM WMI
32-bit. Não mude perfil, idioma, speed=1 ou CPU automaticamente. O adaptador de
voz atual gera/transcreve português; outro idioma precisa de rota testada explícita.

Faça amostra representativa de 8–15 s (ou trecho completo mais curto para edição),
com os tratamentos realmente pedidos. O smoke AiVideo tem 15 s por limite do
contrato. Não adicione música/efeitos só para preencher a amostra; seu tom sintético
é um diagnóstico rotulado, não uma proposta de trilha ou uma voz aprovada.

Meça tempo, CPU, GPU, memória e tamanho. `scripts/measure_dacol.ps1` amostra
contadores do sistema e informa valores ausentes; não atribui o consumo de outros
apps ao render. Exemplo, PowerShell no checkout de validação:

```powershell
python scripts/make_hyperframes_smoke.py --layers --output output/smoke-v001
.\scripts\measure_dacol.ps1 -OutputDirectory output/measure-v001 -Executable python -CommandArguments @('scripts/render_hyperframes.py','output/smoke-v001/project','--action','render','--output','output/smoke-v001/validation.mp4','--gpu')
```

Separar: navegador (Canvas/compositing/WebGL), inferência (PyTorch HIP/modelo),
efeitos (cada filtro/backend) e codificação (h264_amf realmente usado). Um encoder
AMF funcionando não prova render integral na GPU. Compare CPU/GPU com mesmo trecho
quando a escolha depender de desempenho; CQP e CRF não garantem qualidade igual.
Use concorrência 1 para cargas pesadas até medir outra configuração.

VoiceStudio, HyperFrames render e render em blocos usam `MOTION_GPU_LOCK`, padrão
`~/MotionLibrary/gpu.lock`, inclusive entre worktrees. Remotion/AMF usa o mesmo
padrão. Lock é cooperativo: apps externos, WSL ou outro processo que não participa
precisam de fila operacional. Confira jobs ativos antes de iniciar. Nunca apague
lock vivo; após crash, confira host/PID e bytes parciais antes da remoção manual.

## Retomada e falhas

Imagens têm cache por request/hash em `output/asset-cache/images`; cada pacote
recebe cópia independente. Takes ficam em `MOTION_VOICE_CACHE` (padrão
`~/MotionLibrary/voice-cache`) com perfil/versão/payload na chave e revisão ASR
vinculada aos bytes. Modelo/licença/revisão do asset continuam sendo decisões.

`render_chunks.py --resume` verifica hash e parâmetros de cada bloco. A chave usa
somente cenas e assets visíveis no intervalo, código/lockfiles, formato e browser;
áudio contínuo é muxado depois. Alterar um título não invalida cenas de outros
blocos; alterar código ou tempo global pode invalidar vários. Frame bounds
absolutos preservam animações. Não prometa cache de blocos HyperFrames: o renderer
nativo ainda renderiza o projeto inteiro. Versione saídas e preserve checkpoints.

Falha GPU/driver: guardar logs, liberar lease própria e recuperar aceleração antes
de repetir. OOM: reduzir concorrência/tamanho de batch sem mudar entrega; se isso
não bastar, propor redução de complexidade/qualidade. Sem ferramenta: concluir
plano e assets independentes; apresentar rota concreta com perdas/custos para decisão.
Sem armazenamento: não apagar mídia/produções; escolher novo destino aprovado.
Nunca acionar CPU, voz substituta, conversão de cor/formato ou provedor pago como
fallback silencioso. Preservar o último pacote aprovado permite rollback.

## Validação e entrega

Execute lint/check oficial, testes aplicáveis, FFprobe e decode integral. Depois
revise frames de entrada/meio/saída, movimento reproduzido, voz/escuta, sincronismo,
legendas e cortes. Registre revisor e arquivo/resultado em `reviews`; justifique
`not_applicable` quando não há voz/legendas. Não marque inspeção de still como
reprodução validada. Loudness, pico, cor/HDR e legibilidade devem respeitar o
briefing e a rota do editor; o verificador abaixo não mede tudo isso sozinho.

```powershell
python scripts/production.py verify output/projects/meu-video/v001/request.json output/final-v001.mp4 --output output/delivery-v001.json
```

O exit code 2 significa entrega bloqueada (incluindo revisão pendente), mesmo se
`technical=passed`. O relatório confere codec, pixel format, dimensões, FPS,
duração, streams de áudio, decode e hash. Reprodução humana/agentiva, fidelidade
factual, imagem e escuta são evidências separadas e honestas. Entregue também o
manifesto, roteiro/fontes, assets/ledger, props/projeto nativo, legendas pedidas,
medição e comandos/versões para retomar. Faça backup e teste restauração pela
biblioteca antes de apagar qualquer cópia de trabalho.

## Publicação e atualização do checkout

Branch com commits coerentes → PR com evidências e limites → versão aprovada →
sincronização conservadora. Se o checkout DACOL estiver sujo, use worktree nova
e valide lá; não substitua produções para terminar uma auditoria. Depois da aprovação,
confirme status, crie ref de backup, faça fast-forward quando possível e repita
preflight/smoke no destino real. Divergência ou arquivos locais conflitantes pedem
uma decisão concreta de promoção; merge do PR não é presumido. O relatório de
esta sessão está em `docs/production-audit-2026-10-28.md`.
