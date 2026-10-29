SELECT
    v.field_name,
    COUNT(*) AS checked_rows,

    COUNT(*) FILTER (
        WHERE v.raw_value IS DISTINCT FROM v.staging_value
    ) AS mismatched_rows

FROM raw.sales_transactions AS r

JOIN staging.sales_transactions AS s
    ON s.source_file = r.source_file
   AND s.source_period = (r.source_period || '-01')::DATE
   AND s.source_row_number = r."RowNumber"::BIGINT

CROSS JOIN LATERAL (
    VALUES
        (
            'quantity',
            btrim(r."Quantity")::NUMERIC,
            s.quantity
        ),
        (
            'unit_price',
            btrim(r."UnitPrice")::NUMERIC,
            s.unit_price
        ),
        (
            'discount_amount',
            btrim(r."DiscountAmount")::NUMERIC,
            s.discount_amount
        ),
        (
            'service_fee',
            btrim(r."ServiceFee")::NUMERIC,
            s.service_fee
        ),
        (
            'packaging_fee',
            btrim(r."PackagingFee")::NUMERIC,
            s.packaging_fee
        ),
        (
            'subtotal',
            btrim(r."Subtotal")::NUMERIC,
            s.subtotal
        ),
        (
            'additional_fee',
            btrim(r."AdditionalFee")::NUMERIC,
            s.additional_fee
        ),
        (
            'total_price',
            btrim(r."TotalPrice")::NUMERIC,
            s.total_price
        )
) AS v(field_name, raw_value, staging_value)

WHERE r.source_file = 'sales_raw.csv'
    AND r.source_period = :period_text

GROUP BY v.field_name
ORDER BY v.field_name;