"""Repeated stratified 10-fold cross-validation of the rough-set pipeline
against Decision Tree, Random Forest and Naive Bayes.

All preprocessing (category grouping, discretization, reduct, rules) is fit
inside each training fold. Raw per-fold results and test-set scores are
saved so that statistics and figures can be recomputed without refitting.

usage: python -m rsproject.experiment DATA.csv OUTDIR [--repeats 5] [--quick]
"""
import argparse, hashlib, json, os, time, pickle
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold, train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import CategoricalNB
from sklearn.preprocessing import OrdinalEncoder
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                             f1_score, recall_score, matthews_corrcoef)

from . import data
from .discretize import Preprocessor
from .roughsets import RoughSetRuleClassifier

PRUNE = dict(min_support=5, min_conf=0.6)        # fixed before the experiment
GRID = [(s, b) for s in (10, 20, 40) for b in (0.6, 0.7, 0.8)]
PRUNE_GRID = [(s, c) for s in (1, 2, 5, 10, 20, 40) for c in (0, .5, .6, .7, .8)]
CLASS_GRANULATION = [(s, b) for s in (5, 15) for b in (0.12, 0.25, 0.40)]
CLASS_PRUNING = [(s, c) for s in (3, 8) for c in (0.04, 0.12, 0.22)]


def metrics(y, p, classes):
    rec = recall_score(y, p, labels=classes, average=None, zero_division=0)
    out = dict(accuracy=accuracy_score(y, p),
               balanced_accuracy=balanced_accuracy_score(y, p),
               macro_f1=f1_score(y, p, labels=classes, average="macro",
                                 zero_division=0),
               mcc=matthews_corrcoef(y, p))
    for c, r in zip(classes, rec):
        out[f"recall_{c}"] = r
    return out


def rule_stats(clf, codes_test):
    _, kind = clf.scores(codes_test)
    r = clf.rules_
    out = dict(n_rules=len(r),
                n_rules_raw=clf.n_rules_raw_,
                mean_rule_length=float(np.mean([len(x["conds"]) for x in r])) if r else 0,
                mean_support=float(np.mean([x["strength"] for x in r])) if r else 0,
                coverage=float((kind == "complete").mean()),
                reduct_size=len(clf.reduct_),
                boundary_train=clf.regions_["boundary"])
    out.update({f"rules_{cls}": sum(rule["cls"] == i for rule in r)
                for i, cls in enumerate(clf.classes_)})
    return out


def tune_granulation(Xtr, ytr, cats, nums, method, k, seed):
    """Inner holdout (25% of the training fold) to choose granule_min and
    beta; selection by macro-F1 of the pruned model."""
    a, b, ya, yb = train_test_split(Xtr, ytr, test_size=0.25, stratify=ytr,
                                    random_state=seed)
    pre = Preprocessor(cats, nums, method, k).fit(a, ya)
    Za, Zb = pre.transform(a), pre.transform(b)
    best = None
    for s, beta in GRID:
        clf = RoughSetRuleClassifier(granule_min=s, beta=beta, **PRUNE).fit(Za, ya)
        f = f1_score(yb, clf.predict(Zb), average="macro")
        if best is None or f > best[0]:
            best = (f, s, beta)
    return best[1], best[2]


def tune_class_rules(Xtr, ytr, cats, nums, method, k, seed):
    """Select prior-relative granulation and pruning on the inner holdout."""
    a, b, ya, yb = train_test_split(Xtr, ytr, test_size=0.25, stratify=ytr,
                                    random_state=seed)
    pre = Preprocessor(cats, nums, method, k).fit(a, ya)
    za, zb = pre.transform(a), pre.transform(b)
    best = None
    for size, beta in CLASS_GRANULATION:
        clf = RoughSetRuleClassifier(granule_min=size, beta=beta, class_aware=True)
        clf.fit(za, ya)
        for support, confidence in CLASS_PRUNING:
            clf.prune(support, confidence)
            pred = clf.predict(zb)
            score = (balanced_accuracy_score(yb, pred),
                     f1_score(yb, pred, average="macro"), -len(clf.rules_))
            if best is None or score > best[0]:
                best = (score, dict(granule_min=size, beta=beta, min_support=support,
                                    min_conf=confidence, class_aware=True))
    return best[1]


