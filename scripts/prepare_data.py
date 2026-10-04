"""Turn the 9 raw Olist CSV files into a clean STAR SCHEMA (8 CSV tables) for Power BI.
Usage: python scripts/prepare_data.py          (reads data/raw, writes data/processed)
"""
import os, sys
import numpy as np, pandas as pd

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
RAW, OUT = os.path.join(BASE, "raw"), os.path.join(BASE, "processed")

REGIONS = {  # UF: (state name, region)
    "AC": ("Acre", "North"), "AL": ("Alagoas", "Northeast"), "AP": ("Amapá", "North"), "AM": ("Amazonas", "North"),
    "BA": ("Bahia", "Northeast"), "CE": ("Ceará", "Northeast"), "DF": ("Distrito Federal", "Central-West"),
    "ES": ("Espírito Santo", "Southeast"), "GO": ("Goiás", "Central-West"), "MA": ("Maranhão", "Northeast"),
    "MT": ("Mato Grosso", "Central-West"), "MS": ("Mato Grosso do Sul", "Central-West"),
    "MG": ("Minas Gerais", "Southeast"), "PA": ("Pará", "North"), "PB": ("Paraíba", "Northeast"),
    "PR": ("Paraná", "South"), "PE": ("Pernambuco", "Northeast"), "PI": ("Piauí", "Northeast"),
    "RJ": ("Rio de Janeiro", "Southeast"), "RN": ("Rio Grande do Norte", "Northeast"),
    "RS": ("Rio Grande do Sul", "South"), "RO": ("Rondônia", "North"), "RR": ("Roraima", "North"),
    "SC": ("Santa Catarina", "South"), "SP": ("São Paulo", "Southeast"), "SE": ("Sergipe", "Northeast"),
    "TO": ("Tocantins", "North"),
}


def rd(name, **kw):
    path = os.path.join(RAW, name)
    if not os.path.exists(path):
        sys.exit(f"Missing {path}\nRun scripts/download_data.py (Kaggle) or scripts/make_demo_data.py (fake data) first.")
    return pd.read_csv(path, **kw)


def save(df, name):
    df.to_csv(os.path.join(OUT, name), index=False, encoding="utf-8")
    print(f"  {name:<24} {len(df):>8,} rows  {len(df.columns)} cols")


