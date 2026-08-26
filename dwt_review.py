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
