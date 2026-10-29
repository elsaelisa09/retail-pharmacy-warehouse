-- Pemeriksaan 1: cakupan kode produk pada kedua sumber.

WITH sales_products AS (
    SELECT DISTINCT drug_code
    FROM staging.sales_transactions

),

stock_products AS (
    SELECT DISTINCT drug_code
    FROM staging.stock_movements

)

SELECT
    COUNT(*) AS all_products,

    COUNT(*) FILTER (
        WHERE s.drug_code IS NOT NULL
          AND t.drug_code IS NOT NULL
    ) AS in_both,

    COUNT(*) FILTER (
        WHERE s.drug_code IS NOT NULL
          AND t.drug_code IS NULL
    ) AS sales_only,

    COUNT(*) FILTER (
        WHERE s.drug_code IS NULL
          AND t.drug_code IS NOT NULL
    ) AS stock_only

FROM sales_products AS s
FULL OUTER JOIN stock_products AS t
    ON s.drug_code = t.drug_code;


-- Pemeriksaan 2: konsistensi atribut setiap kode produk.

WITH product_records AS (
    SELECT drug_code, drug_name, category, drug_class
    FROM staging.sales_transactions


    UNION ALL

    SELECT drug_code, drug_name, category, drug_class
    FROM staging.stock_movements

),

product_profile AS (
    SELECT
        drug_code,
        COUNT(DISTINCT drug_name) AS name_variants,
        COUNT(DISTINCT category) AS category_variants,
        COUNT(DISTINCT drug_class) AS class_variants
    FROM product_records
    GROUP BY drug_code
)

SELECT
    COUNT(*) AS all_products,

    COUNT(*) FILTER (
        WHERE name_variants > 1
    ) AS multiple_names,

    COUNT(*) FILTER (
        WHERE category_variants > 1
    ) AS multiple_categories,

    COUNT(*) FILTER (
        WHERE class_variants > 1
    ) AS multiple_classes

FROM product_profile;

-- Pemeriksaan 3: kode produk staging yang belum ada di dimensi.

WITH product_codes AS (
    SELECT drug_code
    FROM staging.sales_transactions

    UNION

    SELECT drug_code
    FROM staging.stock_movements
)

SELECT
    COUNT(*) AS staging_products,

    COUNT(*) FILTER (
        WHERE d.product_key IS NOT NULL
    ) AS already_in_dimension,

    COUNT(*) FILTER (
        WHERE d.product_key IS NULL
    ) AS new_products

FROM product_codes AS p
LEFT JOIN warehouse.dim_product AS d
    ON d.drug_code = p.drug_code;
