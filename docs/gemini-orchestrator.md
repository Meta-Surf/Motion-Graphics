# Gemini como planejador do Motion

`src/providers/gemini_orchestrator.py` recebe um roteiro em texto simples, pede um plano ao Gemini com `response_mime_type="application/json"` e `response_schema`, valida o resultado e publica os pedidos de imagem no formato da fila existente. A função pública é `generate_video_manifest(script_text: str) -> VideoManifest`, com opções adicionais por argumentos nomeados.

## SDK e configuração

Foi usado **`google-generativeai==0.8.5`**, conforme solicitado. O Google classifica essa biblioteca como legada e descontinuada; a recomendação oficial para novos projetos é `google-genai`. O código do SDK está isolado neste provedor, permitindo uma migração posterior sem alterar o manifesto, os templates ou a fila. Consulte a [documentação oficial das bibliotecas](https://ai.google.dev/gemini-api/docs/libraries).

Instale as dependências opcionais em seu ambiente Python 3.12+:

```powershell
python -m pip install -r scripts/requirements-gemini.txt
$env:GEMINI_API_KEY = "SUA_CHAVE"
$env:GEMINI_MODEL = "ID_DO_MODELO_DISPONIVEL_NA_SUA_CONTA"
```

Escolha um modelo com suporte a saída estruturada e ao limite de tokens configurado. O código não fixa um modelo sujeito a desligamento; `GEMINI_MODEL` ou `--model` é obrigatório. A chave só vem do ambiente e não é gravada no manifesto, metadados ou logs. `.env.example` documenta os nomes; o script não carrega `.env` automaticamente.

## Executar

```powershell
python src/providers/gemini_orchestrator.py examples/gemini-script.example.txt --video-type short_9_16 --output jobs/manifests/meu-video.json
```

O SDK faz uma chamada somente quando a função é invocada. O comando acima usa a API do Gemini, portanto consome a cota dessa conta. Cloudflare, VoiceStudio e Remotion não são chamados por esse comando.

Opções: `--model`, `--video-type`, `--timeout` (padrão 120 segundos por tentativa), `--max-attempts` (padrão 3) e `--max-output-tokens` (padrão 65536). O modelo escolhido deve aceitar esse orçamento de saída; reduza-o quando necessário. Para roteiros longos, um orçamento pequeno pode truncar o JSON; respostas truncadas são rejeitadas integralmente. A geração não é determinística, mesmo com temperatura baixa.

Uso como módulo, com `src` no caminho de imports, por exemplo a partir de outro script em `src/`:

```python
from providers.gemini_orchestrator import generate_video_manifest

manifest = generate_video_manifest(
    "Uma ideia ganha forma. A revisão melhora o resultado.",
    video_type="short_9_16",
)
```

O retorno é um dicionário tipado com `video_type` e `scenes`. O CLI escreve esse JSON em stdout; logs com os caminhos de saída vão para stderr. Sem `--output`, a saída recebe um nome derivado do conteúdo em `jobs/manifests/gemini-<hash>.json`, preservando planos anteriores.

## Contrato e os 21 padrões

O contrato local é `schemas/gemini-manifest.schema.json`. Cada cena contém **somente** `template_id`, `narration_text` e `image_prompt`. O schema enviado ao Gemini usa o subconjunto suportado pelo protobuf do SDK legado; depois, JSON Schema local rejeita campos extras, templates desconhecidos, textos vazios, limites excedidos e listas inválidas. O parser também rejeita Markdown, propriedades duplicadas e números não finitos.

`motion-library/orchestration-templates.json` associa aliases como `titles`, `comparison` e `semantic-focus` aos IDs P01–P21 do catálogo consolidado. O código verifica cobertura completa e correspondência do enum no schema antes da chamada e inclui nomes e status reais no system instruction. Adicionar ou remover um padrão exige atualizar o registro e o schema juntos.

O prompt orienta seleção semântica do motion, continuidade de câmera/paleta/iluminação e fotografia cinematográfica. Cada prompt visual deve terminar no sufixo compartilhado de `src/video_contract.py`; o código o acrescenta se houver omissão e valida novamente o tamanho final. “8k detail aesthetic” descreve direção de arte, não uma imagem nativa em 8K. As dimensões solicitadas continuam sendo 864×1536 ou 1536×864.

As palavras da narração completa precisam aparecer na mesma ordem em todas as cenas. A comparação normaliza caixa, Unicode, espaços e pontuação; não aceita resumo, paráfrase ou fala inventada. O roteiro deve conter somente a narração desejada. O VoiceStudio atual é configurado para português; use roteiro em português nesse fluxo ou adapte o provedor antes de produzir outros idiomas.

`video_type` pode ser inferido pelo modelo ou fixado com `--video-type`; uma escolha explícita nunca pode ser alterada pela resposta. As durações de 15–180 s e 480–1800 s são orientações de planejamento. A duração real continua dependendo dos WAVs e é validada pelo compilador, não pela estimativa textual do Gemini.

## Saídas e GitHub Actions

O manifesto de vídeo **não é** o manifesto da fila Cloudflare. Colocá-lo diretamente em `jobs/pending/gemini_manifest.json` quebraria `src/process_image_queue.py`, que exige `job_id` e `images`. Por isso o adaptador publica:

| Saída | Conteúdo |
| --- | --- |
| `jobs/manifests/<nome>.json` | Plano de vídeo com o contrato solicitado |
| `jobs/manifests/<nome>.meta.json` | Modelo, hashes, vínculo com P01–P21, IDs das cenas e caminhos dos lotes |
| `jobs/pending/gemini-<hash>.json` | Lotes compatíveis com a fila, com até oito imagens cada |

O código impede que `--output` coloque o plano de vídeo dentro da pasta da fila. Os pedidos usam seeds estáveis derivados dos prompts, dimensões do formato e nomes de arquivo por hash. Pedidos idênticos compartilham uma imagem; cada cena continua identificada no metadado. Republicar os mesmos pedidos não duplica lotes já pendentes ou processados. Um plano diferente ainda pode gerar novos pedidos e custos.

O workflow `cloudflare-image-queue.yml` existente processa os lotes quando eles são enviados à branch monitorada ou encontrados pela execução agendada. Criar arquivos localmente não faz commit, push nem inicia Actions. Alternativamente, rode `python src/process_image_queue.py` com as credenciais Cloudflare no ambiente. Os artefatos e resultados continuam seguindo o fluxo atual.

O `.meta.json` só indica `status: planned`; voz não foi solicitada, e aprovação visual/escuta permanecem pendentes. O planejamento entre 21 padrões não significa que todos estejam adaptados ao renderer universal: `AiVideo` ainda aceita seus sete IDs próprios. O contrato mínimo do Gemini também não contém perfil de voz aprovado, título, guia de arte, seeds e demais metadados exigidos por `video-director.schema.json`.

Portanto, antes de passar o plano a `build_composition.py`, uma etapa editorial deve fornecer esses metadados e vincular cada padrão a um componente realmente implementado. O adaptador não substitui silenciosamente um motion por outro nem marca candidatos como prontos. O texto de cada `narration_text` pode ser fornecido ao `VoiceStudio.narrate()` existente com um perfil aprovado. Esta integração implementa a geração do plano e sua tradução para a fila de imagens; não inicia automaticamente a produção completa.

## Falhas e testes

Timeout, indisponibilidade e HTTP 429 recebem tentativas limitadas com espera exponencial curta e jitter. O retry interno do SDK é desativado para não multiplicar tentativas. Cota diária esgotada falha após o limite, com mensagem para revisar cota/conectividade. Autenticação, modelo inválido e outros erros permanentes falham sem retry. Mensagens brutas da API não são reproduzidas nos logs, evitando exposição de chave ou roteiro em URLs/erros.

Respostas bloqueadas, vazias, incompletas, fora do schema ou com narração alterada não publicam plano nem lotes. Escritas de JSON são atômicas individualmente e protegidas por locks. Uma falha de disco durante a publicação pode deixar um plano ou parte dos lotes válidos; os arquivos não formam uma transação única. Reruns com a mesma resposta são idempotentes. Após encerramento abrupto, confirme que o processo acabou antes de remover apenas o `.lock` correspondente.

```powershell
python scripts/test_gemini_orchestrator.py
python scripts/test_orchestration.py
python scripts/test_pipeline.py
```

Os testes usam o SDK real para conferir a conversão do schema e simulam as respostas de rede. Cobrem os 21 padrões, validação, preservação da narração, sufixo, cotas/timeouts, autenticação, truncamento, proteção da fila, lotes e idempotência, sem chave real ou chamada paga. O workflow `remotion-check.yml` instala as dependências e executa esses testes.

Verificação local: 12 testes do Gemini e os 14 testes de regressão Python passaram. O teste de integração confirmou o consumo dos lotes pelo `process_image_queue.py` real, com a geração de imagem substituída por um provedor falso. O acesso ao modelo e à cota da conta precisa ser validado com a configuração real do usuário.

Referências: [saída estruturada](https://ai.google.dev/gemini-api/docs/structured-output), [RequestOptions do SDK solicitado](https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/docs/api/google/generativeai/types/RequestOptions.md).
