# Phase 4 Findings: Exploratory Data Analysis

All data is **simulated** (Maven Analytics, Global Electronics Retailer). Revenue is quantity x list price;
there are no discounts or price history. Findings describe this dataset only. Notebook:
`notebooks/01_eda_overview.ipynb`; charts: `reports/figures/`.

## Trend
- Yearly revenue: 2016 $6.95M, 2017 $7.42M, 2018 $12.79M, 2019 $18.26M, 2020 $9.29M (-49.1%).
- Profit is about 58% of revenue in every year, so profit adds almost no information beyond revenue here.
- The 12-month average of monthly revenue rose from about $0.57M (2017) to a peak near $1.54M (early 2020),
  then fell to about $0.65M by January 2021.

## Products
- 2,517 products collapse to **885 models** (each product_key is a colour variant; 121 products carry no colour in their name).
- The top 3 models hold 8.9% of revenue; no model exceeds 3.3%.
- 14 models produce 25% of revenue, 64 produce 50%, 231 (26.1%) produce 80%.
- 12 of the top 15 models never appeared in a colour-level top-10, because their revenue is split across 4 to 7 colours.

## Customers and the 2020 decline
- Revenue loss 2019 to 2020 was $8.97M: **60.6% from new customers** ($5.43M) and **39.4% from returning** ($3.54M).
- Active new customers fell 66.6% (2,832 to 947); active returning customers fell 20.3% (3,665 to 2,921).
- Revenue per active customer fell about 16% in both groups.
- One-year retention rose 20.7% (2017), 35.3%, 46.6% (2019), then fell to **28.5%** (2020).
- 1,068 of 2020's 2,921 returning customers had skipped 2019.
- The data does not explain the decline; no causal claim is made.

## Stores, channels and regions
- Store revenue is clustered within countries, so means and medians rank countries differently (for example Canada: mean $716K, median $1.04M, because 2 of 5 stores never sold).
- Store size correlates with revenue (Spearman 0.54), but this is inflated by France (the only country with small stores, 245 to 400 sqm). Within countries the effect is inconsistent (0.78 Australia, 0.78 Germany, 0.43 US, 0.30 France, -0.34 UK; 5 to 20 stores each, none clearly significant).
- Revenue per store tracks customers per store across countries (Spearman 0.86, 8 countries), but this is partly arithmetic: in-store purchases are always domestic.
- Store opening year cannot be tested (62 of 66 stores opened before 2016).
- Online share of revenue rose every year: 16.8%, 18.7%, 20.2%, 21.4%, 22.3%, but gains are shrinking.
- In 2020 seven of eight countries fell 46% to 57%; **France fell only 31.5%** (unexplained). The US contributed 54.2% of the loss against a 55.5% revenue share.

## Daily patterns
- The spring gap is a **cliff**: 35 to 37 consecutive days with zero orders (about 18 March to 24 April, 2016 to 2020).
- The last week before and the first week after the gap trade at about 0.3 to 0.6 of normal; recovery is complete by week 2 (2016 to 2019). In 2020 post-gap weeks stayed near 0.46 of the pre-gap level.
- All 57 other missing days are Sundays. Saturday carries 23% to 25% of orders in every year; Sunday 1.0% to 2.1%.
- December is the seasonal peak; the highest daily revenue is $201.6K (21 Dec 2019).

## Outliers
- No data errors found in orders, customers, days or delivery times.
- The largest order is $43,279 (0.08% of revenue; 2.1% of its month). The largest customer spent $61,872 (0.11% of revenue).
- A raw IQR rule flags 7.4% of orders; a log-scale rule flags none at the top. The two disagree because order values are skewed, so flags were checked against records, not trusted mechanically.
- Day-level anomaly rules are unreliable on low-volume days (Sundays with 1 to 4 orders); a minimum order count is needed.
- Delivery takes 1 to 17 days (median 4); all online lines have a delivery date.

## Implications for Phase 5 (forecasting)
1. Forecast **monthly** revenue using complete months 2016-01 to 2021-01 (61 months).
2. The spring window (about 50 days a year including thin edge weeks) must be handled explicitly, or models will learn a false March/April crash.
3. The 2020 structural break means a model trained across it will mislead; evaluate on a window that respects it.
4. The December peak and Saturday-heavy weekly pattern are real seasonality to model.
5. No price or discount drivers exist; only demand and calendar effects can be modelled.