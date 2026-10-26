"""Measure a rendered reference. Never claims to recover original editor layers.

Optional dependency: opencv-python-headless. ffmpeg/ffprobe must be on PATH.
Run: python scripts/analyze_motion_reference.py input.mp4 --out review/reference
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import wave
from pathlib import Path

import cv2
import numpy as np


def frame_timestamps(source: Path) -> list[float]:
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(source)]))
    return [float(f['best_effort_timestamp_time']) for f in data['frames'] if 'best_effort_timestamp_time' in f]


def contact_pages(thumbs:list, out:Path, per_page:int=48):
    names=[]
    for start in range(0,len(thumbs),per_page):
        page=thumbs[start:start+per_page]
        sheet=np.full((((len(page)+7)//8)*280+10,8*154+10,3),22,np.uint8)
        for j,im in enumerate(page):
            y,x=(j//8)*280+10,(j%8)*154+10
            sheet[y:y+256,x:x+144]=im
        name=f'contact-{start//per_page+1:03d}.jpg'
        cv2.imwrite(str(out/name),sheet,[cv2.IMWRITE_JPEG_QUALITY,94]);names.append(name)
    return names


def analyze(source: Path, out: Path, contact_step:float=.5, save_frames:bool=True) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    frame_dir = out / "frames"
    frame_dir.mkdir(exist_ok=True)
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(source)]))
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    num, den = map(int, video["avg_frame_rate"].split("/"))
    fps = num / den
    timestamps=frame_timestamps(source)
    origin=timestamps[0] if timestamps else float(video.get('start_time',0))
    cap = cv2.VideoCapture(str(source))
    rows, thumbs = [], []
    previous = None
    index = 0
    next_thumb=0.
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(cv2.resize(frame, (180, 320)), cv2.COLOR_BGR2GRAY)
        pts=timestamps[index] if index<len(timestamps) else origin+index/fps
        seconds=pts-origin
        row = {"frame": index, "seconds": round(seconds, 6), "media_seconds":pts,"luma_mean": float(gray.mean()), "edge_fraction": float((cv2.Canny(gray, 65, 160)>0).mean())}
        if previous is not None:
            delta = np.abs(gray.astype(float)-previous.astype(float))
            flow = cv2.calcOpticalFlowFarneback(previous, gray, None, .5, 3, 15, 3, 5, 1.2, 0)
            magnitude = np.linalg.norm(flow, axis=2)
            row.update(delta_mean=float(delta.mean()), flow_median_px=float(np.median(magnitude)), flow_p90_px=float(np.percentile(magnitude,90)))
            dt=pts-(timestamps[index-1] if index-1<len(timestamps) else origin+(index-1)/fps)
            row['flow_p90_px_per_second']=row['flow_p90_px']/dt if dt>0 else None
            row['near_duplicate_previous']=row['delta_mean']<.05
            points = cv2.goodFeaturesToTrack(previous, maxCorners=180, qualityLevel=.02, minDistance=7)
            if points is not None and len(points)>5:
                nxt, status, _ = cv2.calcOpticalFlowPyrLK(previous, gray, points, None)
                valid = status[:,0] == 1
                if valid.sum() >= 6:
                    matrix, inliers = cv2.estimateAffinePartial2D(points[valid], nxt[valid], method=cv2.RANSAC, ransacReprojThreshold=2.)
                    if matrix is not None:
                        a,b = matrix[0,:2]
                        row.update(affine_scale=float(np.hypot(a,b)), affine_angle_deg=float(np.degrees(np.arctan2(-b,a))), affine_tx=float(matrix[0,2]), affine_ty=float(matrix[1,2]), affine_inlier_fraction=float(inliers.mean()))
        else:
            row.update(delta_mean=0., flow_median_px=0., flow_p90_px=0.)
        rows.append(row)
        if save_frames:cv2.imwrite(str(frame_dir/f"{index:04d}.jpg"), frame, [cv2.IMWRITE_JPEG_QUALITY,92])
        if seconds+1e-5 >= next_thumb:
            thumb=cv2.resize(frame,(144,256))
            cv2.putText(thumb,f"f{index:04d} {seconds:05.2f}s",(3,17),cv2.FONT_HERSHEY_SIMPLEX,.34,(50,255,255),1,cv2.LINE_AA)
            thumbs.append(thumb)
            next_thumb+=contact_step
        previous = gray
        index += 1
    cap.release()
    pages=contact_pages(thumbs,out)
    # These are visual discontinuity candidates, not a semantic edit decision list.
    candidates=[]
    differences=np.array([r['delta_mean'] for r in rows[1:]])
    median=float(np.median(differences));mad=float(np.median(np.abs(differences-median)))
    threshold=max(3.,median+7*mad)
    for j in range(1,len(rows)-1):
        r=rows[j]
        if r['delta_mean']>threshold and r['delta_mean']>=rows[j-1]['delta_mean'] and r['delta_mean']>rows[j+1]['delta_mean']:
            candidate={"frame":j,"seconds":r['seconds'],"media_seconds":r['media_seconds'],"delta_mean":round(r['delta_mean'],3)}
            if candidates and r['seconds']-candidates[-1]['seconds']<.12:
                if r['delta_mean']>candidates[-1]['delta_mean']:candidates[-1]=candidate
            else:candidates.append(candidate)
    intervals=np.diff(timestamps[:index]) if timestamps else np.array([])
    inferred_duration=(timestamps[index-1]-origin+float(np.median(intervals))) if len(timestamps)>=index and len(intervals) else index/fps
    result={"schema_version":2,"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"source_name":source.name,"probe":probe,"decoded_frames":index,"fps":fps,"visual_duration_seconds":inferred_duration,"video_pts_origin_seconds":origin,"timestamp_count_matches_decode":len(timestamps)==index,"median_frame_interval_seconds":float(np.median(intervals)) if len(intervals) else None,"frame_interval_max_deviation_seconds":float(np.max(np.abs(intervals-np.median(intervals)))) if len(intervals) else None,"near_duplicate_fraction":sum(r.get('near_duplicate_previous',False) for r in rows)/max(1,index-1),"contact_pages":pages,"contact_step_seconds":contact_step,"analysis_resolution":[180,320],"discontinuity_threshold":threshold,"measurement_notes":["seconds is relative to the first decoded video PTS; media_seconds preserves the source presentation time for audio alignment.","Flow is pixels per source-frame at analysis resolution; per-second flow is also supplied for frame-rate-aware comparisons.","Near-duplicate threshold is mean luma difference below 0.05 at analysis resolution. It does not measure the author's original animation frame rate.","Affine estimates describe dominant image motion, not recovered 3D camera transforms.","Discontinuity candidates require manual semantic review; continuous motion can also produce peaks.","No original alpha, hidden pixels, authoring keyframes or project layers are recovered."],"visual_discontinuity_candidates":candidates,"frames":rows}
    if any(s["codec_type"]=="audio" for s in probe["streams"]):
        wav=out/"reference.wav"
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(source),"-vn","-ac","1","-ar","24000",str(wav)],check=True)
        with wave.open(str(wav),"rb") as reader:
            rate=reader.getframerate()
            samples=np.frombuffer(reader.readframes(reader.getnframes()),np.int16).astype(float)/32768
        envelope=[]
        for j in range(0,len(samples)-1024,256):
            chunk=samples[j:j+1024]
            envelope.append({"seconds":j/rate,"rms_dbfs":float(20*np.log10(max(1e-8,np.sqrt(np.mean(chunk**2))))),"peak_dbfs":float(20*np.log10(max(1e-8,np.max(np.abs(chunk)))))})
        result["audio"]={"sample_rate":rate,"envelope":envelope,"notes":"Mixed reference track only. This analysis does not separate voice/music/effects or judge intelligibility."}
    (out/"measurements.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument('--contact-step',type=float,default=.5,help='Seconds between contact-sheet samples')
    parser.add_argument('--no-frame-files',action='store_true',help='Keep measurements and contact sheets without individual JPGs')
    args=parser.parse_args()
    if args.contact_step<=0:parser.error('--contact-step must be positive')
    data=analyze(args.source,args.out,args.contact_step,not args.no_frame_files)
    print(json.dumps({k:data[k] for k in ["decoded_frames","fps","visual_duration_seconds","visual_discontinuity_candidates"]},ensure_ascii=False))
