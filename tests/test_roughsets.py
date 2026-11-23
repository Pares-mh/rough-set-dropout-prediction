"""Small hand-checkable tests of the rough-set core (run: pytest)."""
import numpy as np
from rsproject import roughsets as R
from rsproject.discretize import EqualFrequency, MDLP

# toy decision table: 5 students, 2 attributes
CODES = np.array([[0, 0], [0, 1], [1, 0], [1, 1], [1, 1]])
Y = np.array(["a", "a", "b", "b", "a"])


def test_granules():
    g = R.granule_ids(CODES)
    assert g[3] == g[4] and len(set(g)) == 4


def test_approximations():
    lower, upper = R.approximations(CODES, Y, "a")
    assert lower.tolist() == [True, True, False, False, False]
    assert upper.tolist() == [True, True, False, True, True]


def test_dependency():
    assert R.dependency(CODES, Y) == 0.6           # 3 of 5 consistent
    assert R.dependency(CODES, Y, min_size=2) == 0.0


def test_lem2_covers_concept_exactly():
    lower, _ = R.approximations(CODES, Y, "a")
    rules = R.lem2(CODES, lower)
    assert rules == [((0, 0),)]                    # IF a1 = 0 THEN a


def test_reduct():
    red, _ = R.quick_reduct(CODES, Y)
    assert red == [0, 1]


def test_discretizers():
    x = np.arange(100, dtype=float)
    assert len(EqualFrequency(4).fit(x).cuts) == 3
    y = np.where(x < 50, "lo", "hi")
    cuts = MDLP().fit(x, y).cuts
    assert len(cuts) == 1 and abs(cuts[0] - 49.5) < 1e-9
    assert len(MDLP().fit(x, np.array(["c"] * 100)).cuts) == 0


def test_class_aware_dependency_and_pruning_keep_enriched_minority():
    codes = np.array([[0]] * 5 + [[1]] * 5)
    labels = np.array(["common"] * 3 + ["minor"] * 2 + ["common"] * 5)
    fixed = R.RoughSetRuleClassifier(granule_min=2, beta=0.6, min_conf=0.6)
    aware = R.RoughSetRuleClassifier(granule_min=2, beta=0.2, min_conf=0.2,
                                    class_aware=True)
    fixed.fit(codes, labels)
    aware.fit(codes, labels)
    assert "minor" not in fixed.predict(codes)
    assert aware.predict(np.array([[0], [1]])).tolist() == ["minor", "common"]
