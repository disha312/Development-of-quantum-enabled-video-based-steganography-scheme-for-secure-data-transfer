
from pathlib import Path

input_folder = Path("input")

for file in input_folder.iterdir():
    if file.is_file():
        size = file.stat().st_size
        print(f"{file.name} - {size} bytes")