from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent

file_path = (
    PROJECT_DIR
    / "Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025"
    / "raw_dataset"
    / "sales_raw.csv"
)

columns = [
    "RowNumber",
    "DateTime",
    "InvoiceNumber",
    "DrugCode",
    "DrugName",
    "BatchAndExpiryDate",
    "Quantity",
    "Unit",
]

sales = pd.read_csv(
    file_path,
    sep=None,
    engine="python",
    encoding="utf-8-sig",
    dtype=str,
    keep_default_na=False,
    usecols=columns,
)

# Menyamakan spasi pada kolom yang sedang diperiksa.
# Perubahan hanya pada data di memori, bukan file CSV.
for column in ["InvoiceNumber", "DrugCode"]:
    sales[column] = sales[column].str.strip()

# Menghitung baris untuk setiap pasangan faktur dan produk.
pair_counts = sales.groupby(
    ["InvoiceNumber", "DrugCode"]
).size()

repeated_pairs = pair_counts[pair_counts > 1]

print(f"Jumlah pasangan faktur-produk: {len(pair_counts):,}")
print(f"Pasangan dengan beberapa baris: {len(repeated_pairs):,}")

if repeated_pairs.empty:
    print("\nSetiap pasangan faktur-produk hanya memiliki satu baris.")
else:
    # Mengambil satu contoh pasangan yang berulang.
    invoice, drug_code = repeated_pairs.index[0]

    example = sales[
        (sales["InvoiceNumber"] == invoice)
        & (sales["DrugCode"] == drug_code)
    ]

    print(f"\nCONTOH FAKTUR: {invoice}")
    print(f"KODE PRODUK: {drug_code}")
    print(f"Jumlah baris pasangan ini: {len(example)}")
    print("\nDitampilkan maksimal 10 baris:")

    print(example[columns].head(10).to_string(index=False))