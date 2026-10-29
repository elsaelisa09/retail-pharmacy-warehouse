from pathlib import Path
import pandas as pd

# Lokasi folder proyek dan file penjualan.
PROJECT_DIR = Path(__file__).resolve().parent

file_path = (
    PROJECT_DIR
    / "Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025"
    / "raw_dataset"
    / "sales_raw.csv"
)

# Membaca lima baris sebagai teks untuk pemeriksaan awal.
sales = pd.read_csv(
    file_path,
    sep=None,
    engine="python",
    encoding="utf-8-sig",
    dtype=str,
    keep_default_na=False,
    nrows=5,
)

print("JUMLAH KOLOM:", len(sales.columns))

print("\nDAFTAR KOLOM:")
for number, column in enumerate(sales.columns, start=1):
    print(f"{number}. {column}")

print("\nLIMA BARIS CONTOH — ENAM KOLOM PERTAMA:")
print(sales.iloc[:, :6].to_string(index=False))