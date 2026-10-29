"""Run the canonical offline checks without providers, generation or model downloads."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python-only',action='store_true')
    args=parser.parse_args()
    checks=[[sys.executable,str(ROOT/'scripts'/('test_'+name+'.py'))] for name in (
        'pipeline','orchestration','gemini_orchestrator','asset_library',
        'library_project','hyperframes','production_workflow')]
    if not args.python_only:
        cli=ROOT/'remotion/node_modules/typescript/bin/tsc'
        files=sorted((ROOT/'remotion/src').glob('*.test.ts'))
        checks.extend([['node','--experimental-strip-types','--test',*[str(f) for f in files]],
                       ['node',str(cli),'--noEmit','--project',str(ROOT/'remotion/tsconfig.json')]])
    for command in checks:
        print('Checking '+Path(command[1]).name,flush=True)
        result=subprocess.run(command,cwd=ROOT)
        if result.returncode:return result.returncode
    print('All offline checks passed. Editorial approval remains separate.')
    return 0

if __name__=='__main__':raise SystemExit(main())
