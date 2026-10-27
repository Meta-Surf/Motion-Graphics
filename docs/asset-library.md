# Biblioteca permanente e montagem por seleções

A biblioteca padrão fica em `~/MotionLibrary`. Configure `MOTION_LIBRARY_ROOT` ou `--root` na CLI. Não a coloque em `output`, `renders`, temporários ou dentro do checkout. Nenhum original é movido ou excluído.

Use o Python da `.venv` do projeto para o compilador e os testes que dependem de `jsonschema`. Biblioteca, galeria e backup usam somente a biblioteca padrão e o FFmpeg/ffprobe já instalados. Não reinstale o ambiente.

```powershell
cd "$env:USERPROFILE\Projects\Motion-Graphics"
python src/asset_library.py import CAMINHO_DOS_RECURSOS
python scripts/import_existing_assets.py CAMINHO_DA_PASTA_DE_ASSETS
python scripts/register_motion_references.py
python src/asset_library.py search "objeto"
python src/library_server.py
```

Abra `http://127.0.0.1:8770`. Pesquise descrição/tags, filtre categoria e revisão, selecione um item e inspecione suas bordas sobre fundos claro, escuro e quadriculado. Informe projeto, cena e camada e clique **Aplicar à cena**. A escolha salva IDs em `projects/<projeto>/resources.json`; o compilador resolve arquivos automaticamente. `background` seleciona o fundo, `motion` escolhe uma referência de template e os demais nomes selecionam camadas transparentes. O acesso é exclusivamente loopback, com validação de Host/Origin e token por processo para alterações. Não exponha a porta pela VPS.

Recursos pendentes só podem ser aplicados em **prévia explícita**. Isso não concede direitos de publicação. A galeria ainda não edita a revisão; use a CLI com evidências reais:

```powershell
python src/asset_library.py review ID --approval pending --license unknown --rights unknown --notes "bordas pendentes de revisão"
python src/asset_library.py apply ID meu-projeto scene-one object --preview
python scripts/extract_alpha_mask.py ID_DO_RECORTE
```

Somente aprove com licença, evidência de direitos e notas de revisão. Licença informada é uma declaração do operador; não é verificada automaticamente contra o provedor. Uma duplicata mantém todos os caminhos de origem e seus metadados separados, sem sobrescrever a revisão anterior. Sidecars reconhecidos preservam prompt, modelo, seed, operação e origem quando disponíveis; dados ausentes continuam desconhecidos. A licença de um arquivo duplicado não é deduzida do hash.

## Contrato e Remotion

`schemas/production-plan.schema.json` adiciona um plano por projeto e idioma. Cada cena declara objetivo, texto, recurso de áudio por ID, recursos necessários, composição e motivo de geração (vazio quando nenhuma geração é necessária). `voices` registra o perfil e a evidência de aprovação por idioma. Planos com IDs e metadados de produções devem permanecer em pastas locais ignoradas pelo Git.

```powershell
.venv\Scripts\python.exe src/compile_library_project.py output/meu-projeto/plan.json --language pt-BR --preview --output output/meu-projeto/composition.json
.venv\Scripts\python.exe scripts/render_library_project.py output/meu-projeto/composition.json --output output/meu-projeto/video-v002.mp4
```

A ponte produz o contrato **AiVideo existente**, com campos opcionais `layers` e `highlight_cues`. As composições antigas permanecem válidas. WAVs PCM são medidos em amostras; a timeline arredonda para frames e acrescenta apenas o silêncio de borda. Fala maior que a duração solicitada causa erro. Não há aceleração nem corte automáticos. A montagem exporta cópias verificadas para `remotion/public/generated/library/`, com caminhos portáveis para `staticFile()` e manifesto de origem/QA ao lado da narração.

Cues são opcionais e devem caber no áudio real. Cues por tomada não equivalem a legendas alinhadas palavra a palavra. Dublagem traduzida, mix de música/SFX e alinhamento automático continuam pendentes neste adaptador; os caminhos anteriores de áudio permanecem disponíveis. Referências de voz não são copiadas para GitHub.

`ReusableLayers` acrescenta recortes independentes, profundidade por camadas e destaques por cues. Isso não reconstrói verso de objetos ou geometria 3D. As seis referências de motions guardam fonte, export, template e hash do código; alterações na fonte exigem registrar novamente a referência. O fingerprint de render inclui as imagens das camadas para impedir reutilização de chunks com mídia alterada.

## Integridade e restauração

O catálogo usa SQLite/FTS5, IDs por conteúdo SHA-256, objetos imutáveis, origens, relações de variantes, revisões, eventos e utilização por projeto/cena/camada. Busca semântica e similaridade visual ainda não foram adotadas: falta medir benefício e validar modelo/licença. Inspeção de alpha decodifica pixels reais; um PNG totalmente transparente é marcado `empty`, não um recorte utilizável. Clipes ficam com alpha não verificado.

```powershell
python src/asset_library.py verify
python src/asset_library.py backup "$env:USERPROFILE\MotionLibraryBackups\NOVA_VERSAO"
python src/asset_library.py restore "$env:USERPROFILE\MotionLibraryBackups\NOVA_VERSAO" "$env:USERPROFILE\MotionLibraryRestoreTests\NOVA_VERSAO"
```

Backup bloqueia escritores, usa a API de backup do SQLite e copia objetos, thumbnails e seleções com checksums. A restauração exige destino inexistente e confere hashes antes de copiar, integridade SQLite e objetos após restaurar. Um backup incompleto não tem `backup.json` válido. O backup local no mesmo disco protege contra erros de operação; não protege contra perda do disco. Uma segunda cópia externa ainda precisa ser configurada.

Se houver `catalog.lock` ou `gpu.lock` após interrupção, confira PID/processos antes de remover apenas o lock órfão. Não apague banco ou mídia. Os novos wrappers coordenam GPU entre si; não controlam chamadas feitas diretamente a VoiceStudio por outros clientes.

## Verificação

```powershell
.venv\Scripts\python.exe scripts/check_production.py
```

Os doze testes novos usam mídia sintética local e verificam identidade/deduplicação, integridade, restauração adulterada, fronteiras da galeria, exportação, aprovação, idioma e preservação das amostras da fala. A revisão audiovisual humana continua independente dos testes.
