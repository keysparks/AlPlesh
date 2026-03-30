import os
from datetime import datetime
import config
import pdf_processor
import image_utils
import symbol_matcher

def main():
    start_time = datetime.now()
    
    print("Setting up directories...")
    config.create_directories()
    
    print("Processing explicit Floor Plan input (PDF or Image)...")
    if not pdf_processor.process_input_file(config.FLOOR_PLAN_PREFIX, "image_4.png", auto_detect_floorplan=True):
        print("Analysis aborted: Missing Floor Plan file.")
        
    print("Applying structural geometry matching against complete Floor Plan...")
    floor_plan_target = os.path.join(config.PAGES_IMAGES_DIR, "image_4.png")
    if os.path.exists(floor_plan_target):
        symbol_matcher.extract_symbols_and_match(floor_plan_target, config.CSV_FILES_DIR)
        print(f"Analysis saved to: {os.path.join(config.CSV_FILES_DIR, 'extracted_details.csv')}")
    else:
        print("Floor plan image (image_4.png) not found for engine matching.")

    end_time = datetime.now()
    print('Floor Plan Analysis Execution Time: {}'.format(end_time - start_time))

if __name__ == "__main__":
    main()
