-- Module 3.3: KPI queries (simulated data; revenue at list price)

-- Q1. Overall KPIs. "What is the size of the business?"
-- Business use: the headline numbers for the executive dashboard.
SELECT
    COUNT(DISTINCT order_number)                        AS orders,
    SUM(quantity)                                       AS units_sold,
    COUNT(DISTINCT customer_key)                        AS active_customers,
    ROUND(SUM(revenue_usd), 2)                          AS revenue_usd,
    ROUND(SUM(cost_usd), 2)                             AS cost_usd,
    ROUND(SUM(profit_usd), 2)                           AS gross_profit_usd,
    ROUND(100 * SUM(profit_usd) / SUM(revenue_usd), 1)  AS margin_pct,
    ROUND(SUM(revenue_usd) / COUNT(DISTINCT order_number), 2) AS avg_order_value
FROM sales.v_sales_enriched;


-- Q2. Performance by year. "Are we growing?"
-- months_covered exposes that 2021 is only Jan 1 to Feb 20: never compare it
-- to full years without noticing that.
SELECT
    year,
    COUNT(DISTINCT month)                               AS months_covered,
    COUNT(DISTINCT order_number)                        AS orders,
    SUM(quantity)                                       AS units_sold,
    ROUND(SUM(revenue_usd), 0)                          AS revenue_usd,
    ROUND(SUM(profit_usd), 0)                           AS profit_usd,
    ROUND(100 * SUM(profit_usd) / SUM(revenue_usd), 1)  AS margin_pct
FROM sales.v_sales_enriched
GROUP BY year
ORDER BY year;


-- Q3. Category performance, with HAVING. "Which categories drive the business?"
-- HAVING filters after aggregation: here, categories with at least $1M revenue.
SELECT
    category,
    SUM(quantity)                                       AS units_sold,
    ROUND(SUM(revenue_usd), 0)                          AS revenue_usd,
    ROUND(SUM(profit_usd), 0)                           AS profit_usd,
    ROUND(100 * SUM(profit_usd) / SUM(revenue_usd), 1)  AS margin_pct,
    ROUND(100 * SUM(revenue_usd) / SUM(SUM(revenue_usd)) OVER (), 1) AS pct_of_revenue
FROM sales.v_sales_enriched
GROUP BY category
HAVING SUM(revenue_usd) >= 1000000
ORDER BY revenue_usd DESC;


-- Q3b above drops categories under $1M BEFORE computing pct_of_revenue, so its percentages are wrong. Use this version for shares.
SELECT category,
       ROUND(SUM(revenue_usd), 0) AS revenue_usd,
       ROUND(100 * SUM(revenue_usd) / SUM(SUM(revenue_usd)) OVER (), 1) AS pct_of_total
FROM sales.v_sales_enriched
GROUP BY category
ORDER BY revenue_usd DESC;

-- Q4. Online vs in-store, for completed history only. "Which channel matters?"
-- WHERE filters rows BEFORE grouping: we drop the partial month (Feb 2021).
SELECT
    channel,
    COUNT(DISTINCT order_number)                        AS orders,
    ROUND(SUM(revenue_usd), 0)                          AS revenue_usd,
    ROUND(SUM(revenue_usd) / COUNT(DISTINCT order_number), 2) AS avg_order_value,
    ROUND(100 * SUM(profit_usd) / SUM(revenue_usd), 1)  AS margin_pct
FROM sales.v_sales_enriched
WHERE order_date < DATE '2021-02-01'
GROUP BY channel
ORDER BY revenue_usd DESC;