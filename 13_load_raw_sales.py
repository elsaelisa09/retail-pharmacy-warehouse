from pathlib import Path
from getpass import getpass
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, Text
from sqlalchemy.engine import URL

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

file_path = (
    PROJECT_DIR
    / "data"
    / "pilot"
    / "2023-01"
    / "sales_raw.csv"
)

# Mempertahankan nilai sumber sebagai teks.
sales = pd.read_csv(
    file_path,
    encoding="utf-8-sig",
    dtype=str,
    keep_default_na=False,
)

if sales.empty:
    raise ValueError("Data penjualan kosong. Pemuatan dibatalkan.")

sales["source_file"] = "sales_raw.csv"
sales["source_period"] = "2023-01"

password = getpass("Masukkan password PostgreSQL: ")

connection_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=password,
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)

engine = create_engine(connection_url)

try:
    with engine.begin() as connection:
        sales.to_sql(
            name="sales_transactions",
            con=connection,
            schema="raw",
            if_exists="fail",
            index=False,
            dtype={column: Text() for column in sales.columns},
            chunksize=1000,
        )

        database_rows = connection.execute(
            text("SELECT COUNT(*) FROM raw.sales_transactions")
        ).scalar_one()

        if database_rows != len(sales):
            raise ValueError(
                f"Jumlah baris berbeda: CSV={len(sales)}, "
                f"database={database_rows}"
            )

    print("\nPEMUATAN DATA PENJUALAN BERHASIL")
    print("Tabel: raw.sales_transactions")
    print(f"Jumlah baris CSV: {len(sales):,}")
    print(f"Jumlah baris database: {database_rows:,}")
    print(f"Jumlah kolom: {len(sales.columns)}")

finally:
    engine.dispose()