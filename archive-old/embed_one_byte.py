import cv2
import numpy as np
import pywt

INPUT = "frames/frame_001.png"
OUTPUT = "one_byte_embedded.png"

# One test byte: 0xAA = 10101010
SECRET_BYTE = 0xAA

ALPHA = 5.0

# Eight separate mid-frequency coefficients.
# We keep away from the DC / low-frequency region.
POSITIONS = [
    (2, 2),
    (2, 3),
    (2, 4),
    (2, 5),
    (3, 2),
    (3, 3),
    (3, 4),
    (3, 5),
]


def byte_to_bits(value):
    return [(value >> i) & 1 for i in range(7, -1, -1)]


# --------------------------------------------------
# 1. Convert byte to 8 bits
# --------------------------------------------------
secret_bits = byte_to_bits(SECRET_BYTE)

# --------------------------------------------------
# 2. Load frame
# --------------------------------------------------
image = cv2.imread(INPUT, cv2.IMREAD_GRAYSCALE)

if image is None:
    raise FileNotFoundError(f"Could not load {INPUT}")

# --------------------------------------------------
# 3. DWT
# --------------------------------------------------
LL, (LH, HL, HH) = pywt.dwt2(
    image.astype(np.float32),
    "haar"
)

# --------------------------------------------------
# 4. DCT on HH
# --------------------------------------------------
dct_hh = cv2.dct(HH)

# --------------------------------------------------
# 5. Embed 8 bits
# --------------------------------------------------
original_coefficients = []

for bit, (row, col) in zip(secret_bits, POSITIONS):

    original = dct_hh[row, col]
    original_coefficients.append(original)

    magnitude = max(abs(original), ALPHA)

    if bit == 1:
        dct_hh[row, col] = magnitude
    else:
        dct_hh[row, col] = -magnitude

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
# 9. Extract the byte again
# --------------------------------------------------
LL2, (LH2, HL2, HH2) = pywt.dwt2(
    reconstructed.astype(np.float32),
    "haar"
)

dct_hh_extracted = cv2.dct(HH2)

extracted_bits = []

for row, col in POSITIONS:
    coefficient = dct_hh_extracted[row, col]
    extracted_bits.append(1 if coefficient >= 0 else 0)

# Convert 8 bits back to one byte
extracted_byte = 0

for bit in extracted_bits:
    extracted_byte = (extracted_byte << 1) | bit

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

# --------------------------------------------------
# 11. Results
# --------------------------------------------------
print("=== ONE-BYTE EMBEDDING TEST ===")
print("Original image shape:      ", image.shape)
print("DWT HH shape:              ", HH.shape)

print(f"Secret byte:               0x{SECRET_BYTE:02X}")
print(f"Secret bits:               {''.join(map(str, secret_bits))}")

print("\nSelected coefficients:")

for position, bit in zip(POSITIONS, secret_bits):
    print(f"  {position} -> bit {bit}")

print("\nExtracted result:")
print(f"Extracted byte:             0x{extracted_byte:02X}")
print(f"Extracted bits:             {''.join(map(str, extracted_bits))}")

print(f"\nMSE:                        {mse:.6f}")

if np.isinf(psnr):
    print("PSNR:                       Infinite")
else:
    print(f"PSNR:                       {psnr:.6f} dB")

print(f"\nOutput: {OUTPUT}")

if SECRET_BYTE == extracted_byte:
    print("ONE-BYTE EMBEDDING: SUCCESS")
else:
    print("ONE-BYTE EMBEDDING: FAILED")
