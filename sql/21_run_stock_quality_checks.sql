WITH run_context AS MATERIALIZED (
    SELECT
        gen_random_uuid() AS run_id,
        CAST(:period_date AS DATE) AS source_period
),

stock_metrics AS (
    SELECT
        COUNT(*) AS total_rows,

        COUNT(*) FILTER (
            WHERE previous_remaining_stock IS NOT NULL
        ) AS checked_links,

        COUNT(*) FILTER (
            WHERE previous_remaining_stock IS NOT NULL
              AND initial_stock <> previous_remaining_stock
        ) AS continuity_issues,

        COUNT(*) FILTER (
            WHERE same_timestamp_count > 1
        ) AS timestamp_warnings,

        COUNT(*) FILTER (
            WHERE initial_stock < 0
               OR remaining_stock < 0
        ) AS negative_balance_warnings

    FROM audit.stock_continuity
    WHERE source_file = 'stock_raw.csv'
      AND source_period = (
          SELECT source_period FROM run_context
      )
),

monthly_metrics AS (
    SELECT
        COUNT(*) AS checked_groups,

        COUNT(*) FILTER (
            WHERE balance_gap IS DISTINCT FROM 0::NUMERIC
        ) AS balance_issues

    FROM marts.monthly_stock_position
    WHERE movement_month = (
        SELECT source_period FROM run_context
    )
),

checks AS (
    SELECT
        'stock_continuity' AS check_name,
        checked_links AS checked_rows,
        continuity_issues AS issue_rows,
        0::BIGINT AS warning_rows,
        'Membandingkan stok awal dengan saldo catatan sebelumnya.'
            AS details
    FROM stock_metrics

    UNION ALL

    SELECT
        'stock_timestamp_ambiguity',
        total_rows,
        0::BIGINT,
        timestamp_warnings,
        'Timestamp sama perlu ditinjau; pengurutan memakai waktu dan identitas sumber.'
    FROM stock_metrics

    UNION ALL

    SELECT
        'stock_monthly_balance',
        checked_groups,
        balance_issues,
        0::BIGINT,
        'Memeriksa saldo awal ditambah masuk dikurangi keluar terhadap saldo terakhir.'
    FROM monthly_metrics

    UNION ALL

    SELECT
        'stock_negative_balance',
        total_rows,
        0::BIGINT,
        negative_balance_warnings,
        'Menandai catatan dengan saldo awal atau akhir negatif untuk ditinjau.'
    FROM stock_metrics
)

INSERT INTO audit.data_quality_results (
    run_id,
    source_period,
    check_name,
    checked_rows,
    issue_rows,
    warning_rows,
    details
)
SELECT
    r.run_id,
    r.source_period,
    c.check_name,
    c.checked_rows,
    c.issue_rows,
    c.warning_rows,
    c.details
FROM run_context AS r
CROSS JOIN checks AS c

RETURNING
    run_id,
    check_name,
    checked_rows,
    issue_rows,
    warning_rows,
    status;