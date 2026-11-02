-- Validation checks for the loaded data (simulated dataset).
-- Each check has an expected result written next to it.

\echo '--- 1. Row counts (expect 15266, 2517, 67, 11215, 62884, 2557)'
SELECT 'dim_customers' AS tbl, COUNT(*) FROM sales.dim_customers
UNION ALL SELECT 'dim_products', COUNT(*) FROM sales.dim_products
UNION ALL SELECT 'dim_stores', COUNT(*) FROM sales.dim_stores
UNION ALL SELECT 'exchange_rates', COUNT(*) FROM sales.exchange_rates
UNION ALL SELECT 'fact_sales', COUNT(*) FROM sales.fact_sales
UNION ALL SELECT 'dim_date', COUNT(*) FROM sales.dim_date;

\echo '--- 2. Naples customers keep state_code NA (expect 10 rows, 0 NULLs)'
SELECT COUNT(*) FILTER (WHERE state_code = 'NA') AS na_rows,
       COUNT(*) FILTER (WHERE state_code IS NULL) AS null_rows
FROM sales.dim_customers;

\echo '--- 3. Dates (expect 2016-01-01 to 2021-02-20)'
SELECT MIN(order_date) AS first_order, MAX(order_date) AS last_order
FROM sales.fact_sales;

\echo '--- 4. Delivery dates (expect NULL = 49719, online = 13165, none online missing)'
SELECT COUNT(*) FILTER (WHERE delivery_date IS NULL) AS null_delivery,
       COUNT(*) FILTER (WHERE store_key = 0) AS online_lines,
       COUNT(*) FILTER (WHERE store_key = 0 AND delivery_date IS NULL) AS online_missing_delivery
FROM sales.fact_sales;

\echo '--- 5. Product prices (expect cost 0.48-1060.22, price 0.95-3199.99)'
SELECT MIN(unit_cost_usd), MAX(unit_cost_usd),
       MIN(unit_price_usd), MAX(unit_price_usd)
FROM sales.dim_products;

\echo '--- 6. Product 1 spot check (expect cost 6.62, price 12.99)'
SELECT product_key, product_name, unit_cost_usd, unit_price_usd
FROM sales.dim_products WHERE product_key = 1;

\echo '--- 7. Online store (expect NULL square_meters)'
SELECT * FROM sales.dim_stores WHERE store_key = 0;

\echo '--- 8. Overall totals in USD (first look at the KPIs)'
SELECT COUNT(DISTINCT f.order_number) AS orders,
       SUM(f.quantity) AS units,
       ROUND(SUM(f.quantity * p.unit_price_usd), 2) AS revenue_usd,
       ROUND(SUM(f.quantity * p.unit_cost_usd), 2) AS cost_usd,
       ROUND(SUM(f.quantity * (p.unit_price_usd - p.unit_cost_usd)), 2) AS profit_usd
FROM sales.fact_sales f
JOIN sales.dim_products p USING (product_key);

\echo '--- 9. Customers vs source (expect birthday range 1935-02-03 to 2002-02-18)'
SELECT MIN(birthday), MAX(birthday) FROM sales.dim_customers;