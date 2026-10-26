# Provedores de imagem, voz e planejamento

`gemini_orchestrator.py` usa o SDK `google-generativeai` solicitado para transformar um roteiro em um manifesto validado e lotes da fila Cloudflare. Leia [configuração, contratos e limitações](../../docs/gemini-orchestrator.md). A dependência é opcional para os demais provedores e o renderer.

Implementar aqui adaptadores independentes de fornecedor. Contrato proposto:

- entrada: prompt, negative prompt opcional, proporção/dimensões, modelo e caminho de saída;
- saída: arquivo de imagem e metadados (provedor, modelo, prompt, parâmetros, data, dimensões, identificador da geração);
- suporte a falhas/retries com limite, sem expor chave em logs;
- geração e regeneração seletiva por `scene.id`;
- testes com respostas simuladas, sem chamadas pagas.

A configuração usa variáveis de ambiente. Nunca salve chaves de API no Git, no storyboard ou em imagens entregues.
