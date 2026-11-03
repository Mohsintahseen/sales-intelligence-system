-- Module 3.7: date trends (simulated data; revenue at list price)
-- Feb 2021 is a partial month (data ends 2021-02-20): excluded where noted.

-- T1. Quarterly revenue and orders. "Which quarters are strong?"
SELECT year, quarter,
       COUNT(DISTINCT order_number)          AS orders,
       ROUND(SUM(revenue_usd), 0)            AS revenue_usd
FROM sales.v_sales_enriched
GROUP BY year, quarter
ORDER BY year, quarter;


-- T2. Monthly series (62 rows incl. the partial Feb 2021). This is the series
-- we will forecast in Phase 5.
SELECT month_start,
       COUNT(DISTINCT order_number)          AS orders,
       ROUND(SUM(revenue_usd), 0)            AS revenue_usd,
       COUNT(DISTINCT order_date)            AS days_with_orders
FROM sales.v_sales_enriched
GROUP BY month_start
ORDER BY month_start;


-- T3. Seasonality: average revenue by calendar month, using the stable years
-- 2016-2019 only (2020 is an anomaly, 2021 is partial).
-- seasonal_index: 100 = an average month; 120 = 20% above average.
WITH monthly AS (
    SELECT year, month, SUM(revenue_usd) AS revenue
    FROM sales.v_sales_enriched
    WHERE year BETWEEN 2016 AND 2019
    GROUP BY year, month
)
SELECT month,
       ROUND(AVG(revenue), 0)                                    AS avg_revenue,
       ROUND(100 * AVG(revenue) / AVG(AVG(revenue)) OVER (), 0)  AS seasonal_index
FROM monthly
GROUP BY month
ORDER BY month;


-- T4. Where did the 2020 drop come from? Revenue by year and channel.
SELECT year, channel,
       COUNT(DISTINCT order_number)          AS orders,
       ROUND(SUM(revenue_usd), 0)            AS revenue_usd
FROM sales.v_sales_enriched
WHERE year BETWEEN 2018 AND 2020
GROUP BY year, channel
ORDER BY channel, year;


-- T5. Weekday pattern. Joins dim_date for the day name.
SELECT d.day_of_week, d.day_name,
       COUNT(DISTINCT f.order_number)        AS orders,
       ROUND(SUM(f.quantity * p.unit_price_usd), 0) AS revenue_usd
FROM sales.fact_sales f
JOIN sales.dim_date d     ON d.full_date   = f.order_date
JOIN sales.dim_products p ON p.product_key = f.product_key
WHERE f.order_date < DATE '2021-02-01'
GROUP BY d.day_of_week, d.day_name
ORDER BY d.day_of_week;


-- G1. Gaps-and-islands: find runs of consecutive calendar days with no orders.
-- Trick: for a run of consecutive missing dates, (date - row_number) is constant,
-- so grouping on it collapses each run into one row.
WITH days AS (
    SELECT d.full_date,
           EXISTS (SELECT 1 FROM sales.fact_sales f
                   WHERE f.order_date = d.full_date) AS has_orders
    FROM sales.dim_date d
    WHERE d.full_date BETWEEN DATE '2016-01-01' AND DATE '2021-02-20'
),
missing AS (
    SELECT full_date,
           full_date - (ROW_NUMBER() OVER (ORDER BY full_date))::int AS run_id
    FROM days
    WHERE NOT has_orders
)
SELECT MIN(full_date) AS gap_start,
       MAX(full_date) AS gap_end,
       COUNT(*)       AS days_missing
FROM missing
GROUP BY run_id
HAVING COUNT(*) >= 3
ORDER BY gap_start;