INSERT INTO warehouse.fact_sales (
    source_file,
    source_period,
    source_row_number,
    date_key,
    product_key,
    sale_at,
    invoice_number,
    unit,
    quantity,
    unit_price,
    discount_pct,
    discount_amount,
    service_fee,
    packaging_fee,
    subtotal,
    invoice_discount_pct,
    promo_discount_pct,
    tax_rate_pct,
    additional_fee,
    total_price
)
SELECT
    s.source_file,
    s.source_period,
    s.source_row_number,
    d.date_key,
    p.product_key,
    s.sale_at,
    s.invoice_number,
    s.unit,
    s.quantity,
    s.unit_price,
    s.discount_pct,
    s.discount_amount,
    s.service_fee,
    s.packaging_fee,
    s.subtotal,
    s.invoice_discount_pct,
    s.promo_discount_pct,
    s.tax_rate_pct,
    s.additional_fee,
    s.total_price

FROM staging.sales_transactions AS s

JOIN warehouse.dim_product AS p
    ON p.drug_code = s.drug_code

JOIN warehouse.dim_date AS d
    ON d.full_date = s.sale_at::DATE

WHERE s.source_file = 'sales_raw.csv'
  AND s.source_period = DATE '2023-01-01';