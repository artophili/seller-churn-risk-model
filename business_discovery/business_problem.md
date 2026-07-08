# Business Problem Statement
## Seller Health & Disengagement Risk

---

### 1. Background

The company operates a multi-sided e-commerce marketplace (Olist-style model) connecting independent sellers with customers. Marketplace value depends on two sides staying healthy simultaneously: customers who keep buying, and sellers who keep listing, fulfilling, and engaging. Most existing monitoring focuses on the customer side (acquisition, retention, satisfaction). The seller side is comparatively unmonitored — there is no existing system that flags when a seller is quietly disengaging before they formally go inactive.

### 2. Stakeholder

**Head of Marketplace Operations / Seller Success** — owns seller retention, onboarding health, and account management prioritization. Also relevant: **Finance** (GMV forecasting depends on seller-side stability) and **Category Management** (product selection depth depends on active sellers per category).

### 3. Problem Statement

> The business has no early-warning system for seller disengagement. Aggregate metrics (total active seller count, total GMV) can look stable even while individual sellers are quietly reducing order volume, slowing fulfillment, and accumulating worse reviews — until they eventually go fully inactive. By the time this shows up in aggregate reporting or a customer complaint, the opportunity for low-cost intervention (e.g., account manager outreach, support, incentives) has passed.

### 4. Business Objectives

1. Construct an operational, data-driven definition of "seller disengagement" — no such label currently exists in raw operational data.
2. Quantify how many sellers are trending toward disengagement today, and what share of GMV/product selection they represent.
3. Identify the earliest behavioral signals (order volume trends, review score trends, fulfillment delay trends) that precede full seller inactivity.
4. Build a predictive model that flags at-risk sellers early enough for account management to intervene — using only information available *before* a seller's activity actually collapses.
5. Translate model output into a business-usable risk score/tier that Seller Success can act on directly.

### 5. Key Business Questions

| # | Question | Analysis Type |
|---|---|---|
| 1 | How should "seller disengagement" be defined and measured from behavioral data (volume, reviews, fulfillment speed)? | Feature/label construction |
| 2 | What is the Seller Friction Index (SFI) — a composite score combining volume decay, review decay, and delay surge — and how is it distributed across the seller base today? | Diagnostic / segmentation |
| 3 | What share of total GMV and product category coverage is represented by high-friction sellers? | Impact sizing |
| 4 | Do high-friction sellers share common characteristics (category, tenure, region, order size) that explain *why* they're struggling? | Root cause analysis |
| 5 | Can a machine learning model predict future seller inactivity using only pre-snapshot behavioral signals, without leaking future information? | Predictive modeling |
| 6 | How much earlier would this model flag risk compared to the business noticing organically (e.g., via a support escalation or a quarterly seller count drop)? | Business impact translation |

### 6. Success Metrics (KPIs)

- Distribution of Seller Friction Index (SFI) across the active seller base (healthy / moderate-risk / high-risk tiers)
- % of GMV represented by high-friction sellers
- Model precision/recall/AUC on predicting seller inactivity in the future window
- Estimated "lead time" gained — how many months earlier the model would flag a seller vs. natural detection via aggregate reporting

### 7. Scope

**In scope:** Behavioral analysis of existing seller order/review/fulfillment history; construction of a friction/risk scoring methodology; a predictive model trained and validated on historical data with a proper time-based train/label split to avoid leakage; business-impact framing and recommendations.

**Out of scope:** Live/real-time monitoring system deployment; actual retention campaign design or execution; seller survey or qualitative research (not available in this dataset).

### 8. Deliverables & Tools

| Stage | Tool |
|---|---|
| Business framing & problem definition | Markdown (this document + business_discovery.md) |
| Multi-source data preparation | Python (pandas) |
| Friction scoring & root cause analysis | SQL (PostgreSQL) |
| Predictive modeling | Python (scikit-learn) |
| Visualization & dashboard | Tableau |
| Reporting | Executive summary + slide deck |
| Version control / portfolio | GitHub |

### 9. Assumptions & Constraints

- Olist data has no explicit `seller_churned` field — disengagement/inactivity must be operationally defined from behavior (see Seller Friction Index methodology in `04_sql_analysis/`).
- Data is historical and fixed (Sept 2016 – Oct 2018), not live. "Prediction" here means: using a seller's behavior up to a defined snapshot date to predict their activity in a later, held-out window — a valid and standard approach for building a proof-of-concept model without live monitoring infrastructure.
- Features and labels are strictly time-separated (features from baseline/recent windows before the snapshot date; labels from a future window after it) to avoid target leakage — this separation is a core methodological requirement of this project, not an optional detail.
- No seller satisfaction survey or qualitative exit-reason data exists. Disengagement is inferred purely from behavioral proxies (volume, reviews, fulfillment speed) — a limitation to be stated explicitly in the final report.
- Sellers with insufficient order history in the baseline window (below a minimum threshold) are excluded from scoring, since short histories produce unstable/unreliable friction scores rather than being treated as false positives.
