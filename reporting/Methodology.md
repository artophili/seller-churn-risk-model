Setting the minimum-order threshold
Given median = 6, a strict threshold (e.g., "must have 20+ baseline orders") would throw out roughly 75% of sellers — too aggressive. But 1-2 orders is too sparse to compute a stable "baseline average" for volume/review/delay trends.
Recommended threshold: minimum 5 baseline orders. 
This is a defensible middle ground — excludes the bottom ~25-30% (too little history to trust a trend), but keeps the median seller and everyone above eligible.

For SFI calculation
For sellers with zero recent orders, set ReviewDecay = 0 and DelaySurge = 0 (i.e., "no additional information, don't penalize twice") and let VolumeDecay = 1.0 alone drive their SFI up. This avoids double-counting the same underlying "they're gone" signal three times.