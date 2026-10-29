CREATE TABLE IF NOT EXISTS staging.stock_movements (
    source_file TEXT NOT NULL,
    source_period DATE NOT NULL,
    source_row_number BIGINT NOT NULL,

    movement_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    warehouse TEXT,
    drug_code TEXT NOT NULL,
    drug_name TEXT,
    document_number TEXT,
    transaction_description TEXT,

    initial_stock BIGINT NOT NULL,
    stock_in BIGINT NOT NULL,
    stock_out BIGINT NOT NULL,
    remaining_stock BIGINT NOT NULL,
    unit TEXT NOT NULL,

    drug_class TEXT,
    category TEXT,
    drug_type TEXT,
    status TEXT,

    CONSTRAINT pk_staging_stock
        PRIMARY KEY (
            source_file,
            source_period,
            source_row_number
        ),

    CONSTRAINT ck_staging_stock_balance
        CHECK (
            initial_stock + stock_in - stock_out
            = remaining_stock
        )
);