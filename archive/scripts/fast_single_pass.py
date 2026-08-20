import cv2
import os
import json
import time

def run():
    video_path = "0729/0729.mp4"
    out_dir = "0729/analysis_output"
    kf_dir = os.path.join(out_dir, "keyframes")
    os.makedirs(kf_dir, exist_ok=True)

    t0 = time.time()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) # 50.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    # Timestamps to extract (every ~5-6s across the whole video)
    timestamps = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 174]

    scenes = []
    for ts in timestamps:
        f_idx = int(ts * fps)
        if f_idx >= total_frames:
            f_idx = total_frames - 1
            
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if ret:
            hd = cv2.resize(frame, (1280, 720))
            img_name = f"kf_{int(ts):03d}s.jpg"
            cv2.imwrite(os.path.join(kf_dir, img_name), hd, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            scenes.append({"ts": ts, "file": img_name})

    cap.release()
    t1 = time.time()
    print(f"Extracted {len(scenes)} keyframes in {t1-t0:.2f}s!")

    with open(os.path.join(out_dir, "timeline.json"), "w") as f:
        json.dump({"duration": duration, "keyframes": len(scenes), "scenes": scenes}, f, indent=2)

if __name__ == "__main__":
    run()
