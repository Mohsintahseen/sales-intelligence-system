-- Sales Intelligence System: schema and table definitions
-- DATA NOTE: all data is SIMULATED (Maven Analytics, Global Electronics Retailer).

DROP SCHEMA IF EXISTS sales CASCADE;   -- makes this script safe to re-run
CREATE SCHEMA sales;
COMMENT ON SCHEMA sales IS 'Simulated electronics retail data (Maven Analytics Global Electronics Retailer)';

-- Dimensions -------------------------------------------------------------

CREATE TABLE sales.dim_customers (
    customer_key  INTEGER PRIMARY KEY,
    gender        TEXT,
    name          TEXT,
    city          TEXT,
    state_code    TEXT,        -- TEXT, not NULL-able junk: 'NA' (Naples) is real data
    state         TEXT,
    zip_code      TEXT,        -- text keeps leading zeros and UK postcodes intact
    country       TEXT,
    continent     TEXT,
    birthday      DATE
);

CREATE TABLE sales.dim_products (
    product_key      INTEGER PRIMARY KEY,
    product_name     TEXT NOT NULL,
    brand            TEXT,
    color            TEXT,
    unit_cost_usd    NUMERIC(10,2) NOT NULL,
    unit_price_usd   NUMERIC(10,2) NOT NULL,
    subcategory_key  INTEGER,
    subcategory      TEXT,
    category_key     INTEGER,
    category         TEXT,
    CHECK (unit_cost_usd >= 0 AND unit_price_usd >= 0)
);

CREATE TABLE sales.dim_stores (
    store_key      INTEGER PRIMARY KEY,   -- key 0 is the Online store
    country        TEXT,
    state          TEXT,
    square_meters  NUMERIC(8,1),          -- NULL for the online store
    open_date      DATE
);

CREATE TABLE sales.dim_date (
    full_date    DATE PRIMARY KEY,
    year         INTEGER NOT NULL,
    quarter      INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    month_name   TEXT NOT NULL,
    day          INTEGER NOT NULL,
    day_of_week  INTEGER NOT NULL,        -- 1 = Monday ... 7 = Sunday (ISO)
    day_name     TEXT NOT NULL,
    is_weekend   BOOLEAN NOT NULL
);

INSERT INTO sales.dim_date
SELECT d::date,
       EXTRACT(YEAR FROM d)::int,
       EXTRACT(QUARTER FROM d)::int,
       EXTRACT(MONTH FROM d)::int,
       TRIM(TO_CHAR(d, 'Month')),
       EXTRACT(DAY FROM d)::int,
       EXTRACT(ISODOW FROM d)::int,
       TRIM(TO_CHAR(d, 'Day')),
       EXTRACT(ISODOW FROM d) IN (6, 7)
FROM generate_series('2015-01-01'::date, '2021-12-31'::date, interval '1 day') AS d;

-- Reference ----------------------------------------------------------------

CREATE TABLE sales.exchange_rates (
    rate_date      DATE NOT NULL,
    currency       CHAR(3) NOT NULL,
    exchange_rate  NUMERIC(10,4) NOT NULL,   -- units of currency per 1 USD
    PRIMARY KEY (rate_date, currency)
);

-- Fact ---------------------------------------------------------------------

CREATE TABLE sales.fact_sales (
    order_number   INTEGER NOT NULL,
    line_item      INTEGER NOT NULL,
    order_date     DATE NOT NULL REFERENCES sales.dim_date (full_date),
    delivery_date  DATE,                      -- NULL = in-store order, nothing delivered
    customer_key   INTEGER NOT NULL REFERENCES sales.dim_customers (customer_key),
    store_key      INTEGER NOT NULL REFERENCES sales.dim_stores (store_key),
    product_key    INTEGER NOT NULL REFERENCES sales.dim_products (product_key),
    quantity       INTEGER NOT NULL CHECK (quantity > 0),
    currency_code  CHAR(3) NOT NULL,
    PRIMARY KEY (order_number, line_item)
);

-- Indexes on the foreign keys we will filter and join on most
CREATE INDEX idx_fact_sales_order_date ON sales.fact_sales (order_date);
CREATE INDEX idx_fact_sales_customer   ON sales.fact_sales (customer_key);
CREATE INDEX idx_fact_sales_product    ON sales.fact_sales (product_key);
CREATE INDEX idx_fact_sales_store      ON sales.fact_sales (store_key);