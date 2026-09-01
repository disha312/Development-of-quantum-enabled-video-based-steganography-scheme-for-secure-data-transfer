from pathlib import Path
from my_qkd import MyQKD
from encryption_gcm import encrypt_data
import time


# Input and output video files
input_file = Path("../day7_embedded_video.mp4")
output_file = Path("encrypted_video_gcm.enc")


# ============================================================
# STEP 1: Generate AES-256 key using BB84 QKD
# ============================================================

print("=" * 60)
print("BB84 QUANTUM KEY GENERATION")
print("=" * 60)

qkd = MyQKD(n_qubits=256)

result = qkd.generate_key(
    detect_eavesdropping=True
)

# Stop encryption if QKD reports an insecure key
if not result["secure"]:
    raise RuntimeError(
        "QKD key is not secure. Encryption stopped."
    )

# Get 32-byte AES-256 key
key = qkd.get_aes_key(
    result,
    key_size=256
)

print("\nQKD key generated successfully.")
print("AES key length:", len(key), "bytes")
print("AES key size:", len(key) * 8, "bits")


# ============================================================
# STEP 2: Read input video
# ============================================================

print("\n" + "=" * 60)
print("AES-256-GCM VIDEO ENCRYPTION")
print("=" * 60)

if not input_file.exists():
    raise FileNotFoundError(
        f"Input video not found: {input_file}"
    )

video_data = input_file.read_bytes()

print("Input video:", input_file)
print("Original size:", len(video_data), "bytes")


# ============================================================
# STEP 3: Encrypt video using AES-256-GCM
# ============================================================

start_time = time.time()

encrypted_data = encrypt_data(
    video_data,
    key
)

encryption_time = time.time() - start_time


# ============================================================
# STEP 4: Save encrypted video
# ============================================================

output_file.write_bytes(encrypted_data)

print("\nEncryption successful!")
print("Output file:", output_file)
print("Encrypted size:", len(encrypted_data), "bytes")
print("Encryption time:", round(encryption_time, 4), "seconds")

print("\n" + "=" * 60)
print("QKD + AES-256-GCM ENCRYPTION COMPLETE")
print("=" * 60)
