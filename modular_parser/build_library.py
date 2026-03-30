import os
from datetime import datetime
import numpy as np
import re

import config
import pdf_processor
import image_utils
import ocr_extractor

def main():
    start_time = datetime.now()
    
    print("Setting up directories...")
    config.create_directories()
    
    print("Processing explicit Legend input (PDF or Image)...")
    if not pdf_processor.process_input_file(config.LEGEND_PREFIX, "image_1.png", auto_detect=True):
        print("Build library aborted: Missing Legend file.")
        return
        
    print("Splitting legend image by vertical whitespace...")
    image_utils.split_by_vertical_whitespace(config.PAGES_IMAGES_DIR, config.SUB_IMAGES_DIR, config.VERT_IMAGES_DIR, 80)
    
    print("Filtering vertically split images...")
    image_utils.filter_and_save_vert_split_images(config.SUB_IMAGES_DIR, config.SUB_FILTERED_DIR)
    
    print("Extracting and processing abbreviations and symbols from filtered chunks...")
    ocr_extractor.process_sub_images(config.SUB_FILTERED_DIR, config.ABBREVIATIONS_DIR, "ABBREVIATIONS")
    ocr_extractor.move_if_keyword_present(config.SUB_FILTERED_DIR, config.PLAN_SYMBOLS_DIR, "PLAN SY")
    ocr_extractor.move_if_keyword_present(config.SUB_FILTERED_DIR, config.SINGLE_LINE_SYMBOLS_DIR, "SINGLE LINE DIAGRAM SYMBOLS")
    
    print("Writing abbreviations data to CSV...")
    csv_output = os.path.join(config.CSV_FILES_DIR, "abbreviations_output.csv")
    ocr_extractor.extract_abbreviations_to_csv(config.ABBREVIATIONS_DIR, csv_output)
    
    print("Extracting raw symbol parts dynamically...")
    if os.path.exists(config.PLAN_SYMBOLS_DIR):
        file_numb = []
        for filename in os.listdir(config.PLAN_SYMBOLS_DIR):
            file_no = re.findall(r'\d+', filename)
            if len(file_no) > 1:
                file_numb.append(int(file_no[1]))
        if file_numb:
            mx = np.max(file_numb)
            for filename in os.listdir(config.PLAN_SYMBOLS_DIR):
                file_no = re.findall(r'\d+', filename)
                if len(file_no) > 1 and int(file_no[1]) == mx:
                    input_path = os.path.join(config.PLAN_SYMBOLS_DIR, filename)
                    image_utils.horizontal_split(input_path, config.SYMBOL_SUB_IMAGES_DIR, 10, 'symbol_')
    
    print("Filtering exact symbol templates and building Library...")
    image_utils.process_images_clean_textless(config.SYMBOL_SUB_IMAGES_DIR)
    image_utils.extract_symbol_templates(config.SYMBOL_SUB_IMAGES_DIR, config.TEMPLATE_PARTS_DIR, config.TEMPLATE_DESC_DIR)

    end_time = datetime.now()
    print('Library Construction Execution Time: {}'.format(end_time - start_time))
    print(f"Permanent Symbol Library successfully updated at: {config.TEMPLATE_PARTS_DIR}")

if __name__ == "__main__":
    main()
