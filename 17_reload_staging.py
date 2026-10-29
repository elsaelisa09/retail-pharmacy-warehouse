from datetime import date

from sqlalchemy import MetaData, Table, delete, func, select, text

from src.cli import get_source_period
from src.db import PROJECT_DIR, create_db_engine


JOBS = [
    {
        "table": "stock_movements",
        "source_file": "stock_raw.csv",
        "sql_file": "02_load_staging_stock.sql",
    },
    {
        "table": "sales_transactions",
        "source_file": "sales_raw.csv",
        "sql_file": "04_load_staging_sales.sql",
    },
]


def main():
    period_text = get_source_period(
        "Memuat ulang satu bulan data raw ke staging."
    )
    period_date = date.fromisoformat(f"{period_text}-01")

    engine = create_db_engine()
    results = []

    try:
        with engine.begin() as connection:
            metadata = MetaData()

            for job in JOBS:
                raw_table = Table(
                    job["table"],
                    metadata,
                    schema="raw",
                    autoload_with=connection,
                )

                staging_table = Table(
                    job["table"],
                    metadata,
                    schema="staging",
                    autoload_with=connection,
                )

                # Periode pada raw disimpan sebagai teks YYYY-MM.
                raw_filter = (
                    (raw_table.c.source_file == job["source_file"])
                    & (raw_table.c.source_period == period_text)
                )

                # Periode pada staging disimpan sebagai DATE.
                staging_filter = (
                    (staging_table.c.source_file == job["source_file"])
                    & (staging_table.c.source_period == period_date)
                )

                source_rows = connection.execute(
                    select(func.count())
                    .select_from(raw_table)
                    .where(raw_filter)
                ).scalar_one()

                if source_rows == 0:
                    raise ValueError(
                        f"Sumber raw kosong untuk {job['table']} "
                        f"periode {period_text}. Pemuatan dibatalkan."
                    )

                count_query = (
                    select(func.count())
                    .select_from(staging_table)
                    .where(staging_filter)
                )

                rows_before = connection.execute(
                    count_query
                ).scalar_one()

                sql_path = PROJECT_DIR / "sql" / job["sql_file"]
                sql_statement = sql_path.read_text(
                    encoding="utf-8-sig"
                )

                # Hanya mengganti batch file dan bulan yang dipilih.
                connection.execute(
                    delete(staging_table).where(staging_filter)
                )

                connection.execute(
                    text(sql_statement),
                    {"source_period": period_text},
                )

                rows_after = connection.execute(
                    count_query
                ).scalar_one()

                if rows_after != source_rows:
                    raise ValueError(
                        f"Jumlah baris {job['table']} berbeda: "
                        f"raw={source_rows}, staging={rows_after}"
                    )

                results.append({
                    "table": job["table"],
                    "source_rows": source_rows,
                    "rows_before": rows_before,
                    "rows_after": rows_after,
                })

        # Ditampilkan setelah kedua pemuatan berhasil di-commit.
        print("\nPEMUATAN ULANG STAGING BERHASIL")
        print(f"Periode: {period_text}")

        for result in results:
            print(f"\nTabel: staging.{result['table']}")
            print(f"Baris sumber raw: {result['source_rows']:,}")
            print(f"Baris batch sebelum: {result['rows_before']:,}")
            print(f"Baris batch sesudah: {result['rows_after']:,}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()