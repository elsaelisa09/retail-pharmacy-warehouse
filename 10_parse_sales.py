from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
FILE_PATH = PROJECT_DIR / "data" / "pilot" / "2023-01" / "sales_raw.csv"

sales = pd.read_csv(
    FILE_PATH,
    encoding="utf-8-sig",
    dtype=str,
    keep_default_na=False,
)

# Menyimpan pasangan nama kolom asli dan hasil konversinya.
converted_columns = {}

# 1. Jumlah barang: mempertahankan titik sebagai desimal.
values = sales["Quantity"].str.strip()
valid = values.str.fullmatch(r"[+-]?\d+(?:\.\d+)?")

sales["QuantityParsed"] = pd.to_numeric(
    values.where(valid),
    errors="coerce",
).astype("Float64")

converted_columns["Quantity"] = "QuantityParsed"

# 2. Nominal uang: menerima bilangan bulat tanpa pemisah.
# Format lain dilaporkan, bukan langsung ditebak.
money_columns = [
    "UnitPrice",
    "DiscountAmount",
    "ServiceFee",
    "PackagingFee",
    "Subtotal",
    "AdditionalFee",
    "TotalPrice",
]

for column in money_columns:
    values = sales[column].str.strip()
    valid = values.str.fullmatch(r"[+-]?\d+")

    target = f"{column}Parsed"

    sales[target] = pd.to_numeric(
        values.where(valid),
        errors="coerce",
    ).astype("Int64")

    converted_columns[column] = target

# 3. Persentase: koma desimal dan tanda persen.
percent_columns = {
    "DiscountPct": "DiscountPctParsed",
    "InvoiceDiscountPct": "InvoiceDiscountPctParsed",
    "PromoDiscountPct": "PromoDiscountPctParsed",
    "TaxAmount": "TaxRatePctParsed",
}

for column, target in percent_columns.items():
    values = sales[column].str.strip()
    valid = values.str.fullmatch(r"[+-]?\d+(?:,\d+)?\s*%")

    normalized = (
        values.where(valid)
        .str.replace("%", "", regex=False)
        .str.strip()
        .str.replace(",", ".", regex=False)
    )

    sales[target] = pd.to_numeric(
        normalized,
        errors="coerce",
    ).astype("Float64")

    converted_columns[column] = target

# Melaporkan hasil seluruh konversi.
print(f"Jumlah baris penjualan: {len(sales):,}")

for original, converted in converted_columns.items():
    unreadable = sales[converted].isna()

    print(f"\n{original}: {unreadable.sum():,} nilai belum terbaca")

    if unreadable.any():
        print(
            sales.loc[unreadable, original]
            .value_counts()
            .head(5)
            .to_string()
        )

print("\nCONTOH KONVERSI JUMLAH DAN HARGA:")
print(
    sales[
        [
            "Quantity",
            "QuantityParsed",
            "UnitPrice",
            "UnitPriceParsed",
            "TotalPrice",
            "TotalPriceParsed",
        ]
    ].head(5).to_string(index=False)
)

print("\nCONTOH KONVERSI PERSENTASE:")
print(
    sales[
        ["DiscountPct", "DiscountPctParsed"]
    ].drop_duplicates().head(8).to_string(index=False)
)

# Memastikan data tersedia dan seluruh konversi berhasil.
parsed_columns = list(converted_columns.values())

if sales.empty:
    raise ValueError("Data penjualan kosong. Penyimpanan dibatalkan.")

if sales[parsed_columns].isna().any().any():
    raise ValueError(
        "Masih ada angka yang belum terbaca. Penyimpanan dibatalkan."
    )

# Menyimpan informasi asal data.
# RowNumber dan seluruh kolom asli tetap dipertahankan.
sales["SourceFile"] = "sales_raw.csv"

output_dir = PROJECT_DIR / "data" / "staging" / "2023-01"
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "sales_staging.csv"

sales.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig",
)

print("\nHASIL STAGING PENJUALAN BERHASIL DISIMPAN")
print(f"Lokasi: {output_path}")
print(f"Jumlah baris: {len(sales):,}")
print(f"Jumlah kolom: {len(sales.columns)}")