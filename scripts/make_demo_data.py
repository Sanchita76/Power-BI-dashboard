"""Creates SMALL FAKE data in exactly the Olist file format, so you can test everything without Kaggle.
Usage: python scripts/make_demo_data.py [--orders 5000]
"""
import argparse, os
import numpy as np, pandas as pd

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")
STATES = {"SP": (-23.55, -46.63), "RJ": (-22.9, -43.2), "MG": (-19.9, -43.9), "RS": (-30.0, -51.2),
          "PR": (-25.4, -49.3), "BA": (-12.97, -38.5), "SC": (-27.6, -48.5), "DF": (-15.8, -47.9),
          "GO": (-16.7, -49.3), "PE": (-8.05, -34.9)}
CATS = ["beleza_saude", "informatica_acessorios", "cama_mesa_banho", "esporte_lazer", "moveis_decoracao",
        "relogios_presentes", "brinquedos", "telefonia", "automotivo", "ferramentas_jardim"]
EN = ["health_beauty", "computers_accessories", "bed_bath_table", "sports_leisure", "furniture_decor",
      "watches_gifts", "toys", "telephony", "auto", "garden_tools"]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--orders", type=int, default=5000); a = ap.parse_args()
    rng = np.random.default_rng(1); os.makedirs(RAW, exist_ok=True)
    ids = lambda p, n: [f"{p}{i:06d}" for i in range(n)]
    nc, npd, ns = max(a.orders // 1.3, 100), 300, 40
    nc = int(nc)
    st = list(STATES)
    # geolocation
    geo = []
    for z in range(1000, 1600):
        s = st[z % len(st)]; la, lo = STATES[s]
        geo.append((z, la + rng.normal(0, .3), lo + rng.normal(0, .3), f"city {z % 25}", s))
    pd.DataFrame(geo, columns=["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng",
                               "geolocation_city", "geolocation_state"]).to_csv(f"{RAW}/olist_geolocation_dataset.csv", index=False)
    zips = rng.integers(1000, 1600, nc)
    cust = pd.DataFrame({"customer_id": ids("c", nc), "customer_unique_id": ids("u", nc),
                         "customer_zip_code_prefix": zips, "customer_city": [f"city {z % 25}" for z in zips],
                         "customer_state": [st[z % len(st)] for z in zips]})
    cust.to_csv(f"{RAW}/olist_customers_dataset.csv", index=False)
    pd.DataFrame({"product_category_name": CATS, "product_category_name_english": EN}).to_csv(
        f"{RAW}/product_category_name_translation.csv", index=False)
    prod = pd.DataFrame({"product_id": ids("p", npd), "product_category_name": rng.choice(CATS, npd),
                         "product_name_lenght": rng.integers(20, 60, npd), "product_description_lenght": rng.integers(100, 1500, npd),
                         "product_photos_qty": rng.integers(1, 8, npd), "product_weight_g": rng.integers(100, 8000, npd),
                         "product_length_cm": rng.integers(10, 60, npd), "product_height_cm": rng.integers(5, 40, npd),
                         "product_width_cm": rng.integers(8, 50, npd)})
    prod.to_csv(f"{RAW}/olist_products_dataset.csv", index=False)
    sz = rng.integers(1000, 1600, ns)
    pd.DataFrame({"seller_id": ids("s", ns), "seller_zip_code_prefix": sz, "seller_city": [f"city {z % 25}" for z in sz],
                  "seller_state": [st[z % len(st)] for z in sz]}).to_csv(f"{RAW}/olist_sellers_dataset.csv", index=False)
    n = a.orders
    days = rng.integers(0, 700, n)
    purchase = pd.Timestamp("2017-01-01") + pd.to_timedelta(days, "D") + pd.to_timedelta(rng.integers(0, 86400, n), "s")
    est = purchase + pd.to_timedelta(rng.integers(10, 30, n), "D")
    deliv = purchase + pd.to_timedelta(rng.gamma(4, 3.2, n) * 86400, "s")
    status = rng.choice(["delivered", "shipped", "canceled", "invoiced", "processing"], n, p=[.93, .02, .02, .015, .015])
    fmt = lambda s: s.dt.strftime("%Y-%m-%d %H:%M:%S")
    orders = pd.DataFrame({"order_id": ids("o", n), "customer_id": rng.choice(cust.customer_id, n), "order_status": status,
                           "order_purchase_timestamp": fmt(pd.Series(purchase)),
                           "order_approved_at": fmt(pd.Series(purchase + pd.Timedelta(hours=2))),
                           "order_delivered_carrier_date": fmt(pd.Series(purchase + pd.Timedelta(days=2))),
                           "order_delivered_customer_date": fmt(pd.Series(deliv)),
                           "order_estimated_delivery_date": fmt(pd.Series(est))})
    orders.loc[orders.order_status != "delivered", "order_delivered_customer_date"] = np.nan
    orders.to_csv(f"{RAW}/olist_orders_dataset.csv", index=False)
    rows, pays, revs = [], [], []
    for i, oid in enumerate(orders.order_id):
        k = rng.choice([1, 1, 1, 2, 3]); tot = 0
        for j in range(1, k + 1):
            price = round(float(rng.lognormal(4.3, .8)), 2); fr = round(float(rng.uniform(5, 40)), 2); tot += price + fr
            rows.append((oid, j, prod.product_id[rng.integers(npd)], f"s{rng.integers(ns):06d}",
                         (purchase[i] + pd.Timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"), price, fr))
        pays.append((oid, 1, rng.choice(["credit_card", "boleto", "voucher", "debit_card"], p=[.74, .19, .05, .02]),
                     int(rng.choice([1, 1, 2, 3, 6, 10])), round(tot, 2)))
        late = deliv[i] > est[i]
        sc = int(rng.choice([1, 2, 3], p=[.6, .25, .15]) if late else rng.choice([3, 4, 5], p=[.1, .25, .65]))
        revs.append((f"r{i:06d}", oid, sc, "", "Produto ok" if rng.random() < .3 else "",
                     purchase[i].strftime("%Y-%m-%d 00:00:00"), (purchase[i] + pd.Timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S")))
    pd.DataFrame(rows, columns=["order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price",
                                "freight_value"]).to_csv(f"{RAW}/olist_order_items_dataset.csv", index=False)
    pd.DataFrame(pays, columns=["order_id", "payment_sequential", "payment_type", "payment_installments",
                                "payment_value"]).to_csv(f"{RAW}/olist_order_payments_dataset.csv", index=False)
    pd.DataFrame(revs, columns=["review_id", "order_id", "review_score", "review_comment_title", "review_comment_message",
                                "review_creation_date", "review_answer_timestamp"]).to_csv(
        f"{RAW}/olist_order_reviews_dataset.csv", index=False)
    print("Demo raw files written to", os.path.abspath(RAW))


if __name__ == "__main__":
    main()
