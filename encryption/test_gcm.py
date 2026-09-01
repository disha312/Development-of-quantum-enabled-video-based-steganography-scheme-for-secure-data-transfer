from encryption_gcm import encrypt_data
from Crypto.Random import get_random_bytes


# Generate a 256-bit AES key
key = get_random_bytes(32)

# Sample data
original_data = b"Hello, this is my AES-256-GCM encryption test."

print("Original data:")
print(original_data)

# Encrypt the data
encrypted_data = encrypt_data(original_data, key)

print("\nEncrypted data:")
print(encrypted_data)

print("\nEncryption successful!")
print("Original data size:", len(original_data), "bytes")
print("Encrypted data size:", len(encrypted_data), "bytes")