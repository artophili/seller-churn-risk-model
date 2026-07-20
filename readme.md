# Seller Health & Disengagement Risk

An end-to-end data analytics + machine learning research project investigating an underexplored side of marketplace health: **seller disengagement**. Most churn projects analyze customers — this project treats sellers as the marketplace's supply side and builds an early-warning system for when they start quietly disengaging, before they fully go inactive.

## Business Problem
Right now, big-picture numbers like total sales or total number of sellers can look totally fine — even while individual sellers are quietly selling less, shipping slower, and getting worse reviews. By the time this shows up in the company's overall reports, it's often too late to do anything cheap and easy about it, like having someone reach out to that seller or offer them support before they leave for good.

## Research Framing
This project is grounded in **two-sided market theory** (Rochet & Tirole, 2003/2006) and extends a small, scattered existing literature on seller/store-side churn (Wang et al. 2013; Öztürk, Tunç & Akay 2023; Batta et al. 2023; among others tracked in `01_business_discovery/research_paper_tracker.xlsx`). The core empirical focus is narrowed to two hypotheses, deliberately prioritized over breadth (see `research_hypotheses.md` for the full reasoning):

- **H1:** Seller disengagement is a gradual, multi-signal process — operational friction (Delay surge) and satisfaction decline (Review decline) measurably precede volume decline.
- **H2:** A composite Seller Friction Index (SFI) predicts future seller inactivity better than order volume alone.

## The Core Methodology: Seller Friction Index (SFI)

Since no "seller churned" label exists in raw marketplace data of Olist Brazilian E-Commerce Public Dataset, this project constructs one — a composite score combining three operational friction signals, each comparing a seller's **recent** behavior (Jan–Apr 2018) against their own **historical baseline** (Apr 2017–Jan 2018):

$$SFI_i = 0.3 \cdot \text{VolumeDecay}_i + 0.3 \cdot \text{ReviewDecay}_i + 0.4 \cdot \text{DelaySurge}_i$$

- **Volume Decay** — drop in recent order *rate* (orders/month) vs. baseline rate
- **Review Decay** — degradation in average customer review score vs. baseline
- **Delay Surge** — relative increase in seller processing time (purchase → carrier handoff) vs. baseline

Model features (SFI inputs) are computed from data through a **snapshot date (2018-04-01)**; the eventual ML label (did the seller go quiet?) will be computed from a **separate, later window** — this time separation is deliberate and central to the project, preventing target leakage and ensuring the model is genuinely predictive rather than descriptive.

## Interim Insights (from SFI construction — data prep complete through Step 6)

Based on 897 eligible sellers (sellers with ≥5 baseline orders and valid processing-time data):

1. **21.2% of eligible sellers (190 of 897) went completely silent** in the 3 months following their baseline period — zero recent orders despite a proven history of activity. This is a substantial, previously invisible-in-aggregate population.
2. **Average review score dropped from 4.10 (baseline) to 3.84 (recent)** among sellers who remained active — early evidence that satisfaction erodes *before or alongside* volume decline, not only after, supporting H1.
3. **The SFI risk-tier split is meaningfully three-way, not binary:** 43% Low risk, **41.5% Moderate risk**, 15.5% High risk. The large moderate-risk middle tier — sellers showing real friction but not yet gone — is the population a leading-indicator system like this is specifically designed to catch, and is itself evidence against a simple "active vs. churned" view of seller health.
4. A subset of sellers (~8%) show a **severe fulfillment slowdown** (median absolute increase of ~3.8 days in processing time), confirmed via direct validation (not a small-denominator ratio artifact) — a distinct, real operational-breakdown signal separate from simple volume decline.


## Project Structure

```
seller-churn-risk/
├── 01_business_discovery/
│   ├── business_discovery.md          # Cross-functional investigation narrative
│   ├── business_problem.md            # Formal problem statement, objectives, KPIs, scope
│   ├── research_hypotheses.md         # Finalized, narrowed research scope (H1/H2 core)
│   ├── literature_review.md           # Theoretical grounding + gap analysis
│   ├── reading_list.md                # Source-verification tracking
│   └── research_paper_tracker.xlsx    # Full paper log with verified findings/citations
├── 02_data/
│   ├── raw/                            # Olist's 9 source CSVs (read-only, not committed)
│   └── processed/                      # sfi_scores.csv and other pipeline outputs
├── 03_data_preparation/                # Python: one script per pipeline stage
│   ├── 01_load_and_explore.py
│   ├── 02_baseline_volume.py
│   ├── 03_baseline_review_dedup.py
│   ├── 04_baseline_delay.py
│   ├── 05_recent_window.py
│   ├── 06_sfi_calculation.py
│   └── findings_log.md                 # Methodology reasoning + findings per step
├── 04_sql_analysis/                    # SQL: independent validation + diagnostic queries
├── 05_ml_model/                        # Python/scikit-learn: predictive model, evaluation
├── 06_tableau/                         # Dashboard spec + published workbook
├── 07_reporting/                       # Executive summary, slide outline, final paper
└── README.md
```

## Dataset

[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle) — 9 relational tables covering ~99K orders, ~3K sellers, Sept 2016–Oct 2018.

## Tech Stack

- **Python** (pandas, scikit-learn) — multi-source data integration, feature engineering, modeling
- **SQL** (PostgreSQL) — independent cross-validation of the Python pipeline, diagnostic analysis
- **Tableau** — seller risk dashboard
- **Markdown / Excel** — documentation and literature tracking

## Methodology and the preprocessing steps

- **Window-length normalization bug:** an early version of VolumeDecay compared raw order counts between a 9-month baseline and 3-month recent window without normalizing for length, making even stable sellers appear to have ~67% decay. Fixed by converting both to a monthly rate before comparing.
- **Data corruption caught via independent SQL validation:** a multi-day discrepancy between Python and SQL seller counts was traced back to the raw source CSV having been silently reformatted by Excel (dates reformatted, seconds dropped) during manual review — not a code bug. Resolved by re-downloading a clean source file. This is the direct payoff of validating every pipeline stage two independent ways rather than trusting one implementation.
- **Review deduplication:** 551 order_ids had duplicate review rows (customer resubmissions); resolved by keeping the most-recent review per order, with the ambiguity of this rule explicitly documented as a limitation.

Full reasoning for every step lives in `findings_log.md`.

## How to Reproduce

```bash
git clone https://github.com/<your-username>/seller-churn-risk.git
cd seller-churn-risk

# Download the 9 Olist CSVs from Kaggle into 02_data/raw/
# IMPORTANT: never open raw CSVs in Excel and save them - this silently
# corrupts date formatting (see Methodology Notes above)

python -m venv venv
venv\Scripts\activate   # or source venv/bin/activate on Mac/Linux
pip install pandas numpy matplotlib pyarrow jupyter sqlalchemy scikit-learn

# Run 03_data_preparation/ scripts in order (01 through 06+)
# Then SQL validation (04_sql_analysis/), then the ML notebook in 05_ml_model/
```

## Why This Project Is Different

Nearly every public churn-analysis portfolio project analyzes the customer side of a business. This project instead treats the **seller/supply side** of a marketplace as the at-risk population — a genuinely underexplored angle grounded in two-sided market theory and a small, scattered prior literature (see `literature_review.md`). The methodology (a multi-signal friction composite + leakage-safe predictive modeling) is also designed to generalize: any marketplace tracking order volume, review scores, and fulfillment timestamps per seller could retrain this approach on their own data.

## Author

Akshay Rane