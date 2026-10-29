from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent

DATA_DIR = (
    PROJECT_DIR
    / "Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025"
    / "raw_dataset"
)

for filename in ["sales_raw.csv", "stock_raw.csv"]:
    print(f"\n{'=' * 50}")
    print(f"MEMERIKSA TANGGAL: {filename}")

    # Hanya membaca kolom tanggal agar lebih ringan.
    data = pd.read_csv(
        DATA_DIR / filename,
        sep=None,
        engine="python",
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
        usecols=["DateTime"],
    )

    # Format contoh: 02 Jan 2023 07:55:43
    parsed_dates = pd.to_datetime(
        data["DateTime"].str.strip(),
        format="%d %b %Y %H:%M:%S",
        errors="coerce",
    )

    unreadable = parsed_dates.isna()

    print(f"Jumlah baris: {len(data):,}")
    print(f"Tanggal berhasil dibaca: {parsed_dates.notna().sum():,}")
    print(f"Tanggal belum terbaca: {unreadable.sum():,}")
    print(f"Waktu paling awal: {parsed_dates.min()}")
    print(f"Waktu paling akhir: {parsed_dates.max()}")

    print("\nJUMLAH BARIS PER TAHUN:")

    year_counts = (
        parsed_dates.dropna()
        .dt.year.value_counts()
        .sort_index()
    )

    for year, count in year_counts.items():
        print(f"{year}: {count:,} baris")

    if unreadable.any():
        print("\nCONTOH TEKS TANGGAL YANG BELUM TERBACA:")

        print(
            data.loc[unreadable, "DateTime"]
            .value_counts()
            .head(10)
            .to_string()
        )

    del data