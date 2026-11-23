"""Rough-set core: information granules, approximations, dependency degree,
(approximate) reducts, LEM2 rule induction, rule pruning, LERS-style
classification and three-way decisions.

All functions work on an integer code matrix (objects x attributes)."""
import numpy as np
import pandas as pd


# ---------------------------------------------------------------- granules
def granule_ids(codes):
    """Index of the indiscernibility class (granule) of every object."""
    if codes.shape[1] == 0 or len(codes) == 0:
        return np.zeros(len(codes), dtype=np.int64)
    order = np.lexsort(codes.T[::-1])
    ordered = codes[order]
    starts = np.r_[False, np.any(ordered[1:] != ordered[:-1], axis=1)]
    ids = np.empty(len(codes), dtype=np.int64)
    ids[order] = np.cumsum(starts)
    return ids


def _class_counts(granules, labels, n_classes):
    return np.bincount(granules * n_classes + labels,
                       minlength=(granules.max(initial=-1) + 1) * n_classes).reshape(-1, n_classes)


def _prior_relative(priors, margin):
    return priors + margin * (1 - priors)


def _dependency(counts, min_size, beta, class_aware=False):
    size = counts.sum(1, keepdims=True)
    if class_aware:
        totals = counts.sum(0)
        priors = totals / totals.sum()
        # Precision above the class prior, on a scale from prior to purity.
        threshold = _prior_relative(priors, beta)
        valid = (size >= min_size) & (counts >= threshold * size - 1e-12)
        return float((np.sum(counts * valid, axis=0) / totals).mean())
    positive = (size[:, 0] >= min_size) & (counts.max(1) >= beta * size[:, 0] - 1e-12)
    return float(size[positive].sum() / counts.sum())


def dependency(codes, y, min_size=1, beta=1.0):
    """Generalized dependency degree gamma_B(D) = |POS_B(D)| / |U|.

    Classical Pawlak (min_size=1, beta=1): share of objects whose granule is
    consistent (all members share one decision).
    min_size > 1: a granule only counts as positive if it holds at least
    min_size objects, so tiny granules made by many-valued attributes are
    not mistaken for certain knowledge.
    beta < 1: variable-precision (Ziarko) positive region - a granule counts
    if its majority decision covers at least a beta share of it."""
    classes, labels = np.unique(y, return_inverse=True)
    return _dependency(_class_counts(granule_ids(codes), labels, len(classes)),
                       min_size, beta)


def approximations(codes, y, cls, beta=1.0):
    """Lower and upper approximation (boolean masks) of concept y == cls.
    beta < 1 gives the variable-precision lower approximation: granules
    whose share of the class is >= beta."""
    g = granule_ids(codes)
    share = pd.Series(y == cls).groupby(g).mean().to_numpy()[g]
    return share >= beta - 1e-12, share > 0


def regions(codes, y, beta=1.0):
    """Share of objects in the (beta-)positive and boundary regions."""
    g = granule_ids(codes)
    ct = pd.crosstab(g, y).to_numpy()
    pos = (ct.max(1) >= beta * ct.sum(1) - 1e-12)[g]
    return {"positive": float(pos.mean()), "boundary": float(1 - pos.mean())}


def cond_entropy(codes, y):
    """H(D | B): conditional entropy of the decision given the granules."""
    g = granule_ids(codes)
    ct = pd.crosstab(g, y).to_numpy().astype(float)
    return _entropy_counts(ct)


def _entropy_counts(ct):
    p = ct / ct.sum(1, keepdims=True)
    h = -(np.where(p > 0, p * np.log2(np.where(p > 0, p, 1)), 0)).sum(1)
    return float((ct.sum(1) / ct.sum() * h).sum())


