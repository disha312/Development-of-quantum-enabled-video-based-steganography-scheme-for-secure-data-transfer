# Day 15 — DWT Foundation

## DWT

DWT stands for Discrete Wavelet Transform.

It transforms an image into frequency-based components instead of working
directly with individual pixel values.

## Four DWT Sub-bands

A single-level 2D DWT produces four sub-bands:

- LL — Approximation
- LH — Detail
- HL — Detail
- HH — Detail

### LL — Approximation
Contains the main low-frequency information and overall image structure.

### LH — Detail
Contains horizontal-related detail information.

### HL — Detail
Contains vertical-related detail information.

### HH — Detail
Contains high-frequency detail such as fine changes and edges.

## Why DWT for Steganography?

DWT allows secret information to be embedded in an appropriate
frequency sub-band instead of directly modifying pixels.

This can help maintain visual quality and improve robustness.

## Our Project

Our planned workflow is:

ZIP
↓
Binary
↓
Video
↓
Frames
↓
DWT
↓
Four sub-bands
↓
Select suitable frequency region
↓
Embedding
↓
Inverse DWT
↓
Modified frame
↓
Stego Video

## Selected Approach

Our project study currently identifies hybrid DWT + DCT as the strongest
candidate because it provides a balance between robustness, visual quality,
and practical implementation.

## Day 15 Status

Theory completed.
No implementation yet.
