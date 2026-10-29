"""Verify, reuse or explicitly download the small model registry. No binary is stored in Git."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, tempfile, urllib.request
ROOT=Path(__file__).resolve().parents[1]

def verify(path, spec):
    path=Path(path)
    if not path.is_file() or path.stat().st_size!=spec['bytes']:return False
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()==spec['sha256']

def install(name,cache,source=None,download=False):
    specs=json.loads((ROOT/'hyperframes/models.json').read_text())['models']
    if name not in specs:raise ValueError('Unknown model')
    spec=specs[name];cache=Path(cache).resolve();dest=cache/spec['filename']
    if dest.exists():
        if not verify(dest,spec):raise ValueError('Existing cached model failed verification; it was not overwritten')
        return dest
    if source is None and not download:raise ValueError('Pass --from-file to reuse or --download explicitly')
    if source is not None and not verify(source,spec):raise ValueError('Source checksum/size mismatch')
    cache.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=spec['filename']+'.',suffix='.partial',dir=cache);os.close(fd)
    temp=Path(tmp)
    try:
        if source is not None:
            temp.unlink()
            try:os.link(source,temp)
            except OSError:shutil.copyfile(source,temp)
        else:
            with urllib.request.urlopen(spec['url'],timeout=60) as remote,temp.open('wb') as out:
                count=0
                while block:=remote.read(1024*1024):
                    count+=len(block)
                    if count>spec['bytes']:raise ValueError('Download exceeded pinned model size')
                    out.write(block)
        if not verify(temp,spec):raise ValueError('Downloaded model checksum/size mismatch')
        # Exclusive creation handles concurrent installers without overwriting a model.
        try:os.link(temp,dest)
        except FileExistsError:
            if not verify(dest,spec):raise ValueError('Concurrent cache write failed verification')
    finally:temp.unlink(missing_ok=True)
    return dest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('name',choices=['whisper-base.en','u2netp']);p.add_argument('--cache',type=Path,default=Path.home()/'.cache/motion-graphics/models');p.add_argument('--from-file',type=Path);p.add_argument('--download',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.from_file and a.download:p.error('Choose reuse or download, not both')
    if a.check:
        spec=json.loads((ROOT/'hyperframes/models.json').read_text())['models'][a.name];path=a.cache/spec['filename'];ok=verify(path,spec);print(json.dumps(dict(path=str(path),ok=ok)));raise SystemExit(0 if ok else 1)
    print(json.dumps(dict(path=str(install(a.name,a.cache,a.from_file,a.download)),verified=True)))
