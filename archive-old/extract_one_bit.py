import cv2
import numpy as np
import pywt

INPUT = "one_bit_embedded.png"

# Must match the embedding experiment
ROW = 2
COL = 2

# --------------------------------------------------
# 1. Load modified frame
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
# 4. Read the selected coefficient
# --------------------------------------------------
coefficient = dct_hh[ROW, COL]

# --------------------------------------------------
# 5. Extract the bit
#
# Positive coefficient -> 1
# Negative coefficient -> 0
# --------------------------------------------------
extracted_bit = 1 if coefficient >= 0 else 0

# --------------------------------------------------
# 6. Display result
# --------------------------------------------------
print("=== ONE-BIT EXTRACTION TEST ===")
print("Modified image shape:      ", image.shape)
print("DWT HH shape:              ", HH.shape)
print(f"Selected coefficient:      ({ROW}, {COL})")
print(f"Coefficient value:         {coefficient:.6f}")
print(f"Extracted bit:             {extracted_bit}")

# Day 31 target
original_bit = 1

print(f"Original bit:              {original_bit}")
print(f"Extracted bit:             {extracted_bit}")

if original_bit == extracted_bit:
    print("\nONE-BIT EXTRACTION: SUCCESS")
else:
    print("\nONE-BIT EXTRACTION: FAILED")
