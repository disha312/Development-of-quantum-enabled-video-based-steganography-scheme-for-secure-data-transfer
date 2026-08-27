
import cv2
import numpy as np

# Load original and reconstructed images
original = cv2.imread("frames/frame_001.png", cv2.IMREAD_GRAYSCALE)
reconstructed = cv2.imread("reconstructed_frame.png", cv2.IMREAD_GRAYSCALE)

if original is None:
    raise FileNotFoundError("Could not load frames/frame_001.png")

if reconstructed is None:
    raise FileNotFoundError("Could not load reconstructed_frame.png")

# Convert to floating point for accurate calculations
original_float = original.astype(np.float64)
reconstructed_float = reconstructed.astype(np.float64)

# Calculate Mean Squared Error (MSE)
mse = np.mean((original_float - reconstructed_float) ** 2)

# Calculate PSNR
if mse == 0:
    psnr = float("inf")
else:
    psnr = 10 * np.log10((255 ** 2) / mse)

print("Original image shape:", original.shape)
print("Reconstructed image shape:", reconstructed.shape)
print(f"MSE: {mse:.6f}")
print(f"PSNR: {psnr:.6f} dB")
