"""Run installed offline checks without generating media or consuming provider quotas."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
checks=['test_asset_library.py','test_library_project.py','test_pipeline.py','test_orchestration.py','test_gemini_orchestrator.py','test_flow_queue.py','test_flow_bridge.py']
results=[]
for name in checks:
    if not (ROOT/'scripts'/name).exists():continue
    start=time.perf_counter()
    result=subprocess.run([sys.executable,str(ROOT/'scripts'/name)],cwd=ROOT,capture_output=True,text=True,errors='replace',timeout=180)
    results.append(dict(check=name,exit_code=result.returncode,seconds=round(time.perf_counter()-start,3),output=result.stdout+result.stderr))
for name in ['test','typecheck']:
    start=time.perf_counter();result=subprocess.run(['npm.cmd' if os.name=='nt' else 'npm','run',name],cwd=ROOT/'remotion',capture_output=True,text=True,errors='replace',timeout=180)
    results.append(dict(check='npm '+name,exit_code=result.returncode,seconds=round(time.perf_counter()-start,3),output=result.stdout+result.stderr))
output=ROOT/'output/maintenance/audit-20261027/checks.json';output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for result in results:print(json.dumps({k:v for k,v in result.items() if k!='output'}))
print('Details: '+str(output))
sys.exit(1 if any(r['exit_code'] for r in results) else 0)
