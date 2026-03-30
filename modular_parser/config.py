import os

# Base paths
# Dynamically get the current script directory (modular_parser) wrapper
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Input and Output Directories
INPUT_DIR = os.path.join(BASE_DIR, "inputs")
LEGEND_PREFIX = "legend"
FLOOR_PLAN_PREFIX = "floor_plan"
TARGET_FLOOR_PLAN_DRAWING = "E1-1"
PAGES_DIR = os.path.join(BASE_DIR, "pages")
PAGES_IMAGES_DIR = os.path.join(BASE_DIR, "pages_images")
SUB_IMAGES_DIR = os.path.join(BASE_DIR, "sub_images")
VERT_IMAGES_DIR = os.path.join(BASE_DIR, "vert_images")
SUB_FILTERED_DIR = os.path.join(BASE_DIR, "sub_filtered_images")
VERT_FILTERED_DIR = os.path.join(BASE_DIR, "vert_filtered_images")
ABBREVIATIONS_DIR = os.path.join(BASE_DIR, "abbreviations")
PLAN_SYMBOLS_DIR = os.path.join(BASE_DIR, "plan_symbols")
SINGLE_LINE_SYMBOLS_DIR = os.path.join(BASE_DIR, "single_line_symbols")
CSV_FILES_DIR = os.path.join(BASE_DIR, "csv_files")
SYMBOL_SUB_IMAGES_DIR = os.path.join(BASE_DIR, "symbol_sub_images")
HORZ_IMAGES_DIR = os.path.join(BASE_DIR, "horz_images")
HORZ_FILTERED_DIR = os.path.join(BASE_DIR, "horz_filtered_images")
THRESH_INV_DIR = os.path.join(BASE_DIR, "thresh_inv_images")
SEGMENT_IMAGES_DIR = os.path.join(BASE_DIR, "segment_images")

TEMPLATE_PARTS_DIR = os.path.join(BASE_DIR, "symbol_template_images", "parts_images")
TEMPLATE_DESC_DIR = os.path.join(BASE_DIR, "symbol_template_images", "description_images")


TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Arrays for coordinate splitting logic
LSIZE = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,55,110,100,75,75,75,75,75,75,75,50,75,75,50,50,50,50,50]
USIZE = [75,160,100,100,100,100,100,100,100,100,0,160,160,75,85,80,90,90,90,93,220,130,210,150,170,110,110,120,130,120,130,130,130,130,125,210,170,170,170,210]
L_SIZE = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,10,0,0,0,0,0,0,0,0,20,0,10,0,0,0,0,0]
U_SIZE = [50,50,50,50,50,50,50,50,50,50,50,50,50,50,80,50,50,50,50,50,50,70,50,40,88,50,50,50,50,50,50,50,50,50,50,50,50,50,50,60]
LVSIZE = [240,240,240,240,240,240,240,240,240,240,0,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240]
UVSIZE = [400,700,600,600,500,750,550,650,600,780,0,600,650,500,450,800,900,950,700,700,900,1050,700,550,450,400,400,480,600,650,700,570,1040,900,600,600,800,800,700,800]
LV_SIZE = [0]
UV_SIZE = [180]

# Weight Mapping
IDX = ['17','14','6a','31','34','35','4','33','22','6b','5','40','30','36','21a','20b','20a','21b','15','12','10','7b','7a','32b','26','28','27','41','25','16','8a','8b','11a','11b','24','13','23','32a','18','19','37','38','39','3','9','29']
VAL = [3]+[2]*2+[1]*4+[0.5]*4+[0.4]*3+[0.9]*9+[0.2]*14+[0.1]*7+[0]*2

def create_directories():
    directories = [INPUT_DIR, PAGES_DIR, PAGES_IMAGES_DIR, SUB_IMAGES_DIR, VERT_IMAGES_DIR,
                   SUB_FILTERED_DIR, VERT_FILTERED_DIR, ABBREVIATIONS_DIR, PLAN_SYMBOLS_DIR,
                   SINGLE_LINE_SYMBOLS_DIR, CSV_FILES_DIR, SYMBOL_SUB_IMAGES_DIR, 
                   HORZ_IMAGES_DIR, HORZ_FILTERED_DIR, THRESH_INV_DIR, SEGMENT_IMAGES_DIR,
                   TEMPLATE_PARTS_DIR, TEMPLATE_DESC_DIR]
    for d in directories:
        os.makedirs(d, exist_ok=True)
