# Milestone: what to submit (due in 1–2 days)

Run `python run_all.py data/data.csv --quick` first. Every number below comes from `results/quick/summary.md`.
**Don't type any numbers in by hand from memory.**

## Suggested structure (about 2 pages, or 4–5 slides)

**1. Progress so far**
- The full pipeline is implemented in Python: discretization (EF, MDLP), reducts, LEM2, pruning, LERS classifier, three-way decision. 6 unit tests check it against a hand-computed toy decision table.
- The early-warning filter is applied: 2nd-semester columns are removed, and that leaves N input attributes (= 30 with the finance attributes, 27 without).
- First results from 10-fold stratified CV (one repeat). The full 5×10 run is planned for the final report.

**2. Preliminary results** (paste from `summary.md`)
- Table: accuracy, balanced accuracy, macro-F1 and MCC for RS-EF-classic, RS-EF-pruned, RS-MDLP-pruned, DT, RF, NB.
- Rule quality: number of rules before and after pruning, mean rule length, coverage.
- Figure: `figures/models_macro_f1.png`.
- Figure: `figures/coverage_accuracy.png`. How much accuracy rises when uncertain students are deferred.
- 3–5 example rules from `final_rules_MDLP.csv`.

**3. Findings and issues so far** (one or two sentences each)
- *Classical reducts overfit*: the exact Pawlak reduct picks many-valued attributes and yields far more rules (compare `n_rules_raw` of RS-EF-classic with the others). Fix: a granule-size-aware dependency (min granule size *s*, precision β), tuned inside each fold.
- *R RoughSets has no entropy discretization*, so we switched to our own Python implementation.
- *Leakage check* on the finance attributes: compare the `all` and `no_finance` rows.
- *"Enrolled" is hard*: look at `recall_Enrolled`. It is the smallest and most ambiguous class, and it ends up mostly in the boundary region.

**4. Plan until the final report (Dec 10)**
- Full 5×10 CV, plus significance tests (Wilcoxon + Holm, corrected t-test)
- Sensitivity: k for equal-frequency, pruning thresholds (grid already saved)
- Dropout early-warning view: accept / defer / reject regions
- Write-up and oral session slides

## Who does what (fill in)
| Task | Person |
|---|---|
| Run experiments, check results | |
| Milestone write-up | |
| Figures / slides | |
