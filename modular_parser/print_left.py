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

print(f"Total height: {h}")

print("Scanning from Left (0 to 600)...")
for i in range(0, 600):
    if valid_cols[i] > 250:
        print(f"First significant vertical wall found at Left X={i} (Density={valid_cols[i]})")
        break

row_sums = np.sum(binary_crop == 255, axis=1)
valid_rows = row_sums.copy()
valid_rows[valid_rows > w * 0.85] = 0

print("Scanning from Top (0 to 600)...")
for i in range(0, 600):
    if valid_rows[i] > 250:
        print(f"First significant horizontal wall found at Top Y={i} (Density={valid_rows[i]})")
        break
