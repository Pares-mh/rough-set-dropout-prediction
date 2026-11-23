"""Summary tables, significance tests and figures from saved results.

usage: python -m rsproject.report OUTDIR
writes OUTDIR/summary.md, OUTDIR/tables/*.csv, OUTDIR/figures/*.png
"""
import json, os, pickle, sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .roughsets import binary_three_way

# reference palette (light mode), categorical slots in fixed order
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3de", "#fcfcfb"
BASELINES = ["DecisionTree", "RandomForest", "NaiveBayes"]
METRICS = ["accuracy", "balanced_accuracy", "macro_f1", "mcc",
           "recall_Dropout", "recall_Enrolled", "recall_Graduate"]

plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "savefig.facecolor": SURF})


def corrected_ttest(d, n_train, n_test):
    """Nadeau & Bengio (2003) corrected resampled t-test."""
    d = np.asarray(d, float)
    J = len(d)
    var = d.var(ddof=1)
    if var == 0:
        return (0.0, 1.0) if d.mean() == 0 else (np.copysign(np.inf, d.mean()), 0.0)
    t = d.mean() / np.sqrt((1 / J + n_test / n_train) * var)
    return float(t), float(2 * stats.t.sf(abs(t), J - 1))


def holm(pvals):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0
    for rank, i in enumerate(order):
        run = max(run, min(1, (len(p) - rank) * p[i]))
        adj[i] = run
    return adj


def summarize(res):
    g = res.groupby(["feature_set", "model"])
    mean = g[METRICS].mean()
    sd = g[METRICS].std()
    tab = mean.round(3).astype(str) + " ± " + sd.round(3).astype(str)
    rule_cols = [c for c in ["n_rules", "n_rules_raw", "mean_rule_length",
                             "mean_support", "coverage", "certain_coverage",
                             "reduct_size", "boundary_train",
                             "rules_Dropout", "rules_Enrolled", "rules_Graduate"] if c in res]
    rules = g[rule_cols].mean().dropna(how="all").round(3)
    return mean, tab, rules


def significance(res, cfg, metric, feature_set="all"):
    n = cfg["n"]; k = cfg["folds"]
    n_test = n / k; n_train = n - n_test
    r = res[res.feature_set == feature_set]
    piv = r.pivot_table(index=["repeat", "fold"], columns="model", values=metric)
    rs_models = [m for m in piv.columns if m.startswith("RS-")]
    rows = []
    for a in rs_models:
        comparators = list(BASELINES)
        if a.endswith("-class-aware"):
            comparators.append(a.replace("-class-aware", "-pruned"))
        for b in comparators:
            if b not in piv:
                continue
            d = (piv[a] - piv[b]).dropna()
            try:
                w = stats.wilcoxon(d).pvalue
            except ValueError:
                w = 1.0
            t, pt = corrected_ttest(d, n_train, n_test)
            rows.append(dict(feature_set=feature_set, metric=metric, rough_set_model=a, baseline=b,
                             mean_diff=d.mean(), wilcoxon_p=w,
                             corrected_t=t, corrected_t_p=pt))
    out = pd.DataFrame(rows)
    if len(out):
        out["wilcoxon_p_holm"] = holm(out["wilcoxon_p"])
        out["corrected_t_p_holm"] = holm(out["corrected_t_p"])
    return out


def coverage_curves(scores, models, grid=np.linspace(0.1, 1.0, 19), feature_set="all"):
    """Expected selective accuracy under uniform tie-breaking at the cutoff."""
    out = []
    for s in scores:
        if s["feature_set"] != feature_set or s["model"] not in models:
            continue
        conf = s["P"].max(1)
        pred = s["classes"][s["P"].argmax(1)]
        sorted_conf = np.sort(conf)[::-1]
        correct = pred == s["y"]
        for c in grid:
            m = max(1, int(round(c * len(conf))))
            cutoff = sorted_conf[m - 1]
            above, tied = conf > cutoff, conf == cutoff
            expected = correct[above].sum() + (m - above.sum()) * correct[tied].mean()
            out.append(dict(model=s["model"], coverage=c,
                            accuracy=expected / m, threshold=cutoff))
    return pd.DataFrame(out).groupby(["model", "coverage"]).mean().reset_index()


def certain_points(scores, feature_set="all"):
    rows = []
    for s in scores:
        if s["feature_set"] != feature_set or "certain" not in s:
            continue
        dec = np.array([v is not None for v in s["certain"]])
        acc = (np.array(s["certain"])[dec] == s["y"][dec]).mean() if dec.any() else np.nan
        rows.append(dict(model=s["model"], coverage=dec.mean(), accuracy=acc))
    return pd.DataFrame(rows).groupby("model").mean()


