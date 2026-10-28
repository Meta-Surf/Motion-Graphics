"""Catalog references to the six existing AiVideo templates, without copying source code."""
import json
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from asset_library import Library,sha
if __name__=='__main__':
    library=Library()
    try:
        result=[];source='remotion/src/MotionTemplates.tsx'
        for template in ('layers','object3d','dataflow','cutaway','scale','compare'):
            reference=dict(kind='remotion-component',source=source,source_sha256=sha(ROOT/source),export='MotionTemplate',template_id=template)
            with tempfile.TemporaryDirectory(dir=library.root,prefix='reference-') as folder:
                path=Path(folder)/(template+'.motionref');path.write_text(json.dumps(reference,sort_keys=True),encoding='utf-8')
                asset=library.import_file(path,dict(description='Remotion '+template,tags=['motion',template],origin=source,license='repository-owner-use; distribution license undecided',rights='Reference to existing project code; see LICENSE-CHOICE.md'),category='component')
                result.append(asset['id'])
        print(json.dumps(result))
    finally:library.close()
