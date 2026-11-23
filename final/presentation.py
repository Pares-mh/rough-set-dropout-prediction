"""Build the final presentation with speaker notes and a PDF rehearsal copy."""
from pathlib import Path
import re
from textwrap import wrap

from final.slide_output import Slide, write_pdf, write_pptx
from final.study import Study, PRIMARY, FIXED, percent, signed
from rsproject.case_study import explain_cases


INK = "#142637"
MUTED = "#496171"
TEAL = "#08665D"
ORANGE = "#AA4B27"
PALE = "#E5F1EC"
PAPER = "#FAFBF9"
WHITE = "#FFFFFF"
LINE = "#CFDDE0"


def build(study, cases):
    slides = []
    p = study.metrics.loc["no_finance", PRIMARY]
    fixed = study.metrics.loc["no_finance", FIXED]
    rf = study.metrics.loc["no_finance", "RandomForest"]
    r = study.rules.loc["no_finance", PRIMARY]
    classic = study.rules.loc["no_finance", "RS-EF-classic"]
    d = study.regions.loc[PRIMARY]
    cert = study.certain.loc[PRIMARY]
    rule_counts = study.primary_folds.n_rules
    recall_sd = study.primary_folds.recall_Enrolled.std() * 100
    curves = study.curves.loc[study.curves.coverage.eq(.75)].set_index("model").accuracy

    def slide(title, notes, subtitle=None, size=33):
        s = Slide(PAPER, notes)
        s.text(title, 48, 38, 864, size, INK, True)
        if subtitle:
            s.text(subtitle, 49, 92, 862, 17, MUTED)
        s.box(48, 501, 864, 1, LINE)
        s.text(str(len(slides) + 1), 890, 511, 22, 12, MUTED)
        slides.append(s)
        return s

    def label(s, heading, text, x, y, width=390, size=20):
        s.text(heading, x, y, width, 22, INK, True)
        s.text(text, x, y + 36, width, size, MUTED)

    def table(s, headers, rows, widths, y=146, height=48, size=18):
        x = 48
        for col, width in zip(headers, widths):
            s.box(x, y, width, height, INK)
            s.text(col, x + 12, y + 13, width - 20, size, WHITE, True)
            x += width
        for i, row in enumerate(rows, 1):
            x = 48
            for col, width in zip(row, widths):
                if i % 2:
                    s.box(x, y + i * height, width, height, PALE)
                s.text(str(col), x + 12, y + i * height + 13, width - 20, size, INK)
                x += width

    s = Slide(INK, "Pares, about 45 seconds. Open with the advisor's decision after semester one. "
              "Introduce all three authors. Say that we tested whether interpretable rules can preserve "
              "the harder Enrolled class and support a review queue. The analysis uses UCI dataset 697.")
    slides.append(s)
    s.box(49, 66, 66, 5, "#78C8AF")
    s.text("Information Granular Computing  /  Sichuan University", 49, 93, 866, 17, "#B6D9D0")
    s.text("Rough-set decision rules\nfor early student dropout\nprediction", 48, 145, 864, 51, WHITE, True)
    s.text("Md Pares Mahmud, Abu Hanif, and Shirsha Mitra", 50, 412, 855, 21, "#D9E9E7")
    s.text("Final project presentation", 50, 456, 855, 16, "#B6D9D0")

    s = slide("What can an advisor know after semester one?",
              "Pares, 1 minute. Explain the prediction date and distinguish it from the final outcome "
              "observation date. The primary analysis drops three finance flags because we lack an "
              "independently verified semester-one timestamp for each. We rerun on all 30 features as "
              "a sensitivity analysis. The original data describe 17 programs and entrants from "
              "2008/09 to 2018/19. Repeated folds do not create more students. The public CSV has "
              "no explicit entry-cohort field. Sources: https://doi.org/10.24432/C5MC89 and "
              "https://doi.org/10.3390/data7110146",
              "4,424 students from one Portuguese higher-education institution", size=30)
    for i, (cls, count) in enumerate([("Dropout", 1421), ("Enrolled", 794), ("Graduate", 2209)]):
        x = 51 + 293 * i
        s.text(f"{count:,}", x, 157, 270, 51, TEAL if i == 1 else INK, True)
        s.text(f"{cls}  ·  {percent(count / 4424)}", x, 228, 275, 19, MUTED)
    s.box(48, 296, 864, 2, LINE)
    label(s, "27 predictors in the primary analysis",
          "Enrollment and semester-one data.\nSemester-two fields are excluded.", 50, 330, 438)
    label(s, "30 predictors in the finance check",
          "Adds debtor, tuition, and scholarship.\nTheir cutoff timing needs verification.", 510, 330, 407)

    s = slide("How rough sets turn student profiles into rules",
              "Pares, 90 seconds. Explain that granules are equivalence classes induced by matching "
              "discretized values. For Dropout, a pure Dropout granule lies in Pawlak's lower approximation, "
              "any granule with Dropout lies in the upper approximation. An overlapping granule sits in "
              "the boundary. QuickReduct is greedy. LEM2 induces evidence rules and LERS combines each "
              "matching rule's votes. References: Pawlak 1982, Chouchoulas and Shen 2001, "
              "Fayyad and Irani 1993, Grzymala-Busse 1997.", size=32)
    for i, (head, body) in enumerate([
        ("Discretize", "Group numeric values into\nquantile or entropy-based bins."),
        ("Find a reduct", "Select attributes that preserve\ndecision-relevant granules."),
        ("Induce and prune", "LEM2 extracts IF–THEN rules.\nKeep rules with enough evidence."),
        ("Vote or defer", "LERS combines rule evidence.\nDefer unresolved cases."),
    ]):
        x = 50 + 448 * (i % 2)
        y = 150 + 155 * (i // 2)
        s.box(x, y, 42, 4, TEAL)
        label(s, head, body, x, y + 17, 414)

    s = slide("Enrolled needed a threshold tied to its prevalence",
              "Pares, 90 seconds. Read the example aloud. The thresholds use the training-fold prior "
              "and an independently tuned margin for rule confidence. The reduct score averages "
              "per-class coverage by qualifying granules. Class-aware LERS divides strength by class "
              "size. A 40 percent Enrolled rule can carry evidence when the outcome occurs 18 percent "
              "of the time, but this figure alone says nothing about generalization. Training-fold counts "
              "supply every prior. Hand over to Hanif for the protocol and results.", size=30)
    s.box(48, 126, 864, 91, PALE)
    s.text("Required precision = class prior + margin × (1 − class prior)",
           69, 153, 825, 26, TEAL, True)
    label(s, "Example with a margin of .25",
          "An 18% Enrolled prior requires 38.5%.\nA 50% Graduate prior requires 62.5%.", 49, 267, 435)
    label(s, "Where the change applies",
          "QuickReduct gives each class equal weight.\nPruning uses class-relative thresholds.\nLERS votes are normalized by class size.",
          502, 267, 411, 18)
    s.text("Illustration uses rounded priors. Each fold estimates its own priors.",
           50, 455, 858, 15, MUTED)

    s = slide("Each outer test fold stays untouched",
              "Hanif, 1 minute. Explain the 5 repeats and shared splits. Inside each outer training split, "
              "use a stratified 75/25 holdout to tune granulation and rule pruning. The class-aware model "
              "selects on balanced accuracy, ties on macro-F1 and smaller rule sets. Refit bins, grouping, "
              "reduct and rules using all outer training data. Report forced predictions and test-fold "
              "scores. Both datasets run the same outer splits. No tuning uses the outer test results.")
    for i, (big, sub, width) in enumerate([
        ("75/25", "Inner training / validation", 260),
        ("90/10", "Outer training / test", 266),
        ("50", "Paired outer evaluations", 277),
    ]):
        x = 50 + i * 292
        s.text(big, x, 161, width, 54, TEAL, True)
        s.text(sub, x, 238, width, 20, INK)
    s.box(48, 295, 863, 2, LINE)
    label(s, "Refit before outer testing",
          "Learn bins, reducts, and rules on the\nfull outer training fold.", 49, 335, 420)
    label(s, "Report class-sensitive results",
          "Macro-F1, balanced accuracy, and\nrecall for each student outcome.", 507, 335, 405)

    s = slide("Class-aware rules recovered Enrolled students",
              f"Hanif, 90 seconds. Quote the actual mean gains, then name the cost. "
              f"Class-aware EF used {r.n_rules:.1f} rules. Compared with fixed EF, Dropout recall "
              f"changed by {signed(p.recall_Dropout - fixed.recall_Dropout, 100, 1)} points. "
              f"Enrolled recall varied by {recall_sd:.1f} percentage points in standard deviation "
              "across test folds. "
              "Random forest remains a strong reference. Macro-F1 weighs each outcome equally. "
              "Results are paired mean test-fold estimates, not results from the full-data rule fit.",
              "Finance excluded  /  Means from five repeats of stratified ten-fold CV", size=32)
    table(s, ["Model", "Macro-F1", "Enrolled recall", "Accuracy"], [
        (name, f"{m.macro_f1:.3f}", percent(m.recall_Enrolled), percent(m.accuracy))
        for m, name in [(fixed, "Fixed-pruning EF"), (p, "Class-aware EF"),
                        (study.metrics.loc["no_finance", "DecisionTree"], "Decision tree"),
                        (rf, "Random forest")]
    ], [295, 168, 212, 189], height=49)
    s.text(f"Class-aware EF recovered {percent(p.recall_Enrolled)} of Enrolled students.",
           49, 426, 863, 23, TEAL, True)

    s = slide("Where the mistakes go",
              "Hanif, 1 minute. Each row fixes the recorded class and shows the distribution of forced "
              "predictions. Walk through the Enrolled row. Then mention how an error such as actual "
              "Dropout predicted Graduate has a different intervention cost from confusing two other "
              "categories. These are means of fold-normalized confusion matrices.",
              "Class-aware EF without finance  /  Each row sums to approximately 100%")
    confusion = study.confusion.loc["no_finance", PRIMARY]["share"].unstack()
    table(s, ["Actual outcome", "Predict Dropout", "Predict Enrolled", "Predict Graduate"], [
        (row, *[percent(confusion.loc[row, col]) for col in study.classes])
        for row in study.classes
    ], [225, 213, 213, 213], y=171, height=58)
    s.text("The Enrolled row shows the remaining ambiguity across outcomes.",
           49, 438, 862, 21, TEAL, True)

    s = slide("The rule set remains much smaller than Pawlak’s",
              "Hanif, 75 seconds. Compare rule counts and lengths. The class-aware threshold permits "
              "more evidence than fixed pruning, which costs some compactness. The classical pipeline "
              "has high-granularity partitions and a much larger rule set. Use support and confidence "
              "to describe profile matches. A training-rule confidence is a historical frequency. "
              "Hand off to Shirsha for the advising example.",
              "Average rules per outer training fold  /  Finance excluded", size=32)
    for i, (name, count, note) in enumerate([
        ("Classical Pawlak", classic.n_rules, "Exact dependency"),
        ("Fixed-pruning EF", study.rules.loc["no_finance", FIXED].n_rules, "Common thresholds"),
        ("Class-aware EF", r.n_rules, f"Median {rule_counts.median():.0f}. "
         f"Range {rule_counts.min():.0f}–{rule_counts.max():.0f} rules."),
    ]):
        y = 149 + i * 103
        s.text(name, 50, y, 330, 25, INK, True)
        s.text(note, 50, y + 38, 330, 17, MUTED)
        s.text(f"{count:,.1f}", 388, y - 6, 250, 40, TEAL if i == 2 else INK, True)
        s.box(48, y + 76, 864, 1, LINE)

    accepted = next(case for case in cases if case["decision"] == "accept")
    deferred = next(case for case in cases if case["decision"] == "defer")
    rule = accepted["rules"][0]
    s = slide("Two held-out cases show how an advisor could act",
              "Shirsha, 90 seconds. These are anonymized cases from the first outer test fold. We "
              "prefer a case with complete matching near the median score in each region. Explain the "
              "matched Dropout rule and its training confidence. The normalized vote can be 1 when "
              "only one class receives votes, even with a much lower rule confidence. The deferred "
              "case has competing full matches. These selected examples illustrate operation and "
              "do not estimate how often the policy is right. Thresholds are .60 and .30.", size=29)
    label(s, "Case A  /  Flag for outreach",
          f"Dropout score {accepted['dropout_score']:.2f}\nObserved outcome {accepted['outcome']}",
          50, 128, 416)
    label(s, "Case B  /  Defer for review",
          f"Dropout score {deferred['dropout_score']:.2f}\nObserved outcome {deferred['outcome']}",
          493, 128, 417)
    s.box(49, 272, 416, 168, PALE)
    s.box(492, 272, 419, 168, PALE)
    lines = "\n".join(wrap("IF " + " AND ".join(rule["conditions"]), width=41))
    s.text(lines + f"\nTHEN {rule['target']}", 63, 294, 390, 19, INK, True)
    s.text(f"{rule['support']:,} matched training cases\n{percent(rule['confidence'])} rule confidence",
           63, 367, 390, 17, MUTED)
    targets = list(dict.fromkeys(item["target"] for item in deferred["rules"]))
    s.text("Matched rules supported\n" + " and ".join(targets) + ".",
           507, 294, 389, 19, INK, True)
    s.text("The score falls inside the\nreview interval of .30 to .60.", 507, 367, 390, 17, MUTED)

    s = slide("Abstention changes both accuracy and workload",
              "Shirsha, 90 seconds. The curve ranks forced predictions by model confidence. "
              "At the coverage cutoff we average the expected contribution of tied scores, "
              "so record order cannot pick which tied students count. The separate diamond "
              "is the certain-rule policy. Distinguish this multiclass selective evaluation "
              "from the next binary Dropout alert policy. "
              "Three-way background: https://doi.org/10.1016/j.ins.2009.09.021",
              "Finance excluded  /  Test-fold accuracy among cases given a decision", size=31)
    s.image(study.root / "figures" / "coverage_accuracy_no_finance.png", 48, 132, 528, 339.4)
    s.text("At 75% coverage", 620, 156, 290, 25, INK, True)
    s.text(f"{percent(curves[PRIMARY])}  Class-aware EF\n{percent(curves['RandomForest'])}  Random forest",
           620, 207, 290, 21, TEAL, True)
    s.text(f"Certain-rule policy\n{percent(cert.coverage)} coverage\n{percent(cert.accuracy)} selective accuracy",
           620, 320, 290, 20, MUTED)

    s = slide("How many recorded dropouts get an alert?",
              "Shirsha, 75 seconds. Here we focus on Dropout as a single target. The bar counts decisions "
              "among actual dropouts only. Some would receive no alert. Precision uses a different "
              "denominator: of those flagged, how many truly dropped out? The cutoffs are illustrative "
              "and the vote score has no probability calibration.",
              "Class-aware EF, 27 predictors  /  Illustrative Dropout score cutoffs .30 and .60")
    items = [("Alert", d.dropouts_flagged, TEAL), ("Defer", d.dropouts_deferred, "#659095"),
             ("No alert", d.dropouts_missed, ORANGE)]
    offset = 48
    denom = sum(frac for _, frac, _ in items)
    for i, (name, frac, color) in enumerate(items):
        width = 864 * frac / denom
        s.box(offset, 168, width, 31, color)
        offset += width
        x = 49 + 294 * i
        s.text(percent(frac), x, 245, 270, 48, color, True)
        s.text(name, x, 308, 270, 23, INK)
    s.text(f"{percent(d.accept_precision)} of alerted cases were recorded dropouts.",
           49, 406, 863, 23, INK, True)

    s = slide("The robustness checks put the gains in context",
              "Shirsha, 1 minute. Compare EF with and without the finance flags. Treat the difference as "
              "sensitivity to feature availability. Compare EF with MDLP under the same 27-feature "
              "protocol. The report includes two- and six-bin checks and corrected paired tests. "
              "The corrected test accounts for overlapping training sets, with Holm adjustment.",
              "Mean outer-test scores  /  Fixed variants and full sensitivity results appear in the report",
              size=31)
    table(s, ["Class-aware configuration", "Macro-F1", "Enrolled recall", "Mean rules"], [
        (label, f"{m.macro_f1:.3f}", percent(m.recall_Enrolled), f"{quality.n_rules:.1f}")
        for group, model, label in study.sensitivity_models
        for m, quality in [(study.metrics.loc[group, model], study.rules.loc[group, model])]
    ], [372, 147, 190, 155], y=133, height=43, size=16)
    comp = study.comparison(FIXED, "macro_f1")
    s.text(f"Class-aware EF vs fixed EF without finance  /  Macro-F1 {signed(comp.mean_diff)}"
           f"  /  adjusted p {study.p_value(comp.corrected_t_p_holm)}",
           50, 453, 862, 17, INK)

    s = slide("What an advisor can take from the model",
              "Shirsha, 1 minute. Summarize the outcome of the research questions, then acknowledge "
              "the limit of one institution and the need to calibrate alerts for the review budget. "
              "End with the role of a human advisor. Invite questions.")
    label(s, "Readable evidence",
          f"The class-aware EF model kept {r.n_rules:.1f} rules\nper fold and recovered "
          f"{percent(p.recall_Enrolled)} of Enrolled.", 49, 138, 420)
    label(s, "A review queue",
          "Matching rules expose why the model\nflags a record or defers a decision.", 498, 138, 413)
    s.box(48, 296, 864, 2, LINE)
    label(s, "What remains for real-world use",
          "Validate on another cohort, confirm feature timestamps, and calibrate\nalert thresholds against advisor capacity and missed-dropout costs.",
          49, 338, 863, 21)

    s = slide("Technical backup",
              "Use this slide only during questions. The slides show cohort-level comparisons and illustrative "
              "cases. Pawlak and Fayyad–Irani are original algorithm sources. In 2024 Zanellati et al. "
              "compared prediction windows. In 2025 Carballo-Mendívil et al. used enrollment-only data. "
              "In 2026 Praptomo et al. used XGBoost and SHAP on the UCI benchmark, including semester-two "
              "features with an 80/20 holdout. The report contains the complete references and links. Rule induction and data "
              "processing are reproducible from the commands in the repository.")
    label(s, "Why can a 40% rule be useful?",
          "40% can be strong evidence for a class\nwith a much lower training prevalence.", 49, 124, 425, 18)
    label(s, "Does finance prove leakage?",
          "The ablation measures sensitivity.\nFeature timestamps would resolve timing.", 507, 124, 409, 18)
    label(s, "Is a vote an individual probability?",
          "It is normalized rule evidence.\nWe did not calibrate predicted probabilities.", 49, 266, 425, 18)
    label(s, "What did we hold out?",
          "Every outer test fold was reserved for\nevaluation after refitting on training data.", 507, 266, 411, 18)
    s.text("References and run settings appear in the final report.", 49, 455, 860, 17, MUTED)
    s = slide("Which changes recovered Enrolled?",
              "Backup slide. For each matched test fold we reused the selected granular representation "
              "and rule induction step. Replacing the relative cutoff with a common 60 percent rule "
              "confidence cutoff cuts Enrolled recall. Replacing normalized LERS with raw votes also "
              "reduces Enrolled recall. These are controlled single-component changes. The altered "
              "variants were not retuned.",
              "50 outer test folds without finance  /  Identical induced rule pools within folds")
    table(s, ["Configuration", "Macro-F1", "Enrolled recall", "Mean rules"], [
        (name, f"{m.macro_f1:.3f}", percent(m.recall_Enrolled), f"{m.rules:.1f}")
        for name, m in study.ablation.iterrows()
    ], [347, 145, 196, 176], y=168, height=52, size=18)
    s.text("Class-relative pruning and voting both contributed under this setup.",
           49, 430, 863, 21, TEAL, True)
    s = slide("What changes when we train on fewer students?",
              "Backup slide for questions about sample size. Within each original outer training "
              "fold, we drew nested stratified subsets and repeated the inner tuning at each size. "
              "The test students stayed identical at every size. This measures sensitivity within "
              "the same dataset. It gives no estimate of transfer to a new institution.",
              "Identical test students at every size  /  Finance excluded")
    table(s, ["Training share", "Mean students", "Macro-F1", "Enrolled recall"], [
        (percent(fraction), f"{row.training_students:,.0f}", f"{row.macro_f1:.3f}",
         percent(row.recall_Enrolled)) for fraction, row in study.learning.iterrows()
    ], [222, 217, 186, 239], y=151, height=50, size=18)
    s.text("Shares are relative to the outer training fold.", 49, 433, 863, 20, MUTED)
    s = slide("A worked example of a rough-set boundary",
              "This is a toy example. Students in each row have the same discretized profile. "
              "Ask which granules qualify as evidence for Dropout. Under Pawlak, every member of "
              "a granule in the lower approximation must be a Dropout. In the middle row, some "
              "students drop out and others graduate despite matching on the selected conditions. "
              "With a minimum granule size of four and a precision threshold of .75, the middle row "
              "qualifies as Dropout evidence. The example has simplified counts for explanation.",
              "Illustrative counts  /  One row per group of students with matching attributes", size=32)
    table(s, ["Matching profile", "Dropout", "Graduate", "Pawlak region"],
          [("A", "4", "0", "Lower approximation"), ("B", "3", "1", "Boundary"),
           ("C", "0", "4", "Outside the upper approximation")],
          [180, 128, 137, 419], y=148, height=54)
    s.text("Allowing 75% precision makes profile B qualify as Dropout evidence.",
           49, 419, 862, 21, TEAL, True)

    s = slide("Dataset source and feature selection",
              "The dataset was released by Realinho et al. through UCI. Its source paper describes "
              "17 undergraduate programs at one Portuguese institution and entrants from 2008/09 "
              "through 2018/19. The public CSV has no explicit entry-cohort column. Point out "
              "that the model predicts after semester one and the recorded outcome reflects the "
              "end of the normal program duration.",
              "UCI Machine Learning Repository  /  Predict Students’ Dropout and Academic Success",
              size=33)
    label(s, "Where the records came from",
          "Polytechnic Institute of Portalegre, Portugal\n17 undergraduate programs\nEntrants from 2008/09 to 2018/19",
          49, 148, 490, 19)
    label(s, "What we used",
          "36 predictors in the public CSV\n30 after removing semester-two fields\n27 in the primary analysis without finance",
          548, 148, 364, 17)
    s.box(48, 306, 864, 1, LINE)
    s.text("Prediction cutoff", 49, 333, 405, 22, INK, True)
    s.text("End of semester one", 49, 370, 405, 19, MUTED)
    s.text("Outcome recorded", 548, 333, 365, 22, INK, True)
    s.text("End of the normal program duration", 548, 370, 365, 17, MUTED)
    s.text("Dataset DOI  10.24432/C5MC89     Data paper DOI  10.3390/data7110146",
           49, 451, 863, 16, TEAL)

    s = slide("References",
              "Keep this slide visible while explaining the two kinds of citations. The foundational "
              "papers describe methods used in our model. The recent papers address prediction "
              "timing and explainability. Praptomo et al. used the same public data, with second-semester "
              "features and an 80/20 holdout. The full bibliography appears in the final report.",
              "Dataset documentation, original methods, and recent studies")
    for y, title, lines in [
        (128, "Dataset",
         ("Realinho et al. (2021), UCI dataset 697  /  10.24432/C5MC89",
          "Realinho et al. (2022), Predicting Student Dropout and Academic Success  /  10.3390/data7110146")),
        (237, "Original methods",
         ("Pawlak (1982), Rough Sets  /  10.1007/BF01001956",
          "Fayyad and Irani (1993), Multi-Interval Discretization  /  IJCAI Proceedings")),
        (344, "Recent studies",
         ("Zanellati et al. (2024), Performance and Explainability  /  10.1109/TLT.2024.3425959",
          "Carballo-Mendívil et al. (2025), Pre-Enrollment Prediction  /  10.3390/app15169202",
          "Praptomo et al. (2026), XGBoost and SHAP on UCI Data  /  10.33650/jeecom.v8i1.16978")),
    ]:
        s.text(title, 49, y, 862, 21, INK, True)
        s.text("\n".join(lines), 49, y + 34, 862, 16, MUTED)

    # Give the longer session time for the worked example and the completed robustness checks.
    order = (1, 2, 18, 3, 17, 4, 5, 6, 7, 8, 12, 15, 16, 9, 10, 11, 13, 19, 14)
    ordered = [slides[index - 1] for index in order]
    names = ["Md Pares Mahmud"] * 7 + ["Abu Hanif"] * 6 + ["Shirsha Mitra"] * 5
    minutes = [1, 2, 1, 2, 3, 3, 2, 3, 2, 2, 2, 2, 2, 3, 3, 2, 1, 1]
    prompts = [
        "Open with a student finishing semester one. What evidence could an advisor inspect before deciding to reach out?",
        "Explain the three labels and class imbalance. Clarify why Enrolled is a separate outcome.",
        "Show the UCI source and trace the feature count from 36 to 30 to 27.",
        "Trace one example feature through discretization, reduct selection, rule induction, and voting.",
        "Ask the audience where profile B belongs under exact rough sets. Work out 3/4 and compare both decisions.",
        "Compute the two precision thresholds aloud. Explain why a class-relative threshold changes which evidence can survive.",
        "Draw one outer split. Show exactly where inner tuning takes place, then hand over to Hanif.",
        "Compare fixed EF with class-aware EF, then with random forest. Distinguish macro-F1 from overall accuracy.",
        "Read the Enrolled row across the table. Compare the two ways this group is misclassified.",
        "Explain the gap between mean and median rule count. Give the 7–206 range to make variation concrete.",
        "Hold model family fixed for the finance comparison. Then compare the bin counts and explain the paired test.",
        "Explain why the ablation starts from the same induced rule pool. Compare the common threshold and raw voting.",
        "Compare the smallest and largest training samples and explain why the test rows stay fixed. Hand over to Shirsha.",
        "Read the alert rule, give its training support, and explain the difference between rule confidence and the vote. Then walk through the conflicting matches in the deferred case.",
        "Point to both models at 75% coverage. Explain the separate diamond, then show why ties matter for a rule score.",
        "Take the denominator of recorded dropouts first. Then explain why alert precision has a different denominator.",
        "Review the evidence the advisor can inspect and the validation needed for use.",
        "Point out the original method papers and one recent study. Allow three minutes for questions.",
    ]
    elapsed = 0
    for i, entry in enumerate(ordered, 1):
        if i > 1:
            for j, obj in enumerate(entry.objects):
                kind, x, y, w, h, value = obj
                if kind == "text" and (x, y) == (890, 511):
                    _, size, color, bold = value
                    entry.objects[j] = (kind, x, y, w, h, ([str(i)], size, color, bold))
        if i > len(minutes):
            entry.notes = "Discussion backup. Use during the final three minutes if needed.\n\n" + entry.notes
            continue
        length = minutes[i - 1]
        content = re.sub(r"^(Pares|Hanif|Shirsha), [^.]+\. ", "", entry.notes)
        content = content.replace(" Hand over to Hanif for the protocol and results.", "")
        content = content.replace(" Hand off to Shirsha for the advising example.", "")
        entry.notes = (f"Presenter {names[i - 1]}. Minutes {elapsed}–{elapsed + length}.\n\n"
                       f"{prompts[i - 1]}\n\n{content}")
        elapsed += length
    assert elapsed == 37
    return ordered


if __name__ == "__main__":
    slides = build(Study(), explain_cases("data/data.csv"))
    write_pdf(slides, Path("final/final_slides.pdf"))
    pptx = Path("final/final_slides.pptx")
    scaffold = pptx if pptx.exists() else Path("milestone/milestone_slides.pptx")
    write_pptx(slides, pptx, scaffold)
