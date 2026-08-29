
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
MARGIN = 100.0


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

    # ============================================================
# DAY 3 — INPUT TESTING
# ============================================================
#
# Purpose:
#     Test whether our working DWT + DCT pair-based
#     steganography method works with different inputs.
#
# Tests:
#     1. Short text
#     2. Longer text
#     3. 00000000
#     4. 11111111
#     5. Random binary
#
# Unlike Day 2, the number of coefficient pairs is generated
# dynamically according to the number of bits in the payload.
# ============================================================

import random


# ------------------------------------------------------------
# 1. Test inputs
# ------------------------------------------------------------

TEST_CASES = [
    ("Short text", "HI"),
    ("Longer text", "HELLO WORLD"),
    ("All zeros", "00000000"),
    ("All ones", "11111111"),
    (
        "Random binary",
        "".join(
            str(random.randint(0, 1))
            for _ in range(8)
        )
    ),
]


# ------------------------------------------------------------
# 2. Function to convert input into binary
# ------------------------------------------------------------
#
# Text:
#     "HI"
#     → 01001000 01001001
#
# Binary input:
#     "00000000"
#     → remains 00000000
#
# We distinguish the two types so that binary strings
# are not converted into ASCII characters.

def convert_to_bits(data):

    # If every character is 0 or 1, treat the input
    # directly as a binary sequence.
    if all(character in "01" for character in data):

        return [
            int(character)
            for character in data
        ]

    # Otherwise treat the input as normal text and
    # convert each character into 8-bit ASCII.
    bits = []

    for character in data:

        bits.extend(
            int(bit)
            for bit in f"{ord(character):08b}"
        )

    return bits


# ------------------------------------------------------------
# 3. Function to generate coefficient pairs
# ------------------------------------------------------------
#
# One coefficient pair stores one bit.
#
# Therefore:
#
#     16 bits → 16 pairs
#     88 bits → 88 pairs
#     etc.
#
# The DCT matrix is 360 × 640 for our current frame,
# so there is plenty of room for these small tests.

def generate_pairs(number_of_bits):

    pairs = []

    # Start away from the DC coefficient at (0,0).
    row = 1

    while len(pairs) < number_of_bits:

        # Use horizontal neighboring coefficients.
        for col in range(1, 639, 2):

            if len(pairs) >= number_of_bits:
                break

            pairs.append(
                (
                    (row, col),
                    (row, col + 1)
                )
            )

        row += 1

        # Prevent accidentally exceeding the DCT matrix.
        if row >= 360:

            raise ValueError(
                "Not enough DCT coefficient pairs "
                "for this payload."
            )

    return pairs


# ------------------------------------------------------------
# 4. Function to embed one test payload
# ------------------------------------------------------------

