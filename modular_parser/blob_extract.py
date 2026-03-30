import cv2
import numpy as np
import os

img_path = 'pages_images/image_4.png'
if not os.path.exists(img_path):
    print("No image")
    exit()

img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

# Dilate aggressively to merge the entire building structure into a single contiguous blob
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
dilated = cv2.dilate(binary, kernel, iterations=3)

# Find all contours
contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Find the absolute largest contour by area (this is mathematically the central apartment block)
largest_contour = max(contours, key=cv2.contourArea)

# Extract its bounding box
x, y, w, h = cv2.boundingRect(largest_contour)
print(f"Largest architectural blob bounded at: {x}, {y}, {w}, {h}")

building_crop = img[y:y+h, x:x+w]

# Now inside the perfect building crop, we can just do the 50% bisect safely!
# Wait, because we stripped all symmetric margins, the building is now tightly bounded.
# Let's see if 50% bisect works natively when perfectly bounded!
mid_y, mid_x = h // 2, w // 2

# Actually, the user's manual snips weren't 50/50 exactly. The internal demising walls were at known coords.
# Let's find the internal demising walls natively inside the building crop
gray_crop = cv2.cvtColor(building_crop, cv2.COLOR_BGR2GRAY)
_, binary_crop = cv2.threshold(gray_crop, 200, 255, cv2.THRESH_BINARY_INV)

row_sums = np.sum(binary_crop == 255, axis=1)
col_sums = np.sum(binary_crop == 255, axis=0)

wall_y = int(h*0.3) + np.argmax(row_sums[int(h*0.3):int(h*0.7)])
wall_x = int(w*0.3) + np.argmax(col_sums[int(w*0.3):int(w*0.7)])

m1 = building_crop[:wall_y, :wall_x]
m2 = building_crop[:wall_y, wall_x:]
m3 = building_crop[wall_y:, :wall_x]
m4 = building_crop[wall_y:, wall_x:]

os.makedirs('isolated_models_v7', exist_ok=True)
cv2.imwrite('isolated_models_v7/model_top_left.png', m1)
cv2.imwrite('isolated_models_v7/model_top_right.png', m2)
cv2.imwrite('isolated_models_v7/model_bottom_left.png', m3)
cv2.imwrite('isolated_models_v7/model_bottom_right.png', m4)
