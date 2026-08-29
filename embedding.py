
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
                centre + 25.0
            )

            dct_hh[row_b, col_b] = (
                centre - 25.0
            )

        else:

            dct_hh[row_a, col_a] = (
                centre - 25.0
            )

            dct_hh[row_b, col_b] = (
                centre + 25.0
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