# Cloudflare no GitHub Actions

Esta integração usa os secrets do repositório. Eles pertencem ao GitHub Actions e **não são automaticamente disponibilizados no Dacol, no terminal local ou nesta conversa**. O workflow injeta os valores somente durante a execução, sem gravá-los nos arquivos do projeto.

## Secrets esperados

Em **Settings → Secrets and variables → Actions**, devem existir:

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

O token deve ter acesso ao Workers AI. Não copie os valores para arquivos versionados nem para logs.

## Gerar imagens para um Short

Para uma sequência de até oito imagens, crie um manifesto JSON em `jobs/pending/<id>.json`, seguindo [image-generation-queue.md](image-generation-queue.md). O push inicia `.github/workflows/cloudflare-image-queue.yml`; a rotina também verifica a fila uma vez por hora.

Após a execução:

1. Abra **Actions → Process Cloudflare image queue** e confira se o job terminou com sucesso.
2. Baixe o artefato `cloudflare-generated-images-<run id>`. Ele fica disponível por sete dias.
3. Extraia os arquivos para a pasta de assets do projeto de edição. O manifesto `asset-manifest.json` registra prompt, modelo, dimensão e seed.
4. Use esses arquivos no Remotion local. O render final permanece no computador de edição e não é enviado ao repositório.

O workflow conclui e move o pedido para `jobs/processed/`. Se as credenciais estiverem ausentes ou inválidas, a etapa Cloudflare falha; os secrets não podem ser lidos de volta pela API, apenas usados pelo workflow. O artefato é a ponte entre geração remota e edição local.

## Checagem sem revelar valores

É possível confirmar que os nomes dos secrets estão registrados em **Settings → Secrets and variables → Actions**; o GitHub não mostra seus valores depois de salvos. A verificação operacional mais segura é uma execução do workflow com um manifesto válido: sucesso na etapa de geração confirma autenticação e autorização, sem imprimir o token.
