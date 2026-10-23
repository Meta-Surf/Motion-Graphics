# Cloudflare Workers AI — geração de imagens

O adaptador usa o modelo `@cf/black-forest-labs/flux-2-klein-4b` pela API REST do Workers AI. O endpoint oficial aceita campos multipart, incluindo prompt e dimensões, e retorna a imagem em Base64.

## Preparação

1. Na Cloudflare, habilite Workers AI e copie o Account ID.
2. Crie um API Token com a permissão mínima de Workers AI necessária para executar inferência.
3. Defina `CLOUDFLARE_ACCOUNT_ID` e `CLOUDFLARE_API_TOKEN` no ambiente local. Não cole o token no GitHub, em prompts ou em arquivos compartilhados.
4. Python 3.10+ é suficiente; o script usa apenas a biblioteca padrão.

## Gerar uma imagem vertical

Linux/macOS:

```bash
export CLOUDFLARE_ACCOUNT_ID="seu_account_id"
export CLOUDFLARE_API_TOKEN="seu_token"
python src/providers/cloudflare_workers_ai.py \
  --prompt "cinematic editorial photograph of a modern AI research laboratory, realistic materials, dramatic teal and amber lighting, vertical composition, no text, no logos" \
  --width 1024 --height 1792 \
  --output output/scenes/scene-01.png
```

PowerShell:

```powershell
$env:CLOUDFLARE_ACCOUNT_ID = "seu_account_id"
$env:CLOUDFLARE_API_TOKEN = "seu_token"
python src/providers/cloudflare_workers_ai.py --prompt "descrição visual detalhada" --width 1024 --height 1792 --output output/scenes/scene-01.png
```

Opcionalmente, use `--seed 1234` para solicitar uma seed reproduzível. O script verifica as credenciais, envia multipart, valida a resposta PNG e salva o arquivo. O padrão é 1024×1792, proporção 9:16; o modelo aceita dimensões entre 256 e 1920.

## Custos e limites

Workers AI oferece uma franquia diária gratuita de 10.000 Neurons. O consumo depende do tamanho de saída; confira a tabela atual de preços antes de gerar lotes. Ao esgotar a franquia no plano gratuito, novas chamadas podem falhar até a renovação diária. O adaptador não faz geração automática em lote nem repete chamadas que possam cobrar novamente.

## Documentação oficial

- [Modelo FLUX.2 Klein 4B](https://developers.cloudflare.com/workers-ai/models/flux-2-klein-4b/)
- [Exemplo oficial de chamada REST multipart](https://developers.cloudflare.com/changelog/post/2026-01-15-flux-2-klein-4b-workers-ai/)
- [Preços do Workers AI](https://developers.cloudflare.com/workers-ai/platform/pricing/)
