from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent

SOURCE_DIR = (
    PROJECT_DIR
    / "Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025"
    / "raw_dataset"
)

OUTPUT_DIR = PROJECT_DIR / "data" / "pilot" / "2023-01"

# Membuat folder tujuan jika belum tersedia.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

start_date = pd.Timestamp("2023-01-01")
end_date = pd.Timestamp("2023-02-01")

for filename in ["sales_raw.csv", "stock_raw.csv"]:
    print(f"\nMEMPROSES: {filename}")

    data = pd.read_csv(
        SOURCE_DIR / filename,
        sep=None,
        engine="python",
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
    )

    # Tanggal hasil parsing hanya untuk memilih baris.
    # Kolom DateTime asli tetap dipertahankan.
    parsed_dates = pd.to_datetime(
        data["DateTime"].str.strip(),
        format="%d %b %Y %H:%M:%S",
        errors="raise",
    )

    # Mulai 1 Januari, sebelum 1 Februari.
    selected = (
        (parsed_dates >= start_date)
        & (parsed_dates < end_date)
    )

    pilot = data.loc[selected].copy()

    if pilot.empty:
        raise ValueError(f"Tidak ditemukan data Januari 2023: {filename}")

    output_path = OUTPUT_DIR / filename

    pilot.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"Jumlah baris sumber: {len(data):,}")
    print(f"Jumlah baris Januari 2023: {len(pilot):,}")
    print(f"Jumlah kolom: {len(pilot.columns)}")
    print(f"Disimpan ke: {output_path}")

    del data, pilot, parsed_dates