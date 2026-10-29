from pathlib import Path
from getpass import getpass
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, Text
from sqlalchemy.engine import URL

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

# Mengambil data pilot dengan nilai asli.
file_path = (
    PROJECT_DIR
    / "data"
    / "pilot"
    / "2023-01"
    / "stock_raw.csv"
)

stock = pd.read_csv(
    file_path,
    encoding="utf-8-sig",
    dtype=str,
    keep_default_na=False,
)

if stock.empty:
    raise ValueError("Data stok kosong. Pemuatan dibatalkan.")

# Metadata untuk menelusuri asal dan periode data.
stock["source_file"] = "stock_raw.csv"
stock["source_period"] = "2023-01"

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
    # Pembuatan tabel, pemuatan, dan pemeriksaan dalam satu transaksi.
    with engine.begin() as connection:
        stock.to_sql(
            name="stock_movements",
            con=connection,
            schema="raw",
            if_exists="fail",
            index=False,
            dtype={column: Text() for column in stock.columns},
            chunksize=1000,
        )

        database_rows = connection.execute(
            text("SELECT COUNT(*) FROM raw.stock_movements")
        ).scalar_one()

        # Jika jumlah berbeda, transaksi dibatalkan.
        if database_rows != len(stock):
            raise ValueError(
                f"Jumlah baris berbeda: CSV={len(stock)}, "
                f"database={database_rows}"
            )

    print("\nPEMUATAN DATA STOK BERHASIL")
    print("Tabel: raw.stock_movements")
    print(f"Jumlah baris CSV: {len(stock):,}")
    print(f"Jumlah baris database: {database_rows:,}")
    print(f"Jumlah kolom: {len(stock.columns)}")

finally:
    engine.dispose()