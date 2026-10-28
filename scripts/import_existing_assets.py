"""Idempotent import of an explicit asset folder with available provenance sidecars."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from asset_library import Library, MEDIA
KEYS={'prompt','model','provider','seed','parameters','license','rights','origin','source','role','description','tags','operation','bbox','visual_review'}

def import_folder(library, folder):
    folder=Path(folder).resolve();provenance={}
    for sidecar in folder.rglob('*.json'):
        if any(p in ('.git','node_modules','.venv') for p in sidecar.parts):continue
        try:data=json.loads(sidecar.read_text(encoding='utf-8-sig'))
        except (ValueError,OSError):continue
        records=data if isinstance(data,list) else data.get('assets',[data]) if isinstance(data,dict) else []
        for record in records:
            if not isinstance(record,dict):continue
            name=record.get('file') or record.get('filename')
            if name:
                candidates={(sidecar.parent/str(name)).resolve(),(sidecar.parent/Path(name).name).resolve()}
                matches=[p for p in candidates if p.is_relative_to(folder) and p.is_file()]
                if len(matches)==1:provenance[matches[0]]={k:v for k,v in record.items() if k in KEYS}
    result=[]
    for path in sorted(folder.rglob('*')):
        if any(p in ('.git','node_modules','.venv') for p in path.parts):continue
        if path.is_file() and path.suffix.lower() in MEDIA:
            meta=provenance.get(path.resolve(),{})
            meta=dict(meta,origin=str(path),description=meta.get('description',path.stem),tags=meta.get('tags',['legacy-import']))
            asset=library.import_file(path,meta)
            result.append(dict(id=asset['id'],description=asset['description'],alpha=asset['metadata']['alpha']))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);p.add_argument('--root',type=Path);a=p.parse_args()
    if not a.folder.is_dir():p.error('Asset folder must exist')
    library=Library(a.root)
    try:print(json.dumps(import_folder(library,a.folder),ensure_ascii=False,indent=2))
    finally:library.close()
