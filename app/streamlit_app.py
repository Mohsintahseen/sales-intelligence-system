"""Sales Intelligence: Streamlit app (Overview page).

All data is SIMULATED (Maven Analytics Global Electronics Retailer dataset).
The app reads two small snapshot files exported from PostgreSQL by
src/export_snapshots.py, so it runs without a database.

Run from the project root:
    streamlit run app/streamlit_app.py
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

SNAP = Path(__file__).resolve().parent / "snapshots"

TEAL, INDIGO, AMBER = "#2DD4BF", "#8E9BFF", "#F5B544"
PANEL, GRID, TEXT, MUTED = "#121B2E", "#22304D", "#E8EDF7", "#93A3BF"
TIER_COLORS = {"No purchases": "#5B6B8C", "Bronze": "#C08A5A", "Silver": "#A9B4C6",
               "Gold": AMBER, "Platinum": "#4FB3E8"}
TIER_ORDER = ["No purchases", "Bronze", "Silver", "Gold", "Platinum"]
BREAK = pd.Timestamp("2020-03-01")
PARTIAL_FROM = pd.Timestamp("2021-02-01")  # Feb 2021 is a partial month

st.set_page_config(page_title="Sales Intelligence", page_icon=None, layout="wide")


@st.cache_data
def load_data():
    lines = pd.read_csv(SNAP / "sales_lines.csv.gz", parse_dates=["order_date"])
    seg = pd.read_csv(SNAP / "customer_segments.csv.gz")
    lines["year"] = lines["order_date"].dt.year
    lines["profit"] = lines["revenue"] - lines["cost"]
    return lines, seg


def money(v: float) -> str:
    return f"${v / 1e6:,.1f}M" if abs(v) >= 1e6 else f"${v:,.0f}"


def style(fig: go.Figure, title: str, height: int = 330) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=TEXT), x=0.02),
        paper_bgcolor=PANEL, plot_bgcolor=PANEL, font=dict(color=MUTED, size=12),
        height=height, margin=dict(l=50, r=20, t=55, b=40),
        legend=dict(orientation="h", y=1.12, x=1, xanchor="right", font=dict(color=MUTED)),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    return fig


lines, seg = load_data()

# ---------- sidebar filters ----------
st.sidebar.header("Filters")
years = sorted(lines["year"].unique())
countries = sorted(lines["store_country"].unique())
categories = sorted(lines["category"].unique())
sel_years = st.sidebar.multiselect("Year", years, default=years)
sel_countries = st.sidebar.multiselect("Store country", countries, default=countries)
sel_cats = st.sidebar.multiselect("Category", categories, default=categories)
st.sidebar.caption("The customer tier chart covers all customers and ignores these filters.")

df = lines[lines["year"].isin(sel_years)
           & lines["store_country"].isin(sel_countries)
           & lines["category"].isin(sel_cats)]

# ---------- header ----------
st.title("Sales Intelligence")
st.caption("Executive overview · Global electronics retailer · SIMULATED DATA (Maven Analytics dataset)")

if df.empty:
    st.warning("No data for these filters. Pick at least one value in each filter.")
    st.stop()

# ---------- KPI row ----------
revenue, profit = df["revenue"].sum(), df["profit"].sum()
orders, customers = df["order_number"].nunique(), df["customer_key"].nunique()
cols = st.columns(6)
cols[0].metric("Revenue", money(revenue))
cols[1].metric("Profit", money(profit))
cols[2].metric("Profit margin", f"{profit / revenue:.1%}")
cols[3].metric("Orders", f"{orders:,}")
cols[4].metric("Customers", f"{customers:,}")
cols[5].metric("Avg. order value", f"${revenue / orders:,.0f}")

# ---------- monthly revenue + yearly columns ----------
left, right = st.columns([3, 2])

full = df[df["order_date"] < PARTIAL_FROM]
monthly = (full.assign(month=full["order_date"].dt.to_period("M").dt.to_timestamp())
           .groupby("month", as_index=False)["revenue"].sum())
fig = go.Figure(go.Scatter(x=monthly["month"], y=monthly["revenue"] / 1e6, mode="lines",
                           line=dict(color=TEAL, width=2.5), name="Revenue",
                           hovertemplate="%{x|%b %Y}: $%{y:.2f}M<extra></extra>"))
if not monthly.empty and monthly["month"].min() <= BREAK <= monthly["month"].max():
    fig.add_shape(type="line", x0=BREAK, x1=BREAK, y0=0, y1=1, yref="paper",
                  line=dict(color=AMBER, width=1.5, dash="dash"))
    fig.add_annotation(x=BREAK, y=1, yref="paper", text="Break begins Mar 2020", showarrow=False,
                       xanchor="left", xshift=6, font=dict(color=AMBER, size=11))
fig.update_yaxes(tickprefix="$", ticksuffix="M", rangemode="tozero")
fig.update_layout(showlegend=False)
left.plotly_chart(style(fig, "Monthly revenue (USD millions, excludes partial Feb 2021)"))

yearly = (df[df["year"] <= 2020].groupby("year", as_index=False)[["revenue", "profit"]].sum())
if yearly.empty:
    right.info("No full years in the current selection.")
else:
    fig = go.Figure()
    fig.add_bar(x=yearly["year"], y=yearly["revenue"] / 1e6, name="Revenue", marker_color=TEAL,
                text=(yearly["revenue"] / 1e6).round(1), textposition="outside")
    fig.add_bar(x=yearly["year"], y=yearly["profit"] / 1e6, name="Profit", marker_color=INDIGO,
                text=(yearly["profit"] / 1e6).round(1), textposition="outside")
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category")
    fig.update_yaxes(ticksuffix="M", rangemode="tozero")
    right.plotly_chart(style(fig, "Revenue and profit by year (USD millions, full years)"))

# ---------- category, customer tier, country ----------
c1, c2, c3 = st.columns(3)

cat = df.groupby("category")["revenue"].sum().sort_values()
fig = go.Figure(go.Bar(x=cat.values / 1e6, y=cat.index, orientation="h", marker_color=TEAL,
                       text=[f"{v / 1e6:,.1f}M" for v in cat.values], textposition="outside"))
fig.update_xaxes(visible=False)
c1.plotly_chart(style(fig, "Revenue by category", 340))

tiers = seg["value_tier"].value_counts()
order = [t for t in TIER_ORDER if t in tiers.index] + [t for t in tiers.index if t not in TIER_ORDER]
tiers = tiers.reindex(order)
fig = go.Figure(go.Pie(labels=tiers.index, values=tiers.values, hole=0.62, sort=False,
                       marker=dict(colors=[TIER_COLORS.get(t, "#4FB3E8") for t in tiers.index],
                                   line=dict(color=PANEL, width=2)),
                       textinfo="percent", textfont=dict(color="#0B1220")))
fig.add_annotation(text=f"{tiers.sum():,}<br>customers", showarrow=False, font=dict(color=TEXT, size=15))
fig.update_layout(legend=dict(orientation="v", y=0.5, x=1.0, xanchor="left"))
c2.plotly_chart(style(fig, "Customers by value tier (all time)", 340))

ctry = df.groupby("store_country")["revenue"].sum().sort_values()
fig = go.Figure(go.Bar(x=ctry.values / 1e6, y=ctry.index, orientation="h", marker_color=INDIGO,
                       text=[f"{v / 1e6:,.1f}M" for v in ctry.values], textposition="outside"))
fig.update_xaxes(visible=False)
c3.plotly_chart(style(fig, "Revenue by store country", 340))

st.caption("Simulated data (Maven Analytics Global Electronics Retailer). KPIs cover Jan 2016 to Feb 20, 2021; "
           "the monthly trend and yearly chart exclude partial periods.")