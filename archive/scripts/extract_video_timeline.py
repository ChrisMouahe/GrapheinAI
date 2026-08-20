import cv2
import numpy as np
import os
import json
import time

def process_video():
    video_path = "0729/0729.mp4"
    out_dir = "0729/analysis_output"
    kf_dir = os.path.join(out_dir, "keyframes")
    os.makedirs(kf_dir, exist_ok=True)

    # Clean existing keyframes
    for f in os.listdir(kf_dir):
        if f.endswith(".jpg"):
            os.remove(os.path.join(kf_dir, f))

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) # 50.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    print(f"Starting extraction: {duration:.2f}s video ({total_frames} frames @ {fps} fps)")

    # Sample every 1 second (50 frames)
    step = int(fps)
    
    timeline = []
    scenes = []
    
    prev_gray = None
    last_saved_ts = -10.0
    
    for f_idx in range(0, total_frames, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if not ret:
            break
            
        ts = f_idx / fps
        small = cv2.resize(frame, (480, 270))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        
        diff = 0.0
        if prev_gray is not None:
            diff = float(np.mean(cv2.absdiff(gray, prev_gray)))
            
        timeline.append({"ts": round(ts, 2), "diff": round(diff, 2)})
        
        # Save keyframe if diff > 3.0 or 4 seconds passed
        if diff > 3.0 or (ts - last_saved_ts >= 4.0) or f_idx == 0:
            hd = cv2.resize(frame, (1280, 720)) # 720p is fast to write and crystal clear
            img_name = f"kf_{int(ts):03d}s.jpg"
            img_path = os.path.join(kf_dir, img_name)
            cv2.imwrite(img_path, hd, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            
            scenes.append({
                "ts": round(ts, 2),
                "diff": round(diff, 2),
                "file": img_name
            })
            last_saved_ts = ts
            
        prev_gray = gray
        if int(ts) % 30 == 0:
            print(f"Processed up to {int(ts)}s / {int(duration)}s...")

    cap.release()
    
    report = {
        "duration": round(duration, 2),
        "total_keyframes": len(scenes),
        "scenes": scenes,
        "timeline": timeline
    }
    
    with open(os.path.join(out_dir, "timeline.json"), "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"Extraction Complete! Generated {len(scenes)} keyframes and saved timeline.json.")

if __name__ == "__main__":
    process_video()
