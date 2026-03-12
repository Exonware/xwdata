"""Quick script to check 5GB file generation progress."""

import pathlib
import time
file_path = pathlib.Path("xwdata/examples/chatdb_bigfile/data/chatdb_5gb.xwjson")
data_file_path = pathlib.Path("xwdata/examples/chatdb_bigfile/data/chatdb_5gb.data.xwjson")
print("Checking 5GB file generation progress...")
print()
if file_path.exists():
    size_gb = file_path.stat().st_size / (1024 * 1024 * 1024)
    print(f"Main file exists: {file_path.name}")
    print(f"Size: {size_gb:.2f} GB ({size_gb / 5.0 * 100:.1f}% of 5GB)")
else:
    print("Main file not found yet")
if data_file_path.exists():
    size_gb = data_file_path.stat().st_size / (1024 * 1024 * 1024)
    print(f"Data file exists: {data_file_path.name}")
    print(f"Size: {size_gb:.2f} GB ({size_gb / 5.0 * 100:.1f}% of 5GB)")
else:
    print("Data file not found yet")
