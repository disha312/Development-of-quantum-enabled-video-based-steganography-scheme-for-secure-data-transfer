
# Day 22 — Understanding DCT

## Objective

Understand the basic concepts behind the Discrete Cosine Transform (DCT) and why it is useful for image/video steganography.

The main idea is that DCT allows image information to be represented using frequency components instead of working directly with pixel values.

---

## 1. Spatial Domain

The spatial domain is the normal representation of an image.

An image is represented by its individual pixel values.

For example:

Image → pixels → spatial domain

If we directly modify pixel values to hide information, we are working in the spatial domain.

---

## 2. Frequency Domain

The frequency domain represents an image using frequency components rather than individual pixels.

In general:

- Low-frequency components represent smooth areas and gradual changes.
- High-frequency components represent edges, fine details, and rapid changes.

The basic transformation is:

Spatial image
→ DCT
→ Frequency representation

---

## 3. DCT Coefficients

When DCT is applied, it produces numerical values called DCT coefficients.

These coefficients describe how much different frequency patterns are present in the image.

### DC Coefficient

The DC coefficient represents the low-frequency/average component of the image block.

### AC Coefficients

The AC coefficients represent different frequency and detail components.

For this stage of the project, advanced mathematics and the DCT equation are not required.

The important idea is that the image is represented using coefficients corresponding to different frequencies.

---

## 4. Why DCT Is Useful for Steganography

DCT can be useful for steganography because secret data can be embedded into selected frequency components rather than directly changing visible pixel values.

Instead of:

Secret data
→ Directly modify pixels

we can use:

Image
→ DCT
→ DCT coefficients
→ Modify selected coefficients
→ Inverse DCT
→ Image

The objective is to hide information while keeping the resulting image visually similar to the original.

---

## 5. DCT and Image/Video Steganography

Our project uses frequency-domain techniques because modifying selected frequency components can provide better control over visual distortion than simply changing pixels directly.

The basic concept is:

SPATIAL DOMAIN
       │
       │ DCT
       ↓
FREQUENCY DOMAIN
       │
       ├── DC coefficient
       └── AC coefficients
              │
              ↓
       Potential embedding
              │
              │ Inverse DCT
              ↓
       Reconstructed image

---

## 6. Important Project Consideration

DCT does not automatically make modifications invisible.

The final visual quality depends on:

- Which coefficients are modified
- How much each coefficient is changed
- How much secret data is embedded

Therefore, later in the project we will use image/video quality measurements such as:

- MSE — Mean Squared Error
- PSNR — Peak Signal-to-Noise Ratio

These measurements help us determine how much distortion is introduced by the embedding process.

---

## 7. Key Difference: Spatial vs Frequency Domain

| Domain | Representation | Example |
|---|---|---|
| Spatial domain | Pixel values | Directly modifying image pixels |
| Frequency domain | Frequency coefficients | Modifying DCT coefficients |

---

## 8. Key Takeaway

DCT transforms image information from the spatial domain into frequency components represented by DCT coefficients.

For our steganography project, this gives us a way to embed secret data into selected frequency components rather than directly changing pixel values.

We do not need advanced DCT mathematics yet.

The important concept is:

Image
→ DCT
→ Frequency coefficients
→ Embed data into selected coefficients
→ Inverse DCT
→ Modified image

The exact coefficients and embedding strategy will be determined during the implementation and testing stages.