CREATE TABLE IF NOT EXISTS audit.data_quality_results (
    result_id BIGINT
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    run_id UUID NOT NULL,
    source_period DATE NOT NULL,
    check_name TEXT NOT NULL,

    checked_rows BIGINT NOT NULL
        CHECK (checked_rows >= 0),

    issue_rows BIGINT NOT NULL
        CHECK (issue_rows >= 0),

    status TEXT GENERATED ALWAYS AS (
        CASE
            WHEN issue_rows > 0 THEN 'FAIL'
            WHEN checked_rows = 0 THEN 'NO_DATA'
            ELSE 'PASS'
        END
    ) STORED,

    details TEXT,

    checked_at TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_quality_result
        UNIQUE (
            run_id,
            source_period,
            check_name
        )
);