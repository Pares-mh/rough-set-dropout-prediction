"""Reproduce anonymized explanations from the first outer test fold."""
import argparse
import json

import numpy as np
from sklearn.model_selection import RepeatedStratifiedKFold

from . import data
from .discretize import Preprocessor
from .experiment import tune_class_rules
from .roughsets import RoughSetRuleClassifier, binary_three_way


def explain_cases(path):
    x, y, cats, nums = data.early_warning(data.load(path), exclude_finance=True)
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=5, random_state=42)
    train, test = next(cv.split(x, y))
    x_train, y_train = x.iloc[train], y[train]
    setting = tune_class_rules(x_train, y_train, cats, nums, "EF", 4, 42)
    pre = Preprocessor(cats, nums, "EF", 4).fit(x_train, y_train)
    clf = RoughSetRuleClassifier(**setting).fit(pre.transform(x_train), y_train)
    z = pre.transform(x.iloc[test])
    scores, kind = clf.scores(z)
    positive = scores[:, list(clf.classes_).index("Dropout")]
    region = binary_three_way(positive, 0.6, 0.3)
    labels = clf.classes_[scores.argmax(1)]
    fraction = clf._match_frac(z)
    cases = []
    for decision in ("accept", "defer", "reject"):
        # Prefer a complete explanation and a score near the region median.
        pool = np.flatnonzero(region == decision)
        if not len(pool):
            continue
        complete = pool[kind[pool] == "complete"]
        if len(complete):
            pool = complete
        idx = int(pool[np.abs(positive[pool] - np.median(positive[pool])).argmin()])
        position = int(test[idx])
        match = fraction[idx]
        eligible = match == 1 if kind[idx] == "complete" else match > 0
        rule_details = []
        candidates = np.flatnonzero(eligible)
        ranking = candidates[np.argsort(-(match * clf._wb)[candidates], kind="stable")]
        for rank in ranking[:3]:
            rule = clf.rules_[rank]
            conditions = [pre.describe(pre.columns[clf.reduct_[j]], value)
                          for j, value in rule["conds"]]
            rule_details.append(dict(conditions=conditions, target=str(clf.classes_[rule["cls"]]),
                                     matched_share=float(match[rank]), support=rule["support"],
                                     confidence=rule["conf"]))
        cases.append(dict(decision=decision, outcome=str(y[position]), prediction=str(labels[idx]),
                          dropout_score=float(positive[idx]), match_type=str(kind[idx]),
                          rules=rule_details))
    return cases


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", nargs="?", default="data/data.csv")
    print(json.dumps(explain_cases(parser.parse_args().data), indent=2))
