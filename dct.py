

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

#DCT Reconstruction Section
INPUT = "frames/frame_001.png"
OUTPUT = "dct_reconstructed.png"

# 1. Load the original image
image = cv2.imread(INPUT, cv2.IMREAD_GRAYSCALE)

if image is None:
    raise FileNotFoundError(f"Could not load {INPUT}")

# 2. Convert to float32 for DCT
image_float = np.float32(image)

# 3. Apply DCT
dct_coefficients = cv2.dct(image_float)

# 4. Apply Inverse DCT
reconstructed = cv2.idct(dct_coefficients)

# 5. Convert reconstructed image back to 8-bit
reconstructed = np.clip(reconstructed, 0, 255).astype(np.uint8)

# 6. Save reconstructed image
cv2.imwrite(OUTPUT, reconstructed)

# 7. Calculate reconstruction difference
difference = (
    image.astype(np.float64)
    - reconstructed.astype(np.float64)
)

mse = np.mean(difference ** 2)

if mse == 0:
    psnr = float("inf")
else:
    psnr = 10 * np.log10((255 ** 2) / mse)

# 8. Display results
print("=== DCT RECONSTRUCTION ===")
print("Original image shape:      ", image.shape)
print("DCT coefficient shape:    ", dct_coefficients.shape)
print("Reconstructed image shape: ", reconstructed.shape)
print(f"MSE:                       {mse:.6f}")

if np.isinf(psnr):
    print("PSNR:                      Infinite")
else:
    print(f"PSNR:                      {psnr:.6f} dB")

print("\nDCT transformation: SUCCESS")
print("Inverse DCT:         SUCCESS")
print(f"Reconstructed image saved as: {OUTPUT}")

#DCT Quality Test Section


ORIGINAL = "frames/frame_001.png"
RECONSTRUCTED = "dct_reconstructed.png"

# Load both images
original = cv2.imread(ORIGINAL, cv2.IMREAD_GRAYSCALE)
reconstructed = cv2.imread(RECONSTRUCTED, cv2.IMREAD_GRAYSCALE)

if original is None:
    raise FileNotFoundError(f"Could not load {ORIGINAL}")

if reconstructed is None:
    raise FileNotFoundError(f"Could not load {RECONSTRUCTED}")

# Make sure dimensions match
if original.shape != reconstructed.shape:
    raise ValueError(
        f"Image dimensions do not match: "
        f"{original.shape} vs {reconstructed.shape}"
    )

# Calculate MSE
difference = (
    original.astype(np.float64)
    - reconstructed.astype(np.float64)
)

mse = np.mean(difference ** 2)

# Calculate PSNR
if mse == 0:
    psnr = float("inf")
else:
    psnr = 10 * np.log10((255 ** 2) / mse)

print("=== DCT QUALITY TEST ===")
print("Original image shape:      ", original.shape)
print("Reconstructed image shape: ", reconstructed.shape)
print(f"MSE:                       {mse:.6f}")

if np.isinf(psnr):
    print("PSNR:                      Infinite")
else:
    print(f"PSNR:                      {psnr:.6f} dB")

print("\nDCT reconstruction quality test completed successfully.")