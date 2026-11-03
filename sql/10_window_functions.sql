-- Module 3.8: window functions (simulated data; revenue at list price)
-- Feb 2021 is excluded: it is a partial month (data ends 2021-02-20).

-- W1. Month-over-month (MoM) and year-over-year (YoY) growth.
-- Two versions of MoM: raw revenue, and revenue per ACTIVE day. Every spring has a
-- 35-37 day gap with no orders (Module 3.7), so raw MoM around March-May is distorted.
-- YoY compares the same month a year earlier, which removes seasonality, but March and
-- April stay unreliable: each year's gap leaves a different number of active days (5 to 7 in April).
WITH monthly AS (
    SELECT month_start,
           SUM(revenue_usd)           AS revenue,
           COUNT(DISTINCT order_date) AS active_days
    FROM sales.v_sales_enriched
    WHERE order_date < DATE '2021-02-01'
    GROUP BY month_start
)
SELECT month_start,
       ROUND(revenue, 0)                                               AS revenue_usd,
       ROUND(100 * (revenue - LAG(revenue) OVER w) / LAG(revenue) OVER w, 1)       AS mom_pct,
       ROUND(100 * (revenue - LAG(revenue, 12) OVER w) / LAG(revenue, 12) OVER w, 1) AS yoy_pct,
       active_days,
       ROUND(revenue / active_days, 0)                                 AS revenue_per_active_day,
       ROUND(100 * (revenue / active_days - LAG(revenue / active_days) OVER w)
             / LAG(revenue / active_days) OVER w, 1)                   AS mom_pct_per_day
FROM monthly
WINDOW w AS (ORDER BY month_start)
ORDER BY month_start;


-- W2. Running total and trailing-12-month revenue.
-- A trailing 12-month sum always contains exactly one spring gap, so it is a fair,
-- smooth trend line. Only shown once a full 12 months are available.
WITH monthly AS (
    SELECT month_start, SUM(revenue_usd) AS revenue
    FROM sales.v_sales_enriched
    WHERE order_date < DATE '2021-02-01'
    GROUP BY month_start
)
SELECT month_start,
       ROUND(revenue, 0)                                              AS revenue_usd,
       ROUND(SUM(revenue) OVER (ORDER BY month_start), 0)             AS cumulative_usd,
       CASE WHEN COUNT(*) OVER w12 = 12
            THEN ROUND(SUM(revenue) OVER w12, 0) END                  AS trailing_12m_usd
FROM monthly
WINDOW w12 AS (ORDER BY month_start ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
ORDER BY month_start;


-- W3. Top 3 products in each category by revenue (RANK within a partition).
-- Note: each product_key is one COLOR variant of a model (seen in J4).
WITH product_revenue AS (
    SELECT category, product_name,
           SUM(revenue_usd) AS revenue
    FROM sales.v_sales_enriched
    GROUP BY category, product_key, product_name
),
ranked AS (
    SELECT category, product_name, revenue,
           RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rnk
    FROM product_revenue
)
SELECT category, rnk, product_name, ROUND(revenue, 0) AS revenue_usd
FROM ranked
WHERE rnk <= 3
ORDER BY category, rnk;


-- W4. Customer concentration: spend by decile (NTILE). The question left open in C2:
-- "do the top 10% of customers carry the business?" Decile 1 = biggest spenders.
WITH customer_spend AS (
    SELECT customer_key, SUM(revenue_usd) AS spend
    FROM sales.v_sales_enriched
    GROUP BY customer_key
),
deciles AS (
    SELECT spend, NTILE(10) OVER (ORDER BY spend DESC) AS decile
    FROM customer_spend
)
SELECT decile,
       COUNT(*)                                                       AS customers,
       ROUND(SUM(spend), 0)                                           AS revenue_usd,
       ROUND(100 * SUM(spend) / SUM(SUM(spend)) OVER (), 1)           AS pct_revenue,
       ROUND(100 * SUM(SUM(spend)) OVER (ORDER BY decile)
             / SUM(SUM(spend)) OVER (), 1)                            AS cumulative_pct
FROM deciles
GROUP BY decile
ORDER BY decile;