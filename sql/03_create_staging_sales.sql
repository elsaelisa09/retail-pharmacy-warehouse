CREATE TABLE IF NOT EXISTS staging.sales_transactions (
    source_file TEXT NOT NULL,
    source_period DATE NOT NULL,
    source_row_number BIGINT NOT NULL,

    sale_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    invoice_number TEXT NOT NULL,

    drug_code TEXT NOT NULL,
    drug_name TEXT,
    drug_class TEXT,
    category TEXT,
    manufacturer TEXT,
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

    cashier_id TEXT,
    shift_raw TEXT,
    batch_and_expiry_raw TEXT,
    price_tier_raw TEXT,
    is_member_raw TEXT,
    payment_type TEXT,
    print_count_raw TEXT,

    CONSTRAINT pk_staging_sales
        PRIMARY KEY (
            source_file,
            source_period,
            source_row_number
        )
);