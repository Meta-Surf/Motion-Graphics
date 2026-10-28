"""Local ASR/cutouts with pinned models. No provider calls or automatic quality approval."""
from pathlib import Path
import argparse,json,os,subprocess,tempfile
from hyperframes_models import install,verify
ROOT=Path(__file__).resolve().parents[1]

def transcribe(source,output,model,whisper):
    specs=json.loads((ROOT/'hyperframes/models.json').read_text())['models']
    if not verify(model,specs['whisper-base.en']):raise ValueError('Whisper model is not the verified registry version')
    if not whisper.is_file():raise ValueError('Provide the local whisper.cpp executable with --whisper')
    # HyperFrames resolves its Whisper model in this documented cache; reuse verified bytes.
    install('whisper-base.en',Path.home()/'.cache/hyperframes/whisper/models',source=model)
    cli=ROOT/'hyperframes/node_modules/.bin'/('hyperframes.cmd' if os.name=='nt' else 'hyperframes')
    env=os.environ.copy();env['HYPERFRAMES_WHISPER_PATH']=str(whisper.resolve())
    with tempfile.TemporaryDirectory(prefix='motion-asr-') as temp:
        result=subprocess.run([str(cli),'transcribe',str(source.resolve()),'--dir',temp,'--engine','whisper','--model','base.en','--language','en','--no-runtime-install','--json'],env=env,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=300)
        result.check_returncode();data=json.loads(result.stdout)
        if data.get('ok') is not True:raise RuntimeError('Transcription did not produce a successful transcript: '+str(data))
        path=Path(data['transcriptPath']).resolve()
        if not path.is_relative_to(Path(temp).resolve()):raise RuntimeError('Unexpected transcript output path')
        words=json.loads(path.read_text(encoding='utf-8'))
    from sys import path as imports
    imports.insert(0,str(ROOT/'src'));from hyperframes_bridge import group_words
    # Validate ordering/positive finite intervals before exposing a transcript to the compiler.
    group_words(words,max((w['end'] for w in words),default=0))
    with output.open('x',encoding='utf-8') as f:json.dump(words,f,indent=2,ensure_ascii=False)
    return dict(output=str(output),words=len(words),review='Compare recognized text to script before caption compilation')

def cutout(source,output,model):
    from PIL import Image
    import numpy as np
    spec=json.loads((ROOT/'hyperframes/models.json').read_text())['models']['u2netp']
    if not verify(model,spec):raise ValueError('U2-NetP model checksum mismatch; run hyperframes_models.py')
    sidecar=output.with_suffix('.qa.json')
    if sidecar.exists():raise ValueError('QA sidecar exists')
    image=Image.open(source).convert('RGB');pixels=np.asarray(image.resize((320,320),Image.Resampling.LANCZOS)).astype('float32')
    pixels=pixels/max(float(pixels.max()),1)
    pixels=(pixels-np.array([.485,.456,.406],dtype='float32'))/np.array([.229,.224,.225],dtype='float32')
    with tempfile.TemporaryDirectory(prefix='motion-mask-') as temp:
        inp=Path(temp)/'input.bin';out=Path(temp)/'mask.bin';pixels.transpose(2,0,1).copy().tofile(inp)
        subprocess.run(['node',str(ROOT/'hyperframes/segment.cjs'),str(model.resolve()),str(inp),str(out)],check=True,timeout=120)
        pred=np.fromfile(out,dtype='float32').reshape(320,320)
    if not np.isfinite(pred).all():raise ValueError('Model produced non-finite alpha')
    pred=(pred-pred.min())/max(float(pred.max()-pred.min()),1e-8)
    mask=Image.fromarray((pred*255).astype('uint8')).resize(image.size,Image.Resampling.LANCZOS)
    result=image.convert('RGBA');result.putalpha(mask)
    # File opened exclusively prevents replacing an existing asset in concurrent runs.
    with output.open('xb') as f:result.save(f,format='PNG')
    bbox=mask.getbbox();qa=dict(model='u2netp',provider='cpu',approval='pending',alpha_bbox=bbox,
        edge_contact=bool(bbox and (bbox[0]==0 or bbox[1]==0 or bbox[2]==image.width or bbox[3]==image.height)),
        required_review=['object integrity','missing parts','halos','light/dark/contrasting backgrounds'])
    with sidecar.open('x',encoding='utf-8') as f:json.dump(qa,f,indent=2)
    return dict(output=str(output),qa=qa)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['transcribe','cutout']);p.add_argument('input',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--model',type=Path);p.add_argument('--whisper',type=Path);a=p.parse_args()
    if not a.input.is_file():p.error('Input missing')
    if a.output.exists():p.error('Output exists; never overwrite a source asset')
    if a.action=='cutout' and a.output.suffix.lower()!='.png':p.error('Cutouts must be PNG')
    from hyperframes_cli import local_environment
    if a.model is None:a.model=Path.home()/'.cache/motion-graphics/models'/('ggml-base.en.bin' if a.action=='transcribe' else 'u2netp.onnx')
    if a.action=='transcribe' and a.whisper is None:
        configured=local_environment().get('HYPERFRAMES_WHISPER_PATH')
        if not configured:p.error('Provide --whisper or configure ignored hyperframes/local.json')
        a.whisper=Path(configured)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    print(json.dumps(transcribe(a.input,a.output,a.model,a.whisper) if a.action=='transcribe' else cutout(a.input,a.output,a.model)))
