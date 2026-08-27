
# ============================================================
# DAY 1 — ONE-BYTE DWT + DCT STEGANOGRAPHY
# ============================================================
#
# Goal:
#     0xAA → 10101010 → EMBED → EXTRACT → 10101010 → 0xAA
#
# Embedding pipeline:
#
#     Image
#       ↓
#      DWT
#       ↓
#      HH sub-band
#       ↓
#      DCT
#       ↓
#   Pair-based embedding
#       ↓
#   Inverse DCT
#       ↓
#   Inverse DWT
#       ↓
#   Stego image
#
# Extraction:
#
#     Stego image
#       ↓
#      DWT
#       ↓
#      HH
#       ↓
#      DCT
#       ↓
#   Compare coefficient pairs
#       ↓
#      8 bits
#       ↓
#      byte
#
# Each secret bit is represented by TWO coefficients.
#
#     bit 1 → coefficient A is greater than B
#     bit 0 → coefficient B is greater than A
#
# ============================================================

import cv2
import numpy as np
import pywt


# ------------------------------------------------------------
# 1. File configuration
# ------------------------------------------------------------

INPUT = "frames/frame_001.png"
OUTPUT = "output/one_byte_embedded.png"


# ------------------------------------------------------------
# 2. Secret byte
# ------------------------------------------------------------

# 0xAA = 10101010
SECRET_BYTE = 0xAA


# ------------------------------------------------------------
# 3. Embedding strength
# ------------------------------------------------------------

# This is the minimum difference we try to maintain
# between the two coefficients in each pair.
#
# A larger value gives a stronger signal but can introduce
# more visible distortion.
MARGIN = 50.0


# ------------------------------------------------------------
# 4. Eight coefficient pairs
# ------------------------------------------------------------
#
# Each pair stores ONE bit.
#
# Pair 1 → Bit 1
# Pair 2 → Bit 2
# ...
# Pair 8 → Bit 8
#
# The positions are chosen from the mid-frequency area of
# the DCT rather than the DC coefficient.

COEFFICIENT_PAIRS = [
    ((2, 2), (2, 3)),
    ((2, 4), (2, 5)),
    ((3, 2), (3, 3)),
    ((3, 4), (3, 5)),
    ((4, 2), (4, 3)),
    ((4, 4), (4, 5)),
    ((5, 2), (5, 3)),
    ((5, 4), (5, 5)),
]


# ------------------------------------------------------------
# 5. Convert byte to binary
# ------------------------------------------------------------

bits = [
    (SECRET_BYTE >> position) & 1
    for position in range(7, -1, -1)
]

print("=== DAY 1: ONE-BYTE PAIR EMBEDDING TEST ===")
print(f"Secret byte: 0x{SECRET_BYTE:02X}")
print("Secret bits:", "".join(map(str, bits)))


# ------------------------------------------------------------
# 6. Load original frame
# ------------------------------------------------------------

image = cv2.imread(
    INPUT,
    cv2.IMREAD_GRAYSCALE
)

if image is None:
    raise FileNotFoundError(
        f"Could not load {INPUT}"
    )


# ------------------------------------------------------------
# 7. Apply DWT
# ------------------------------------------------------------

LL, (LH, HL, HH) = pywt.dwt2(
    image.astype(np.float32),
    "haar"
)


# ------------------------------------------------------------
# 8. Apply DCT to HH
# ------------------------------------------------------------

dct_hh = cv2.dct(HH)


# ------------------------------------------------------------
# 9. Embed the eight bits
# ------------------------------------------------------------

print("\n--- EMBEDDING ---")

for index, (bit, pair) in enumerate(
    zip(bits, COEFFICIENT_PAIRS),
    start=1
):

    (row_a, col_a), (row_b, col_b) = pair

    # Read both coefficients.
    a = dct_hh[row_a, col_a]
    b = dct_hh[row_b, col_b]

    # Use their average as the centre point.
    centre = (a + b) / 2.0

    # For bit 1:
    #
    #     A = centre + margin/2
    #     B = centre - margin/2
    #
    # Therefore:
    #
    #     A > B
    #
    # For bit 0 we reverse them:
    #
    #     B > A

    if bit == 1:

        dct_hh[row_a, col_a] = (
            centre + MARGIN / 2
        )

        dct_hh[row_b, col_b] = (
            centre - MARGIN / 2
        )

    else:

        dct_hh[row_a, col_a] = (
            centre - MARGIN / 2
        )

        dct_hh[row_b, col_b] = (
            centre + MARGIN / 2
        )

    print(
        f"Bit {index}: {bit} | "
        f"A({row_a},{col_a}) = "
        f"{dct_hh[row_a, col_a]:.4f} | "
        f"B({row_b},{col_b}) = "
        f"{dct_hh[row_b, col_b]:.4f}"
    )


