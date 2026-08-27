import cv2
import pywt
import numpy as np

# Load frame.png as a grayscale im
image = cv2.imread("frames/frame_001.png", cv2.IMREAD_GRAYSCALE)

if image is None:
    raise FileNotFoundError("Could not load frames/frame_001.png")

# Apply 2D Haar DWT
LL, (LH, HL, HH) = pywt.dwt2(image, "haar")

# Normalize sub-bands so they can be saved as images
def normalize_band(band):
    band = np.abs(band)
    return cv2.normalize(band, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

# Convert each sub-band to viewable image format
LL_img = normalize_band(LL)
LH_img = normalize_band(LH)
HL_img = normalize_band(HL)
HH_img = normalize_band(HH)

# Save the resulting sub-bands
cv2.imwrite("LL.png", LL_img)
cv2.imwrite("LH.png", LH_img)
cv2.imwrite("HL.png", HL_img)
cv2.imwrite("HH.png", HH_img)

print("Original image shape:", image.shape)
print("LL shape:", LL.shape)
print("LH shape:", LH.shape)
print("HL shape:", HL.shape)
print("HH shape:", HH.shape)

print("\nDWT completed successfully.")
print("Sub-band images saved: LL.png, LH.png, HL.png, HH.png")
