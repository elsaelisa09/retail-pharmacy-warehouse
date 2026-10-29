CREATE OR REPLACE VIEW marts.monthly_stock_movements AS
SELECT
    date_trunc('month', f.movement_at)::DATE AS movement_month,
    f.product_key,
    p.drug_code,
    p.drug_name,
    f.warehouse,
    f.unit,

    COUNT(*) AS movement_count,
    SUM(f.stock_in) AS total_stock_in,
    SUM(f.stock_out) AS total_stock_out,

    SUM(f.stock_in) - SUM(f.stock_out)
        AS net_recorded_movement

FROM warehouse.fact_stock_movements AS f

JOIN warehouse.dim_product AS p
    ON p.product_key = f.product_key

GROUP BY
    date_trunc('month', f.movement_at)::DATE,
    f.product_key,
    p.drug_code,
    p.drug_name,
    f.warehouse,
    f.unit;


-- Menampilkan lima kelompok produk pertama.

SELECT
    drug_code,
    drug_name,
    warehouse,
    unit,
    movement_count,
    total_stock_in,
    total_stock_out,
    net_recorded_movement
FROM marts.monthly_stock_movements
WHERE movement_month = DATE '2023-01-01'
ORDER BY drug_code, warehouse, unit
LIMIT 5;


-- Memastikan seluruh pergerakan tercakup dalam laporan.

SELECT
    COUNT(*) AS report_groups,
    SUM(movement_count) AS represented_movements
FROM marts.monthly_stock_movements
WHERE movement_month = DATE '2023-01-01';