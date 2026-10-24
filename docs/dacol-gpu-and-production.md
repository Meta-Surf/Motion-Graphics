# DACOL: voz por GPU e produção independente

## Correção de 24/10/2026

A auditoria inicial verificou o aplicativo Windows em localhost:3900. Ele tem PyTorch 2.8.0+cu128 e não usa a Radeon. Havia, porém, uma instalação ROCm previamente funcional no Ubuntu-24.04/WSL2, em localhost:3901. Não foi necessário trocar o motor nem instalar uma nova distribuição.

Condições encontradas: distribuição WSL parada, serviço `voicestudio-gpu` desabilitado e inativo. O cliente do último Short apontava para o aplicativo Windows em 3900. Os logs mostram parada do serviço WSL; não determinam quem iniciou essa parada.

Correções aplicadas:

- `systemctl enable --now voicestudio-gpu` no Ubuntu existente.
- Inicialização por usuário no logon do Windows, através de `scripts/install-voice-startup.ps1`.
- Processo de manutenção da sessão WSL: serviços systemd sozinhos não impedem o encerramento da distribuição.
- Provedor `src/providers/voicestudio.py` usa 3901 e exige dispositivo GPU antes de cada tomada; não faz fallback silencioso para CPU.
- Perfil do narrador salvo no serviço GPU usando o áudio de referência da produção aprovada e transcrição conferida por ASR. O texto anterior era maior que o áudio de referência.

## Resultados reais

- PyTorch WSL: `2.9.1+rocm7.2.1.gitff65f5bc`, HIP `7.2.53211-e1a6bc5663`.
- GPU: AMD Radeon RX 7800 XT, teste matricial 512×512 com resultado finito.
- Health: `cuda (AMD Radeon RX 7800 XT)`. A palavra CUDA é o nome da API exposta pelo PyTorch, não indica uma placa NVIDIA neste ambiente.
- Geração sem referência: 8,64 s de áudio em 16,848 s, 16 passos.
- Geração com referência do canal: 7,84 s de áudio em 24,06 s, 32 passos.
- ASR da amostra clonada: 4,07 s; texto retornado corresponde ao solicitado, sem palavras adicionais.

Estes são testes curtos com o modelo disponível. Não são uma comparação medida contra CPU nem garantem tempo linear em roteiros longos. Escuta e aprovação de timbre continuam necessárias. O logon automático foi configurado; não reiniciamos o Windows para testá-lo.

## Pastas e comandos

Checkout do projeto no DACOL:

`C:\Users\marco\Projects\Motion-Graphics`

As produções anteriores em Videos/Artificial Curiosity e Videos/CanalVideos permanecem nos seus caminhos. O novo repositório guarda ferramentas e templates, não incorpora os episódios anteriores.

```powershell
cd 'C:\Users\marco\Projects\Motion-Graphics'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/start-voice-gpu.ps1
python src/providers/voicestudio.py --health
cd remotion
npm.cmd run studio
npm.cmd run preview:library
```

O health deve informar AMD. Se informar CPU, a geração é bloqueada para corrigirmos o serviço antes de gastar tempo.

## Voz

```powershell
python src/providers/voicestudio.py --script roteiro.txt --profile-id ID_DO_PERFIL_APROVADO --output review/narracao.wav
```

O provedor gera frases curtas sequencialmente, salva cache e registra tempos/durações. A velocidade é 1,0; não acelera nem corta a fala para caber no vídeo. Alterações do perfil invalidam o cache. A montagem das cenas deve usar a duração real da locução.

O teste de ASR da referência corrigiu uma divergência concreta: o texto antigo incluía frases que não cabiam no recorte usado. Nenhuma referência de voz entra no Git.

## Renders AMD

No diretório remotion:

```powershell
npm.cmd run render:amf -- --composition MotionLibraryDemo --silent-preview --output renders/motion-library-preview-v001.mp4 --ffmpeg CAMINHO_FFMPEG
```

Para produção, passe `--voice CAMINHO_WAV` e `--ffprobe CAMINHO_FFPROBE`, sem `--silent-preview`. O exportador usa metadata resolvida pelos props, renderiza frames por Chrome/ANGLE, codifica H.264 AMF e chama o finalizador. A saída existente não é sobrescrita. Caso a composição também contenha música/SFX, forneça o mix completo como WAV: o caminho AMF não extrai automaticamente a mixagem do React.

`scripts/finalize_short.py` preserva a fala, normaliza e inclui AAC. Rejeita narração maior que o vídeo, arquivo final sem áudio, dimensão/codec/duração fora do alvo e erros de decodificação. A aprovação técnica não substitui escuta e revisão visual.

## Limitação ASR observada nos logs

Uma transcrição longa anterior excedeu o watchdog de 300 s enquanto TTS e ASR compartilhavam a GPU. Para revisão, processe trechos ou descarregue o TTS antes de transcrições longas. Não execute simultaneamente geração de voz e uma transcrição longa. O novo provedor gera de forma sequencial e não modifica o runtime do VoiceStudio.

## Verificações da primeira implementação

- Nove testes TypeScript, quatro testes Python e typecheck passaram.
- Finalizador testado com fixture técnica de 30 s: H.264/AAC, decodificação completa aprovada; a fixture não é um Short editorial.
- Seis stills da biblioteca renderizados e inspecionados.
- Catálogo de 34 s: 1.020 frames, Chrome/ANGLE + H.264 AMF, exportado em aproximadamente 63 s (primeira execução medida).
- Provedor de voz: trecho de 3,52 s em 8,777 s; segunda chamada reutilizou cache sem nova inferência.
- Dependência Zod atualizada por override compatível; npm audit sem vulnerabilidades na verificação local.
- Exportador declara Rec.709 e faixa de vídeo limitada para consistência entre players.

## Correção da referência e revisão de cada tomada

A revisão integral identificou vazamento de “Creators” em algumas tomadas, vindo do fim de um recorte de referência que terminava durante o nome YouTube Create. Uma amostra curta havia passado; ela não era suficiente para aprovar a referência inteira.

Usamos a transcrição com timestamps para encontrar o fim da primeira frase: “artificial?” termina em aproximadamente 4,68 s, e a frase seguinte começa em 5,00 s. O novo recorte tem 5,00 s, encerra uma frase completa e inclui sua pausa final. A transcrição fornecida ao clone corresponde apenas a essa frase. Duas tomadas de teste com a nova referência retornaram exatamente o texto pedido.

O provedor agora transcreve cada tomada antes de aceitá-la no áudio montado. Ele bloqueia “Create/Creator/Creators” quando não constam do texto e divergências grandes em relação ao roteiro. As revisões ficam em cache junto aos WAVs; alterar a referência invalida o cache. ASR continua sendo uma triagem, não uma prova de pronúncia ou uma substituição da escuta. O contador atual é de nove testes TypeScript e quatro testes Python.
