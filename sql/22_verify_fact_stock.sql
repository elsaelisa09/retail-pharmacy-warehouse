-- Membandingkan staging dengan warehouse.

SELECT
    'staging' AS layer,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT drug_code) AS unique_products,
    MIN(movement_at) AS earliest_movement,
    MAX(movement_at) AS latest_movement
FROM staging.stock_movements
WHERE source_file = 'stock_raw.csv'
  AND source_period = DATE '2023-01-01'

UNION ALL

SELECT
    'warehouse' AS layer,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT product_key) AS unique_products,
    MIN(movement_at) AS earliest_movement,
    MAX(movement_at) AS latest_movement
FROM warehouse.fact_stock_movements
WHERE source_file = 'stock_raw.csv'
  AND source_period = DATE '2023-01-01';