WITH raw_keys AS (
    SELECT
        'sales' AS dataset,
        source_file,
        (source_period || '-01')::DATE AS source_period,
        "RowNumber"::BIGINT AS source_row_number
    FROM raw.sales_transactions
    WHERE source_period = '2023-01'

    UNION ALL

    SELECT
        'stock' AS dataset,
        source_file,
        (source_period || '-01')::DATE AS source_period,
        "RowNumber"::BIGINT AS source_row_number
    FROM raw.stock_movements
    WHERE source_period = '2023-01'
),

staging_keys AS (
    SELECT
        'sales' AS dataset,
        source_file,
        source_period,
        source_row_number
    FROM staging.sales_transactions
    WHERE source_period = DATE '2023-01-01'

    UNION ALL

    SELECT
        'stock' AS dataset,
        source_file,
        source_period,
        source_row_number
    FROM staging.stock_movements
    WHERE source_period = DATE '2023-01-01'
)

SELECT
    COALESCE(r.dataset, s.dataset) AS dataset,

    COUNT(r.source_row_number) AS raw_rows,
    COUNT(s.source_row_number) AS staging_rows,

    COUNT(*) FILTER (
        WHERE r.source_row_number IS NOT NULL
          AND s.source_row_number IS NULL
    ) AS missing_in_staging,

    COUNT(*) FILTER (
        WHERE r.source_row_number IS NULL
          AND s.source_row_number IS NOT NULL
    ) AS extra_in_staging

FROM raw_keys AS r
FULL OUTER JOIN staging_keys AS s
    ON r.dataset = s.dataset
   AND r.source_file = s.source_file
   AND r.source_period = s.source_period
   AND r.source_row_number = s.source_row_number

GROUP BY COALESCE(r.dataset, s.dataset)
ORDER BY dataset;