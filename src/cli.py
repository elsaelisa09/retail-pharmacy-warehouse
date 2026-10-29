import argparse
import re
from datetime import datetime


def validate_period(value):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}", value):
        raise argparse.ArgumentTypeError(
            "Gunakan format YYYY-MM, misalnya 2023-02."
        )

    try:
        datetime.strptime(value, "%Y-%m")
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Periode tidak valid. Gunakan tahun dan bulan yang benar."
        ) from None

    return value


def get_source_period(description):
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "--period",
        type=validate_period,
        default="2023-01",
        help="Periode dalam format YYYY-MM. Default: 2023-01.",
    )

    args = parser.parse_args()
    return args.period