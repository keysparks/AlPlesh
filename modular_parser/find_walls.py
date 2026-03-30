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

print(f"Blueprint dimensions: {w}x{h}")
print(f"Center bisect would be: X={w//2}, Y={h//2}")
print(f"Found physical structural walls at: X={wall_x}, Y={wall_y}")

m1 = ink_crop[:wall_y, :wall_x]
m2 = ink_crop[:wall_y, wall_x:]
m3 = ink_crop[wall_y:, :wall_x]
m4 = ink_crop[wall_y:, wall_x:]

os.makedirs('isolated_models_v3', exist_ok=True)
cv2.imwrite('isolated_models_v3/model_top_left.png', m1)
cv2.imwrite('isolated_models_v3/model_top_right.png', m2)
cv2.imwrite('isolated_models_v3/model_bottom_left.png', m3)
cv2.imwrite('isolated_models_v3/model_bottom_right.png', m4)
