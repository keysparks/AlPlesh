# -*- coding: utf-8 -*-
"""
Created on Sun May 11 13:10:59 2025

@author: gov97
"""

import os
from PyPDF2 import PdfReader, PdfWriter
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import re
import numpy as np
import fitz
import pandas as pd
from datetime import datetime
import shutil
from pytesseract import Output
import math
from PIL import Image
start_time = datetime.now()
def split_pdf_to_pages(input_path):
    # Create output folder named 'pages' if it doesn't exist
    output_folder = "pages"
    os.makedirs(output_folder, exist_ok=True)
    
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    for i in range(total_pages):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        
        output_filename = os.path.join(output_folder, f"page_{i + 1}.pdf")
        with open(output_filename, 'wb') as output_file:
            writer.write(output_file)
        #print(f"Saved: {output_filename}")
local_machine="C:/KeySparks/Clients/Plesh/"
dir="final_demo_code"
input_pdf_path = local_machine+dir+"/input_pdf/input.pdf"
split_pdf_to_pages(input_pdf_path)
def pdf_to_zoomed_image(pdf_path, page_num, zoom_x, zoom_y):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_num)
    mat = fitz.Matrix(zoom_x, zoom_y)
    pix = page.get_pixmap(matrix=mat)
    
    # Convert to PIL Image
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return image
folder="pages_images"
os.makedirs(folder, exist_ok=True)

pdf_pages_path = local_machine+dir+"/pages/page_4.pdf"
page_number = 0  # Select the page number
zoom_x = 2.0  # Zoom factor along x-axis
zoom_y = 2.0  # Zoom factor along y-axis
image = pdf_to_zoomed_image(pdf_pages_path, page_number, zoom_x, zoom_y)
image.save(local_machine+dir+"/pages_images/image_4.png")

pdf_pages_path = local_machine+dir+"/pages/page_1.pdf" 
page_number = 0  # Select the page number
zoom_x = 2.0  # Zoom factor along x-axis
zoom_y = 2.0  # Zoom factor along y-axis
image = pdf_to_zoomed_image(pdf_pages_path, page_number, zoom_x, zoom_y)
image.save(local_machine+dir+"/pages_images/image_1.png" )

