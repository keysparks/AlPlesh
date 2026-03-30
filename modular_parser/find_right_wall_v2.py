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

# Connect dotted lines vertically!
kernel_v = np.ones((75, 1), np.uint8)
dilated_v = cv2.dilate(binary_crop, kernel_v, iterations=1)

col_sums = np.sum(dilated_v == 255, axis=0)
row_sums = np.sum(binary_crop == 255, axis=1)

mid_h_start, mid_h_end = int(h*0.35), int(h*0.65)
mid_w_start, mid_w_end = int(w*0.35), int(w*0.65)

wall_y = mid_h_start + np.argmax(row_sums[mid_h_start:mid_h_end])
wall_x = mid_w_start + np.argmax(col_sums[mid_w_start:mid_w_end])

print(f"Center vertical wall at: {wall_x}")

# Find Right Wall
# After wall_x, find the next massive peak. We look roughly where the right wall should be.
# It should be roughly at wall_x + (wall_x * 0.9) to wall_x + (wall_x * 1.1)
right_search_start = int(wall_x * 1.5)
right_search_end = int(wall_x * 2.1)

# Just find the peak in the dilated column sums
right_wall_x = right_search_start + np.argmax(col_sums[right_search_start:right_search_end])
print(f"Right external vertical wall found at: {right_wall_x}")

# Now, does the bottom have garbage?
# The user said model_bottom_left looks perfect. That means no garbage at the bottom.
# But looking at model_bottom_right, there is a massive chunk of white space and notes underneath.
# Model A1 Reverse is lower than B1, but does it go all the way to the bottom?
# Let's find the bottom wall!
bottom_search_start = int(wall_y * 1.5)
bottom_search_end = min(int(wall_y * 2.2), h)

# Connect dotted lines horizontally
kernel_h = np.ones((1, 75), np.uint8)
dilated_h = cv2.dilate(binary_crop, kernel_h, iterations=1)
row_sums_dilated = np.sum(dilated_h == 255, axis=1)

bottom_wall_y = bottom_search_start + np.argmax(row_sums_dilated[bottom_search_start:bottom_search_end])
print(f"Bottom external horizontal wall found at: {bottom_wall_y}")

m1 = ink_crop[:wall_y, :wall_x]
m2 = ink_crop[:wall_y, wall_x:right_wall_x]
m3 = ink_crop[wall_y:bottom_wall_y, :wall_x]
m4 = ink_crop[wall_y:bottom_wall_y, wall_x:right_wall_x]

os.makedirs('isolated_models_v5', exist_ok=True)
cv2.imwrite('isolated_models_v5/model_top_left.png', m1)
cv2.imwrite('isolated_models_v5/model_top_right.png', m2)
cv2.imwrite('isolated_models_v5/model_bottom_left.png', m3)
cv2.imwrite('isolated_models_v5/model_bottom_right.png', m4)
