import os
import subprocess
import sys
from datetime import date
from getpass import getpass

from sqlalchemy import text

from src.db import PROJECT_DIR, create_db_engine
from src.cli import get_source_period



STEPS = [
    ("Memuat ulang raw stok", "15_reload_raw_stock.py"),
    ("Memuat ulang raw penjualan", "16_reload_raw_sales.py"),
    ("Memuat ulang staging", "17_reload_staging.py"),
    ("Menjalankan audit penjualan raw ke staging", "19_run_sales_quality_checks.py"),
    ("Memperbarui dimensi produk", "20_refresh_product_dimension.py"),
    ("Memuat ulang fakta", "18_reload_facts.py"),
    ("Memeriksa penjualan staging ke fakta", "21_run_sales_fact_quality_checks.py"),
    ("Menjalankan audit stok", "14_run_stock_quality_checks.py"),
]



def finish_run(
    engine,
    pipeline_run_id,
    status,
    failed_step=None,
    error_message=None,
):
    with engine.begin() as connection:
        result = connection.execute(
            text("""
                UPDATE audit.pipeline_runs
                SET status = :status,
                    finished_at = clock_timestamp(),
                    failed_step = :failed_step,
                    error_message = :error_message
                WHERE pipeline_run_id = :pipeline_run_id
            """),
            {
                "pipeline_run_id": pipeline_run_id,
                "status": status,
                "failed_step": failed_step,
                "error_message": error_message,
            },
        )

        if result.rowcount != 1:
            raise RuntimeError("Catatan eksekusi pipeline tidak ditemukan.")


def main():

    period_text = get_source_period(
        "Menjalankan pipeline pharmacy warehouse untuk satu bulan."
    )
    period_date = date.fromisoformat(f"{period_text}-01")

    child_env = os.environ.copy()

    if "DB_PASSWORD" not in child_env:
        child_env["DB_PASSWORD"] = getpass(
            "Masukkan password PostgreSQL: "
        )

    engine = create_db_engine(password=child_env["DB_PASSWORD"])
    pipeline_run_id = None
    current_step = "initialization"

    try:
        # Catatan RUNNING disimpan sebelum menjalankan tahap pipeline.
        with engine.begin() as connection:
            pipeline_run_id = connection.execute(
                text("""
                    INSERT INTO audit.pipeline_runs (
                        pipeline_name,
                        source_period
                    )
                    VALUES (:pipeline_name, :source_period)
                    RETURNING pipeline_run_id
                """),
                {
                    "pipeline_name": "retail_pharmacy_pilot",
                    "source_period": period_date,
                },
            ).scalar_one()

        print(
            f"\nPIPELINE PHARMACY WAREHOUSE — PERIODE {period_text}",
            flush=True,
        )
        print(f"Pipeline Run ID: {pipeline_run_id}", flush=True)

        for number, (description, filename) in enumerate(STEPS, start=1):
            current_step = filename

            print(
                f"\n[{number}/{len(STEPS)}] {description}",
                flush=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_DIR / filename),
                    "--period",
                    period_text,
                ],
                cwd=str(PROJECT_DIR),
                env=child_env,
                check=True,
            )

        current_step = "finalize_run"

        finish_run(
            engine,
            pipeline_run_id,
            status="SUCCESS",
        )

        print(
            "\nPIPELINE PILOT BERHASIL: status SUCCESS tersimpan.",
            flush=True,
        )
        return 0

    except (Exception, KeyboardInterrupt) as error:
        message = (
            "Dihentikan oleh pengguna."
            if isinstance(error, KeyboardInterrupt)
            else f"{type(error).__name__}: {error}"
        )

        if pipeline_run_id is not None:
            try:
                finish_run(
                    engine,
                    pipeline_run_id,
                    status="FAILED",
                    failed_step=current_step,
                    error_message=message,
                )
            except Exception as audit_error:
                print(
                    f"\nPencatatan kegagalan tidak berhasil: {audit_error}",
                    flush=True,
                )

        print(f"\nPIPELINE BERHENTI pada {current_step}.", flush=True)
        print(message, flush=True)
        return 1

    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())