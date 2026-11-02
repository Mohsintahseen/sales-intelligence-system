-- Module 3.5: subqueries and CTEs (simulated data; revenue at list price)

-- C1. Repeat customer rate (a KPI from Module 2.1).
-- Step 1 (CTE): count orders per customer. Step 2: summarise that.
WITH orders_per_customer AS (
    SELECT customer_key, COUNT(DISTINCT order_number) AS orders
    FROM sales.fact_sales
    GROUP BY customer_key
)
SELECT COUNT(*)                                             AS ordering_customers,
       COUNT(*) FILTER (WHERE orders > 1)                   AS repeat_customers,
       ROUND(100.0 * COUNT(*) FILTER (WHERE orders > 1) / COUNT(*), 1) AS repeat_rate_pct,
       ROUND(AVG(orders), 2)                                AS avg_orders_per_customer,
       MAX(orders)                                          AS max_orders
FROM orders_per_customer;


-- C2. Do a few big spenders carry the business?
-- The CTE is used THREE times below, which is where CTEs beat nested subqueries.
-- Scalar subqueries supply the benchmark (average) and the total.
WITH customer_spend AS (
    SELECT customer_key, SUM(revenue_usd) AS spend
    FROM sales.v_sales_enriched
    GROUP BY customer_key
)
SELECT (SELECT ROUND(AVG(spend), 0) FROM customer_spend)    AS avg_spend,
       COUNT(*)                                             AS customers_above_avg,
       ROUND(SUM(spend), 0)                                 AS their_revenue,
       ROUND(100 * SUM(spend) / (SELECT SUM(spend) FROM customer_spend), 1) AS pct_of_revenue
FROM customer_spend
WHERE spend > (SELECT AVG(spend) FROM customer_spend);


-- C3. Follow-up to J3: where are Australia's never-ordered customers?
-- Is the 45.1% spread evenly, or concentrated in some states?
WITH ordering AS (
    SELECT DISTINCT customer_key FROM sales.fact_sales
)
SELECT c.state,
       COUNT(*)                                             AS customers,
       COUNT(*) FILTER (WHERE o.customer_key IS NULL)       AS never_ordered,
       ROUND(100.0 * COUNT(*) FILTER (WHERE o.customer_key IS NULL) / COUNT(*), 1) AS pct_never_ordered
FROM sales.dim_customers c
LEFT JOIN ordering o ON o.customer_key = c.customer_key
WHERE c.country = 'Australia'
GROUP BY c.state
ORDER BY customers DESC;


-- C4. Hypothesis test: do customers only buy in stores in their own country?
-- (Online orders excluded.) If cross-country purchases are zero, a country's
-- customers depend entirely on that country's physical stores.
SELECT customer_country,
       COUNT(*)                                             AS in_store_lines,
       COUNT(*) FILTER (WHERE store_country = customer_country)  AS same_country_lines,
       COUNT(*) FILTER (WHERE store_country <> customer_country) AS cross_country_lines
FROM sales.v_sales_enriched
WHERE channel = 'In-store'
GROUP BY customer_country
ORDER BY in_store_lines DESC;


-- C5. Do in-store purchases happen in the customer's own state?
-- Grouped by country because state spellings could differ between tables.
SELECT c.country,
       COUNT(*)                                       AS in_store_lines,
       COUNT(*) FILTER (WHERE c.state = s.state)      AS same_state,
       COUNT(*) FILTER (WHERE c.state <> s.state)     AS other_state
FROM sales.fact_sales f
JOIN sales.dim_customers c ON c.customer_key = f.customer_key
JOIN sales.dim_stores    s ON s.store_key    = f.store_key
WHERE f.store_key <> 0
GROUP BY c.country
ORDER BY in_store_lines DESC;


-- C6. South Australia: did the few customers who ordered buy online?
SELECT channel, COUNT(*) AS lines, COUNT(DISTINCT customer_key) AS customers
FROM sales.v_sales_enriched
WHERE customer_country = 'Australia'
  AND customer_key IN (SELECT customer_key FROM sales.dim_customers WHERE state = 'South Australia')
GROUP BY channel;


-- C7. Do customers in states with a dead store avoid in-store buying entirely?
WITH cust AS (
    SELECT c.customer_key, c.country, c.state,
           EXISTS (SELECT 1 FROM sales.fact_sales f
                   WHERE f.customer_key = c.customer_key AND f.store_key <> 0) AS bought_in_store,
           EXISTS (SELECT 1 FROM sales.dim_stores s
                   WHERE s.country = c.country AND s.state = c.state
                     AND s.store_key NOT IN (SELECT store_key FROM sales.fact_sales)) AS state_has_dead_store
    FROM sales.dim_customers c
)
SELECT country,
       state_has_dead_store,
       COUNT(*)                                            AS customers,
       COUNT(*) FILTER (WHERE bought_in_store)             AS in_store_buyers,
       ROUND(100.0 * COUNT(*) FILTER (WHERE bought_in_store) / COUNT(*), 1) AS pct_in_store_buyers
FROM cust
GROUP BY country, state_has_dead_store
ORDER BY country, state_has_dead_store;