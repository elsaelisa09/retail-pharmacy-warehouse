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

    UNION ALL

    SELECT
        drug_code,
        drug_name,
        category,
        drug_class
    FROM staging.stock_movements
),

product_candidates AS (
    SELECT
        drug_code,
        MAX(drug_name) AS drug_name,
        MAX(category) AS category,
        MAX(drug_class) AS drug_class
    FROM product_records
    GROUP BY drug_code
)

INSERT INTO warehouse.dim_product (
    drug_code,
    drug_name,
    category,
    drug_class
)
SELECT
    p.drug_code,
    p.drug_name,
    p.category,
    p.drug_class
FROM product_candidates AS p
WHERE NOT EXISTS (
    SELECT 1
    FROM warehouse.dim_product AS d
    WHERE d.drug_code = p.drug_code
)
ORDER BY p.drug_code
ON CONFLICT (drug_code) DO NOTHING;