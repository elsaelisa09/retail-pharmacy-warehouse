from pathlib import Path
from getpass import getpass
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

PROJECT_DIR = Path(__file__).resolve().parent

# Membaca konfigurasi dari folder proyek.
load_dotenv(PROJECT_DIR / ".env")

# Password tidak ditampilkan saat diketik.
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
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        ).one()

        print("\nKONEKSI PYTHON BERHASIL")
        print(f"Database: {result[0]}")
        print(f"User: {result[1]}")
finally:
    engine.dispose()