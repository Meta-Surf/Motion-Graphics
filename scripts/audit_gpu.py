"""Explicit AMF/CPU encode probes; no fallback and no claim of quality equivalence."""
import argparse
import ctypes
import json
import os
import subprocess
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from asset_library import binary, write_json

def process_memory(pid):
    if os.name=='nt':
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_=[('cb',wintypes.DWORD),('faults',wintypes.DWORD)]+[(s,ctypes.c_size_t) for s in ('peak_working','working','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile')]
        kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.restype=wintypes.HANDLE
        kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        psapi=ctypes.WinDLL('psapi');psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
        handle=kernel.OpenProcess(0x1000|0x10,False,pid)
        if not handle:return None
        try:
            counters=Counters();counters.cb=ctypes.sizeof(counters)
            if psapi.GetProcessMemoryInfo(handle,ctypes.byref(counters),counters.cb):return counters.peak_working
        finally:kernel.CloseHandle(handle)
    else:
        try:
            for line in Path(f'/proc/{pid}/status').read_text().splitlines():
                if line.startswith('VmHWM:'):return int(line.split()[1])*1024
        except OSError:pass
    return None

def measured(args,log):
    start=time.perf_counter();peak=0
    with log.open('wb') as stream:
        child=subprocess.Popen(args,stdout=stream,stderr=stream)
        try:
            while child.poll() is None:
                peak=max(peak,process_memory(child.pid) or 0)
                if time.perf_counter()-start>120:child.kill();child.wait();raise TimeoutError('GPU probe exceeded 120 seconds')
                time.sleep(.05)
        finally:
            if child.poll() is None:child.kill();child.wait()
    return dict(exit_code=child.returncode,seconds=round(time.perf_counter()-start,3),peak_process_ram_bytes=peak or None,vram_bytes=None,vram_note='Not measured; driver counter sampling not yet implemented',log=log.name)

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'output/maintenance/audit-20261027/gpu');a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    lock=Path(os.getenv('MOTION_GPU_LOCK',str(Path.home()/'MotionLibrary/gpu.lock')));lock.parent.mkdir(parents=True,exist_ok=True)
    with lock.open('x') as f:f.write(str(os.getpid()))
    try:
        ffmpeg=binary('ffmpeg');report=dict(device='Configure the target adapter; encoder success alone does not identify the device',fallback=False,probes=[])
        for encoder,backend,options in [('h264_amf','AMF',['-quality','quality','-rc','cqp','-qp_i','20','-qp_p','20']),('libx264','CPU-explicit',['-crf','18','-preset','medium'])]:
            path=a.output/(encoder+'.mp4')
            if path.exists():raise ValueError('Probe output already exists; choose a new output directory')
            args=[ffmpeg,'-v','info','-f','lavfi','-i','testsrc2=size=1280x720:rate=30','-t','2','-an','-c:v',encoder,*options,'-pix_fmt','yuv420p',str(path)]
            result=measured(args,a.output/(encoder+'.log'));result.update(encoder=encoder,backend=backend,width=1280,height=720,frames=60)
            if result['exit_code']==0:
                result['bytes']=path.stat().st_size
                result['decode']=measured([ffmpeg,'-v','error','-i',str(path),'-f','null','-'],a.output/(encoder+'-decode.log'))
            report['probes'].append(result)
        report['comparison']='Capability and elapsed time only. AMF CQP20 and x264 CRF18 are not equivalent quality; no speed superiority conclusion.'
        write_json(a.output/'report.json',report);print(json.dumps(report,indent=2))
    finally:lock.unlink(missing_ok=True)
if __name__=='__main__':main()
