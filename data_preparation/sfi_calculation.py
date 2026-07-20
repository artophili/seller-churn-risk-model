"""
STEP 6: Seller Friction Index (SFI) Calculation
==================================================

WHAT THIS STEP DOES
--------------------
Combines the baseline (Steps 2-4) and recent (Step 5) components into the
three SFI sub-scores - VolumeDecay, ReviewDecay, DelaySurge - and the final
weighted composite Seller Friction Index for all 897 eligible sellers.

    SFI = 0.3 * VolumeDecay + 0.3 * ReviewDecay + 0.4 * DelaySurge

WHY THIS STEP MATTERS (METHODOLOGY REASONING)
------------------------------------------------
This is the core methodological contribution of the whole project - turning
three separate behavioral signals into one leading-indicator composite score
that (per the research hypotheses) should predict future seller inactivity
better than any single signal alone, and earlier than volume decline alone
would reveal it.

While doing the exploration of the data we found below bugs 
Bug #1: Comparing different time lengths unfairly
Our "baseline" period is 9 months long. Our "recent" period is only 3 months long — a third as long. If we just compare raw order counts between them (like "50 orders in baseline" vs "15 orders in recent"), 
a seller who is doing perfectly fine — same steady pace, nothing wrong — would still look like they lost two-thirds of their business, just because we're comparing a big bucket of time to a small bucket of time.
The fix: 
turn both numbers into "orders per month" first (divide by 9 for baseline, divide by 3 for recent), then compare those.

Bug #2: Punishing "gone" sellers three times instead of once
Some sellers had zero orders in the recent period — they've basically disappeared. Since they have no recent orders, 
they also have no recent review score and no recent delivery-speed number to calculate (there's nothing to measure).
If we're not careful, this shows up as "missing data" for two of our three signals — which could either accidentally 
let them off the hook, or accidentally penalize them extra hard in a confusing way.
The fix: 
for these "gone quiet" sellers, we just say their review-decline score and their delay score are both 0 (nothing extra to add) — 
and let the volume score alone (which will already be at its maximum, 1.0) tell the story that they're gone. This way, "they disappeared" only counts once, not three times.
"""

import pandas as pd
import numpy as np

# -----------------------------------------------------------------------
# 1. Rebuild everything needed (self-contained - see Steps 2-5 for the
#    detailed reasoning behind each of these blocks)
# -----------------------------------------------------------------------

orders = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_orders_dataset.csv")
sellers = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_sellers_dataset.csv")
order_items = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_items_dataset.csv")
reviews = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_reviews_dataset.csv")

orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
orders["order_delivered_carrier_date"] = pd.to_datetime(orders["order_delivered_carrier_date"])

orders_sellers = order_items.merge(orders, on="order_id", how="left")
orders_sellers_dedup = orders_sellers.drop_duplicates(subset=["order_id", "seller_id"])

reviews_dedup = (
    reviews.sort_values("review_creation_date")
    .drop_duplicates(subset="order_id", keep="last")
)

BASELINE_START, BASELINE_END = "2017-04-01", "2018-01-01"
RECENT_START, RECENT_END = "2018-01-01", "2018-04-01"
MIN_BASELINE_ORDERS = 5
BASELINE_MONTHS = 9
RECENT_MONTHS = 3

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

baseline_eligible = baseline[baseline["seller_id"].isin(FINAL_ELIGIBLE)]
baseline_with_reviews = baseline_eligible.merge(reviews_dedup[["order_id","review_score"]], on="order_id", how="left")
review_baseline = baseline_with_reviews.groupby("seller_id")["review_score"].mean()

recent = orders_sellers_dedup[
    (orders_sellers_dedup["order_purchase_timestamp"] >= RECENT_START) &
    (orders_sellers_dedup["order_purchase_timestamp"] < RECENT_END)
].copy()
recent_eligible = recent[recent["seller_id"].isin(FINAL_ELIGIBLE)].copy()
recent_eligible["processing_days"] = (
    recent_eligible["order_delivered_carrier_date"] - recent_eligible["order_purchase_timestamp"]
).dt.total_seconds() / 86400

