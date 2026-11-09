# Phase 5 Findings: Sales Forecasting

> **All data in this project is simulated** (Maven Analytics Global Electronics Retailer dataset). The results below demonstrate a forecasting methodology. They are not evidence about any real business.

## 1. Question and setup

**Question:** Can we forecast monthly revenue for the next six months (Feb to Jul 2021), and how far should the forecast be trusted?

- **Series:** monthly revenue, Jan 2016 to Jan 2021 (61 months). Feb 2021 is partial and excluded.
- **Source:** `sales.v_sales_enriched`, loaded by `src/series.py`.
- **Transform:** natural log, because seasonality is multiplicative (seasonal swings grow with the level).
- **Known structure:** a spring order gap each year (35 to 37 consecutive zero-order days, about Mar 18 to Apr 23), and a **structural break in 2020** (annual revenue -49%, new customers -66.6%, trailing-12-month revenue from $18.52M in Feb 2020 to $7.74M in Jan 2021).

## 2. How models were judged

Rolling-origin backtest (`src/backtest.py`): expanding window, minimum 36 training months, horizon 3, **23 origins, 69 forecasts, 25 distinct target months**.

Results are split by regime because one pooled number would hide the break:

| Regime | Origins | Forecasts |
|---|---|---|
| Pre-break | 12 | 36 |
| Touches the 2020 break | 11 | 33 |

Metrics: MAE, RMSE, MAPE, WAPE and bias. WAPE is the headline because several months have very small revenue, which inflates MAPE.

## 3. Scoreboard (WAPE %, bias % in brackets)

| Model | Pre-break | Touches break | Mar-Oct 2020 origins |
|---|---|---|---|
| Seasonal naive | 25.4 (-25.4) | 131.8 (+126.4) | 229.5 (+228.4) |
| **ETS** (damped Holt-Winters on log) | 10.3 (+8.1) | **50.3 (+36.6)** | **76.6 (+55.8)** |
| SARIMA (12-combo grid, AIC) | 19.8 (+18.5) | 57.6 (+51.9) | 83.6 (+74.9) |
| Ridge (trend + month dummies) | 12.1 (-8.8) | 152.7 (+151.4) | 256.1 (+255.9) |
| Ridge+break (adds post-Mar-2020 flag) | 12.1 (-8.8) | 86.1 (+84.2) | 132.5 (+131.3) |
| ETS+Ridge (50/50 average) | **6.5 (-0.3)** | 96.1 (+94.0) | 156.4 (+155.9) |
| ETS+SARIMA (50/50 average) | 14.3 (+13.3) | 52.9 (+44.3) | 79.8 (+65.4) |

**Reading the table**

- **ETS is the most robust model.** It beat seasonal naive at 12 of 12 pre-break origins and beat SARIMA at 10 of 12. Its advantage in the break regime comes entirely from the six origins May to Oct 2020, which is thin evidence.
- **Ridge is competitive when the regime is stable** (it beats ETS at 6 of 12 pre-break origins) **and fails at the break** (0 of 11). A fixed linear trend cannot see a structural collapse.
- **Ridge+break reduces the damage but is not a fix.** The flag is learned from only 1 to 8 post-break months, so it adapts too slowly. It also was designed after seeing the break, so its score is a best case, not what it would have achieved in real time.
- **ETS+Ridge has the best stable-regime accuracy** because the two models' biases cancel (ETS +8.1, Ridge -8.8). This pair was chosen after looking at the same backtest, on 12 origins, so the 3.8-point gain is suggestive only. It was not adopted, because its gain disappears in the regime we are now in.
- **ETS+SARIMA is worse than ETS alone** in both regimes.

## 4. The 2020 stress test (ETS, one-month-ahead)

| Target | Error vs actual |
|---|---|
| Mar 2020 | +31% (made before the break was visible, so unforecastable) |
| Apr 2020 | -27% (tiny base, about $0.06M) |
| May 2020 | +90% |
| Jun 2020 | +61% |
| Jul 2020 | +71% |
| Aug 2020 | +52% |
| Sep 2020 | +10% |
| Oct 2020 | +25% |
| Nov 2020 | -14% |

ETS kept expecting the normal post-spring rebound for about five months after the break, then adapted. Error spread (standard deviation of log error) was 0.10 pre-break and **0.53** in the break regime, about five times larger.

## 5. Uncertainty bands

Bands are empirical: quantiles of the backtest log errors, applied to the forecast as multipliers. No distributional assumption.