def baselines(Xtr, ytr, Xte, seed, Ztr=None, Zte=None):
    out = {}
    dt = DecisionTreeClassifier(min_samples_leaf=5, random_state=seed).fit(Xtr, ytr)
    out["DecisionTree"] = (dt.predict(Xte), dt.predict_proba(Xte), dt.classes_)
    rf = RandomForestClassifier(n_estimators=300, n_jobs=-1,
                                random_state=seed).fit(Xtr, ytr)
    out["RandomForest"] = (rf.predict(Xte), rf.predict_proba(Xte), rf.classes_)
    if Ztr is not None:
        encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1,
                                 dtype=np.int64)
        train = encoder.fit_transform(Ztr) + 1
        test = encoder.transform(Zte) + 1
        nb = CategoricalNB().fit(train, ytr)
        out["NaiveBayes"] = (nb.predict(test), nb.predict_proba(test), nb.classes_)
    return out


def run(path, outdir, repeats=5, folds=10, quick=False, seed=42, k=4):
    os.makedirs(outdir, exist_ok=True)
    df = data.load(path)
    classes = data.CLASSES
    rows, scores, reducts, prune_rows, rules_store = [], [], [], [], {}
    cv = RepeatedStratifiedKFold(n_splits=folds, n_repeats=repeats,
                                 random_state=seed)
    settings = [("all", False), ("no_finance", True)]
    t0 = time.time()
    for feat_set, excl in settings:
        X, y, cats, nums = data.early_warning(df, exclude_finance=excl)
        for f_id, (tr, te) in enumerate(cv.split(X, y)):
            rep, fold = divmod(f_id, folds)
            Xtr, Xte, ytr, yte = X.iloc[tr], X.iloc[te], y[tr], y[te]
            base = dict(feature_set=feat_set, repeat=rep, fold=fold)
            preds = {}
            methods = ["EF", "MDLP"] if feat_set == "all" else ["MDLP", "EF"]
            Z = {}
            for method in methods:
                pre = Preprocessor(cats, nums, method, k).fit(Xtr, ytr)
                Ztr, Zte = pre.transform(Xtr), pre.transform(Xte)
                Z[method] = (Ztr, Zte)
                # standard Pawlak pipeline (exact reduct, no pruning)
                if not quick and method == "EF":
                    clf = RoughSetRuleClassifier().fit(Ztr, ytr)
                    preds[f"RS-{method}-classic"] = (clf, Zte, pre)
                s, beta = tune_granulation(Xtr, ytr, cats, nums, method, k,
                                           seed + f_id)
                clf = RoughSetRuleClassifier(granule_min=s, beta=beta,
                                             min_support=1, min_conf=0).fit(Ztr, ytr)
                # pruning sensitivity (cheap: rules are re-selected, not refit)
                if feat_set == "all":
                    for ms, mc in PRUNE_GRID:
                        clf.prune(ms, mc)
                        p = clf.predict(Zte)
                        prune_rows.append(dict(base, method=method, min_support=ms,
                                               min_conf=mc, n_rules=len(clf.rules_),
                                               macro_f1=f1_score(yte, p, average="macro"),
                                               balanced_accuracy=balanced_accuracy_score(yte, p)))
                clf.prune(1, 0)
                preds[f"RS-{method}"] = (pickle.loads(pickle.dumps(clf)), Zte, pre)
                clf.prune(**PRUNE)
                preds[f"RS-{method}-pruned"] = (pickle.loads(pickle.dumps(clf)), Zte, pre)
                clf.balanced = True          # class-normalized LERS voting
                preds[f"RS-{method}-pruned-bal"] = (clf, Zte, pre)
                reducts.append(dict(base, method=method, granule_min=s, beta=beta,
                                    reduct=[pre.columns[j] for j in clf.reduct_]))
                if not quick:
                    params = tune_class_rules(Xtr, ytr, cats, nums, method, k, seed + f_id)
                    aware = RoughSetRuleClassifier(**params).fit(Ztr, ytr)
                    preds[f"RS-{method}-class-aware"] = (aware, Zte, pre)
                    reducts.append(dict(base, method=f"{method}-class-aware", **params,
                                        reduct=[pre.columns[j] for j in aware.reduct_]))
            if not quick and feat_set == "all":
                for bins in (2, 6):
                    pre = Preprocessor(cats, nums, "EF", bins).fit(Xtr, ytr)
                    params = tune_class_rules(Xtr, ytr, cats, nums, "EF", bins, seed + f_id)
                    aware = RoughSetRuleClassifier(**params).fit(pre.transform(Xtr), ytr)
                    preds[f"RS-EF-class-aware-k{bins}"] = (aware, pre.transform(Xte), pre)
            for name, (clf, Zte, pre) in preds.items():
                p = clf.predict(Zte)
                P, kind = clf.scores(Zte)
                tw = clf.three_way_certain(Zte)
                rows.append(dict(base, model=name, **metrics(yte, p, classes),
                                 **rule_stats(clf, Zte),
                                 certain_coverage=float(np.mean([v is not None for v in tw]))))
                scores.append(dict(base, model=name, y=yte, P=P, classes=clf.classes_,
                                   certain=tw, kind=kind))
                if rep == 0 and fold == 0:
                    rules_store[(feat_set, name)] = clf.describe_rules(pre, pre.columns)
            Zm = Z["EF"]
            for name, (p, P, cl) in baselines(Xtr, ytr, Xte, seed + f_id,
                                              Zm[0], Zm[1]).items():
                rows.append(dict(base, model=name, **metrics(yte, p, classes)))
                scores.append(dict(base, model=name, y=yte, P=P, classes=cl))
            print(f"[{feat_set}] repeat {rep} fold {fold} done "
                  f"({time.time() - t0:.0f}s)", flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(outdir, "fold_results.csv"), index=False)
    pd.DataFrame(prune_rows).to_csv(os.path.join(outdir, "pruning_grid.csv"), index=False)
    pd.DataFrame(reducts).to_json(os.path.join(outdir, "reducts.json"), orient="records")
    with open(os.path.join(outdir, "scores.pkl"), "wb") as fh:
        pickle.dump(scores, fh)
    with open(os.path.join(outdir, "rules_fold0.pkl"), "wb") as fh:
        pickle.dump(rules_store, fh)
    json.dump(dict(data=os.path.basename(path), repeats=repeats, folds=folds,
                   data_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                   class_granulation=CLASS_GRANULATION, class_pruning=CLASS_PRUNING,
                   seed=seed, k=k, prune=PRUNE, grid=GRID, n=len(df),
                   class_counts=df["target"].value_counts().to_dict(),
                   runtime_s=time.time() - t0),
              open(os.path.join(outdir, "config.json"), "w"), indent=2)
    return res


