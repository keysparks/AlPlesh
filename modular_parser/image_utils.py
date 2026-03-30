import os
import cv2
import numpy as np
from PIL import Image
import re
import config

def filter_and_save_images(input_folder, output_folder, condition_func):
    """Generic function to filter images based on a lambda condition."""
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            if condition_func(img.size):
                img.save(os.path.join(output_folder, filename))

def find_whitespace_splits(img, axis, min_gap):
    _, binary = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
    white_lines = np.where(np.all(binary == 255, axis=axis))[0]
    splits = []
    if len(white_lines) == 0: return splits
    start = 0
    for i in range(1, len(white_lines)):
        if white_lines[i] != white_lines[i-1] + 1:
            if white_lines[i-1] - white_lines[start] > min_gap:
                split_point = (white_lines[start] + white_lines[i-1]) // 2
                splits.append(split_point)
            start = i
    if (white_lines[-1] - white_lines[start]) > min_gap:
        split_point = (white_lines[start] + white_lines[-1]) // 2
        splits.append(split_point)
    return splits

def unified_split_by_whitespace(file_path, axis, min_gap, min_crop_size, filename_formatter_func):
    """axis=0 for vertical, axis=1 for horizontal"""
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return
    splits = find_whitespace_splits(img, axis, min_gap)
    prev = 0
    img_bound = img.shape[1] if axis == 0 else img.shape[0]
    for idx, split in enumerate(splits + [img_bound]):
        cropped = img[:, prev:split] if axis == 0 else img[prev:split, :]
        crop_size = cropped.shape[1] if axis == 0 else cropped.shape[0]
        if crop_size > min_crop_size:
            filename_formatter_func(os.path.basename(file_path), idx, cropped)
        prev = split
            
def split_by_vertical_whitespace(input_folder, output_folder_1, output_folder_2=None, n=80, is_symbol=False):
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')): continue
        
        def formatter(fname, idx, cropped):
            m = re.findall(r'\d+', fname)
            file_no = int(m[0]) if m else 0
            if is_symbol:
                cv2.imwrite(os.path.join(output_folder_1, f"image_{file_no}_part_{idx+1}.png"), cropped)
            else:
                if file_no == 1 and output_folder_1:
                    cv2.imwrite(os.path.join(output_folder_1, f"image_{file_no}_part_{idx+1}.png"), cropped)
                elif output_folder_2:
                    cv2.imwrite(os.path.join(output_folder_2, f"image_{file_no}_part_{idx+1}.png"), cropped)
                else:
                    cv2.imwrite(os.path.join(output_folder_1, f"image_{file_no}_part_{idx+1}.png"), cropped)
                    
        unified_split_by_whitespace(os.path.join(input_folder, filename), 0, 10, n, formatter)

def filter_and_save_vert_split_images(input_folder, output_folder):
    filter_and_save_images(input_folder, output_folder, lambda size: size[0] > int(size[1]/5))

def filter_and_save_horz_split_images(input_folder, output_folder):
    filter_and_save_images(input_folder, output_folder, lambda size: size[1] > int(size[0]/4))

def horizontal_split(input_path, output_folder, N, file_prefix):
    def formatter(fname, idx, cropped):
        cv2.imwrite(os.path.join(output_folder, file_prefix + f"part_{idx+1}.png"), cropped)
    unified_split_by_whitespace(input_path, 1, N, 10, formatter)

def split_by_horizontal_whitespace(input_folder, output_folder, n):
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')): continue
        def formatter(fname, idx, cropped):
            cv2.imwrite(os.path.join(output_folder, f"page_1_sub_4_part_{idx+1}.png"), cropped)
        unified_split_by_whitespace(os.path.join(input_folder, filename), 1, 10, n, formatter)

def is_fully_white(image, threshold=250):
    return np.all(image >= threshold)

def has_text(image, min_text_pixels=500):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
    text_pixels = cv2.countNonZero(binary)
    return text_pixels > min_text_pixels

