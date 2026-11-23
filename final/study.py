"""Read the final tables used by the report and presentation."""
import json
from pathlib import Path

import pandas as pd

from rsproject.data import LABELS


PRIMARY = "RS-EF-class-aware"
FIXED = "RS-EF-pruned"
MODELS = (
    ("RS-EF-classic", "Classical Pawlak EF"),
    (FIXED, "Fixed-pruning EF"),
    ("RS-MDLP-pruned", "Fixed-pruning MDLP"),
    (PRIMARY, "Class-aware EF"),
    ("RS-MDLP-class-aware", "Class-aware MDLP"),
    ("DecisionTree", "Decision tree"),
    ("RandomForest", "Random forest"),
    ("NaiveBayes", "Categorical Naive Bayes"),
)
REFERENCES = (
    ("Realinho et al. (2021). Predict Students’ Dropout and Academic Success. UCI Repository.",
     "https://doi.org/10.24432/C5MC89"),
    ("Realinho et al. (2022). Predicting Student Dropout and Academic Success. Data, 7(11), 146.",
     "https://doi.org/10.3390/data7110146"),
    ("Fayyad and Irani (1993). Multi-Interval Discretization. IJCAI, 1022–1029.",
     "https://ijcai.org/proceedings/1993/141"),
    ("Pawlak (1982). Rough sets. International Journal of Computer & Information Sciences, 11, 341–356.",
     "https://doi.org/10.1007/BF01001956"),
    ("Chouchoulas and Shen (2001). Rough set-aided keyword reduction. Applied Artificial Intelligence.",
     "https://doi.org/10.1080/088395101753210773"),
    ("Grzymala-Busse (1997). A new version of the rule induction system LERS. Fundamenta Informaticae.",
     "https://dblp.org/rec/journals/fuin/GrzymalaBusse97.html"),
    ("Yao (2010). Three-way decisions with probabilistic rough sets. Information Sciences, 180, 341–353.",
     "https://doi.org/10.1016/j.ins.2009.09.021"),
    ("Nadeau and Bengio (2003). Inference for the generalization error. Machine Learning, 52, 239–281.",
     "https://doi.org/10.1023/A:1024068626366"),
    ("Zanellati et al. (2024). Balancing Performance and Explainability in Academic Dropout Prediction. IEEE TLT, 17, 2086–2099.",
     "https://doi.org/10.1109/TLT.2024.3425959"),
    ("Carballo-Mendívil et al. (2025). Predicting Student Dropout from Day One. Applied Sciences, 15, 9202.",
     "https://doi.org/10.3390/app15169202"),
    ("Praptomo et al. (2026). Explainable Machine Learning for Predicting Student Dropout and Academic Success Using XGBoost and SHAP. JEECOM, 8(1).",
     "https://doi.org/10.33650/jeecom.v8i1.16978"),
)


def percent(value):
    return f"{value:.1%}"


def signed(value, scale=1, decimals=3):
    return f"{value * scale:+.{decimals}f}"


class Study:
    classes = ["Dropout", "Enrolled", "Graduate"]
    sensitivity_models = (
        ("no_finance", PRIMARY, "Class-aware EF, 27 features"),
        ("no_finance", "RS-MDLP-class-aware", "Class-aware MDLP, 27 features"),
        ("all", "RS-EF-class-aware-k2", "Class-aware EF, 2 bins + finance"),
        ("all", PRIMARY, "Class-aware EF, 4 bins + finance"),
        ("all", "RS-EF-class-aware-k6", "Class-aware EF, 6 bins + finance"),
        ("all", "RS-MDLP-class-aware", "Class-aware MDLP + finance"),
    )

    def __init__(self, root=Path("results/full")):
        self.root = root
        self.config = json.loads((root / "config.json").read_text(encoding="utf-8"))
        if (self.config["repeats"], self.config["folds"]) != (5, 10):
            raise ValueError("The report requires the completed 5 × 10 experiment.")
        tables = root / "tables"
        self.folds = pd.read_csv(root / "fold_results.csv")
        self.primary_folds = self.folds.loc[
            self.folds.feature_set.eq("no_finance") & self.folds.model.eq(PRIMARY)
        ]
        if len(self.primary_folds) != 50 or self.primary_folds.duplicated(["repeat", "fold"]).any():
            raise ValueError("Expected 50 distinct outer evaluations of the primary model.")
        self.metrics = pd.read_csv(tables / "metrics_mean.csv", index_col=[0, 1])
        self.rules = pd.read_csv(tables / "rule_quality.csv", index_col=[0, 1])
        self.confusion = pd.read_csv(tables / "confusion_rates.csv", index_col=[0, 1, 2, 3])
        self.certain = pd.read_csv(tables / "certain_rule_3wd_no_finance.csv", index_col=0)
        self.curves = pd.read_csv(tables / "coverage_curves_no_finance.csv")
        self.regions = pd.read_csv(tables / "dropout_three_regions_no_finance.csv", index_col=0)
        self.significance = pd.read_csv(tables / "significance.csv")
        self.ablation = pd.read_csv(tables / "component_ablation.csv", index_col=0)
        self.learning = pd.read_csv(tables / "learning_curve.csv", index_col=0)
        self.final_rules = pd.read_csv(root / "final_rules_EF_class_aware_no_finance.csv")
        self.examples = [next(self.final_rules.loc[self.final_rules.cls.eq(cls)].itertuples(index=False))
                         for cls in self.classes if self.final_rules.cls.eq(cls).any()]

    def comparison(self, baseline, metric):
        sig = self.significance
        return sig.loc[sig.feature_set.eq("no_finance") & sig.rough_set_model.eq(PRIMARY)
                       & sig.baseline.eq(baseline) & sig.metric.eq(metric)].iloc[0]

    def feature_frequency(self):
        reducts = pd.read_json(self.root / "reducts.json")
        primary = reducts.loc[reducts.feature_set.eq("no_finance") &
                              reducts.method.eq("EF-class-aware")].reduct
        return [(LABELS.get(key, key), count / len(primary))
                for key, count in primary.explode().value_counts().items()]

    @staticmethod
    def p_value(value):
        return "< .0001" if value == 0 else f"{value:.4f}"
