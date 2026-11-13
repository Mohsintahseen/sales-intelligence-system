"""Export small snapshot files from PostgreSQL for the Streamlit app.

All data is SIMULATED (Maven Analytics Global Electronics Retailer dataset).

Run from the project root, with the virtual environment active:
    python src/export_snapshots.py

Writes:
    app/snapshots/sales_lines.csv.gz         one row per order line
    app/snapshots/customer_segments.csv.gz   one row per customer

The script re-computes the totals straight from the database and compares
them with the snapshot and with the figures verified in Phases 3 and 6.
It stops with an error if anything differs.
"""
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db import get_engine  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "app" / "snapshots"

# Figures verified earlier (SQL and Power BI reconciliation).
EXPECTED = {
    "rows": 62_884,
    "orders": 26_326,
    "customers": 11_887,
    "revenue": 55_755_479.59,
    "profit": 32_662_688.38,
    "segments": 15_266,
}

LINES_SQL = """
SELECT f.order_number,
       f.line_item,
       f.order_date,
       f.customer_key,
       f.store_key,
       s.country  AS store_country,
       p.category,
       p.subcategory,
       f.quantity,
       f.quantity * p.unit_price_usd                       AS revenue,
       f.quantity * p.unit_cost_usd                        AS cost
FROM sales.fact_sales f
JOIN sales.dim_products p ON p.product_key = f.product_key
JOIN sales.dim_stores   s ON s.store_key   = f.store_key
ORDER BY f.order_date, f.order_number, f.line_item
"""

SEGMENTS_SQL = """
SELECT customer_key,
       value_tier,
       frequency_segment,
       orders,
       lifetime_spend_usd,
       country
FROM sales.v_customer_segments
ORDER BY customer_key
"""

# Independent totals straight from the database (not from the snapshot).
CHECK_SQL = """
SELECT COUNT(*)                                                        AS rows,
       COUNT(DISTINCT f.order_number)                                  AS orders,
       COUNT(DISTINCT f.customer_key)                                  AS customers,
       ROUND(SUM(f.quantity * p.unit_price_usd), 2)                    AS revenue,
       ROUND(SUM(f.quantity * (p.unit_price_usd - p.unit_cost_usd)), 2) AS profit
FROM sales.fact_sales f
JOIN sales.dim_products p USING (product_key)
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = get_engine()

    with engine.connect() as conn:
        lines = pd.read_sql(text(LINES_SQL), conn, parse_dates=["order_date"])
        seg = pd.read_sql(text(SEGMENTS_SQL), conn)
        db = conn.execute(text(CHECK_SQL)).one()

    for col in ["revenue", "cost"]:
        lines[col] = lines[col].astype(float).round(2)
    seg["lifetime_spend_usd"] = seg["lifetime_spend_usd"].astype(float).round(2)

    snap = {
        "rows": len(lines),
        "orders": int(lines["order_number"].nunique()),
        "customers": int(lines["customer_key"].nunique()),
        "revenue": round(float(lines["revenue"].sum()), 2),
        "profit": round(float((lines["revenue"] - lines["cost"]).sum()), 2),
        "segments": len(seg),
    }
    dbv = {"rows": int(db.rows), "orders": int(db.orders), "customers": int(db.customers),
           "revenue": float(db.revenue), "profit": float(db.profit), "segments": len(seg)}

    print(f"{'metric':10s} {'snapshot':>16s} {'database':>16s} {'expected':>16s}")
    problems = []
    for k in EXPECTED:
        s, d, e = snap[k], dbv[k], EXPECTED[k]
        print(f"{k:10s} {s:>16,.2f} {d:>16,.2f} {e:>16,.2f}")
        if abs(s - d) > 0.01 or abs(s - e) > 0.01:
            problems.append(k)

    if problems:
        sys.exit(f"MISMATCH on: {problems}. Nothing was written.")

    lines.to_csv(OUT_DIR / "sales_lines.csv.gz", index=False)
    seg.to_csv(OUT_DIR / "customer_segments.csv.gz", index=False)

    print("\nAll checks passed. Files written:")
    for p in sorted(OUT_DIR.glob("*.csv.gz")):
        print(f"  {p.relative_to(OUT_DIR.parent.parent)}  {p.stat().st_size / 1024:,.0f} KB")
    print("\nDate range:", lines["order_date"].min().date(), "to", lines["order_date"].max().date())
    print("Store countries:", lines["store_country"].nunique(), "| Categories:", lines["category"].nunique())


if __name__ == "__main__":
    main()