def process_images_clean_textless(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            file_path = os.path.join(folder_path, filename)
            image = cv2.imread(file_path)
            if image is None: continue
            if is_fully_white(image):
                os.remove(file_path)
            elif has_text(image):
                continue
            else:
                os.remove(file_path)

def improve_contrast_and_invert(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            img_path = os.path.join(input_folder, filename)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
            histog = cv2.equalizeHist(thresh)
            cv2.imwrite(os.path.join(output_folder, filename), histog)

def segment(img):
    ret1, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 3)
    thresh1 = dist_transform.copy()
    thresh1[thresh1>2] = 255
    return thresh1

def split_on_huge_transitions(data, absolute_threshold=500):
    data = np.array(data)
    if len(data) == 0: return []
    diffs = np.diff(data)
    transition_indices = np.where(np.abs(diffs) > absolute_threshold)[0] + 1
    split_data = []
    prev_index = 0
    for index in transition_indices:
        split_data.append(data[prev_index:index].tolist())
        prev_index = index
    split_data.append(data[prev_index:].tolist())
    return split_data

def part_images_lw(lower_img, lw_array, output_folder):
    part_1 = lower_img[:, 0:lw_array[0][1]-lw_array[0][2]]
    part_2 = lower_img[:, lw_array[0][1]+lw_array[0][2]:lw_array[1][1]-lw_array[1][2]]
    part_3 = lower_img[:, lw_array[1][1]+lw_array[1][2]:]
    cv2.imwrite(os.path.join(output_folder, "part_1.png"), part_1)
    cv2.imwrite(os.path.join(output_folder, "part_2.png"), part_2)
    cv2.imwrite(os.path.join(output_folder, "part_3.png"), part_3)

def part_images_uw(upper_img, uw_array, output_folder):
    part_4 = upper_img[10:, 0:uw_array[0][1]-uw_array[0][2]]
    part_5 = upper_img[10:, uw_array[0][1]+uw_array[0][2]:uw_array[1][1]-uw_array[1][2]]
    part_6 = upper_img[10:, uw_array[1][1]+uw_array[1][2]:]
    cv2.imwrite(os.path.join(output_folder, "part_4.png"), part_4)
    cv2.imwrite(os.path.join(output_folder, "part_5.png"), part_5)
    cv2.imwrite(os.path.join(output_folder, "part_6.png"), part_6)

def apply_segmentation_logic(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')): continue
        image_path = os.path.join(input_folder, filename)
        img1 = cv2.imread(image_path)
        if img1 is None: continue
        img = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        thresh1 = segment(img)
        x = thresh1.sum(axis=1)
        x_ceil = [k for k in range(len(x)) if x[k] > 0.5*np.max(x)]
        if not x_ceil: continue
        segmentsx = split_on_huge_transitions(x_ceil, absolute_threshold=500)
        if not segmentsx: continue
        
        arrx = []
        for sg in segmentsx:
            if not sg: continue
            meanx = int(np.mean(sg))
            arrx.append([meanx-np.min(sg), meanx, np.max(sg)-meanx])
            
        if not arrx: continue

        lower_img = img[0:arrx[0][1]-arrx[0][0],:]
        upper_img = img[arrx[0][1]+arrx[0][2]:,:]
        
        lw_thresh = segment(lower_img)
        lower_y = lw_thresh.sum(axis=0)
        lw_y_ceil = [k for k in range(len(lower_y)) if lower_y[k] > 0.5*np.max(lower_y)]
        
        uw_thresh = segment(upper_img)
        upper_y = uw_thresh.sum(axis=0)
        uw_y_ceil = [k for k in range(len(upper_y)) if upper_y[k] > 0.5*np.max(upper_y)]
        
        lw_segment = split_on_huge_transitions(lw_y_ceil, absolute_threshold=500)
        uw_segment = split_on_huge_transitions(uw_y_ceil, absolute_threshold=500)
        
        lw_array = []
        for sg in lw_segment:
            if not sg: continue
            mean_lw = int(np.mean(sg))
            lw_array.append([mean_lw-np.min(sg), mean_lw, np.max(sg)-mean_lw])
            
        uw_array = []
        for sg in uw_segment:
            if not sg: continue
            mean_uw = int(np.mean(sg))
            uw_array.append([mean_uw-np.min(sg), mean_uw, np.max(sg)-mean_uw])

        if len(lw_array) >= 2:
            part_images_lw(lower_img, lw_array, output_folder)
        if len(uw_array) >= 2:
            part_images_uw(upper_img, uw_array, output_folder)

def save_if_new(img_array, output_path):
    if os.path.exists(output_path):
        existing_img = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
        if existing_img is not None and existing_img.shape == img_array.shape:
            if np.array_equal(existing_img, img_array):
                return 0, 1 # new=0, duplicate=1
    cv2.imwrite(output_path, img_array)
    return 1, 0 # new=1, duplicate=0

def extract_symbol_templates(input_folder, output_folder_1, output_folder_2):
    cnt = 0
    fn = []; gx = []; g1 = []; g2 = []
    
    new_symbols = 0
    duplicate_symbols = 0
    
    lsize = config.LSIZE
    usize = config.USIZE
    l_size = config.L_SIZE
    u_size = config.U_SIZE
    lvsize = config.LVSIZE
    uvsize = config.UVSIZE
    lv_size = config.LV_SIZE
    uv_size = config.UV_SIZE

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            img_path = os.path.join(input_folder, filename)
            f = filename.split('_')
            fn.append(img_path)
            gx.append(filename)
            if cnt != 10:
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                
                if cnt not in [24, 34]:
                    cropped_1 = img[l_size[cnt]:u_size[cnt], lsize[cnt]:usize[cnt]]
                    cropped_2 = img[:, lvsize[cnt]:uvsize[cnt]]
                else:
                    cropped_1 = img[l_size[cnt]:u_size[cnt], lsize[cnt]:usize[cnt]]
                    cropped_2 = img[lv_size[0]+10:uv_size[0], lvsize[cnt]:uvsize[cnt]]
                
                output_path_1 = os.path.join(output_folder_1, filename)
                n1, d1 = save_if_new(cropped_1, output_path_1)
                
                # Check bounds for description target, handling filenames dynamically
                if len(f) > 2:
                    desc_suffix = f[2]
                else:
                    desc_suffix = "default.png"
                    
                output_path_2 = os.path.join(output_folder_2, 'description_' + desc_suffix)
                n2, d2 = save_if_new(cropped_2, output_path_2)
                
                # Track counts only for files that are not deleted shortly after (indices in split array)
                if cnt not in [35, 36, 37, 1, 10, 11, 23]:
                    new_symbols += (n1 + n2)
                    duplicate_symbols += (d1 + d2)
                
                g1.append(output_path_1)
                g2.append(output_path_2)
        cnt += 1

    split = [35, 36, 37, 1, 10, 11, 23]
    split_path_1 = [g1[i] for i in split if i < len(g1)]
    split_path_2 = [g2[i] for i in split if i < len(g2)]
    
    symb_rz_a = []; symb_rz_b = []; txt_rz = []
    for i in range(len(split_path_1)):
        img_1 = cv2.imread(split_path_1[i], cv2.IMREAD_GRAYSCALE)
        img_2 = cv2.imread(split_path_2[i], cv2.IMREAD_GRAYSCALE)
        if img_1 is None or img_2 is None: continue
        
        h, w = img_1.shape
        if split[i] != 23:
            rsz_1 = img_1[:, :int(w/2)]
            rsz_2 = img_1[:, int(w/2):]
        else:
            rsz_1 = img_1[0:int(h/2)+5, :]
            rsz_2 = img_1[int(h/2)+5:, :w-30]
            rsz_1a = img_2[0:int(img_2.shape[0]/2), :]
            rsz_2a = img_2[int(img_2.shape[0]/2):, :]
            
        symb_rz_a.append(rsz_1)
        symb_rz_b.append(rsz_2)
        
        if split[i] != 23:
            txt_rz.append([img_2]*2)
        else:
            txt_rz.append([rsz_1a, rsz_2a])
            
    txt_rz = [item for sublist in txt_rz for item in sublist]             
    symb_split_a = ['symbol_part_6a.png','symbol_part_7a.png','symbol_part_8a.png','symbol_part_11a.png',
                'symbol_part_20a.png','symbol_part_21a.png','symbol_part_32a.png']
    symb_split_b = ['symbol_part_6b.png','symbol_part_7b.png','symbol_part_8b.png','symbol_part_11b.png',
                'symbol_part_20b.png','symbol_part_21b.png','symbol_part_32b.png']
    desc_split = ['description_6a.png','description_6b.png','description_7a.png','description_7b.png',
                'description_8a.png','description_8b.png','description_11a.png','description_11b.png',
                'description_20a.png','description_20b.png','description_21a.png','description_21b.png',
                'description_32a.png','description_32b.png']
                
    for remv_path in split_path_1: 
        if os.path.exists(remv_path): os.remove(remv_path)
    for remv_path in split_path_2: 
        if os.path.exists(remv_path): os.remove(remv_path)

    for i in range(min(len(symb_split_a), len(symb_rz_a))):
        output_path_a = os.path.join(output_folder_1, symb_split_a[i])
        output_path_b = os.path.join(output_folder_1, symb_split_b[i])
        n, d = save_if_new(symb_rz_a[i], output_path_a)
        new_symbols += n; duplicate_symbols += d
        
        n, d = save_if_new(symb_rz_b[i], output_path_b)
        new_symbols += n; duplicate_symbols += d
        
    for i in range(min(len(desc_split), len(txt_rz))):
        output_path_c = os.path.join(output_folder_2, desc_split[i])
        n, d = save_if_new(txt_rz[i], output_path_c)
        new_symbols += n; duplicate_symbols += d

    print(f"\n================ LIBRARY UPDATE REPORT ================")
    if new_symbols > 0:
        print(f"Update Status: {new_symbols} NEW imagery files found and added to the library!")
    else:
        print(f"Update Status: NO new imagery files found. The library is already up-to-date.")
    print(f"({duplicate_symbols} identical symbol images were verified and skipped natively)")
    print(f"=======================================================\n")

def crop_building_quadrants(img_path, output_dir):
    """Automatically slices the architectural layout into 4 unit quadrants by mapping structural demising walls."""
    if not os.path.exists(img_path): return
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. Strip the blank white asymetrical margins from the pure document page
    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    coords = cv2.findNonZero(binary)
    if coords is None: return
    x, y, w, h = cv2.boundingRect(coords)
    ink_crop = img[y:y+h, x:x+w]
    
    # 2. Re-evaluate purely within the bounding ink box to find demising structural walls
    gray_crop = cv2.cvtColor(ink_crop, cv2.COLOR_BGR2GRAY)
    _, binary_crop = cv2.threshold(gray_crop, 200, 255, cv2.THRESH_BINARY_INV)
    
    row_sums = np.sum(binary_crop == 255, axis=1)
    col_sums = np.sum(binary_crop == 255, axis=0)
    
    # 3. Filter out solid page borders/title blocks (>85% solid ink)
    valid_cols = col_sums.copy()
    valid_cols[valid_cols > h * 0.85] = 0
    valid_rows = row_sums.copy()
    valid_rows[valid_rows > w * 0.85] = 0
    
    # Center structural walls physically exist in the central 30-70% zone of the layout
    mid_h_start, mid_h_end = int(h*0.35), int(h*0.65)
    mid_w_start, mid_w_end = int(w*0.35), int(w*0.65)
    
    # The physical interior demising walls are the longest/thickest lines in this region
    wall_y = mid_h_start + np.argmax(valid_rows[mid_h_start:mid_h_end])
    wall_x = mid_w_start + np.argmax(valid_cols[mid_w_start:mid_w_end])
    
    # 4. Find outermost structural boundaries using a Hybrid Extraction Engine
    # Top and Left walls face open white space filled with floating text (<200 density)
    # We scan inwards and lock onto the FIRST dense structural line (>400 density)
    THRESHOLD = 400
    left_wall_x = next((i for i, val in enumerate(valid_cols[:wall_x-100]) if val > THRESHOLD), 0)
    top_wall_y = next((i for i, val in enumerate(valid_rows[:wall_y-100]) if val > THRESHOLD), 0)
    
    # Right and Bottom walls face adjacent architectural zones (W.I.C hatching) that are connected.
    # We use argmax to locate the singular thickest architectural demising wall in those zones.
    right_half = valid_cols[wall_x+100 : w-50]
    right_wall_x = wall_x + 100 + np.argmax(right_half) if len(right_half) > 0 else w
    
    bottom_half = valid_rows[wall_y+100 : h-50]
    bottom_wall_y = wall_y + 100 + np.argmax(bottom_half) if len(bottom_half) > 0 else h
    
    # 5. Slice precisely down exactly the 3x3 structural boundaries identified
    model_1 = ink_crop[top_wall_y:wall_y, left_wall_x:wall_x]
    model_2 = ink_crop[top_wall_y:wall_y, wall_x:right_wall_x]
    model_3 = ink_crop[wall_y:bottom_wall_y, left_wall_x:wall_x]
    model_4 = ink_crop[wall_y:bottom_wall_y, wall_x:right_wall_x]
    import shutil
    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith('.png'):
                os.remove(os.path.join(output_dir, f))
    
    os.makedirs(output_dir, exist_ok=True)
    cv2.imwrite(os.path.join(output_dir, 'model_top_left.png'), model_1)
    cv2.imwrite(os.path.join(output_dir, 'model_top_right.png'), model_2)
    cv2.imwrite(os.path.join(output_dir, 'model_bottom_left.png'), model_3)
    cv2.imwrite(os.path.join(output_dir, 'model_bottom_right.png'), model_4)
