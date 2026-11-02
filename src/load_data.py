"""Load the Global Electronics Retailer CSVs into the PostgreSQL 'sales' schema.

DATA NOTE: the dataset is SIMULATED (Maven Analytics).
Cleaning rules applied here come from the Module 2.4 data quality log.
"""
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine

RAW = Path("data/raw")
DATE_FMT = "%m/%d/%Y"
CHUNK = 5000


def read_csv(name: str, **kwargs) -> pd.DataFrame:
    """Read a raw CSV. Only truly empty cells become missing, so the text 'NA'
    (Naples, Italy) is kept as real data."""
    return pd.read_csv(
        RAW / name, keep_default_na=False, na_values=[""], **kwargs
    )


def parse_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, format=DATE_FMT).dt.date


def parse_money(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.str.replace(r"[$,]", "", regex=True))


def load_customers() -> pd.DataFrame:
    df = read_csv("Customers.csv", encoding="latin1", dtype={"Zip Code": str})
    return pd.DataFrame({
        "customer_key": df["CustomerKey"],
        "gender": df["Gender"],
        "name": df["Name"],
        "city": df["City"],
        "state_code": df["State Code"],
        "state": df["State"],
        "zip_code": df["Zip Code"],
        "country": df["Country"],
        "continent": df["Continent"],
        "birthday": parse_date(df["Birthday"]),
    })


def load_products() -> pd.DataFrame:
    df = read_csv("Products.csv")
    return pd.DataFrame({
        "product_key": df["ProductKey"],
        "product_name": df["Product Name"],
        "brand": df["Brand"],
        "color": df["Color"],
        "unit_cost_usd": parse_money(df["Unit Cost USD"]),
        "unit_price_usd": parse_money(df["Unit Price USD"]),
        "subcategory_key": df["SubcategoryKey"],
        "subcategory": df["Subcategory"],
        "category_key": df["CategoryKey"],
        "category": df["Category"],
    })


def load_stores() -> pd.DataFrame:
    df = read_csv("Stores.csv")
    return pd.DataFrame({
        "store_key": df["StoreKey"],
        "country": df["Country"],
        "state": df["State"],
        "square_meters": df["Square Meters"],
        "open_date": parse_date(df["Open Date"]),
    })


def load_rates() -> pd.DataFrame:
    df = read_csv("Exchange_Rates.csv")
    return pd.DataFrame({
        "rate_date": parse_date(df["Date"]),
        "currency": df["Currency"],
        "exchange_rate": df["Exchange"],
    })


def load_sales() -> pd.DataFrame:
    df = read_csv("Sales.csv")
    return pd.DataFrame({
        "order_number": df["Order Number"],
        "line_item": df["Line Item"],
        "order_date": parse_date(df["Order Date"]),
        # Blank delivery date = in-store order; stays NULL in the database
        "delivery_date": pd.to_datetime(df["Delivery Date"], format=DATE_FMT).dt.date,
        "customer_key": df["CustomerKey"],
        "store_key": df["StoreKey"],
        "product_key": df["ProductKey"],
        "quantity": df["Quantity"],
        "currency_code": df["Currency Code"],
    })


def main() -> None:
    # (table name, builder function) in dependency order: dimensions before facts
    steps = [
        ("dim_customers", load_customers),
        ("dim_products", load_products),
        ("dim_stores", load_stores),
        ("exchange_rates", load_rates),
        ("fact_sales", load_sales),
    ]
    engine = get_engine()

    # engine.begin() = one transaction: all tables load, or none do
    with engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE sales.fact_sales, sales.dim_customers, sales.dim_products, "
            "sales.dim_stores, sales.exchange_rates"
        ))
        for table, builder in steps:
            df = builder()
            df.to_sql(table, conn, schema="sales", if_exists="append",
                      index=False, method="multi", chunksize=CHUNK)
            print(f"Loaded {len(df):>6} rows into sales.{table}")

    print("Done. All tables committed.")


if __name__ == "__main__":
    main()