def split_by_vertical_whitespace(input_path,output_folder_1,output_folder_2,n):
    for filename in os.listdir(input_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            file_no=re.findall(r'\d+', filename)
            file_no=int(file_no[0])
            img_path = os.path.join(input_path, filename)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise FileNotFoundError(f"Image not found at path: {input_path}")
            _, binary = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
            white_cols = np.where(np.all(binary == 255, axis=0))[0]
            splits = []
            start = 0
            min_gap = 10  # Minimum width of white gap to be considered a separator
            for i in range(1, len(white_cols)):
                if white_cols[i] != white_cols[i-1] + 1:
                    if white_cols[i-1] - white_cols[start] > min_gap:
                        split_point = (white_cols[start] + white_cols[i-1]) // 2
                        splits.append(split_point)
                    start = i
            if len(white_cols) > 0 and (white_cols[-1] - white_cols[start]) > min_gap:
                split_point = (white_cols[start] + white_cols[-1]) // 2
                splits.append(split_point)
            prev = 0
            for idx, split in enumerate(splits + [img.shape[1]]):  # Include end of image
                cropped = img[:, prev:split]
                if cropped.shape[1] > n:  # Avoid saving very narrow crops
                    if file_no==1:
                        output_path = os.path.join(output_folder_1, f"image_{file_no}_part_{idx+1}.png")
                    else:
                        output_path = os.path.join(output_folder_2, f"image_{file_no}_part_{idx+1}.png")
                        #print(output_path)
                    cv2.imwrite(output_path, cropped)
                prev = split
input_path = os.path.join(local_machine+dir+"/pages_images/")
folder_1="sub_images"
os.makedirs(folder_1, exist_ok=True)
output_folder_1 = local_machine+dir+"/"+folder_1
folder_2="vert_images"
os.makedirs(folder_2, exist_ok=True)
output_folder_2 = local_machine+dir+"/"+folder_2
split_by_vertical_whitespace(input_path,output_folder_1,output_folder_2,80)

####################Symbol Template Preparation###################
input_folder=local_machine+dir+"/sub_images/"
folder="sub_filtered_images"
os.makedirs(folder, exist_ok=True)
output_folder=local_machine+dir+"/sub_filtered_images/"
def filter_and_save_vert_split_images(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            if img.size[0] > int(img.size[1]/5):
                output_path = os.path.join(output_folder, filename)
                img.save(output_path)
filter_and_save_vert_split_images(input_folder, output_folder)
def horizontal_split(input_path,output_folder,N,file_name):
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Image not found at path: {input_path}")
    
    # Threshold the image to binary (white: 255, black: 0)
    _, binary = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
    
    # Find rows that are completely white
    white_rows = np.where(np.all(binary == 255, axis=1))[0]
    
    # Group consecutive white rows to detect whitespace regions
    splits = []
    start = 0
    min_gap = N  # Minimum gap height to be considered a separator
    for i in range(1, len(white_rows)):
        if white_rows[i] != white_rows[i-1] + 1:
            if white_rows[i-1] - white_rows[start] > min_gap:
                split_point = (white_rows[start] + white_rows[i-1]) // 2
                splits.append(split_point)
            start = i
    
    # Add last split if applicable
    if len(white_rows) > 0 and (white_rows[-1] - white_rows[start]) > min_gap:
        split_point = (white_rows[start] + white_rows[-1]) // 2
        splits.append(split_point)
    
    # Split the image using the detected horizontal whitespace positions
    prev = 0
    for idx, split in enumerate(splits + [img.shape[0]]):  # Add the end of image as final boundary
        cropped = img[prev:split, :]
        if cropped.shape[0] > 10:  # Avoid saving tiny crops
            output_path = os.path.join(output_folder, file_name+f"part_{idx+1}.png")
            cv2.imwrite(output_path, cropped)
        prev = split
def is_underlined(image_path, keyword):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Run OCR to get bounding boxes
    data = pytesseract.image_to_data(gray, output_type=Output.DICT)

    for i, word in enumerate(data["text"]):
        if word.strip().upper() == keyword.upper():
            # Bounding box for the word
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            
            # Define region just below the word
            roi_y1 = y + h
            roi_y2 = roi_y1 + 10  # 10-pixel band under the word
            roi = gray[roi_y1:roi_y2, x:x+w]
            
            # Use edge detection to see if there's a horizontal line
            edges = cv2.Canny(roi, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, math.pi/180, threshold=10, minLineLength=w//2, maxLineGap=5)

            if lines is not None:
                return True
    return False

def process_sub_images(input_folder,output_folder,keyword):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            file_path = os.path.join(input_folder, filename)
            if is_underlined(file_path, keyword):
                shutil.move(file_path, os.path.join(output_folder, filename))
def normalize_text(text):
    # Collapse multiple whitespaces/newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip().upper()
def contains_keyword(image_path, keyword):
    text = pytesseract.image_to_string(Image.open(image_path))
    text_clean = normalize_text(text)
    return keyword.upper() in text_clean.upper()

input_folder=local_machine+dir+"/sub_filtered_images/"
folder="abbreviations"
os.makedirs(folder, exist_ok=True)
output_folder=local_machine+dir+"/abbreviations/"
keyword = "ABBREVIATIONS"
process_sub_images(input_folder,output_folder,keyword)          
        
input_folder=local_machine+dir+"/sub_filtered_images/"
folder="plan_symbols"
os.makedirs(folder, exist_ok=True)
output_folder=local_machine+dir+"/plan_symbols/"
keyword = "PLAN SY"

for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        full_path = os.path.join(input_folder, filename)
        if contains_keyword(full_path, keyword):
            dest_path = os.path.join(output_folder, filename)
            shutil.move(full_path, dest_path)
            
input_folder=local_machine+dir+"/sub_filtered_images/"
folder="single_line_symbols"
os.makedirs(folder, exist_ok=True)
output_folder=local_machine+dir+"/single_line_symbols/"
keyword = "SINGLE LINE DIAGRAM SYMBOLS"
    
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        full_path = os.path.join(input_folder, filename)
        if contains_keyword(full_path, keyword):
            dest_path = os.path.join(output_folder, filename)
            shutil.move(full_path, dest_path)        
        
input_folder = local_machine+dir+"/abbreviations"
folder="csv_files"
os.makedirs(folder, exist_ok=True)
output_csv_path = local_machine+dir+"/csv_files/abbreviations_output.csv"
file_numb=[];file_name=[]
for filename in os.listdir(input_folder):
    file_no=re.findall(r'\d+', filename)
    file_name.append(filename)
image_path = os.path.join(input_folder, file_name[0])
try:
    img = Image.open(image_path)
    custom_config = r'--psm 6'
    extracted_text = pytesseract.image_to_string(img, config=custom_config)
    data = []
    lines = extracted_text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue # Skip empty lines
        parts = re.split(r'\s{2,}', line, maxsplit=1)

        abbreviation = None
        full_form = None

        if len(parts) == 2:
            # Success with primary method
            abbreviation = parts[0].strip()
            full_form = parts[1].strip()
            if abbreviation == '@' and not full_form and len(parts[0]) == 1 : # Added len check
                 #print(f"Warning: Line starting with solitary '@' might need manual check: '{line}'")
                 full_form = ""
        else:
            found_split_point = -1
            for i in range(len(line) - 2, 0, -1):
                if line[i] == ' ':
                    char_after = line[i+1]
                    if char_after.isupper():
                        found_split_point = i
                        break 
            if found_split_point != -1:
                abbreviation = line[:found_split_point].strip()
                full_form = line[found_split_point+1:].strip()
            elif line.startswith('@'):
                potential_split = re.split(r'(@)', line, maxsplit=1) # Format: ['', '@', 'RestOfLine']
                if len(potential_split) == 3 and potential_split[1] == '@':
                    abbreviation = '@'
                    full_form = potential_split[2].strip()
                    if not full_form: # If line was just "@ "
                         print(f"Warning: Line with only '@' potentially followed by space found: '{line}'")
                         full_form = "" # Assign empty string
                elif line == '@': # Handle line with only '@'
                     abbreviation = '@'
                     full_form = '' # Assign empty or placeholder?
                else: # Unrecognized pattern starting with @
                     print(f"Skipping line (unrecognized pattern starting with '@'): '{line}'")
                     continue
            elif line.strip() and ' ' not in line.strip():
                #print(f"Warning: Line contains single word, assigning to Abbreviation: '{line}'")
                abbreviation = line.strip()
                full_form = "" # Assign empty string to the second column
            else:
                print(f"Skipping line (primary & fallback split failed): '{line}'")
                continue # Skip to next line

        # Add the extracted data if valid
        if abbreviation is not None and full_form is not None:
             # Add even if one part is empty, might indicate OCR issue to fix manually
             data.append({'Abbreviation': abbreviation, 'Full Form': full_form})
    if data: # Only create DataFrame if data was actually extracted
        df = pd.DataFrame(data)
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
    else:
        print("\nNo data was successfully extracted to create a CSV.")
except FileNotFoundError:
    print(f"Error: Image file not found at '{image_path}'")
except pytesseract.TesseractNotFoundError:
     print("ERROR: Tesseract executable not found or not configured.")
     print("Please ensure Tesseract is installed and its path is correct (either in system PATH or set in the script).")
except Exception as e:
    print(f"An unexpected error occurred: {e}")        
      
input_folder=local_machine+dir+"/plan_symbols/"
folder="symbol_sub_images"
os.makedirs(folder, exist_ok=True)
output_folder=local_machine+dir+"/symbol_sub_images/"
file_numb=[]
for filename in os.listdir(input_folder):
    file_no=re.findall(r'\d+', filename)
    file_numb.append(int(file_no[1]))
mx=np.max(file_numb)
for filename in os.listdir(input_folder):
    file_no=re.findall(r'\d+', filename)
    if int(file_no[1])==mx:
        fx='symbol_'
        input_path = os.path.join(input_folder, filename)
        horizontal_split(input_path,output_folder,10,fx)       

def is_fully_white(image, threshold=250):
    return np.all(image >= threshold)

def has_text(image, min_text_pixels=500):
    # Convert to grayscale and detect non-white regions
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
    text_pixels = cv2.countNonZero(binary)
    return text_pixels > min_text_pixels

def process_images(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            file_path = os.path.join(folder_path, filename)
            image = cv2.imread(file_path)

            if image is None:
                print(f"Failed to read {filename}, skipping.")
                continue

            if is_fully_white(image):
                #print(f"Deleting fully white image: {filename}")
                os.remove(file_path)
            elif has_text(image):
                #print(f"Retaining image with text: {filename}")
                # Retain image as-is
                continue
            else:
                #print(f"No text detected, deleting: {filename}")
                os.remove(file_path)

process_images(output_folder)

def split_by_vertical_whitespace(input_path,output_folder,n):
    for filename in os.listdir(input_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            file_no=re.findall(r'\d+', filename)
            file_no=int(file_no[0])
            img_path = os.path.join(input_path, filename)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise FileNotFoundError(f"Image not found at path: {input_path}")
            _, binary = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
            white_cols = np.where(np.all(binary == 255, axis=0))[0]
            splits = []
            start = 0
            min_gap = 10  # Minimum width of white gap to be considered a separator
            for i in range(1, len(white_cols)):
                if white_cols[i] != white_cols[i-1] + 1:
                    if white_cols[i-1] - white_cols[start] > min_gap:
                        split_point = (white_cols[start] + white_cols[i-1]) // 2
                        splits.append(split_point)
                    start = i
            if len(white_cols) > 0 and (white_cols[-1] - white_cols[start]) > min_gap:
                split_point = (white_cols[start] + white_cols[-1]) // 2
                splits.append(split_point)
            prev = 0
            for idx, split in enumerate(splits + [img.shape[1]]):  # Include end of image
                cropped = img[:, prev:split]
                if cropped.shape[1] > n:  # Avoid saving very narrow crops
                    output_path = os.path.join(output_folder, f"image_{file_no}_part_{idx+1}.png")
                    cv2.imwrite(output_path, cropped)
                prev = split
input_folder = os.path.join(local_machine+dir+"/symbol_sub_images/")
folder_1="symbol_template_images/parts_images"
os.makedirs(folder_1, exist_ok=True)
folder_2="symbol_template_images/description_images"
os.makedirs(folder_2, exist_ok=True)
output_folder_1=local_machine+dir+"/symbol_template_images/parts_images/"
output_folder_2=local_machine+dir+"/symbol_template_images/description_images/"
lsize=[50,50,50,50,50,50,50,50,50,50,
       50,50,50,50,50,50,50,50,50,50,
       50,50,55,110,100,75,75,75,75,75,
       75,75,50,75,75,50,50,50,50,50]

usize=[75,160,100,100,100,100,100,100,100,100,
       0,160,160,75,85,80,90,90,90,93,
       220,130,210,150,170,110,110,120,130,120,
       130,130,130,130,125,210,170,170,170,210]

l_size=[0,0,0,0,0,0,0,0,0,0,
       0,0,0,0,0,0,0,0,0,0,
       0,0,0,10,0,0,0,0,0,0,
       0,0,20,0,10,0,0,0,0,0]
u_size=[50,50,50,50,50,50,50,50,50,50,
       50,50,50,50,80,50,50,50,50,50,
       50,70,50,40,88,50,50,50,50,50,
       50,50,50,50,50,50,50,50,50,60]
lvsize=[240,240,240,240,240,240,240,240,240,240,
        0,240,240,240,240,240,240,240,240,240,
        240,240,240,240,240,240,240,240,240,240,
        240,240,240,240,240,240,240,240,240,240]
uvsize=[400,700,600,600,500,750,550,650,600,780,
        0,600,650,500,450,800,900,950,700,700,
        900,1050,700,550,450,400,400,480,600,650,
        700,570,1040,900,600,600,800,800,700,800]
lv_size=[0];uv_size=[180]

cnt=0;fn=[];gx=[];g1=[];g2=[];gy=[]
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        img_path = os.path.join(input_folder, filename)
        f=filename.split('_')
        fn.append(img_path)
        gx.append(filename)
        if cnt!=10:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            
            if cnt not in [24,34]:
                cropped_1=img[l_size[cnt]:u_size[cnt],lsize[cnt]:usize[cnt]]
                cropped_2=img[:,lvsize[cnt]:uvsize[cnt]]
            else:
                #print(img_path)
                cropped_1=img[l_size[cnt]:u_size[cnt],lsize[cnt]:usize[cnt]]
                cropped_2=img[lv_size[0]+10:uv_size[0],lvsize[cnt]:uvsize[cnt]]
            
            output_path_1 = os.path.join(output_folder_1,filename)
            cv2.imwrite(output_path_1, cropped_1)
            output_path_2 = os.path.join(output_folder_2,'description_'+f[2])
            cv2.imwrite(output_path_2, cropped_2)
            g1.append(output_path_1);g2.append(output_path_2)
    cnt=cnt+1

split=[35,36,37,1,10,11,23]
typex=['H','H','H','H','H','H','H','V']
split_path_1=[g1[i] for i in split]
split_path_2=[g2[i] for i in split]
symb_rz_a=[];symb_rz_b=[];txt_rz=[]
for i in range(len(split)):
    img_1= cv2.imread(split_path_1[i], cv2.IMREAD_GRAYSCALE)
    img_2= cv2.imread(split_path_2[i], cv2.IMREAD_GRAYSCALE)
    h,w=img_1.shape
    if split[i]!=23:
        rsz_1=img_1[:,:int(w/2)]
        rsz_2=img_1[:,int(w/2):]
    else:
        rsz_1=img_1[0:int(h/2)+5,:]
        rsz_2=img_1[int(h/2)+5:,:w-30]
        rsz_1a=img_2[0:int(h/2),:]
        rsz_2a=img_2[int(h/2):,:]
    symb_rz_a.append(rsz_1);symb_rz_b.append(rsz_2)
    if split[i]!=23:
        txt_rz.append([img_2]*2)
    else:
        txt_rz.append([rsz_1a,rsz_2a])
txt_rz=[item for sublist in txt_rz for item in sublist]             
symb_split_a=['symbol_part_6a.png','symbol_part_7a.png','symbol_part_8a.png','symbol_part_11a.png',
            'symbol_part_20a.png','symbol_part_21a.png','symbol_part_32a.png']
symb_split_b=['symbol_part_6b.png','symbol_part_7b.png','symbol_part_8b.png','symbol_part_11b.png',
            'symbol_part_20b.png','symbol_part_21b.png','symbol_part_32b.png']
desc_split=['description_6a.png','description_6b.png',
            'description_7a.png','description_7b.png',
            'description_8a.png','description_8b.png',
            'description_11a.png','description_11b.png',
            'description_20a.png','description_20b.png',
            'description_21a.png','description_21b.png',
            'description_32a.png','description_32b.png']
for remv_path in split_path_1:
    os.remove(remv_path)
for remv_path in split_path_2:
    os.remove(remv_path)
for i in range(len(symb_split_a)):
    output_path_a = os.path.join(output_folder_1,symb_split_a[i])
    output_path_b = os.path.join(output_folder_1,symb_split_b[i])
    cv2.imwrite(output_path_a, symb_rz_a[i])
    cv2.imwrite(output_path_b, symb_rz_b[i])
for i in range(len(desc_split)):
    output_path_c = os.path.join(output_folder_2,desc_split[i])
    cv2.imwrite(output_path_c, txt_rz[i])
########################Processing Plan Images#############
input_folder=local_machine+dir+"/vert_images/"
folder="vert_filtered_images"
os.makedirs(folder, exist_ok=True)
output_folder=local_machine+dir+"/vert_filtered_images/"
filter_and_save_vert_split_images(input_folder, output_folder)

def split_by_horizontal_whitespace(input_path,output_folder,n):
    for filename in os.listdir(input_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            img_path = os.path.join(input_path, filename)
            #print(img_path)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise FileNotFoundError(f"Image not found at path: {input_path}")
            
            # Threshold the image to binary (white: 255, black: 0)
            _, binary = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
            
            # Find rows that are completely white
            white_rows = np.where(np.all(binary == 255, axis=1))[0]
            
            # Group consecutive white rows to detect whitespace regions
            splits = []
            start = 0
            min_gap = 10  # Minimum gap height to be considered a separator
            for i in range(1, len(white_rows)):
                if white_rows[i] != white_rows[i-1] + 1:
                    if white_rows[i-1] - white_rows[start] > min_gap:
                        split_point = (white_rows[start] + white_rows[i-1]) // 2
                        splits.append(split_point)
                    start = i
            
            # Add last split if applicable
            if len(white_rows) > 0 and (white_rows[-1] - white_rows[start]) > min_gap:
                split_point = (white_rows[start] + white_rows[-1]) // 2
                splits.append(split_point)
            
            # Split the image using the detected horizontal whitespace positions
            prev = 0
            for idx, split in enumerate(splits + [img.shape[0]]):  # Add the end of image as final boundary
                cropped = img[prev:split, :]
                if cropped.shape[0] >n:  # Avoid saving tiny crops
                    output_path = os.path.join(output_folder, f"page_1_sub_4_part_{idx+1}.png")
                    cv2.imwrite(output_path, cropped)
                prev = split
input_folder=local_machine+dir+"/vert_filtered_images/"
folder="horz_images"
os.makedirs(folder, exist_ok=True)
output_folder=local_machine+dir+"/horz_images/"
split_by_horizontal_whitespace(input_folder,output_folder,80)

def filter_and_save_horz_split_images(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            if img.size[1] > int(img.size[0]/4):
                output_path = os.path.join(output_folder, filename)
                img.save(output_path)
input_folder=local_machine+dir+"/horz_images/"
folder="horz_filtered_images"
os.makedirs(folder, exist_ok=True)
output_folder=local_machine+dir+"/horz_filtered_images/"
filter_and_save_horz_split_images(input_folder, output_folder)

def improve_contrast(gray):
    equalized = cv2.equalizeHist(gray)
    return equalized
input_folder=local_machine+dir+"/horz_filtered_images/"
folder="thresh_inv_images"
os.makedirs(folder, exist_ok=True)
output_folder=local_machine+dir+"/thresh_inv_images/"
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        img_path = os.path.join(input_folder, filename)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        binx, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
        histog = improve_contrast(thresh)
        op_img=Image.fromarray(histog)
        output_path = os.path.join(output_folder, filename)
        op_img.save(output_path)
def segment(img):
    #Threshold image to binary using OTSU. ALl thresholded pixels will be set to 255
    ret1, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 1)
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,3)
    thresh1=dist_transform.copy()
    thresh1[thresh1>2]=255
    return thresh1
def split_on_huge_transitions(data, absolute_threshold=500):
    data = np.array(data)
    diffs = np.diff(data)
    
    # Find indices where a huge jump occurs
    transition_indices = np.where(np.abs(diffs) > absolute_threshold)[0] + 1

    # Split data at transition points
    split_data = []
    prev_index = 0
    for index in transition_indices:
        split_data.append(data[prev_index:index].tolist())
        prev_index = index
    split_data.append(data[prev_index:].tolist())  # Add remaining part
    
    return split_data
def part_images_lw(lower_img,lw_array):
    part_1=lower_img[:,0:lw_array[0][1]-lw_array[0][2]]
    part_2=lower_img[:,lw_array[0][1]+lw_array[0][2]:lw_array[1][1]-lw_array[1][2]]
    part_3=lower_img[:,lw_array[1][1]+lw_array[1][2]:]
    output_path= os.path.join(output_folder, "part_1.png")
    cv2.imwrite(output_path, part_1)
    output_path= os.path.join(output_folder, "part_2.png")
    cv2.imwrite(output_path, part_2)
    output_path= os.path.join(output_folder, "part_3.png")
    cv2.imwrite(output_path, part_3)
def part_images_uw(lower_img,lw_array):
    part_1=lower_img[10:,0:lw_array[0][1]-lw_array[0][2]]
    part_2=lower_img[10:,lw_array[0][1]+lw_array[0][2]:lw_array[1][1]-lw_array[1][2]]
    part_3=lower_img[10:,lw_array[1][1]+lw_array[1][2]:]
    output_path= os.path.join(output_folder, "part_4.png")
    cv2.imwrite(output_path, part_1)
    output_path= os.path.join(output_folder, "part_5.png")
    cv2.imwrite(output_path, part_2)
    output_path= os.path.join(output_folder, "part_6.png")
    cv2.imwrite(output_path, part_3)

input_folder=local_machine+dir+"/thresh_inv_images/"
folder="segment_images"
os.makedirs(folder, exist_ok=True)
output_folder=local_machine+dir+"/segment_images/"
for filename in os.listdir(input_folder):
    image_path = os.path.join(input_folder, filename)
    img1= cv2.imread(image_path)  #now, we can read each file since we have the full path
    img = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
    thresh1=segment(img)
    x=thresh1.sum(axis=1)
    x_ceil=[k for k in range(len(x)) if x[k] > 0.5*np.max(x)]
    segmentsx = split_on_huge_transitions(x_ceil,absolute_threshold=500)
    arrx=[]
    for i in range(len(segmentsx)):
        sg=segmentsx[i]
        meanx=int(np.mean(sg))
        arrx.append([meanx-np.min(sg), meanx,np.max(sg)-meanx]);
    # lower_img=img[:idx-12,:]
    lower_img=img[0:arrx[0][1]-arrx[0][0],:]
    upper_img=img[arrx[0][1]+arrx[0][2]:,:]
    lw_thresh=segment(lower_img)
    lower_y=lw_thresh.sum(axis=0)
    lw_y_ceil=[k for k in range(len(lower_y)) if lower_y[k] > 0.5*np.max(lower_y)]
    uw_thresh=segment(upper_img)
    upper_y=uw_thresh.sum(axis=0)
    uw_y_ceil=[k for k in range(len(upper_y)) if upper_y[k] > 0.5*np.max(upper_y)]
    lw_segment= split_on_huge_transitions(lw_y_ceil,absolute_threshold=500)
    uw_segment= split_on_huge_transitions(uw_y_ceil,absolute_threshold=500)
    lw_array=[]
    for i in range(len(lw_segment)):
        sg=lw_segment[i]
        mean_lw=int(np.mean(sg))
        lw_array.append([mean_lw-np.min(sg), mean_lw,np.max(sg)-mean_lw]);
    uw_array=[]
    for i in range(len(uw_segment)):
        sg=uw_segment[i]
        mean_uw=int(np.mean(sg))
        uw_array.append([mean_uw-np.min(sg), mean_uw,np.max(sg)-mean_uw]);
    part_images_lw(lower_img,lw_array)
    part_images_uw(upper_img,uw_array)
idx=['17','14','6a','31','34','35','4','33','22',
     '6b','5','40','30','36','21a','20b','20a',
     '21b','15','12','10','7b','7a','32b',
     '26','28','27','41','25','16','8a','8b',
     '11a','11b','24','13','23','32a',
     '18','19','37','38','39','3','9','29']
val=[3]+[2]*2+[1]*4+[0.5]*4+[0.4]*3+[0.9]*9+[0.2]*14+[0.1]*7+[0]*2
lst_idx=['description_'+i+'.png' for i in idx]
weight=pd.DataFrame()
weight['desc_filename']=lst_idx
weight['scale_weight']=val
# def remove_small_text(img, min_size=10):
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     config = r'--oem 3 --psm 6'
#     data = pytesseract.image_to_data(gray, config=config, output_type=pytesseract.Output.DICT)
#     n_boxes = len(data['level'])
#     for i in range(n_boxes):
#         if data['level'][i] == 5:
#             (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
#             if w < min_size or h < min_size:
#                 cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0,0), -1)
#     return img
# input_folder=local_machine+dir+"/segment_images/"
# folder="inpainted_images"
# os.makedirs(folder, exist_ok=True)
# output_folder=local_machine+dir+"/inpainted_images/"
# for filename in os.listdir(input_folder):
#     if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
#         ip_path=os.path.join(input_folder, filename)
#         img_text = cv2.imread(ip_path)
#         im_text=img_text.copy()
#         for min_text_size in [20,19,18,17,16,15,14,13,12,11,10]:
#             processed_image = remove_small_text(im_text, min_text_size)
#             im_text=processed_image.copy()
#             output_path= os.path.join(output_folder, filename)
#             cv2.imwrite(output_path, im_text)
#######################Finding the Count###################
INPUT_FLOOR_PLAN_IMAGE = local_machine+dir+"/segment_images/part_1.png"
INPUT_TEMPLATE_SYMBOLS_DIR = local_machine+dir+"/symbol_template_images/parts_images/"
INPUT_TEMPLATE_DESCRIPTIONS_DIR = local_machine+dir+"/symbol_template_images/description_images/"

RESIZE_FACTOR = 0.4 # <<<--- Further reduced resize factor
NMS_THRESHOLD = 0.1   # NMS threshold (0.3 is usually okay)
OUTPUT_CSV_PATH = local_machine+dir+"/csv_files/"

def get_desc_filename(symbol_filename):
    match = re.match(r"symbol_(\d+)\.(png|jpg|jpeg|bmp|gif)", symbol_filename, re.IGNORECASE)
    if match: return f"description_{match.group(1)}.{match.group(2)}"
    if symbol_filename.startswith("symbol_"): 
        return "description_" + symbol_filename[len("symbol_"):]
    return None

def clean_ocr_text(text):
    if not text: return ""
    return ' '.join(text.split()).strip()

def group_rectangles(rects, threshold):
    if len(rects) == 0: return []
    boxes = np.array([[x, y, x + w, y + h] for x, y, w, h in rects])
    scores = np.ones(len(boxes)); x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (x2 - x1 + 1) * (y2 - y1 + 1); order = scores.argsort()[::-1]; keep = []
    while order.size > 0:
        i = order[0]; keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]]); yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]]); yy2 = np.minimum(y2[i], y2[order[1:]])
        w_overlap = np.maximum(0.0, xx2 - xx1 + 1); h_overlap = np.maximum(0.0, yy2 - yy1 + 1)
        intersection = w_overlap * h_overlap; overlap = intersection / (areas[i] + areas[order[1:]] - intersection + 1e-5)
        inds = np.where(overlap <= threshold)[0]; order = order[inds + 1]
    return [rects[i] for i in keep]

