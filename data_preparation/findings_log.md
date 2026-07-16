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

#Issue found while exploring data
Data integrity issue found: Mid-project, Python and SQL baseline counts diverged (1,683 vs 1,643 sellers) despite identical logic. Traced through: kernel state, join types, duplicate keys, seller_id formatting, timestamp parsing options — all ruled out one by one. Root cause: the raw olist_orders_dataset.csv had been opened and saved in Excel at some point, which silently reformatted the date strings (ISO → DD-MM-YYYY, seconds dropped). Fixed by re-downloading a fresh copy from Kaggle. Lesson: treat all files in 02_data/raw/ as strictly read-only; never open raw data in Excel, even just to look at it — use df.head() in Python or a plain text viewer instead.