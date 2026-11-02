-- Module 3.6: segmentation (simulated data; revenue at list price)

-- S0a. Distribution of lifetime spend per ordering customer.
-- percentile_cont(0.5) is the median: half of customers spend less than this.
WITH customer_spend AS (
    SELECT customer_key, SUM(revenue_usd) AS spend
    FROM sales.v_sales_enriched
    GROUP BY customer_key
)
SELECT COUNT(*)                                                    AS customers,
       ROUND(MIN(spend), 0)                                        AS min_spend,
       ROUND(percentile_cont(0.25) WITHIN GROUP (ORDER BY spend)::numeric, 0) AS p25,
       ROUND(percentile_cont(0.50) WITHIN GROUP (ORDER BY spend)::numeric, 0) AS median,
       ROUND(percentile_cont(0.75) WITHIN GROUP (ORDER BY spend)::numeric, 0) AS p75,
       ROUND(percentile_cont(0.90) WITHIN GROUP (ORDER BY spend)::numeric, 0) AS p90,
       ROUND(percentile_cont(0.99) WITHIN GROUP (ORDER BY spend)::numeric, 0) AS p99,
       ROUND(MAX(spend), 0)                                        AS max_spend,
       ROUND(AVG(spend), 0)                                        AS mean_spend
FROM customer_spend;


-- S0b. Distribution of order value (one row per order).
WITH order_value AS (
    SELECT order_number, SUM(revenue_usd) AS value
    FROM sales.v_sales_enriched
    GROUP BY order_number
)
SELECT COUNT(*)                                                    AS orders,
       ROUND(MIN(value), 0)                                        AS min_value,
       ROUND(percentile_cont(0.25) WITHIN GROUP (ORDER BY value)::numeric, 0) AS p25,
       ROUND(percentile_cont(0.50) WITHIN GROUP (ORDER BY value)::numeric, 0) AS median,
       ROUND(percentile_cont(0.75) WITHIN GROUP (ORDER BY value)::numeric, 0) AS p75,
       ROUND(percentile_cont(0.90) WITHIN GROUP (ORDER BY value)::numeric, 0) AS p90,
       ROUND(MAX(value), 0)                                        AS max_value,
       ROUND(AVG(value), 0)                                        AS mean_value
FROM order_value;


-- S0c. Distribution of product list price (one row per product).
SELECT COUNT(*)                                                    AS products,
       MIN(unit_price_usd)                                         AS min_price,
       percentile_cont(0.25) WITHIN GROUP (ORDER BY unit_price_usd)::numeric(10,2) AS p25,
       percentile_cont(0.50) WITHIN GROUP (ORDER BY unit_price_usd)::numeric(10,2) AS median,
       percentile_cont(0.75) WITHIN GROUP (ORDER BY unit_price_usd)::numeric(10,2) AS p75,
       percentile_cont(0.90) WITHIN GROUP (ORDER BY unit_price_usd)::numeric(10,2) AS p90,
       MAX(unit_price_usd)                                         AS max_price
FROM sales.dim_products;


-- S0d. How many customers placed 1, 2, 3, ... orders?
WITH orders_per_customer AS (
    SELECT customer_key, COUNT(DISTINCT order_number) AS orders
    FROM sales.fact_sales
    GROUP BY customer_key
)
SELECT orders,
       COUNT(*)                                          AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_customers
FROM orders_per_customer
GROUP BY orders
ORDER BY orders;


-- S1. Customer value tiers: size and revenue share.
SELECT value_tier,
       COUNT(*)                                                       AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)             AS pct_customers,
       ROUND(SUM(lifetime_spend_usd), 0)                              AS revenue_usd,
       ROUND(100 * SUM(lifetime_spend_usd) / SUM(SUM(lifetime_spend_usd)) OVER (), 1) AS pct_revenue
FROM sales.v_customer_segments
GROUP BY value_tier
ORDER BY MIN(lifetime_spend_usd);


-- S2. Frequency segments: size and revenue share.
SELECT frequency_segment,
       COUNT(*)                                                       AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)             AS pct_customers,
       ROUND(SUM(lifetime_spend_usd), 0)                              AS revenue_usd,
       ROUND(100 * SUM(lifetime_spend_usd) / SUM(SUM(lifetime_spend_usd)) OVER (), 1) AS pct_revenue
FROM sales.v_customer_segments
GROUP BY frequency_segment
ORDER BY MIN(orders);


-- S3. Order size bands: where does revenue come from?
WITH order_value AS (
    SELECT order_number, SUM(revenue_usd) AS value
    FROM sales.v_sales_enriched
    GROUP BY order_number
)
SELECT CASE WHEN value < 500   THEN 'Small'
            WHEN value < 3000  THEN 'Medium'
            WHEN value < 10000 THEN 'Large'
            ELSE 'Very large' END                                     AS order_band,
       COUNT(*)                                                       AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)             AS pct_orders,
       ROUND(SUM(value), 0)                                           AS revenue_usd,
       ROUND(100 * SUM(value) / SUM(SUM(value)) OVER (), 1)           AS pct_revenue
FROM order_value
GROUP BY 1
ORDER BY MIN(value);


-- S4. Product price tiers: how much of the catalog vs how much of the revenue?
-- LEFT JOIN keeps products that never sold; COUNT(DISTINCT) avoids fan-out.
SELECT CASE WHEN p.unit_price_usd < 100  THEN 'Budget'
            WHEN p.unit_price_usd < 500  THEN 'Mid'
            WHEN p.unit_price_usd < 1500 THEN 'Premium'
            ELSE 'Luxury' END                                         AS price_tier,
       COUNT(DISTINCT p.product_key)                                  AS products,
       COALESCE(SUM(f.quantity), 0)                                   AS units_sold,
       ROUND(COALESCE(SUM(f.quantity * p.unit_price_usd), 0), 0)      AS revenue_usd,
       ROUND(100 * COALESCE(SUM(f.quantity * p.unit_price_usd), 0)
             / SUM(COALESCE(SUM(f.quantity * p.unit_price_usd), 0)) OVER (), 1) AS pct_revenue
FROM sales.dim_products p
LEFT JOIN sales.fact_sales f ON f.product_key = p.product_key
GROUP BY 1
ORDER BY MIN(p.unit_price_usd);