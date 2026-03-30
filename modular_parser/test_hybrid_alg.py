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

valid_cols = col_sums.copy()
valid_cols[valid_cols > h * 0.85] = 0
valid_rows = row_sums.copy()
valid_rows[valid_rows > w * 0.85] = 0

mid_h_start, mid_h_end = int(h*0.35), int(h*0.65)
mid_w_start, mid_w_end = int(w*0.35), int(w*0.65)

wall_y = mid_h_start + np.argmax(valid_rows[mid_h_start:mid_h_end])
wall_x = mid_w_start + np.argmax(valid_cols[mid_w_start:mid_w_end])

THRESHOLD = 400

# Top/Left: Stop at the first line coming from white space that is structural (>400)
left_wall_x = next((i for i, val in enumerate(valid_cols[:wall_x-100]) if val > THRESHOLD), 0)
top_wall_y = next((i for i, val in enumerate(valid_rows[:wall_y-100]) if val > THRESHOLD), 0)

# Right/Bottom: Use absolute max density (argmax) to find demising structural walls to strip connected hatched zones
right_half = valid_cols[wall_x+100 : w-50]
right_wall_x = wall_x + 100 + np.argmax(right_half) if len(right_half) > 0 else w

bottom_half = valid_rows[wall_y+100 : h-50]
bottom_wall_y = wall_y + 100 + np.argmax(bottom_half) if len(bottom_half) > 0 else h

print(f"Top: {top_wall_y}, Bottom: {bottom_wall_y}")
print(f"Left: {left_wall_x}, Right: {right_wall_x}")
print(f"Center Y: {wall_y}, Center X: {wall_x}")

model_1 = ink_crop[top_wall_y:wall_y, left_wall_x:wall_x]
model_2 = ink_crop[top_wall_y:wall_y, wall_x:right_wall_x]
model_3 = ink_crop[wall_y:bottom_wall_y, left_wall_x:wall_x]
model_4 = ink_crop[wall_y:bottom_wall_y, wall_x:right_wall_x]

os.makedirs('isolated_models_v8', exist_ok=True)
cv2.imwrite('isolated_models_v8/model_top_left.png', model_1)
cv2.imwrite('isolated_models_v8/model_top_right.png', model_2)
cv2.imwrite('isolated_models_v8/model_bottom_left.png', model_3)
cv2.imwrite('isolated_models_v8/model_bottom_right.png', model_4)
