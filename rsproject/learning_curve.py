"""Measure the effect of training sample size on the finance-excluded model."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold, train_test_split

from .data import CLASSES, early_warning, load
from .discretize import Preprocessor
from .experiment import metrics, tune_class_rules
from .roughsets import RoughSetRuleClassifier


def run(source=Path("data/data.csv"), output=Path("results/full")):
    X, y, cats, nums = early_warning(load(source), exclude_finance=True)
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=5, random_state=42)
    rows = []
    for i, (train, test) in enumerate(cv.split(X, y)):
        # Nested samples make adjacent training sizes comparable within each split.
        smaller = train
        for fraction, previous in ((1.0, 1.0), (.75, 1.0), (.50, .75), (.25, .50)):
            if fraction < previous:
                smaller, _ = train_test_split(smaller, train_size=fraction / previous,
                                               stratify=y[smaller], random_state=2026 + i)
            x_train, y_train = X.iloc[smaller], y[smaller]
            setting = tune_class_rules(x_train, y_train, cats, nums, "EF", 4, 42 + i)
            pre = Preprocessor(cats, nums, "EF", 4).fit(x_train, y_train)
            clf = RoughSetRuleClassifier(**setting).fit(pre.transform(x_train), y_train)
            pred = clf.predict(pre.transform(X.iloc[test]))
            rows.append(dict(repeat=i // 10, fold=i % 10, fraction=fraction,
                             training_students=len(smaller), rules=len(clf.rules_),
                             **metrics(y[test], pred, CLASSES)))
    folds = pd.DataFrame(rows)
    original = pd.read_csv(output / "fold_results.csv")
    original = original.query("feature_set == 'no_finance' and model == 'RS-EF-class-aware'")
    paired = folds.loc[folds.fraction.eq(1)].merge(original, on=["repeat", "fold"])
    if len(paired) != 50 or not np.allclose(paired.macro_f1_x, paired.macro_f1_y):
        raise ValueError("Full-size learning curve failed to reproduce the primary results.")
    tables = output / "tables"
    folds.to_csv(tables / "learning_curve_folds.csv", index=False)
    columns = ["training_students", "macro_f1", "recall_Enrolled", "rules"]
    mean = folds.groupby("fraction")[columns].mean()
    spread = folds.groupby("fraction")[["macro_f1", "recall_Enrolled"]].std().add_suffix("_sd")
    mean.join(spread).to_csv(tables / "learning_curve.csv")


if __name__ == "__main__":
    run()
