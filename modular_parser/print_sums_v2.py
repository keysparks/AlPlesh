import cv2
import numpy as np

img = cv2.imread('pages_images/image_4.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
coords = cv2.findNonZero(binary)
x, y, w, h = cv2.boundingRect(coords)
ink_crop = img[y:y+h, x:x+w]

gray_crop = cv2.cvtColor(ink_crop, cv2.COLOR_BGR2GRAY)
_, binary_crop = cv2.threshold(gray_crop, 200, 255, cv2.THRESH_BINARY_INV)

col_sums = np.sum(binary_crop == 255, axis=0)

valid_cols = col_sums.copy()
valid_cols[valid_cols > h * 0.85] = 0

mid_w_start, mid_w_end = int(w*0.35), int(w*0.65)
wall_x = mid_w_start + np.argmax(valid_cols[mid_w_start:mid_w_end])

right_half = valid_cols[wall_x+500:w-50]
right_wall_x = wall_x + 500 + np.argmax(right_half)

print(f"Center Wall: {wall_x}")
print(f"Right Wall: {right_wall_x} (Density: {valid_cols[right_wall_x]})")
