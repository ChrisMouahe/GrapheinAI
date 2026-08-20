import os
import json
import glob
import easyocr

def ocr_keyframes(keyframes_dir, output_json):
    reader = easyocr.Reader(['en', 'fr'], gpu=False)
    image_files = sorted(glob.glob(os.path.join(keyframes_dir, "*.jpg")))
    
    ocr_results = {}
    
    for img_path in image_files:
        basename = os.path.basename(img_path)
        print(f"Running OCR on {basename}...")
        results = reader.readtext(img_path, detail=0)
        ocr_results[basename] = results
        
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(ocr_results, f, ensure_ascii=False, indent=2)
        
    print(f"OCR completed for {len(image_files)} keyframes. Output saved to {output_json}")

if __name__ == "__main__":
    ocr_keyframes("0729/analysis_output/keyframes", "0729/analysis_output/ocr_results.json")
