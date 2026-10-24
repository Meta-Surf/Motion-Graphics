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


def analyze(source: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    frame_dir = out / "frames"
    frame_dir.mkdir(exist_ok=True)
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(source)]))
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    num, den = map(int, video["avg_frame_rate"].split("/"))
    fps = num / den
    cap = cv2.VideoCapture(str(source))
    rows, thumbs = [], []
    previous = None
    index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(cv2.resize(frame, (180, 320)), cv2.COLOR_BGR2GRAY)
        row = {"frame": index, "seconds": round(index/fps, 6), "luma_mean": float(gray.mean()), "edge_fraction": float((cv2.Canny(gray, 65, 160)>0).mean())}
        if previous is not None:
            delta = np.abs(gray.astype(float)-previous.astype(float))
            flow = cv2.calcOpticalFlowFarneback(previous, gray, None, .5, 3, 15, 3, 5, 1.2, 0)
            magnitude = np.linalg.norm(flow, axis=2)
            row.update(delta_mean=float(delta.mean()), flow_median_px=float(np.median(magnitude)), flow_p90_px=float(np.percentile(magnitude,90)))
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
        cv2.imwrite(str(frame_dir/f"{index:04d}.jpg"), frame, [cv2.IMWRITE_JPEG_QUALITY,92])
        if index % 6 == 0:
            thumb=cv2.resize(frame,(144,256))
            cv2.putText(thumb,f"f{index:03d}  {index/fps:05.2f}s",(3,17),cv2.FONT_HERSHEY_SIMPLEX,.36,(50,255,255),1,cv2.LINE_AA)
            thumbs.append(thumb)
        previous = gray
        index += 1
    cap.release()
    sheet=np.full((((len(thumbs)+9)//10)*276,10*154,3),22,np.uint8)
    for j,im in enumerate(thumbs):
        y,x=(j//10)*276+10,(j%10)*154+5
        sheet[y:y+256,x:x+144]=im
    cv2.imwrite(str(out/"contact-frames.jpg"),sheet,[cv2.IMWRITE_JPEG_QUALITY,94])
    # These are visual discontinuity candidates, not a semantic edit decision list.
    candidates=[]
    for j in range(1,len(rows)-1):
        r=rows[j]
        if r["delta_mean"]>16 and r["delta_mean"]>=rows[j-1]["delta_mean"] and r["delta_mean"]>rows[j+1]["delta_mean"]:
            candidates.append({"frame":j,"seconds":round(j/fps,4),"delta_mean":round(r["delta_mean"],3)})
    result={"schema_version":1,"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"source_name":source.name,"probe":probe,"decoded_frames":index,"fps":fps,"visual_duration_seconds":index/fps,"analysis_resolution":[180,320],"measurement_notes":["Flow is pixels per source-frame at analysis resolution; it mixes object, camera, blur and text motion.","Affine estimates describe dominant image motion, not recovered 3D camera transforms.","Discontinuity candidates require manual semantic review; continuous motion can also produce peaks.","No original alpha, hidden pixels, authoring keyframes or project layers are recovered."],"visual_discontinuity_candidates":candidates,"frames":rows}
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
    args=parser.parse_args()
    data=analyze(args.source,args.out)
    print(json.dumps({k:data[k] for k in ["decoded_frames","fps","visual_duration_seconds","visual_discontinuity_candidates"]},ensure_ascii=False))
