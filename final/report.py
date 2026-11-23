"""Build the final research report directly from the completed experiment."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from final.study import Study, MODELS, PRIMARY, FIXED, REFERENCES, percent, signed
from rsproject.case_study import explain_cases


BLACK = colors.black
WIDTH = A4[0] - 92
STYLES = {
    "category": ParagraphStyle("Category", fontName="Times-Bold", fontSize=11,
                               textColor=BLACK, leading=14, spaceAfter=12),
    "title": ParagraphStyle("Title", fontName="Times-Bold", fontSize=27,
                            textColor=BLACK, leading=30, spaceAfter=16),
    "h1": ParagraphStyle("Heading1", fontName="Times-Bold", fontSize=17,
                         textColor=BLACK, leading=20, spaceBefore=12, spaceAfter=7,
                         keepWithNext=True),
    "h2": ParagraphStyle("Heading2", fontName="Times-Bold", fontSize=13,
                         textColor=BLACK, leading=16, spaceBefore=9, spaceAfter=5,
                         keepWithNext=True),
    "body": ParagraphStyle("Body", fontName="Times-Roman", fontSize=11.5,
                           textColor=BLACK, leading=15, spaceAfter=8, alignment=TA_LEFT),
    "small": ParagraphStyle("Small", fontName="Times-Roman", fontSize=10,
                            textColor=BLACK, leading=13, spaceAfter=7),
    "cell": ParagraphStyle("Cell", fontName="Times-Roman", fontSize=10,
                           textColor=BLACK, leading=12),
    "th": ParagraphStyle("Column", fontName="Times-Bold", fontSize=10,
                         textColor=BLACK, leading=12),
}


def paragraph(text, role="body"):
    return Paragraph(text, STYLES[role])


def table(headers, rows, widths):
    content = [[paragraph(escape(str(value)), "th") for value in headers]]
    content.extend([paragraph(escape(str(value)), "cell") for value in line] for line in rows)
    result = Table(content, colWidths=[WIDTH * f for f in widths], repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.7, BLACK),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BLACK),
        ("LINEBELOW", (0, -1), (-1, -1), 0.7, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return result


def footer(canvas, doc):
    canvas.setTitle("Rough-set decision rules for early student dropout prediction")
    canvas.setAuthor("Md Pares Mahmud, Abu Hanif, and Shirsha Mitra")
    canvas.setFillColor(BLACK)
    canvas.setFont("Times-Roman", 10)
    canvas.drawCentredString(A4[0] / 2, 26, str(doc.page))


def monochrome_coverage(study, certain):
    figure = Figure(figsize=(7.2, 3.7), facecolor="white")
    FigureCanvasAgg(figure)
    axis = figure.add_subplot()
    for model, name, style in (
        (PRIMARY, "Class-aware EF", "-"),
        ("RandomForest", "Random forest", "--"),
        ("DecisionTree", "Decision tree", ":"),
    ):
        points = study.curves.loc[study.curves.model.eq(model)]
        axis.plot(points.coverage, points.accuracy, color="black", linestyle=style,
                  linewidth=1.4, label=name)
    axis.scatter(certain.coverage, certain.accuracy, color="black", marker="D",
                 s=22, label="Certain-rule decision", zorder=5)
    axis.set(xlabel="Share of students given a decision",
             ylabel="Accuracy among decided students")
    axis.legend(loc="lower left", frameon=False, fontsize=8)
    figure.tight_layout()
    buffer = BytesIO()
    figure.savefig(buffer, format="png", dpi=180)
    buffer.seek(0)
    return Image(buffer, width=432, height=222, hAlign="CENTER")


def build(study, cases, destination):
    p = study.metrics.loc["no_finance", PRIMARY]
    old = study.metrics.loc["no_finance", FIXED]
    forest = study.metrics.loc["no_finance", "RandomForest"]
    rules = study.rules.loc["no_finance", PRIMARY]
    oldrules = study.rules.loc["no_finance", FIXED]
    classic = study.rules.loc["no_finance", "RS-EF-classic"]
    stories = []

    def add(text, role="body"):
        stories.append(paragraph(text, role))

    def heading(number, title):
        add(f"{number}. {title}", "h1")

    def grid(headers, rows, widths):
        stories.extend([table(headers, rows, widths), Spacer(1, 8)])

    add("Information Granular Computing | Final Project Report", "category")
    add("Rough-Set Decision Rules for Early Student Dropout Prediction", "title")
    add("Md Pares Mahmud<br/>Abu Hanif<br/>"
        "Shirsha Mitra<br/>Sichuan University")
    stories.append(Spacer(1, 20))
    add("Abstract", "h2")
    add("Early-warning models should recognize several student outcomes and give an advisor "
        "evidence for each decision. We predicted Dropout, Enrolled, and Graduate at the end of "
        "the first semester using 4,424 records. Our class-aware rough-set model uses the prevalence "
        "of each outcome to set the precision required of its information granules and rules. "
        f"In five repeats of stratified ten-fold cross-validation without the finance fields, "
        f"the Equal-Frequency model recovered {percent(p.recall_Enrolled)} of Enrolled students "
        f"({percent(old.recall_Enrolled)} with fixed pruning), with macro-F1 "
        f"of {p.macro_f1:.3f} versus {old.macro_f1:.3f}. It averaged {rules.n_rules:.1f} rules, "
        f"compared with {oldrules.n_rules:.1f} for fixed pruning and {classic.n_rules:,.0f} "
        "for classical Pawlak rough sets. "
        f"Random forest achieved {forest.macro_f1:.3f} macro-F1. A held-out case walkthrough "
        "illustrates how rule evidence can trigger outreach or defer a decision.")
    add("Research questions", "h2")
    add("<b>RQ1.</b> Can rough-set rules recover Enrolled students while remaining inspectable?")
    add("<b>RQ2.</b> How do discretization and finance-field availability change the trade-off "
        "between predictive performance and rule complexity?")
    add("<b>RQ3.</b> At matched coverage, how accurately do rough sets and standard classifiers "
        "decide the cases they retain?")
    add("Primary analysis uses the 27-feature configuration that excludes debtor status, "
        "tuition status, and scholarship status. The 30-feature version quantifies sensitivity "
        "to the availability of those fields.", "small")
    add("Related work", "h2")
    add("Recent studies compare prediction windows and explainability [9] or work with enrollment-only "
        "features [10]. A 2026 XGBoost and SHAP study uses the same public benchmark, includes "
        "semester-two features, and evaluates on an 80/20 holdout [11]. Its results describe "
        "a different prediction and evaluation setup. Our comparisons use a semester-one cutoff "
        "and the same outer test folds for every tested model.")

    stories.append(PageBreak())
    heading(1, "Dataset and Evaluation")
    add("The UCI dataset represents one Portuguese higher-education institution. The source "
        "describes 17 undergraduate programs and entrants from 2008/09 to 2018/19. The UCI "
        "CSV has no explicit entry-cohort field for a later-cohort test. It records a "
        "student's status at the end of the normal course duration [1, 2]. Enrolled is a distinct "
        "recorded status. Longer follow-up could change that status.")
    grid(["Outcome", "Records", "Share"], [
        (label, f"{n:,}", percent(n / study.config["n"]))
        for label, n in study.config["class_counts"].items()
    ], [.52, .24, .24])
    add("The source file has 36 predictors and one outcome column. We verified that it contains "
        "no missing cells or exact duplicate rows. We removed the six second-semester predictors. "
        "The three finance fields have no independently verified semester-one timestamps in the "
        "supplied files, so we evaluated all methods with and without them.")
    add("Fold-local training", "h2")
    add("Five repeats of stratified ten-fold cross-validation create 50 shared outer splits. "
        "For each rough-set variant, a stratified 75/25 split of the outer training portion selects "
        "hyperparameters. It fits the discretizer and rare-category grouping on the inner training "
        "portion. After selection, we refit on the entire outer training portion and evaluate on "
        "the untouched outer test portion. An unseen categorical value falls into an Other or "
        "reserved unknown bucket using training-fitted mappings.")
    grid(["Measures", "How to read them"], [
        ("Macro-F1 and balanced accuracy", "Give each of the three outcomes equal weight."),
        ("Per-class recall", "Fraction of a recorded outcome recovered by the model."),
        ("Accuracy and MCC", "Overall correctness and multiclass association."),
        ("Rule count, mean length, coverage", "Size and inspectability of the rule set."),
        ("Selective accuracy", "Accuracy on the cases that receive a decision."),
    ], [.37, .63])
    add("Decision tree and random forest use original numeric values and integer-coded categorical "
        "fields. Categorical Naive Bayes uses Equal-Frequency codes with the encoder fitted "
        "on training data. Baselines and rough sets receive the same feature sets and outer splits.", "small")

    heading(2, "Rough-Set Methods")
    add("The proposal specified the R RoughSets package. The final implementation uses Python "
        "so both discretizers and all rough-set variants share the same fold-local interface.")
    add("Equal-Frequency (EF) uses empirical quantile bins (four by default). MDLP [3] searches "
        "for entropy-reducing split points and stops using a minimum-description-length criterion. "
        "Categories below 2% of training frequency are grouped. Identical discretized values "
        "on a feature subset define an information granule.")
    add("From granules to interpretable rules", "h2")
    add("<b>Classical Pawlak.</b> A granule contributes to dependency only when all members "
        "share a class. Its lower approximation has pure granules and its upper approximation "
        "contains granules with any members of that class [4].")
    add("<b>Fixed-pruning reference.</b> QuickReduct [5] uses a minimum granule size and a common "
        "precision threshold. LEM2 [6] induces rules for lower and upper approximations. A rule "
        "survives when it matches at least five training cases of its predicted class and reaches "
        "60% training confidence.")
    add("<b>Class-aware extension.</b> For class <i>c</i> with training prior <i>p</i><sub>c</sub>, "
        "a granule of sufficient size enters its lower approximation when its class share is "
        "at least <i>p</i><sub>c</sub> + <i>b</i>(1 − <i>p</i><sub>c</sub>). A higher prior "
        "therefore requires higher absolute precision for the same margin <i>b</i>. "
        "The dependency averages across classes the fraction of their training members "
        "covered by qualifying granules. Greedy QuickReduct searches for a small feature set "
        "under that criterion. Lower approximations can overlap when a granule exceeds the "
        "threshold for more than one class.")
    add("The class-aware pruning threshold uses the same formula with a separately tuned margin "
        "<i>q</i>. Inner validation tries granule sizes 5 and 15, margins <i>b</i> of .12, .25 and .40, "
        "minimum correct counts of 3 and 8, and margins <i>q</i> of .04, .12 and .22. "
        "Balanced accuracy selects a configuration. Ties use macro-F1 and fewer rules.")
    add("LERS voting and uncertainty", "h2")
    add("LERS adds each fully matched rule's voting weight. With no full match, partial "
        "matches receive weight in proportion to their matched conditions. Class-aware "
        "weights multiply the number of correctly matched training cases by rule length "
        "and divide by the training class count. Votes are normalized across classes. "
        "The highest vote gives the forced prediction. Certain-rule abstention assigns a class "
        "when fully matched lower-approximation rules agree on one class and defers otherwise.")
    add("Rule support counts all matching training cases. Rule strength counts matching cases "
        "of the predicted class. Confidence is strength divided by support. "
        "If pruning empties the rule set, the strongest available rule provides a fallback. "
        "Normalized votes have no probability calibration.", "small")

    heading(3, "Predictive Results")
    add("The main comparison uses the 27 predictors. All rows are means over the same "
        "50 test folds. Standard deviations, per-fold results, and all model variants are "
        "available in the experiment outputs.")
    grid(["Model", "Accuracy", "Macro-F1", "Bal. acc.", "MCC", "Enrolled recall"], [
        (label, f"{m.accuracy:.3f}", f"{m.macro_f1:.3f}", f"{m.balanced_accuracy:.3f}",
         f"{m.mcc:.3f}", percent(m.recall_Enrolled))
        for model, label in MODELS for m in [study.metrics.loc["no_finance", model]]
    ], [.31, .12, .13, .13, .11, .20])
    add("Where the mistakes go", "h2")
    confusion = study.confusion.loc["no_finance", PRIMARY]["share"].unstack()
    grid(["Actual class", "Predict Dropout", "Predict Enrolled", "Predict Graduate"], [
        (label, *[percent(confusion.loc[label, col]) for col in study.classes])
        for label in study.classes
    ], [.31, .23, .23, .23])
    add("Each row shows the average distribution of predictions for the actual class. "
        f"Relative to fixed pruning, class-aware EF changed Enrolled recall by "
        f"{signed(p.recall_Enrolled - old.recall_Enrolled, 100, 1)} percentage points and Dropout "
        f"recall by {signed(p.recall_Dropout - old.recall_Dropout, 100, 1)} points. "
        "The confusion table shows why Enrolled remains the hardest class to assign reliably.")
    recall = study.primary_folds.recall_Enrolled
    by_repeat = study.primary_folds.groupby("repeat").recall_Enrolled.mean()
    add(f"Enrolled recall was {percent(recall.mean())} on average with a standard deviation "
        f"of {recall.std() * 100:.1f} percentage points across folds. The five repeat means "
        f"ranged from {percent(by_repeat.min())} to {percent(by_repeat.max())}. "
        "These values describe split-to-split variability.")

    heading(4, "Rule Quality and Reduct Stability")
    grid(["Model", "Rules", "Mean length", "Full match", "Reduct size", "Enrolled rules"], [
        (label, f"{r.n_rules:,.1f}", f"{r.mean_rule_length:.2f}", percent(r.coverage),
         f"{r.reduct_size:.1f}", f"{r.rules_Enrolled:.1f}")
        for model, label in MODELS if model.startswith("RS-")
        for r in [study.rules.loc["no_finance", model]]
    ], [.28, .13, .14, .15, .14, .16])
    add("Interpretation-only rules", "h2")
    rule_counts = study.primary_folds.n_rules
    add(f"The class-aware EF rule count ranged from {rule_counts.min():.0f} to "
        f"{rule_counts.max():.0f} across folds, with a median of {rule_counts.median():.0f}. "
        f"The examples below come from the {len(study.final_rules)}-rule full-data EF fit "
        "excluding finance. "
        "Their support and confidence summarize that fit. The evaluation table comes from "
        "independent outer test predictions.")
    grid(["Example rule", "Matches", "Confidence"], [
        (row.rule, f"{int(row.support):,}", percent(row.confidence)) for row in study.examples
    ], [.74, .11, .15])
    add("Reduct stability", "h2")
    selected = study.feature_frequency()
    add("The most frequently selected fields in the 50 outer training folds were "
        + ", ".join(f"{escape(name)} ({percent(freq)})" for name, freq in selected[:5])
        + ". Frequencies describe the feature-selection procedure. "
        "Changes in cut points and neighboring granules can lead to different rules across folds.")
    add("The matched comparison changes dependency, pruning, and voting together. "
        "Section 7 examines pruning and voting separately.", "small")

    heading(5, "Three-Way Decisions")
    cert = study.certain.loc[PRIMARY]
    at75 = study.curves.loc[study.curves.coverage.eq(.75)].set_index("model").accuracy
    add(f"Without finance, fully matched certain rules gave a unique class to "
        f"{percent(cert.coverage)} of cases at {percent(cert.accuracy)} accuracy on those cases. "
        f"By ranking confidence at matched 75% coverage, class-aware EF attained "
        f"{percent(at75[PRIMARY])} selective accuracy and random forest attained "
        f"{percent(at75['RandomForest'])}. Scores tied at a coverage cutoff receive "
        "uniform expected selection so the row order cannot change the result.")
    stories.append(monochrome_coverage(study, cert))
    add("Figure 1. Rank-based selective accuracy. The diamond represents the separate "
        "certain-rule policy. Points use the same outer folds.", "small")
    add("Dropout alerting with a review queue [7]", "h2")
    d = study.regions.loc[PRIMARY]
    add(f"With illustrative score cutoffs of .60 for an alert and .30 for no alert, "
        f"the class-aware EF model flagged {percent(d.accept_share)} of students and deferred "
        f"{percent(d.defer_share)}. Of recorded dropouts, {percent(d.dropouts_flagged)} "
        f"were flagged, {percent(d.dropouts_deferred)} deferred, and "
        f"{percent(d.dropouts_missed)} received no alert. The share of flagged students "
        f"who dropped out was {percent(d.accept_precision)}. These thresholds represent an "
        "illustrative policy with a measurable false-negative burden.")

    heading(6, "Robustness Checks")
    grid(["Setting", "Macro-F1", "Bal. acc.", "Enrolled recall", "Rules"], [
        (label, f"{m.macro_f1:.3f}", f"{m.balanced_accuracy:.3f}",
         percent(m.recall_Enrolled), f"{r.n_rules:.1f}")
        for group, model, label in study.sensitivity_models
        for m, r in [(study.metrics.loc[group, model], study.rules.loc[group, model])]
    ], [.39, .15, .15, .17, .14])
    add("EF varies its bin count while reselecting other settings inside the training fold. "
        "The finance comparison measures sensitivity to feature availability. Its performance "
        "difference alone cannot establish data leakage or a causal role for finance.")
    add("Paired comparisons", "h2")
    grid(["Comparison (27 predictors)", "Metric", "Mean difference", "Adjusted p"], [
        (name, metric, signed(row.mean_diff), study.p_value(row.corrected_t_p_holm))
        for name, baseline in [("Class-aware EF vs fixed EF", FIXED),
                               ("Class-aware EF vs random forest", "RandomForest")]
        for metric, key in [("Macro-F1", "macro_f1"), ("Balanced accuracy", "balanced_accuracy")]
        for row in [study.comparison(baseline, key)]
    ], [.42, .24, .17, .17])
    add("Differences use identical train/test splits. Adjusted p-values are from a "
        "Nadeau–Bengio corrected resampled t-test with Holm adjustment within each "
        "feature-set and metric family [8]. Fold overlap makes the accompanying Wilcoxon "
        "results a descriptive sensitivity check. Internal cross-validation assesses models "
        "within this dataset. It cannot verify performance in a different year or institution.")
    add("Tables in results/full also report the fixed-pruning sensitivity grid, including "
        "support and confidence trade-offs. Exploratory outer-test sweeps were not used "
        "to choose the reported fold models.", "small")

    heading(7, "Component Analysis and Test Cases")
    add("An ablation uses the same 50 finance-excluded splits and the same inner-selected EF "
        "granules and unpruned candidate rules. Within each outer fit, we replace one component "
        "at a time while leaving the induced rule pool fixed.")
    grid(["Configuration", "Macro-F1", "Enrolled recall", "Rules"], [
        (name, f"{row.macro_f1:.3f}", percent(row.recall_Enrolled), f"{row.rules:.1f}")
        for name, row in study.ablation.iterrows()
    ], [.45, .18, .19, .18])
    standard = study.ablation.loc["Common .60 rule cutoff"]
    unweighted = study.ablation.loc["Without normalized voting"]
    add(f"The common cutoff left {percent(standard.recall_Enrolled)} Enrolled recall. "
        f"Keeping relative pruning and removing class-normalized votes gave "
        f"{percent(unweighted.recall_Enrolled)}. The results show that both mechanisms matter "
        "under the selected configurations. These single-component changes were not retuned.")
    add("Held-out examples", "h2")
    add("These examples use the first outer test fold. Within each Dropout score region, "
        "we show a fully matched case near the median score when available.")
    grid(["Policy decision", "Dropout score", "Forced label", "Recorded outcome"], [
        (case["decision"].capitalize(), f"{case['dropout_score']:.2f}",
         case["prediction"], case["outcome"]) for case in cases
    ], [.29, .19, .25, .27])
    alert = next(case for case in cases if case["decision"] == "accept")
    rule = alert["rules"][0]
    add("For the alerted case, the strongest vote came from <b>IF "
        + escape(" AND ".join(rule["conditions"])) + " THEN " + escape(rule["target"])
        + f"</b>. Its training support was {rule['support']:,} cases and its confidence "
        f"was {percent(rule['confidence'])}. The vote can reach 1 when one class receives every vote. "
        "In the deferred example, several fully matched rules supported different classes.")

    heading(8, "Training Sample Size")
    add("We repeated the class-aware EF experiment at four training sizes. Within each outer "
        "training fold we drew nested stratified subsets and reran inner tuning, discretization, "
        "rule induction, and pruning at each size. All four models then faced the same outer test "
        "students. Finance fields were excluded throughout.")
    grid(["Training share", "Mean students", "Macro-F1", "Enrolled recall", "Mean rules"], [
        (percent(fraction), f"{row.training_students:,.0f}",
         f"{row.macro_f1:.3f} ± {row.macro_f1_sd:.3f}",
         f"{percent(row.recall_Enrolled)} ± {row.recall_Enrolled_sd * 100:.1f} pp",
         f"{row.rules:.1f}") for fraction, row in study.learning.iterrows()
    ], [.20, .20, .21, .25, .14])
    first, last = study.learning.iloc[0], study.learning.iloc[-1]
    add(f"From the smallest to the full training size, mean macro-F1 changed by "
        f"{signed(last.macro_f1 - first.macro_f1)} and mean Enrolled recall changed by "
        f"{signed(last.recall_Enrolled - first.recall_Enrolled, 100, 1)} percentage points. "
        "Mean macro-F1 was essentially the same at the two largest training sizes. "
        "Each mean summarizes 50 outer folds. The ± values are standard deviations across "
        "folds and describe variability.")
    add("This experiment measures how sample size affects the model within the observed dataset. "
        "Validation on new cohorts or institutions requires records from those populations. "
        "The archived per-fold results retain the split and training size for each comparison.")

    heading(9, "Conclusion")
    add(f"Class-aware rough sets recovered {percent(p.recall_Enrolled)} of Enrolled students "
        f"under the finance-excluded protocol, while keeping voting evidence in IF–THEN "
        "form. The rule set is larger than fixed pruning and much smaller than the classical "
        "Pawlak set. The baseline comparison and selective accuracy curves quantify the cost "
        "of preferring readable rule evidence.")
    add("For advising, a flagged or deferred case would start a review. The source institution's "
        "outcome definition, student support practices, and reliance on variables such as program "
        "and economic conditions limit transfer. The tree baselines' integer-coded categories also "
        "permit splits based on arbitrary code order. A deployment study would need a time-based or "
        "external holdout, verified timestamps, subgroup error checks, and threshold calibration "
        "against review capacity and the cost of missed dropouts.")
    heading(10, "Team Roles")
    add("The milestone report recorded the work completed at that stage and assigned the following "
        "responsibilities for the final phase.")
    grid(["Team member", "Milestone contribution", "Final-phase responsibility"], [
        ("Md Pares Mahmud", "Implemented the pipeline, ran experiments, and checked the results.",
         "Improve Enrolled recall and oversee the repeated 5 × 10 evaluation."),
        ("Abu Hanif", "Wrote the milestone report.",
         "Handle the significance tests and sensitivity analysis."),
        ("Shirsha Mitra", "Prepared figures and presentation slides.",
         "Explain the dropout alert, defer, and no-alert decisions and prepare the final slides."),
    ], [.22, .37, .41])
    add("Reproduce the results", "h2")
    add("From <font name='Courier'>gc_project</font>, install <font name='Courier'>requirements.txt</font> "
        "and run <font name='Courier'>python run_all.py data/data.csv</font>. The run records its "
        "seed, data fingerprint, fold metrics, rules and threshold tables. "
        "<font name='Courier'>python -m rsproject.case_study</font> recreates the held-out examples. "
        "<font name='Courier'>python -m rsproject.learning_curve</font> reruns the sample-size analysis.")
    add("References", "h2")
    for number, (label, url) in enumerate(REFERENCES, 1):
        add(f'[{number}] <link href="{escape(url)}" color="#000000">{escape(label)}</link>', "small")
    destination.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(destination), pagesize=A4, leftMargin=46, rightMargin=46,
                            topMargin=45, bottomMargin=52)
    doc.build(stories, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build(Study(), explain_cases("data/data.csv"), Path("final/final_report.pdf"))
