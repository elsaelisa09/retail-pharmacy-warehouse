from src.cli import get_source_period
from src.db import PROJECT_DIR, create_db_engine
from src.raw_loader import reload_raw_batch


def main():
    period = get_source_period(
        "Memuat ulang satu bulan data raw pergerakan stok."
    )

    file_path = (
        PROJECT_DIR
        / "data"
        / "pilot"
        / period
        / "stock_raw.csv"
    )

    engine = create_db_engine()

    try:
        result = reload_raw_batch(
            engine=engine,
            file_path=file_path,
            table_name="stock_movements",
            source_period=period,
        )

        print("\nPEMUATAN ULANG RAW STOK BERHASIL")
        print(f"Periode: {period}")
        print(f"Jumlah baris CSV: {result['csv_rows']:,}")
        print(f"Baris batch sebelum: {result['rows_before']:,}")
        print(f"Baris batch sesudah: {result['rows_after']:,}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()