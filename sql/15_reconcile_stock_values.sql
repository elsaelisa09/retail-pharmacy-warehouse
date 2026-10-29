WITH staging_pilot AS (
    SELECT *
    FROM staging.stock_movements
    WHERE source_file = 'stock_raw.csv'
      AND source_period = :period_date
),

warehouse_pilot AS (
    SELECT
        f.*,
        p.drug_code,
        d.full_date
    FROM warehouse.fact_stock_movements AS f

    LEFT JOIN warehouse.dim_product AS p
        ON p.product_key = f.product_key

    LEFT JOIN warehouse.dim_date AS d
        ON d.date_key = f.date_key

    WHERE f.source_file = 'stock_raw.csv'
      AND f.source_period = :period_date
)

SELECT
    COUNT(s.source_row_number) AS staging_rows,
    COUNT(f.source_row_number) AS fact_rows,

    COUNT(*) FILTER (
        WHERE s.source_row_number IS NOT NULL
          AND f.source_row_number IS NULL
    ) AS missing_in_fact,

    COUNT(*) FILTER (
        WHERE s.source_row_number IS NULL
          AND f.source_row_number IS NOT NULL
    ) AS extra_in_fact,

    COUNT(*) FILTER (
        WHERE s.source_row_number IS NOT NULL
          AND f.source_row_number IS NOT NULL
          AND ROW(
              s.initial_stock,
              s.stock_in,
              s.stock_out,
              s.remaining_stock,
              s.unit,
              s.movement_at,
              s.drug_code,
              s.movement_at::DATE
          ) IS DISTINCT FROM ROW(
              f.initial_stock,
              f.stock_in,
              f.stock_out,
              f.remaining_stock,
              f.unit,
              f.movement_at,
              f.drug_code,
              f.full_date
          )
    ) AS mismatched_values

FROM staging_pilot AS s
FULL OUTER JOIN warehouse_pilot AS f
    ON f.source_file = s.source_file
   AND f.source_period = s.source_period
   AND f.source_row_number = s.source_row_number;