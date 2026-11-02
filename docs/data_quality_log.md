# Data Quality Log

Dataset: Global Electronics Retailer (Maven Analytics), simulated data.
Profiled with `src/quality_checks.py` and `src/verify_findings.py`.

## Checks that passed
No duplicate keys, no orphan foreign keys, no unparseable dates or prices,
no non-positive quantities, no delivery before order, no cost above price,
and an exchange rate exists for every sale's date and currency.

## Issues found and how the loader handles them

| # | Issue | Handling |
|---|---|---|
| 1 | `Customers.csv` is latin1, not UTF-8 | Read with `encoding="latin1"` |
| 2 | Product cost and price stored as text (`$6.62`) | Strip `$` and `,`, store as NUMERIC |
| 3 | Dates stored as `M/D/YYYY` text | Parsed to DATE |
| 4 | Delivery date blank on 49,719 rows (79%) | Kept NULL; blank means an in-store order, not missing data |
| 5 | State code `NA` (Naples, Italy) read as missing by pandas | Loaded with `keep_default_na=False` |
| 6 | Online store has no square meters | Kept NULL |
| 7 | Data ends 2021-02-20 (partial month) | Excluded from forecasting |
| 8 | No discount column | Discount KPI dropped |
| 9 | One price per product, no price history | Documented as a limitation |