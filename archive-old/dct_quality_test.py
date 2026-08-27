
import cv2
import numpy as np

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