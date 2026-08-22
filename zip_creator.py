
import zipfile
from pathlib import Path

input_folder = Path("input")
zip_file = Path("payload.zip")

with zipfile.ZipFile(zip_file, "w") as zipf:
    for file in input_folder.iterdir():
        if file.is_file():
            zipf.write(file, arcname=file.name)

print(f"ZIP created: {zip_file}")