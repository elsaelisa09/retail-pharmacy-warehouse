from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent

file_path = (
    PROJECT_DIR
    / "Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025"
    / "raw_dataset"
    / "sales_raw.csv"
)

# Hanya membaca kolom yang diperlukan.
columns = [
    "RowNumber",
    "InvoiceNumber",
    "DrugCode",
    "DrugName",
    "Quantity",
    "Unit",
    "UnitPrice",
    "Subtotal",
    "TotalPrice",
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

# Menghitung jumlah baris untuk setiap nomor faktur.
invoice_numbers = sales["InvoiceNumber"].str.strip()
rows_per_invoice = invoice_numbers.value_counts()

multiple_rows = rows_per_invoice[rows_per_invoice > 1]

print(f"Jumlah baris penjualan: {len(sales):,}")
print(f"Jumlah RowNumber unik: {sales['RowNumber'].nunique():,}")
print(f"Jumlah nomor faktur unik: {len(rows_per_invoice):,}")
print(f"Faktur dengan lebih dari satu baris: {len(multiple_rows):,}")
print(f"Jumlah baris terbanyak dalam satu faktur: {rows_per_invoice.max()}")

# Menampilkan satu contoh faktur dengan beberapa baris.
if not multiple_rows.empty:
    example_invoice = multiple_rows.index[0]

    example = sales.loc[
        invoice_numbers == example_invoice,
        columns,
    ]

    print(f"\nCONTOH FAKTUR: {example_invoice}")
    print(f"Jumlah seluruh baris faktur ini: {len(example)}")
    print("Ditampilkan maksimal 10 baris:\n")

    print(example.head(10).to_string(index=False))
else:
    print("\nSetiap nomor faktur hanya muncul pada satu baris.")