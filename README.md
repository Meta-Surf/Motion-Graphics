# Motion Graphics

Sistema local para planejar, criar, editar e validar vídeos, cortes e motion graphics.
O projeto mantém briefing, decisões, assets, fontes e composição editável junto das
evidências de entrega. **`main` é a única versão de referência** no GitHub e no DACOL.

Leia o [procedimento operacional](docs/production-procedure.md). O
[AGENTS.md](AGENTS.md) torna essas regras permanentes para agentes que trabalham no
projeto. O sistema auxilia a produção; aprovação visual, escuta e decisões do
usuário continuam explícitas.

## O que funciona

| Etapa | Implementação | Limite verificado |
|---|---|---|
| Entrada | `production.py init`, classificação e manifesto validado | Pergunta decisões ausentes; não inventa consentimento |
| Inspeção | Doctor, FFprobe e SHA-256 dos arquivos | Instalação e health não comprovam inferência |
| Planejamento | Seleção de rotas com motivos e bloqueios | Não executa serviços pagos nem transforma plano em aprovação |
| Biblioteca | SQLite/FTS5, importação, seleção, backup e restauração | Licença/direitos e qualidade precisam ser aprovados |
| Novo motion | HyperFrames 0.8.211 e GSAP fixados | Ponte testada para `photo_essay` e `layers` |
| Composições existentes | Remotion 4.0.538/AiVideo | Sete templates; preserva o renderer identificado |
| Voz | Adaptador VoiceStudio, GPU obrigatória, cache e ASR | Português; perfil autorizado, dispositivo confirmado e speed=1 |
| Imagens | Fila Cloudflare ou geração direta explícita | Provedor, licença, privacidade e orçamento aprovados antes da chamada |
| Edição/revisão | Handoff local para editonny | Preflight → inspeção → cartão → resposta posterior → trabalho |
| Entrega | Probe, codecs, FPS, duração, áudio, decode e hashes | Revisões finais devem corresponder aos bytes entregues |

Concat está disponível como opção de timeline local quando houver prova de
importação, salvamento e reabertura. A integração automática com ele permanece
pendente. Os **21 padrões catalogados são receitas/estudos**, não 21 templates
intercambiáveis. Consulte a [matriz de contratos](docs/contract-compatibility.md).

## Instalação reproduzível

Python 3.12+, Node 22.13+ ou 24+, FFmpeg e FFprobe no PATH. PowerShell, na raiz:

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r scripts/requirements-gemini.txt
npm.cmd ci --prefix remotion
npm.cmd ci --prefix hyperframes
```

Os lockfiles npm fixam as dependências. O SDK Gemini legado permanece isolado no
adaptador existente. Modelos de ASR/recorte e o VoiceStudio têm preparação própria;
instalar dependências não baixa todos os modelos nem instala serviços externos.
Consulte [HyperFrames](docs/hyperframes.md) e [voz/GPU no DACOL](docs/dacol-gpu-and-production.md).
Credenciais ficam no ambiente; `.env.example` contém somente nomes e exemplos.

## Começar um pedido

Nos exemplos, `python` representa o executável da venv. Guarde pedidos reais em
`output/projects/`, fora do Git:

```powershell
python scripts/production.py doctor --output output/maintenance/doctor.json
python scripts/production.py init "Criar um motion para apresentar o produto" --project-id produto --output output/projects/produto/request.json
python scripts/production.py inspect CAMINHO_DO_VIDEO.mp4
python scripts/production.py plan output/projects/produto/request.json --capabilities examples/capabilities.example.json
```

O `init` cria um briefing com decisões desconhecidas como `null`. Complete somente
os campos comprovados pelo pedido ou pela inspeção. No `plan`, substitua o exemplo
de capacidades por observações locais com evidência. Arquivos já existentes não
são sobrescritos: edite o pedido em andamento para retomar o trabalho.

Antes de produção integral, defina roteiro, fontes, cenas, assets, áudio, ferramentas
e critérios; gere e meça uma amostra representativa. Registre os aceites reais com
o hash retornado pelo planner. Mudanças nas decisões invalidam aceites anteriores.
Música, efeitos, voz, cor, formato e serviço pago nunca são alterados silenciosamente.

## Produzir uma amostra editável

Diagnóstico sintético de 15 s, com SVG em camadas, tom de teste e rótulo temporizado:

```powershell
python scripts/make_hyperframes_smoke.py --layers --output output/smoke
python scripts/render_hyperframes.py output/smoke/project --action render --output output/smoke/preview.mp4 --gpu
```

`--gpu` é uma escolha explícita de navegador/encoder. Omiti-lo seleciona o perfil
CPU da CLI; não há fallback automático entre perfis. Use diretórios novos para
novas amostras. Para renderizar uma composição real compatível:

```powershell
python scripts/render_library_project.py composition.json --renderer hyperframes --output output/preview.mp4 --gpu
```

Composições Remotion existentes usam a rota correspondente. O render em blocos
reutiliza intervalos válidos por hash e dependências; a união compatível usa stream
copy, e o áudio contínuo é muxado no final:

```powershell
python scripts/render_chunks.py composition.json --output output/final.mp4 --concurrency 1 --resume
```

Voz e renders participantes compartilham `MOTION_GPU_LOCK`; o cache de takes usa
`MOTION_VOICE_CACHE`. Consulte o procedimento para medir CPU/GPU/memória e recuperar
falhas. Encoder de GPU não comprova aceleração de todas as outras etapas.

## Validar e entregar

```powershell
python scripts/check_project.py
python scripts/production.py verify output/projects/produto/request.json output/final.mp4 --output output/delivery.json
```

A primeira linha roda as suites offline e o typecheck, sem provedores de geração.
A segunda valida o arquivo real. Exit code **2** significa entrega bloqueada,
inclusive quando a parte técnica passou mas faltam imagem, escuta, sincronismo,
legendas, reprodução ou direitos. Registre revisor, evidência e hash de mídia;
`not_applicable` também precisa de justificativa.

Entregue o vídeo, manifesto, roteiro/fontes, assets selecionados e ledger, projeto
nativo/props, legendas solicitadas e evidências. Preserve originais e projetos de
produção fora do código reutilizável. Credenciais, referências de voz, bancos,
modelos, mídia privada e renders não entram no Git.

## Evidências e documentação

- [Validação medida e limites atuais](docs/production-audit-2026-10-28.md).
- [Operação completa e recuperação](docs/production-procedure.md).
- [Biblioteca e restauração](docs/asset-library.md).
- [Contratos e compatibilidade](docs/contract-compatibility.md).
- [HyperFrames e modelos locais](docs/hyperframes.md).
- [AiVideo, voz e render em blocos](docs/universal-video-pipeline.md).
- [Gemini: planejamento e publicação explícita de imagens](docs/gemini-orchestrator.md).
- [Fila de imagens e retenção dos artefatos](docs/image-generation-queue.md).
- [Editonny: confirmação e revisão](docs/editonny-review.md).
- [Estudos de motion e qualidade](docs/motion-library.md).

As medições descrevem as amostras executadas, sem prometer aprovação editorial,
suporte universal a formatos ou integração que ainda não tenha sido testada.
