# Instruções permanentes de produção

Leia `docs/production-procedure.md` antes de iniciar um pedido de vídeo. Use o
manifesto `schemas/production-request.schema.json`; ele coordena decisões e não é
um substituto das props de render. Não presuma integração a partir de um catálogo.

1. Inspecione Git, worktrees e fontes antes de mudar qualquer coisa. Preserve
   arquivos privados, produções existentes e branches locais. Use nova branch e
   worktree quando houver produção ou mudanças em andamento. Não faça reset/stash
   automático nem sincronize um checkout sujo por cima de trabalho do usuário.
2. Classifique criação, edição, corte, motion, revisão ou atualização. Infira o
   que o pedido e a inspeção comprovarem. Pergunte somente decisões ausentes;
   sugestões não são aprovações. Registre o briefing e sua origem.
3. Em qualquer nova edição editonny: leia a skill instalada, faça preflight e
   inspeção; apresente o cartão completo e aguarde uma resposta explícita posterior.
   O pedido inicial não aprova o cartão. Não crie workspace ou render editorial
   antes dessa resposta. Diagnósticos sintéticos de instalação são outro escopo.
4. Reutilize mídia real e assets aprovados adequados. Para novos motions avalie
   HyperFrames primeiro; use Remotion para composições existentes e capacidades
   que sua amostra atender melhor. Registre requisito e motivo da exceção.
   `photo_essay/layers` têm ponte HyperFrames; 21 aliases Gemini não têm binding
   automático. Nunca traduza um padrão para outro silenciosamente.
5. VoiceStudio no DACOL: confirme o dispositivo AMD/ROCm ao vivo, perfil autorizado,
   idioma e speed=1 antes de gerar. Sem troca silenciosa de voz, CPU ou velocidade.
   Concat só recebe timeline nativa após teste de importação e reabertura; não é
   anunciado como encoder. Serviços pagos precisam de provedor e limite aprovados.
6. Aprove roteiro, cenas, fontes, planos de assets/áudio e critérios; produza e meça
   uma amostra representativa antes do render integral. Separe aceleração de
   navegador, inferência, efeitos e encoder. Serialize trabalhos pesados pelo
   mesmo `MOTION_GPU_LOCK`, inclusive entre worktrees; aplicativos independentes
   precisam de coordenação operacional. Não remova lock vivo.
7. Registre origem, direitos/licença, modelo/prompt quando aplicável, hashes,
   destino, versões e decisões. Reuse cache verificado; renderize apenas blocos
   afetados. Valide os bytes finais, reprodução, imagem, escuta, sincronismo e
   legendas. CI ou FFprobe não aprovam aparência e conteúdo.
8. Entregue MP4 aprovado mais projeto editável, fontes selecionadas, manifesto,
   legendas solicitadas e evidências. Não versione credenciais, referências de
   voz, mídia privada, modelos, bancos ou renders. Uma limitação medida deve ser
   registrada como tal, sem promover ferramenta apenas instalada a produção.

A versão operacional única é `main`. O checkout principal do DACOL deve apontar
para o mesmo commit aprovado. Integrações temporárias são consolidadas e removidas
após validação; fontes de projetos privados e histórico Git são preservados.

Checks: `python scripts/check_project.py` executa as suites Python, Remotion e o
typecheck sem serviços de geração. Use `--python-only` em ambientes sem Node.
A suite Gemini requer `scripts/requirements-gemini.txt`. Não execute geração paga
em testes. Comece um briefing com `production.py init`, sem usar o diagnóstico
sintético como se fossem decisões de um pedido real.
