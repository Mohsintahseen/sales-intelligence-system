"""Forecasting functions with the (train, h) -> array signature used by backtest.py."""
import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

LOG: list[dict] = []     # one entry per forecaster call; cleared by the caller before a real run

RIDGE_ALPHA = 0.1                       # fixed in advance, not tuned
BREAK_START = pd.Timestamp("2020-03-01")

# 12 combinations: d = 1 and D = 1 are fixed so AIC is comparable across the grid
SARIMA_GRID = [((p, 1, q), (P, 1, Q, 12))
               for p in (0, 1) for q in (0, 1) for P, Q in ((0, 0), (0, 1), (1, 0))]


def seasonal_naive(train: pd.Series, h: int) -> np.ndarray:
    n = len(train)
    return np.array([train.iloc[n - 12 + k] for k in range(h)])


def _record(model, train, status, **extra):
    LOG.append({"model": model, "origin": train.index[-1], "status": status, **extra})


def ets_log(train: pd.Series, h: int) -> np.ndarray:
    """Damped-trend additive Holt-Winters on log revenue."""
    ly = np.log(train.astype(float))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            fit = ExponentialSmoothing(ly, trend="add", damped_trend=True, seasonal="add",
                                       seasonal_periods=12, initialization_method="estimated").fit()
            fc = np.exp(np.asarray(fit.forecast(h), dtype=float))
            if np.all(np.isfinite(fc)):
                _record("ETS", train, "ok", n_warnings=len(w),
                        phi=round(float(fit.params["damping_trend"]), 3))
                return fc
            _record("ETS", train, "fallback: non-finite forecast", n_warnings=len(w))
        except Exception as e:
            _record("ETS", train, f"fallback: {type(e).__name__}: {e}", n_warnings=len(w))
    return seasonal_naive(train, h)


def sarima_log(train: pd.Series, h: int) -> np.ndarray:
    """SARIMA on log revenue; order picked by AIC from SARIMA_GRID, converged fits only."""
    ly = np.log(train.astype(float))
    best, n_conv = None, 0
    for order, sorder in SARIMA_GRID:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                fit = SARIMAX(ly, order=order, seasonal_order=sorder,
                              enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
            except Exception:
                continue
        if not fit.mle_retvals.get("converged", False) or not np.isfinite(fit.aic):
            continue
        n_conv += 1
        if best is None or fit.aic < best[0]:
            best = (fit.aic, order, sorder, fit)
    if best is not None:
        fc = np.exp(np.asarray(best[3].forecast(h), dtype=float))
        if np.all(np.isfinite(fc)):
            _record("SARIMA", train, "ok", n_converged=n_conv, order=f"{best[1]}x{best[2]}")
            return fc
    _record("SARIMA", train, "fallback: no usable fit", n_converged=n_conv)
    return seasonal_naive(train, h)


def _design(index: pd.DatetimeIndex, with_break: bool) -> pd.DataFrame:
    """Calendar features: years since Jan 2016, 11 month dummies (January is the base), optional break flag."""
    X = pd.DataFrame(index=index)
    t = (index.year - 2016) * 12 + (index.month - 1)
    X["trend_years"] = np.asarray(t) / 12.0
    for m in range(2, 13):
        X[f"m{m}"] = (index.month == m).astype(float)
    if with_break:
        X["post_break"] = (index >= BREAK_START).astype(float)
    return X


def _ridge(train: pd.Series, h: int, with_break: bool, name: str) -> np.ndarray:
    ly = np.log(train.astype(float))
    X = _design(train.index, with_break)
    future = pd.date_range(train.index[-1] + pd.offsets.MonthBegin(1), periods=h, freq="MS")
    Xf = _design(future, with_break)
    try:
        model = Ridge(alpha=RIDGE_ALPHA).fit(X, ly)
        fc = np.exp(model.predict(Xf))
        if np.all(np.isfinite(fc)):
            coefs = dict(zip(X.columns, model.coef_))
            extra = {"annual_growth_pct": round(100 * (np.exp(coefs["trend_years"]) - 1), 1)}
            if with_break:
                extra["n_post_break_train"] = int(X["post_break"].sum())
                extra["post_break_coef"] = round(float(coefs["post_break"]), 3)
            _record(name, train, "ok", **extra)
            return fc
        _record(name, train, "fallback: non-finite forecast")
    except Exception as e:
        _record(name, train, f"fallback: {type(e).__name__}: {e}")
    return seasonal_naive(train, h)


def ridge_log(train: pd.Series, h: int) -> np.ndarray:
    return _ridge(train, h, False, "Ridge")


def ridge_break_log(train: pd.Series, h: int) -> np.ndarray:
    return _ridge(train, h, True, "Ridge+break")