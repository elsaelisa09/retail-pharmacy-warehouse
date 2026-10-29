from pathlib import Path

import pandas as pd
from sqlalchemy import MetaData, Table, delete, func, select


def reload_raw_batch(engine, file_path, table_name, source_period):
    file_path = Path(file_path)

    data = pd.read_csv(
        file_path,
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
    )

    # Pemeriksaan dilakukan sebelum mengganti data database.
    if data.empty:
        raise ValueError("File kosong. Pemuatan dibatalkan.")

    required_columns = {"RowNumber", "DateTime"}

    if not required_columns.issubset(data.columns):
        raise ValueError("Kolom RowNumber atau DateTime tidak ditemukan.")

    row_numbers = data["RowNumber"].str.strip()

    if row_numbers.eq("").any() or row_numbers.duplicated().any():
        raise ValueError("RowNumber kosong atau berulang dalam batch.")

    dates = pd.to_datetime(
        data["DateTime"].str.strip(),
        format="%d %b %Y %H:%M:%S",
        errors="raise",
    )

    if not dates.dt.strftime("%Y-%m").eq(source_period).all():
        raise ValueError("Ada tanggal di luar periode batch.")

    data["source_file"] = file_path.name
    data["source_period"] = source_period

    with engine.begin() as connection:
        # Membaca struktur tabel yang sudah tersedia.
        table = Table(
            table_name,
            MetaData(),
            schema="raw",
            autoload_with=connection,
        )

        if set(data.columns) != set(table.columns.keys()):
            raise ValueError("Kolom CSV berbeda dari struktur tabel raw.")

        batch_filter = (
            (table.c.source_file == file_path.name)
            & (table.c.source_period == source_period)
        )

        count_query = (
            select(func.count())
            .select_from(table)
            .where(batch_filter)
        )

        rows_before = connection.execute(count_query).scalar_one()

        # Mengganti batch yang sama dalam satu transaksi.
        connection.execute(
            delete(table).where(batch_filter)
        )

        data.to_sql(
            name=table_name,
            con=connection,
            schema="raw",
            if_exists="append",
            index=False,
            chunksize=1000,
        )

        rows_after = connection.execute(count_query).scalar_one()

        if rows_after != len(data):
            raise ValueError("Jumlah baris hasil pemuatan tidak sesuai CSV.")

    return {
        "csv_rows": len(data),
        "rows_before": rows_before,
        "rows_after": rows_after,
    }