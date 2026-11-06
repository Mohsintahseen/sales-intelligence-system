"""Rolling-origin backtesting utilities (decision D3, Phase 5)."""
from typing import Callable

import numpy as np
import pandas as pd

H = 3                                  # forecast horizon in months
MIN_TRAIN = 36                         # first origin trains on Jan 2016 to Dec 2018
BREAK = pd.Timestamp("2020-03-01")     # first month of the 2020 collapse (Module 4.6)

# A forecaster takes (training series, horizon) and returns h forecasts
Forecaster = Callable[[pd.Series, int], np.ndarray]


def rolling_origin(y: pd.Series, forecaster: Forecaster, h: int = H,
                   min_train: int = MIN_TRAIN) -> pd.DataFrame:
    """Expanding-window backtest. The forecaster only ever receives data up to the origin."""
    rows = []
    for n in range(min_train, len(y) - h + 1):
        train, actual = y.iloc[:n], y.iloc[n:n + h]
        fc = np.asarray(forecaster(train.copy(), h), dtype=float)
        assert fc.shape == (h,), "forecaster must return exactly h values"
        for k in range(h):
            rows.append({"origin": train.index[-1], "origin_n": n, "h": k + 1,
                         "target": actual.index[k], "actual": actual.iloc[k],
                         "forecast": fc[k]})
    return pd.DataFrame(rows)


def add_regime(bt: pd.DataFrame) -> pd.DataFrame:
    """Label each origin by whether its whole forecast window is before the 2020 break."""
    bt = bt.copy()
    last_target = bt.groupby("origin")["target"].transform("max")
    bt["regime"] = np.where(last_target < BREAK, "pre-break", "touches 2020 break")
    return bt


def metrics(df: pd.DataFrame) -> pd.Series:
    """MAE, RMSE, MAPE, WAPE and signed bias (positive bias = over-forecasting)."""
    e = df["forecast"] - df["actual"]
    return pd.Series({
        "n": len(df),
        "MAE": e.abs().mean(),
        "RMSE": np.sqrt((e ** 2).mean()),
        "MAPE_%": 100 * (e.abs() / df["actual"]).mean(),
        "WAPE_%": 100 * e.abs().sum() / df["actual"].sum(),
        "bias_%": 100 * e.sum() / df["actual"].sum(),
    })


def summarise(bt: pd.DataFrame) -> pd.DataFrame:
    """Metrics per regime, with and without March/April (the spring-gap months, decision D2)."""
    groups = {"pre-break": bt[bt["regime"] == "pre-break"],
              "touches 2020 break": bt[bt["regime"] != "pre-break"],
              "all origins": bt}
    parts = {}
    for name, g in groups.items():
        parts[(name, "all months")] = metrics(g)
        parts[(name, "excl. Mar/Apr")] = metrics(g[~g["target"].dt.month.isin([3, 4])])
    return pd.DataFrame(parts).T


def leakage_check(y: pd.Series, forecaster: Forecaster, h: int = H,
                  min_train: int = MIN_TRAIN, n_scrambled: int = 12):
    """Scramble the last n_scrambled months. Forecasts from origins whose training data
    does not include those months must be identical; if not, the forecaster is peeking.
    Returns (passed, number_of_forecasts_compared)."""
    a = rolling_origin(y, forecaster, h, min_train)
    y2 = y.copy()
    y2.iloc[-n_scrambled:] = y.iloc[-n_scrambled:].values[::-1] * 7.0
    b = rolling_origin(y2, forecaster, h, min_train)
    safe = a["origin_n"] <= len(y) - n_scrambled
    return bool(np.allclose(a.loc[safe, "forecast"], b.loc[safe, "forecast"])), int(safe.sum())