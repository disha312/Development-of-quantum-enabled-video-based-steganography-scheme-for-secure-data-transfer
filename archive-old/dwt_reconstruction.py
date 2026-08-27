import cv2
import pywt
import numpy as np

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