def embed_payload(bits, output_file):

    # Load the original frame.
    image = cv2.imread(
        INPUT,
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:

        raise FileNotFoundError(
            f"Could not load {INPUT}"
        )

    # Apply DWT.
    LL, (LH, HL, HH) = pywt.dwt2(
        image.astype(np.float32),
        "haar"
    )

    # Apply DCT to the HH sub-band.
    dct_hh = cv2.dct(HH)

    # Generate exactly as many pairs as we need.
    pairs = generate_pairs(len(bits))

    # Embed every bit.
    for bit, pair in zip(bits, pairs):

        (row_a, col_a), (row_b, col_b) = pair

        coefficient_a = dct_hh[row_a, col_a]
        coefficient_b = dct_hh[row_b, col_b]

        # Centre the pair around its original average.
        centre = (
            coefficient_a + coefficient_b
        ) / 2.0

        # Same pair-based method that successfully
        # passed Day 1 and Day 2.
        if bit == 1:

            dct_hh[row_a, col_a] = (
                centre + 100.0
            )

            dct_hh[row_b, col_b] = (
                centre - 100.0
            )

        else:

            dct_hh[row_a, col_a] = (
                centre - 100.0
            )

            dct_hh[row_b, col_b] = (
                centre + 100.0
            )

    # Inverse DCT.
    modified_HH = cv2.idct(dct_hh)

    # Inverse DWT.
    reconstructed = pywt.idwt2(
        (
            LL,
            (
                LH,
                HL,
                modified_HH
            )
        ),
        "haar"
    )

    # Convert to a valid image.
    reconstructed = np.clip(
        reconstructed,
        0,
        255
    ).astype(np.uint8)

    # Save the stego image.
    if not cv2.imwrite(
        output_file,
        reconstructed
    ):

        raise IOError(
            f"Could not save {output_file}"
        )

    return pairs


# ------------------------------------------------------------
# 5. Function to extract one test payload
# ------------------------------------------------------------

def extract_payload(output_file, pairs):

    # Load the embedded image.
    image = cv2.imread(
        output_file,
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:

        raise FileNotFoundError(
            f"Could not load {output_file}"
        )

    # Apply DWT.
    _, (_, _, HH) = pywt.dwt2(
        image.astype(np.float32),
        "haar"
    )

    # Apply DCT.
    dct_hh = cv2.dct(HH)

    extracted_bits = []

    # Read each coefficient pair.
    for pair in pairs:

        (row_a, col_a), (row_b, col_b) = pair

        coefficient_a = dct_hh[
            row_a,
            col_a
        ]

        coefficient_b = dct_hh[
            row_b,
            col_b
        ]

        # Same rule used during embedding:
        #
        #     A > B → 1
        #     A < B → 0
        extracted_bit = (
            1
            if coefficient_a > coefficient_b
            else 0
        )

        extracted_bits.append(
            extracted_bit
        )

    return extracted_bits


# ------------------------------------------------------------
# 6. Function to convert bits back to text
# ------------------------------------------------------------

def bits_to_text(bits):

    text = ""

    # Process eight bits at a time.
    for position in range(
        0,
        len(bits),
        8
    ):

        byte_bits = bits[
            position:position + 8
        ]

        # A text character must contain exactly 8 bits.
        if len(byte_bits) != 8:

            return None

        value = 0

        for bit in byte_bits:

            value = (
                (value << 1) | bit
            )

        text += chr(value)

    return text


# ============================================================
# 7. Run all Day 3 tests
# ============================================================

print("\n\n============================================================")
print("DAY 3 — INPUT TESTING")
print("============================================================")


day3_results = []


for test_name, test_input in TEST_CASES:

    print("\n------------------------------------------------------------")
    print(f"TEST: {test_name}")
    print(f"INPUT: {test_input}")
    print("------------------------------------------------------------")

    # Convert the input into bits.
    original_bits = convert_to_bits(
        test_input
    )

    print(
        "Number of bits:",
        len(original_bits)
    )

    print(
        "Binary:",
        "".join(
            str(bit)
            for bit in original_bits
        )
    )

    # Create a separate output image for this test.
    safe_name = test_name.lower().replace(
        " ",
        "_"
    )

    output_file = (
        f"output/day3_{safe_name}.png"
    )

    # Embed the payload.
    pairs = embed_payload(
        original_bits,
        output_file
    )

    # Extract the payload.
    extracted_bits = extract_payload(
        output_file,
        pairs
    )

    # Compare original and extracted bits.
    bits_match = (
        original_bits == extracted_bits
    )

    # Display extracted binary.
    print(
        "Extracted:",
        "".join(
            str(bit)
            for bit in extracted_bits
        )
    )

    print(
        "Bits match:",
        bits_match
    )

    # Handle text tests separately from raw binary tests.
    if not all(
        character in "01"
        for character in test_input
    ):

        extracted_value = bits_to_text(
            extracted_bits
        )

        print(
            "Extracted text:",
            extracted_value
        )

        test_passed = (
            extracted_value == test_input
        )

    else:

        extracted_value = "".join(
            str(bit)
            for bit in extracted_bits
        )

        test_passed = (
            extracted_value == test_input
        )

    print(
        "TEST RESULT:",
        "PASS" if test_passed else "FAIL"
    )

    day3_results.append(
        test_passed
    )


# ============================================================
# 8. Day 3 summary
# ============================================================

print("\n\n============================================================")
print("DAY 3 — FINAL SUMMARY")
print("============================================================")

for (test_name, _), result in zip(
    TEST_CASES,
    day3_results
):

    print(
        f"{test_name}: "
        f"{'PASS' if result else 'FAIL'}"
    )


if all(day3_results):

    print("\nDAY 3: ALL INPUT TESTS PASSED")

else:

    print("\nDAY 3: SOME INPUT TESTS FAILED")

    # ============================================================
# DAY 4 — SINGLE-FRAME PIPELINE TEST
# ============================================================

print("\n\n============================================================")
print("DAY 4 — SINGLE-FRAME PIPELINE")
print("============================================================")

DAY4_TEXT = "HELLO"

print(f"Input frame: {INPUT}")
print(f"Secret text: {DAY4_TEXT}")


# ------------------------------------------------------------
# 1. Read input frame
# ------------------------------------------------------------

day4_image = cv2.imread(
    INPUT,
    cv2.IMREAD_GRAYSCALE
)

if day4_image is None:
    raise FileNotFoundError(
        f"Could not load input frame: {INPUT}"
    )

print(f"Original frame shape: {day4_image.shape}")


# ------------------------------------------------------------
# 2. Convert secret text → binary
# ------------------------------------------------------------

day4_bits = convert_to_bits(DAY4_TEXT)

print(
    "Secret binary:",
    "".join(str(bit) for bit in day4_bits)
)

print(f"Total bits: {len(day4_bits)}")


# ------------------------------------------------------------
# 3. DWT
# ------------------------------------------------------------

day4_LL, (
    day4_LH,
    day4_HL,
    day4_HH
) = pywt.dwt2(
    day4_image.astype(np.float32),
    "haar"
)

print(
    "DWT completed"
)

print(
    f"HH shape: {day4_HH.shape}"
)


# ------------------------------------------------------------
# 4. DCT
# ------------------------------------------------------------

day4_dct_hh = cv2.dct(day4_HH)

print(
    "DCT completed"
)


# ------------------------------------------------------------
# 5. Generate coefficient pairs
# ------------------------------------------------------------

day4_pairs = generate_pairs(
    len(day4_bits)
)

print(
    f"Coefficient pairs selected: "
    f"{len(day4_pairs)}"
)


# ------------------------------------------------------------
# 6. Embed payload
# ------------------------------------------------------------

for bit, pair in zip(
    day4_bits,
    day4_pairs
):

    (row_a, col_a), (
        row_b,
        col_b
    ) = pair

    coefficient_a = (
        day4_dct_hh[
            row_a,
            col_a
        ]
    )

    coefficient_b = (
        day4_dct_hh[
            row_b,
            col_b
        ]
    )

    centre = (
        coefficient_a +
        coefficient_b
    ) / 2.0

    if bit == 1:

        day4_dct_hh[
            row_a,
            col_a
        ] = centre + 25.0

        day4_dct_hh[
            row_b,
            col_b
        ] = centre - 25.0

    else:

        day4_dct_hh[
            row_a,
            col_a
        ] = centre - 25.0

        day4_dct_hh[
            row_b,
            col_b
        ] = centre + 25.0


print(
    "Payload embedding completed"
)


# ------------------------------------------------------------
# 7. Inverse DCT
# ------------------------------------------------------------

day4_modified_HH = cv2.idct(
    day4_dct_hh
)

print(
    "Inverse DCT completed"
)


# ------------------------------------------------------------
# 8. Inverse DWT
# ------------------------------------------------------------

day4_reconstructed = pywt.idwt2(
    (
        day4_LL,
        (
            day4_LH,
            day4_HL,
            day4_modified_HH
        )
    ),
    "haar"
)


day4_reconstructed = np.clip(
    day4_reconstructed,
    0,
    255
).astype(np.uint8)


print(
    "Inverse DWT completed"
)


# ------------------------------------------------------------
# 9. Save stego frame
# ------------------------------------------------------------

DAY4_OUTPUT = (
    "output/day4_single_frame.png"
)

if not cv2.imwrite(
    DAY4_OUTPUT,
    day4_reconstructed
):

    raise IOError(
        f"Could not save {DAY4_OUTPUT}"
    )


print(
    f"Stego frame saved to: {DAY4_OUTPUT}"
)


# ------------------------------------------------------------
# 10. Extract from the resulting frame
# ------------------------------------------------------------

day4_extracted_image = cv2.imread(
    DAY4_OUTPUT,
    cv2.IMREAD_GRAYSCALE
)

if day4_extracted_image is None:
    raise FileNotFoundError(
        f"Could not load {DAY4_OUTPUT}"
    )


_, (
    _,
    _,
    day4_extracted_HH
) = pywt.dwt2(
    day4_extracted_image.astype(
        np.float32
    ),
    "haar"
)


day4_extracted_dct = cv2.dct(
    day4_extracted_HH
)


day4_extracted_bits = []

for pair in day4_pairs:

    (row_a, col_a), (
        row_b,
        col_b
    ) = pair

    coefficient_a = (
        day4_extracted_dct[
            row_a,
            col_a
        ]
    )

    coefficient_b = (
        day4_extracted_dct[
            row_b,
            col_b
        ]
    )

    extracted_bit = (
        1
        if coefficient_a > coefficient_b
        else 0
    )

    day4_extracted_bits.append(
        extracted_bit
    )


# ------------------------------------------------------------
# 11. Convert extracted bits → text
# ------------------------------------------------------------

day4_extracted_text = bits_to_text(
    day4_extracted_bits
)


# ------------------------------------------------------------
# 12. Final result
# ------------------------------------------------------------

print("\n--- DAY 4 FINAL RESULT ---")

print(
    f"Original text:  {DAY4_TEXT}"
)

print(
    "Original binary:",
    "".join(
        str(bit)
        for bit in day4_bits
    )
)

print(
    f"Extracted text: {day4_extracted_text}"
)

print(
    "Extracted binary:",
    "".join(
        str(bit)
        for bit in day4_extracted_bits
    )
)


if (
    day4_extracted_text ==
    DAY4_TEXT
):

    print(
        "\nDAY 4 SINGLE-FRAME PIPELINE: SUCCESS"
    )

    print(
        "Input → DWT → DCT → Embed → "
        "Inverse DCT → Inverse DWT → Extract → HELLO"
    )

else:

    print(
        "\nDAY 4 SINGLE-FRAME PIPELINE: FAILED"
    )

    print(
        f"Expected: {DAY4_TEXT}"
    )

    print(
        f"Got:      {day4_extracted_text}"
    )

    # ============================================================
# DAY 5 — SINGLE-FRAME EXTRACTION
# ============================================================

print("\n\n============================================================")
print("DAY 5 — SINGLE-FRAME EXTRACTION")
print("============================================================")

DAY5_TEXT = "HELLO"

print(f"Stego frame: {DAY4_OUTPUT}")
print(f"Expected text: {DAY5_TEXT}")


# ------------------------------------------------------------
# 1. Convert original secret to bits
# ------------------------------------------------------------

day5_original_bits = convert_to_bits(
    DAY5_TEXT
)

print(
    "Expected binary:",
    "".join(
        str(bit)
        for bit in day5_original_bits
    )
)


# ------------------------------------------------------------
# 2. Load the stego frame created by Day 4
# ------------------------------------------------------------

day5_stego_image = cv2.imread(
    DAY4_OUTPUT,
    cv2.IMREAD_GRAYSCALE
)

if day5_stego_image is None:

    raise FileNotFoundError(
        f"Could not load stego frame: {DAY4_OUTPUT}"
    )

print(
    f"Stego frame shape: {day5_stego_image.shape}"
)


# ------------------------------------------------------------
# 3. Apply DWT to stego frame
# ------------------------------------------------------------

day5_LL, (
    day5_LH,
    day5_HL,
    day5_HH
) = pywt.dwt2(
    day5_stego_image.astype(np.float32),
    "haar"
)

print("DWT extraction stage: SUCCESS")


# ------------------------------------------------------------
# 4. Apply DCT to HH sub-band
# ------------------------------------------------------------

day5_dct_hh = cv2.dct(
    day5_HH
)

print("DCT extraction stage: SUCCESS")


# ------------------------------------------------------------
# 5. Use the same coefficient pairs
# ------------------------------------------------------------

day5_pairs = generate_pairs(
    len(day5_original_bits)
)

print(
    f"Coefficient pairs used: {len(day5_pairs)}"
)


# ------------------------------------------------------------
# 6. Extract every bit
# ------------------------------------------------------------

day5_extracted_bits = []

for pair in day5_pairs:

    (row_a, col_a), (
        row_b,
        col_b
    ) = pair

    coefficient_a = (
        day5_dct_hh[
            row_a,
            col_a
        ]
    )

    coefficient_b = (
        day5_dct_hh[
            row_b,
            col_b
        ]
    )

    extracted_bit = (
        1
        if coefficient_a > coefficient_b
        else 0
    )

    day5_extracted_bits.append(
        extracted_bit
    )


# ------------------------------------------------------------
# 7. Compare every bit
# ------------------------------------------------------------

print(
    "Extracted binary:",
    "".join(
        str(bit)
        for bit in day5_extracted_bits
    )
)

bits_match = (
    day5_original_bits ==
    day5_extracted_bits
)

print(
    f"Exact bit recovery: "
    f"{'SUCCESS' if bits_match else 'FAILED'}"
)


# ------------------------------------------------------------
# 8. Convert recovered bits back to text
# ------------------------------------------------------------

day5_extracted_text = bits_to_text(
    day5_extracted_bits
)

print(
    f"Recovered text: {day5_extracted_text}"
)


# ------------------------------------------------------------
# 9. Final Day 5 verification
# ------------------------------------------------------------

print("\n--- DAY 5 FINAL RESULT ---")

if (
    bits_match
    and
    day5_extracted_text == DAY5_TEXT
):

    print(
        "Original text: ",
        DAY5_TEXT
    )

    print(
        "Extracted text:",
        day5_extracted_text
    )

    print(
        "\nDAY 5 SINGLE-FRAME EXTRACTION: SUCCESS"
    )

    print(
        "Exact recovery verified:"
    )

    print(
        "HELLO → binary → "
        "DWT → DCT → extract → binary → HELLO"
    )

else:

    print(
        "DAY 5 SINGLE-FRAME EXTRACTION: FAILED"
    )

    print(
        "Expected:",
        DAY5_TEXT
    )

    print(
        "Extracted:",
        day5_extracted_text
    )

    # ============================================================
# DAY 6 — FRAME SELECTION
# ============================================================

print("\n\n============================================================")
print("DAY 6 — FRAME SELECTION")
print("============================================================")

# Select every Nth frame for payload embedding
FRAME_INTERVAL = 10

# Number of frames in our test video
TOTAL_FRAMES = 100

selected_frames = []

for frame_number in range(TOTAL_FRAMES):

    if frame_number % FRAME_INTERVAL == 0:
        selected_frames.append(frame_number)


print(
    f"Frame interval: every {FRAME_INTERVAL} frames"
)

print(
    f"Total frames: {TOTAL_FRAMES}"
)

print(
    f"Selected frames: {len(selected_frames)}"
)

print(
    "Selected frame numbers:"
)

print(
    selected_frames
)


# ------------------------------------------------------------
# Verify frame selection
# ------------------------------------------------------------

expected_frames = list(
    range(
        0,
        TOTAL_FRAMES,
        FRAME_INTERVAL
    )
)

if selected_frames == expected_frames:

    print(
        "\nDAY 6 FRAME SELECTION: SUCCESS"
    )

    print(
        "Payload frames selected correctly."
    )

else:

    print(
        "\nDAY 6 FRAME SELECTION: FAILED"
    )

    print(
        f"Expected: {expected_frames}"
    )

    print(
        f"Got:      {selected_frames}"
    )

    # ============================================================
# DAY 7 — EMBED PAYLOAD ACROSS VIDEO FRAMES
# ============================================================

print("\n\n============================================================")
print("DAY 7 — EMBED ACROSS VIDEO FRAMES")
print("============================================================")

DAY7_VIDEO_INPUT = "input/MyTest_Video.mp4"
DAY7_VIDEO_OUTPUT = "output/day7_embedded_video.avi"

DAY7_TEXT = "HELLO WORLD"
DAY7_BITS = convert_to_bits(DAY7_TEXT)

FRAME_INTERVAL = 10

print(f"Input video: {DAY7_VIDEO_INPUT}")
print(f"Secret text: {DAY7_TEXT}")
print(f"Total payload bits: {len(DAY7_BITS)}")
print(f"Frame interval: every {FRAME_INTERVAL} frames")


# ------------------------------------------------------------
# 1. Open video
# ------------------------------------------------------------

day7_cap = cv2.VideoCapture(
    DAY7_VIDEO_INPUT
)

if not day7_cap.isOpened():
    raise IOError(
        f"Could not open video: {DAY7_VIDEO_INPUT}"
    )


fps = day7_cap.get(cv2.CAP_PROP_FPS)
width = int(
    day7_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)
height = int(
    day7_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)
total_frames = int(
    day7_cap.get(cv2.CAP_PROP_FRAME_COUNT)
)

print(f"FPS: {fps}")
print(f"Resolution: {width} x {height}")
print(f"Total frames: {total_frames}")


# ------------------------------------------------------------
# 2. Create temporary output video
# ------------------------------------------------------------

fourcc = cv2.VideoWriter_fourcc(
    *"FFV1"
)
day7_writer = cv2.VideoWriter(
    DAY7_VIDEO_OUTPUT,
    fourcc,
    fps,
    (width, height),
    True
)

if not day7_writer.isOpened():
    day7_cap.release()

    raise IOError(
        f"Could not create output video: "
        f"{DAY7_VIDEO_OUTPUT}"
    )


# ------------------------------------------------------------
# 3. Calculate payload capacity per selected frame
# ------------------------------------------------------------

BITS_PER_FRAME = 40

payload_position = 0
selected_frame_count = 0
embedded_frame_count = 0


# ------------------------------------------------------------
# 4. Process video frames
# ------------------------------------------------------------

frame_number = 0

while True:

    success, frame = day7_cap.read()

    if not success:
        break

    # Select every Nth frame.
    if (
        frame_number % FRAME_INTERVAL == 0
        and payload_position < len(DAY7_BITS)
    ):

        selected_frame_count += 1

        # Convert frame to grayscale for
        # DWT + DCT processing.
        gray_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # DWT.
        LL, (
            LH,
            HL,
            HH
        ) = pywt.dwt2(
            gray_frame.astype(
                np.float32
            ),
            "haar"
        )

        # DCT on HH.
        dct_hh = cv2.dct(HH)

        # Take the next payload chunk.
        remaining_bits = (
            len(DAY7_BITS)
            - payload_position
        )

        chunk_size = min(
            BITS_PER_FRAME,
            remaining_bits
        )

        chunk = DAY7_BITS[
            payload_position:
            payload_position + chunk_size
        ]

        # Generate coefficient pairs.
        pairs = generate_pairs(
            chunk_size
        )

        # Embed chunk.
        for bit, pair in zip(
            chunk,
            pairs
        ):

            (row_a, col_a), (
                row_b,
                col_b
            ) = pair

            coefficient_a = (
                dct_hh[
                    row_a,
                    col_a
                ]
            )

            coefficient_b = (
                dct_hh[
                    row_b,
                    col_b
                ]
            )

            centre = (
                coefficient_a
                + coefficient_b
            ) / 2.0

            if bit == 1:

                dct_hh[
                    row_a,
                    col_a
                ] = centre + 25.0

                dct_hh[
                    row_b,
                    col_b
                ] = centre - 25.0

            else:

                dct_hh[
                    row_a,
                    col_a
                ] = centre - 25.0

                dct_hh[
                    row_b,
                    col_b
                ] = centre + 25.0


        # Inverse DCT.
        modified_HH = cv2.idct(
            dct_hh
        )

        # Inverse DWT.
        reconstructed = pywt.idwt2(
            (
                LL,
                (
                    LH,
                    HL,
                    modified_HH
                )
            ),
            "haar"
        )

        reconstructed = np.clip(
            reconstructed,
            0,
            255
        ).astype(np.uint8)

        # Convert grayscale stego frame
        # back to BGR so the video writer
        # receives the expected format.
        frame = cv2.cvtColor(
            reconstructed,
            cv2.COLOR_GRAY2BGR
        )

        payload_position += chunk_size
        embedded_frame_count += 1

        print(
            f"Frame {frame_number}: "
            f"embedded {chunk_size} bits"
        )

    # Write frame whether modified or not.
    day7_writer.write(frame)

    frame_number += 1


# ------------------------------------------------------------
# 5. Release video resources
# ------------------------------------------------------------

day7_cap.release()
day7_writer.release()


# ------------------------------------------------------------
# 6. Final result
# ------------------------------------------------------------

print("\n--- DAY 7 FINAL RESULT ---")

print(
    f"Frames processed: {frame_number}"
)

print(
    f"Selected frames: {selected_frame_count}"
)

print(
    f"Frames carrying payload: "
    f"{embedded_frame_count}"
)

print(
    f"Bits embedded: {payload_position}"
)

print(
    f"Total payload bits: {len(DAY7_BITS)}"
)

print(
    f"Output video: {DAY7_VIDEO_OUTPUT}"
)


if payload_position == len(DAY7_BITS):

    print(
        "\nDAY 7 MULTI-FRAME EMBEDDING: SUCCESS"
    )

    print(
        "Video → Frames → DWT + DCT → "
        "Embedding completed"
    )

else:

    print(
        "\nDAY 7 MULTI-FRAME EMBEDDING: FAILED"
    )

    print(
        f"Expected {len(DAY7_BITS)} bits, "
        f"embedded {payload_position}"
    )

    # ============================================================
# DAY 9 — VIDEO EXTRACTION
# ============================================================

print("\n\n============================================================")
print("DAY 9 — VIDEO EXTRACTION")
print("============================================================")

DAY9_VIDEO_INPUT = "output/day7_embedded_video.avi"

DAY9_EXPECTED_TEXT = "HELLO WORLD"
DAY9_EXPECTED_BITS = convert_to_bits(DAY9_EXPECTED_TEXT)

FRAME_INTERVAL = 10
BITS_PER_FRAME = 40

print(f"Stego video: {DAY9_VIDEO_INPUT}")
print(f"Expected text: {DAY9_EXPECTED_TEXT}")
print(f"Expected bits: {len(DAY9_EXPECTED_BITS)}")
print(f"Frame interval: every {FRAME_INTERVAL} frames")


# ------------------------------------------------------------
# 1. Open stego video
# ------------------------------------------------------------

day9_cap = cv2.VideoCapture(
    DAY9_VIDEO_INPUT
)

if not day9_cap.isOpened():

    raise IOError(
        f"Could not open stego video: "
        f"{DAY9_VIDEO_INPUT}"
    )


total_frames = int(
    day9_cap.get(cv2.CAP_PROP_FRAME_COUNT)
)

print(f"Total frames: {total_frames}")


# ------------------------------------------------------------
# 2. Extract payload from selected frames
# ------------------------------------------------------------

extracted_bits = []

frame_number = 0

while True:

    success, frame = day9_cap.read()

    if not success:
        break

    # Only inspect the same frames used
    # during embedding.
    if (
        frame_number % FRAME_INTERVAL == 0
        and len(extracted_bits)
        < len(DAY9_EXPECTED_BITS)
    ):

        remaining_bits = (
            len(DAY9_EXPECTED_BITS)
            - len(extracted_bits)
        )

        chunk_size = min(
            BITS_PER_FRAME,
            remaining_bits
        )

        print(
            f"Frame {frame_number}: "
            f"extracting {chunk_size} bits"
        )

        # Convert frame to grayscale.
        gray_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # DWT.
        _, (
            _,
            _,
            HH
        ) = pywt.dwt2(
            gray_frame.astype(
                np.float32
            ),
            "haar"
        )

        # DCT.
        dct_hh = cv2.dct(HH)

        # Generate the exact same coefficient
        # pairs used during embedding.
        pairs = generate_pairs(
            chunk_size
        )

        # Extract bits.
        for pair in pairs:

            (row_a, col_a), (
                row_b,
                col_b
            ) = pair

            coefficient_a = (
                dct_hh[
                    row_a,
                    col_a
                ]
            )

            coefficient_b = (
                dct_hh[
                    row_b,
                    col_b
                ]
            )

            bit = (
                1
                if coefficient_a > coefficient_b
                else 0
            )

            extracted_bits.append(bit)

    frame_number += 1


day9_cap.release()


# ------------------------------------------------------------
# 3. Convert extracted bits to text
# ------------------------------------------------------------

extracted_bits = extracted_bits[
    :len(DAY9_EXPECTED_BITS)
]

extracted_text = bits_to_text(
    extracted_bits
)


# ------------------------------------------------------------
# 4. Verify exact recovery
# ------------------------------------------------------------

print("\n--- DAY 9 FINAL RESULT ---")

print(
    f"Expected text:  {DAY9_EXPECTED_TEXT}"
)

print(
    f"Extracted text: {extracted_text}"
)

print(
    f"Expected bits:  "
    f"{''.join(map(str, DAY9_EXPECTED_BITS))}"
)

print(
    f"Extracted bits: "
    f"{''.join(map(str, extracted_bits))}"
)


if extracted_bits == DAY9_EXPECTED_BITS:

    print(
        "\nBinary extraction: SUCCESS"
    )

else:

    print(
        "\nBinary extraction: FAILED"
    )


if extracted_text == DAY9_EXPECTED_TEXT:

    print(
        "Text extraction: SUCCESS"
    )

    print(
        "\nDAY 9 VIDEO EXTRACTION: SUCCESS"
    )

else:

    print(
        "Text extraction: FAILED"
    )

    print(
        "\nDAY 9 VIDEO EXTRACTION: FAILED"
    )

    # ============================================================
# DAY 11 — ZIP PAYLOAD
# ============================================================

import zipfile
from pathlib import Path


DAY11_INPUT_FILE = "payload/test.txt"
DAY11_ZIP_FILE = "output/day11_payload.zip"


def zip_payload(input_file, zip_file):
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Could not find {input_file}"
        )

    Path(zip_file).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with zipfile.ZipFile(
        zip_file,
        "w",
        compression=zipfile.ZIP_DEFLATED
    ) as zf:

        zf.write(
            input_path,
            arcname=input_path.name
        )


def file_to_binary(file_path):

    data = Path(file_path).read_bytes()

    bits = "".join(
        format(byte, "08b")
        for byte in data
    )

    return bits


print()
print("=" * 60)
print("DAY 11 — ZIP PAYLOAD")
print("=" * 60)

zip_payload(
    DAY11_INPUT_FILE,
    DAY11_ZIP_FILE
)

zip_bits = file_to_binary(
    DAY11_ZIP_FILE
)

print(f"Input file: {DAY11_INPUT_FILE}")
print(f"ZIP file: {DAY11_ZIP_FILE}")
print(f"ZIP size: {Path(DAY11_ZIP_FILE).stat().st_size} bytes")
print(f"Binary payload size: {len(zip_bits)} bits")

print()
print("DAY 11 ZIP PAYLOAD: SUCCESS")
print("Files → ZIP → Binary → Ready for embedding")

# ============================================================
# DAY 12 — ZIP RECOVERY
# ============================================================

DAY12_ZIP_INPUT = "output/day11_payload.zip"
DAY12_RECOVERED_ZIP = "output/day12_recovered.zip"
DAY12_RECOVERED_DIR = "output/day12_recovered_files"


def binary_to_file(bits, output_file):

    if len(bits) % 8 != 0:
        raise ValueError(
            "Binary payload length must be a multiple of 8"
        )

    data = bytes(
        int(bits[i:i + 8], 2)
        for i in range(0, len(bits), 8)
    )

    Path(output_file).write_bytes(data)


def recover_zip_from_binary(zip_file):

    zip_bytes = Path(zip_file).read_bytes()

    bits = "".join(
        format(byte, "08b")
        for byte in zip_bytes
    )

    return bits


print()
print("=" * 60)
print("DAY 12 — ZIP RECOVERY")
print("=" * 60)

# Read the ZIP as binary.
recovery_bits = recover_zip_from_binary(
    DAY12_ZIP_INPUT
)

print(f"Original ZIP: {DAY12_ZIP_INPUT}")
print(f"Binary payload: {len(recovery_bits)} bits")

# Reconstruct the ZIP.
binary_to_file(
    recovery_bits,
    DAY12_RECOVERED_ZIP
)

# Extract the reconstructed ZIP.
Path(DAY12_RECOVERED_DIR).mkdir(
    parents=True,
    exist_ok=True
)

with zipfile.ZipFile(
    DAY12_RECOVERED_ZIP,
    "r"
) as zf:

    zf.extractall(
        DAY12_RECOVERED_DIR
    )

recovered_file = (
    Path(DAY12_RECOVERED_DIR)
    / Path(DAY11_INPUT_FILE).name
)

original_data = Path(
    DAY11_INPUT_FILE
).read_bytes()

recovered_data = recovered_file.read_bytes()

print(f"Recovered file: {recovered_file}")
print(f"Original size: {len(original_data)} bytes")
print(f"Recovered size: {len(recovered_data)} bytes")

if original_data == recovered_data:

    print()
    print("DAY 12 ZIP RECOVERY: SUCCESS")
    print("Original and recovered files are byte-for-byte identical.")

else:

    print()
    print("DAY 12 ZIP RECOVERY: FAILED")
    print("Recovered file differs from original.")

    # ============================================================
# DAY 13 — TXT PAYLOAD TEST
# ============================================================

print()
print("=" * 60)
print("DAY 13 — TXT PAYLOAD TEST")
print("=" * 60)

DAY13_INPUT_FILE = "payload/day13/test.txt"
DAY13_ZIP_FILE = "output/day13_txt.zip"
DAY13_VIDEO_OUTPUT = "output/day13_txt_stego.avi"
DAY13_RECOVERED_ZIP = "output/day13_txt_recovered.zip"
DAY13_RECOVERED_DIR = "output/day13_txt_recovered_files"

DAY13_FRAME_INTERVAL = 10
DAY13_BITS_PER_FRAME = 40


# ------------------------------------------------------------
# 1. Create ZIP
# ------------------------------------------------------------

zip_payload(
    DAY13_INPUT_FILE,
    DAY13_ZIP_FILE
)

day13_bits = file_to_binary(
    DAY13_ZIP_FILE
)

print(f"Input file: {DAY13_INPUT_FILE}")
print(f"ZIP file: {DAY13_ZIP_FILE}")
print(
    f"ZIP size: "
    f"{Path(DAY13_ZIP_FILE).stat().st_size} bytes"
)
print(f"Payload bits: {len(day13_bits)}")


# ------------------------------------------------------------
# 2. Open original video
# ------------------------------------------------------------

day13_cap = cv2.VideoCapture(
    DAY7_VIDEO_INPUT
)

if not day13_cap.isOpened():

    raise IOError(
        f"Could not open video: {DAY7_VIDEO_INPUT}"
    )

fps = day13_cap.get(
    cv2.CAP_PROP_FPS
)

width = int(
    day13_cap.get(
        cv2.CAP_PROP_FRAME_WIDTH
    )
)

height = int(
    day13_cap.get(
        cv2.CAP_PROP_FRAME_HEIGHT
    )
)

total_frames = int(
    day13_cap.get(
        cv2.CAP_PROP_FRAME_COUNT
    )
)

print(f"FPS: {fps}")
print(f"Resolution: {width} x {height}")
print(f"Total frames: {total_frames}")


# ------------------------------------------------------------
# 3. Check capacity
# ------------------------------------------------------------

selected_frames = (
    (total_frames - 1)
    // DAY13_FRAME_INTERVAL
    + 1
)

capacity = (
    selected_frames
    * DAY13_BITS_PER_FRAME
)

print(f"Video capacity: {capacity} bits")

if len(day13_bits) > capacity:

    day13_cap.release()

    raise ValueError(
        f"Payload too large: "
        f"{len(day13_bits)} bits > "
        f"{capacity} bits"
    )


# ------------------------------------------------------------
# 4. Create stego video
# ------------------------------------------------------------

fourcc = cv2.VideoWriter_fourcc(
    *"FFV1"
)

day13_writer = cv2.VideoWriter(
    DAY13_VIDEO_OUTPUT,
    fourcc,
    fps,
    (width, height),
    True
)

if not day13_writer.isOpened():

    day13_cap.release()

    raise IOError(
        f"Could not create "
        f"{DAY13_VIDEO_OUTPUT}"
    )


# ------------------------------------------------------------
# 5. Embed ZIP binary across frames
# ------------------------------------------------------------

payload_position = 0
frame_number = 0
embedded_frames = 0

while True:

    success, frame = day13_cap.read()

    if not success:
        break

    if (
        frame_number % DAY13_FRAME_INTERVAL == 0
        and payload_position < len(day13_bits)
    ):

        remaining_bits = (
            len(day13_bits)
            - payload_position
        )

        chunk_size = min(
            DAY13_BITS_PER_FRAME,
            remaining_bits
        )

        chunk = day13_bits[
            payload_position:
            payload_position + chunk_size
        ]

        gray_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        LL, (
            LH,
            HL,
            HH
        ) = pywt.dwt2(
            gray_frame.astype(
                np.float32
            ),
            "haar"
        )

        dct_hh = cv2.dct(HH)

        pairs = generate_pairs(
            chunk_size
        )

        for bit, pair in zip(
            chunk,
            pairs
        ):

            (row_a, col_a), (
                row_b,
                col_b
            ) = pair

            coefficient_a = dct_hh[
                row_a,
                col_a
            ]

            coefficient_b = dct_hh[
                row_b,
                col_b
            ]

            centre = (
                coefficient_a
                + coefficient_b
            ) / 2.0

            if bit == "1":

                dct_hh[
                    row_a,
                    col_a
                ] = centre + MARGIN / 2

                dct_hh[
                    row_b,
                    col_b
                ] = centre - MARGIN/2

            else:

                dct_hh[
                    row_a,
                    col_a
                ] = centre - MARGIN / 2

                dct_hh[
                    row_b,
                    col_b
                ] = centre + MARGIN / 2

        modified_HH = cv2.idct(
            dct_hh
        )

        reconstructed = pywt.idwt2(
            (
                LL,
                (
                    LH,
                    HL,
                    modified_HH
                )
            ),
            "haar"
        )

        reconstructed = np.clip(
            reconstructed,
            0,
            255
        ).astype(np.uint8)

        frame = cv2.cvtColor(
            reconstructed,
            cv2.COLOR_GRAY2BGR
        )

        payload_position += chunk_size
        embedded_frames += 1

        print(
            f"Frame {frame_number}: "
            f"embedded {chunk_size} bits"
        )

    day13_writer.write(frame)

    frame_number += 1


day13_cap.release()
day13_writer.release()


# ------------------------------------------------------------
# 6. Extract ZIP binary from stego video
# ------------------------------------------------------------

day13_cap = cv2.VideoCapture(
    DAY13_VIDEO_OUTPUT
)

if not day13_cap.isOpened():

    raise IOError(
        f"Could not open "
        f"{DAY13_VIDEO_OUTPUT}"
    )

extracted_bits = []
frame_number = 0

while True:

    success, frame = day13_cap.read()

    if not success:
        break

    if (
        frame_number % DAY13_FRAME_INTERVAL == 0
        and len(extracted_bits)
        < len(day13_bits)
    ):

        remaining_bits = (
            len(day13_bits)
            - len(extracted_bits)
        )

        chunk_size = min(
            DAY13_BITS_PER_FRAME,
            remaining_bits
        )

        gray_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        _, (
            _,
            _,
            HH
        ) = pywt.dwt2(
            gray_frame.astype(
                np.float32
            ),
            "haar"
        )

        dct_hh = cv2.dct(HH)

        pairs = generate_pairs(
            chunk_size
        )

        for pair in pairs:

            (row_a, col_a), (
                row_b,
                col_b
            ) = pair

            coefficient_a = dct_hh[
                row_a,
                col_a
            ]

            coefficient_b = dct_hh[
                row_b,
                col_b
            ]

            bit = (
                "1"
                if coefficient_a > coefficient_b
                else "0"
            )

            extracted_bits.append(
                bit
            )

    frame_number += 1

day13_cap.release()

extracted_bits = extracted_bits[
    :len(day13_bits)
]


# ------------------------------------------------------------
# 7. Reconstruct ZIP
# ------------------------------------------------------------

DAY13_RECOVERED_DIR_PATH = Path(
    DAY13_RECOVERED_DIR
)

DAY13_RECOVERED_DIR_PATH.mkdir(
    parents=True,
    exist_ok=True
)

extracted_binary = "".join(
    extracted_bits
)

binary_to_file(
    extracted_binary,
    DAY13_RECOVERED_ZIP
)

# ------------------------------------------------------------
# 7A. Compare original and extracted binary
# ------------------------------------------------------------

original_bits = day13_bits

mismatch_count = sum(
    a != b
    for a, b in zip(
        original_bits,
        extracted_bits
    )
)

print()
print("--- DAY 13 BINARY COMPARISON ---")
print(f"Original bits:  {len(original_bits)}")
print(f"Extracted bits: {len(extracted_bits)}")
print(f"Bit mismatches: {mismatch_count}")

if mismatch_count == 0:

    print("Binary payload: EXACT MATCH")

else:

    print("Binary payload: MISMATCH")

    first_mismatch = None

    for i, (a, b) in enumerate(
        zip(
            original_bits,
            extracted_bits
        )
    ):

        if a != b:

            first_mismatch = i
            break

    if first_mismatch is not None:

        print(
            f"First mismatch at bit: "
            f"{first_mismatch}"
        )

        start = max(
            0,
            first_mismatch - 16
        )

        end = min(
            len(original_bits),
            first_mismatch + 32
        )

        print(
            "Original:  ",
            original_bits[start:end]
        )

        print(
            "Extracted: ",
            extracted_bits[start:end]
        )


# ------------------------------------------------------------
# 8. Extract recovered ZIP
# ------------------------------------------------------------

with zipfile.ZipFile(
    DAY13_RECOVERED_ZIP,
    "r"
) as zf:

    zf.extractall(
        DAY13_RECOVERED_DIR
    )


recovered_file = (
    DAY13_RECOVERED_DIR_PATH
    / Path(DAY13_INPUT_FILE).name
)


# ------------------------------------------------------------
# 9. Verify
# ------------------------------------------------------------

original_data = Path(
    DAY13_INPUT_FILE
).read_bytes()

recovered_data = recovered_file.read_bytes()


print()
print("--- DAY 13 TXT TEST RESULT ---")
print(f"Original file: {DAY13_INPUT_FILE}")
print(f"Recovered file: {recovered_file}")
print(f"Original size: {len(original_data)} bytes")
print(f"Recovered size: {len(recovered_data)} bytes")
print(
    f"Payload bits: {len(day13_bits)}"
)
print(
    f"Extracted bits: {len(extracted_bits)}"
)


if (
    extracted_bits == list(day13_bits)
    and original_data == recovered_data
):

    print()
    print(
        "DAY 13 TXT PAYLOAD TEST: SUCCESS"
    )
    print(
        "ZIP → Binary → Video Embedding → "
        "Extraction → ZIP → TXT"
    )
    print(
        "Original and recovered files are "
        "byte-for-byte identical."
    )

else:

    print()
    print(
        "DAY 13 TXT PAYLOAD TEST: FAILED"
    )

# ============================================================
# DAY 13 — PAYLOAD TESTING
# ============================================================

print()
print("=" * 60)
print("DAY 13 — PAYLOAD TESTING")
print("=" * 60)

DAY13_TESTS = {
    "TXT": "output/day13_txt.zip",
    "JPG": "output/day13_jpg.zip",
    "PDF": "output/day13_pdf.zip",
    "MULTIPLE": "output/day13_multiple.zip"
}

# Current Day 7 embedding capacity.
# 3 selected frames × 40 bits per frame = 120 bits.
DAY13_VIDEO_CAPACITY_BITS = 3 * 40

print(
    f"Current video payload capacity: "
    f"{DAY13_VIDEO_CAPACITY_BITS} bits"
)

print()

day13_all_valid = True

for test_name, zip_file in DAY13_TESTS.items():

    zip_path = Path(zip_file)

    print("-" * 60)
    print(f"{test_name} PAYLOAD")
    print("-" * 60)

    if not zip_path.exists():

        print(f"ZIP file not found: {zip_file}")
        day13_all_valid = False
        continue

    zip_size = zip_path.stat().st_size
    zip_bits = zip_size * 8

    print(f"ZIP file: {zip_file}")
    print(f"ZIP size: {zip_size} bytes")
    print(f"Binary payload: {zip_bits} bits")

    # --------------------------------------------------------
    # Verify ZIP integrity
    # --------------------------------------------------------

    try:

        with zipfile.ZipFile(
            zip_file,
            "r"
        ) as zf:

            bad_file = zf.testzip()
            file_names = zf.namelist()

            if bad_file is not None:

                print(
                    f"ZIP integrity: FAILED "
                    f"(corrupt file: {bad_file})"
                )

                day13_all_valid = False

            else:

                print("ZIP integrity: SUCCESS")
                print(f"Files inside ZIP: {file_names}")

    except zipfile.BadZipFile:

        print("ZIP integrity: FAILED")
        day13_all_valid = False
        continue

    # --------------------------------------------------------
    # Capacity check
    # --------------------------------------------------------

    if zip_bits <= DAY13_VIDEO_CAPACITY_BITS:

        print("Current video capacity: SUFFICIENT")

    else:

        print("Current video capacity: INSUFFICIENT")

    print()


# ============================================================
# DAY 13 FINAL RESULT
# ============================================================

print("=" * 60)
print("DAY 13 FINAL RESULT")
print("=" * 60)

if day13_all_valid:

    print("TXT test: SUCCESS")
    print("JPG test: SUCCESS")
    print("PDF test: SUCCESS")
    print("Multiple-file test: SUCCESS")

    print()
    print("All ZIP payloads are valid and readable.")
    print(
        "Payload sizes were measured in bytes and bits."
    )

    print()
    print("DAY 13 PAYLOAD TESTING: SUCCESS")

else:

    print()
    print("One or more payload tests FAILED.")

    print()
    print("DAY 13 PAYLOAD TESTING: FAILED")
