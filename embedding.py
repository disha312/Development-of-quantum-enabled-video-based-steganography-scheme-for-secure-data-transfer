
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

        # ============================================================
# DAY 2 — SMALL TEXT TEST
# ============================================================
#
# Goal:
#     HELLO
#       ↓
#     40 binary bits
#       ↓
#     DWT + DCT embedding
#       ↓
#     extraction
#       ↓
#     HELLO
#
# This section extends the successful Day 1 pair-based
# embedding method from 8 bits to 40 bits.
# ============================================================


# ------------------------------------------------------------
# 1. Secret text
# ------------------------------------------------------------

SECRET_TEXT = "HELLO"


# ------------------------------------------------------------
# 2. Convert text to binary
# ------------------------------------------------------------
#
# Each character uses 8 bits.
#
# HELLO contains 5 characters:
#
#     5 × 8 = 40 bits
#
# Example:
#
#     H → 01001000

payload_bits = []

for character in SECRET_TEXT:

    character_bits = [
        int(bit)
        for bit in f"{ord(character):08b}"
    ]

    payload_bits.extend(character_bits)


print("\n\n=== DAY 2: SMALL TEXT TEST ===")

print(f"Secret text: {SECRET_TEXT}")

print(
    "Secret binary:",
    " ".join(
        f"{ord(character):08b}"
        for character in SECRET_TEXT
    )
)

print(f"Total bits: {len(payload_bits)}")


# ------------------------------------------------------------
# 3. Create 40 coefficient pairs
# ------------------------------------------------------------
#
# One pair stores one bit.
#
# 40 bits therefore require 40 pairs.
#
# We use the same pair-based method that successfully
# recovered 0xAA on Day 1.

TEXT_PAIRS = []

for row in range(1, 9):

    for col in range(1, 11, 2):

        TEXT_PAIRS.append(
            (
                (row, col),
                (row, col + 1)
            )
        )


# Make sure we really have 40 pairs.

if len(TEXT_PAIRS) != 40:

    raise RuntimeError(
        f"Expected 40 pairs, got {len(TEXT_PAIRS)}"
    )


# ------------------------------------------------------------
# 4. Load the original frame
# ------------------------------------------------------------

text_image = cv2.imread(
    INPUT,
    cv2.IMREAD_GRAYSCALE
)

if text_image is None:

    raise FileNotFoundError(
        f"Could not load {INPUT}"
    )


# ------------------------------------------------------------
# 5. Apply DWT
# ------------------------------------------------------------

text_LL, (
    text_LH,
    text_HL,
    text_HH
) = pywt.dwt2(
    text_image.astype(np.float32),
    "haar"
)


# ------------------------------------------------------------
# 6. Apply DCT to HH
# ------------------------------------------------------------

text_dct_hh = cv2.dct(text_HH)


# ------------------------------------------------------------
# 7. Embed all 40 bits
# ------------------------------------------------------------

print("\n--- TEXT EMBEDDING ---")

TEXT_MARGIN = 50.0

for index, (bit, pair) in enumerate(
    zip(payload_bits, TEXT_PAIRS),
    start=1
):

    (row_a, col_a), (row_b, col_b) = pair

    # Read the original coefficient pair.
    coefficient_a = text_dct_hh[row_a, col_a]
    coefficient_b = text_dct_hh[row_b, col_b]

    # Calculate their centre value.
    centre = (
        coefficient_a + coefficient_b
    ) / 2.0

    # Encode the bit through the relationship
    # between the two coefficients.
    #
    # Bit 1 → A > B
    # Bit 0 → A < B

    if bit == 1:

        text_dct_hh[row_a, col_a] = (
            centre + TEXT_MARGIN / 2
        )

        text_dct_hh[row_b, col_b] = (
            centre - TEXT_MARGIN / 2
        )

    else:

        text_dct_hh[row_a, col_a] = (
            centre - TEXT_MARGIN / 2
        )

        text_dct_hh[row_b, col_b] = (
            centre + TEXT_MARGIN / 2
        )


# ------------------------------------------------------------
# 8. Inverse DCT
# ------------------------------------------------------------

