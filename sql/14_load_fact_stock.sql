INSERT INTO warehouse.fact_stock_movements (
    source_file,
    source_period,
    source_row_number,
    date_key,
    product_key,
    movement_at,
    warehouse,
    document_number,
    transaction_description,
    initial_stock,
    stock_in,
    stock_out,
    remaining_stock,
    unit,
    drug_type,
    status
)
SELECT
    s.source_file,
    s.source_period,
    s.source_row_number,
    d.date_key,
    p.product_key,
    s.movement_at,
    s.warehouse,
    s.document_number,
    s.transaction_description,
    s.initial_stock,
    s.stock_in,
    s.stock_out,
    s.remaining_stock,
    s.unit,
    s.drug_type,
    s.status

FROM staging.stock_movements AS s

JOIN warehouse.dim_product AS p
    ON p.drug_code = s.drug_code

JOIN warehouse.dim_date AS d
    ON d.full_date = s.movement_at::DATE

WHERE s.source_file = 'stock_raw.csv'
  AND s.source_period = DATE '2023-01-01';