def final_rules(path, outdir, method="MDLP", k=4, seed=42, class_aware=False,
                exclude_finance=False):
    """Fit the pruned model on ALL data once, for interpretation only."""
    df = data.load(path)
    X, y, cats, nums = data.early_warning(df, exclude_finance=exclude_finance)
    if class_aware:
        params = tune_class_rules(X, y, cats, nums, method, k, seed)
    else:
        s, beta = tune_granulation(X, y, cats, nums, method, k, seed)
        params = dict(granule_min=s, beta=beta, **PRUNE)
    pre = Preprocessor(cats, nums, method, k).fit(X, y)
    Z = pre.transform(X)
    clf = RoughSetRuleClassifier(**params).fit(Z, y)
    rules = clf.describe_rules(pre, pre.columns)
    tag = method + ("_class_aware" if class_aware else "") + ("_no_finance" if exclude_finance else "")
    rules.to_csv(os.path.join(outdir, f"final_rules_{tag}.csv"), index=False)
    info = dict(method=method, **params,
                reduct=[pre.columns[j] for j in clf.reduct_],
                reduct_trace=[(pre.columns[j], g) for j, g in clf.reduct_trace_],
                regions=clf.regions_, n_rules_raw=clf.n_rules_raw_,
                n_rules=len(clf.rules_),
                cuts={c: list(map(float, pre.tf[c].cuts)) for c in nums})
    json.dump(info, open(os.path.join(outdir, f"final_model_{tag}.json"), "w"),
              indent=2)
    return rules, info


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("outdir")
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    run(a.data, a.outdir, a.repeats, quick=a.quick)
    for m in ("EF", "MDLP"):
        final_rules(a.data, a.outdir, m)
