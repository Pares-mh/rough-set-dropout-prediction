"""Loading the UCI 'Predict Students' Dropout and Academic Success' dataset
and building the early-warning feature set (enrollment + 1st semester only)."""
import re
import numpy as np
import pandas as pd

# normalized original column name -> short name
_CANON = {
    "maritalstatus": "marital",
    "applicationmode": "app_mode",
    "applicationorder": "app_order",
    "course": "course",
    "daytimeeveningattendance": "daytime",
    "previousqualification": "prev_qual",
    "previousqualificationgrade": "prev_qual_grade",
    "nacionality": "nationality",
    "nationality": "nationality",
    "mothersqualification": "mother_qual",
    "fathersqualification": "father_qual",
    "mothersoccupation": "mother_occ",
    "fathersoccupation": "father_occ",
    "admissiongrade": "admission_grade",
    "displaced": "displaced",
    "educationalspecialneeds": "special_needs",
    "debtor": "debtor",
    "tuitionfeesuptodate": "tuition_up_to_date",
    "gender": "gender",
    "scholarshipholder": "scholarship",
    "ageatenrollment": "age",
    "international": "international",
    "unemploymentrate": "unemployment",
    "inflationrate": "inflation",
    "gdp": "gdp",
    "target": "target",
}
for _s, _tag in (("1st", "cu1"), ("2nd", "cu2")):
    for _f in ("credited", "enrolled", "evaluations", "approved", "grade",
               "withoutevaluations"):
        _short = "without_eval" if _f == "withoutevaluations" else _f
        _CANON[f"curricularunits{_s}sem{_f}"] = f"{_tag}_{_short}"

CATEGORICAL = ["marital", "app_mode", "course", "daytime", "prev_qual",
               "nationality", "mother_qual", "father_qual", "mother_occ",
               "father_occ", "displaced", "special_needs", "debtor",
               "tuition_up_to_date", "gender", "scholarship", "international"]
NUMERIC_ENROLL = ["app_order", "prev_qual_grade", "admission_grade", "age",
                  "unemployment", "inflation", "gdp"]
NUMERIC_SEM1 = ["cu1_credited", "cu1_enrolled", "cu1_evaluations",
                "cu1_approved", "cu1_grade", "cu1_without_eval"]
SEM2 = ["cu2_credited", "cu2_enrolled", "cu2_evaluations", "cu2_approved",
        "cu2_grade", "cu2_without_eval"]
# attributes whose measurement time is not documented (possible leakage)
FINANCE = ["debtor", "tuition_up_to_date", "scholarship"]

LABELS = {
    "marital": "Marital status", "app_mode": "Application mode",
    "app_order": "Application order", "course": "Course",
    "daytime": "Daytime attendance", "prev_qual": "Previous qualification",
    "prev_qual_grade": "Previous qualification grade",
    "nationality": "Nationality", "mother_qual": "Mother's qualification",
    "father_qual": "Father's qualification",
    "mother_occ": "Mother's occupation", "father_occ": "Father's occupation",
    "admission_grade": "Admission grade", "displaced": "Displaced",
    "special_needs": "Special educational needs", "debtor": "Debtor",
    "tuition_up_to_date": "Tuition fees up to date", "gender": "Gender",
    "scholarship": "Scholarship holder", "age": "Age at enrollment",
    "international": "International", "unemployment": "Unemployment rate",
    "inflation": "Inflation rate", "gdp": "GDP growth",
    "cu1_credited": "1st-sem units credited",
    "cu1_enrolled": "1st-sem units enrolled",
    "cu1_evaluations": "1st-sem evaluations",
    "cu1_approved": "1st-sem units approved",
    "cu1_grade": "1st-sem grade average",
    "cu1_without_eval": "1st-sem units without evaluation",
}
# value names for binary codes (from the UCI variable table)
VALUE_NAMES = {
    "daytime": {1: "daytime", 0: "evening"},
    "gender": {1: "male", 0: "female"},
    **{c: {1: "yes", 0: "no"} for c in
       ["displaced", "special_needs", "debtor", "tuition_up_to_date",
        "scholarship", "international"]},
}
CLASSES = ["Dropout", "Enrolled", "Graduate"]


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def load(path):
    with open(path, "r", encoding="utf-8-sig") as fh:
        head = fh.readline()
    sep = ";" if head.count(";") > head.count(",") else ","
    df = pd.read_csv(path, sep=sep, encoding="utf-8-sig")
    rename, missing = {}, []
    for col in df.columns:
        key = _norm(col)
        if key in _CANON:
            rename[col] = _CANON[key]
    df = df.rename(columns=rename)
    need = CATEGORICAL + NUMERIC_ENROLL + NUMERIC_SEM1 + ["target"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise ValueError(f"columns not found in {path}: {missing}")
    df["target"] = df["target"].astype(str).str.strip().str.capitalize()
    bad = set(df["target"]) - set(CLASSES)
    if bad:
        raise ValueError(f"unexpected target values: {bad}")
    return df


def early_warning(df, exclude_finance=False):
    """Return X (DataFrame), y (np.array of str), categorical and numeric
    column lists. Second-semester attributes are always dropped."""
    cats = [c for c in CATEGORICAL if not (exclude_finance and c in FINANCE)]
    nums = NUMERIC_ENROLL + NUMERIC_SEM1
    X = df[cats + nums].copy()
    y = df["target"].to_numpy()
    return X, y, cats, nums
