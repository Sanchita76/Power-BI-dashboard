// ============================================================================
// POWER QUERY (M) CODE - one block per table. In Power BI Desktop:
//   Home -> Transform data -> New Source -> Blank Query -> Advanced Editor -> paste ONE block -> Done -> rename query
// STEP 0: create the parameter first:  Home -> Manage Parameters -> New Parameter
//         Name: DataFolder | Type: Text | Current Value: the full path ending with a backslash, e.g.
//         C:\Users\you\bi-projects\03-powerbi-olist-dashboard\data\processed\
// ============================================================================

// ---------------------------------------------------------------- dim_customers
let
    Source  = Csv.Document(File.Contents(DataFolder & "dim_customers.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"customer_id", type text}, {"customer_unique_id", type text}, {"zip_prefix", type text}, {"city", type text}, {"state_code", type text}}, "en-US")
in
    Typed

// ---------------------------------------------------------------- dim_date
let
    Source  = Csv.Document(File.Contents(DataFolder & "dim_date.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"date", type date}, {"year", Int64.Type}, {"quarter", type text}, {"month_num", Int64.Type}, {"month_name", type text}, {"year_month", type text}, {"week_of_year", Int64.Type}, {"weekday_num", Int64.Type}, {"weekday_name", type text}, {"is_weekend", Int64.Type}}, "en-US")
in
    Typed

// ---------------------------------------------------------------- dim_geo
let
    Source  = Csv.Document(File.Contents(DataFolder & "dim_geo.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"zip_prefix", type text}, {"latitude", type number}, {"longitude", type number}, {"city", type text}, {"state_code", type text}}, "en-US")
in
    Typed

// ---------------------------------------------------------------- dim_products
let
    Source  = Csv.Document(File.Contents(DataFolder & "dim_products.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"product_id", type text}, {"category", type text}, {"product_photos_qty", Int64.Type}, {"product_weight_g", Int64.Type}, {"volume_cm3", Int64.Type}}, "en-US")
in
    Typed

// ---------------------------------------------------------------- dim_sellers
let
    Source  = Csv.Document(File.Contents(DataFolder & "dim_sellers.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"seller_id", type text}, {"zip_prefix", type text}, {"city", type text}, {"state_code", type text}}, "en-US")
in
    Typed

// ---------------------------------------------------------------- dim_state
let
    Source  = Csv.Document(File.Contents(DataFolder & "dim_state.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"state_code", type text}, {"state_name", type text}, {"region", type text}, {"map_location", type text}}, "en-US")
in
    Typed

// ---------------------------------------------------------------- fact_order_items
let
    Source  = Csv.Document(File.Contents(DataFolder & "fact_order_items.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"order_id", type text}, {"order_item_id", type text}, {"product_id", type text}, {"seller_id", type text}, {"shipping_limit_date", type datetime}, {"price", type number}, {"freight_value", type number}, {"purchase_date", type date}, {"line_total", type number}}, "en-US")
in
    Typed

// ---------------------------------------------------------------- fact_orders
let
    Source  = Csv.Document(File.Contents(DataFolder & "fact_orders.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"order_id", type text}, {"customer_id", type text}, {"status", type text}, {"purchase_date", type date}, {"purchase_ts", type datetime}, {"approved_at", type datetime}, {"carrier_delivery_ts", type datetime}, {"customer_delivery_ts", type datetime}, {"estimated_delivery_ts", type datetime}, {"delivery_days", type number}, {"estimated_days", type number}, {"delay_days", type number}, {"is_delivered", Int64.Type}, {"is_late", Int64.Type}, {"items_count", Int64.Type}, {"items_value", type number}, {"freight_value", type number}, {"payment_value", type number}, {"max_installments", Int64.Type}, {"review_score", type number}}, "en-US")
in
    Typed

// ---------------------------------------------------------------- fact_payments
let
    Source  = Csv.Document(File.Contents(DataFolder & "fact_payments.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"order_id", type text}, {"payment_sequential", Int64.Type}, {"payment_type", type text}, {"installments", Int64.Type}, {"payment_value", type number}}, "en-US")
in
    Typed

// ---------------------------------------------------------------- fact_reviews
let
    Source  = Csv.Document(File.Contents(DataFolder & "fact_reviews.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"review_id", type text}, {"order_id", type text}, {"score", Int64.Type}, {"has_comment", Int64.Type}, {"creation_date", type date}, {"response_hours", type number}}, "en-US")
in
    Typed

