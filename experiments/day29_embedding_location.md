
# Day 29 — Decide Embedding Location

## Objective

Choose the DWT sub-band and DCT coefficient region for future secret-data embedding based on the experiments completed so far.

The location should not be chosen randomly.

---

## 1. DWT Experiment Review

The DWT decomposition produced four sub-bands:

- LL
- LH
- HL
- HH

The LL sub-band contains low-frequency information and represents important broad image structure.

The HH sub-band contains high-frequency detail.

Our DWT → Inverse DWT reconstruction produced:

- MSE: 0.011360
- PSNR: 67.577176 dB

This confirms that the DWT transformation and reconstruction preserve the frame very accurately.

### DWT Embedding Decision

For the initial embedding design, we select:

**HH sub-band**

Reason:

- HH represents high-frequency detail.
- It avoids directly modifying the major low-frequency structure contained in LL.
- It provides a reasonable starting point for testing frequency-domain embedding.

We will validate this choice experimentally once secret-data embedding is implemented.

---

## 2. DCT Experiment Review

The DCT converts the image into frequency coefficients.

The coefficient matrix contains:

- DC coefficient
- Low-frequency coefficients
- Mid-frequency coefficients
- High-frequency coefficients

The top-left region contains the low-frequency/DC information.

Our DCT → Inverse DCT reconstruction produced:

- MSE: 0.834195
- PSNR: 48.918128 dB

This confirms that the DCT transformation and inverse transformation work correctly.

### DCT Embedding Decision

We should avoid blindly modifying:

- The DC coefficient
- Important low-frequency coefficients

These coefficients contain important information about the image structure and brightness.

For the initial embedding strategy, we select:

**A mid-frequency DCT coefficient region**

Reason:

- Low-frequency coefficients are important to the visual structure.
- Extremely high-frequency coefficients can be more fragile and affected by noise or compression.
- Mid-frequency coefficients provide a potential balance between imperceptibility and robustness.

The exact coefficient position will be determined during implementation and testing rather than assumed in advance.

---

## 3. Initial Embedding Strategy

Our initial design is:

DWT
↓
HH sub-band
↓
DCT
↓
Mid-frequency coefficient region
↓
Embed secret data
↓
Inverse DCT
↓
Inverse DWT
↓
Modified frame

---

## 4. Why We Chose This Location

The selection is based on the experiments completed during Days 17–26.

### We avoid LL

LL contains important low-frequency image information.

Large changes in LL could produce noticeable visual distortion.

### We avoid the DCT DC/low-frequency region

The DC and nearby low-frequency coefficients contain important overall image information.

Blindly changing them could increase visual distortion.

### We initially choose HH

HH contains high-frequency detail and is therefore a reasonable DWT sub-band for initial embedding experiments.

### We initially choose mid-frequency DCT coefficients

Mid-frequency coefficients provide a potential compromise between:

- Visual imperceptibility
- Robustness
- Embedding capacity

---

## 5. Important Validation Step

This is an initial experimentally motivated choice.

It is not yet proven to be the optimal embedding location.

After implementing secret-data embedding, we must evaluate:

- MSE
- PSNR
- Embedding capacity
- Extraction accuracy
- Robustness
- Visual quality

If the results are poor, the DWT sub-band or DCT coefficient region can be changed based on experimental evidence.

---

## 6. Day 29 Decision

### Selected DWT sub-band

**HH**

### Selected DCT region

**Mid-frequency coefficients**

### Decision

For the next stage of the project, the initial embedding pipeline will use:

**Frame → DWT → HH sub-band → DCT → selected mid-frequency coefficients → embedding**

This decision is based on the DWT and DCT experiments rather than a random coefficient selection.

---

## Key Takeaway

The embedding location should be selected deliberately.

For the initial implementation:

**DWT → HH sub-band**

and

**DCT → Mid-frequency coefficient region**

will be tested first.

The final choice will be validated through actual embedding and extraction experiments.