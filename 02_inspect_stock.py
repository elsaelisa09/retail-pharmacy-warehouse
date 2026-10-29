from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent

file_path = (
    PROJECT_DIR
    / "Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025"
    / "raw_dataset"
    / "stock_raw.csv"
)

# Membaca lima baris tanpa mengubah format nilai aslinya.
stock = pd.read_csv(
    file_path,
    sep=None,
    engine="python",
    encoding="utf-8-sig",
    dtype=str,
    keep_default_na=False,
    nrows=5,
)

print("JUMLAH KOLOM:", len(stock.columns))

print("\nDAFTAR KOLOM:")
for number, column in enumerate(stock.columns, start=1):
    print(f"{number}. {column}")

# Kolom yang membantu memahami pergerakan stok.
preview_columns = [
    "DrugCode",
    "TransactionDescription",
    "InitialStock",
    "StockIn",
    "StockOut",
    "RemainingStock",
]

print("\nLIMA BARIS CONTOH PERGERAKAN STOK:")
print(stock[preview_columns].to_string(index=False))