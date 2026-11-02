-- Module 3.4: JOIN analysis (simulated data; revenue at list price)

-- J1. Revenue by store country, with revenue per store (INNER JOINs).
-- Business use: separates "big because of many stores" from "big per store".
-- Feb 2021 excluded (partial month).
SELECT s.country,
       COUNT(DISTINCT s.store_key)                           AS stores_with_sales,
       ROUND(SUM(f.quantity * p.unit_price_usd), 0)          AS revenue_usd,
       ROUND(SUM(f.quantity * p.unit_price_usd)
             / COUNT(DISTINCT s.store_key), 0)               AS revenue_per_store
FROM sales.fact_sales f
JOIN sales.dim_products p ON p.product_key = f.product_key
JOIN sales.dim_stores   s ON s.store_key   = f.store_key
WHERE f.order_date < DATE '2021-02-01'
GROUP BY s.country
ORDER BY revenue_usd DESC;


-- J1b. Divide by all the stores
SELECT s.country,
       COUNT(DISTINCT s.store_key)                           AS stores_total,
       COUNT(DISTINCT f.store_key)                           AS stores_with_sales,
       ROUND(SUM(f.quantity * p.unit_price_usd), 0)          AS revenue_usd,
       ROUND(SUM(f.quantity * p.unit_price_usd)
             / COUNT(DISTINCT s.store_key), 0)               AS revenue_per_store
FROM sales.dim_stores s
LEFT JOIN sales.fact_sales f
       ON f.store_key = s.store_key
      AND f.order_date < DATE '2021-02-01'
LEFT JOIN sales.dim_products p ON p.product_key = f.product_key
GROUP BY s.country
ORDER BY revenue_per_store DESC;



-- J2. Stores that never made a sale (anti-join with LEFT JOIN ... IS NULL).
-- Business use: candidates for review or closure, or a data problem.
SELECT s.store_key, s.country, s.state, s.square_meters, s.open_date
FROM sales.dim_stores s
LEFT JOIN sales.fact_sales f ON f.store_key = s.store_key
WHERE f.store_key IS NULL
ORDER BY s.country, s.state;


-- J3. Customers who never ordered, by country.
-- The derived table (the subquery in parentheses) reduces the fact table to
-- ONE row per ordering customer first. Joining customers straight to
-- fact_sales would multiply each customer by their number of order lines
-- and inflate every count (a "fan-out").
SELECT c.country,
       COUNT(*)                                              AS customers,
       COUNT(*) FILTER (WHERE o.customer_key IS NULL)        AS never_ordered,
       ROUND(100.0 * COUNT(*) FILTER (WHERE o.customer_key IS NULL)
             / COUNT(*), 1)                                  AS pct_never_ordered
FROM sales.dim_customers c
LEFT JOIN (SELECT DISTINCT customer_key FROM sales.fact_sales) o
       ON o.customer_key = c.customer_key
GROUP BY c.country
ORDER BY customers DESC;


-- J4. Top 10 products by revenue.
-- Business use: where inventory and marketing attention should go.
-- Grouped by product_key (the true identifier), not just the name.
SELECT p.product_name, p.brand, p.category,
       SUM(f.quantity)                                       AS units_sold,
       ROUND(SUM(f.quantity * p.unit_price_usd), 0)          AS revenue_usd
FROM sales.fact_sales f
JOIN sales.dim_products p ON p.product_key = f.product_key
GROUP BY p.product_key, p.product_name, p.brand, p.category
ORDER BY revenue_usd DESC
LIMIT 10;