# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 14:34:53 2026

@author: kkeramati
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils_io import read_parquet

PARQUET_DIR = PROJECT_ROOT / "data" / "processed"

parquets = sorted(PARQUET_DIR.glob("*.parquet"))
if not parquets:
    raise FileNotFoundError(
        f"No Parquet files found in: {PARQUET_DIR}. Run scripts/01_convert_to_parquet.py first."
    )

df = read_parquet(parquets[0])
print("Loaded:", parquets[0].name)
print(df.head())
