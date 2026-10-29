from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data" / "pilot" / "2023-01"

columns_to_check = {
    "sales_raw.csv": [
        "Quantity",
        "UnitPrice",
        "DiscountPct",
        "TaxAmount",
        "Subtotal",
        "TotalPrice",
    ],
    "stock_raw.csv": [
        "InitialStock",
        "StockIn",
        "StockOut",
        "RemainingStock",
    ],
}

for filename, columns in columns_to_check.items():
    print(f"\n{'=' * 50}")
    print(f"FILE: {filename}")

    # File pilot sebelumnya disimpan dengan pemisah koma.
    data = pd.read_csv(
        DATA_DIR / filename,
        sep=",",
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
        usecols=columns,
    )

    for column in columns:
        values = data[column]

        # Mengambil beberapa contoh nilai yang berbeda.
        examples = values.drop_duplicates().head(6).tolist()

        # Mencari contoh yang mengandung titik, koma, atau persen.
        special_values = values[
            values.str.contains(r"[.,%]", regex=True)
        ]

        special_examples = (
            special_values.drop_duplicates().head(6).tolist()
        )

        print(f"\nKOLOM: {column}")
        print(f"Contoh nilai asli: {examples}")

        if special_examples:
            print(f"Contoh dengan titik/koma/persen: {special_examples}")