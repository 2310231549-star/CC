"""
Reusable OCR script — extract Chinese/English text from images.
Usage: python ocr_image.py <image_path>
Output: prints text to stdout and saves to <image_path>_text.txt
"""
import sys
import os
import shutil

def ocr_image(image_path):
    # Step 1: if path has non-ASCII chars, copy to temp ASCII path
    img_dir = os.path.dirname(image_path) or '.'
    img_name = os.path.basename(image_path)
    temp_path = os.path.join(img_dir, '_ocr_temp' + os.path.splitext(image_path)[1])

    need_cleanup = False
    try:
        img_name.encode('ascii')
    except UnicodeEncodeError:
        shutil.copy2(image_path, temp_path)
        work_path = temp_path
        need_cleanup = True
    else:
        work_path = image_path

    # Step 2: OCR
    import easyocr
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    result = reader.readtext(work_path, detail=0)

    # Step 3: Output
    text = '\n'.join(result)
    print(text)

    # Save alongside original
    out_path = os.path.splitext(image_path)[0] + '_text.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"\n[Saved to: {out_path}]")

    # Cleanup
    if need_cleanup and os.path.exists(temp_path):
        os.remove(temp_path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python ocr_image.py <image_path>")
        sys.exit(1)
    ocr_image(sys.argv[1])
