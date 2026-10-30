CREATE OR REPLACE VIEW marts.monthly_sales_daily_average AS

WITH activity AS (
    SELECT
        date_trunc('month', sale_at)::DATE AS sales_month,
        COUNT(DISTINCT sale_at::DATE) AS recorded_sales_days

    FROM warehouse.fact_sales
    WHERE source_file = 'sales_raw.csv'

    GROUP BY date_trunc('month', sale_at)::DATE
),

monthly_context AS (
    SELECT
        m.sales_month,
        m.recorded_sales_value,
        a.recorded_sales_days,

        EXTRACT(
            DAY FROM (
                m.sales_month
                + INTERVAL '1 month'
                - INTERVAL '1 day'
            )
        )::INTEGER AS calendar_days

    FROM marts.monthly_sales AS m

    JOIN activity AS a
        ON a.sales_month = m.sales_month
)

SELECT
    sales_month,
    recorded_sales_value,
    calendar_days,
    recorded_sales_days,

    ROUND(
        recorded_sales_value / NULLIF(calendar_days, 0),
        2
    ) AS avg_value_per_calendar_day,

    ROUND(
        recorded_sales_value / NULLIF(recorded_sales_days, 0),
        2
    ) AS avg_value_per_recorded_day

FROM monthly_context;