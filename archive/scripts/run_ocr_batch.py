import os
import json
import glob
import easyocr

def ocr_all():
    out_dir = "0729/analysis_output"
    kf_dir = os.path.join(out_dir, "keyframes")
    ocr_file = os.path.join(out_dir, "ocr_text.json")
    
    images = sorted(glob.glob(os.path.join(kf_dir, "*.jpg")))
    if not images:
        print("No images found yet.")
        return

    print(f"Initializing EasyOCR for {len(images)} images...")
    reader = easyocr.Reader(['en', 'fr'], gpu=False)
    
    ocr_data = {}
    if os.path.exists(ocr_file):
        try:
            with open(ocr_file, "r", encoding="utf-8") as f:
                ocr_data = json.load(f)
        except:
            pass

    for img_path in images:
        fname = os.path.basename(img_path)
        if fname not in ocr_data:
            print(f"OCR processing {fname}...")
            text_lines = reader.readtext(img_path, detail=0)
            ocr_data[fname] = text_lines

    with open(ocr_file, "w", encoding="utf-8") as f:
        json.dump(ocr_data, f, ensure_ascii=False, indent=2)

    print(f"OCR batch finished. Total processed keyframes: {len(ocr_data)}")

if __name__ == "__main__":
    ocr_all()
