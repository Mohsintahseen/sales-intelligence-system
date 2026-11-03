# Phase 3 Findings: SQL Analysis

All data is **simulated** (Maven Analytics, Global Electronics Retailer). Revenue is quantity x list price;
the data has no discounts or price history. Findings describe this dataset only, not real businesses.

## Headline KPIs (Jan 2016 to 20 Feb 2021)
26,326 orders, 197,757 units, $55.76M revenue, $32.66M gross profit (58.6% margin), average order value $2,118.
11,887 of 15,266 customers (77.9%) have ordered; 3,379 never have.

## Growth and the 2020 break
| Year | Revenue | Change |
|---|---|---|
| 2016 | $6.95M | |
| 2017 | $7.42M | +6.8% |
| 2018 | $12.79M | +72.3% |
| 2019 | $18.26M | +42.8% |
| 2020 | $9.29M | -49.1% |
| 2021 (to Feb 20) | $1.04M | partial |

- Growth slowed from about +45% year-on-year (mid-2019) to about +6% (Jan to Feb 2020), then reversed from March 2020.
- Year-on-year declines deepened to about -84% to -85% by Oct to Nov 2020. Trailing-12-month revenue peaked at $18.52M (Feb 2020) and was $7.74M by Jan 2021 (-58%).
- Both channels fell by about the same amount (in-store -49.7%, online -47.0%), so the cause is business-wide.
- Customers placing a first order fell from 2,832 (2019) to 947 (2020), -67%.
- The data does not explain the cause. No causal claim is made.

## Products and categories
- Computers 34.6% of revenue, Home Appliances 19.4%, Cameras 11.7%, Cell phones 11.1%, TV and Video 10.6%, Audio 5.7%, Music/Movies 5.6%, Games and Toys 1.3%.
- Margins are nearly constant (56.6% to 61.0% by category, 58.4% to 59.1% by year), so profit adds little beyond revenue.
- Budget products (under $100) are 35.6% of units and 4.5% of revenue; Luxury ($1,500+) is 2.1% of units and 16.3% of revenue.
- Each product_key is a colour variant, so "top products" lists are dominated by a few models.

## Channels and stores
- In-store 79.6% of revenue, online 20.4% (to Jan 2021). Average order value $2,137 vs $2,045.
- Online (one channel) earned about 15 times the revenue of the average selling physical store.
- Revenue per store (all stores counted) is highest in the US ($979,580) and lowest in France ($173,053).
- 9 of 66 physical stores never made a sale.
- In-store purchases are always in the customer's own country.

## Customers
- 61.2% of ordering customers are repeat customers (average 2.21 orders over five years).
- Top 10% of buyers hold 36.0% of revenue, top 20% 55.3%, top 40% 79.2%. The 80/20 rule does not hold.
- Platinum and Gold are 21.1% of all customers and 65.5% of revenue; Bronze is 17.8% of customers and 2.2% of revenue.
- Loyal customers (4+ orders) average about $10.1K lifetime spend vs about $2.1K for one-time customers.
- **Tenure caveat (tested):** first-year spend is flat across the 2016 to 2019 cohorts (about $2,950 to $3,300) while
  lifetime spend differs almost 2-fold, so tiers largely reflect how long a customer has existed.
- Australia: 45.1% of customers never ordered, South Australia 88.7% (its only store never sold; its 19 buyers were online-only).
  Customers in states whose store never sold buy in-store less often (0% to 48% vs 67% to 77% elsewhere), but the
  data does not show why. Hypotheses tested and rejected or left open are in `sql/06_subqueries_ctes.sql`.

## Time patterns
- December is the peak (seasonal index 181, from 2016 to 2019), November 119, February 134.
- Saturday has 23.8% of orders, Sunday 1.7%.
- Every year 35 to 37 consecutive days (about 18 March to 24 April) have no orders. 237 of 1,878 days have none.
  March and April totals and seasonal indices are understated; per-active-day normalisation only partly fixes this.

## Implications for later phases
1. Forecasting (Phase 5) must handle the spring gap and the 2020 structural break; a model trained across both will mislead.
2. Complete months for forecasting: 2016-01 to 2021-01.
3. Compare customers within a cohort, not across acquisition years.
4. Group products at model level (strip colour) for best-seller analysis.
5. Discount and price-elasticity analysis are not possible with this data.