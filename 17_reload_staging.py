from datetime import date

from sqlalchemy import MetaData, Table, delete, func, select, text

from src.db import PROJECT_DIR, create_db_engine

# Runner ini khusus pilot Januari 2023.
PERIOD_DATE = date(2023, 1, 1)
PERIOD_TEXT = PERIOD_DATE.strftime("%Y-%m")

# Menggunakan kembali SQL transformasi yang sudah diuji.
jobs = [
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

engine = create_db_engine()
results = []

try:
    with engine.begin() as connection:
        metadata = MetaData()

        for job in jobs:
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

            raw_filter = (
                (raw_table.c.source_file == job["source_file"])
                & (raw_table.c.source_period == PERIOD_TEXT)
            )

            staging_filter = (
                (staging_table.c.source_file == job["source_file"])
                & (staging_table.c.source_period == PERIOD_DATE)
            )

            source_rows = connection.execute(
                select(func.count())
                .select_from(raw_table)
                .where(raw_filter)
            ).scalar_one()

            if source_rows == 0:
                raise ValueError(
                    f"Sumber raw kosong untuk {job['table']}. "
                    "Pemuatan dibatalkan."
                )

            count_query = (
                select(func.count())
                .select_from(staging_table)
                .where(staging_filter)
            )

            rows_before = connection.execute(count_query).scalar_one()

            sql_path = PROJECT_DIR / "sql" / job["sql_file"]
            sql_statement = sql_path.read_text(encoding="utf-8-sig")

            connection.execute(
                delete(staging_table).where(staging_filter)
            )

            connection.execute(text(sql_statement))

            rows_after = connection.execute(count_query).scalar_one()

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

    # Ditampilkan setelah seluruh transaksi berhasil.
    print("\nPEMUATAN ULANG STAGING BERHASIL")

    for result in results:
        print(f"\nTabel: staging.{result['table']}")
        print(f"Baris sumber raw: {result['source_rows']:,}")
        print(f"Baris batch sebelum: {result['rows_before']:,}")
        print(f"Baris batch sesudah: {result['rows_after']:,}")

finally:
    engine.dispose()