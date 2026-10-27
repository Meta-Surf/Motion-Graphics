# Decisões do ciclo de biblioteca

- **Armazenamento:** SQLite FTS5 e objetos em disco fora da produção, sem novos pacotes Python. IDs SHA-256 identificam conteúdo; caminhos originais e metadados de cada origem permanecem separados.
- **Preservação:** copiar e verificar antes de registrar; nunca mover originais. Duplicação não prova equivalência de licença. Revisão pendente é o padrão.
- **Portabilidade:** o catálogo usa caminhos relativos para seus objetos; exportação ao Remotion copia os arquivos necessários por hash. Caminhos pessoais só ficam no registro local de origem.
- **Contratos:** adaptar o plano por idiomas ao AiVideo existente; adicionar camadas e cues opcionais sem invalidar composições anteriores. Usar WAV real e silêncio de borda, sem ajustar a velocidade da voz.
- **Geração:** pesquisar primeiro, manter o motivo de solicitação no plano. A nova ponte não chama provedores; Flow segue assistido. Não duplicar sua fila só para acrescentar estados cosméticos.
- **GPU:** conservar VoiceStudio ROCm e AMF existentes. Guardar erros de aceleração e parar se o diagnóstico do novo wrapper não confirmar hardware; perfis CPU são explícitos. Extração de alpha não é inferência de segmentação.
- **Licenças:** nenhum modelo, fonte, música ou plugin novo adotado. A instalação Remotion 4.0.538 permite uso gratuito por indivíduo, organização com até três empregados, entidade sem fins lucrativos ou avaliação não comercial; a elegibilidade jurídica não foi auditada. Fontes do sistema não são redistribuídas. O repositório mantém `LICENSE-CHOICE.md` e nenhuma licença aberta foi imposta. Licenças dos pesos de voz, termos atuais de saída dos provedores e direitos de imagens importadas precisam de revisão antes de aprovação editorial.
- **Segurança local:** galeria somente em loopback, token para alterações e validação de origem; não guardar sessão Google. Catálogo, backups, referências de voz, mídia grande e relatórios privados ficam fora do Git.
- **Backup:** snapshot consistente via SQLite e cópia dos objetos sob lock; restauração em pasta nova e validação de hashes antes e depois. Backup no mesmo disco não substitui segunda cópia externa.
- **Validação:** testes pequenos de integridade e contratos, mais revisão de frames e provas de alpha. O término do render só aprova a parte técnica; escuta e revisão visual são decisões separadas.
