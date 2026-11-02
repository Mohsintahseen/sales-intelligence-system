-- Central analytics view: one row per order line, with revenue, cost and profit.
-- DATA NOTE: simulated data (Maven Analytics Global Electronics Retailer).
-- Revenue is at list price; the dataset has no discounts or price history.

CREATE OR REPLACE VIEW sales.v_sales_enriched AS
SELECT
    f.order_number,
    f.line_item,
    f.order_date,
    f.delivery_date,
    (f.delivery_date - f.order_date)                  AS delivery_days,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    DATE_TRUNC('month', f.order_date)::date           AS month_start,
    f.customer_key,
    c.gender,
    c.country                                         AS customer_country,
    c.continent                                       AS customer_continent,
    f.store_key,
    CASE WHEN f.store_key = 0 THEN 'Online' ELSE 'In-store' END AS channel,
    s.country                                         AS store_country,
    f.product_key,
    p.product_name,
    p.brand,
    p.category,
    p.subcategory,
    f.quantity,
    f.currency_code,
    p.unit_price_usd,
    p.unit_cost_usd,
    f.quantity * p.unit_price_usd                     AS revenue_usd,
    f.quantity * p.unit_cost_usd                      AS cost_usd,
    f.quantity * (p.unit_price_usd - p.unit_cost_usd) AS profit_usd,
    r.exchange_rate,
    ROUND(f.quantity * p.unit_price_usd * r.exchange_rate, 2) AS revenue_local
FROM sales.fact_sales f
LEFT JOIN sales.dim_date       d ON d.full_date    = f.order_date
LEFT JOIN sales.dim_customers  c ON c.customer_key = f.customer_key
LEFT JOIN sales.dim_stores     s ON s.store_key    = f.store_key
LEFT JOIN sales.dim_products   p ON p.product_key  = f.product_key
LEFT JOIN sales.exchange_rates r ON r.rate_date    = f.order_date
                                AND r.currency     = f.currency_code;

COMMENT ON VIEW sales.v_sales_enriched IS
  'One row per order line with USD revenue, cost and profit. Simulated data.';