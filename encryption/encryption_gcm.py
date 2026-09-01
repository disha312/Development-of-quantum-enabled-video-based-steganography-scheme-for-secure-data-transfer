from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def encrypt_data(data: bytes, key: bytes) -> bytes:
    """
    Encrypt binary data using AES-256-GCM.

    Args:
        data: Data to encrypt.
        key: 32-byte AES-256 key.

    Returns:
        Nonce + authentication tag + ciphertext.
    """

    if len(key) != 32:
        raise ValueError("AES-256 requires a 32-byte key.")

    # Generate a unique random nonce for this encryption
    nonce = get_random_bytes(12)

    # Create AES-GCM cipher
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    # Encrypt the data and generate authentication tag
    ciphertext, tag = cipher.encrypt_and_digest(data)

    # Store everything needed for later verification/decryption:
    # nonce + tag + ciphertext
    return nonce + tag + ciphertext


