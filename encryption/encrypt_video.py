from aes_encryption import encrypt_video


# Temporary 256-bit key for testing
# 32 bytes = 256 bits
#
# Later, this key will come from
# the BB84 quantum-key module.

quantum_key = bytes.fromhex(
    "00112233445566778899aabbccddeeff"
    "00112233445566778899aabbccddeeff"
)


#current input video
input_video = "MyTest_Video.mp4"


# Encrypted output
output_file = "encrypted_video.enc"


# Start encryption
encrypt_video(
    input_video,
    output_file,
    quantum_key
)