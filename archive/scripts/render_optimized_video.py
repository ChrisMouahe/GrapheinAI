import cv2
import numpy as np
import os
import math
import time

def smoothstep(x):
    """Cubic smoothstep ease-in-ease-out interpolation function."""
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

def render_video():
    src_video = "0729/0729.mp4"
    out_video = "0729/GrapheinAI_Demo_Optimized.mp4"

    cap = cv2.VideoCapture(src_video)
    if not cap.isOpened():
        print(f"Error opening {src_video}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) # 50.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w_orig = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # 3840
    h_orig = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # 2160
    duration = total_frames / fps

    out_fps = 25.0
    out_w, out_h = 1920, 1080
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(out_video, fourcc, out_fps, (out_w, out_h))

    print(f"Ultra-Fast Video Renderer (25 FPS HD): {src_video} -> {out_video}", flush=True)

    timeline_waypoints = [
        (0.0,   1.00, 0.50, 0.50, "1. MULTIMODAL RESEARCH DASHBOARD"),
        (12.0,  1.00, 0.50, 0.50, "1. MULTIMODAL RESEARCH DASHBOARD"),
        (15.0,  1.45, 0.70, 0.35, "2. OPENCV GEOMETRY & VISION PREVIEW"),
        (32.0,  1.45, 0.70, 0.35, "2. OPENCV GEOMETRY & VISION PREVIEW"),
        (35.0,  1.40, 0.70, 0.60, "3. NATURAL LANGUAGE QUERY & PRESETS"),
        (52.0,  1.40, 0.70, 0.60, "3. NATURAL LANGUAGE QUERY & PRESETS"),
        (55.0,  1.50, 0.50, 0.65, "4. HUMAN-IN-THE-LOOP (HITL) DATA GRID"),
        (78.0,  1.50, 0.50, 0.65, "4. HUMAN-IN-THE-LOOP (HITL) DATA GRID"),
        (81.0,  1.30, 0.50, 0.40, "5. MULTIMODAL PIPELINE EXECUTION"),
        (102.0, 1.30, 0.50, 0.40, "5. MULTIMODAL PIPELINE EXECUTION"),
        (105.0, 1.55, 0.50, 0.35, "6. SAFECALCULATOR AST (ZERO HALLUCINATION)"),
        (130.0, 1.55, 0.50, 0.35, "6. SAFECALCULATOR AST (ZERO HALLUCINATION)"),
        (133.0, 1.40, 0.50, 0.60, "7. EXPLAINABILITY ENGINE (XAI TRACEABILITY)"),
        (155.0, 1.40, 0.50, 0.60, "7. EXPLAINABILITY ENGINE (XAI TRACEABILITY)"),
        (158.0, 1.45, 0.50, 0.50, "8. REPORTLAB OFFICIAL PDF REPORT EXPORT"),
        (174.4, 1.00, 0.50, 0.50, "8. REPORTLAB OFFICIAL PDF REPORT EXPORT")
    ]

    t0 = time.time()
    frame_idx = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process every 2nd frame for 25 FPS output
        if frame_idx % 2 == 0:
            current_ts = frame_idx / fps

            wp_start = timeline_waypoints[0]
            wp_end = timeline_waypoints[-1]

            for i in range(len(timeline_waypoints) - 1):
                if timeline_waypoints[i][0] <= current_ts <= timeline_waypoints[i+1][0]:
                    wp_start = timeline_waypoints[i]
                    wp_end = timeline_waypoints[i+1]
                    break

            t_s, z_s, cx_s, cy_s, badge_s = wp_start
            t_e, z_e, cx_e, cy_e, badge_e = wp_end

            if t_e > t_s:
                alpha = (current_ts - t_s) / (t_e - t_s)
            else:
                alpha = 1.0

            alpha_smooth = smoothstep(alpha)

            cur_zoom = z_s + (z_e - z_s) * alpha_smooth
            cur_cx   = cx_s + (cx_e - cx_s) * alpha_smooth
            cur_cy   = cy_s + (cy_e - cy_s) * alpha_smooth
            cur_badge = badge_e if alpha_smooth > 0.5 else badge_s

            crop_w = int(w_orig / cur_zoom)
            crop_h = int(h_orig / cur_zoom)

            center_x_px = int(cur_cx * w_orig)
            center_y_px = int(cur_cy * h_orig)

            x0 = max(0, min(w_orig - crop_w, center_x_px - crop_w // 2))
            y0 = max(0, min(h_orig - crop_h, center_y_px - crop_h // 2))

            cropped = frame[y0:y0+crop_h, x0:x0+crop_w]
            resized = cv2.resize(cropped, (out_w, out_h), interpolation=cv2.INTER_LINEAR)

            # Draw Premium SaaS Lower-Third Badge
            badge_box_w = 680
            badge_box_h = 56
            bx0, by0 = 40, 40

            overlay = resized.copy()
            cv2.rectangle(overlay, (bx0, by0), (bx0 + badge_box_w, by0 + badge_box_h), (15, 23, 42), -1)
            cv2.addWeighted(overlay, 0.88, resized, 0.12, 0, resized)

            cv2.rectangle(resized, (bx0, by0), (bx0 + 6, by0 + badge_box_h), (255, 144, 30), -1)
            cv2.rectangle(resized, (bx0, by0), (bx0 + badge_box_w, by0 + badge_box_h), (50, 60, 80), 1)

            cv2.putText(resized, f"GrapheinAI | {cur_badge}", (bx0 + 20, by0 + 36), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

            writer.write(resized)
            saved_count += 1

            if saved_count % 500 == 0:
                pct = (frame_idx / total_frames) * 100
                print(f"Rendered {saved_count} frames ({pct:.1f}%)", flush=True)

        frame_idx += 1

    cap.release()
    writer.release()
    t1 = time.time()
    print(f"RENDER COMPLETE in {t1 - t0:.2f}s! Output saved to {out_video}", flush=True)

if __name__ == "__main__":
    render_video()