def dropout_regions(scores, models, alpha=0.6, beta=0.3, feature_set="all"):
    """Binary early-warning view for the 'Dropout' class (three regions)."""
    rows = []
    for s in scores:
        if s["feature_set"] != feature_set or s["model"] not in models:
            continue
        j = list(s["classes"]).index("Dropout")
        reg = binary_three_way(s["P"][:, j], alpha, beta)
        isd = s["y"] == "Dropout"
        acc = reg == "accept"; rej = reg == "reject"; dfr = reg == "defer"
        rows.append(dict(model=s["model"], accept_share=acc.mean(),
                         defer_share=dfr.mean(), reject_share=rej.mean(),
                         accept_precision=isd[acc].mean() if acc.any() else np.nan,
                         reject_npv=(~isd[rej]).mean() if rej.any() else np.nan,
                         dropouts_flagged=acc[isd].mean(),
                         dropouts_deferred=dfr[isd].mean(),
                         dropouts_missed=rej[isd].mean(),
                         dropout_rate_in_defer=isd[dfr].mean() if dfr.any() else np.nan))
    return pd.DataFrame(rows).groupby("model").mean()


def confusion_rates(scores):
    rows = []
    for s in scores:
        pred = s["classes"][s["P"].argmax(1)]
        for actual in s["classes"]:
            values = pred[s["y"] == actual]
            rows.extend(dict(feature_set=s["feature_set"], model=s["model"], actual=actual,
                             predicted=label, share=np.mean(values == label))
                        for label in s["classes"])
    return pd.DataFrame(rows).groupby(["feature_set", "model", "actual", "predicted"]).mean()


