"""Pinned project CLI with ignored local runtime selection and local-only deployment guard."""
from pathlib import Path
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
REMOTE={'cloud','lambda','cloudrun','publish'}

def local_environment(root=ROOT):
    config=root/'hyperframes/local.json'
    settings=json.loads(config.read_text(encoding='utf-8-sig')) if config.exists() else {}
    env=os.environ.copy()
    if settings.get('whisper_executable') and not env.get('HYPERFRAMES_WHISPER_PATH'):
        path=Path(settings['whisper_executable'])
        if not path.is_file():raise ValueError('Configured whisper.cpp executable missing')
        env['HYPERFRAMES_WHISPER_PATH']=str(path.resolve())
    return env

def main(arguments=None):
    arguments=sys.argv[1:] if arguments is None else arguments
    if arguments and arguments[0] in REMOTE:raise ValueError('This integration is local-only; cloud rendering and publishing are disabled')
    cli=ROOT/'hyperframes/node_modules/.bin'/('hyperframes.cmd' if os.name=='nt' else 'hyperframes')
    if not cli.is_file():raise ValueError('Run npm ci --prefix hyperframes first')
    return subprocess.run([str(cli),*arguments],cwd=ROOT,env=local_environment()).returncode
if __name__=='__main__':sys.exit(main())
