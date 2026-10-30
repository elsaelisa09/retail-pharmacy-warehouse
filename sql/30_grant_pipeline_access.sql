BEGIN;

GRANT CONNECT
ON DATABASE retail_pharmacy_dw
TO pharmacy_etl;

GRANT USAGE
ON SCHEMA raw, staging, warehouse, marts, audit
TO pharmacy_etl;

-- Pemuatan ulang mengganti batch menggunakan DELETE dan INSERT.
GRANT SELECT, INSERT, DELETE
ON TABLE
    raw.stock_movements,
    raw.sales_transactions,
    staging.stock_movements,
    staging.sales_transactions,
    warehouse.fact_stock_movements,
    warehouse.fact_sales
TO pharmacy_etl;

-- Dimensi produk hanya dibaca dan ditambahkan.
GRANT SELECT, INSERT
ON TABLE warehouse.dim_product
TO pharmacy_etl;

GRANT SELECT
ON TABLE warehouse.dim_date
TO pharmacy_etl;

-- Hasil audit ditambahkan; riwayat pipeline diperbarui statusnya.
GRANT SELECT, INSERT
ON TABLE audit.data_quality_results
TO pharmacy_etl;

GRANT SELECT, INSERT, UPDATE
ON TABLE audit.pipeline_runs
TO pharmacy_etl;

GRANT SELECT
ON TABLE
    audit.stock_continuity,
    audit.sales_fact_reconciliation,
    marts.monthly_stock_position
TO pharmacy_etl;

GRANT USAGE
ON ALL SEQUENCES IN SCHEMA warehouse, audit
TO pharmacy_etl;

COMMIT;