# ------------------------------------------------------------------ figures
def fig_models(res, path, metric="macro_f1", label="Macro-F1"):
    r = res[res.feature_set == "all"]
    g = r.groupby("model")[metric].agg(["mean", "std"]).sort_values("mean")
    fig, ax = plt.subplots(figsize=(7, 0.42 * len(g) + 1.2))
    y = np.arange(len(g))
    colors = [S1 if m.startswith("RS-") else INK2 for m in g.index]
    ax.errorbar(g["mean"], y, xerr=g["std"], fmt="none", ecolor=GRID,
                elinewidth=2, capsize=0)
    ax.scatter(g["mean"], y, s=60, c=colors, zorder=3,
               edgecolors=SURF, linewidths=2)
    for yi, (m, row) in zip(y, g.iterrows()):
        ax.text(row["mean"] + row["std"] + 0.004, yi, f"{row['mean']:.3f}",
                va="center", color=INK2, fontsize=9)
    ax.set_yticks(y, g.index, color=INK)
    ax.set_xlabel(f"{label} (mean ± SD over CV folds)")
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.set_title(f"{label} by model  ·  blue = rough-set models", loc="left",
                 color=INK, fontsize=11)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_coverage(curves, certain, path, models):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for m, col in zip(models, (S1, S2, S3)):
        c = curves[curves.model == m]
        if c.empty:
            continue
        ax.plot(c.coverage, c.accuracy, color=col, lw=2, label=m)
        if m in certain.index:
            p = certain.loc[m]
            ax.scatter([p.coverage], [p.accuracy], s=70, marker="D", color=col,
                       edgecolors=SURF, linewidths=2, zorder=4)
            ax.annotate("certain-rule 3WD", (p.coverage, p.accuracy),
                        xytext=(8, -14), textcoords="offset points",
                        color=INK2, fontsize=8)
    ax.set_xlabel("Coverage: share of students given a decision")
    ax.set_ylabel("Accuracy on decided students")
    ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower left")
    ax.set_title("Three-way decision: deferring uncertain students",
                 loc="left", color=INK, fontsize=11)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_pruning(grid, path):
    g = grid.groupby(["method", "min_support", "min_conf"])[["n_rules", "macro_f1"]].mean().reset_index()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for m, col in (("EF", S1), ("MDLP", S2)):
        c = g[g.method == m]
        ax.scatter(c.n_rules, c.macro_f1, s=40, color=col, label=f"{m} discretization",
                   edgecolors=SURF, linewidths=1.5, zorder=3)
    ax.set_xscale("log")
    ax.set_xlabel("Number of rules after pruning (log scale)")
    ax.set_ylabel("Macro-F1")
    ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.legend(frameon=False)
    ax.set_title("Pruning by support and confidence: rule count vs. quality",
                 loc="left", color=INK, fontsize=11)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def fig_reducts(reducts, path, method):
    r = reducts[(reducts.feature_set == "all") & (reducts.method == method)]
    cnt = pd.Series([a for red in r.reduct for a in red]).value_counts() / len(r)
    cnt = cnt.sort_values()
    fig, ax = plt.subplots(figsize=(7, 0.35 * len(cnt) + 1.2))
    ax.barh(cnt.index, cnt.values, color=S1, height=0.6)
    for i, v in enumerate(cnt.values):
        ax.text(v + 0.01, i, f"{v:.0%}", va="center", color=INK2, fontsize=9)
    ax.set_xlim(0, 1.12); ax.set_xlabel("Share of CV folds where attribute is in the reduct")
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.set_title(f"Reduct stability ({method})", loc="left", color=INK, fontsize=11)
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def main(outdir):
    res = pd.read_csv(os.path.join(outdir, "fold_results.csv"))
    cfg = json.load(open(os.path.join(outdir, "config.json")))
    scores = pickle.load(open(os.path.join(outdir, "scores.pkl"), "rb"))
    grid = pd.read_csv(os.path.join(outdir, "pruning_grid.csv"))
    reducts = pd.read_json(os.path.join(outdir, "reducts.json"))
    T = os.path.join(outdir, "tables"); F = os.path.join(outdir, "figures")
    os.makedirs(T, exist_ok=True); os.makedirs(F, exist_ok=True)

    mean, tab, rules = summarize(res)
    mean.round(4).to_csv(os.path.join(T, "metrics_mean.csv"))
    tab.to_csv(os.path.join(T, "metrics_mean_sd.csv"))
    rules.to_csv(os.path.join(T, "rule_quality.csv"))
    sig = pd.concat([significance(res, cfg, m, group)
                     for group in ("all", "no_finance")
                     for m in ("macro_f1", "balanced_accuracy")])
    sig.round(4).to_csv(os.path.join(T, "significance.csv"), index=False)

    confusion_rates(scores).round(4).to_csv(os.path.join(T, "confusion_rates.csv"))
    primary = "RS-EF-class-aware" if "RS-EF-class-aware" in mean.loc["all"].index else "RS-EF-pruned"
    curve_models = [primary, "RandomForest", "DecisionTree"]
    for group, suffix in (("all", ""), ("no_finance", "_no_finance")):
        curves = coverage_curves(scores, curve_models, feature_set=group)
        curves.round(4).to_csv(os.path.join(T, f"coverage_curves{suffix}.csv"), index=False)
        cert = certain_points(scores, group)
        cert.round(4).to_csv(os.path.join(T, f"certain_rule_3wd{suffix}.csv"))
        drop = dropout_regions(scores, curve_models, feature_set=group)
        drop.round(4).to_csv(os.path.join(T, f"dropout_three_regions{suffix}.csv"))
        fig_coverage(curves, cert, os.path.join(F, f"coverage_accuracy{suffix}.png"), curve_models)
        if group == "all":
            all_cert, all_drop = cert, drop
    pg = grid.groupby(["method", "min_support", "min_conf"])[["n_rules", "macro_f1", "balanced_accuracy"]].mean().round(4)
    pg.to_csv(os.path.join(T, "pruning_grid_mean.csv"))

    fig_models(res, os.path.join(F, "models_macro_f1.png"))
    fig_models(res, os.path.join(F, "models_balanced_acc.png"),
               "balanced_accuracy", "Balanced accuracy")
    fig_pruning(grid, os.path.join(F, "pruning.png"))
    for m in reducts.method.unique():
        fig_reducts(reducts, os.path.join(F, f"reduct_stability_{m}.png"), m)

    gran = reducts.groupby(["feature_set", "method"])[["granule_min", "beta"]].agg(
        lambda s: s.value_counts().idxmax())
    with open(os.path.join(outdir, "summary.md"), "w", encoding="utf-8") as fh:
        fh.write(f"# Results summary\n\nData: {cfg['data']} (n={cfg['n']}), "
                 f"{cfg['repeats']}x{cfg['folds']} stratified CV, class counts "
                 f"{cfg['class_counts']}\n\n## Metrics (mean ± SD)\n\n")
        fh.write(tab.to_markdown() + "\n\n## Rule quality\n\n" + rules.to_markdown())
        fh.write("\n\n## Significance (rough-set vs baselines, Holm-adjusted)\n\n")
        fh.write(sig.round(4).to_markdown(index=False))
        fh.write("\n\n## Certain-rule three-way decision (finance included)\n\n" + all_cert.round(3).to_markdown())
        fh.write("\n\n## Dropout early-warning regions (alpha=0.6, beta=0.3)\n\n"
                 + all_drop.round(3).to_markdown())
        fh.write("\n\n## Most common granulation choice per fold\n\n" + gran.to_markdown())
    print(open(os.path.join(outdir, "summary.md"), encoding="utf-8").read())


if __name__ == "__main__":
    main(sys.argv[1])
