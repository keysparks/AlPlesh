import cv2
import numpy as np
import os

img_path = 'pages_images/image_4.png'
if not os.path.exists(img_path):
    print("Error: Could not find image_4.png")
    exit()

img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

row_sums = np.sum(binary == 255, axis=1)
col_sums = np.sum(binary == 255, axis=0)

h, w = binary.shape
mid_h_start, mid_h_end = int(h*0.15), int(h*0.85)
mid_w_start, mid_w_end = int(w*0.15), int(w*0.85)

best_row = mid_h_start + np.argmax(row_sums[mid_h_start:mid_h_end])
best_col = mid_w_start + np.argmax(col_sums[mid_w_start:mid_w_end])

print(f"Splitting at Y={best_row}, X={best_col}")

model_1 = img[:best_row, :best_col]
model_2 = img[:best_row, best_col:]
model_3 = img[best_row:, :best_col]
model_4 = img[best_row:, best_col:]

os.makedirs('isolated_models', exist_ok=True)
cv2.imwrite('isolated_models/model_1_top_left.png', model_1)
cv2.imwrite('isolated_models/model_2_top_right.png', model_2)
cv2.imwrite('isolated_models/model_3_bottom_left.png', model_3)
cv2.imwrite('isolated_models/model_4_bottom_right.png', model_4)

print("Successfully exported 4 isolated models to /isolated_models/")
