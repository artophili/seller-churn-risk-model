"""
STEP 3: Review Deduplication & Baseline Review Score
======================================================

WHAT THIS STEP DOES
--------------------
1. Loads the order_reviews table.
2. Checks for and removes duplicate reviews per order_id (some orders have
   more than one review row - a customer resubmitting/updating their review).
3. Merges the deduplicated reviews onto the baseline order-seller table
   (from Step 2) and computes each eligible seller's average review score
   over the baseline window.

WHY THIS STEP MATTERS (METHODOLOGY REASONING)
------------------------------------------------
We found earlier that 551 order_ids in the reviews table have MORE THAN ONE
review row. If we merge without deduplicating first, those orders get
double (or more) counted in a seller's average review score - silently
biasing the "baseline satisfaction" number we'll later compare against the
"recent satisfaction" number to compute Review Decay (part of the SFI).

WHY WE KEEP THE MOST RECENT REVIEW (not the first, not an average):
We inspected sample duplicate pairs directly and found a MIXED pattern - some are simple resubmissions with the same score, but at
least one case showed a genuinely different score between submissions. "Most recent" is a defensible, simple rule
that approximates "the customer's settled opinion" in most cases, but it is
NOT perfect (one sample case showed the earlier submission had a LOWER
score than a later one, which complicates "most recent = most negative"
assumptions). This ambiguity should be stated as a known limitation in the
final report, not hidden.
"""

import pandas as pd

# -----------------------------------------------------------------------
# 1. Rebuild the Step 2 baseline + eligible sellers
#    WHY: each step script is self-contained and re-derives what it needs
#    from raw data, rather than depending on variables surviving in memory
#    from a previous script - this avoids the exact kind of stale-state
#    confusion.
# -----------------------------------------------------------------------
orders = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_orders_dataset.csv")
sellers = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_sellers_dataset.csv")
order_items = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_items_dataset.csv")
reviews = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_reviews_dataset.csv")

orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])

orders_sellers = order_items.merge(orders, on="order_id", how="left")
orders_sellers_dedup = orders_sellers.drop_duplicates(subset=["order_id", "seller_id"])

BASELINE_START = "2017-04-01"
BASELINE_END = "2018-01-01"
MIN_BASELINE_ORDERS = 5

baseline = orders_sellers_dedup[
    (orders_sellers_dedup["order_purchase_timestamp"] >= BASELINE_START) &
    (orders_sellers_dedup["order_purchase_timestamp"] < BASELINE_END)
]

seller_order_counts = baseline.groupby("seller_id").size()
eligible_sellers = seller_order_counts[seller_order_counts >= MIN_BASELINE_ORDERS].index
baseline_eligible = baseline[baseline["seller_id"].isin(eligible_sellers)].copy()

print("Eligible sellers:", len(eligible_sellers))

# -----------------------------------------------------------------------
# 2. Checking for and removing duplicate reviews
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print("REVIEW DUPLICATE CHECK")
print("=" * 60)
n_dupe_order_ids = reviews["order_id"].duplicated().sum()
print(f"Duplicate order_ids in reviews table: {n_dupe_order_ids}")

reviews_dedup = (
    reviews.sort_values("review_creation_date")
    .drop_duplicates(subset="order_id", keep="last")
)

print(f"Review rows before dedup: {reviews.shape[0]}")
print(f"Review rows after dedup:  {reviews_dedup.shape[0]}")
print(f"Still duplicated after dedup: {reviews_dedup['order_id'].duplicated().sum()}")

# -----------------------------------------------------------------------
# 3. Merge deduplicated reviews onto baseline, compute per-seller average
# -----------------------------------------------------------------------
baseline_with_reviews = baseline_eligible.merge(
    reviews_dedup[["order_id", "review_score"]], on="order_id", how="left"
)

print("\n" + "=" * 60)
print("MERGE INTEGRITY CHECK")
print("=" * 60)
print(f"Baseline eligible rows: {baseline_eligible.shape[0]}")
print(f"Baseline with reviews rows (after dedup): {baseline_with_reviews.shape[0]}")

review_baseline = baseline_with_reviews.groupby("seller_id")["review_score"].mean()

print("\n" + "=" * 60)
print("BASELINE REVIEW SCORE PER SELLER")
print("=" * 60)
print(f"Sellers with review data: {review_baseline.notna().sum()} out of {len(eligible_sellers)} eligible")
print(review_baseline.describe())