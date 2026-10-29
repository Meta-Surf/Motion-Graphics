"""Offline entry point: classify a request, plan routes, or verify actual delivery bytes."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from production_workflow import classify, plan_request, delivery_report
from video_contract import read_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    commands=p.add_subparsers(dest='action',required=True)
    c=commands.add_parser('classify');c.add_argument('request')
    c=commands.add_parser('plan');c.add_argument('request',type=Path);c.add_argument('--capabilities',type=Path,required=True)
    c=commands.add_parser('verify');c.add_argument('request',type=Path);c.add_argument('media',type=Path);c.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.action=='classify':result=dict(suggested_kind=classify(a.request))
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
