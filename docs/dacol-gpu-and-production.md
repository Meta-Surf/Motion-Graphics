# DACOL — operação da versão principal

A referência operacional é `main` em `C:\Users\marco\Projects\Motion-Graphics`.
O README, `AGENTS.md` e `docs/production-procedure.md` descrevem o mesmo fluxo.
Worktrees de integração são temporários; projetos privados e evidências não são
outras versões ativas do pipeline.

## Preflight

```powershell
& .\.venv\Scripts\python.exe scripts/production.py doctor --output output/maintenance/doctor.json
& .\.venv\Scripts\python.exe scripts/check_project.py
```

Escolha novo caminho para um relatório novo. Doctor é inventário, sem instalar,
gerar mídia ou aprovar capacidades. Use `production.py inspect` nas fontes reais.
O relatório público atual é [a validação do procedimento](production-audit-2026-10-28.md);
inventário detalhado e arquivos pessoais ficam em `output/maintenance`.

## Voz e ROCm

VoiceStudio desktop Windows e backend GPU WSL são instalações distintas. A rota
existente de produção usa o backend na porta 3901, perfil autorizado e speed=1.
A API PyTorch pode chamar o dispositivo AMD de `cuda`; confirme também HIP e o nome
real do dispositivo. Defina `MOTION_VOICE_DEVICE=AMD Radeon RX 7800 XT` no processo
que gera voz para rejeitar outro dispositivo. Não substitua voz, idioma, CPU ou
velocidade automaticamente.

O serviço existente usa detecção DXG no WSL. Um probe avulso precisa do mesmo loader
ROCm e da detecção, antes de importar PyTorch. Com a instalação observada:

```powershell
wsl -u canalvideo -e env LD_LIBRARY_PATH=/opt/rocm-7.2.1/lib:/usr/lib/wsl/lib /opt/voicestudio-gpu-venv/bin/python /mnt/c/Users/marco/Projects/Motion-Graphics/scripts/probe_rocm.py
```

O probe configura `HSA_ENABLE_DXG_DETECTION=1` quando encontra `/dev/dxg`. Ele exige
GPU e HIP e verifica um cálculo de tensor. Não carrega modelos ou gera voz.
Cálculo passou na RX 7800 XT; a narração de cada trabalho ainda precisa de perfil
aprovado, take representativo, ASR e escuta. O adaptador atual é de português.

Para iniciar o serviço já instalado, os scripts `start-voice-gpu.ps1` e
`install-voice-startup.ps1` documentam a rota existente. Não execute instalação de
startup ou reinstale modelos durante um simples diagnóstico. Antes de reiniciar
qualquer serviço, verifique trabalhos em andamento.

## GPU, render e fila

HyperFrames é avaliado primeiro para novos motions suportados. Remotion mantém
composições existentes e recursos especializados. Navegador, inferência, efeitos
e encoder são capacidades separadas; h264_amf não prova todas elas.

Todos os participantes devem usar o mesmo `MOTION_GPU_LOCK` (padrão
`~/MotionLibrary/gpu.lock`). Não há remoção automática de locks vivos. Aplicativos
externos e processos que não participam do lock precisam de coordenação operacional.
Comece com concorrência 1 em cargas pesadas; aumente somente após medição.
`scripts/measure_dacol.ps1` mede CPU, engines GPU e memória dedicada do sistema,
incluindo outros aplicativos; valores ausentes não são zero medido.

Use cache de assets/takes e `render_chunks.py --resume`. Preserve o destino e a
assinatura dos blocos; uma saída nova evita sobrescrever a entrega anterior.
O cache HyperFrames não promete retomada incremental por cena.

## Atualização e entrega

Atualize o checkout principal somente para `main` testada, preservando arquivos
privados e reconciliando alterações locais. Depois rode doctor, checks e uma
amostra no checkout efetivo. Não deixe vários checkouts divergentes como referências
operacionais. Não publique referências de voz, credenciais, modelos, bancos ou mídia.

Valide os bytes finais com `production.py verify`; imagem, escuta, legendas,
sincronismo, direitos e reprodução permanecem revisões explícitas. Retenha projeto
editável e evidências. Concat só é considerado uma timeline integrada após teste
de importação/salvamento/reabertura; editonny mantém sua confirmação posterior ao
cartão antes de cada novo trabalho editorial.
