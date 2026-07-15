import pandas as pd
import numpy as np


orders = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_orders_dataset.csv")
sellers = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_sellers_dataset.csv")
order_items = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_items_dataset.csv")
reviews = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_reviews_dataset.csv")

print("Orders shape:", orders.shape)
print("Sellers shape:", sellers.shape)
print("Order items shape:", order_items.shape)
print("Reviews shape:", reviews.shape)

print("\nOrder date range:")
print(orders["order_purchase_timestamp"].min(), "to", orders["order_purchase_timestamp"].max())

print("\nOrders missing values:\n", orders.isna().sum())


print(orders["order_status"].value_counts())
print()
print(orders[orders["order_delivered_customer_date"].isna()]["order_status"].value_counts())


orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])

orders_sellers = order_items.merge(orders, on="order_id", how="left")

baseline_start = "2017-04-01"
baseline_end = "2018-01-01"

baseline = orders_sellers[
    (orders_sellers["order_purchase_timestamp"] >= baseline_start) &
    (orders_sellers["order_purchase_timestamp"] < baseline_end)
]

print("Baseline window rows:", baseline.shape[0])
print("Unique sellers in baseline:", baseline["seller_id"].nunique())
print(baseline.groupby("seller_id").size().describe())


seller_order_counts = baseline.groupby("seller_id").size()
eligible_sellers = seller_order_counts[seller_order_counts >= 5].index

print("Sellers eligible for scoring (>=5 baseline orders):", len(eligible_sellers))
print("% of baseline sellers retained:", round(100 * len(eligible_sellers) / len(seller_order_counts), 1))


# restrict baseline to eligible sellers only
baseline_eligible = baseline[baseline["seller_id"].isin(eligible_sellers)]

# --- Review score baseline ---
baseline_with_reviews = baseline_eligible.merge(
    reviews[["order_id", "review_score"]], on="order_id", how="left"
)
review_baseline = baseline_with_reviews.groupby("seller_id")["review_score"].mean()

print("Sellers with review data in baseline:", review_baseline.notna().sum())
print(review_baseline.describe())

# --- Delay baseline: seller's processing time (purchase -> handed to carrier) ---
baseline_eligible = baseline_eligible.copy()
baseline_eligible["order_delivered_carrier_date"] = pd.to_datetime(baseline_eligible["order_delivered_carrier_date"])
baseline_eligible["processing_days"] = (
    baseline_eligible["order_delivered_carrier_date"] - baseline_eligible["order_purchase_timestamp"]
).dt.total_seconds() / 86400

delay_baseline = baseline_eligible.groupby("seller_id")["processing_days"].median()

print("\nSellers with delay data in baseline:", delay_baseline.notna().sum())
print(delay_baseline.describe())


print("Baseline eligible rows:", baseline_eligible.shape[0])
print("Baseline with reviews rows:", baseline_with_reviews.shape[0])
print("Duplicate order_ids in reviews:", reviews["order_id"].duplicated().sum())

dupe_order_ids = reviews[reviews["order_id"].duplicated(keep=False)]["order_id"].unique()
sample_dupes = reviews[reviews["order_id"].isin(dupe_order_ids[:5])].sort_values("order_id")
print(sample_dupes[["order_id", "review_score", "review_creation_date", "review_answer_timestamp"]])


reviews_dedup = (
    reviews.sort_values("review_creation_date")
    .drop_duplicates(subset="order_id", keep="last")
)

print("Original review rows:", reviews.shape[0])
print("Deduplicated review rows:", reviews_dedup.shape[0])
print("Still duplicated after dedup:", reviews_dedup["order_id"].duplicated().sum())

baseline_with_reviews = baseline_eligible.merge(
    reviews_dedup[["order_id", "review_score"]], on="order_id", how="left"
)
print("Baseline eligible rows:", baseline_eligible.shape[0])
print("Baseline with reviews rows (after dedup):", baseline_with_reviews.shape[0])




recent_start = "2018-01-01"
recent_end = "2018-04-01"

recent = orders_sellers[
    (orders_sellers["order_purchase_timestamp"] >= recent_start) &
    (orders_sellers["order_purchase_timestamp"] < recent_end)
]

recent_eligible = recent[recent["seller_id"].isin(eligible_sellers)].copy()

# Volume
recent_volume = recent_eligible.groupby("seller_id").size()
print("Recent volume - sellers with any orders:", recent_volume.shape[0])
print(recent_volume.describe())

