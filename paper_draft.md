# Catching Seller Disengagement Before It Happens: A Friction-Based Early Warning Approach for Online Marketplaces

**Status: Working draft — covers business problem, methodology, and first hypothesis test results. Literature review, GMV analysis, and predictive model sections to be added as those stages complete.**

---

## 1. Introduction

Online marketplaces (like Amazon Marketplace, Etsy, or Olist) work by connecting buyers with independent sellers. For the marketplace to succeed, both sides need to stay healthy — buyers need to keep coming back, and sellers need to keep listing and shipping products.

Most companies pay close attention to the buyer side: are customers happy, are they coming back, are they spending more or less. Far less attention usually goes to the seller side. But if good sellers quietly start slowing down — shipping late, getting worse reviews, selling less — and eventually leave the platform, that hurts every buyer at once, because there's less to choose from and less competition keeping prices fair.

The problem is: by the time a company notices a seller has "gone quiet," it's often too late to do anything cheap and easy about it, like simply reaching out and asking if something's wrong. This paper is about building a way to notice the warning signs *earlier* — while there's still time to act.

## 2. The Business Problem

Big-picture numbers like "total number of active sellers" or "total sales" can look completely normal even while individual sellers are struggling. A handful of sellers quietly reducing their orders, or shipping a bit slower, or picking up a few bad reviews, doesn't show up in a company-wide report until it's already a bigger problem. There's currently no simple, direct way to answer the question: **"Which of our sellers are quietly struggling right now, before they actually stop selling?"**

## 3. Research Questions

This project focuses on two specific, testable questions:

**Question 1 (H1):** Does a seller's trouble show up gradually, across more than one type of behavior (like slower shipping and worse reviews), *before* their order volume actually drops? Or does volume just drop suddenly with no earlier warning signs?

**Question 2 (H2):** Can we build one combined score — using shipping speed, review scores, and order volume together — that identifies sellers likely to go quiet *better* than just watching order volume alone?

*(Two additional angles — how concentrated marketplace revenue is among top sellers, and whether certain product categories are more at risk than others — were considered but deliberately set aside for this paper, to keep the focus tight on the two questions above. They are noted as future work in Section 8.)*

## 4. Data

This study uses the **Olist Brazilian E-Commerce dataset**, a public dataset covering roughly 99,000 orders and 3,000 sellers between September 2016 and October 2018. It includes order timestamps, which seller fulfilled each order, review scores customers left, and shipping information.

## 5. Method: Building a "Seller Friction Score"

There's no existing label in this data that says "this seller quit" or "this seller is struggling" — so the first job was to build one ourselves, from the sellers' actual behavior.

### 5.1 Comparing "now" to "before"

For every seller who had a reasonable amount of order history (at least 5 orders over about 9 months), we compared two things:
- Their **normal, historical behavior** ("baseline") — from April 2017 to January 2018
- Their **more recent behavior** ("recent") — from January 2018 to April 2018

We picked a specific date (April 1, 2018) to act as "today," and only used information available up to that date to build each seller's score. This matters a lot for Question 2 — more on why in Section 5.3.

After applying this baseline requirement, **897 sellers** qualified for the study.

### 5.2 Three signals combined into one score

We measured three things for each seller, comparing recent behavior to their own baseline:

1. **Volume Decay** — how much their order pace slowed down (adjusted fairly for the fact that the "recent" period was shorter than the "baseline" period, so we compared monthly rates, not raw totals).
2. **Review Decay** — how much their average customer rating dropped.
3. **Delay Surge** — how much slower they got at handing orders off to the shipping carrier.

Each of these three signals was turned into a number between 0 (no problem) and 1 (maximum problem), then combined into one overall score, which we call the **Seller Friction Index (SFI)**:

> SFI = 0.3 × Volume Decay + 0.3 × Review Decay + 0.4 × Delay Surge

These starting weights were a reasonable first guess, not something proven optimal — Section 8 discusses testing different weightings as a next step.

### 5.3 The most important design choice: avoiding a "trick" result

