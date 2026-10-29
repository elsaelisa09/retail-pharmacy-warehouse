from datetime import date

from sqlalchemy import text

from src.cli import get_source_period
from src.db import PROJECT_DIR, create_db_engine


def read_sql(filename):
    return (
        PROJECT_DIR / "sql" / filename
    ).read_text(encoding="utf-8-sig")


PERIOD_TEXT = get_source_period(
    "Memeriksa kualitas data stok untuk satu bulan."
)

PERIOD_DATE = date.fromisoformat(f"{PERIOD_TEXT}-01")
QUERY_PARAMS = {"period_date": PERIOD_DATE}

engine = create_db_engine()

try:
    print(f"\nMenjalankan pemeriksaan stok periode {PERIOD_TEXT}...")

    with engine.begin() as connection:
        # Membandingkan kunci dan nilai stok staging dengan fakta.
        reconciliation = connection.execute(
            text(read_sql("15_reconcile_stock_values.sql")),
            QUERY_PARAMS,
        ).mappings().one()

        # Menjalankan dan menyimpan tiga pemeriksaan stok yang sudah ada.
        results = connection.execute(
            text(read_sql("21_run_stock_quality_checks.sql")),
            QUERY_PARAMS,
        ).mappings().all()

        if not results:
            raise RuntimeError("Pemeriksaan tidak mengembalikan hasil.")

        run_id = results[0]["run_id"]

        # Mencatat rekonsiliasi menggunakan Run ID yang sama.
        reconciliation_result = connection.execute(
            text("""
                INSERT INTO audit.data_quality_results (
                    run_id,
                    source_period,
                    check_name,
                    checked_rows,
                    issue_rows,
                    details
                )
                VALUES (
                    :run_id,
                    :source_period,
                    :check_name,
                    :checked_rows,
                    :issue_rows,
                    :details
                )
                RETURNING
                    run_id,
                    check_name,
                    checked_rows,
                    issue_rows,
                    status
            """),
            {
                "run_id": run_id,
                "source_period": PERIOD_DATE,
                "check_name": "stock_staging_fact_reconciliation",
                "checked_rows": (
                    reconciliation["staging_rows"]
                    + reconciliation["extra_in_fact"]
                ),
                "issue_rows": (
                    reconciliation["missing_in_fact"]
                    + reconciliation["extra_in_fact"]
                    + reconciliation["mismatched_values"]
                ),
                "details": (
                    "Memeriksa kunci baris, jumlah stok, satuan, "
                    "waktu pergerakan, serta pemetaan produk dan tanggal "
                    "antara staging dan fakta."
                ),
            },
        ).mappings().one()

        results.append(reconciliation_result)

    # Seluruh hasil audit sudah tersimpan sebelum evaluasi status.
    print(f"\nRun ID: {run_id}")
    print(f"Periode: {PERIOD_TEXT}")

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