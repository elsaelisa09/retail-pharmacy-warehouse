from sqlalchemy import text

from src.cli import get_source_period
from src.db import PROJECT_DIR, create_db_engine


PERIOD_TEXT = get_source_period(
    "Menambahkan kode produk staging yang belum tersedia di dimensi."
)

engine = create_db_engine()

try:
    with engine.begin() as connection:
        # MAX pada SQL dimensi hanya digunakan setelah memastikan
        # satu kode tidak memiliki beberapa nilai atribut nonkosong.
        conflicts = connection.execute(
            text("""
                WITH product_records AS (
                    SELECT drug_code, drug_name, category, drug_class
                    FROM staging.sales_transactions

                    UNION ALL

                    SELECT drug_code, drug_name, category, drug_class
                    FROM staging.stock_movements
                )
                SELECT drug_code
                FROM product_records
                GROUP BY drug_code
                HAVING
                    drug_code IS NULL
                    OR btrim(drug_code) = ''
                    OR COUNT(DISTINCT drug_name) > 1
                    OR COUNT(DISTINCT category) > 1
                    OR COUNT(DISTINCT drug_class) > 1
                ORDER BY drug_code
                LIMIT 10
            """)
        ).scalars().all()

        if conflicts:
            raise ValueError(
                "Kode produk kosong atau atribut produk tidak konsisten. "
                f"Contoh kode yang perlu ditinjau: {conflicts}"
            )

        rows_before = connection.execute(
            text("SELECT COUNT(*) FROM warehouse.dim_product")
        ).scalar_one()

        sql_path = PROJECT_DIR / "sql" / "08_build_dim_product.sql"
        sql_statement = sql_path.read_text(encoding="utf-8-sig")

        # File 08 saat ini berisi dua perintah:
        # CREATE TABLE, kemudian INSERT dengan CTE.
        create_statement, insert_statement = sql_statement.split(";", 1)

        connection.execute(text(create_statement))
        connection.execute(text(insert_statement))

        rows_after = connection.execute(
            text("SELECT COUNT(*) FROM warehouse.dim_product")
        ).scalar_one()

    print("\nPEMBARUAN DIMENSI PRODUK BERHASIL")
    print(f"Periode pipeline: {PERIOD_TEXT}")
    print("Cakupan dimensi: seluruh data staging yang tersedia")
    print(f"Produk sebelum: {rows_before:,}")
    print(f"Produk sesudah: {rows_after:,}")
    print(f"Produk ditambahkan: {rows_after - rows_before:,}")

finally:
    engine.dispose()