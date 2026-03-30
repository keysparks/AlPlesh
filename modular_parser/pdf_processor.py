import os
import shutil
import glob
from PyPDF2 import PdfReader, PdfWriter
import fitz
from PIL import Image
import cv2
import numpy as np
import pytesseract
import config

def split_pdf_to_pages(input_path, output_folder):
    """Splits a multipage PDF into single page PDF files."""
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    for i in range(total_pages):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        output_filename = os.path.join(output_folder, f"page_{i + 1}.pdf")
        with open(output_filename, 'wb') as output_file:
            writer.write(output_file)

def pdf_to_zoomed_image(pdf_path, page_num, zoom_x, zoom_y):
    """Converts a single PDF page into a high-res Zoomed image."""
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_num)
    mat = fitz.Matrix(zoom_x, zoom_y)
    pix = page.get_pixmap(matrix=mat)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return image

def find_legend_page(pdf_path):
    """Scans PDF pages for legend keywords using fast vector text extraction or fallback OCR."""
    pdf_document = fitz.open(pdf_path)
    keywords = ["ABBREVIATIONS", "PLAN SYMBOLS", "LEGEND", "SYMBOLS"]
    
    print(f"Scanning {len(pdf_document)} pages for legend matching...")
    
    # Pass 1: Fast PyMuPDF Vector Text Extraction
    for i in range(len(pdf_document)):
        page = pdf_document.load_page(i)
        text = page.get_text("text").upper()
        if any(kw in text for kw in keywords):
            print(f"-> Found legend on page {i + 1} using fast vector scanning!")
            return i
            
    # Pass 2: Fallback to OCR if the PDF is a flattened scan
    print("-> Vector scan failed. PDF might be a flattened image. Running OCR fallback (this may take a while)...")
    for i in range(len(pdf_document)):
        print(f"OCR scanning page {i + 1}...")
        page = pdf_document.load_page(i)
        
        # Render low res for fast OCR
        mat = fitz.Matrix(1.5, 1.5)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        text = pytesseract.image_to_string(gray).upper()
        if any(kw in text for kw in keywords):
            print(f"-> Found legend on page {i + 1} using OCR!")
            return i
            
    print("-> Warning: Could not automatically detect legend on any page. Defaulting to page 1.")
    return 0

def find_floorplan_page(pdf_path, target_drawing):
    """Scans PDF text vectors for a specific large-font drawing number (e.g. E1-1)."""
    pdf_document = fitz.open(pdf_path)
    print(f"Scanning {len(pdf_document)} pages for explicit drawing '{target_drawing}'...")
    
    for i in range(len(pdf_document)):
        page = pdf_document.load_page(i)
        blocks = page.get_text("dict").get("blocks", [])
        for b in blocks:
            for l in b.get("lines", []):
                for s in l.get("spans", []):
                    if target_drawing.upper() in s["text"].upper():
                        if s["size"] > 16:
                            print(f"-> Verified drawing '{target_drawing}' on page {i + 1} (Font Size: {s['size']:.1f})!")
                            return i
                            
    print(f"-> Warning: Could not explicitly locate large drawing number '{target_drawing}'. Defaulting to page 1.")
    return 0

def process_input_file(prefix, target_img_name, auto_detect=False, auto_detect_floorplan=False):
    """Dynamically finds a file by prefix and processes it into the pipeline as an image."""
    search_pattern = os.path.join(config.INPUT_DIR, f"{prefix}.*")
    matches = glob.glob(search_pattern)
    
    if not matches:
        print(f"Warning: No input file found for '{prefix}' at {config.INPUT_DIR}")
        return False
        
    input_file = matches[0]
    ext = input_file.lower().split('.')[-1]
    target_path = os.path.join(config.PAGES_IMAGES_DIR, target_img_name)
    
    if os.path.exists(target_path):
        os.remove(target_path)
    
    if ext == 'pdf':
        page_num = 0
        if auto_detect:
            page_num = find_legend_page(input_file)
        elif auto_detect_floorplan:
            page_num = find_floorplan_page(input_file, config.TARGET_FLOOR_PLAN_DRAWING)
            
        print(f"Converting PDF '{os.path.basename(input_file)}' (Page {page_num + 1}) to zoomed image...")
        img = pdf_to_zoomed_image(input_file, page_num, 2.0, 2.0)
        img.save(target_path)
    elif ext in ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif']:
        print(f"Copying native image '{os.path.basename(input_file)}' directly to pipeline...")
        shutil.copy(input_file, target_path)
    else:
        print(f"Warning: Unsupported file type '{ext}' for file {input_file}")
        return False
    return True
