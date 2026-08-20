import cv2
import numpy as np
import os
import json
import time

def analyze_video(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    frames_dir = os.path.join(output_dir, "keyframes")
    os.makedirs(frames_dir, exist_ok=True)

    t0 = time.time()
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps

    print(f"Lightning Fast Video Processing: {width}x{height} @ {fps:.2f} fps | {total_frames} frames | {duration:.2f}s")

    sample_step = int(fps) # 1 frame per second (50 frames)
    
    prev_gray = None
    sampled_frames = []
    saved_scenes = []
    last_saved_ts = -10.0
    scene_idx = 1
    
    frame_count = 0
    while frame_count < total_frames:
        ret, frame = cap.read()
        if not ret:
            break
            
        timestamp = frame_count / fps
        small = cv2.resize(frame, (640, 360))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        
        diff_score = 0.0
        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            diff_score = float(np.mean(diff))
            
        sampled_frames.append({
            "timestamp": round(timestamp, 2),
            "diff_score": round(diff_score, 4)
        })
        
        # Save keyframe if significant change or every 5s
        if diff_score > 3.0 or (timestamp - last_saved_ts >= 5.0) or frame_count == 0:
            hd_frame = cv2.resize(frame, (1920, 1080))
            img_name = f"sec_{int(timestamp):03d}.jpg"
            img_path = os.path.join(frames_dir, img_name)
            cv2.imwrite(img_path, hd_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            
            saved_scenes.append({
                "scene_idx": scene_idx,
                "timestamp": round(timestamp, 2),
                "diff_score": round(diff_score, 2),
                "image_file": img_name
            })
            scene_idx += 1
            last_saved_ts = timestamp
            
        prev_gray = gray
        frame_count += 1
        
        # Fast skip 49 frames with grab()
        for _ in range(sample_step - 1):
            if frame_count < total_frames:
                grabbed = cap.grab()
                if not grabbed:
                    break
                frame_count += 1
        
    cap.release()
    t1 = time.time()
    print(f"Processed video in {t1 - t0:.2f}s! Sampled {len(sampled_frames)} frames. Saved {len(saved_scenes)} keyframes.")

    report = {
        "video_path": video_path,
        "width": width,
        "height": height,
        "fps": fps,
        "total_frames": total_frames,
        "duration": round(duration, 2),
        "sampled_count": len(sampled_frames),
        "keyframes_saved": len(saved_scenes),
        "scenes": saved_scenes,
        "timeline": sampled_frames
    }
    
    report_path = os.path.join(output_dir, "fast_analysis.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    analyze_video("0729/0729.mp4", "0729/analysis_output")
