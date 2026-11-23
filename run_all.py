"""One command for the whole project.

  python run_all.py data/data.csv            # full: 5x10 CV
  python run_all.py data/data.csv --quick    # milestone: 1x10 CV, no classic RS
  python run_all.py --synthetic --quick      # test without the real data

Results go to results/full or results/quick (or results/synthetic):
  summary.md, tables/*.csv, figures/*.png, final_rules_*.csv
"""
import argparse, os, sys

from rsproject import experiment, report, synthetic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?", default="data/data.csv")
    ap.add_argument("--quick", action="store_true",
                    help="1 repeat of 10-fold CV, skip the slow classic model")
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--synthetic", action="store_true",
                    help="generate and use a SYNTHETIC stand-in dataset")
    a = ap.parse_args()

    if a.synthetic:
        os.makedirs("data", exist_ok=True)
        a.data = "data/synthetic.csv"
        synthetic.make().to_csv(a.data, sep=";", index=False)
        out = "results/synthetic"
    else:
        if not os.path.exists(a.data):
            sys.exit(f"{a.data} not found - see data/PUT_data.csv_HERE.txt")
        out = "results/quick" if a.quick else "results/full"

    repeats = 1 if a.quick else a.repeats
    experiment.run(a.data, out, repeats=repeats, quick=a.quick)
    for m in ("EF", "MDLP"):
        experiment.final_rules(a.data, out, m)
        if not a.quick:
            for exclude_finance in (False, True):
                experiment.final_rules(a.data, out, m, class_aware=True,
                                       exclude_finance=exclude_finance)
    report.main(out)
    print(f"\nDone. Open {out}/summary.md and {out}/figures/")


if __name__ == "__main__":
    main()
