"""Probe pruning and voting independently in the finance-excluded EF model."""
import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold

from . import data
from .discretize import Preprocessor
from .experiment import metrics, tune_class_rules
from .roughsets import RoughSetRuleClassifier


def run(path, output):
    x, y, cats, nums = data.early_warning(data.load(path), exclude_finance=True)
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=5, random_state=42)
    rows = []
    for i, (train, test) in enumerate(cv.split(x, y)):
        fold, repeat = i % 10, i // 10
        x_train, x_test = x.iloc[train], x.iloc[test]
        y_train, y_test = y[train], y[test]
        params = tune_class_rules(x_train, y_train, cats, nums, "EF", 4, 42 + i)
        pre = Preprocessor(cats, nums, "EF", 4).fit(x_train, y_train)
        clf = RoughSetRuleClassifier(**params).fit(pre.transform(x_train), y_train)
        z = pre.transform(x_test)
        for mode in ("Class-aware EF", "Without normalized voting", "Common .60 rule cutoff"):
            clf.balanced = mode != "Without normalized voting"
            if mode == "Common .60 rule cutoff":
                clf.prune(5, .6, relative=False)
            rows.append(dict(repeat=repeat, fold=fold, variant=mode, rules=len(clf.rules_),
                             **metrics(y_test, clf.predict(z), data.CLASSES)))
    out = pd.DataFrame(rows)
    output.mkdir(parents=True, exist_ok=True)
    out.to_csv(output / "component_ablation_folds.csv", index=False)
    summary = out.drop(columns=["repeat", "fold"]).groupby("variant").mean()
    summary.round(4).to_csv(output / "component_ablation.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", default="data/data.csv")
    parser.add_argument("--output", type=Path, default=Path("results/full/tables"))
    options = parser.parse_args()
    run(options.data, options.output)
