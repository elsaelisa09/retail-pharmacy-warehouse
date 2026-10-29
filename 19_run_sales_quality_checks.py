from datetime import date
from uuid import uuid4

from sqlalchemy import text

from src.db import PROJECT_DIR, create_db_engine

SOURCE_PERIOD = date(2023, 1, 1)

EXPECTED_FIELDS = [
    "quantity",
    "unit_price",
    "discount_amount",
    "service_fee",
    "packaging_fee",
    "subtotal",
    "additional_fee",
    "total_price",
]


def read_sql(filename):
    return (
        PROJECT_DIR / "sql" / filename
    ).read_text(encoding="utf-8-sig")


engine = create_db_engine()
run_id = uuid4()

try:
    with engine.begin() as connection:
        # Memakai kembali pemeriksaan identitas baris.
        coverage_results = connection.execute(
            text(read_sql("05_reconcile_row_keys.sql"))
        ).mappings().all()

        sales_coverage = next(
            (
                row for row in coverage_results
                if row["dataset"] == "sales"
            ),
            {
                "raw_rows": 0,
                "missing_in_staging": 0,
                "extra_in_staging": 0,
            },
        )

        records = [{
            "run_id": run_id,
            "source_period": SOURCE_PERIOD,
            "check_name": "sales_raw_staging_row_coverage",
            "checked_rows": (
                sales_coverage["raw_rows"]
                + sales_coverage["extra_in_staging"]
            ),
            "issue_rows": (
                sales_coverage["missing_in_staging"]
                + sales_coverage["extra_in_staging"]
            ),
            "details": (
                "Memeriksa baris yang hilang atau tambahan "
                "antara raw dan staging penjualan."
            ),
        }]

        # Memakai kembali pemeriksaan nilai per baris.
        value_results = connection.execute(
            text(read_sql("06_reconcile_sales_values.sql"))
        ).mappings().all()

        values_by_field = {
            row["field_name"]: row
            for row in value_results
        }

        for field in EXPECTED_FIELDS:
            result = values_by_field.get(
                field,
                {
                    "checked_rows": 0,
                    "mismatched_rows": 0,
                },
            )

            records.append({
                "run_id": run_id,
                "source_period": SOURCE_PERIOD,
                "check_name": f"sales_raw_staging_{field}",
                "checked_rows": result["checked_rows"],
                "issue_rows": result["mismatched_rows"],
                "details": (
                    f"Membandingkan nilai {field} "
                    "antara raw dan staging."
                ),
            })

        connection.execute(
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
            """),
            records,
        )

        results = connection.execute(
            text("""
                SELECT
                    check_name,
                    checked_rows,
                    issue_rows,
                    status
                FROM audit.data_quality_results
                WHERE run_id = :run_id
                ORDER BY check_name
            """),
            {"run_id": run_id},
        ).mappings().all()

    # Hasil audit sudah tersimpan sebelum status dievaluasi.
    print(f"\nRun ID audit penjualan: {run_id}")

    for row in results:
        print(
            f"{row['check_name']}: {row['status']} "
            f"| diperiksa={row['checked_rows']:,} "
            f"| temuan={row['issue_rows']:,}"
        )

    if any(row["status"] != "PASS" for row in results):
        print("\nAUDIT PENJUALAN PERLU DITINJAU.")
        raise SystemExit(1)

    print("\nAUDIT PENJUALAN BERHASIL: seluruh pemeriksaan PASS.")

finally:
    engine.dispose()