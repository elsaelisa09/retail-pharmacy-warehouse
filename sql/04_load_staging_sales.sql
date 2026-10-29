INSERT INTO staging.sales_transactions (
    source_file,
    source_period,
    source_row_number,
    sale_at,
    invoice_number,
    drug_code,
    drug_name,
    drug_class,
    category,
    manufacturer,
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
    total_price,
    cashier_id,
    shift_raw,
    batch_and_expiry_raw,
    price_tier_raw,
    is_member_raw,
    payment_type,
    print_count_raw
)
SELECT
    r.source_file,
    (r.source_period || '-01')::DATE,
    r."RowNumber"::BIGINT,

    to_timestamp(
        btrim(r."DateTime"),
        'DD Mon YYYY HH24:MI:SS'
    )::TIMESTAMP WITHOUT TIME ZONE,

    btrim(r."InvoiceNumber"),
    btrim(r."DrugCode"),
    NULLIF(btrim(r."DrugName"), ''),
    NULLIF(btrim(r."DrugClass"), ''),
    NULLIF(btrim(r."Category"), ''),
    NULLIF(btrim(r."Manufacturer"), ''),
    btrim(r."Unit"),

    btrim(r."Quantity")::NUMERIC,
    btrim(r."UnitPrice")::NUMERIC,

    replace(
        replace(btrim(r."DiscountPct"), '%', ''),
        ',', '.'
    )::NUMERIC,

    btrim(r."DiscountAmount")::NUMERIC,
    btrim(r."ServiceFee")::NUMERIC,
    btrim(r."PackagingFee")::NUMERIC,
    btrim(r."Subtotal")::NUMERIC,

    replace(
        replace(btrim(r."InvoiceDiscountPct"), '%', ''),
        ',', '.'
    )::NUMERIC,

    replace(
        replace(btrim(r."PromoDiscountPct"), '%', ''),
        ',', '.'
    )::NUMERIC,

    replace(
        replace(btrim(r."TaxAmount"), '%', ''),
        ',', '.'
    )::NUMERIC,

    btrim(r."AdditionalFee")::NUMERIC,
    btrim(r."TotalPrice")::NUMERIC,

    NULLIF(btrim(r."CashierID"), ''),
    NULLIF(btrim(r."Shift"), ''),
    NULLIF(btrim(r."BatchAndExpiryDate"), ''),
    NULLIF(btrim(r."PriceTier"), ''),
    NULLIF(btrim(r."IsMember"), ''),
    NULLIF(btrim(r."PaymentType"), ''),
    NULLIF(btrim(r."PrintCount"), '')

FROM raw.sales_transactions AS r
WHERE r.source_file = 'sales_raw.csv'
  AND r.source_period = :source_period;