def main():
    os.makedirs(OUT, exist_ok=True)
    print("Reading raw files...")
    orders = rd("olist_orders_dataset.csv", parse_dates=[
        "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date"])
    items = rd("olist_order_items_dataset.csv", parse_dates=["shipping_limit_date"])
    pays = rd("olist_order_payments_dataset.csv")
    revs = rd("olist_order_reviews_dataset.csv", parse_dates=["review_creation_date", "review_answer_timestamp"])
    cust = rd("olist_customers_dataset.csv")
    prod = rd("olist_products_dataset.csv")
    sell = rd("olist_sellers_dataset.csv")
    geo = rd("olist_geolocation_dataset.csv")
    trans = rd("product_category_name_translation.csv")

    print("Building tables...")
    # ---------- dim_state ----------
    dim_state = pd.DataFrame([(k, v[0], v[1], f"{v[0]}, Brazil") for k, v in REGIONS.items()],
                             columns=["state_code", "state_name", "region", "map_location"])
    # ---------- dim_geo (one row per zip prefix) ----------
    dim_geo = (geo.groupby("geolocation_zip_code_prefix")
               .agg(latitude=("geolocation_lat", "mean"), longitude=("geolocation_lng", "mean"),
                    city=("geolocation_city", "first"), state_code=("geolocation_state", "first")).reset_index()
               .rename(columns={"geolocation_zip_code_prefix": "zip_prefix"}))
    dim_geo["city"] = dim_geo["city"].str.title()
    dim_geo[["latitude", "longitude"]] = dim_geo[["latitude", "longitude"]].round(5)
    # ---------- dim_customers ----------
    dim_cust = cust.rename(columns={"customer_zip_code_prefix": "zip_prefix", "customer_city": "city",
                                    "customer_state": "state_code"})
    dim_cust["city"] = dim_cust["city"].str.title()
    # ---------- dim_sellers ----------
    dim_sell = sell.rename(columns={"seller_zip_code_prefix": "zip_prefix", "seller_city": "city",
                                    "seller_state": "state_code"})
    dim_sell["city"] = dim_sell["city"].str.title()
    # ---------- dim_products ----------
    p = prod.merge(trans, on="product_category_name", how="left")
    p["category"] = p["product_category_name_english"].fillna(p["product_category_name"]).fillna("unknown")
    p["category"] = p["category"].str.replace("_", " ").str.title()
    p["volume_cm3"] = p["product_length_cm"] * p["product_height_cm"] * p["product_width_cm"]
    dim_prod = p[["product_id", "category", "product_photos_qty", "product_weight_g", "volume_cm3"]].copy()
    # ---------- fact_order_items ----------
    f_items = items.merge(orders[["order_id", "order_purchase_timestamp"]], on="order_id", how="left")
    f_items["purchase_date"] = f_items["order_purchase_timestamp"].dt.date
    f_items["line_total"] = (f_items["price"] + f_items["freight_value"]).round(2)
    f_items = f_items.drop(columns=["order_purchase_timestamp"])
    # ---------- fact_payments ----------
    f_pay = pays.rename(columns={"payment_installments": "installments"})
    # ---------- fact_reviews ----------
    f_rev = revs.rename(columns={"review_score": "score"})
    f_rev["has_comment"] = f_rev["review_comment_message"].notna().astype(int)
    f_rev["creation_date"] = f_rev["review_creation_date"].dt.date
    f_rev["response_hours"] = ((f_rev["review_answer_timestamp"] - f_rev["review_creation_date"])
                               .dt.total_seconds() / 3600).round(1)
    f_rev = f_rev[["review_id", "order_id", "score", "has_comment", "creation_date", "response_hours"]]
    # ---------- fact_orders ----------
    o = orders.copy()
    o["purchase_date"] = o["order_purchase_timestamp"].dt.date
    o["delivery_days"] = ((o["order_delivered_customer_date"] - o["order_purchase_timestamp"]).dt.total_seconds() / 86400).round(2)
    o["estimated_days"] = ((o["order_estimated_delivery_date"] - o["order_purchase_timestamp"]).dt.total_seconds() / 86400).round(2)
    o["delay_days"] = ((o["order_delivered_customer_date"] - o["order_estimated_delivery_date"]).dt.total_seconds() / 86400).round(2)
    o["is_delivered"] = (o["order_status"] == "delivered").astype(int)
    o["is_late"] = ((o["order_delivered_customer_date"] > o["order_estimated_delivery_date"]) & (o["is_delivered"] == 1)).astype(int)
    agg_items = items.groupby("order_id").agg(items_count=("order_item_id", "count"), items_value=("price", "sum"),
                                              freight_value=("freight_value", "sum")).reset_index()
    agg_pay = pays.groupby("order_id").agg(payment_value=("payment_value", "sum"),
                                           max_installments=("payment_installments", "max")).reset_index()
    agg_rev = revs.groupby("order_id").agg(review_score=("review_score", "mean")).reset_index()
    o = o.merge(agg_items, on="order_id", how="left").merge(agg_pay, on="order_id", how="left") \
         .merge(agg_rev, on="order_id", how="left")
    for c in ["items_count", "items_value", "freight_value", "payment_value"]:
        o[c] = o[c].fillna(0)
    o["review_score"] = o["review_score"].round(2)
    f_orders = o.rename(columns={"order_status": "status", "order_purchase_timestamp": "purchase_ts",
                                 "order_approved_at": "approved_at",
                                 "order_delivered_carrier_date": "carrier_delivery_ts",
                                 "order_delivered_customer_date": "customer_delivery_ts",
                                 "order_estimated_delivery_date": "estimated_delivery_ts"})
    f_orders = f_orders[["order_id", "customer_id", "status", "purchase_date", "purchase_ts", "approved_at",
                         "carrier_delivery_ts", "customer_delivery_ts", "estimated_delivery_ts", "delivery_days",
                         "estimated_days", "delay_days", "is_delivered", "is_late", "items_count", "items_value",
                         "freight_value", "payment_value", "max_installments", "review_score"]]
    # ---------- dim_date ----------
    d0, d1 = pd.to_datetime(f_orders["purchase_date"]).min(), pd.to_datetime(f_orders["purchase_date"]).max()
    dates = pd.date_range(d0.replace(day=1), (d1 + pd.offsets.MonthEnd(0)))
    dim_date = pd.DataFrame({"date": dates})
    dim_date["year"] = dates.year; dim_date["quarter"] = "Q" + dates.quarter.astype(str)
    dim_date["month_num"] = dates.month; dim_date["month_name"] = dates.strftime("%b")
    dim_date["year_month"] = dates.strftime("%Y-%m"); dim_date["week_of_year"] = dates.isocalendar().week.values
    dim_date["weekday_num"] = dates.weekday + 1; dim_date["weekday_name"] = dates.strftime("%a")
    dim_date["is_weekend"] = (dates.weekday >= 5).astype(int)
    dim_date["date"] = dim_date["date"].dt.date

    print(f"Saving to {os.path.abspath(OUT)}")
    for df, n in [(f_orders, "fact_orders.csv"), (f_items, "fact_order_items.csv"), (f_pay, "fact_payments.csv"),
                  (f_rev, "fact_reviews.csv"), (dim_cust, "dim_customers.csv"), (dim_prod, "dim_products.csv"),
                  (dim_sell, "dim_sellers.csv"), (dim_date, "dim_date.csv"), (dim_state, "dim_state.csv"),
                  (dim_geo, "dim_geo.csv")]:
        save(df, n)
    print("\nDone. Next: load these CSVs in Power BI (see README).")


if __name__ == "__main__":
    main()
