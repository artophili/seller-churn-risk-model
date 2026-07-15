import pandas as pd
import numpy as np

#Loading the required data from the raw data folder and checking the shape of the dataframes
orders = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_orders_dataset.csv")
sellers = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_sellers_dataset.csv")
order_items = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_items_dataset.csv")
reviews = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_reviews_dataset.csv")

print("Orders shape:", orders.shape)
print("Sellers shape:", sellers.shape)
print("Order items shape:", order_items.shape)
print("Reviews shape:", reviews.shape)

# -----------------------------------------------------------------------
# 2. Date range of the orders table
#    this tells us how much history we have to work with, and lets us
#    plan baseline / recent / future windows later.
# -----------------------------------------------------------------------
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
 
print("\n" + "=" * 60)
print("DATE RANGE")
print("=" * 60)
print(f"Earliest order: {orders['order_purchase_timestamp'].min()}")
print(f"Latest order:   {orders['order_purchase_timestamp'].max()}")

# 3. Missing values in orders
#    some missing delivery dates are EXPECTED (a canceled order never
#    gets delivered) - we need to confirm this before assuming it's a
#    data-quality problem that needs fixing.
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print("MISSING VALUES IN ORDERS TABLE")
print("=" * 60)
print(orders.isna().sum())

#-----------------------------------------------------------------------
# 4. Order status breakdown
#    cross-checking missing delivery dates against order_status tells
#    us whether missingness is explained by business logic (canceled /
#    unavailable / still-processing orders) or is a genuine anomaly.
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print("ORDER STATUS BREAKDOWN (all orders)")
print("=" * 60)
print(orders["order_status"].value_counts())
 
print("\n" + "=" * 60)
print("ORDER STATUS BREAKDOWN (only orders MISSING a delivery date)")
print("=" * 60)
print(orders[orders["order_delivered_customer_date"].isna()]["order_status"].value_counts())

# -----------------------------------------------------------------------
# 5. Sanity check: canceled orders that DO have a delivery date
#    earlier in this project we found 6 such orders - a real, small
#    edge case (order canceled AFTER delivery, e.g. a post-delivery refund).
#    Not a bug, just something to be aware of.
# -----------------------------------------------------------------------
canceled = orders[orders["order_status"] == "canceled"]
canceled_with_delivery = canceled[canceled["order_delivered_customer_date"].notna()]
 
print("\n" + "=" * 60)
print("EDGE CASE CHECK: canceled orders that still have a delivery date")
print("=" * 60)
print(f"Total canceled orders: {canceled.shape[0]}")
print(f"Canceled orders WITH a delivery date recorded: {canceled_with_delivery.shape[0]}")
print("(Expected: a small number - likely post-delivery cancellations/refunds, not a data error)")