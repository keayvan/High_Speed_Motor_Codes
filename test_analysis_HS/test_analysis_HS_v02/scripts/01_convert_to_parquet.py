# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 13:51:16 2026

@author: kkeramati
"""
from pathlib import Path
import sys

# # project root = parent of scripts/
# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# sys.path.insert(0, str(PROJECT_ROOT))

# from utils_io import convert_csv_to_parquet

# RAW_DIR = PROJECT_ROOT / "data" / "raw" / "Salea"
# OUT_DIR = PROJECT_ROOT / "data" / "processed"
# OUT_DIR.mkdir(parents=True, exist_ok=True)

# print("PROJECT_ROOT:", PROJECT_ROOT)
# print("RAW_DIR:", RAW_DIR)

# csv_files = sorted(RAW_DIR.glob("*.csv"))
# if not csv_files:
#     raise FileNotFoundError(f"No CSV files found in: {RAW_DIR}")

# converted = 0
# skipped = 0

# for csv_path in csv_files:
#     parquet_path = OUT_DIR / (csv_path.stem + ".parquet")

#     # Skip if already converted AND parquet is newer than csv
#     if parquet_path.exists():
#         if parquet_path.stat().st_mtime >= csv_path.stat().st_mtime:
#             print("Skip (up-to-date):", csv_path.name)
#             skipped += 1
#             continue

#     print("Convert:", csv_path.name, "->", parquet_path.name)
#     convert_csv_to_parquet(csv_path, parquet_path)
#     converted += 1

# print(f"Done. Converted: {converted}, Skipped: {skipped}")


from pathlib import Path
import sys

# project root = parent of scripts/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils_io import convert_csv_to_parquet

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "Salea"
OUT_DIR = PROJECT_ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("PROJECT_ROOT:", PROJECT_ROOT)
print("RAW_DIR:", RAW_DIR)

# Find all CSVs recursively
csv_files = sorted(RAW_DIR.rglob("*.csv"))
if not csv_files:
    raise FileNotFoundError(f"No CSV files found under: {RAW_DIR}")

converted = 0
skipped = 0

for csv_path in csv_files:
    # Folder that contains the CSV
    parent_folder_name = csv_path.parent.name

    # Output file: processed/<folder_name>.parquet
    parquet_path = OUT_DIR / f"{parent_folder_name}.parquet"

    # Skip if already converted AND parquet is newer than csv
    if parquet_path.exists() and parquet_path.stat().st_mtime >= csv_path.stat().st_mtime:
        print("Skip (up-to-date):", csv_path.relative_to(RAW_DIR))
        skipped += 1
        continue

    print(
        "Convert:",
        csv_path.relative_to(RAW_DIR),
        "->",
        parquet_path.name
    )

    convert_csv_to_parquet(csv_path, parquet_path)
    converted += 1

print(f"Done. Converted: {converted}, Skipped: {skipped}")
