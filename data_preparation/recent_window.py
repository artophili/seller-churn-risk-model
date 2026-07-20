"""
STEP 5: Recent Window (Volume, Review, Delay)
================================================

WHAT THIS STEP DOES
--------------------
Mirrors the Baseline Volume,Review Dedup + Baseline Review Score and Baseline Delay, 
but for the RECENT window (2018-01-01 to 2018-04-01) instead of the baseline window. 
Computes the same three components -
order volume, average review score, and median processing delay - for
each of our 897 SFI-eligible sellers (the 898 sellers, minus the 1
seller excluded for having no valid delay data at all).

The whole point of the Seller Friction Index is comparing a seller's
RECENT behavior against their own BASELINE. We've now built the baseline
side - this step builds the recent side using the exact same
logic, so the two are genuinely comparable (same dedup rules, same
aggregation methods - median for delay, mean for review, count for volume).

IMPORTANT: NOT EVERY ELIGIBLE SELLER WILL HAVE RECENT ORDERS
Some sellers who were active in the 9-month baseline window may have ZERO
orders in the 3-month recent window - this is not missing data, it's a
real and important signal: a seller going from "active" to "zero recent
orders" is exactly the kind of disengagement this project is trying to
detect.

"""
import pandas as pd
orders = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_orders_dataset.csv")
sellers = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_sellers_dataset.csv")
order_items = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_items_dataset.csv")
reviews = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_reviews_dataset.csv")

orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
orders["order_delivered_carrier_date"] = pd.to_datetime(orders["order_delivered_carrier_date"])

orders_sellers = order_items.merge(orders, on="order_id", how="left")
orders_sellers_dedup = orders_sellers.drop_duplicates(subset=["order_id", "seller_id"])

BASELINE_START = "2017-04-01"
BASELINE_END = "2018-01-01"
MIN_BASELINE_ORDERS = 5

baseline = orders_sellers_dedup[
    (orders_sellers_dedup["order_purchase_timestamp"] >= BASELINE_START) &
    (orders_sellers_dedup["order_purchase_timestamp"] < BASELINE_END)
].copy()

seller_order_counts = baseline.groupby("seller_id").size()
eligible_sellers_v1 = seller_order_counts[seller_order_counts >= MIN_BASELINE_ORDERS].index

# Recompute Step 4's delay exclusion
baseline["processing_days"] = (
    baseline["order_delivered_carrier_date"] - baseline["order_purchase_timestamp"]
).dt.total_seconds() / 86400
delay_baseline = baseline[baseline["seller_id"].isin(eligible_sellers_v1)].groupby("seller_id")["processing_days"].median()

FINAL_ELIGIBLE_SELLERS = delay_baseline.dropna().index  # 897 sellers

print(f"Final eligible seller population (carried into recent window): {len(FINAL_ELIGIBLE_SELLERS)}")

# -----------------------------------------------------------------------
# 2. Deduplicate reviews (same rule as Step 3)
# -----------------------------------------------------------------------
reviews_dedup = (
    reviews.sort_values("review_creation_date")
    .drop_duplicates(subset="order_id", keep="last")
)

# -----------------------------------------------------------------------
# 3. Filter to the RECENT window
# -----------------------------------------------------------------------
RECENT_START = "2018-01-01"
RECENT_END = "2018-04-01"

recent = orders_sellers_dedup[
    (orders_sellers_dedup["order_purchase_timestamp"] >= RECENT_START) &
    (orders_sellers_dedup["order_purchase_timestamp"] < RECENT_END)
].copy()

recent_eligible = recent[recent["seller_id"].isin(FINAL_ELIGIBLE_SELLERS)].copy()

# -----------------------------------------------------------------------
# 4. Recent volume
# -----------------------------------------------------------------------
recent_volume = recent_eligible.groupby("seller_id").size()

sellers_with_zero_recent = set(FINAL_ELIGIBLE_SELLERS) - set(recent_volume.index)

print("\n" + "=" * 60)
print("RECENT VOLUME")
print("=" * 60)
print(f"Eligible sellers with ANY recent orders: {recent_volume.shape[0]} out of {len(FINAL_ELIGIBLE_SELLERS)}")
print(f"Eligible sellers with ZERO recent orders (gone quiet): {len(sellers_with_zero_recent)} "
      f"({round(100*len(sellers_with_zero_recent)/len(FINAL_ELIGIBLE_SELLERS),1)}%)")
print(recent_volume.describe())

# -----------------------------------------------------------------------
# 5. Recent review score
# -----------------------------------------------------------------------
recent_with_reviews = recent_eligible.merge(
    reviews_dedup[["order_id", "review_score"]], on="order_id", how="left"
)
recent_review = recent_with_reviews.groupby("seller_id")["review_score"].mean()

print("\n" + "=" * 60)
print("RECENT REVIEW SCORE")
print("=" * 60)
print(f"Sellers with recent review data: {recent_review.notna().sum()}")
print(recent_review.describe())

# -----------------------------------------------------------------------
# 6. Recent delay
# -----------------------------------------------------------------------
recent_eligible["processing_days"] = (
    recent_eligible["order_delivered_carrier_date"] - recent_eligible["order_purchase_timestamp"]
).dt.total_seconds() / 86400
recent_delay = recent_eligible.groupby("seller_id")["processing_days"].median()

print("\n" + "=" * 60)
print("RECENT PROCESSING DELAY")
print("=" * 60)
print(f"Sellers with recent delay data: {recent_delay.notna().sum()}")
print(recent_delay.describe())