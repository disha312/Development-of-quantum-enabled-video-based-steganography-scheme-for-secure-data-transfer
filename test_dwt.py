
import cv2
import pywt

image = cv2.imread("test_data/input_image.png", cv2.IMREAD_GRAYSCALE)

if image is None:
    raise FileNotFoundError("Could not load input_image.png")

LL, (LH, HL, HH) = pywt.dwt2(image, "haar")

print("Original image shape:", image.shape)
print("LL shape:", LL.shape)
print("LH shape:", LH.shape)
print("HL shape:", HL.shape)
print("HH shape:", HH.shape)