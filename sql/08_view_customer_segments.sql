-- Customer segments: one row per customer (all 15,266), simulated data.
-- Cut-offs were chosen from the spend distribution in Module 3.6 (see 07_segmentation.sql).
-- Lifetime spend covers 2016-01-01 to 2021-02-20, so earlier customers had longer to spend.

CREATE OR REPLACE VIEW sales.v_customer_segments AS
WITH spend AS (
    SELECT customer_key,
           COUNT(DISTINCT order_number) AS orders,
           SUM(revenue_usd)             AS spend,
           MIN(order_date)              AS first_order,
           MAX(order_date)              AS last_order
    FROM sales.v_sales_enriched
    GROUP BY customer_key
)
SELECT c.customer_key,
       c.gender,
       c.country,
       c.state,
       c.continent,
       COALESCE(s.orders, 0)  AS orders,
       COALESCE(s.spend, 0)   AS lifetime_spend_usd,
       s.first_order,
       s.last_order,
       CASE WHEN s.customer_key IS NULL THEN 'No purchases'
            WHEN s.spend < 1000  THEN 'Bronze'
            WHEN s.spend < 6000  THEN 'Silver'
            WHEN s.spend < 11000 THEN 'Gold'
            ELSE 'Platinum' END AS value_tier,
       CASE WHEN s.customer_key IS NULL THEN 'No purchases'
            WHEN s.orders = 1    THEN 'One-time'
            WHEN s.orders <= 3   THEN 'Repeat'
            ELSE 'Loyal' END    AS frequency_segment
FROM sales.dim_customers c
LEFT JOIN spend s ON s.customer_key = c.customer_key;