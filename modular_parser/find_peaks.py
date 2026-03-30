import cv2
import numpy as np
from scipy.signal import find_peaks

img_path = 'pages_images/image_4.png'
img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Bounding box of ink
_, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
coords = cv2.findNonZero(binary)
x, y, w, h = cv2.boundingRect(coords)
ink_crop = img[y:y+h, x:x+w]

gray_crop = cv2.cvtColor(ink_crop, cv2.COLOR_BGR2GRAY)
_, binary_crop = cv2.threshold(gray_crop, 200, 255, cv2.THRESH_BINARY_INV)

row_sums = np.sum(binary_crop == 255, axis=1)
col_sums = np.sum(binary_crop == 255, axis=0)

# We want to find the top 3 peaks (Left, Center, Right wall)
# Minimum distance of 500 pixels between major structural walls
col_peaks, _ = find_peaks(col_sums, distance=500, height=np.max(col_sums)*0.3)
row_peaks, _ = find_peaks(row_sums, distance=500, height=np.max(row_sums)*0.3)

# Sort peaks by prominence/height (keep the top 3 if there are more)
col_peaks = sorted(col_peaks, key=lambda p: col_sums[p], reverse=True)[:3]
row_peaks = sorted(row_peaks, key=lambda p: row_sums[p], reverse=True)[:3]

# Sort them spatially
col_peaks = sorted(col_peaks)
row_peaks = sorted(row_peaks)

print(f"Vertical structural walls found at X: {col_peaks}")
print(f"Horizontal structural walls found at Y: {row_peaks}")

# If we found 3 walls in both directions, we can explicitly bounds the 4 units
if len(col_peaks) >= 3 and len(row_peaks) >= 3:
    print("Found true 3x3 structural boundaries!")
else:
    print("Could not cleanly detect outer walls.")
