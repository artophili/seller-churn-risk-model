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
============================================================
Baseline window rows (order-items): 42547
Unique sellers in baseline window:  1683

============================================================
ORDERS-PER-SELLER DISTRIBUTION (baseline window)
============================================================
count    1683.000000
mean       25.280452
std        71.048373
min         1.000000
25%         2.000000
50%         6.000000
75%        20.000000
max      1119.000000
dtype: float64
There are total 1683 unique sellers in the baseline window.


Step 3: Review Dedup + Baseline Review Score (03_baseline_review_dedup.py)

What this step does:




Why it matters:




Findings:


Step 4: Baseline Delay (04_baseline_delay.py)

What this step does:




Why it matters:




Findings:


Step 5: Recent Window (05_recent_window.py)

What this step does:




Why it matters:




Findings:


Step 6: SFI Calculation (06_sfi_calculation.py)

What this step does:




Why it matters:




Findings:


Step 7: Risk Tiers & GMV Concentration (07_risk_tiers_and_gmv.py)

What this step does:




Why it matters:




Findings: