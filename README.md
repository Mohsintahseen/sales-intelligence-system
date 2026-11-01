# AI-Powered Sales Intelligence & Forecasting System

An end-to-end sales analytics platform that answers five business questions: what happened, why it happened, what will happen, what the business should do, and how confident the forecasts are.

> **Status:** Phase 1 complete (environment setup). Under active development.

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

Dataset details will be added in Phase 2. Any simulated data will be clearly labeled as such.