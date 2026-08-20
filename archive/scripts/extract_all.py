import cv2
import numpy as np
import os
import json
import time

def run():
    video_path = "0729/0729.mp4"
    out_dir = "0729/analysis_output"
    kf_dir = os.path.join(out_dir, "keyframes")
    os.makedirs(kf_dir, exist_ok=True)

    # Clean existing
    for f in os.listdir(kf_dir):
        if f.endswith(".jpg"):
            try: os.remove(os.path.join(kf_dir, f))
            except: pass

    t0 = time.time()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) # 50.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    print(f"High-Speed Sampling: {duration:.2f}s video ({total_frames} frames @ {fps} fps)")

    # Sample every 5.0 seconds (250 frames)
    step = 250
    scenes = []
    
    frame_idx = 0
    while frame_idx < total_frames:
        if frame_idx % step == 0:
            ret, frame = cap.read()
            if not ret:
                break
            ts = frame_idx / fps
            hd = cv2.resize(frame, (1280, 720))
            img_name = f"kf_{int(ts):03d}s.jpg"
            cv2.imwrite(os.path.join(kf_dir, img_name), hd, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            scenes.append({"ts": round(ts, 2), "file": img_name})
            print(f"Saved keyframe at {ts:.1f}s")
            frame_idx += 1
        else:
            # Fast grab to skip decoding
            ret = cap.grab()
            if not ret:
                break
            frame_idx += 1

    cap.release()
    t1 = time.time()
    print(f"High-Speed Extraction Complete in {t1-t0:.2f}s! Keyframes: {len(scenes)}")

    report_data = {"duration": round(duration, 2), "total_keyframes": len(scenes), "scenes": scenes}
    with open(os.path.join(out_dir, "timeline.json"), "w") as f:
        json.dump(report_data, f, indent=2)

if __name__ == "__main__":
    run()
