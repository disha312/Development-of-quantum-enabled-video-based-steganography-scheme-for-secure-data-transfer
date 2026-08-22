
from pathlib import Path

zip_file = Path("payload.zip")

with open(zip_file, "rb") as file:
    data = file.read()

print("Number of bytes:", len(data))

bits = "".join(format(byte, "08b") for byte in data)

print("Number of bits:", len(bits))
print("First 64 bits:", bits[:64])