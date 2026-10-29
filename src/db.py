from pathlib import Path
from getpass import getpass
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

PROJECT_DIR = Path(__file__).resolve().parent.parent


def create_db_engine(password=None):
    load_dotenv(PROJECT_DIR / ".env")

    if password is None:
        password = os.getenv("DB_PASSWORD")

    if password is None:
        password = getpass("Masukkan password PostgreSQL: ")

    connection_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=password,
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    )

    return create_engine(connection_url)