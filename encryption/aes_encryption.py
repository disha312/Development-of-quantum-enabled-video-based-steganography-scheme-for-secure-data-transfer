from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad


# AES always uses a 16-byte block size
BLOCK_SIZE = AES.block_size


def encrypt_data(data, key):
    """
    Encrypt binary data using AES-256 in CBC mode.
    """

    # Generate a random Initialization Vector
    iv = get_random_bytes(BLOCK_SIZE)

    # Create AES cipher in CBC mode
    cipher = AES.new(
        key,
        AES.MODE_CBC,
        iv
    )

    # Add padding to make data a multiple of 16 bytes
    padded_data = pad(
        data,
        BLOCK_SIZE
    )

    # Encrypt the padded data
    encrypted_data = cipher.encrypt(
        padded_data
    )

    # Return IV + encrypted data
    return iv + encrypted_data


def encrypt_video(input_video, output_file, key):
    """
    Read a video file, encrypt it using AES-256-CBC,
    and save the encrypted data to a file.
    """

    input_video = Path(input_video)
    output_file = Path(output_file)

    # Check whether the video exists
    if not input_video.exists():
        raise FileNotFoundError(
            f"Video not found: {input_video}"
        )

    # Read the video as binary data
    video_data = input_video.read_bytes()

    print("Video loaded successfully.")
    print("Original video size:", len(video_data), "bytes")

    # Encrypt the video
    encrypted_data = encrypt_data(
        video_data,
        key
    )

    # Save encrypted data
    output_file.write_bytes(
        encrypted_data
    )

    print("Encryption successful!")
    print("Input :", input_video)
    print("Output:", output_file)
    print(
        "Encrypted file size:",
        len(encrypted_data),
        "bytes"
    )
