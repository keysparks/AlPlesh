import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import pytesseract
import config

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

def clean_ocr_text(text):
    if not text: return ""
    return ' '.join(text.split()).strip()

def extract_symbols_and_match(floor_plan_image_path, output_csv_path):
    template_files = sorted([f for f in os.listdir(config.TEMPLATE_PARTS_DIR) if f.lower().startswith('symbol_') and f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))])
    
    # Pre-process the floor plan image ONCE outside the loop
    floor_plan_img_color = cv2.imread(floor_plan_image_path)
    if floor_plan_img_color is None:
        print(f"Error: Could not read floor plan image {floor_plan_image_path}")
        return
        
    floor_plan_gray_original = cv2.cvtColor(floor_plan_img_color, cv2.COLOR_BGR2GRAY)
    floor_plan_gray_resized = cv2.resize(floor_plan_gray_original, (floor_plan_gray_original.shape[1], floor_plan_gray_original.shape[0]), interpolation=cv2.INTER_AREA)
    
    # Erase light gray drafting lines: 
    # Anything lighter than 200 becomes solid white (255). Solid structures (< 200) become solid black (0).
    _, floor_plan_clean = cv2.threshold(floor_plan_gray_resized, 200, 255, cv2.THRESH_BINARY)
    
    # Save a diagnostic copy so the user can literally see the gray lines magically erased in the folder
    cv2.imwrite(os.path.join(output_csv_path, 'diagnostic_clean_background.png'), floor_plan_clean)
    
    file_details = []
    for filename in template_files:
        symbol_path = os.path.join(config.TEMPLATE_PARTS_DIR, filename)
        z = filename.replace(".png", "").replace(".jpg","")
        z1 = z.split("_")
        if len(z1) > 2:
            desc_filename = 'description_' + z1[2] + '.png'
        else:
            desc_filename = 'description_' + z1[-1] + '.png'
            
        desc_path = os.path.join(config.TEMPLATE_DESC_DIR, desc_filename)
        
        template_pil = Image.open(symbol_path)
        template_cv_gray = cv2.cvtColor(np.array(template_pil.convert('RGB')), cv2.COLOR_RGB2GRAY)
        
        # Auto-crop excessive white padding to prevent adjacent symbols from penalizing the match score
        _, _temp_bin = cv2.threshold(template_cv_gray, 200, 255, cv2.THRESH_BINARY_INV)
        _coords = cv2.findNonZero(_temp_bin)
        if _coords is not None:
            _tx, _ty, _tw, _th = cv2.boundingRect(_coords)
            _tx, _ty = max(0, _tx - 2), max(0, _ty - 2)
            _tw, _th = min(template_cv_gray.shape[1] - _tx, _tw + 4), min(template_cv_gray.shape[0] - _ty, _th + 4)
            template_cv_gray = template_cv_gray[_ty:_ty+_th, _tx:_tx+_tw]
            
        h_o, w_o = template_cv_gray.shape[:2]
        
        w_r, h_r = max(1, int(w_o)), max(1, int(h_o))
        template_cv_gray_resized = cv2.resize(template_cv_gray, (w_r, h_r), interpolation=cv2.INTER_AREA)
        _, template_clean = cv2.threshold(template_cv_gray_resized, 200, 255, cv2.THRESH_BINARY)
        
        # Execute multi-axis Template Matching correlation to detect symbols on perpendicular walls
        match_threshold = 0.65  # Recalibrated to strict unpadded geometry
        rects = []
        for k in range(4):
            rotated_template = np.rot90(template_clean, k)
            res = cv2.matchTemplate(floor_plan_clean, rotated_template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= match_threshold)
            
            rot_w = int(w_r) if k % 2 == 0 else int(h_r)
            rot_h = int(h_r) if k % 2 == 0 else int(w_r)
            
            for pt in zip(*loc[::-1]):
                rects.append([int(pt[0]), int(pt[1]), rot_w, rot_h])
            
        boxes = []
        if len(rects) > 0:
            rects = np.array(rects)
            pick = []
            x1 = rects[:,0]
            y1 = rects[:,1]
            x2 = rects[:,0] + rects[:,2]
            y2 = rects[:,1] + rects[:,3]
            area = (x2 - x1 + 1) * (y2 - y1 + 1)
            idxs = np.argsort(y2)
            
            while len(idxs) > 0:
                last = len(idxs) - 1
                i = idxs[last]
                pick.append(i)
                suppress = [last]
                for pos in range(last):
                    j = idxs[pos]
                    xx1 = max(x1[i], x1[j])
                    yy1 = max(y1[i], y1[j])
                    xx2 = min(x2[i], x2[j])
                    yy2 = min(y2[i], y2[j])
                    w = max(0, xx2 - xx1 + 1)
                    h = max(0, yy2 - yy1 + 1)
                    overlap = float(w * h) / area[j]
                    if overlap > 0.3:
                        suppress.append(pos)
                idxs = np.delete(idxs, suppress)
            boxes = rects[pick].tolist()
            
        count_ip = len(boxes)
        count_tp = len(boxes)
        
        # Feature: Draw Bounding Recangles for Visual Verification
        import binascii
        crc = binascii.crc32(filename.encode('utf8'))
        color = (int(crc & 0xFF), int((crc >> 8) & 0xFF), int((crc >> 16) & 0xFF))
        
        for b in boxes:
            x, y, w, h = b
            cv2.rectangle(floor_plan_img_color, (x, y), (x + w, y + h), color, 4)
                
        description_text = ""
        if os.path.exists(desc_path):
            desc_img = Image.open(desc_path)
            custom_config = r'--oem 3 --psm 6'
            ocr_raw_text = pytesseract.image_to_string(desc_img, config=custom_config, lang='eng')
            description_text = clean_ocr_text(ocr_raw_text)
            
        file_details.append([desc_filename, filename, description_text, count_ip, count_tp])

    if not file_details: return
    
    col = ['desc_filename', 'symbol_filename', 'description_text', 'min_count', 'max_count']
    file_details_df = pd.DataFrame(file_details, columns=col)
    
    lst_idx = ['description_'+i+'.png' for i in config.IDX]
    weight = pd.DataFrame({'desc_filename': lst_idx, 'scale_weight': config.VAL})
    
    wfile_details = pd.merge(file_details_df, weight, on=['desc_filename'])
    wfile_details['min_count'] = wfile_details.apply(lambda x: int(np.round(x['min_count']*x['scale_weight'], 0)), axis=1)
    wfile_details['max_count'] = wfile_details.apply(lambda x: int(np.round(x['max_count']*x['scale_weight'], 0)), axis=1)
    wfile_details = wfile_details.sort_values(by=['min_count'], ascending=False).reset_index(drop=True)
    wfile_details.drop(['scale_weight'], axis=1, inplace=True)
    
    df_sorted = pd.DataFrame(np.sort(wfile_details[['min_count', 'max_count']].values, axis=1), columns=['min_count', 'max_count'])
    wfile_details = pd.concat([wfile_details.iloc[:,0:3], df_sorted], axis=1)
    
    csv_target = os.path.join(output_csv_path, 'extracted_details.csv')
    try:
        wfile_details.to_csv(csv_target, index=False)
    except PermissionError:
        csv_target = os.path.join(output_csv_path, 'extracted_details_safe_copy.csv')
        wfile_details.to_csv(csv_target, index=False)
        print(f"Warning: Original CSV locked by another app. Saved to: {csv_target}")
    
    # Save the rendered Verification Map
    annotated_output_path = os.path.join(output_csv_path, 'visual_takeoff_report.png')
    cv2.imwrite(annotated_output_path, floor_plan_img_color)
    print(f"Visual overlay report generated at: {annotated_output_path}")
