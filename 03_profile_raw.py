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
    print(f"MEMERIKSA: {filename}")
    print("Sedang membaca seluruh data...")

    data = pd.read_csv(
        DATA_DIR / filename,
        sep=None,
        engine="python",
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
    )

    total_rows = len(data)

    print(f"Jumlah baris : {total_rows:,}")
    print(f"Jumlah kolom : {len(data.columns)}")

    # Menghitung nilai kosong atau yang hanya berisi spasi.
    empty_counts = data.apply(
        lambda column: column.fillna("").str.strip().eq("").sum()
    )

    summary = pd.DataFrame({
        "Kolom": empty_counts.index,
        "Jumlah_Kosong": empty_counts.values,
        "Persentase_Kosong": (
            empty_counts.values / total_rows * 100
        ).round(2),
    })

    # Menampilkan kolom yang memiliki nilai kosong saja.
    summary = summary[summary["Jumlah_Kosong"] > 0]

    print("\nKOLOM YANG MEMILIKI NILAI KOSONG:")

    if summary.empty:
        print("Tidak ditemukan nilai kosong.")
    else:
        print(summary.to_string(index=False))

    # Melepaskan data sebelum membaca file berikutnya.
    del data