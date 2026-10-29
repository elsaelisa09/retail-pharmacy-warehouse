SELECT
    COUNT(*) AS staging_rows,

    COUNT(*) FILTER (
        WHERE p.product_key IS NULL
    ) AS missing_product,

    COUNT(*) FILTER (
        WHERE d.date_key IS NULL
    ) AS missing_date

FROM staging.sales_transactions AS s

LEFT JOIN warehouse.dim_product AS p
    ON p.drug_code = s.drug_code

LEFT JOIN warehouse.dim_date AS d
    ON d.full_date = s.sale_at::DATE

WHERE s.source_file = 'sales_raw.csv'
  AND s.source_period = DATE '2023-01-01';