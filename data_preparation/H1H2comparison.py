"""
STEP 8: Direct H1/H2 Comparison Test
=======================================
Restricts to the 707 sellers who were ACTIVE as of the snapshot date
(2018-04-01) - i.e. excludes the 190 who were already at zero recent
orders, since for them "inactive" was already visible from raw volume
alone and proves nothing new.

Within this "looked fine at the time" group of 707, splits into:
  - 92 sellers who became INACTIVE in the future window
  - 615 sellers who STAYED ACTIVE

Then compares SFI and its three components between these two groups.

This is the cleanest, most interpretable test of H1 and H2 BEFORE building
any formal ML model:

  - H1 predicts that operational friction (review decay, delay surge)
    should ALREADY be elevated in the 92 "became inactive" sellers, even
    though their ORDER VOLUME looked completely normal at the snapshot
    (that's the whole point - volume alone wouldn't have caught them).

  - H2 predicts that the COMPOSITE SFI score should be meaningfully higher
    for the 92 than the 615, because it's designed to catch exactly this
    kind of seller - someone whose volume hasn't dropped yet, but whose
    review/delay signals already show trouble.

If the 92 group does NOT show elevated SFI/component scores compared to
the 615, that would be evidence AGAINST H1/H2, not for it - this test is
a genuine, falsifiable check, not a foregone conclusion.

STATISTICAL TEST CHOICE:
We use the Mann-Whitney U test (not a t-test) because the SFI components
are bounded, right-skewed distributions, not normally distributed - 
Mann-Whitney doesn't assume normality and compares distributions more robustly for this kind of skewed data.

"""

import pandas as pd
from scipy.stats import mannwhitneyu

# -----------------------------------------------------------------------
# 1. Load the labeled dataset from Step 7
# -----------------------------------------------------------------------
sfi_df = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Processed/sfi_scores_with_label.csv", index_col="seller_id")
print(f"Loaded {sfi_df.shape[0]} sellers with SFI scores and future labels")

# -----------------------------------------------------------------------
# 2. Restrict to sellers who were ACTIVE at the snapshot
#    (this is the group where volume alone gives no warning signal)
# -----------------------------------------------------------------------
active_at_snapshot = sfi_df[sfi_df["recent_volume"] > 0].copy()
print(f"Sellers active at snapshot: {active_at_snapshot.shape[0]}")

became_inactive = active_at_snapshot[active_at_snapshot["is_inactive"] == 1]
stayed_active = active_at_snapshot[active_at_snapshot["is_inactive"] == 0]

print(f"  - Became inactive afterward: {became_inactive.shape[0]}")
print(f"  - Stayed active: {stayed_active.shape[0]}")

# -----------------------------------------------------------------------
# 3. Compare SFI and each component between the two groups
# -----------------------------------------------------------------------
metrics = ["SFI", "volume_decay", "review_decay", "delay_surge"]

print("\n" + "=" * 70)
print("GROUP COMPARISON: Became Inactive (n={}) vs Stayed Active (n={})".format(
    became_inactive.shape[0], stayed_active.shape[0]))
print("=" * 70)

results = []
for metric in metrics:
    inactive_vals = became_inactive[metric].dropna()
    active_vals = stayed_active[metric].dropna()

    stat, pval = mannwhitneyu(inactive_vals, active_vals, alternative="greater")

    results.append({
        "metric": metric,
        "mean_became_inactive": round(inactive_vals.mean(), 4),
        "mean_stayed_active": round(active_vals.mean(), 4),
        "median_became_inactive": round(inactive_vals.median(), 4),
        "median_stayed_active": round(active_vals.median(), 4),
        "mannwhitney_pvalue": round(pval, 5),
        "significant_at_0.05": pval < 0.05
    })

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

print("\nNOTE: alternative='greater' tests whether 'became inactive' group has")
print("HIGHER values than 'stayed active' - this is the directional hypothesis")
print("H1/H2 actually predict (friction signals should be elevated BEFORE")
print("a seller goes inactive, not just after).")

# -----------------------------------------------------------------------
# 4. Save the comparison table for use in the paper's Results section
# -----------------------------------------------------------------------
results_df.to_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Processed/h1_h2_comparison_results.csv", index=False)
print("\nSaved: C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Processed/h1_h2_comparison_results.csv")

