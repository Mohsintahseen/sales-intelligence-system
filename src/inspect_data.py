from pathlib import Path
import pandas as pd

RAW = Path("data/raw")

for name in ["Customers", "Products", "Sales", "Stores", "Exchange_Rates"]:
    path = RAW / f"{name}.csv"
    try:
        df = pd.read_csv(path)
        encoding = "utf-8"
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin1")
        encoding = "latin1 (utf-8 failed)"
    print(f"\n=== {name}.csv | encoding: {encoding} ===")
    print("Rows, columns:", df.shape)
    print("Columns:", list(df.columns))
    print(df.head(3).to_string())