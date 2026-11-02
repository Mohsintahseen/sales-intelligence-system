from pathlib import Path
import pandas as pd

RAW = Path("data/raw")

customers = pd.read_csv(RAW / "Customers.csv", encoding="latin1")
products = pd.read_csv(RAW / "Products.csv")
sales = pd.read_csv(RAW / "Sales.csv")
stores = pd.read_csv(RAW / "Stores.csv")
rates = pd.read_csv(RAW / "Exchange_Rates.csv")

tables = {"Customers": customers, "Products": products, "Sales": sales,
          "Stores": stores, "Exchange_Rates": rates}


def header(title):
    print(f"\n=== {title} ===")


header("1. Missing values (columns with at least one)")
for name, df in tables.items():
    nulls = df.isna().sum()
    print(name, nulls[nulls > 0].to_dict() or "none")

header("2. Duplicates")
print("Sales duplicate (Order Number, Line Item):",
      sales.duplicated(["Order Number", "Line Item"]).sum())
print("Sales fully duplicated rows:", sales.duplicated().sum())
print("Duplicate CustomerKey:", customers["CustomerKey"].duplicated().sum())
print("Duplicate ProductKey:", products["ProductKey"].duplicated().sum())
print("Duplicate StoreKey:", stores["StoreKey"].duplicated().sum())

header("3. Sales keys with no match in the parent table")
for col, parent in [("CustomerKey", customers), ("ProductKey", products),
                    ("StoreKey", stores)]:
    missing = ~sales[col].isin(parent[col])
    print(f"{col}: {missing.sum()} rows, "
          f"{sales.loc[missing, col].nunique()} distinct keys not found")

header("4. Dates")
order_dt = pd.to_datetime(sales["Order Date"], format="%m/%d/%Y", errors="coerce")
deliv_dt = pd.to_datetime(sales["Delivery Date"], format="%m/%d/%Y", errors="coerce")
print("Order date range:", order_dt.min().date(), "to", order_dt.max().date())
print("Unparseable order dates:", order_dt.isna().sum())
print("Blank delivery dates:", deliv_dt.isna().sum())
print("Blank delivery dates where StoreKey = 0:",
      (deliv_dt.isna() & (sales["StoreKey"] == 0)).sum())
print("Rows with StoreKey = 0:", (sales["StoreKey"] == 0).sum())
print("Delivery before order:", (deliv_dt < order_dt).sum())

header("5. Quantity")
print(sales["Quantity"].describe().to_string())
print("Quantity <= 0:", (sales["Quantity"] <= 0).sum())

header("6. Product prices")
cost = pd.to_numeric(products["Unit Cost USD"].str.replace(r"[$,]", "", regex=True),
                     errors="coerce")
price = pd.to_numeric(products["Unit Price USD"].str.replace(r"[$,]", "", regex=True),
                      errors="coerce")
print("Unparseable cost:", cost.isna().sum(), "| unparseable price:", price.isna().sum())
print("Cost range:", cost.min(), "to", cost.max())
print("Price range:", price.min(), "to", price.max())
print("Cost greater than price:", (cost > price).sum())

header("7. Currencies and exchange rates")
print("Sales currencies:\n", sales["Currency Code"].value_counts().to_string())
print("Rate currencies:", sorted(rates["Currency"].unique()))
rate_keys = set(zip(pd.to_datetime(rates["Date"], format="%m/%d/%Y"), rates["Currency"]))
sale_keys = list(zip(order_dt, sales["Currency Code"]))
unmatched = sum(1 for k in sale_keys if k not in rate_keys)
print("Sales rows with no exchange rate for their date and currency:", unmatched)

header("8. Customers and stores")
print(customers["Gender"].value_counts(dropna=False).to_string())
birth = pd.to_datetime(customers["Birthday"], format="%m/%d/%Y", errors="coerce")
print("Birthday range:", birth.min().date(), "to", birth.max().date())
print("Unparseable birthdays:", birth.isna().sum())
print("Customer countries:\n", customers["Country"].value_counts().to_string())
print("Store countries:\n", stores["Country"].value_counts().to_string())