# Day 20 — Measuring Reconstruction Difference

## Objective

Compare the original video frame with the DWT reconstructed frame and measure how similar they are.

## Mean Squared Error (MSE)

MSE measures the average squared difference between corresponding pixels of two images.

- Lower MSE means less difference.
- MSE = 0 means the images are identical pixel-by-pixel.

For our reconstruction:

**MSE = 0.011360**

This very small value indicates that the reconstructed frame is extremely close to the original.

## Peak Signal-to-Noise Ratio (PSNR)

PSNR measures the quality of the reconstructed image compared with the original image.

- Higher PSNR generally means better reconstruction quality.
- PSNR is measured in decibels (dB).
- A very high PSNR indicates very little distortion.

For our reconstruction:

**PSNR = 67.577176 dB**

This indicates that the reconstructed frame has very high similarity to the original frame.

## Our Results

| Metric | Result |
|---|---:|
| MSE | 0.011360 |
| PSNR | 67.577176 dB |

## Conclusion

The DWT → Inverse DWT process reconstructed the frame with extremely low error and very high PSNR.

This confirms that the DWT reconstruction process preserves the image very accurately before any secret data is embedded.

## Project Relevance

MSE and PSNR will later help us evaluate how much visual distortion is introduced when secret data is embedded into video frames.

The goal will be to maintain low MSE and high PSNR while achieving useful embedding capacity.
