CREATE OR REPLACE VIEW marts.daily_sales AS
SELECT
    d.full_date AS sales_date,
    COUNT(*) AS sales_line_count,
    COUNT(DISTINCT f.invoice_number) AS invoice_count,
    COUNT(DISTINCT f.product_key) AS unique_products,
    SUM(f.total_price) AS recorded_sales_value

FROM warehouse.fact_sales AS f

JOIN warehouse.dim_date AS d
    ON d.date_key = f.date_key

GROUP BY d.full_date;


-- Menampilkan lima tanggal pertama pada pilot.

SELECT *
FROM marts.daily_sales
WHERE sales_date >= DATE '2023-01-01'
  AND sales_date < DATE '2023-02-01'
ORDER BY sales_date
LIMIT 5;


-- Memeriksa total laporan Januari 2023.

SELECT
    SUM(sales_line_count) AS total_sales_lines,
    SUM(recorded_sales_value) AS total_recorded_value
FROM marts.daily_sales
WHERE sales_date >= DATE '2023-01-01'
  AND sales_date < DATE '2023-02-01';