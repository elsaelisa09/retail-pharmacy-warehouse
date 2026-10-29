from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
FILE_PATH = PROJECT_DIR / "data" / "pilot" / "2023-01" / "stock_raw.csv"

stock = pd.read_csv(
    FILE_PATH,
    encoding="utf-8-sig",
    dtype=str,
    keep_default_na=False,
)

columns = ["InitialStock", "StockIn", "StockOut", "RemainingStock"]

# Menerima bilangan bulat, termasuk negatif dan pemisah ribuan titik.
# Contoh: "199.271 Pcs" atau "-5 Tab".
pattern = r"^\s*([+-]?(?:\d{1,3}(?:\.\d{3})+|\d+))\s+(.+?)\s*$"

for column in columns:
    extracted = stock[column].str.extract(pattern)

    quantity = extracted[0].str.replace(".", "", regex=False)

    stock[f"{column}Qty"] = pd.to_numeric(
        quantity,
        errors="coerce",
    ).astype("Int64")

    stock[f"{column}Unit"] = extracted[1].str.strip()

    unreadable = stock[f"{column}Qty"].isna()

    print(f"{column}: {unreadable.sum():,} nilai belum terbaca")

    if unreadable.any():
        print(
            stock.loc[unreadable, column]
            .value_counts()
            .head(5)
            .to_string()
        )

# Memastikan keempat jumlah berhasil dibaca.
quantity_columns = [f"{column}Qty" for column in columns]
parsed_ok = stock[quantity_columns].notna().all(axis=1)

# Memastikan satuan pada empat kolom dalam satu baris sama.
unit_columns = [f"{column}Unit" for column in columns]
same_unit = stock[unit_columns].nunique(axis=1).eq(1)

eligible = parsed_ok & same_unit

print(f"\nJumlah baris: {len(stock):,}")
print(f"Baris dengan seluruh jumlah terbaca: {parsed_ok.sum():,}")
print(
    "Baris terbaca tetapi satuannya berbeda: "
    f"{(parsed_ok & ~same_unit).sum():,}"
)

# Memeriksa saldo hanya jika jumlah terbaca dan satuannya sama.
checked = stock.loc[eligible].copy()

calculated_balance = (
    checked["InitialStockQty"]
    + checked["StockInQty"]
    - checked["StockOutQty"]
)

balance_ok = calculated_balance.eq(checked["RemainingStockQty"])

print(f"\nBaris yang dapat diperiksa saldonya: {len(checked):,}")
print(f"Saldo sesuai: {balance_ok.sum():,}")
print(f"Saldo berbeda: {(~balance_ok).sum():,}")

print("\nCONTOH HASIL PEMISAHAN:")
print(
    stock[
        ["InitialStock", "InitialStockQty", "InitialStockUnit"]
    ].head(5).to_string(index=False)
)

if (~balance_ok).any():
    print("\nCONTOH BARIS DENGAN SALDO BERBEDA:")
    print(
        checked.loc[
            ~balance_ok,
            ["RowNumber"] + columns,
        ].head(5).to_string(index=False)
    )



    # Menyimpan hasil hanya jika seluruh pemeriksaan lulus.
if stock.empty:
    raise ValueError("Data stok kosong. Penyimpanan dibatalkan.")

if not (
    parsed_ok.all()
    and same_unit.all()
    and balance_ok.all()
):
    raise ValueError(
        "Masih ada pemeriksaan yang gagal. Penyimpanan dibatalkan."
    )

# Menambahkan satu kolom satuan bersama karena sudah terbukti konsisten.
stock["Unit"] = stock["InitialStockUnit"]

# Menyimpan informasi asal data.
# RowNumber dari sumber tetap dipertahankan.
stock["SourceFile"] = "stock_raw.csv"

output_dir = PROJECT_DIR / "data" / "staging" / "2023-01"
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "stock_staging.csv"

stock.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig",
)

print("\nHASIL STAGING BERHASIL DISIMPAN")
print(f"Lokasi: {output_path}")
print(f"Jumlah baris: {len(stock):,}")
print(f"Jumlah kolom: {len(stock.columns)}")