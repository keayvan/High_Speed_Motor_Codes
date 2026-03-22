# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 13:52:32 2026

@author: kkeramati
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd



def convert_csv_to_parquet(csv_path: Path, parquet_path: Path, chunksize: int = 250_000) -> Path:
    """
    Robust CSV -> Parquet conversion using pandas.

    - Reads CSV in chunks (memory-safe)
    - Parses first column as datetime UTC (best-effort)
    - Converts all other columns to float32 (best-effort, invalid -> NaN)
    - Writes to a single Parquet file (via pyarrow)

    Requirements:
      pip install pyarrow
    """
    csv_path = Path(csv_path)
    parquet_path = Path(parquet_path)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)

    # We'll stream chunks and accumulate to parquet using pyarrow
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except Exception as e:
        raise ImportError(
            "Missing dependency 'pyarrow'. Install it with: pip install pyarrow"
        ) from e

    writer = None

    for chunk in pd.read_csv(csv_path, chunksize=chunksize, low_memory=False):
        # parse time column (assume first col)
        time_col = chunk.columns[0]
        chunk[time_col] = pd.to_datetime(chunk[time_col], utc=True, errors="coerce")

        # numeric conversion for other columns
        for c in chunk.columns[1:]:
            chunk[c] = pd.to_numeric(chunk[c], errors="coerce").astype("float32")

        table = pa.Table.from_pandas(chunk, preserve_index=False)

        if writer is None:
            writer = pq.ParquetWriter(parquet_path, table.schema, compression="snappy")
        writer.write_table(table)

    if writer is not None:
        writer.close()
    else:
        raise ValueError(f"No data read from CSV: {csv_path}")

    return parquet_path


def read_parquet(parquet_path: Path) -> pd.DataFrame:
    """Fast Parquet reader (pandas)."""
    return pd.read_parquet(parquet_path)
