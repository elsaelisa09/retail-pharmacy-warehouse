CREATE OR REPLACE VIEW audit.stock_continuity AS
SELECT
    f.stock_movement_key,
    f.source_file,
    f.source_period,
    f.source_row_number,
    f.product_key,
    f.warehouse,
    f.unit,
    f.movement_at,
    f.initial_stock,
    f.remaining_stock,

    LAG(f.remaining_stock) OVER movement_order
        AS previous_remaining_stock,

    COUNT(*) OVER (
        PARTITION BY
            f.product_key,
            f.warehouse,
            f.unit,
            f.movement_at
    ) AS same_timestamp_count

FROM warehouse.fact_stock_movements AS f

WINDOW movement_order AS (
    PARTITION BY
        f.product_key,
        f.warehouse,
        f.unit

    ORDER BY
        f.movement_at,
        f.source_file,
        f.source_period,
        f.source_row_number
);


-- Ringkasan pemeriksaan Januari 2023.

SELECT
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE previous_remaining_stock IS NULL
    ) AS first_records,

    COUNT(*) FILTER (
        WHERE previous_remaining_stock IS NOT NULL
    ) AS checked_links,

    COUNT(*) FILTER (
        WHERE previous_remaining_stock IS NOT NULL
          AND initial_stock <> previous_remaining_stock
    ) AS links_to_review,

    COUNT(*) FILTER (
        WHERE same_timestamp_count > 1
    ) AS same_time_records

FROM audit.stock_continuity
WHERE source_file = 'stock_raw.csv'
  AND source_period = DATE '2023-01-01';


-- Contoh hubungan saldo yang perlu ditinjau.

SELECT
    c.source_row_number,
    p.drug_code,
    c.unit,
    c.movement_at,
    c.previous_remaining_stock,
    c.initial_stock,
    c.initial_stock - c.previous_remaining_stock AS balance_gap,
    c.same_timestamp_count

FROM audit.stock_continuity AS c

JOIN warehouse.dim_product AS p
    ON p.product_key = c.product_key

WHERE c.source_file = 'stock_raw.csv'
  AND c.source_period = DATE '2023-01-01'
  AND c.previous_remaining_stock IS NOT NULL
  AND c.initial_stock <> c.previous_remaining_stock

ORDER BY c.product_key, c.movement_at, c.source_row_number
LIMIT 10;