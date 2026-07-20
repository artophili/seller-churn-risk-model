"""
STEP 4: Baseline Delay (Seller Processing Time)
==================================================

WHAT THIS STEP DOES
--------------------
Computes each eligible seller's baseline "processing time" - the time
between a customer purchasing an order and the seller handing that order
off to the carrier (order_delivered_carrier_date - order_purchase_timestamp).
This is the third and final baseline component (alongside volume and review score) needed for the Seller Friction Index.

Processing time is the seller's own operational responsibility - unlike
total delivery time (which also depends on the carrier/logistics network,
outside the seller's control), the purchase-to-carrier-handoff time is a
much cleaner measure of SELLER fulfillment speed specifically. This is why
we use order_delivered_carrier_date, not order_delivered_customer_date, for
this component - we want to isolate what the SELLER controls, not the
carrier.

Processing time is highly right-skewed (a small number of very slow orders
can inflate a mean far more than they should). Median is more robust to
these outliers and better represents a seller's "typical" processing speed.

Orders that were canceled, marked unavailable, or never shipped will have
a missing order_delivered_carrier_date as this we have already confirmed in the previous steps. 
This means some eligible sellers may have NO baseline delay
value if literally all their baseline orders fall into one of these
non-shipped categories. This is expected, not a bug - but it does mean we
may lose a small number of sellers at this stage who passed the volume and
review checks but have no valid delay data.

"""

import pandas as pd

# -----------------------------------------------------------------------
# 1. Rebuild baseline + eligible sellers (self-contained, same as Step 3)
# -----------------------------------------------------------------------

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
]

seller_order_counts = baseline.groupby("seller_id").size()
eligible_sellers = seller_order_counts[seller_order_counts >= MIN_BASELINE_ORDERS].index
baseline_eligible = baseline[baseline["seller_id"].isin(eligible_sellers)].copy()

print("Eligible sellers:", len(eligible_sellers))

# -----------------------------------------------------------------------
# 2. Compute processing_days = carrier handoff date - purchase date
# -----------------------------------------------------------------------
baseline_eligible["processing_days"] = (
    baseline_eligible["order_delivered_carrier_date"] - baseline_eligible["order_purchase_timestamp"]
).dt.total_seconds() / 86400

n_missing = baseline_eligible["processing_days"].isna().sum()
print("\n" + "=" * 60)
print("MISSING PROCESSING TIME CHECK")
print("=" * 60)
print(f"Baseline order-seller rows missing processing_days: {n_missing} out of {baseline_eligible.shape[0]}")

# -----------------------------------------------------------------------
# 3. Aggregate to seller level using MEDIAN (robust to outliers)
# -----------------------------------------------------------------------
delay_baseline = baseline_eligible.groupby("seller_id")["processing_days"].median()

print("\n" + "=" * 60)
print("BASELINE PROCESSING TIME PER SELLER (median days)")
print("=" * 60)
print(f"Eligible sellers with valid delay data: {delay_baseline.notna().sum()} out of {len(eligible_sellers)}")
print(delay_baseline.describe())

# -----------------------------------------------------------------------
# 4. Identify and briefly inspect any sellers LOST at this stage
#    (had enough baseline orders, but ALL of them lack a carrier date)
# -----------------------------------------------------------------------
sellers_lost = set(eligible_sellers) - set(delay_baseline.dropna().index)

if sellers_lost:
    print("\n" + "=" * 60)
    print(f"SELLERS LOST AT THIS STEP: {len(sellers_lost)}")
    print("=" * 60)
    example_seller = list(sellers_lost)[0]
    print(f"Example seller ({example_seller}) order_status breakdown:")
    print(baseline_eligible[baseline_eligible["seller_id"] == example_seller]["order_status"].value_counts())
else:
    print("\nNo sellers lost at this step - all eligible sellers have valid delay data.")
