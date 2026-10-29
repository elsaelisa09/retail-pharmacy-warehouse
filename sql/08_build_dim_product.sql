CREATE TABLE IF NOT EXISTS warehouse.dim_product (
    product_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    drug_code TEXT NOT NULL UNIQUE,
    drug_name TEXT,
    category TEXT,
    drug_class TEXT,
    created_at TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT CURRENT_TIMESTAMP
);

WITH product_records AS (
    SELECT
        drug_code,
        drug_name,
        category,
        drug_class
    FROM staging.sales_transactions
    WHERE source_period = DATE '2023-01-01'

    UNION ALL

    SELECT
        drug_code,
        drug_name,
        category,
        drug_class
    FROM staging.stock_movements
    WHERE source_period = DATE '2023-01-01'
)

INSERT INTO warehouse.dim_product (
    drug_code,
    drug_name,
    category,
    drug_class
)
SELECT
    drug_code,
    MAX(drug_name),
    MAX(category),
    MAX(drug_class)
FROM product_records
GROUP BY drug_code
ORDER BY drug_code;