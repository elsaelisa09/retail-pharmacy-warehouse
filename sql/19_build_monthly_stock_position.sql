CREATE OR REPLACE VIEW marts.monthly_stock_position AS

WITH ranked_movements AS (
    SELECT
        f.*,
        date_trunc('month', f.movement_at)::DATE AS movement_month,

        ROW_NUMBER() OVER (
            PARTITION BY
                date_trunc('month', f.movement_at),
                f.product_key,
                f.warehouse,
                f.unit
            ORDER BY
                f.movement_at,
                f.source_file,
                f.source_period,
                f.source_row_number
        ) AS first_rank,

        ROW_NUMBER() OVER (
            PARTITION BY
                date_trunc('month', f.movement_at),
                f.product_key,
                f.warehouse,
                f.unit
            ORDER BY
                f.movement_at DESC,
                f.source_file DESC,
                f.source_period DESC,
                f.source_row_number DESC
        ) AS last_rank

    FROM warehouse.fact_stock_movements AS f
),

monthly AS (
    SELECT
        movement_month,
        product_key,
        warehouse,
        unit,
        COUNT(*) AS movement_count,

        MAX(initial_stock) FILTER (
            WHERE first_rank = 1
        ) AS opening_recorded_stock,

        SUM(stock_in) AS total_stock_in,
        SUM(stock_out) AS total_stock_out,

        MAX(remaining_stock) FILTER (
            WHERE last_rank = 1
        ) AS last_recorded_stock,

        MIN(movement_at) AS first_movement_at,
        MAX(movement_at) AS last_movement_at

    FROM ranked_movements
    GROUP BY
        movement_month,
        product_key,
        warehouse,
        unit
)

SELECT
    m.*,
    p.drug_code,
    p.drug_name,

    m.opening_recorded_stock
        + m.total_stock_in
        - m.total_stock_out
        - m.last_recorded_stock AS balance_gap

FROM monthly AS m
JOIN warehouse.dim_product AS p
    ON p.product_key = m.product_key;