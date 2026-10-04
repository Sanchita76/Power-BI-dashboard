# Data model (Model view in Power BI)

After loading all 10 tables, open **Model view** and create these relationships
(drag the column on the "one" side onto the column on the "many" side). Power BI may auto-detect some - verify all.

| From (one side) | To (many side) | Cardinality | Filter direction |
|---|---|---|---|
| `dim_date[date]` | `fact_orders[purchase_date]` | 1 -> * | Single |
| `dim_customers[customer_id]` | `fact_orders[customer_id]` | 1 -> * | Single |
| `fact_orders[order_id]` | `fact_order_items[order_id]` | 1 -> * | Single |
| `fact_orders[order_id]` | `fact_payments[order_id]` | 1 -> * | Single |
| `fact_orders[order_id]` | `fact_reviews[order_id]` | 1 -> * | Single |
| `dim_products[product_id]` | `fact_order_items[product_id]` | 1 -> * | Single |
| `dim_sellers[seller_id]` | `fact_order_items[seller_id]` | 1 -> * | Single |
| `dim_state[state_code]` | `dim_customers[state_code]` | 1 -> * | Single |
| `dim_geo[zip_prefix]` | `dim_customers[zip_prefix]` | 1 -> * | Single |

**Do NOT** relate `dim_date` to `fact_order_items` / `fact_reviews` directly - date filters flow
`dim_date -> fact_orders -> items/payments/reviews`, which avoids ambiguous paths.
`dim_sellers[state_code]` is used only as a column (seller-state analysis), not as a relationship.

Then: select `dim_date` -> Table tools -> **Mark as date table** -> column `date`.
Hide the key columns (`*_id`, `zip_prefix`) from Report view (right-click -> Hide) for a cleaner field list.
Set data categories: `dim_geo[latitude]` = Latitude, `dim_geo[longitude]` = Longitude, `dim_state[map_location]` = State or Province.
Sort `dim_date[month_name]` by `month_num`, and `dim_date[weekday_name]` by `weekday_num`.
Set formats: Revenue/AOV = Currency (R$), percentages = Percentage (1 decimal).

```
                 dim_date
                    |
 dim_state -- dim_customers -- fact_orders -- fact_payments
 dim_geo ---/                     |  \------- fact_reviews
                            fact_order_items
                              /        \
                     dim_products   dim_sellers
```
