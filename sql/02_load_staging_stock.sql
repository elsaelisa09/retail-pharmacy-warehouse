INSERT INTO staging.stock_movements (
    source_file,
    source_period,
    source_row_number,
    movement_at,
    warehouse,
    drug_code,
    drug_name,
    document_number,
    transaction_description,
    initial_stock,
    stock_in,
    stock_out,
    remaining_stock,
    unit,
    drug_class,
    category,
    drug_type,
    status
)
SELECT
    r.source_file,
    (r.source_period || '-01')::DATE,
    r."RowNumber"::BIGINT,

    to_timestamp(
        btrim(r."DateTime"),
        'DD Mon YYYY HH24:MI:SS'
    )::TIMESTAMP WITHOUT TIME ZONE,

    NULLIF(btrim(r."Warehouse"), ''),
    btrim(r."DrugCode"),
    NULLIF(btrim(r."DrugName"), ''),
    NULLIF(btrim(r."DocumentNumber"), ''),
    NULLIF(btrim(r."TransactionDescription"), ''),

    replace(
        (regexp_split_to_array(
            btrim(r."InitialStock"), '[[:space:]]+'
        ))[1],
        '.', ''
    )::BIGINT,

    replace(
        (regexp_split_to_array(
            btrim(r."StockIn"), '[[:space:]]+'
        ))[1],
        '.', ''
    )::BIGINT,

    replace(
        (regexp_split_to_array(
            btrim(r."StockOut"), '[[:space:]]+'
        ))[1],
        '.', ''
    )::BIGINT,

    replace(
        (regexp_split_to_array(
            btrim(r."RemainingStock"), '[[:space:]]+'
        ))[1],
        '.', ''
    )::BIGINT,

    regexp_replace(
        btrim(r."InitialStock"),
        '^[^[:space:]]+[[:space:]]+',
        ''
    ),

    NULLIF(btrim(r."DrugClass"), ''),
    NULLIF(btrim(r."Category"), ''),
    NULLIF(btrim(r."DrugType"), ''),
    NULLIF(btrim(r."Status"), '')

FROM raw.stock_movements AS r
WHERE r.source_file = 'stock_raw.csv'
  AND r.source_period = '2023-01';