def quick_reduct(codes, y, eps=0.0, min_size=1, beta=1.0, min_gain=None,
                 max_attrs=None, class_aware=False):
    """QuickReduct: greedy forward selection by (generalized) dependency,
    then backward elimination of redundant attributes.

    Stops when gamma_B >= (1 - eps) * gamma_C, or when no attribute raises
    gamma by at least min_gain (with min_size > 1 gamma is not monotone, so
    this is the usual stopping point). Returns (attribute indices, trace)."""
    m = codes.shape[1]
    classical = (min_size == 1 and beta == 1.0 and not class_aware)
    if min_gain is None:       # classical QuickReduct runs to the target
        min_gain = 0.0 if classical else 1e-3
    classes, labels = np.unique(y, return_inverse=True)

    def counts(cols):
        return _class_counts(granule_ids(codes[:, cols]), labels, len(classes))

    def dep(cols):
        return _dependency(counts(cols), min_size, beta, class_aware)
    # the generalized measure is not monotone, so gamma_C is no target there:
    # we grow B until no attribute adds at least min_gain
    target = (1 - eps) * dep(list(range(m))) if classical else 1.0
    nvals = [len(np.unique(codes[:, j])) for j in range(m)]
    B, cur, trace = [], dep([]), []
    while cur < target - 1e-12 and (max_attrs is None or len(B) < max_attrs):
        best = None
        for j in range(m):
            if j in B:
                continue
            # ties (e.g. gamma = 0 for every single attribute) are broken by
            # conditional entropy, then by fewer attribute values
            ct = counts(B + [j])
            key = (_dependency(ct, min_size, beta, class_aware), -_entropy_counts(ct),
                   -nvals[j])
            if best is None or key > best[0]:
                best = (key, j)
        if best is None:
            break
        if min_gain > 0 and best[0][0] - cur < min_gain and B:
            break
        B.append(best[1])
        cur = best[0][0]
        trace.append((best[1], cur))
    final = cur
    for j in list(B):                      # remove redundant attributes
        rest = [a for a in B if a != j]
        if rest and dep(rest) >= final - 1e-12:
            B = rest
    return sorted(B), trace


# -------------------------------------------------------------------- LEM2
def lem2(codes, concept):
    """LEM2 (Grzymala-Busse): minimal set of minimal rules covering a
    definable concept (lower or upper approximation). Returns a list of
    rules, each a tuple of (attribute_index, value) conditions."""
    n, m = codes.shape
    if m == 0 or not concept.any():
        return []
    pairs = [(j, v) for j in range(m) for v in np.unique(codes[:, j])]
    P = np.array([codes[:, j] == v for j, v in pairs])           # P x n
    Pint = P.astype(np.int32)
    psize = P.sum(1)
    pattr = np.array([j for j, _ in pairs])
    rules, covered = [], np.zeros(n, bool)
    G = concept.copy()
    while G.any():
        T, cover, Gcur, used = [], np.ones(n, bool), G.copy(), set()
        while not T or (cover & ~concept).any():
            inter = Pint @ Gcur.astype(np.int32)
            ok = (inter > 0) & ~np.isin(pattr, list(used))
            if not ok.any():
                break
            cand = np.where(ok)[0]
            # max |[t] ∩ G|, ties -> smallest |[t]|
            best = cand[np.lexsort((psize[cand], -inter[cand]))[0]]
            T.append(best)
            used.add(pattr[best])
            cover &= P[best]
            Gcur &= P[best]
        # drop superfluous conditions
        for t in list(T):
            if len(T) == 1:
                break
            rest = [u for u in T if u != t]
            c = np.logical_and.reduce(P[rest])
            if not (c & ~concept).any():
                T, cover = rest, c
        rules.append(T)
        covered |= cover
        G = concept & ~covered
    # drop redundant rules
    covers = [np.logical_and.reduce(P[T]) for T in rules]
    keep = list(range(len(rules)))
    for i in sorted(keep, key=lambda i: covers[i].sum()):
        others = [k for k in keep if k != i]
        if others and (concept <= np.logical_or.reduce(
                [covers[k] for k in others])).all():
            keep = others
    return [tuple((int(pairs[t][0]), int(pairs[t][1])) for t in rules[i])
            for i in keep]


