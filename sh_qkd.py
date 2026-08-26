import shutil
import os
from my_qkd import MyQKD
 
# --- 0. Anchor every path to this script's own folder ---
# This makes the script work no matter which directory you run it from.
script_dir = os.path.dirname(os.path.abspath(__file__))
 
# --- 1. Generate the quantum key (your existing code) ---
qkd = MyQKD(n_qubits=512)
result = qkd.generate_key()
aes_key = qkd.get_aes_key(result, key_size=256)
 
key_path = os.path.join(script_dir, "quantum_key.bin")
with open(key_path, "wb") as f:
    f.write(aes_key)
 
# --- 2. Use shutil to hand the key off to the shared project folder ---
shared_folder = os.path.join(script_dir, "shared_with_team", "keys")
os.makedirs(shared_folder, exist_ok=True)
 
shutil.copy2(key_path, os.path.join(shared_folder, "quantum_key.bin"))
print(f"Key copied to {shared_folder}\\quantum_key.bin for AES module")
 
# --- 3. Zip the confidential data folder before embedding (Section 5.2 of your synopsis) ---
data_folder = os.path.join(script_dir, "data_to_hide")
 
# Guard clause: fail with a clear message instead of a traceback
if not os.path.isdir(data_folder):
    raise FileNotFoundError(
        f"'{data_folder}' not found. "
        f"Create this folder (next to sh_qkd.py) and put the confidential files inside it before running."
    )
 
archive_base = os.path.join(script_dir, "confidential_payload")
shutil.make_archive(
    base_name=archive_base,   # creates confidential_payload.zip next to the script
    format="zip",
    root_dir=data_folder
)
print(f"✅ Zipped '{data_folder}' → {archive_base}.zip")
 
# --- 4. At the receiver side: unzip after extraction (Section 5.12) ---
archive_path = archive_base + ".zip"
recovered_dir = os.path.join(script_dir, "recovered_data")
 
shutil.unpack_archive(archive_path, extract_dir=recovered_dir)
print(f"ZIP extracted and original folder recovered to {recovered_dir}")
 
# --- 5. Clean up temp frame-extraction folders after stego video is built ---
temp_frames_dir = os.path.join(script_dir, "temp_video_frames")
if os.path.exists(temp_frames_dir):
    shutil.rmtree(temp_frames_dir)
    print("Temporary frame files cleaned up")
 
