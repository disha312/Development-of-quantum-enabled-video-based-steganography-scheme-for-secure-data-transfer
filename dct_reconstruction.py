import cv2
import numpy as np

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
