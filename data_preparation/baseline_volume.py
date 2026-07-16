"""
STEP 2: Baseline Volume & Eligible Seller Filter
==================================================
 
WHAT THIS STEP DOES
--------------------
1. Joins orders to order_items to attach a seller_id to every order (an order
   can contain items from multiple sellers, so this join happens at the
   order_item level, not the order level).
2. Filters to a "baseline" historical window: 2017-04-01 to 2018-01-01
   (9 months). This is meant to represent each seller's "normal" historical
   behavior, BEFORE we look at anything recent.
3. Counts how many orders each seller had in this baseline window.
4. Filters out sellers with too little baseline history to be scored
   reliably. We are considering a minimum of 5 baseline orders to be eligible for scoring.
 
METHODOLOGY REASONING
------------------------------------------------
The Seller Friction Index (SFI) we're building compares a seller's RECENT
behavior against their OWN BASELINE. That comparison is only meaningful if
the baseline itself is stable - a seller with only 1-2 baseline orders
doesn't have a reliable "normal" to compare against; any change looks like
either 0% or 100% decay, which is noise, not signal.
 
WHY 2017-04-01 to 2018-01-01 SPECIFICALLY:
The full dataset runs Sept 2016 - Oct 2018 (confirmed in Step 1). We need
room for FOUR separate windows without overlap:
  - Baseline  (seller's normal behavior)      -> 2017-04-01 to 2018-01-01
  - Recent    (feeds the SFI - current state) -> 2018-01-01 to 2018-04-01
  - Snapshot date (the "today" we pretend it is) -> 2018-04-01
  - Future/Label (did they actually go quiet?)   -> 2018-04-01 to 2018-10-17
This leaves the first ~7 months of the dataset unused (not enough runway
before the baseline start)
 
WHY MINIMUM 5 BASELINE ORDERS:
Looking at the distribution of orders-per-seller (median was only 6 orders,
heavily right-skewed - a handful of sellers dominate volume). A threshold
of 5 is a middle ground: strict enough to exclude sellers with too little
history to trust, loose enough to keep the median seller and above eligible.
"""
import pandas as pd
import numpy as np

#Loading the required data from the raw data folder and converting the timestamps to datetime objects
orders = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_orders_dataset.csv")
order_items = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_items_dataset.csv")

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    format="mixed",
    dayfirst=False,
    errors="coerce"
)

# 2. Join orders -> order_items to get seller_id per order
orders_sellers = order_items.merge(orders, on="order_id", how="left")

# 3. Filtering data to the baseline window
#As decided in the methodology reasoning, the baseline window is set to be from 2017-04-01 to 2018-01-01
BASELINE_START = "2017-04-01"
BASELINE_END = "2018-01-01"

#Baseline window orders are filtered from the orders_sellers dataframe based on the order_purchase_timestamp column
baseline = orders_sellers[
    (orders_sellers["order_purchase_timestamp"] >= BASELINE_START) &
    (orders_sellers["order_purchase_timestamp"] < BASELINE_END)
]

print("=" * 60)
print(f"BASELINE WINDOW: {BASELINE_START} to {BASELINE_END}")
print("=" * 60)
print(f"Baseline window rows (order-items): {baseline.shape[0]}")
print(f"Unique sellers in baseline window:  {baseline['seller_id'].nunique()}")


# 4. Orders-per-seller distribution
#this tells us how skewed seller activity is, and helps justify the minimum-order threshold below.

#Grouping the baseline dataframe by seller_id and counting the number of orders per seller
seller_order_counts = baseline.groupby("seller_id").size()
 
print("\n" + "=" * 60)
print("ORDERS-PER-SELLER DISTRIBUTION (baseline window)")
print("=" * 60)
print(seller_order_counts.describe())
'''order_items.merge(orders, on="order_id"). order_items has one row per line-item, not per order. 
If a customer buys 3 different products from the same seller in a single order, that's 3 rows in order_items for 1 actual order. 
When we then do baseline.groupby("seller_id").size(), we're counting line items sold, not orders fulfilled.
If we want to count actual orders per seller, we need to drop duplicates of order_id before grouping by seller_id.'''

# Deduplicate order-item rows to get unique order-seller pairs
orders_sellers_dedup = orders_sellers.drop_duplicates(subset=["order_id", "seller_id"])

print("Order-item rows (before dedup):", orders_sellers.shape[0])
print("Order-seller pairs (after dedup):", orders_sellers_dedup.shape[0])

# Recomputing baseline window and seller order counts after deduplication
baseline_dedup = orders_sellers_dedup[
    (orders_sellers_dedup["order_purchase_timestamp"] >= BASELINE_START) &
    (orders_sellers_dedup["order_purchase_timestamp"] < BASELINE_END)
]
seller_order_counts = baseline_dedup.groupby("seller_id").size()

print("\nUnique sellers in baseline:", baseline_dedup["seller_id"].nunique())
print(seller_order_counts.describe())


#Validating the discrepancy in the unique seller count through SQL an python
print(orders.shape[0])       # should be 99441
print(order_items.shape[0])  # should be 112650

print(orders["order_id"].duplicated().sum()) #Checking the duplicates in the orders dataset, should be 0


print(order_items["seller_id"].nunique())
print(order_items["seller_id"].str.strip().nunique())  # checking for whitespace issues

#Checking the number of orders in the baseline window using a direct filter on the orders dataframe, without joining to order_items
count = orders[
    (orders["order_purchase_timestamp"] >= "2017-04-01") &
    (orders["order_purchase_timestamp"] < "2018-01-01")
].shape[0]
print("Orders in baseline window (Python, no join):", count)


#Checking the data timestamps as the issue lies in the count of baeline order. 
#SQL says that there are 39839 order in that time period but python says that there are 37719 orders

print(orders["order_purchase_timestamp"].min(), orders["order_purchase_timestamp"].max())

#Changing the timestamp format to a more standard format to see if that resolves the discrepancy
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])

count = orders[
    (orders["order_purchase_timestamp"] >= "2017-04-01") &
    (orders["order_purchase_timestamp"] < "2018-01-01")
].shape[0]
print("Orders in baseline window (Python):", count)

