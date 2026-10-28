# Local reusable asset library

The SQLite/FTS5 library stores media by SHA-256, retains source metadata, rights,
review state and usage records, and exports selected assets to the shared Motion
composition contract. Imports do not move or edit the originals. Keep catalog data,
private media, voice takes and rendered files outside Git.

Use `python src/asset_library.py --help` for import, search, review, apply, verify,
backup and restore. The optional `--root` selects an isolated library; use a fresh
root when experimenting instead of modifying production records.

```powershell
python src/asset_library.py --root library-data/demo import PATH_TO_MEDIA
python src/asset_library.py --root library-data/demo search GPU
python src/asset_library.py --root library-data/demo verify
```

Imported content is not automatically approved for production. Inspect its origin,
license, integrity and visual/audio quality before using the review command.
Transparent pixels alone do not prove an acceptable cutout. Follow each command's
help for required rights/review fields; never invent a license or approval.

`compile_library_project.py` resolves a reviewed production plan and selections to
the same composition JSON consumed by Remotion or the optional HyperFrames bridge.
See [HyperFrames integration](hyperframes.md) for supported templates and the
explicit renderer selector. The default renderer remains Remotion.

Backups include hashes and catalog metadata; restore into a new destination and
verify it before adoption. No automatic migration, publishing, paid generation or
remote production access is performed by this integration's tests.

Offline regression checks:

```powershell
python scripts/test_asset_library.py
python scripts/test_library_project.py
```
