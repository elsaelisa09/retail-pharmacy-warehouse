CREATE OR REPLACE VIEW audit.sales_fact_reconciliation AS

WITH staging_sales AS (
    SELECT *
    FROM staging.sales_transactions
    WHERE source_file = 'sales_raw.csv'
),

fact_sales AS (
    SELECT
        f.*,
        p.drug_code,
        d.full_date

    FROM warehouse.fact_sales AS f

    LEFT JOIN warehouse.dim_product AS p
        ON p.product_key = f.product_key

    LEFT JOIN warehouse.dim_date AS d
        ON d.date_key = f.date_key

    WHERE f.source_file = 'sales_raw.csv'
)

SELECT
    COALESCE(s.source_period, f.source_period) AS source_period,

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
              s.sale_at,
              s.invoice_number,
              s.unit,
              s.quantity,
              s.unit_price,
              s.discount_pct,
              s.discount_amount,
              s.service_fee,
              s.packaging_fee,
              s.subtotal,
              s.invoice_discount_pct,
              s.promo_discount_pct,
              s.tax_rate_pct,
              s.additional_fee,
              s.total_price,
              s.drug_code,
              s.sale_at::DATE
          ) IS DISTINCT FROM ROW(
              f.sale_at,
              f.invoice_number,
              f.unit,
              f.quantity,
              f.unit_price,
              f.discount_pct,
              f.discount_amount,
              f.service_fee,
              f.packaging_fee,
              f.subtotal,
              f.invoice_discount_pct,
              f.promo_discount_pct,
              f.tax_rate_pct,
              f.additional_fee,
              f.total_price,
              f.drug_code,
              f.full_date
          )
    ) AS mismatched_values

FROM staging_sales AS s

FULL OUTER JOIN fact_sales AS f
    ON f.source_file = s.source_file
   AND f.source_period = s.source_period
   AND f.source_row_number = s.source_row_number

GROUP BY COALESCE(s.source_period, f.source_period);