template_files = sorted([f for f in os.listdir(INPUT_TEMPLATE_SYMBOLS_DIR) if f.lower().startswith('symbol_') and f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))])
detections_coords=[];file_details=[]
for filename in template_files:
    symbol_path = os.path.join(INPUT_TEMPLATE_SYMBOLS_DIR, filename)
    z=filename.replace(".png","")
    z1=z.split("_")
    desc_filename='description_'+z1[2]+'.png'
    #desc_filename = get_desc_filename(filename)
    desc_path = os.path.join(INPUT_TEMPLATE_DESCRIPTIONS_DIR, desc_filename) if desc_filename else None
    template_pil = Image.open(symbol_path)
    template_cv_gray = cv2.cvtColor(np.array(template_pil.convert('RGB')), cv2.COLOR_RGB2GRAY)
    h_o, w_o = template_cv_gray.shape[:2]

    w_r = max(1, int(w_o)); h_r = max(1, int(h_o))
    template_cv_gray_resized = cv2.resize(template_cv_gray, (w_r, h_r), interpolation=cv2.INTER_AREA)
    # Binarize template (assuming white symbols)
    _, template_cv_binary_resized = cv2.threshold(template_cv_gray_resized, 128, 255, cv2.THRESH_BINARY)
    floor_plan_img_color = cv2.imread(INPUT_FLOOR_PLAN_IMAGE)
    if floor_plan_img_color is None: raise ValueError("Could not read floor plan.")
    floor_plan_gray_original = cv2.cvtColor(floor_plan_img_color, cv2.COLOR_BGR2GRAY)
    h_orig, w_orig = floor_plan_gray_original.shape
    w_resized = int(w_orig); h_resized = int(h_orig)
    floor_plan_gray_resized = cv2.resize(floor_plan_gray_original, (w_resized, h_resized), interpolation=cv2.INTER_AREA)
    # Binarize floor plan (assuming white symbols on black background)
    _, floor_plan_binary_resized = cv2.threshold(floor_plan_gray_resized, 50, 255, cv2.THRESH_BINARY)
    
   
    #res = cv2.matchTemplate(floor_plan_binary_resized, template_cv_binary_resized, cv2.TM_CCOEFF_NORMED)
    sift = cv2.SIFT_create()
    
    kp1, des1 = sift.detectAndCompute(template_cv_binary_resized, None)
    kp2, des2 = sift.detectAndCompute(floor_plan_binary_resized, None)
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good_matches = []
    for m, n in matches:
        if m.distance < n.distance:
            good_matches.append(m)
    
    input_coordinates = []
    template_coordinates = []

    if len(good_matches) > 0:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)
    
        for i in range(len(good_matches)):
          input_coordinates.append(src_pts[i][0].tolist())
          template_coordinates.append(dst_pts[i][0].tolist())
    ip_coordinates=(list(map(list,set(map(tuple,input_coordinates)))))
    tp_coordinates=(list(map(list,set(map(tuple,template_coordinates)))))
    count_ip = len(ip_coordinates)
    count_tp = len(tp_coordinates)
    desc_full_path = os.path.join(INPUT_TEMPLATE_DESCRIPTIONS_DIR, desc_filename)
    desc_img = Image.open(desc_full_path)
    custom_config = r'--oem 3 --psm 6'
    ocr_raw_text = pytesseract.image_to_string(desc_img, config=custom_config, lang='eng')
    description_text = clean_ocr_text(ocr_raw_text)
    file_details.append([desc_filename,filename,description_text,count_ip,count_tp])
col=['desc_filename','symbol_filename','description_text','min_count', 'max_count']
file_details_df=pd.DataFrame(file_details,columns=col)
#file_details_df = file_details_df.sort_values(by=['count_pos'], ascending=False)
wfile_details=pd.merge(file_details_df,weight,on=['desc_filename'])
wfile_details['min_count']=wfile_details.apply(lambda x:int(np.round(x['min_count']*x['scale_weight'],0)),axis=1)
wfile_details['max_count']=wfile_details.apply(lambda x:int(np.round(x['max_count']*x['scale_weight'],0)),axis=1)
wfile_details = wfile_details.sort_values(by=['min_count'], ascending=False).reset_index(drop=True)
wfile_details.drop(['scale_weight'], axis=1, inplace=True)
df_sorted = pd.DataFrame(np.sort(wfile_details[['min_count', 'max_count']].values, axis=1), columns=['min_count', 'max_count'])
wfile_details=pd.concat([wfile_details.iloc[:,0:3],df_sorted],axis=1)

wfile_details.to_csv(os.path.join(OUTPUT_CSV_PATH, 'extracted_details.csv'),index=False)

end_time = datetime.now()
print('Code Exection Time: {}'.format(end_time - start_time))
print("End of Code Execution") 
