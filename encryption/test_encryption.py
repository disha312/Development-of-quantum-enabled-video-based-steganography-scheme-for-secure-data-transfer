from aes_encryption import encrypt_data


# Temporary 256-bit key
# 32 bytes = 256 bits
key = bytes.fromhex(
    "00112233445566778899aabbccddeeff"
    "00112233445566778899aabbccddeeff"
)


# Small test message
data = b"Hello, this is my AES encryption test."


# Encrypt the message
encrypted_data = encrypt_data(
    data,
    key
)


print("Original data:")
print(data)

print("\nEncrypted data:")
print(encrypted_data)

print("\nEncryption successful!")