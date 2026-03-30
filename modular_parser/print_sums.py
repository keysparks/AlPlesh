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
row_sums = np.sum(binary_crop == 255, axis=1)

mid_w_start, mid_w_end = int(w*0.35), int(w*0.65)
wall_x = mid_w_start + np.argmax(col_sums[mid_w_start:mid_w_end])

right_half = col_sums[wall_x+500:w-150] 
top_indices = np.argsort(right_half)[-20:] 
top_indices = top_indices + wall_x + 500

print(f"Center Wall X: {wall_x}")
print(f"Image Width: {w}")
for idx in sorted(top_indices):
    print(f"X: {idx}, Density: {col_sums[idx]}")
