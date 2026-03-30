import cv2
import numpy as np
import os

img_path = 'pages_images/image_4.png'
if not os.path.exists(img_path):
    print("Error: Could not find image_4.png")
    exit()

img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

coords = cv2.findNonZero(binary)
if coords is not None:
    x, y, w, h = cv2.boundingRect(coords)
    # The blueprint title block is often far right or bottom. Let's crop to ink.
    ink_crop = img[y:y+h, x:x+w]
    
    half_h, half_w = h // 2, w // 2
    
    m1 = ink_crop[:half_h, :half_w]
    m2 = ink_crop[:half_h, half_w:]
    m3 = ink_crop[half_h:, :half_w]
    m4 = ink_crop[half_h:, half_w:]
    
    os.makedirs('isolated_models', exist_ok=True)
    cv2.imwrite('isolated_models/model_top_left.png', m1)
    cv2.imwrite('isolated_models/model_top_right.png', m2)
    cv2.imwrite('isolated_models/model_bottom_left.png', m3)
    cv2.imwrite('isolated_models/model_bottom_right.png', m4)
    print("SUCCESS")
else:
    print("No ink found")
