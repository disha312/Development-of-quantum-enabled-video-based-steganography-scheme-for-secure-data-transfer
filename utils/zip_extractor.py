
import zipfile
from pathlib import Path

zip_file = Path("payload.zip")
output_folder = Path("output")

output_folder.mkdir(exist_ok=True)

with zipfile.ZipFile(zip_file, "r") as zipf:
    zipf.extractall(output_folder)

print(f"ZIP extracted to: {output_folder}")