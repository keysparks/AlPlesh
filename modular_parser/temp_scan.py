import fitz
import os
import glob

pdf_files = glob.glob("inputs/*.pdf")
for pdf_path in pdf_files:
    print(f"=== Scanning {pdf_path} ===")
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        page = doc.load_page(i)
        text = page.get_text("text")
        print(f"--- PAGE {i+1} ---")
        print(text)
