# Seller Health & Disengagement Risk

An end-to-end data analytics + machine learning project investigating an underexplored side of marketplace health: **seller disengagement**. Most churn projects analyze customers — this project treats sellers as the marketplace's supply side and builds an early-warning system for when they start quietly disengaging, before they fully go inactive.

## Business Problem

Marketplace-wide metrics (total GMV, total active sellers) can look healthy in aggregate even while individual sellers are reducing order volume, slowing fulfillment, and accumulating worse reviews — until they eventually stop selling altogether. By the time this surfaces in aggregate reporting, the low-cost window for intervention (account manager outreach, support, incentives) has already closed.

Full write-up: [`01_business_discovery/business_problem.md`](01_business_discovery/business_problem.md) · Cross-functional discovery narrative: [`01_business_discovery/business_discovery.md`](01_business_discovery/business_discovery.md)

## The Core Methodology: Seller Friction Index (SFI)

Since no "seller churned" label exists in raw marketplace data, this project constructs one — a composite score combining three operational friction signals:

$$SFI_i = w_1 \cdot \text{VolumeDecay}_i + w_2 \cdot \text{ReviewDecay}_i + w_3 \cdot \text{DelaySurge}_i$$

- **Volume Decay** — relative drop in recent order velocity vs. a seller's own historical baseline
- **Review Decay** — degradation in average customer review score vs. baseline
- **Delay Surge** — share of recent orders shipped later than the seller's own historical norm

Features (SFI inputs) are computed from a **baseline + recent window**; the ML label (did the seller go quiet?) is computed from a **separate, later window** — this time separation is deliberate and central to the project, preventing target leakage and ensuring the model is genuinely predictive rather than descriptive.

## Project Structure

```
seller-churn-risk/
├── 01_business_discovery/
│   ├── business_discovery.md          # Cross-functional investigation narrative
│   └── business_problem.md            # Formal problem statement, objectives, KPIs, scope
├── 02_data/
│   ├── raw/                            # Olist's 9 source CSVs (not committed — see .gitignore)
│   └── processed/                      # Cleaned, merged, feature-engineered data
├── 03_data_preparation/                # Python: multi-source joins, cleaning, feature engineering
├── 04_sql_analysis/                    # SQL: SFI construction, root-cause diagnostic queries
├── 05_ml_model/                        # Python/scikit-learn: predictive model, evaluation
├── 06_tableau/                         # Dashboard spec + published workbook
├── 07_reporting/                       # Executive summary, slide outline
└── README.md
```

## Dataset

[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle) — 9 relational tables covering ~99K orders, ~3K sellers, Sept 2016–Oct 2018.

## Tech Stack

- **Python** (pandas, scikit-learn) — multi-source data integration, feature engineering, modeling
- **SQL** (PostgreSQL) — friction index construction, diagnostic analysis
- **Tableau** — seller risk dashboard
- **Markdown** — documentation

## How to Reproduce

```bash
git clone https://github.com/<your-username>/seller-churn-risk.git
cd seller-churn-risk

# Download the 9 Olist CSVs from Kaggle into 02_data/raw/

python -m venv venv
venv\Scripts\activate   # or source venv/bin/activate on Mac/Linux
pip install pandas numpy matplotlib pyarrow jupyter sqlalchemy scikit-learn

# Run data preparation, then SQL analysis (04_sql_analysis/), then the ML notebook in 05_ml_model/
```

## Key Findings

> _Populate once analysis and modeling are complete._

1. [Finding 1 — SFI distribution / GMV at risk]
2. [Finding 2 — root cause of high-friction sellers]
3. [Finding 3 — model performance and lead-time gained]

## Why This Project Is Different

Nearly every public churn-analysis portfolio project analyzes the customer side of a business. This project instead treats the **seller/supply side** of a marketplace as the at-risk population — a genuinely underexplored angle, since a marketplace's entire value proposition (selection, price competition, availability) depends on sellers staying active. The methodology (a multi-signal friction composite + leakage-safe predictive modeling) is also designed to generalize: any marketplace tracking order volume, review scores, and fulfillment timestamps per seller could retrain this approach on their own data.

## Author
Akshay Rane