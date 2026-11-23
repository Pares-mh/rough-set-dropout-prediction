"""Discretization (fit on training folds only).

EqualFrequency : unsupervised quantile cuts (k intervals).
MDLP           : supervised entropy-based cuts, Fayyad & Irani (1993) MDL stop.
CategoryGrouper: merges rare category codes into one 'other' value so that
                 information granules are not fragmented by rare codes.
"""
import numpy as np


class EqualFrequency:
    name = "EF"

    def __init__(self, k=4):
        self.k = k

    def fit(self, x, y=None):
        qs = np.quantile(x, np.linspace(0, 1, self.k + 1)[1:-1])
        cuts = np.unique(qs)
        # a cut at the minimum would create an empty bin
        self.cuts = cuts[cuts > np.min(x)]
        return self

    def transform(self, x):
        return np.searchsorted(self.cuts, x, side="right")


def _entropy(counts):
    n = counts.sum()
    if n == 0:
        return 0.0
    p = counts[counts > 0] / n
    return float(-(p * np.log2(p)).sum())


class MDLP:
    name = "MDLP"

    def __init__(self, max_depth=8):
        self.max_depth = max_depth

    def fit(self, x, y):
        classes, yi = np.unique(y, return_inverse=True)
        vals, vi = np.unique(x, return_inverse=True)
        # class counts per distinct value
        counts = np.zeros((len(vals), len(classes)))
        np.add.at(counts, (vi, yi), 1)
        self._vals, self._counts = vals, counts
        self.cuts = np.array(sorted(self._split(0, len(vals), 0)))
        return self

    def _split(self, lo, hi, depth):
        """Recursive split on distinct-value index range [lo, hi)."""
        if hi - lo < 2 or depth >= self.max_depth:
            return []
        c = self._counts[lo:hi]
        total = c.sum(0)
        n = total.sum()
        ent = _entropy(total)
        cum = np.cumsum(c, 0)[:-1]          # left counts for each cut point
        def weighted_entropy(counts):
            probabilities = counts / counts.sum(1, keepdims=True)
            return -(counts * np.log2(np.where(counts > 0, probabilities, 1))).sum(1)

        candidate_entropy = (weighted_entropy(cum) + weighted_entropy(total - cum)) / n
        best_i = int(candidate_entropy.argmin())
        bl, br = cum[best_i], total - cum[best_i]
        best = candidate_entropy[best_i]
        gain = ent - best
        k = (total > 0).sum()
        k1, k2 = (bl > 0).sum(), (br > 0).sum()
        delta = np.log2(3 ** k - 2) - (k * ent - k1 * _entropy(bl)
                                       - k2 * _entropy(br))
        if gain <= (np.log2(n - 1) + delta) / n:
            return []
        cut_idx = lo + best_i
        cut = (self._vals[cut_idx] + self._vals[cut_idx + 1]) / 2
        return ([cut] + self._split(lo, cut_idx + 1, depth + 1)
                + self._split(cut_idx + 1, hi, depth + 1))

    def transform(self, x):
        return np.searchsorted(self.cuts, x, side="right")


class CategoryGrouper:
    OTHER = -1

    def __init__(self, min_frac=0.02):
        self.min_frac = min_frac

    def fit(self, x, y=None):
        vals, cnt = np.unique(x, return_counts=True)
        self.keep = set(vals[cnt >= self.min_frac * len(x)].tolist())
        return self

    def transform(self, x):
        return np.array([v if v in self.keep else self.OTHER for v in x])


class Preprocessor:
    """Turns a raw feature DataFrame into a matrix of small integer codes."""

    def __init__(self, cats, nums, method="EF", k=4, min_frac=0.02):
        self.cats, self.nums = cats, nums
        self.method, self.k, self.min_frac = method, k, min_frac

    def fit(self, X, y):
        self.tf = {}
        for c in self.cats:
            self.tf[c] = CategoryGrouper(self.min_frac).fit(X[c].to_numpy())
        for c in self.nums:
            d = EqualFrequency(self.k) if self.method == "EF" else MDLP()
            self.tf[c] = d.fit(X[c].to_numpy().astype(float), y)
        self.columns = self.cats + self.nums
        return self

    def transform(self, X):
        out = np.empty((len(X), len(self.columns)), dtype=np.int64)
        for j, c in enumerate(self.columns):
            v = X[c].to_numpy()
            out[:, j] = self.tf[c].transform(v if c in self.cats
                                             else v.astype(float))
        return out

    def n_intervals(self):
        return {c: len(self.tf[c].cuts) + 1 for c in self.nums}

    def describe(self, col, code):
        """Human-readable condition for attribute `col` == `code`."""
        from .data import LABELS, VALUE_NAMES
        lab = LABELS.get(col, col)
        if col in self.cats:
            if code == CategoryGrouper.OTHER:
                return f"{lab} = other (rare code)"
            name = VALUE_NAMES.get(col, {}).get(int(code))
            return f"{lab} = {name}" if name else f"{lab} = code {int(code)}"
        cuts = self.tf[col].cuts
        lo = -np.inf if code == 0 else cuts[code - 1]
        hi = np.inf if code >= len(cuts) else cuts[code]
        f = lambda v: f"{v:g}"
        if np.isinf(lo):
            return f"{lab} < {f(hi)}"
        if np.isinf(hi):
            return f"{lab} >= {f(lo)}"
        return f"{f(lo)} <= {lab} < {f(hi)}"
