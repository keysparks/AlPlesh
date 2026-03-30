import fitz
import pytesseract
from PIL import Image
import os
import re

pdf_path = "inputs/floor_plan.pdf"
doc = fitz.open(pdf_path)

target_page_num = -1
for i in range(len(doc)):
    page = doc.load_page(i)
    text = page.get_text("text").upper()
    if "E1-1" in text or "E-CS" in text: # fallback to 0 if only 1 page
        target_page_num = i
        break

if target_page_num == -1:
    target_page_num = 0

print(f"Scanning Page {target_page_num+1} for Models...")
page = doc.load_page(target_page_num)
mat = fitz.Matrix(3.0, 3.0) # High res for accurate OCR
pix = page.get_pixmap(matrix=mat)
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(img, config=custom_config)

models = set()
for line in text.split('\n'):
    line = line.strip().upper()
    if "MODEL" in line and len(line) < 30: # Filter out garbage
        match = re.search(r'MODEL\s*([A-Z0-9]+)', line)
        if match:
            models.add(match.group(0))

print("\n--- RESULTS ---")
if models:
    for m in models:
        print(f"Found: {m}")
else:
    print("No valid 'MODEL' strings found by OCR on this page.")
