import cv2
import numpy as np
import os

def test_roi():
    video_path = "0729/0729.mp4"
    out_dir = "0729/test_zooms"
    os.makedirs(out_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) # 50.0

    # Define test zoom points: (timestamp, zoom_level, center_x_norm, center_y_norm, name)
    test_points = [
        (5.0,  1.00, 0.50, 0.50, "01_full_dashboard"),
        (20.0, 1.45, 0.70, 0.35, "02_cv_preview"),
        (45.0, 1.40, 0.70, 0.60, "03_question_input"),
        (65.0, 1.50, 0.50, 0.65, "04_hitl_editor"),
        (90.0, 1.35, 0.50, 0.40, "05_pipeline_progress"),
        (115.0, 1.55, 0.50, 0.35, "06_ast_result_badge"),
        (140.0, 1.40, 0.50, 0.60, "07_graph_interpreter_xai"),
        (165.0, 1.45, 0.50, 0.50, "08_pdf_export_button"),
    ]

    for ts, zoom, cx_n, cy_n, name in test_points:
        f_idx = int(ts * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if not ret:
            continue
            
        H, W, _ = frame.shape
        crop_w = int(W / zoom)
        crop_h = int(H / zoom)
        
        center_x = int(cx_n * W)
        center_y = int(cy_n * H)
        
        x0 = max(0, min(W - crop_w, center_x - crop_w // 2))
        y0 = max(0, min(H - crop_h, center_y - crop_h // 2))
        
        cropped = frame[y0:y0+crop_h, x0:x0+crop_w]
        resized = cv2.resize(cropped, (1920, 1080), interpolation=cv2.INTER_CUBIC)
        
        # Add a subtle callout badge on top
        overlay = resized.copy()
        cv2.rectangle(overlay, (40, 40), (600, 100), (20, 20, 30), -1)
        cv2.addWeighted(overlay, 0.85, resized, 0.15, 0, resized)
        cv2.rectangle(resized, (40, 40), (600, 100), (30, 144, 255), 2)
        cv2.putText(resized, f"GrapheinAI: {name.upper()}", (60, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        
        cv2.imwrite(os.path.join(out_dir, f"{name}.jpg"), resized)

    cap.release()
    print("ROI Test Images Generated in 0729/test_zooms!")

if __name__ == "__main__":
    test_roi()
