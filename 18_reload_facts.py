from datetime import date

from sqlalchemy import MetaData, Table, delete, func, select, text

from src.db import PROJECT_DIR, create_db_engine

# Runner ini khusus pilot Januari 2023.
PERIOD_DATE = date(2023, 1, 1)

jobs = [
    {
        "staging_table": "stock_movements",
        "fact_table": "fact_stock_movements",
        "source_file": "stock_raw.csv",
        "sql_file": "14_load_fact_stock.sql",
    },
    {
        "staging_table": "sales_transactions",
        "fact_table": "fact_sales",
        "source_file": "sales_raw.csv",
        "sql_file": "12_load_fact_sales.sql",
    },
]

engine = create_db_engine()
results = []

try:
    with engine.begin() as connection:
        metadata = MetaData()

        for job in jobs:
            staging_table = Table(
                job["staging_table"],
                metadata,
                schema="staging",
                autoload_with=connection,
            )

            fact_table = Table(
                job["fact_table"],
                metadata,
                schema="warehouse",
                autoload_with=connection,
            )

            staging_filter = (
                (staging_table.c.source_file == job["source_file"])
                & (staging_table.c.source_period == PERIOD_DATE)
            )

            fact_filter = (
                (fact_table.c.source_file == job["source_file"])
                & (fact_table.c.source_period == PERIOD_DATE)
            )

            source_rows = connection.execute(
                select(func.count())
                .select_from(staging_table)
                .where(staging_filter)
            ).scalar_one()

            if source_rows == 0:
                raise ValueError(
                    f"Staging kosong untuk {job['fact_table']}. "
                    "Pemuatan dibatalkan."
                )

            count_query = (
                select(func.count())
                .select_from(fact_table)
                .where(fact_filter)
            )

            rows_before = connection.execute(count_query).scalar_one()

            sql_path = PROJECT_DIR / "sql" / job["sql_file"]
            sql_statement = sql_path.read_text(encoding="utf-8-sig")

            connection.execute(
                delete(fact_table).where(fact_filter)
            )

            connection.execute(text(sql_statement))

            rows_after = connection.execute(count_query).scalar_one()

            if rows_after != source_rows:
                raise ValueError(
                    f"Jumlah baris {job['fact_table']} berbeda: "
                    f"staging={source_rows}, fakta={rows_after}"
                )

            results.append({
                "table": job["fact_table"],
                "source_rows": source_rows,
                "rows_before": rows_before,
                "rows_after": rows_after,
            })

    # Pesan berhasil ditampilkan setelah kedua pemuatan di-commit.
    print("\nPEMUATAN ULANG FAKTA BERHASIL")

    for result in results:
        print(f"\nTabel: warehouse.{result['table']}")
        print(f"Baris sumber staging: {result['source_rows']:,}")
        print(f"Baris batch sebelum: {result['rows_before']:,}")
        print(f"Baris batch sesudah: {result['rows_after']:,}")

finally:
    engine.dispose()