"""Reusable data-loading functions. Notebooks and the app import these."""
import pandas as pd

from db import get_engine


def load_sales_enriched() -> pd.DataFrame:
    """Load sales.v_sales_enriched (one row per order line) with proper dtypes."""
    df = pd.read_sql("SELECT * FROM sales.v_sales_enriched", get_engine())
    for col in ["order_date", "delivery_date", "month_start"]:
        df[col] = pd.to_datetime(df[col])
    return df