A model that just predicts "sellers who already have zero recent orders will have zero future orders too" wouldn't actually be useful — that's not a prediction, that's stating the obvious. To make sure our score is a genuine *early warning*, not just a restatement of something already visible, we split the data into two non-overlapping time periods:

- Everything used to build the friction score comes from **before** April 1, 2018.
- Whether a seller actually became inactive is measured **only** using data from **after** April 1, 2018 (through the end of the dataset, mid-October 2018).

This way, the score is being tested on its ability to predict something it never got to see.

## 6. Results

### 6.1 How many sellers were already gone vs. genuinely at risk

Of the 897 sellers studied:
- **190 sellers (21.2%)** had already stopped receiving orders by the snapshot date — these are already-visible cases, not useful for testing an early-warning system.
- Of the **707 sellers who still looked active** at the snapshot date, **92 of them (13%) went on to become completely inactive** in the following 6.5 months, despite looking fine at the time.

This second group — 92 sellers who looked completely normal but were about to disappear — is exactly who an early-warning system needs to catch, and exactly who we tested our score against.

### 6.2 Did the friction signals show up before these sellers disappeared?

We compared the 92 "became inactive" sellers against the 615 who stayed active, looking at each signal separately:

| Signal | Average score (sellers who became inactive) | Average score (sellers who stayed active) | Meaningful difference? |
|---|---|---|---|
| **Overall Friction Score (SFI)** | 0.325 | 0.165 | **Yes** |
| Volume slowdown | 0.381 | 0.144 | **Yes** |
| Review score drop | 0.172 | 0.100 | No |
| Shipping slowdown | 0.397 | 0.230 | **Yes** |

("Meaningful difference" here means we ran a statistical test confirming the gap between groups almost certainly isn't due to random chance.)

### 6.3 What this tells us

**The combined Friction Score does distinguish at-risk sellers from healthy ones, using only information from before they actually went inactive.** Sellers who were about to disappear had, on average, roughly double the friction score of sellers who stayed. This supports Question 2 — a combined score genuinely adds early-warning value beyond just watching order volume.

However, the results only **partly** support Question 1. We expected all three signals (volume, reviews, shipping speed) to show trouble gradually building up together. What we actually found:
- **Volume slowdown and shipping delays** were both strong, statistically real warning signs — sellers were already ordering less often and shipping slower before fully disappearing, even while technically still "active."
- **Review scores did not meaningfully differ** between the two groups. In this dataset, a dropping review score does not appear to be an early warning sign of a seller going inactive.

We think it's important to report this honestly rather than only emphasizing the parts that worked — a mixed result like this is more trustworthy than a paper claiming every single piece worked exactly as predicted.

## 7. Limitations

- This dataset only covers a fixed historical period (Sept 2016 – Oct 2018), not live, ongoing data — so "prediction" here means testing the approach on historical data split by time, not a live production test.
- There's no direct information from sellers about *why* they slowed down or left (no surveys or exit interviews) — everything is inferred from their behavior alone.
- A seller is only labeled "inactive" if they have zero orders for the entire ~6.5 month future window — a small number of sellers with occasional gaps may not fit neatly into "active" or "inactive."
- The 0.3 / 0.3 / 0.4 weighting used to combine the three signals into one score was a reasonable starting choice, not a proven optimal one — especially now that we know Review Decay isn't pulling its weight.

## 8. Next Steps

- **Re-test the score with different weightings** — since review score decline didn't turn out to be a meaningful signal, testing a version of the score that weighs volume and shipping delay more heavily (and review score less) is a natural next experiment.
- **Build an actual predictive model** using these signals as inputs, to see how well we could rank sellers by risk, not just confirm a group-level difference.
- **Look at revenue concentration** — how much of the marketplace's total sales come from a small number of sellers, which would show how much is riding on keeping the most important sellers engaged (set aside for this paper, but a natural follow-up).
- **Category-level patterns** — whether certain product categories are more prone to this kind of seller disengagement than others (also set aside for now).
- **Complete literature review** — grounding this work more formally against existing research on seller/store survival in online marketplaces (in progress separately).
