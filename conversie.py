# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 12:38:18 2025

@author: razva
"""

import pandas as pd

def main():
    # Calea către fișierul Parquet inițial
    input_path = "C:\\Users\\razva\\Desktop\\Challenge veridion\\veridion_entity_resolution_challenge.snappy.parquet"
    output_path = "C:\\Users\\razva\\Desktop\\Challenge veridion\\veridion_entity_resolution_challenge.xlsx"

    print(f"Loading Parquet file: {input_path}")

    # Citește fișierul Parquet
    df = pd.read_parquet(input_path, engine="pyarrow")  # sau "fastparquet"

    print(f"Dataset loaded with shape: {df.shape}")

    # Scrie direct în Excel
    df.to_excel(output_path, index=False, engine="openpyxl")

    print(f"✅ Excel file saved: {output_path}")

if __name__ == "__main__":
    main()
