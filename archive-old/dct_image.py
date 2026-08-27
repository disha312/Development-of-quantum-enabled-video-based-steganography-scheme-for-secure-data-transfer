
import cv2
import numpy as np

# Load frame as grayscale
image = cv2.imread("frames/frame_001.png", cv2.IMREAD_GRAYSCALE)

if image is None:
    raise FileNotFoundError("Could not load frames/frame_001.png")

# Convert image to float32 for DCT
image_float = np.float32(image)

# Apply 2D DCT
dct_coefficients = cv2.dct(image_float)

print("Original image shape:", image.shape)
print("DCT coefficient shape:", dct_coefficients.shape)

# Display some low-frequency coefficients
print("\nTop-left 5x5 DCT coefficients:")
print(dct_coefficients[:5, :5])

# Create a visual representation of DCT coefficients
dct_visual = np.log(np.abs(dct_coefficients) + 1)

dct_visual = cv2.normalize(
    dct_visual,
    None,
    0,
    255,
    cv2.NORM_MINMAX
).astype(np.uint8)

# Save DCT visualization
cv2.imwrite("dct_coefficients.png", dct_visual)

print("\nDCT completed successfully.")
print("DCT coefficient visualization saved as: dct_coefficients.png")