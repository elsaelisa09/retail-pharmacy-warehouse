import argparse
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent

SOURCE_DIR = (
    PROJECT_DIR
    / "Retail Pharmacy Sales and Stock Dataset in Indonesia, 2023-2025"
    / "raw_dataset"
)


def validate_period(value):
    """Memastikan periode menggunakan format YYYY-MM yang valid."""
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}", value):
        raise argparse.ArgumentTypeError(
            "Gunakan format YYYY-MM, misalnya 2023-02."
        )

    try:
        datetime.strptime(value, "%Y-%m")
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Periode tidak valid. Gunakan tahun dan bulan yang benar."
        ) from None

    return value


def main():
    parser = argparse.ArgumentParser(
        description="Membuat CSV pilot penjualan dan stok untuk satu bulan."
    )

    parser.add_argument(
        "--period",
        type=validate_period,
        default="2023-01",
        help="Bulan yang diproses dalam format YYYY-MM. Default: 2023-01.",
    )

    args = parser.parse_args()
    period = args.period

    start_date = pd.Timestamp(f"{period}-01")
    end_date = start_date + pd.DateOffset(months=1)

    output_dir = PROJECT_DIR / "data" / "pilot" / period

    print(f"MEMBUAT PILOT PERIODE: {period}")
    print(f"Rentang: {start_date.date()} sampai sebelum {end_date.date()}")

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

        # Tanggal hasil parsing hanya digunakan untuk memilih baris.
        # Nilai DateTime asli tetap dipertahankan.
        parsed_dates = pd.to_datetime(
            data["DateTime"].str.strip(),
            format="%d %b %Y %H:%M:%S",
            errors="raise",
        )

        selected = (
            (parsed_dates >= start_date)
            & (parsed_dates < end_date)
        )

        pilot = data.loc[selected].copy()

        if pilot.empty:
            raise ValueError(
                f"Tidak ditemukan data periode {period}: {filename}"
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename

        pilot.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig",
        )

        print(f"Jumlah baris sumber: {len(data):,}")
        print(f"Jumlah baris periode {period}: {len(pilot):,}")
        print(f"Jumlah kolom: {len(pilot.columns)}")
        print(f"Disimpan ke: {output_path}")

        del data, pilot, parsed_dates

    print(f"\nPEMBUATAN PILOT {period} SELESAI.")


if __name__ == "__main__":
    main()