# Dashboard build guide - 4 report pages

Canvas: View -> Page view -> **Fit to page**; Format page -> Canvas settings: **16:9**. Apply theme: View -> Themes -> Browse for themes -> `theme.json`.
Add on **every page**: a title text box, and slicers on the left/top (Year, Quarter - from `dim_date`; Region - from `dim_state`).
Sync slicers across pages: View -> Sync slicers.

---
## Page 1 - Executive Overview
| Visual | Fields |
|---|---|
| 5 x **Card** (top row) | `Revenue`, `Orders`, `Average Order Value`, `Customers`, `Avg Review Score` |
| **KPI** / card w/ subtitle | `Revenue YoY %` (conditional font colour by rule: >=0 green, <0 red) |
| **Line + clustered column** | X: `dim_date[year_month]`; Column: `Revenue`; Line: `Revenue Rolling 3M` |
| **Area chart** | X: `dim_date[year_month]`; Y: `Revenue Running Total` |
| **Donut** | Legend: `fact_payments[payment_type]`; Values: `Payment Value` |
| **Filled map / Azure map** | Location: `dim_state[map_location]`; Size/colour: `Revenue` |
| **Bar chart** | Axis: `dim_state[region]`; Values: `Revenue` |
Tip: Format -> Cards -> turn on "Reference labels" to show `Revenue MoM %` under the Revenue card.

## Page 2 - Products & Sellers
| Visual | Fields |
|---|---|
| **Treemap** | Group: `dim_products[category]`; Values: `Revenue` |
| **Bar chart (Top 10)** | Axis: `dim_products[category]`; Values: `Revenue`; Filters pane -> Top N = 10 by `Revenue` |
| **Pareto** (Line + column) | X: category (sorted desc by Revenue); Column: `Revenue`; Line: `Cumulative Revenue Share %` |
| **Scatter** | Details: `dim_products[category]`; X: `Average Order Value`; Y: `Avg Review Score`; Size: `Revenue` |
| **Table** (Top sellers) | `dim_sellers[seller_id]`, `dim_sellers[state_code]`, `Revenue`, `Orders`, `Avg Review Score`, `Seller Revenue Rank` (Top N = 15) |
| **Column chart** | X: `fact_order_items[Price Band]`; Y: `Items Sold` |

## Page 3 - Logistics & Delivery
| Visual | Fields |
|---|---|
| Cards | `Avg Delivery Days`, `Avg Estimated Days`, `On-time Delivery %`, `Late Orders`, `Cancelled Orders %` |
| **Gauge** | Value: `On-time Delivery %`; Target 95%; Min 0; Max 100% |
| **Line chart** | X: `dim_date[year_month]`; Y: `Late Delivery %` |
| **Clustered column** | X: `fact_orders[Delivery Bucket]`; Y: `Delivered Orders` |
| **Bar chart** | Axis: `dim_state[state_name]`; Values: `Avg Delivery Days` (sort desc) |
| **Matrix (heat-map)** | Rows: `dim_state[region]`; Columns: `dim_date[year]`; Values: `Late Delivery %`; Conditional formatting -> background colour scale (green -> red) |

## Page 4 - Customer Satisfaction
| Visual | Fields |
|---|---|
| Cards | `Avg Review Score`, `Positive Reviews %`, `Negative Reviews %`, `Review Net Score` |
| **Column chart** | X: `fact_reviews[score]`; Y: `Reviews` |
| **Clustered column** | X: `dim_date[year_month]`; Y: `Avg Review Score (Late)` and `Avg Review Score (On time)` (shows delivery-delay impact on reviews) |
| **Bar chart** | Axis: `dim_products[category]`; Values: `Avg Review Score` (Filters: Reviews >= 50) |
| **Decomposition tree** | Analyze: `Negative Reviews %`; Explain by: category, state_name, payment_type, Delivery Bucket |
| **Key influencers** | Analyze: `fact_reviews[score]` (is 1-2) ; Explain by: `fact_orders[delivery_days]`, `is_late`, `freight_value` |

## Extras that make it look professional
* **Bookmarks + buttons** for a navigation bar (Insert -> Buttons -> Navigator -> Page navigator).
* **Drill-through**: create a hidden page "Category Detail" with drill-through field `dim_products[category]`.
* **Tooltip pages** for bar charts (Report page tooltip with a small line chart).
* Use dynamic card title: set title -> fx -> field `Title Revenue`.
* **Mobile layout**: View -> Mobile layout, drag the 5 main cards and 2 charts.

## Publish / share
File -> Save as `olist_dashboard.pbix`. Home -> Publish (needs a free work/school Power BI account; personal gmail accounts are not accepted by the Power BI service).
