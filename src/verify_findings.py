import pandas as pd

c = pd.read_csv("data/raw/Customers.csv", encoding="latin1", keep_default_na=False)
print("Customers with blank or 'NA' State Code:")
print(c[c["State Code"].isin(["", "NA"])][["CustomerKey", "City", "State Code", "State", "Country"]].to_string())

s = pd.read_csv("data/raw/Stores.csv")
print("\nStore 0 and stores with missing size:")
print(s[s["Square Meters"].isna() | (s["StoreKey"] == 0)].to_string())

sales = pd.read_csv("data/raw/Sales.csv")
online = sales["StoreKey"] == 0
print("\nDelivery dates present, online vs in-store:")
print(sales.groupby(online)["Delivery Date"].apply(lambda x: x.notna().sum()).to_string())

d = pd.to_datetime(sales["Order Date"], format="%m/%d/%Y")
print("\nLast 3 months, order lines per month:")
print(d.groupby(d.dt.to_period("M")).size().tail(3).to_string())