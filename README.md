# Development of Quantum-Enabled Video-Based Steganography Scheme for Secure Data Transfer

## Project Overview

This project implements a video steganography system for securely embedding secret data into video frames.

The implemented approach processes video frames and applies:

Video → Frames → DWT → DCT → Coefficient-Pair Embedding → Stego Video

The system also supports file-based payloads by converting files into ZIP archives and then into binary data before embedding.

---

## Main Features

- Text payload embedding
- Binary payload generation
- Image-based steganography
- Video frame selection
- Multi-frame video embedding
- DWT-based transformation
- DCT-based transformation
- Coefficient-pair based bit embedding
- Video payload extraction
- ZIP payload creation
- ZIP binary conversion
- ZIP recovery
- TXT, JPG and PDF payload testing
- Multiple-file payload testing
- Recovery accuracy evaluation
- Embedding capacity measurement
- MSE measurement
- PSNR measurement
- SSIM measurement
- Embedding-time measurement
- Extraction-time measurement

---

## Project Pipeline

### Text Payload

Text → Binary → DWT → DCT → Embedding

### File Payload

File(s) → ZIP → Binary → Video Frames → DWT → DCT → Embedding

### Recovery

Stego Video → Frames → DWT → DCT → Binary → ZIP → Original File

---

## Technologies Used

- Python
- OpenCV
- NumPy
- PyWavelets
- SciPy / related numerical processing libraries
- scikit-image
- ZIP file handling
- Git / GitHub

---
---

## Final Evaluation Results

The system was evaluated using the complete video embedding and extraction pipeline.

| Metric | Result |
|---|---:|
| Recovery Accuracy | 100.00% |
| Embedding Capacity | 3080 bits (385 bytes) |
| Average MSE | 0.029337 |
| Average SSIM | 0.999820 |
| Embedding Time | 85.4819 seconds |
| Extraction Time | 18.1664 seconds |

### Payload Testing

The following payload types were tested:

- TXT — SUCCESS
- JPG — SUCCESS
- PDF — SUCCESS
- Multiple files — SUCCESS

All tested ZIP payloads were successfully created and validated. The TXT payload was additionally embedded into the video, extracted, reconstructed as a ZIP, and recovered byte-for-byte identical to the original file.

### Final Pipeline Verification

The complete `embedding.py` pipeline was executed successfully from Day 1 through Day 14.

Final verification:

```text
DAY 13 PAYLOAD TESTING: SUCCESS
DAY 14 SYSTEM EVALUATION: SUCCESS

## Project Structure

```text
video-steganography/
│
├── embedding.py
├── dct.py
├── dwt.py
├── video_io.py
├── README.md
│
├── archive-old/
│   └── Earlier development experiments
│
├── experiments/
│   └── Development notes and experiments
│
├── frames/
│   └── Extracted/reference video frames
│
├── input/
│   └── Input images, video and reference files
│
├── output/
│   └── Generated results and evaluation outputs
│
├── payload/
│   └── Payload files used for testing
│
├── tests/
│   └── Test scripts
│
└── utils/
    ├── binary_reader.py
    ├── file_handling.py
    ├── measure_difference.py
    ├── zip_creator.py
    └── zip_extractor.py
