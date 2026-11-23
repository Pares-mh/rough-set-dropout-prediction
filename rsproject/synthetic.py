"""SYNTHETIC stand-in with the same column names/format as the UCI data.csv.
Only for testing that the code runs. Results on it mean nothing."""
import numpy as np
import pandas as pd

COLS = ["Marital status", "Application mode", "Application order", "Course",
        "Daytime/evening attendance\t", "Previous qualification",
        "Previous qualification (grade)", "Nacionality",
        "Mother's qualification", "Father's qualification",
        "Mother's occupation", "Father's occupation", "Admission grade",
        "Displaced", "Educational special needs", "Debtor",
        "Tuition fees up to date", "Gender", "Scholarship holder",
        "Age at enrollment", "International"]


def make(n=4424, seed=0):
    r = np.random.default_rng(seed)
    d = {}
    d["Marital status"] = r.choice([1, 2, 4], n, p=[.88, .09, .03])
    d["Application mode"] = r.choice([1, 17, 39, 43, 44, 7], n)
    d["Application order"] = r.integers(0, 7, n)
    d["Course"] = r.choice([9500, 9147, 9238, 9254, 171, 9773, 9670], n)
    d["Daytime/evening attendance\t"] = r.choice([1, 0], n, p=[.89, .11])
    d["Previous qualification"] = r.choice([1, 39, 19, 3], n, p=[.84, .05, .05, .06])
    d["Previous qualification (grade)"] = np.round(r.normal(132, 13, n), 1)
    d["Nacionality"] = r.choice([1, 41, 26], n, p=[.97, .02, .01])
    for c in ["Mother's qualification", "Father's qualification"]:
        d[c] = r.choice([1, 19, 37, 38, 3, 34], n)
    for c in ["Mother's occupation", "Father's occupation"]:
        d[c] = r.choice([9, 4, 5, 7, 10, 3, 0], n)
    d["Admission grade"] = np.round(r.normal(127, 14, n), 1)
    d["Displaced"] = r.choice([1, 0], n)
    d["Educational special needs"] = r.choice([0, 1], n, p=[.99, .01])
    debtor = r.choice([0, 1], n, p=[.89, .11])
    tuition = r.choice([1, 0], n, p=[.88, .12])
    d["Debtor"], d["Tuition fees up to date"] = debtor, tuition
    d["Gender"] = r.choice([0, 1], n, p=[.65, .35])
    sch = r.choice([0, 1], n, p=[.75, .25])
    d["Scholarship holder"] = sch
    age = np.clip(np.round(r.gamma(2, 3, n) + 17), 17, 70).astype(int)
    d["Age at enrollment"] = age
    d["International"] = r.choice([0, 1], n, p=[.97, .03])
    # latent ability drives outcome and semester results
    z = (r.normal(0, 1, n) - 1.2 * (1 - tuition) - .4 * debtor + .3 * sch
         - .04 * (age - 20) + .02 * (d["Admission grade"] - 127))
    enrolled = r.integers(5, 8, n)
    approved = np.clip(np.round(enrolled * (1 / (1 + np.exp(-(z + .8))))
                       + r.normal(0, 1, n)), 0, enrolled).astype(int)
    grade = np.where(approved > 0, np.round(np.clip(r.normal(12 + z, 1.5), 10, 18), 2), 0)
    for s, sh in (("1st", 0), ("2nd", .2)):
        d[f"Curricular units {s} sem (credited)"] = r.choice([0, 0, 0, 1, 2], n)
        d[f"Curricular units {s} sem (enrolled)"] = enrolled
        d[f"Curricular units {s} sem (evaluations)"] = enrolled + r.integers(0, 4, n)
        d[f"Curricular units {s} sem (approved)"] = np.clip(approved + np.round(r.normal(sh, 1, n)), 0, enrolled).astype(int)
        d[f"Curricular units {s} sem (grade)"] = grade
        d[f"Curricular units {s} sem (without evaluations)"] = r.choice([0, 0, 0, 0, 1], n)
    d["Unemployment rate"] = r.choice([10.8, 13.9, 9.4, 16.2, 15.5, 12.4], n)
    d["Inflation rate"] = r.choice([1.4, -0.3, 0.6, 2.8, 0.3], n)
    d["GDP"] = r.choice([1.74, 0.79, -3.12, 3.51, -1.7], n)
    s = z + r.normal(0, .8, n)
    tgt = np.where(s < -0.6, "Dropout", np.where(s < 0.1, "Enrolled", "Graduate"))
    d["Target"] = tgt
    return pd.DataFrame(d)


if __name__ == "__main__":
    import sys
    make().to_csv(sys.argv[1] if len(sys.argv) > 1 else "synthetic.csv",
                  sep=";", index=False)
