"""Sales Intelligence: Forecast page.

All data is SIMULATED (Maven Analytics Global Electronics Retailer dataset).
Reads snapshot files only: no database is needed.
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

SNAP = Path(__file__).resolve().parent / "snapshots"

TEAL, INDIGO, AMBER = "#2DD4BF", "#8E9BFF", "#F5B544"
PANEL, GRID, TEXT, MUTED = "#121B2E", "#22304D", "#E8EDF7", "#93A3BF"
BREAK = pd.Timestamp("2020-03-01")
PARTIAL_FROM = pd.Timestamp("2021-02-01")


@st.cache_data
def load_data():
    lines = pd.read_csv(SNAP / "sales_lines.csv.gz", usecols=["order_date", "revenue"],
                        parse_dates=["order_date"])
    full = lines[lines["order_date"] < PARTIAL_FROM]
    monthly = (full.assign(month=full["order_date"].dt.to_period("M").dt.to_timestamp())
               .groupby("month", as_index=False)["revenue"].sum())
    fc = pd.read_csv(SNAP / "forecast_feb_jul_2021.csv", parse_dates=["month"])
    board = pd.read_csv(SNAP / "model_scoreboard.csv")
    return monthly, fc, board


def m(v: float) -> str:
    return f"${v / 1e6:,.2f}M"


def style(fig: go.Figure, title: str, height: int = 420) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=TEXT), x=0.02),
        paper_bgcolor=PANEL, plot_bgcolor=PANEL, font=dict(color=MUTED, size=12),
        height=height, margin=dict(l=50, r=20, t=60, b=40),
        legend=dict(orientation="h", y=1.1, x=1, xanchor="right", font=dict(color=MUTED)),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    return fig


monthly, fc, board = load_data()
ets = board.loc[board["model"] == "ETS"].iloc[0]

st.title("Forecast: Feb to Jul 2021")
st.caption("ETS (damped Holt-Winters on log revenue) · SIMULATED DATA · "
           "a forecast with stated limits, not a promise")

# ---------- headline numbers ----------
c = st.columns(4)
c[0].metric("ETS forecast, Feb to Jul 2021", m(fc["forecast"].sum()),
            help="Sum of the six monthly point forecasts. No interval is given for the total, "
                 "because monthly errors are correlated.")
c[1].metric("Ridge+break scenario", m(fc["ridge_break"].sum()),
            help="Optimistic scenario: assumes pre-2020 growth resumes. It lost to ETS in the backtest.")
c[2].metric("ETS error in stable months", f"{ets['pre_break_wape']:.1f}% WAPE",
            help="Backtest, 12 origins before the 2020 break.")
c[3].metric("ETS error around the break", f"{ets['break_wape']:.1f}% WAPE",
            help="Backtest, 11 origins whose forecasts touch the 2020 break.")

# ---------- chart ----------
WINDOWS = {"Since the break (Mar 2020)": "2020-03-01",
           "Since Jan 2019": "2019-01-01",
           "Full history (from 2016)": "2016-01-01"}
window = st.radio("Time window", list(WINDOWS), horizontal=True)
hist = monthly[monthly["month"] >= WINDOWS[window]]


def band(lo, hi, fill, name):
    x = list(fc["month"]) + list(fc["month"][::-1])
    y = list(hi / 1e6) + list((lo / 1e6)[::-1])
    return go.Scatter(x=x, y=y, mode="lines", fill="toself", fillcolor=fill, line=dict(width=0),
                      hoverinfo="skip", name=name)


fig = go.Figure()
fig.add_trace(band(fc["wide_lo"], fc["wide_hi"], "rgba(245,181,68,0.14)", "Regime-risk band (80%)"))
fig.add_trace(band(fc["stable_lo"], fc["stable_hi"], "rgba(245,181,68,0.34)", "Stable-regime band (80%)"))
fig.add_trace(go.Scatter(x=hist["month"], y=hist["revenue"] / 1e6, mode="lines", name="Actual",
                         line=dict(color=TEAL, width=2.5),
                         hovertemplate="%{x|%b %Y}: $%{y:.2f}M<extra>Actual</extra>"))
last = hist.iloc[-1]
fig.add_trace(go.Scatter(x=[last["month"], fc["month"].iloc[0]],
                         y=[last["revenue"] / 1e6, fc["forecast"].iloc[0] / 1e6], mode="lines",
                         line=dict(color=AMBER, width=1.5, dash="dot"), showlegend=False, hoverinfo="skip"))
fig.add_trace(go.Scatter(x=fc["month"], y=fc["forecast"] / 1e6, mode="lines+markers", name="ETS forecast",
                         line=dict(color=AMBER, width=2.5), marker=dict(size=7),
                         hovertemplate="%{x|%b %Y}: $%{y:.2f}M<extra>ETS forecast</extra>"))
fig.add_trace(go.Scatter(x=fc["month"], y=fc["ridge_break"] / 1e6, mode="lines+markers",
                         name="Ridge+break (scenario)", line=dict(color=INDIGO, width=2, dash="dash"),
                         marker=dict(size=5), hovertemplate="%{x|%b %Y}: $%{y:.2f}M<extra>Ridge+break</extra>"))
if hist["month"].min() <= BREAK:
    fig.add_shape(type="line", x0=BREAK, x1=BREAK, y0=0, y1=1, yref="paper",
                  line=dict(color=MUTED, width=1, dash="dash"))
    fig.add_annotation(x=BREAK, y=1, yref="paper", text="Break begins Mar 2020", showarrow=False,
                       xanchor="left", xshift=6, font=dict(color=MUTED, size=11))
fig.update_yaxes(tickprefix="$", ticksuffix="M", rangemode="tozero")
st.plotly_chart(style(fig, "Monthly revenue: actual and forecast (USD millions)"))

# ---------- forecast table ----------
ly = monthly.set_index("month")["revenue"]


def vs_2019(month, value):
    base = ly.get(month - pd.DateOffset(years=2))
    return f"{value / base - 1:+.0%}" if base else "n/a"


table = pd.DataFrame({
    "Month": fc["month"].dt.strftime("%b %Y"),
    "ETS forecast": [m(v) for v in fc["forecast"]],
    "Stable band": [f"{m(a)} to {m(b)}" for a, b in zip(fc["stable_lo"], fc["stable_hi"])],
    "Regime-risk band": [f"{m(a)} to {m(b)}" for a, b in zip(fc["wide_lo"], fc["wide_hi"])],
    "Ridge+break": [m(v) for v in fc["ridge_break"]],
    "ETS vs same month 2019": [vs_2019(mo, v) for mo, v in zip(fc["month"], fc["forecast"])],
})
st.subheader("Forecast table")
st.dataframe(table, hide_index=True, width="stretch")
st.caption("Comparing with 2019 (the last pre-break year) is fairer than comparing with 2020, "
           "whose later months were already depressed. April is the least reliable month: "
           "its forecast is about as low as the lowest April on record, so read its band as leaning upward.")

# ---------- how the bands work ----------
st.subheader("How to read the bands")
st.markdown(
    "- **Stable-regime band** (forecast x0.79 to x1.01): built from backtest errors in calm periods. "
    "It covered only **18%** of actual outcomes in the months around the 2020 break, so it is too narrow "
    "if another shift happens.\n"
    "- **Regime-risk band** (forecast x0.52 to x1.17): built from all 69 backtest errors, including the break. "
    "It still covered only **61%** of break-period outcomes, even though those errors were used to build it.\n"
    "- Neither is a guarantee. Both come from the model's own past mistakes, with no distribution assumed."
)

# ---------- scoreboard ----------
st.subheader("How the models compared in the backtest")
fig = go.Figure()
fig.add_bar(x=board["model"], y=board["pre_break_wape"], name="Stable months", marker_color=TEAL,
            text=board["pre_break_wape"].round(1), textposition="outside")
fig.add_bar(x=board["model"], y=board["break_wape"], name="Months touching the 2020 break",
            marker_color=AMBER, text=board["break_wape"].round(1), textposition="outside")
fig.update_layout(barmode="group")
fig.update_yaxes(ticksuffix="%", rangemode="tozero")
st.plotly_chart(style(fig, "Forecast error by model (WAPE %, lower is better)", 380))
st.caption("23 rolling-origin backtests, 3 months ahead, 69 forecasts in total. ETS is the primary model: "
           "best in the break period and close to the best in stable months. ETS+Ridge is better in stable "
           "months but fails at the break, and was chosen after seeing the results.")
with st.expander("Full scoreboard"):
    st.dataframe(board.rename(columns={
        "model": "Model", "pre_break_wape": "Stable WAPE %", "pre_break_bias": "Stable bias %",
        "break_wape": "Break WAPE %", "break_bias": "Break bias %",
        "mar_oct_2020_wape": "Mar-Oct 2020 WAPE %"}), hide_index=True, width="stretch")

# ---------- limitations ----------
with st.expander("Limitations"):
    st.markdown(
        "1. **One structural break.** Everything about break behaviour rests on one event and about six "
        "informative months.\n"
        "2. **One post-break year.** Seasonal patterns come mostly from 2016 to 2019 and may not hold now.\n"
        "3. **The 2020 drop may or may not be permanent.** The forecast assumes the new level persists.\n"
        "4. **Ridge+break was designed after seeing the break,** so it is an optimistic scenario, not a "
        "competing forecast.\n"
        "5. **Single monthly total.** No product, store or country forecasts, and no outside drivers.\n"
        "6. **The data is simulated.** The conclusions are about method, not about a real business."
    )

st.caption("Simulated data (Maven Analytics Global Electronics Retailer).")