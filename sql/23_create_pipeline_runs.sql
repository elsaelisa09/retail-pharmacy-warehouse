CREATE TABLE IF NOT EXISTS audit.pipeline_runs (
    pipeline_run_id UUID PRIMARY KEY
        DEFAULT gen_random_uuid(),

    pipeline_name TEXT NOT NULL,
    source_period DATE NOT NULL,

    status TEXT NOT NULL DEFAULT 'RUNNING'
        CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),

    started_at TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT clock_timestamp(),

    finished_at TIMESTAMP WITH TIME ZONE,
    failed_step TEXT,
    error_message TEXT,

    CONSTRAINT ck_pipeline_run_completion
        CHECK (
            (
                status = 'RUNNING'
                AND finished_at IS NULL
            )
            OR
            (
                status IN ('SUCCESS', 'FAILED')
                AND finished_at IS NOT NULL
            )
        )
);