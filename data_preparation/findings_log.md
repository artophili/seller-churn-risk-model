Findings Log

Step 1: Load & Explore Raw Data (load_and_explore.py)
Findings:
Shapes - 
Orders shape: (99441, 8)
Sellers shape: (3095, 4)
Order items shape: (112650, 7)
Reviews shape: (99224, 7)
Date range:
Earliest order: 2016-09-04 21:15:19
Latest order:   2018-10-17 17:30:18
Missing values found:
order_id                            0
customer_id                         0
order_status                        0
order_purchase_timestamp            0
order_approved_at                 160
order_delivered_carrier_date     1783
order_delivered_customer_date    2965
order_estimated_delivery_date       0
dtype: int64
Order status breakdown:
ORDER STATUS BREAKDOWN (only orders MISSING a delivery date)
order_status
shipped        1107
canceled        619
unavailable     609
invoiced        314
processing      301
delivered         8
created           5
approved          2
Name: count, dtype: int64
Any surprises or edge cases:
Total canceled orders: 625
Canceled orders WITH a delivery date recorded: 6
(Expected: a small number - likely post-delivery cancellations/refunds, not a data error)


Step 2: Baseline Volume (baseline_volume.py)
============================================================
BASELINE WINDOW: 2017-04-01 to 2018-01-01

#Issue found while exploring data
Data integrity issue found: Mid-project, Python and SQL baseline counts diverged (1,683 vs 1,643 sellers) despite identical logic. Traced through: kernel state, join types, duplicate keys, seller_id formatting, timestamp parsing options — all ruled out one by one. Root cause: the raw olist_orders_dataset.csv had been opened and saved in Excel at some point, which silently reformatted the date strings (ISO → DD-MM-YYYY, seconds dropped). Fixed by re-downloading a fresh copy from Kaggle. Lesson: treat all files in data/raw/ as strictly read-only; never open raw data in Excel, even just to look at it — use df.head() in Python or a plain text viewer instead.

Final verdict for step 2 : Final validated baseline: 1,643 unique sellers, median 5 orders, max 1,152. Eligible sellers (≥5 orders): 898 (54.7%).

Step 3: Review Dedup + Baseline Review Score
There are 551 orders which have more than one review row. First we dedup the review data and we found below insights
We found that some data contains resubmissions of the same review scores so this can affect the average score for the sellers. We are considering the latest score as the score for that seller however this could be a limitation in the final report as we are considering the most recent review only by assuming that review as the customer's settled opinion.
There are total Eligible sellers: 898
Duplicate order ids where 551 and after deduplication the review rows are 98673
Baseline eligible rows after dedup are 38359 with mean review of 4.10 and median review as 4.17.

Step 4: Baseline Delay
345 of 38,359 baseline order-seller rows (~0.9%) are missing a processing time value — expected, since orders that were canceled/unavailable/still-processing never got a carrier handoff date.
897 of 898 eligible sellers have valid baseline delay data. 1 seller was lost at this stage — investigated directly and confirmed: all 8 of their baseline orders were stuck in processing status, so no carrier date exists for any of them. Not a data error, a genuine "this seller's baseline orders never shipped" case.
Baseline processing time distribution: median 2.29 days, mean 3.06 days, max 27.1 days — right-skewed as expected
Decision: the 1 seller with no valid delay data will be excluded from the final SFI-eligible population (897 sellers going into Step 5+), since they can't receive a DelaySurge score. This is a negligible loss (0.1%).

step 5: 
190 of 897 sellers (21.2%) went completely quiet — zero recent orders despite meeting the baseline activity threshold. That's a substantial, headline-worthy number for your paper on its own.
Review score: baseline mean 4.10 → recent mean 3.84. A real, meaningful decline (~0.26 points) among sellers who did have recent orders — directionally exactly what your friction hypothesis predicts: satisfaction erodes before/alongside volume decline, not just among the fully-gone sellers.
Delay: baseline median 2.29 days → recent median 2.36 days. Nearly flat at the aggregate level — similar to what you saw in your last project, aggregate delay doesn't move much, but (as we found investigating the delay_surge ceiling earlier) there's likely a real subset of individual sellers with a sharp increase, hidden inside this stable-looking median.
703 of 707 sellers have delay data — 4 sellers with recent orders but no valid delay data (likely all their recent orders are still in-transit/canceled/unavailable) — small, expected loss, similar pattern to Step 4.

Step 6 — SFI Calculation
SFI
Low (0-0.15)            43.0
Moderate (0.15-0.35)    41.5
High (0.35-1.0)         15.5

SFI
Low (0-0.15)            386
Moderate (0.15-0.35)    372
High (0.35-1.0)         139

There are total 15.5% sellers i.e Around 139 sellers out of 897 are showing in high risk category according to SFI index.



