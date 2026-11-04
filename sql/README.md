# SQL Scripts

All data is **simulated** (Maven Analytics, Global Electronics Retailer).

Run a file with:
`psql -U postgres -h localhost -p <port> -d sales_intelligence -f sql/<file>`

## Run order

| Step | File | Purpose |
|---|---|---|
| 1 | `01_create_schema.sql` | Creates schema `sales`, tables, indexes, calendar |
| 2 | `python src/load_data.py` | Loads the CSVs |
| 3 | `02_validate_load.sql` | Row counts and spot checks |
| 4 | `03_view_sales_enriched.sql` | View with revenue, cost and profit per order line |
| 5 | `08_view_customer_segments.sql` | View with customer value and frequency segments |
| 6 | `04` to `07`, `09` to `11` | Analysis queries, in any order |

`07_segmentation.sql` uses the view from `08`, so run `08` first.

## Analysis files

| File | Topic |
|---|---|
| `04_kpi_queries.sql` | Overall, yearly, category and channel KPIs |
| `05_join_analysis.sql` | Stores, customers and products across tables |
| `06_subqueries_ctes.sql` | Repeat rate, concentration, state drill-downs |
| `07_segmentation.sql` | Distributions and CASE-based segments |
| `09_date_trends.sql` | Quarterly and monthly trends, seasonality, order gaps |
| `10_window_functions.sql` | Growth rates, trailing totals, rankings, deciles |
| `11_tenure_check.sql` | Whether customer value reflects customer age |

## Conventions

- Revenue is quantity x list price (no discounts or price history in the data).
- February 2021 is partial (data ends 2021-02-20) and is excluded from trends.
- About 35 to 37 days each spring have no orders.