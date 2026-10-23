# Cloudflare Workers AI — geração de imagens

O adaptador usa o modelo `@cf/black-forest-labs/flux-2-klein-4b` pela API REST do Workers AI. O endpoint oficial aceita campos multipart, incluindo prompt e dimensões, e retorna a imagem em Base64.

## Gerar pelo GitHub Actions, sem o Dacol

O workflow `.github/workflows/generate-cloudflare-image.yml` gera uma imagem quando você o executa manualmente. Para cadastrar as credenciais sem compartilhá-las no chat:

1. No repositório, abra **Settings → Secrets and variables → Actions**.
2. Clique em **New repository secret** e cadastre:
   - `CLOUDFLARE_ACCOUNT_ID` — Account ID mostrado no painel Cloudflare.
   - `CLOUDFLARE_API_TOKEN` — token Workers AI criado no painel.
3. Abra **Actions → Generate image with Cloudflare Workers AI → Run workflow**.
4. Informe prompt, largura e altura. Para 9:16, o padrão é 1024×1792.
5. Após a execução, abra o workflow concluído e baixe o artefato `cloudflare-generated-image`.

Os valores de secret são ocultos pelo GitHub e o workflow não os grava no repositório. Nunca os inclua em logs, prompts, arquivos versionados ou mensagens. O adaptador detecta se o retorno é PNG, JPEG ou WebP e salva com a extensão correspondente. O artefato fica disponível por sete dias.

## Gerar localmente

1. Na Cloudflare, abra Workers AI → Use REST API e crie um Workers AI API Token.
2. Defina `CLOUDFLARE_ACCOUNT_ID` e `CLOUDFLARE_API_TOKEN` no ambiente local. Não cole o token no GitHub como arquivo.
3. Python 3.10+ é suficiente; o script usa apenas a biblioteca padrão.

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

Opcionalmente, use `--seed 1234` para solicitar uma seed reproduzível. O script verifica as credenciais, envia multipart, identifica o formato de imagem retornado (PNG, JPEG ou WebP) e salva o arquivo com a extensão correta. O modelo aceita dimensões entre 256 e 1920.

## Custos e limites

Workers AI oferece uma franquia diária gratuita de 10.000 Neurons. O consumo depende do tamanho de saída; confira a tabela atual de preços antes de gerar lotes. Ao esgotar a franquia no plano gratuito, novas chamadas podem falhar até a renovação diária. O adaptador não faz geração automática em lote nem repete chamadas que possam cobrar novamente. O uso de GitHub Actions também está sujeito aos limites e à política do plano do GitHub.

## Documentação oficial

- [Modelo FLUX.2 Klein 4B](https://developers.cloudflare.com/workers-ai/models/flux-2-klein-4b/)
- [Exemplo oficial de chamada REST multipart](https://developers.cloudflare.com/changelog/post/2026-01-15-flux-2-klein-4b-workers-ai/)
- [Preços do Workers AI](https://developers.cloudflare.com/workers-ai/platform/pricing/)