# ------------------------------------------------------------- classifier
class RoughSetRuleClassifier:
    """Reduct -> LEM2 certain (+ possible) rules -> pruning -> LERS voting.

    granule_min, beta : generalized dependency used to pick the reduct
    min_support : keep rules covering >= this many correct training cases
    min_conf    : keep rules with training confidence >= this value
    """

    def __init__(self, reduct_eps=0.0, granule_min=1, beta=1.0,
                 possible_rules=True, min_support=1, min_conf=0.0, class_aware=False):
        self.reduct_eps = reduct_eps
        self.granule_min = granule_min
        self.beta = beta
        self.possible_rules = possible_rules
        self.min_support = min_support
        self.min_conf = min_conf
        self.class_aware = class_aware

    def fit(self, codes, y):
        self.classes_ = np.unique(y)
        self.reduct_, self.reduct_trace_ = quick_reduct(
            codes, y, self.reduct_eps, self.granule_min, self.beta,
            class_aware=self.class_aware)
        C = codes[:, self.reduct_]
        granules = granule_ids(C)
        counts = _class_counts(granules, np.searchsorted(self.classes_, y), len(self.classes_))
        sizes = counts.sum(1, keepdims=True)
        proportions = counts / sizes
        self.class_counts_ = counts.sum(0)
        priors = self.class_counts_ / len(y)
        threshold = _prior_relative(priors, self.beta) if self.class_aware else self.beta
        lower_granules = proportions >= threshold - 1e-12
        if self.class_aware:
            lower_granules &= sizes >= self.granule_min
        coverage = float(lower_granules.any(1)[granules].mean())
        self.regions_ = {"positive": coverage, "boundary": 1 - coverage}
        raw = []
        for ci, cls in enumerate(self.classes_):
            lower = lower_granules[granules, ci]
            upper = counts[granules, ci] > 0
            for r in lem2(C, lower):
                raw.append((r, ci, "certain"))
            if self.possible_rules and (upper & ~lower).any():
                for r in lem2(C, upper):
                    raw.append((r, ci, "possible"))
        self.n_rules_raw_ = len(raw)
        rules = []
        seen = set()
        for conds, ci, kind in raw:
            if (conds, ci) in seen:
                continue
            seen.add((conds, ci))
            m = self._match(C, conds)
            sup = int(m.sum())
            correct = int((m & (y == self.classes_[ci])).sum())
            rules.append(dict(conds=conds, cls=ci, kind=kind, support=sup,
                              strength=correct,
                              conf=correct / sup if sup else 0.0))
        self.rules_all_ = rules
        self.majority_ = int(np.argmax(self.class_counts_))
        self.balanced = self.class_aware
        self.prune(self.min_support, self.min_conf)
        return self

    def prune(self, min_support, min_conf, relative=None):
        """(Re)select rules by support and confidence; cheap, no refit."""
        self.min_support, self.min_conf = min_support, min_conf
        rules = self.rules_all_
        threshold = min_conf
        if relative is None:
            relative = self.class_aware
        if relative:
            priors = self.class_counts_ / self.class_counts_.sum()
            threshold = _prior_relative(priors, min_conf)
        thresholds = np.broadcast_to(threshold, len(self.classes_))
        self.rules_ = [r for r in rules if r["strength"] >= min_support
                       and r["conf"] >= thresholds[r["cls"]]]
        if not self.rules_ and rules:            # never leave it empty
            self.rules_ = sorted(rules, key=lambda r: -r["strength"])[:1]
        self._compile()
        return self

    @staticmethod
    def _match(C, conds):
        m = np.ones(len(C), bool)
        for j, v in conds:
            m &= C[:, j] == v
        return m

    def _compile(self):
        self._attr = [np.array([j for j, _ in r["conds"]]) for r in self.rules_]
        self._val = [np.array([v for _, v in r["conds"]]) for r in self.rules_]
        self._cls = np.array([r["cls"] for r in self.rules_], dtype=int)
        self._w = np.array([r["strength"] * len(r["conds"])
                            for r in self.rules_], dtype=float)
        # relative strength: strength / |class| (for imbalanced classes)
        self._wb = self._w / self.class_counts_[self._cls] if len(self._w) else self._w
        self._certain = np.array([r["kind"] == "certain"
                                  for r in self.rules_], dtype=bool)

    def _match_frac(self, codes):
        """objects x rules: fraction of a rule's conditions satisfied."""
        C = codes[:, self.reduct_]
        F = np.zeros((len(C), len(self.rules_)))
        for k, (a, v) in enumerate(zip(self._attr, self._val)):
            F[:, k] = (C[:, a] == v).mean(1)
        return F

    def scores(self, codes):
        """LERS support per class: complete matching first, partial matching
        (weighted by matching factor) when no rule matches completely.
        Returns (normalized scores, match type per object)."""
        n, K = len(codes), len(self.classes_)
        if not self.rules_:
            P = np.zeros((n, K)); P[:, self.majority_] = 1
            self._last_full = np.zeros((n, 0), bool)
            return P, np.array(["none"] * n)
        F = self._match_frac(codes)
        full = F == 1.0
        S = np.zeros((n, K))
        onehot = np.eye(K)[self._cls]                        # rules x K
        w = self._wb if self.balanced else self._w
        S_full = (full * w) @ onehot
        S_part = (F * w) @ onehot
        has_full = full.any(1)
        S[has_full] = S_full[has_full]
        S[~has_full] = S_part[~has_full]
        kind = np.where(has_full, "complete",
                        np.where(F.max(1) > 0, "partial", "none"))
        tot = S.sum(1, keepdims=True)
        P = np.where(tot > 0, S / np.where(tot > 0, tot, 1), 0)
        P[tot.ravel() == 0, self.majority_] = 1.0
        self._last_full = full
        return P, kind

    def predict(self, codes):
        P, _ = self.scores(codes)
        return self.classes_[P.argmax(1)]

    # ----------------------------------------------------- three-way views
    def three_way_certain(self, codes):
        """Rough-set three-way decision: ACCEPT class c when the object matches
        certain rules (from (beta-)lower approximations) of class c only;
        otherwise
        DEFER (boundary evidence, conflict, or no matching rule).
        Returns predictions with None for deferred objects."""
        P, _ = self.scores(codes)
        full = self._last_full
        out = np.empty(len(codes), dtype=object)
        for i in range(len(codes)):
            cert = full[i] & self._certain
            cls = set(self._cls[cert].tolist())
            out[i] = self.classes_[cls.pop()] if len(cls) == 1 else None
        return out

    def describe_rules(self, pre, columns, top=None, cls=None):
        rows = []
        for r in sorted(self.rules_, key=lambda r: -r["strength"]):
            if cls is not None and self.classes_[r["cls"]] != cls:
                continue
            conds = " AND ".join(pre.describe(columns[self.reduct_[j]], v)
                                 for j, v in r["conds"])
            rows.append(dict(rule=f"IF {conds} THEN {self.classes_[r['cls']]}",
                             cls=self.classes_[r["cls"]], kind=r["kind"],
                             length=len(r["conds"]), support=r["support"],
                             strength=r["strength"], confidence=r["conf"]))
        df = pd.DataFrame(rows)
        return df.head(top) if top else df


def three_way_threshold(P, classes, alpha):
    """Probabilistic (DTRS-style) three-way decision on rule scores:
    decide argmax class when its score >= alpha, else DEFER (None)."""
    out = np.empty(len(P), dtype=object)
    best = P.argmax(1)
    ok = P.max(1) >= alpha
    out[ok] = classes[best[ok]]
    out[~ok] = None
    return out


def binary_three_way(p_target, alpha, beta):
    """Three regions for one target class (e.g. Dropout), Yao (2010):
    ACCEPT if p >= alpha, REJECT if p <= beta, DEFER otherwise."""
    return np.where(p_target >= alpha, "accept",
                    np.where(p_target <= beta, "reject", "defer"))
