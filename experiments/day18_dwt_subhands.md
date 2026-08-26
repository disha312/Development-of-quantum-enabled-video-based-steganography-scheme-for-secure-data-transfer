# Day 18 — Understanding DWT Sub-bands

## DWT Overview

Discrete Wavelet Transform (DWT) decomposes an image/frame into four frequency sub-bands:

- LL — Approximation / low-frequency information
- LH — Detail information
- HL — Detail information
- HH — High-frequency / fine-detail information

## LL — Approximation

LL contains the main structure and overall appearance of the image.

For our project, we currently avoid modifying LL because changes here can have a stronger effect on the visible image.

## LH — Detail

LH contains high-frequency detail information in one direction.

It is a possible sub-band for data embedding, but it is not our primary choice at this stage.

## HL — Detail

HL contains another type of high-frequency detail information.

It is also a possible embedding region, but it is not our primary choice at this stage.

## HH — High-Frequency Detail

HH contains fine, high-frequency and diagonal detail information.

HH is our current main candidate for embedding secret data because modifications in high-frequency regions can be less visually noticeable.

However, the final embedding sub-band/strategy will be determined experimentally based on embedding capacity and video quality.

## Project Pipeline

Video Frame
→ DWT
→ LL, LH, HL, HH
→ Select appropriate detail sub-band
→ Embed secret data
→ Inverse DWT
→ Modified Frame
→ Reconstruct Video

## Key Takeaway

DWT allows us to work with different frequency components of a video frame instead of modifying the entire frame directly.

For our project, the important question is:

**Where can we embed data while maintaining good visual quality and sufficient embedding capacity?**
