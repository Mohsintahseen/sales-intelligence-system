# AI-Powered Sales Intelligence & Forecasting System

An end-to-end sales analytics platform that answers five business questions: what happened, why it happened, what will happen, what the business should do, and how confident the forecasts are.

> **Status:** Phase 5 complete (sales forecasting) Under active development.

## Planned Features

- Relational sales database in PostgreSQL with SQL-based analysis
- Exploratory data analysis with Python (Pandas, NumPy, Seaborn, Plotly)
- Sales forecasting with statistical and machine learning models, evaluated with MAE, RMSE and MAPE
- Interactive Power BI dashboard
- AI-generated business explanations grounded in verified calculations
- Streamlit web application

## Tech Stack

| Area | Tools |
|---|---|
| Database | PostgreSQL 18, SQL |
| Analysis | Python 3.13, Pandas, NumPy, Matplotlib, Seaborn, Plotly |
| Forecasting | Scikit-learn, Statsmodels |
| BI | Microsoft Power BI |
| App | Streamlit |

## Project Structure

```
app/         Streamlit application
data/        Raw and processed data (not tracked in Git)
docs/        Documentation and diagrams
notebooks/   EDA and forecasting notebooks
reports/     Saved figures and reports
sql/         Schema and analysis queries
src/         Reusable Python modules
tests/       Validation tests
```

## Setup

1. Clone the repository and open the folder.
2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file in the project root:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=sales_intelligence
   DB_USER=postgres
   DB_PASSWORD=your-password
   ```
5. Verify the connection: `python src/test_connection.py`

## Data

**All data in this project is SIMULATED.** It is the *Global Electronics Retailer* dataset published by [Maven Analytics](https://mavenanalytics.io/data-playground/global-electronics-retailer) for a fictitious company. Findings describe this dataset only and are not real-world business observations.

| Table | Rows | Description |
|---|---|---|
| `fact_sales` | 62,884 | Order lines, Jan 2016 to 20 Feb 2021 |
| `dim_customers` | 15,266 | Customers in 8 countries |
| `dim_products` | 2,517 | Products with unit cost and price |
| `dim_stores` | 67 | Physical stores plus the online store (key 0) |
| `dim_date` | 2,557 | Calendar table |
| `exchange_rates` | 11,215 | Daily rates against USD |

The raw CSVs are not stored in this repository. To reproduce the database:

1. Download the dataset from Maven Analytics and place the CSVs in `data/raw/`.
2. Create the schema: `psql -U postgres -d sales_intelligence -f sql/01_create_schema.sql`
3. Load the data: `python src/load_data.py`
4. Validate: `psql -U postgres -d sales_intelligence -f sql/02_validate_load.sql`

### Known limitations

- No discount data exists, so discount analysis is out of scope.
- Each product has a single price, so revenue changes come only from quantity and product mix.
- The simulated margin (about 59%) is far above real retail levels.
- February 2021 is a partial month and is excluded from forecasting.
- About 10% of days each year (a fixed spring window) have no orders, so March and April totals are understated.

See `docs/data_quality_log.md` for the data profiling results.