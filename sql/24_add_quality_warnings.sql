BEGIN;

ALTER TABLE audit.data_quality_results
ADD COLUMN IF NOT EXISTS warning_rows BIGINT
    NOT NULL DEFAULT 0
    CHECK (warning_rows >= 0);

ALTER TABLE audit.data_quality_results
DROP COLUMN status;

ALTER TABLE audit.data_quality_results
ADD COLUMN status TEXT
GENERATED ALWAYS AS (
    CASE
        WHEN issue_rows > 0 THEN 'FAIL'
        WHEN checked_rows = 0 THEN 'NO_DATA'
        WHEN warning_rows > 0 THEN 'WARN'
        ELSE 'PASS'
    END
) STORED;

COMMIT;