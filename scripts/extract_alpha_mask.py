"""Preserve a verified cutout and register its actual alpha as a separate mask variant.
This is CPU alpha extraction, not AI segmentation or reconstruction of hidden surfaces.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from asset_library import Library, binary, sha

def extract(library, ident):
    original=library.get(ident);source=library.path(original['file'])
    if sha(source)!=original['sha256']:raise ValueError('Source hash mismatch')
    if original['metadata'].get('alpha')!='transparent':raise ValueError('No real transparent pixels to extract')
    with tempfile.TemporaryDirectory(prefix='alpha-',dir=library.root) as directory:
        mask=Path(directory)/'mask.png'
        subprocess.run([binary('ffmpeg'),'-v','error','-i',str(source),'-vf','alphaextract','-frames:v','1',str(mask)],check=True,timeout=120)
        result=library.import_file(mask,dict(description=original['description']+' alpha mask',tags=['mask','alpha'],provider='local-ffmpeg',model=None,parameters={'filter':'alphaextract','backend':'CPU-explicit'},source_asset_id=ident,license=original['license'],rights=original['rights']),category='mask')
        library.link(ident,result['id'],'mask')
    return result['id']

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('asset_id');p.add_argument('--root',type=Path);a=p.parse_args();l=Library(a.root)
    try:print(json.dumps(dict(mask_asset_id=extract(l,a.asset_id),backend='CPU-explicit')))
    finally:l.close()
