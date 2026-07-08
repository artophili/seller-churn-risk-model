# Research Hypotheses (Finalized Scope)

## Core Research Question

> Can a multi-signal composite of supply-side behavioral friction (order volume decay, review score decay, fulfillment delay surge) predict seller disengagement earlier and more reliably than order volume alone, in a two-sided e-commerce marketplace?

## Primary Hypotheses (full empirical treatment — the spine of this study)

**H1:** Seller disengagement is a gradual, multi-signal process rather than a sudden event — operational friction (delivery delays) and satisfaction decline (reviews) measurably precede order volume decline.

**H2:** A composite Seller Friction Index (SFI), combining volume decay, review decay, and delay surge, predicts future seller inactivity significantly better (higher precision/recall/AUC) than order volume decline alone.

*These two hypotheses will receive the full treatment: literature grounding, formal methodology, a leakage-safe train/label split, model evaluation, and discussion.*

## Supporting Motivational Fact (not a full hypothesis — contextual, one section)

**Context statistic:** Marketplace GMV is highly concentrated among a small subset of sellers (consistent with documented power-law/Pareto patterns in real marketplaces — Amazon, eBay, Etsy, TikTok Shop). This will be calculated directly on the Olist dataset (top-X% seller GMV share) and used in the Introduction/Discussion to justify *why* seller-level risk matters disproportionately — not defended as an independent research contribution.

## Future Work (mentioned, not answered, in this study)

**H4 (deferred):** Certain product categories may be more exposed to supply-side risk than others, creating category-level availability risk. Flagged in the Conclusion as a natural extension, not investigated empirically here — attempting to answer this alongside H1/H2 would dilute the rigor of the core contribution.

## Why This Scoping Decision

A paper attempting to fully defend four hypotheses at once tends to under-deliver on all of them. Concentrating full rigor on H1/H2 — the genuinely novel contribution — produces a defensible, complete piece of work rather than four shallow threads. This mirrors standard practice in applied ML papers: one tight empirical claim, well-evidenced, beats several loosely-supported ones.
