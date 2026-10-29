CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year_number SMALLINT NOT NULL,
    quarter_number SMALLINT NOT NULL,
    month_number SMALLINT NOT NULL,
    day_of_month SMALLINT NOT NULL,
    iso_day_of_week SMALLINT NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

WITH calendar AS (
    SELECT
        DATE '2023-01-01' + day_offset AS calendar_date
    FROM generate_series(
        0,
        DATE '2025-12-31' - DATE '2023-01-01'
    ) AS g(day_offset)
)

INSERT INTO warehouse.dim_date (
    date_key,
    full_date,
    year_number,
    quarter_number,
    month_number,
    day_of_month,
    iso_day_of_week,
    is_weekend
)
SELECT
    to_char(calendar_date, 'YYYYMMDD')::INTEGER,
    calendar_date,
    EXTRACT(YEAR FROM calendar_date)::SMALLINT,
    EXTRACT(QUARTER FROM calendar_date)::SMALLINT,
    EXTRACT(MONTH FROM calendar_date)::SMALLINT,
    EXTRACT(DAY FROM calendar_date)::SMALLINT,
    EXTRACT(ISODOW FROM calendar_date)::SMALLINT,
    EXTRACT(ISODOW FROM calendar_date) IN (6, 7)
FROM calendar
ORDER BY calendar_date

ON CONFLICT (full_date) DO NOTHING;