# Review (using deduped reviews)
recent_with_reviews = recent_eligible.merge(
    reviews_dedup[["order_id", "review_score"]], on="order_id", how="left"
)
recent_review = recent_with_reviews.groupby("seller_id")["review_score"].mean()
print("\nRecent review - sellers with data:", recent_review.notna().sum())
print(recent_review.describe())

# Delay
recent_eligible["order_delivered_carrier_date"] = pd.to_datetime(recent_eligible["order_delivered_carrier_date"])
recent_eligible["processing_days"] = (
    recent_eligible["order_delivered_carrier_date"] - recent_eligible["order_purchase_timestamp"]
).dt.total_seconds() / 86400
recent_delay = recent_eligible.groupby("seller_id")["processing_days"].median()
print("\nRecent delay - sellers with data:", recent_delay.notna().sum())
print(recent_delay.describe())



#Full SFI computation

import numpy as np

# Build a single sellers dataframe with baseline + recent for all 3 components
sfi_df = pd.DataFrame(index=list(eligible_sellers))
sfi_df["baseline_volume"] = seller_order_counts.reindex(sfi_df.index)
sfi_df["recent_volume"] = recent_volume.reindex(sfi_df.index).fillna(0)

sfi_df["baseline_review"] = review_baseline.reindex(sfi_df.index)
sfi_df["recent_review"] = recent_review.reindex(sfi_df.index)  # NaN if zero recent orders

sfi_df["baseline_delay"] = delay_baseline.reindex(sfi_df.index)
sfi_df["recent_delay"] = recent_delay.reindex(sfi_df.index)  # NaN if zero recent orders

# --- VolumeDecay ---
sfi_df["volume_decay"] = ((sfi_df["baseline_volume"] - sfi_df["recent_volume"]) / sfi_df["baseline_volume"]).clip(lower=0)

# --- ReviewDecay (0 if no recent data) ---
sfi_df["review_decay"] = ((sfi_df["baseline_review"] - sfi_df["recent_review"]) / sfi_df["baseline_review"]).clip(lower=0)
sfi_df["review_decay"] = sfi_df["review_decay"].fillna(0)

# --- DelaySurge: recent processing time vs baseline, as a ratio-based surge (0 if no recent data) ---
sfi_df["delay_surge"] = ((sfi_df["recent_delay"] - sfi_df["baseline_delay"]) / sfi_df["baseline_delay"]).clip(lower=0, upper=1)
sfi_df["delay_surge"] = sfi_df["delay_surge"].fillna(0)

# --- Composite SFI (weights from your framework: 0.3/0.3/0.4) ---
sfi_df["SFI"] = 0.3*sfi_df["volume_decay"] + 0.3*sfi_df["review_decay"] + 0.4*sfi_df["delay_surge"]

print(sfi_df[["volume_decay","review_decay","delay_surge","SFI"]].describe())
print("\nSellers with zero recent orders (max volume decay):", (sfi_df["recent_volume"]==0).sum())



baseline_months = 9
recent_months = 3

sfi_df["baseline_rate"] = sfi_df["baseline_volume"] / baseline_months
sfi_df["recent_rate"] = sfi_df["recent_volume"] / recent_months

sfi_df["volume_decay"] = (
    (sfi_df["baseline_rate"] - sfi_df["recent_rate"]) / sfi_df["baseline_rate"]
).clip(lower=0)

# Recompute SFI with corrected volume_decay
sfi_df["SFI"] = 0.3*sfi_df["volume_decay"] + 0.3*sfi_df["review_decay"] + 0.4*sfi_df["delay_surge"]

print(sfi_df[["volume_decay","review_decay","delay_surge","SFI"]].describe())


import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15,4))
sfi_df["volume_decay"].hist(bins=30, ax=axes[0])
axes[0].set_title("Volume Decay Distribution")
sfi_df["review_decay"].hist(bins=30, ax=axes[1])
axes[1].set_title("Review Decay Distribution")
sfi_df["delay_surge"].hist(bins=30, ax=axes[2])
axes[2].set_title("Delay Surge Distribution")
plt.tight_layout()
#plt.savefig("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/reporting/sfi_component_distributions.png")
#plt.show()

# check the sellers hitting the delay_surge ceiling
ceiling_sellers = sfi_df[(sfi_df["delay_surge"] >= 1.0) & (sfi_df["recent_volume"] > 0)]
print("Sellers at delay_surge ceiling:", len(ceiling_sellers))
print(ceiling_sellers[["baseline_delay", "recent_delay"]].describe())

ceiling_sellers = ceiling_sellers.copy()
ceiling_sellers["absolute_delay_increase"] = ceiling_sellers["recent_delay"] - ceiling_sellers["baseline_delay"]
print(ceiling_sellers["absolute_delay_increase"].describe())


