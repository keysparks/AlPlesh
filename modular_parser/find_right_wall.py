import cv2
import numpy as np
import os

img_path = 'pages_images/image_4.png'
img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

_, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
coords = cv2.findNonZero(binary)
x, y, w, h = cv2.boundingRect(coords)
ink_crop = img[y:y+h, x:x+w]

gray_crop = cv2.cvtColor(ink_crop, cv2.COLOR_BGR2GRAY)
_, binary_crop = cv2.threshold(gray_crop, 200, 255, cv2.THRESH_BINARY_INV)

row_sums = np.sum(binary_crop == 255, axis=1)
col_sums = np.sum(binary_crop == 255, axis=0)

mid_h_start, mid_h_end = int(h*0.35), int(h*0.65)
mid_w_start, mid_w_end = int(w*0.35), int(w*0.65)

wall_y = mid_h_start + np.argmax(row_sums[mid_h_start:mid_h_end])
wall_x = mid_w_start + np.argmax(col_sums[mid_w_start:mid_w_end])

print(f"Center vertical wall at: {wall_x}")

# Find Right Wall (should be located in the right 30% of the image)
# The left units span from 0 -> wall_x. So right units should span roughly wall_x -> wall_x*2
right_search_start = min(int(wall_x * 1.5), w - 50)
right_search_end = min(int(wall_x * 2.2), w)

right_wall_x = right_search_start + np.argmax(col_sums[right_search_start:right_search_end])
print(f"Right external vertical wall found at: {right_wall_x}")

# Find Top Wall (assuming the title block at the bottom extends the drawing down)
# Model B1 and E1 are the top units. Do they have extra garbage at the top? 
# The user said "model_bottom_left.png - Looks perfect. other 2 images are 90% correct."
# Which 2 images? There are 4 images. If bottom left perfectly worked, then Top Left and Top Right also might be mostly perfect except for the right side.
# Let's cleanly crop using the Right Wall only.

m1 = ink_crop[:wall_y, :wall_x]
m2 = ink_crop[:wall_y, wall_x:right_wall_x]  # Strip right garbage
m3 = ink_crop[wall_y:, :wall_x]
m4 = ink_crop[wall_y:, wall_x:right_wall_x]  # Strip right garbage

os.makedirs('isolated_models_v4', exist_ok=True)
cv2.imwrite('isolated_models_v4/model_top_left.png', m1)
cv2.imwrite('isolated_models_v4/model_top_right.png', m2)
cv2.imwrite('isolated_models_v4/model_bottom_left.png', m3)
cv2.imwrite('isolated_models_v4/model_bottom_right.png', m4)
