-- Module 3.9: does customer value mostly reflect how long a customer has existed?
-- Cohort = calendar year of a customer's first order. Simulated data.

-- K1. Lifetime spend by cohort (unequal observation windows).
WITH first_orders AS (
    SELECT customer_key, MIN(order_date) AS first_order
    FROM sales.fact_sales
    GROUP BY customer_key
)
SELECT EXTRACT(YEAR FROM fo.first_order)::int                       AS cohort_year,
       COUNT(*)                                                      AS customers,
       ROUND(AVG(cs.lifetime_spend_usd), 0)                          AS avg_lifetime_spend,
       ROUND(AVG(cs.orders), 2)                                      AS avg_orders,
       ROUND(100.0 * COUNT(*) FILTER (WHERE cs.value_tier IN ('Gold', 'Platinum'))
             / COUNT(*), 1)                                          AS pct_gold_platinum
FROM first_orders fo
JOIN sales.v_customer_segments cs ON cs.customer_key = fo.customer_key
GROUP BY 1
ORDER BY 1;


-- K2. Equal-window comparison: spend within each customer's FIRST 365 days.
-- Only customers whose first order is on or before 2020-02-20 are included,
-- so every one of them has a full 365 days of observation (data ends 2021-02-20).
WITH first_orders AS (
    SELECT customer_key, MIN(order_date) AS first_order
    FROM sales.fact_sales
    GROUP BY customer_key
)
SELECT EXTRACT(YEAR FROM fo.first_order)::int                       AS cohort_year,
       COUNT(DISTINCT v.customer_key)                                AS customers,
       ROUND(SUM(v.revenue_usd) / COUNT(DISTINCT v.customer_key), 0) AS avg_first_year_spend,
       ROUND(COUNT(DISTINCT v.order_number)::numeric
             / COUNT(DISTINCT v.customer_key), 2)                    AS avg_first_year_orders
FROM sales.v_sales_enriched v
JOIN first_orders fo ON fo.customer_key = v.customer_key
WHERE fo.first_order <= DATE '2020-02-20'
  AND v.order_date < fo.first_order + 365
GROUP BY 1
ORDER BY 1;