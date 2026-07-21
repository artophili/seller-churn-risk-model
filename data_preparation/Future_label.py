"""
STEP 7: Future Label Construction (for testing H2)
=====================================================

WHAT THIS STEP DOES
--------------------
For each of our 897 SFI-eligible sellers, checks their order activity in a
FUTURE window - strictly AFTER the snapshot date (2018-04-01) - and builds
a binary label: did this seller effectively go inactive/dark after the
snapshot, or did they remain active?

This is THE critical step that makes H2 testable at all. Everything built
till now uses data up through the previous date only. If we want
to claim SFI is PREDICTIVE not just descriptive, we need a label that
comes from a time period the SFI calculation never trained on - otherwise we'd
just be measuring whether SFI can predict itself, which proves nothing

The full dataset ends 2018-10-17. This gives us a ~6.5 month future window
to observe whether a seller actually stayed inactive or came back - long enough
that a seller with a couple of slow months isn't mistakenly labeled "Inactive"
just from short-term noise.

HOW "INACTIVE" IS DEFINED:
A seller is labeled inactive (1) if they have ZERO orders in the ENTIRE
future window. This is a deliberately strict, simple definition - a seller
with even one order in 6.5 months is NOT labeled inactive. This is a
design choice, not the only valid one - a "mostly inactive" (e.g. <2
orders) definition would also be defensible, but we start with the
strictest, most unambiguous version first.
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

BASELINE_START, BASELINE_END = "2017-04-01", "2018-01-01"
MIN_BASELINE_ORDERS = 5

baseline = orders_sellers_dedup[
    (orders_sellers_dedup["order_purchase_timestamp"] >= BASELINE_START) &
    (orders_sellers_dedup["order_purchase_timestamp"] < BASELINE_END)
].copy()
baseline["processing_days"] = (
    baseline["order_delivered_carrier_date"] - baseline["order_purchase_timestamp"]
).dt.total_seconds() / 86400

seller_order_counts = baseline.groupby("seller_id").size()
eligible_v1 = seller_order_counts[seller_order_counts >= MIN_BASELINE_ORDERS].index
delay_baseline = baseline[baseline["seller_id"].isin(eligible_v1)].groupby("seller_id")["processing_days"].median()
FINAL_ELIGIBLE = delay_baseline.dropna().index  # 897 sellers

# -----------------------------------------------------------------------
# 2. Load the saved SFI scores from Step 6
#    WHY: we need to compare the future label against SFI (and against
#    volume_decay alone) - loading the saved file rather than
#    recalculating keeps this step focused only on the NEW piece (the
#    label), not re-deriving something already validated.
# -----------------------------------------------------------------------
sfi_df = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Processed/sfi_scores.csv", index_col="seller_id")
print(f"Loaded SFI scores for {sfi_df.shape[0]} sellers")

# -----------------------------------------------------------------------
# 3. Define the FUTURE window and build the label
#    CRITICAL: this window starts EXACTLY where the recent window
#    ended - 2018-04-01 - and never overlaps with any data used to build
#    the SFI features. This is the leakage-safe separation the whole
#    project's methodology depends on.
# -----------------------------------------------------------------------
FUTURE_START = "2018-04-01"
FUTURE_END = "2018-10-17"

future = orders_sellers_dedup[
    (orders_sellers_dedup["order_purchase_timestamp"] >= FUTURE_START) &
    (orders_sellers_dedup["order_purchase_timestamp"] <= FUTURE_END)
].copy()

future_eligible = future[future["seller_id"].isin(FINAL_ELIGIBLE)]
future_order_counts = future_eligible.groupby("seller_id").size()

sfi_df["future_orders"] = future_order_counts.reindex(sfi_df.index).fillna(0)
sfi_df["is_inactive"] = (sfi_df["future_orders"] == 0).astype(int)

print("\n" + "=" * 60)
print("FUTURE LABEL DISTRIBUTION")
print("=" * 60)
print(sfi_df["is_inactive"].value_counts())
print(f"% inactive: {round(100 * sfi_df['is_inactive'].mean(), 1)}%")

# -----------------------------------------------------------------------
# 4. Compare against the Step 5 "zero recent orders" group
#    WHY: this tells us whether the future label is mostly just re-stating
#    sellers who were ALREADY gone as of the snapshot (which would make
#    prediction trivial/meaningless), or whether it captures a genuinely
#    NEW group who looked fine at the snapshot but declined afterward
#    (which is what makes H2 a real, non-trivial prediction task).
# -----------------------------------------------------------------------
already_zero_recent = sfi_df["recent_volume"] == 0

print("\n" + "=" * 60)
print("OVERLAP CHECK: already-zero-recent-orders vs future inactive label")
print("=" * 60)
crosstab = pd.crosstab(already_zero_recent, sfi_df["is_inactive"],
                       rownames=["Zero recent orders (as of snapshot)"],
                       colnames=["Inactive (future)"])
print(crosstab)

newly_inactive = sfi_df[(~already_zero_recent) & (sfi_df["is_inactive"] == 1)]
print(f"\nSellers who were ACTIVE at snapshot but became inactive afterward: {len(newly_inactive)}")
print(f"This is the group that makes H2 a meaningful prediction task "
      f"({round(100*len(newly_inactive)/(~already_zero_recent).sum(),1)}% of previously-active sellers)")

# -----------------------------------------------------------------------
# 5. Save the labeled dataset
# -----------------------------------------------------------------------
sfi_df.to_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Processed/sfi_scores_with_label.csv", index_label="seller_id")
print("\nC:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Processed/sfi_scores_with_label.csv")