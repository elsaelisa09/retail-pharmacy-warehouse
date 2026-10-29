from sqlalchemy import text

from src.db import PROJECT_DIR, create_db_engine

sql_path = (
    PROJECT_DIR
    / "sql"
    / "21_run_stock_quality_checks.sql"
)

sql_statement = sql_path.read_text(encoding="utf-8-sig")

engine = create_db_engine()

try:
    print("\nMenjalankan pemeriksaan stok Januari 2023...")

    with engine.begin() as connection:
        results = connection.execute(
            text(sql_statement)
        ).mappings().all()

    # Hasil audit sudah tersimpan setelah transaksi selesai.
    if not results:
        raise RuntimeError("Pemeriksaan tidak mengembalikan hasil.")

    print(f"\nRun ID: {results[0]['run_id']}")

    for row in results:
        print(
            f"{row['check_name']}: {row['status']} "
            f"| diperiksa={row['checked_rows']:,} "
            f"| temuan={row['issue_rows']:,}"
        )

    unsuccessful = [
        row for row in results
        if row["status"] != "PASS"
    ]

    if unsuccessful:
        print("\nAUDIT PERLU DITINJAU. Hasil tersimpan di database.")
        raise SystemExit(1)

    print("\nAUDIT BERHASIL: seluruh pemeriksaan berstatus PASS.")

finally:
    engine.dispose()