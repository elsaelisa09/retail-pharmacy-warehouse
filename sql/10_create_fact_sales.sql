CREATE TABLE IF NOT EXISTS warehouse.fact_sales (
    sale_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    source_file TEXT NOT NULL,
    source_period DATE NOT NULL,
    source_row_number BIGINT NOT NULL,

    date_key INTEGER NOT NULL,
    product_key BIGINT NOT NULL,

    sale_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    invoice_number TEXT NOT NULL,
    unit TEXT NOT NULL,

    quantity NUMERIC NOT NULL,
    unit_price NUMERIC NOT NULL,
    discount_pct NUMERIC NOT NULL,
    discount_amount NUMERIC NOT NULL,
    service_fee NUMERIC NOT NULL,
    packaging_fee NUMERIC NOT NULL,
    subtotal NUMERIC NOT NULL,
    invoice_discount_pct NUMERIC NOT NULL,
    promo_discount_pct NUMERIC NOT NULL,
    tax_rate_pct NUMERIC NOT NULL,
    additional_fee NUMERIC NOT NULL,
    total_price NUMERIC NOT NULL,

    loaded_at TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_fact_sales_source
        UNIQUE (
            source_file,
            source_period,
            source_row_number
        ),

    CONSTRAINT fk_fact_sales_date
        FOREIGN KEY (date_key)
        REFERENCES warehouse.dim_date (date_key),

    CONSTRAINT fk_fact_sales_product
        FOREIGN KEY (product_key)
        REFERENCES warehouse.dim_product (product_key)
);