recent_volume = recent_eligible.groupby("seller_id").size()
recent_with_reviews = recent_eligible.merge(reviews_dedup[["order_id","review_score"]], on="order_id", how="left")
recent_review = recent_with_reviews.groupby("seller_id")["review_score"].mean()
recent_delay = recent_eligible.groupby("seller_id")["processing_days"].median()

print(f"Final eligible seller population: {len(FINAL_ELIGIBLE)}")

# -----------------------------------------------------------------------
# 2. Assemble the SFI working table
# -----------------------------------------------------------------------
sfi_df = pd.DataFrame(index=list(FINAL_ELIGIBLE))

sfi_df["baseline_volume"] = seller_order_counts.reindex(sfi_df.index)
sfi_df["recent_volume"] = recent_volume.reindex(sfi_df.index).fillna(0)

sfi_df["baseline_review"] = review_baseline.reindex(sfi_df.index)
sfi_df["recent_review"] = recent_review.reindex(sfi_df.index)  # NaN if zero recent orders

sfi_df["baseline_delay"] = delay_baseline.reindex(sfi_df.index)
sfi_df["recent_delay"] = recent_delay.reindex(sfi_df.index)  # NaN if zero recent orders / no shipped orders

# -----------------------------------------------------------------------
# 3. VolumeDecay - BUG FIX 1 applied: normalize to monthly rate first
# -----------------------------------------------------------------------
sfi_df["baseline_rate"] = sfi_df["baseline_volume"] / BASELINE_MONTHS
sfi_df["recent_rate"] = sfi_df["recent_volume"] / RECENT_MONTHS

sfi_df["volume_decay"] = (
    (sfi_df["baseline_rate"] - sfi_df["recent_rate"]) / sfi_df["baseline_rate"]
).clip(lower=0)

# -----------------------------------------------------------------------
# 4. ReviewDecay - BUG FIX 2 applied: 0 (not NaN) for zero-recent-order sellers
# -----------------------------------------------------------------------
sfi_df["review_decay"] = (
    (sfi_df["baseline_review"] - sfi_df["recent_review"]) / sfi_df["baseline_review"]
).clip(lower=0)
sfi_df["review_decay"] = sfi_df["review_decay"].fillna(0)

# -----------------------------------------------------------------------
# 5. DelaySurge - relative ratio, capped at 1.0, validated against absolute
#    day differences (see docstring) - BUG FIX 2 applied here too
# -----------------------------------------------------------------------
sfi_df["delay_surge"] = (
    (sfi_df["recent_delay"] - sfi_df["baseline_delay"]) / sfi_df["baseline_delay"]
).clip(lower=0, upper=1)
sfi_df["delay_surge"] = sfi_df["delay_surge"].fillna(0)

# -----------------------------------------------------------------------
# 6. Composite SFI
# -----------------------------------------------------------------------
W_VOLUME, W_REVIEW, W_DELAY = 0.3, 0.3, 0.4
sfi_df["SFI"] = W_VOLUME*sfi_df["volume_decay"] + W_REVIEW*sfi_df["review_decay"] + W_DELAY*sfi_df["delay_surge"]

print("\n" + "=" * 60)
print("SFI COMPONENT DISTRIBUTIONS")
print("=" * 60)
print(sfi_df[["volume_decay","review_decay","delay_surge","SFI"]].describe())

print("\n" + "=" * 60)
print("ROUGH SFI RANGE BREAKDOWN")
print("=" * 60)
bins = [-0.01, 0.15, 0.35, 1.0]
labels = ["Low (0-0.15)", "Moderate (0.15-0.35)", "High (0.35-1.0)"]
sfi_range = pd.cut(sfi_df["SFI"], bins=bins, labels=labels)
print(sfi_range.value_counts())
print(sfi_range.value_counts(normalize=True).round(3) * 100)

# -----------------------------------------------------------------------
# 7. Saving the SFI table
# -----------------------------------------------------------------------
sfi_df.to_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/sfi_scores.csv", index_label="seller_id")
print("\nSaved: C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/sfi_scores.csv")