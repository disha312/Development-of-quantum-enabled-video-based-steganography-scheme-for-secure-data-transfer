import cv2
import numpy as np
import pywt

INPUT = "frames/frame_001.png"
OUTPUT = "one_bit_embedded.png"

# The single secret bit for today's experiment.
SECRET_BIT = 1

# Small modification strength.
ALPHA = 5.0

# --------------------------------------------------
# 1. Load frame
# --------------------------------------------------
image = cv2.imread(INPUT, cv2.IMREAD_GRAYSCALE)

if image is None:
    raise FileNotFoundError(f"Could not load {INPUT}")

# --------------------------------------------------
# 2. DWT
# --------------------------------------------------
LL, (LH, HL, HH) = pywt.dwt2(
    image.astype(np.float32),
    "haar"
)

# --------------------------------------------------
# 3. DCT on HH sub-band
# --------------------------------------------------
dct_hh = cv2.dct(HH)

# --------------------------------------------------
# 4. Select ONE mid-frequency coefficient
# --------------------------------------------------
ROW = 2
COL = 2

original_coefficient = dct_hh[ROW, COL]

# --------------------------------------------------
# 5. Embed ONE bit
#
# We use the coefficient sign:
#
# bit 1 -> positive coefficient
# bit 0 -> negative coefficient
#
# The magnitude is kept at least ALPHA.
# --------------------------------------------------
if SECRET_BIT == 1:
    dct_hh[ROW, COL] = max(abs(original_coefficient), ALPHA)
else:
    dct_hh[ROW, COL] = -max(abs(original_coefficient), ALPHA)

modified_coefficient = dct_hh[ROW, COL]

# --------------------------------------------------
# 6. Inverse DCT
# --------------------------------------------------
modified_HH = cv2.idct(dct_hh)

# --------------------------------------------------
# 7. Inverse DWT
# --------------------------------------------------
reconstructed = pywt.idwt2(
    (LL, (LH, HL, modified_HH)),
    "haar"
)

# --------------------------------------------------
# 8. Convert and save
# --------------------------------------------------
reconstructed = np.clip(reconstructed, 0, 255).astype(np.uint8)

cv2.imwrite(OUTPUT, reconstructed)

# --------------------------------------------------
# 9. Verify the embedded bit
# --------------------------------------------------
extracted_coefficient = cv2.dct(
    pywt.dwt2(
        reconstructed.astype(np.float32),
        "haar"
    )[1][2]
)[ROW, COL]

extracted_bit = 1 if extracted_coefficient >= 0 else 0

# --------------------------------------------------
# 10. Quality measurement
# --------------------------------------------------
difference = (
    image.astype(np.float64)
    - reconstructed.astype(np.float64)
)

mse = np.mean(difference ** 2)

if mse == 0:
    psnr = float("inf")
else:
    psnr = 10 * np.log10((255 ** 2) / mse)

print("=== ONE-BIT EMBEDDING TEST ===")
print("Original image shape:      ", image.shape)
print("DWT HH shape:              ", HH.shape)
print(f"Selected coefficient:      ({ROW}, {COL})")
print(f"Original coefficient:      {original_coefficient:.6f}")
print(f"Modified coefficient:      {modified_coefficient:.6f}")
print(f"Secret bit:                {SECRET_BIT}")
print(f"Extracted bit:             {extracted_bit}")
print(f"MSE:                       {mse:.6f}")

if np.isinf(psnr):
    print("PSNR:                      Infinite")
else:
    print(f"PSNR:                      {psnr:.6f} dB")

print(f"\nOne-bit embedding output: {OUTPUT}")

if SECRET_BIT == extracted_bit:
    print("ONE-BIT EMBEDDING: SUCCESS")
else:
    print("ONE-BIT EMBEDDING: FAILED")
