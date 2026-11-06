"""The monthly revenue series used for forecasting (decision D1, Phase 5)."""
import pandas as pd

from db import get_engine

QUERY = """
    SELECT month_start, SUM(revenue_usd) AS revenue
    FROM sales.v_sales_enriched
    WHERE order_date < DATE '2021-02-01'      -- Feb 2021 is partial (data ends 2021-02-20)
    GROUP BY month_start
    ORDER BY month_start
"""


def load_monthly_revenue() -> pd.Series:
    """Monthly revenue in USD, Jan 2016 to Jan 2021, as a float series with a month-start index."""
    df = pd.read_sql(QUERY, get_engine())
    s = pd.Series(df["revenue"].astype(float).values,
                  index=pd.DatetimeIndex(pd.to_datetime(df["month_start"]), name="month"),
                  name="revenue")
    return s.asfreq("MS")      # explicit monthly frequency; would insert NaN for any missing month