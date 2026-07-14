Baseline window rows: 44958
Unique sellers in baseline: 1643
count - 1643.00000
mean - 27.36336
std - 76.79724
min - 1.00000
25% - 2.00000
50% - 6.00000
75% - 22.00000
max - 1198.00000

1. 1,643 unique sellers appear in the 9-month baseline window (out of ~3,095 total sellers in the dataset — so roughly half the seller base has zero baseline activity in this period, likely sellers who joined later or churned earlier).
2. The distribution is heavily right-skewed: median is just 6 orders, but the mean is 27.4 — pulled up hard by a max of 1,198 orders from a single seller. The gap between the 75th percentile (22) and the max (1,198) is enormous.
3. Sellers eligible for scoring (>=5 baseline orders): 965
% of baseline sellers retained: 58.7

Review data baseline
Sellers with review data in baseline: 965
count    965.000000
mean       4.031913
std        0.622132
min        1.000000
25%        3.818182
50%        4.142857
75%        4.405405
max        5.000000


Delay data baseline
Sellers with delay data in baseline: 961
count    961.000000
mean       3.249157
std        2.971996
min        0.482373
25%        1.740810
50%        2.366308
75%        3.814190
max       33.941528

Recent window calculation - 

Recent volume - sellers with any orders: 749
count    749.000000
mean      26.400534
std       55.613110
min        1.000000
25%        4.000000
50%       10.000000
75%       26.000000
max      524.000000
dtype: float64

Recent review - sellers with data: 749
count    749.000000
mean       3.793076
std        0.877632
min        1.000000
25%        3.428571
50%        3.944444
75%        4.344828
max        5.000000
Name: review_score, dtype: float64

Recent delay - sellers with data: 743
count    743.000000
mean       3.517699
std        3.722800
min        0.350880
25%        1.642020
50%        2.387326
75%        3.934757
max       34.896065

216 sellers (965 − 749) had ZERO orders in the recent window — meaning their VolumeDecay = 1.0 (maximum), even before we compute anything else. This is a real, meaningful chunk of your eligible seller population (22.4%) — worth noting as a headline number for your paper.
Review score dropped slightly: baseline mean ~4.03 → recent mean ~3.79. Directionally exactly what your friction hypothesis predicts — satisfaction is declining, not just volume.
Delay is basically flat (median 2.37 → 2.39 days) — no meaningful DelaySurge signal at the aggregate level, though individual sellers will vary; the aggregate stability doesn't rule out real variation seller-by-seller.