| Band | Built from | Multiplier (80%) | Coverage |
|---|---|---|---|
| Stable-regime | 36 pre-break errors | x0.79 to x1.01 | Pre-break 28/36 (78%, in-sample). **Break 6/33 (18%).** |
| Regime-risk | all 69 errors | x0.52 to x1.17 | Pre-break 35/36 (97%). Break 20/33 (61%, in-sample). Overall 55/69 (79.7%). |

- The stable-regime band is almost one-sided (its upper edge is about the forecast itself) because ETS over-forecast in most backtest months.
- No single band suits both regimes. The stable band is too narrow after a break, and the regime-risk band is too wide in calm periods and still misses the worst months (for example May 2020).
- Quantiles from 36 errors are rough estimates.
- Monthly bands are not summed into a total interval, because monthly errors are correlated.

## 6. Final forecast: Feb to Jul 2021

Model: ETS refitted on all 61 months (damping phi = 0.995, no fit warnings, no fallback). Values in $M.

| Month | ETS forecast | Stable band | Regime-risk band | Ridge+break (sensitivity) |
|---|---|---|---|---|
| Feb 2021 | 0.61 | 0.48 to 0.62 | 0.32 to 0.72 | 0.97 |
| Mar 2021 | 0.23 | 0.18 to 0.23 | 0.12 to 0.26 | 0.46 |
| Apr 2021 | 0.05 | 0.04 to 0.05 | 0.03 to 0.06 | 0.11 |
| May 2021 | 0.41 | 0.32 to 0.42 | 0.21 to 0.48 | 0.83 |
| Jun 2021 | 0.38 | 0.30 to 0.38 | 0.20 to 0.44 | 0.76 |
| Jul 2021 | 0.32 | 0.26 to 0.33 | 0.17 to 0.38 | 0.66 |

Total ETS point forecast: about **$2.0M**. Saved to `reports/forecast_feb_jul_2021.csv`; chart at `reports/figures/final_forecast.png`.

**Sanity checks**

- Dec 2020 ($0.65M) and Jan 2021 ($0.51M) ran at roughly a quarter of the same months a year earlier. The forecast implies about the same ratio against the equivalent pre-break months.
- Shape is as expected: April is the trough (spring order gap), February is above March, and May to July rebound.
- Comparing with Feb to Jul 2020 is misleading for March onward, because those months were already post-break. The shrinking gap in May to July reflects a low base, not a recovery.

**The sensitivity line.** Ridge+break is about 1.6 to 2 times ETS and sits above even the regime-risk band. It assumes the pre-2020 growth rate (fitted 37.1% a year) resumes on top of the post-break level. The 2020 data does not show that, and the model lost to ETS at the break in the backtest. Treat it as an optimistic recovery scenario, not a competing forecast.

## 7. Limitations

1. **One structural break.** Everything about break behaviour rests on one event and about six informative origins.
2. **Only one post-break year of data.** Seasonal indices are learned mostly from 2016 to 2019, and we cannot know whether they still hold.
3. **We do not know whether the 2020 drop is permanent.** The forecast assumes the new level persists.
4. **April is the least reliable month.** $0.05M is lower than any April on record, and ETS under-forecast April 2020. The stable band understates the upside for that month.
5. **ETS carries its recent downward trend forward** (almost no damping), which produces the slow slide from May to July.
6. **Bands are empirical and small-sample,** and the in-sample coverage figures are optimistic.
7. **Choices made after seeing results:** the Ridge+break design, and the ETS+Ridge ensemble. Neither is used as the headline.
8. **Not tuned:** ridge alpha was fixed at 0.1; SARIMA was searched over only 12 combinations.
9. **Scope:** a single monthly total. No product, store or country forecasts, and no outside drivers such as promotions or the economy.
10. **The data is simulated.** Conclusions are about methodology.

## 8. Process notes (what went wrong and how it was caught)

- Both ridge models silently fell back to the naive forecast at all 23 origins because of a `NameError`, and the leakage check passed vacuously because the fallback forecast cannot leak. The giveaway was that the Ridge and Ridge+break forecasts were identical to naive. Fix: `src/forecasters.py` was rewritten with its constants at the top, every fit is logged, and the notebook asserts that no fit fell back. The same assertion guards the final forecast.
- **Lesson:** a passing check is only meaningful if the thing being checked actually ran. Log fallbacks and fail loudly.

## 9. Files

- `notebooks/02_forecasting.ipynb`: the full analysis.
- `src/series.py`, `src/backtest.py`, `src/forecasters.py`: reusable code.
- `reports/figures/`: `stl_decomposition`, `baseline_forecast`, `model_comparison`, `ridge_comparison`, `final_forecast`.
- `reports/forecast_feb_jul_2021.csv`: the forecast table.
