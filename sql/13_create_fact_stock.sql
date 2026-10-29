CREATE TABLE IF NOT EXISTS warehouse.fact_stock_movements (
    stock_movement_key BIGINT
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    source_file TEXT NOT NULL,
    source_period DATE NOT NULL,
    source_row_number BIGINT NOT NULL,

    date_key INTEGER NOT NULL,
    product_key BIGINT NOT NULL,

    movement_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    warehouse TEXT,
    document_number TEXT,
    transaction_description TEXT,

    initial_stock BIGINT NOT NULL,
    stock_in BIGINT NOT NULL,
    stock_out BIGINT NOT NULL,
    remaining_stock BIGINT NOT NULL,
    unit TEXT NOT NULL,

    drug_type TEXT,
    status TEXT,

    loaded_at TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_fact_stock_source
        UNIQUE (
            source_file,
            source_period,
            source_row_number
        ),

    CONSTRAINT fk_fact_stock_date
        FOREIGN KEY (date_key)
        REFERENCES warehouse.dim_date (date_key),

    CONSTRAINT fk_fact_stock_product
        FOREIGN KEY (product_key)
        REFERENCES warehouse.dim_product (product_key),

    CONSTRAINT ck_fact_stock_balance
        CHECK (
            initial_stock + stock_in - stock_out
            = remaining_stock
        )
);


-- Memastikan setiap pergerakan memiliki pasangan dimensi.

SELECT
    COUNT(*) AS staging_rows,

    COUNT(*) FILTER (
        WHERE p.product_key IS NULL
    ) AS missing_product,

    COUNT(*) FILTER (
        WHERE d.date_key IS NULL
    ) AS missing_date

FROM staging.stock_movements AS s

LEFT JOIN warehouse.dim_product AS p
    ON p.drug_code = s.drug_code

LEFT JOIN warehouse.dim_date AS d
    ON d.full_date = s.movement_at::DATE

WHERE s.source_file = 'stock_raw.csv'
  AND s.source_period = DATE '2023-01-01';