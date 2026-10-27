# Roadmap de produção reutilizável

Este documento descreve a evolução das ferramentas. Inventários de máquinas, saldos, perfis de voz, caminhos pessoais, medições de produções e evidências operacionais devem permanecer em relatórios locais ignorados pelo Git.

1. Preservar o checkout, revisar arquivos não versionados e isolar alterações reutilizáveis em branches próprias.
2. Catalogar recursos por conteúdo, registrar origem e direitos, pesquisar antes de solicitar geração e aplicar seleções à cena por ID.
3. Confirmar alpha nos pixels, preservar original/máscara/recorte e revisar bordas em fundos claro, escuro e quadriculado. Segmentar materiais difíceis exige ferramenta e modelo compatíveis e licenciados.
4. Compilar roteiro, objetivos narrativos, recursos, camadas, idiomas e áudio usando a duração real das tomadas. Manter revisões de texto, ASR, legendas e escuta separadas.
5. Evoluir a fila de provedores com reserva e conciliação de cotas, retomada e importação idempotente. Não repetir geração de resultado incerto. Operação assistida em navegador não equivale a serviço autônomo.
6. Parametrizar motions e direção visual com movimento explicativo, hierarquia tipográfica e áreas seguras; conservar cenas de referência para comparação.
7. Validar arquivo final, revisar qualidade audiovisual e direitos, restaurar backup em destino separado e arquivar mídia fora do Git.

Busca por similaridade, embeddings, segmentação por GPU, dublagem automática e orquestração adicional precisam de benefício medido e licença compatível antes da adoção. Um serviço novo só deve ser introduzido quando resolver uma necessidade concreta sem custo adicional.

As verificações offline estão em `scripts/check_production.py`. Resultado de testes ou término do render não concede aprovação audiovisual nem direitos de publicação.
