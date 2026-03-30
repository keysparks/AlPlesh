import os
import cv2
import math
import pytesseract
from pytesseract import Output
import re
import shutil
import pandas as pd
from PIL import Image
import config

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

def is_underlined(image_path, keyword):
    image = cv2.imread(image_path)
    if image is None: return False
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(gray, output_type=Output.DICT)

    for i, word in enumerate(data["text"]):
        if word.strip().upper() == keyword.upper():
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            roi_y1 = y + h
            roi_y2 = roi_y1 + 10
            roi = gray[roi_y1:roi_y2, x:x+w]
            edges = cv2.Canny(roi, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, math.pi/180, threshold=10, minLineLength=w//2, maxLineGap=5)
            if lines is not None:
                return True
    return False

def process_sub_images(input_folder, output_folder, keyword):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            file_path = os.path.join(input_folder, filename)
            if is_underlined(file_path, keyword):
                shutil.move(file_path, os.path.join(output_folder, filename))

def normalize_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip().upper()

def contains_keyword(image_path, keyword):
    text = pytesseract.image_to_string(Image.open(image_path))
    text_clean = normalize_text(text)
    return keyword.upper() in text_clean.upper()

def move_if_keyword_present(input_folder, output_folder, keyword):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            full_path = os.path.join(input_folder, filename)
            if contains_keyword(full_path, keyword):
                shutil.move(full_path, os.path.join(output_folder, filename))

def extract_abbreviations_to_csv(input_folder, output_csv_path):
    file_name = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    if not file_name: return
    
    image_path = os.path.join(input_folder, file_name[0])
    try:
        img = Image.open(image_path)
        custom_config = r'--psm 6'
        extracted_text = pytesseract.image_to_string(img, config=custom_config)
        data = []
        for line in extracted_text.splitlines():
            line = line.strip()
            if not line: continue
            parts = re.split(r'\s{2,}', line, maxsplit=1)
            abbrev = None
            full_form = None

            if len(parts) == 2:
                abbrev = parts[0].strip()
                full_form = parts[1].strip()
                if abbrev == '@' and not full_form and len(parts[0]) == 1:
                     full_form = ""
            else:
                found_split = -1
                for i in range(len(line) - 2, 0, -1):
                    if line[i] == ' ':
                        if line[i+1].isupper():
                            found_split = i
                            break 
                if found_split != -1:
                    abbrev = line[:found_split].strip()
                    full_form = line[found_split+1:].strip()
                elif line.startswith('@'):
                    potential_split = re.split(r'(@)', line, maxsplit=1)
                    if len(potential_split) == 3 and potential_split[1] == '@':
                        abbrev = '@'
                        full_form = potential_split[2].strip()
                        if not full_form: full_form = "" 
                    elif line == '@': 
                         abbrev = '@'
                         full_form = ''
                    else: continue
                elif line.strip() and ' ' not in line.strip():
                    abbrev = line.strip()
                    full_form = "" 
                else: continue

            if abbrev is not None and full_form is not None:
                 data.append({'Abbreviation': abbrev, 'Full Form': full_form})
        
        if data:
            df = pd.DataFrame(data)
            df.to_csv(output_csv_path, index=False, encoding='utf-8')
    except Exception as e:
        print(f"Error extracting abbreviations: {e}")
