CREATE OR REPLACE VIEW marts.monthly_sales AS

WITH monthly AS (
    SELECT
        date_trunc('month', sale_at)::DATE AS sales_month,
        COUNT(*) AS sales_line_count,
        COUNT(DISTINCT invoice_number) AS invoice_count,
        COUNT(DISTINCT product_key) AS unique_products,
        SUM(total_price) AS recorded_sales_value

    FROM warehouse.fact_sales
    WHERE source_file = 'sales_raw.csv'

    GROUP BY date_trunc('month', sale_at)::DATE
),

with_previous AS (
    SELECT
        monthly.*,

        LAG(sales_month) OVER (
            ORDER BY sales_month
        ) AS previous_month,

        LAG(recorded_sales_value) OVER (
            ORDER BY sales_month
        ) AS previous_recorded_sales_value

    FROM monthly
)

SELECT
    sales_month,
    sales_line_count,
    invoice_count,
    unique_products,
    recorded_sales_value,

    ROUND(
        recorded_sales_value / NULLIF(invoice_count, 0),
        2
    ) AS avg_recorded_value_per_invoice,

    CASE
        WHEN previous_month =
             (sales_month - INTERVAL '1 month')::DATE
        THEN ROUND(
            100.0
            * (recorded_sales_value - previous_recorded_sales_value)
            / NULLIF(previous_recorded_sales_value, 0),
            2
        )
    END AS recorded_value_mom_pct

FROM with_previous;