text_modified_HH = cv2.idct(
    text_dct_hh
)


# ------------------------------------------------------------
# 9. Inverse DWT
# ------------------------------------------------------------

text_reconstructed = pywt.idwt2(
    (
        text_LL,
        (
            text_LH,
            text_HL,
            text_modified_HH
        )
    ),
    "haar"
)


# ------------------------------------------------------------
# 10. Convert reconstructed image to uint8
# ------------------------------------------------------------

text_reconstructed = np.clip(
    text_reconstructed,
    0,
    255
).astype(np.uint8)


# ------------------------------------------------------------
# 11. Save text-containing image
# ------------------------------------------------------------

TEXT_OUTPUT = "output/hello_embedded.png"

if not cv2.imwrite(
    TEXT_OUTPUT,
    text_reconstructed
):

    raise IOError(
        f"Could not save {TEXT_OUTPUT}"
    )

print(
    f"Text embedded image saved to: {TEXT_OUTPUT}"
)


# ============================================================
# DAY 2 — EXTRACTION
# ============================================================


# ------------------------------------------------------------
# 12. Load the embedded image
# ------------------------------------------------------------

text_embedded_image = cv2.imread(
    TEXT_OUTPUT,
    cv2.IMREAD_GRAYSCALE
)

if text_embedded_image is None:

    raise FileNotFoundError(
        f"Could not load {TEXT_OUTPUT}"
    )


# ------------------------------------------------------------
# 13. DWT on embedded image
# ------------------------------------------------------------

_, (
    _,
    _,
    extracted_text_HH
) = pywt.dwt2(
    text_embedded_image.astype(np.float32),
    "haar"
)


# ------------------------------------------------------------
# 14. DCT on extracted HH
# ------------------------------------------------------------

extracted_text_dct = cv2.dct(
    extracted_text_HH
)


# ------------------------------------------------------------
# 15. Extract all 40 bits
# ------------------------------------------------------------

extracted_text_bits = []

print("\n--- TEXT EXTRACTION ---")

for index, pair in enumerate(
    TEXT_PAIRS,
    start=1
):

    (row_a, col_a), (row_b, col_b) = pair

    coefficient_a = extracted_text_dct[
        row_a,
        col_a
    ]

    coefficient_b = extracted_text_dct[
        row_b,
        col_b
    ]

    # Compare the two coefficients.
    #
    # A > B → 1
    # A < B → 0

    extracted_bit = (
        1
        if coefficient_a > coefficient_b
        else 0
    )

    extracted_text_bits.append(
        extracted_bit
    )


# ------------------------------------------------------------
# 16. Convert 40 bits back to text
# ------------------------------------------------------------

extracted_text = ""

for position in range(
    0,
    len(extracted_text_bits),
    8
):

    byte_bits = extracted_text_bits[
        position:position + 8
    ]

    value = 0

    for bit in byte_bits:

        value = (
            (value << 1) | bit
        )

    extracted_text += chr(value)


# ------------------------------------------------------------
# 17. Display result
# ------------------------------------------------------------

extracted_binary = " ".join(
    "".join(
        str(bit)
        for bit in extracted_text_bits[
            position:position + 8
        ]
    )
    for position in range(
        0,
        len(extracted_text_bits),
        8
    )
)

print("\n=== DAY 2 FINAL RESULT ===")

print(
    f"Original text:   {SECRET_TEXT}"
)

print(
    f"Original binary: "
    f"{' '.join(f'{ord(c):08b}' for c in SECRET_TEXT)}"
)

print(
    f"Extracted text:  {extracted_text}"
)

print(
    f"Extracted binary: {extracted_binary}"
)


# ------------------------------------------------------------
# 18. Verify text
# ------------------------------------------------------------

if extracted_text == SECRET_TEXT:

    print("\nTEXT EXTRACTION: SUCCESS")
    print(
        "HELLO → binary → DWT + DCT → "
        "embed → extract → HELLO"
    )

else:

    print("\nTEXT EXTRACTION: FAILED")
    print(
        f"Expected: {SECRET_TEXT}"
    )
    print(
        f"Received: {extracted_text}"
    )