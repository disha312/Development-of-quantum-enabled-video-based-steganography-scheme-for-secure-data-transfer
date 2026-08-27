
#DWT Transformation and reconstruction section

import cv2
import pywt
import numpy as np

INPUT = "frames/frame_001.png"
OUTPUT = "dwt_review_reconstructed.png"

# 1. Load frame
image = cv2.imread(INPUT, cv2.IMREAD_GRAYSCALE)

if image is None:
    raise FileNotFoundError(f"Could not load {INPUT}")

# 2. Apply DWT
LL, (LH, HL, HH) = pywt.dwt2(image, "haar")

# 3. Inverse DWT
reconstructed = pywt.idwt2((LL, (LH, HL, HH)), "haar")

# 4. Convert reconstructed image for saving
reconstructed = np.clip(reconstructed, 0, 255).astype(np.uint8)

# 5. Save reconstructed frame
cv2.imwrite(OUTPUT, reconstructed)

# 6. Measure difference
difference = np.abs(
    image.astype(np.float64) - reconstructed.astype(np.float64)
)

mse = np.mean(difference ** 2)

if mse == 0:
    psnr = float("inf")
else:
    psnr = 10 * np.log10((255 ** 2) / mse)

# 7. Display review results
print("=== DWT REVIEW ===")
print("Original shape:      ", image.shape)
print("LL shape:            ", LL.shape)
print("LH shape:            ", LH.shape)
print("HL shape:            ", HL.shape)
print("HH shape:            ", HH.shape)
print("Reconstructed shape: ", reconstructed.shape)
print(f"MSE:                 {mse:.6f}")
print(f"PSNR:                {psnr:.6f} dB")
print("\nDWT transformation: SUCCESS")
print("Inverse DWT:         SUCCESS")
print(f"Reconstructed image saved as: {OUTPUT}")

#DWT Reconstruction section


# Load the original image
image = cv2.imread("frames/frame_001.png", cv2.IMREAD_GRAYSCALE)

if image is None:
    raise FileNotFoundError("Could not load frames/frame_001.png")

# DWT: decompose the image
LL, (LH, HL, HH) = pywt.dwt2(image, "haar")

# Inverse DWT: reconstruct the image
reconstructed = pywt.idwt2((LL, (LH, HL, HH)), "haar")

# Convert back to uint8 for saving
reconstructed = np.clip(reconstructed, 0, 255).astype(np.uint8)

# Save reconstructed image
cv2.imwrite("reconstructed_frame.png", reconstructed)

# Calculate reconstruction error
difference = np.abs(image.astype(np.float64) - reconstructed.astype(np.float64))

print("Original image shape:", image.shape)
print("Reconstructed image shape:", reconstructed.shape)
print("Maximum pixel difference:", difference.max())
print("Mean pixel difference:", difference.mean())

print("\nDWT → Inverse DWT reconstruction completed.")
print("Saved as: reconstructed_frame.png")

#DWT Visualization section
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