# ------------------------------------------------------------
# 10. Inverse DCT
# ------------------------------------------------------------

modified_HH = cv2.idct(dct_hh)


# ------------------------------------------------------------
# 11. Inverse DWT
# ------------------------------------------------------------

reconstructed = pywt.idwt2(
    (LL, (LH, HL, modified_HH)),
    "haar"
)


# ------------------------------------------------------------
# 12. Convert to an 8-bit image
# ------------------------------------------------------------

reconstructed = np.clip(
    reconstructed,
    0,
    255
).astype(np.uint8)


# ------------------------------------------------------------
# 13. Save stego image
# ------------------------------------------------------------

if not cv2.imwrite(OUTPUT, reconstructed):
    raise IOError(
        f"Could not save {OUTPUT}"
    )

print(f"\nEmbedded image saved to: {OUTPUT}")


# ============================================================
# EXTRACTION
# ============================================================


# ------------------------------------------------------------
# 14. Load stego image
# ------------------------------------------------------------

embedded_image = cv2.imread(
    OUTPUT,
    cv2.IMREAD_GRAYSCALE
)

if embedded_image is None:
    raise FileNotFoundError(
        f"Could not load {OUTPUT}"
    )


# ------------------------------------------------------------
# 15. Apply DWT to stego image
# ------------------------------------------------------------

_, (_, _, extracted_HH) = pywt.dwt2(
    embedded_image.astype(np.float32),
    "haar"
)


# ------------------------------------------------------------
# 16. Apply DCT to extracted HH
# ------------------------------------------------------------

extracted_dct_hh = cv2.dct(
    extracted_HH
)


# ------------------------------------------------------------
# 17. Extract eight bits
# ------------------------------------------------------------

extracted_bits = []

print("\n--- EXTRACTION ---")

for index, pair in enumerate(
    COEFFICIENT_PAIRS,
    start=1
):

    (row_a, col_a), (row_b, col_b) = pair

    # Read both coefficients after the complete
    # DWT → DCT → image reconstruction → DWT → DCT
    # round trip.
    a = extracted_dct_hh[row_a, col_a]
    b = extracted_dct_hh[row_b, col_b]

    # Compare the two coefficients.
    #
    # A > B → 1
    # A < B → 0

    extracted_bit = 1 if a > b else 0

    extracted_bits.append(extracted_bit)

    print(
        f"Bit {index}: {extracted_bit} | "
        f"A = {a:.4f} | "
        f"B = {b:.4f} | "
        f"A-B = {a - b:.4f}"
    )


# ------------------------------------------------------------
# 18. Convert extracted bits to byte
# ------------------------------------------------------------

extracted_byte = 0

for bit in extracted_bits:

    extracted_byte = (
        (extracted_byte << 1) | bit
    )


# ------------------------------------------------------------
# 19. Display result
# ------------------------------------------------------------

original_bits = "".join(
    map(str, bits)
)

extracted_bits_string = "".join(
    map(str, extracted_bits)
)

print("\n=== FINAL RESULT ===")

print(
    f"Original byte:  0x{SECRET_BYTE:02X}"
)

print(
    f"Original bits:  {original_bits}"
)

print(
    f"Extracted byte: 0x{extracted_byte:02X}"
)

print(
    f"Extracted bits: {extracted_bits_string}"
)


# ------------------------------------------------------------
# 20. Verify all eight bits
# ------------------------------------------------------------

if extracted_bits == bits:

    print("\nALL 8 BITS MATCH: SUCCESS")
    print("ONE-BYTE EMBEDDING: SUCCESS")

else:

    print("\nALL 8 BITS MATCH: FAILED")
    print("ONE-BYTE EMBEDDING: FAILED")

    print("\nBit-by-bit comparison:")

    for index, (expected, actual) in enumerate(
        zip(bits, extracted_bits),
        start=1
    ):

        status = "OK" if expected == actual else "FAIL"

        print(
            f"Bit {index}: "
            f"expected={expected}, "
            f"extracted={actual} → {status}"
        )