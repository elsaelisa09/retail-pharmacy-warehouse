from datetime import date
from uuid import uuid4

from sqlalchemy import text

from src.cli import get_source_period
from src.db import create_db_engine


def main():
    period_text = get_source_period(
        "Memeriksa rekonsiliasi penjualan staging ke fakta."
    )
    period_date = date.fromisoformat(f"{period_text}-01")

    run_id = uuid4()
    engine = create_db_engine()

    try:
        with engine.begin() as connection:
            reconciliation = connection.execute(
                text("""
                    SELECT
                        staging_rows,
                        fact_rows,
                        missing_in_fact,
                        extra_in_fact,
                        mismatched_values
                    FROM audit.sales_fact_reconciliation
                    WHERE source_period = :period_date
                """),
                {"period_date": period_date},
            ).mappings().one_or_none()

            # Periode tanpa data tetap dicatat sebagai NO_DATA.
            if reconciliation is None:
                reconciliation = {
                    "staging_rows": 0,
                    "fact_rows": 0,
                    "missing_in_fact": 0,
                    "extra_in_fact": 0,
                    "mismatched_values": 0,
                }

            result = connection.execute(
                text("""
                    INSERT INTO audit.data_quality_results (
                        run_id,
                        source_period,
                        check_name,
                        checked_rows,
                        issue_rows,
                        warning_rows,
                        details
                    )
                    VALUES (
                        :run_id,
                        :source_period,
                        :check_name,
                        :checked_rows,
                        :issue_rows,
                        0,
                        :details
                    )
                    RETURNING
                        check_name,
                        checked_rows,
                        issue_rows,
                        status
                """),
                {
                    "run_id": run_id,
                    "source_period": period_date,
                    "check_name": "sales_staging_fact_reconciliation",
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
                        "Memeriksa cakupan kunci baris, nilai penjualan, "
                        "serta pemetaan produk dan tanggal "
                        "antara staging dan fakta."
                    ),
                },
            ).mappings().one()

        # Hasil audit sudah tersimpan sebelum evaluasi status.
        print(f"\nRun ID: {run_id}")
        print(f"Periode: {period_text}")
        print(f"Baris staging: {reconciliation['staging_rows']:,}")
        print(f"Baris fakta: {reconciliation['fact_rows']:,}")

        print(
            f"{result['check_name']}: {result['status']} "
            f"| diperiksa={result['checked_rows']:,} "
            f"| temuan={result['issue_rows']:,}"
        )

        if result["status"] != "PASS":
            print("\nAUDIT REKONSILIASI PENJUALAN PERLU DITINJAU.")
            return 1

        print("\nAUDIT REKONSILIASI PENJUALAN BERHASIL.")
        return 0

    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())