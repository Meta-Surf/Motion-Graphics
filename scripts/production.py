"""Offline entry point: classify a request, plan routes, or verify actual delivery bytes."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from production_workflow import KINDS, classify, new_request, plan_request, delivery_report
from video_contract import read_json, probe, file_digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    commands=p.add_subparsers(dest='action',required=True)
    c=commands.add_parser('doctor');c.add_argument('--output',type=Path,required=True)
    c=commands.add_parser('init');c.add_argument('request');c.add_argument('--project-id',required=True);c.add_argument('--kind',choices=KINDS);c.add_argument('--output',type=Path,required=True)
    c=commands.add_parser('classify');c.add_argument('request')
    c=commands.add_parser('inspect');c.add_argument('sources',type=Path,nargs='+')
    c=commands.add_parser('plan');c.add_argument('request',type=Path);c.add_argument('--capabilities',type=Path,required=True)
    c=commands.add_parser('verify');c.add_argument('request',type=Path);c.add_argument('media',type=Path);c.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.action=='doctor':
        if a.output.exists():p.error('Inventory output exists; choose a new version')
        from production_doctor import inventory
        result=inventory();a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    elif a.action=='init':
        if a.output.exists():p.error('Request exists; edit or resume that request instead')
        result=new_request(a.request,a.project_id,a.kind);a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    elif a.action=='classify':result=dict(suggested_kind=classify(a.request))
    elif a.action=='inspect':result=dict(sources=[dict(path=str(path.resolve()),sha256=file_digest(path),media=probe(path,'ffprobe')) for path in a.sources])
    elif a.action=='plan':result=plan_request(read_json(a.request),read_json(a.capabilities))
    else:
        if a.output.exists():p.error('Evidence output exists; choose a new version')
        result=delivery_report(a.media,read_json(a.request))
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if a.action=='verify':return 0 if result['delivery']=='approved' else 2
    return 0

if __name__=='__main__':raise SystemExit(main())
