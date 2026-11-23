"""Build milestone/milestone_report.docx (run from gc_project/)."""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FIG = "results/quick/figures"
os.makedirs("milestone", exist_ok=True)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)      # A4
for side in ("left_margin", "right_margin"):
    setattr(sec, side, Inches(0.7))
sec.top_margin = sec.bottom_margin = Inches(0.6)

st = doc.styles["Normal"]
st.font.name = "Calibri"; st.font.size = Pt(9.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.paragraph_format.space_after = Pt(2)
st.paragraph_format.line_spacing = 1.0
for name in ("List Bullet",):
    doc.styles[name].font.size = Pt(9.5)
    doc.styles[name].paragraph_format.space_after = Pt(1)


def para(text="", bold=False, size=None, align=None, after=None, italic=False):
    p = doc.add_paragraph()
    if text:
        add_runs(p, text, bold, italic, size)
    if align: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    return p


def add_runs(p, text, bold=False, italic=False, size=None):
    """**bold** segments inside text."""
    parts = text.split("**")
    for i, s in enumerate(parts):
        if not s: continue
        r = p.add_run(s)
        r.bold = bold or (i % 2 == 1); r.italic = italic
        if size: r.font.size = Pt(size)


def heading(text):
    p = para(text, bold=True, size=11, after=1)
    p.paragraph_format.space_before = Pt(5)
    p.runs[0].font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    add_runs(p, text)
    return p


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd"); s.set(qn("w:val"), "clear")
    s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), hexcolor); tcPr.append(s)


def table(rows, widths, size=8.5, header_fill="DCE6F0", bold_rows=()):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.width = Inches(widths[j])
            p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            r = p.add_run(str(val)); r.font.size = Pt(size)
            r.bold = (i == 0) or (i in bold_rows)
            if j > 0: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if i == 0: shade(c, header_fill)
    return t


def caption(text):
    p = para(text, italic=True, size=8, after=3)
    return p


# ---------------------------------------------------------------- title
para("Rough-Set Decision Rules for Early Prediction of Student Dropout",
     bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
para("Information Granular Computing · Milestone Report", size=10,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
para("Md Pares Mahmud, Abu Hanif, Shirsha Mitra", size=10,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=4)

# ---------------------------------------------------------------- 1
heading("1. Progress so far")
bullet("**Full pipeline implemented in Python**: discretization (Equal-Frequency k = 4 and "
       "entropy-based MDLP, Fayyad & Irani 1993), rare-category grouping (< 2 %), QuickReduct, "
       "LEM2 certain and possible rules, support/confidence pruning, LERS classification and "
       "three-way decisions. Six unit tests check the core against a hand-computed 5-object "
       "decision table; all pass.")
bullet("**Data and early-warning filter**: UCI “Predict Students' Dropout and Academic Success” "
       "(Realinho et al.), 4,424 students: 2,209 Graduate, 1,421 Dropout, 794 Enrolled. All "
       "2nd-semester columns are removed, which leaves **30 condition attributes** (27 without "
       "the finance attributes).")
bullet("**First results**: one repeat of stratified 10-fold CV. All discretization, reducts and "
       "rules are fit inside each training fold. The granulation parameters (minimum granule "
       "size s, precision β) are tuned on a 25 % inner holdout. Baselines: Decision Tree, "
       "Random Forest, Naive Bayes.")

# ---------------------------------------------------------------- 2
heading("2. Preliminary results")
rows = [["Model", "Accuracy", "Balanced acc.", "Macro-F1", "MCC", "Recall Enrolled",
         "Macro-F1 no finance"],
        ["RS-EF-classic*", ".635 ± .020", ".525 ± .020", ".524 ± .022", ".379 ± .036", ".164", "–"],
        ["RS-EF-pruned", ".669 ± .012", ".523 ± .008", ".480 ± .008", ".448 ± .019", ".000", ".468"],
        ["RS-MDLP-pruned", ".660 ± .017", ".514 ± .018", ".472 ± .014", ".431 ± .032", ".000", ".450"],
        ["Decision Tree", ".667 ± .027", ".602 ± .028", ".601 ± .028", ".459 ± .043", ".343", ".569"],
        ["Random Forest", ".743 ± .024", ".639 ± .031", ".644 ± .035", ".572 ± .043", ".252", ".613"],
        ["Naive Bayes", ".691 ± .016", ".599 ± .019", ".598 ± .020", ".485 ± .028", ".234", ".567"]]
table(rows, [1.25, 0.9, 0.95, 0.9, 0.9, 0.9, 1.0])
caption("Table 1. Test-fold performance, mean ± SD over 1×10 CV, all 30 attributes; last column without "
        "Debtor / Tuition / Scholarship. *The quick run skips the classic model; we ran it "
        "separately on the same 10 folds.")

rows = [["Model", "Rules before pruning", "Rules after", "Mean length", "Mean support",
         "Test coverage (full match)", "Reduct size"],
        ["RS-EF-classic", "1337.4", "– (no pruning)", "4.50", "4.3", ".780", "13.2"],
        ["RS-EF-pruned", "17.9", "8.2", "1.92", "435.5", ".774", "2.8"],
        ["RS-MDLP-pruned", "20.2", "8.2", "1.64", "443.4", ".759", "2.3"]]
table(rows, [1.25, 1.05, 0.95, 0.8, 0.85, 1.25, 0.8])
caption("Table 2. Rule quality (fold means). Pruning keeps rules with support ≥ 5 and confidence ≥ 0.6; "
        "unmatched students are classified by LERS partial matching.")

# figures side by side
t = doc.add_table(rows=1, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER
for cell, f in zip(t.rows[0].cells, ("models_macro_f1.png", "coverage_accuracy.png")):
    p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(os.path.join(FIG, f), width=Inches(3.35))
caption("Figure 1 (left). Macro-F1 by model. Figure 2 (right). Accuracy on the students who get a "
        "decision when the least confident ones are deferred. The diamond marks the rough-set "
        "three-way decision (accept only when certain rules of a single class match).")

para("**Three-way decision.** The certain-rule decision gives a class to 75.6 % of students with "
     "76.9 % accuracy, against 66.9 % when the pruned model must decide for everyone. At 75 % "
     "coverage, though, Random Forest reaches 83.6 %. Also, the rough-set curve stays flat "
     "(≈ 0.74–0.77) as more students are deferred, so the LERS vote is not yet a useful "
     "confidence score.", after=2)
para("**Example rules** (MDLP, fit on all data for interpretation only; grades on the 0–20 scale; "
     "support = matching students):", after=1)
for r in ("IF Tuition fees up to date = yes AND 1st-sem grade average ≥ 13.29 THEN Graduate "
          "(support 1,156, confidence 0.80)",
          "IF 1st-sem grade average < 9.9 THEN Dropout (support 719, confidence 0.79)",
          "IF Tuition fees up to date = no THEN Dropout (support 528, confidence 0.87)",
          "IF Tuition fees up to date = no AND 10.54 ≤ 1st-sem grade average < 12.26 THEN Dropout "
          "(support 160, confidence 0.89)"):
    bullet(r)

# ---------------------------------------------------------------- 3
heading("3. Findings and issues so far")
bullet("**Classical reducts overfit.** The exact Pawlak reduct keeps 13.2 attributes on average (in fold 1: "
       "course, application mode, mother's qualification and both parents' occupations, among others). That gives 1,337 rules "
       "with a mean support of only 4 students, and an empty boundary region on the training data. "
       "The granule-size-aware dependency (s, β tuned per fold; usually s = 10, β = 0.6) cuts this "
       "to 2–3 attributes and about 8 rules, and raises accuracy (.635 → .669) and MCC "
       "(.379 → .448). Macro-F1, however, is **lower** (.524 → .480), because the compact models "
       "never predict Enrolled (next point).")
bullet("**\"Enrolled\" is not predicted at all by the pruned rough-set models** (recall 0.000 in every "
       "fold). Granules with an Enrolled majority are rare and tiny (at most 6 students, in 3 of the 20 "
       "fold models), and the other Enrolled rules with at least 5 students reach at most about 0.40 confidence. "
       "So the support ≥ 5 / confidence ≥ 0.6 filter removes every Enrolled rule in 19 of the 20 fold models; the one "
       "surviving rule (6 students) is outvoted by much stronger Graduate and Dropout rules. Class-normalized "
       "voting (-bal) therefore cannot help. This is the main reason the rough-set models are about 0.12–0.17 "
       "macro-F1 below the baselines. On **macro-F1** and balanced accuracy (the two metrics tested) every "
       "pruned-RS vs. baseline difference is significant: the Wilcoxon p = 0.002 is the smallest possible with "
       "10 folds (Holm 0.035), and the corrected t-test gives p < 0.01. On plain accuracy (not tested), "
       "RS-EF-pruned (.669) is about equal to the Decision Tree (.667).")
bullet("**Python instead of the R package RoughSets.** RoughSets has no entropy-based "
       "discretization, so we implemented reducts, LEM2 and LERS ourselves.")
bullet("**Leakage check (finance attributes).** Without Debtor / Tuition / Scholarship, macro-F1 drops "
       "slightly (RF .644 → .613, RS-EF-pruned .480 → .468). Tuition fees is in 70 % of the EF reducts and half of "
       "the MDLP reducts, and in many top rules, so its unknown measurement time needs to be settled before the final report.")
bullet("**Tuning hits the edge of the grid.** The most common choice, s = 10 and β = 0.6, is the smallest value tried, so "
       "the grid should be extended (s = 5, β = 0.5).")

# ---------------------------------------------------------------- 4
heading("4. Plan until the final report (Dec 10)")
bullet("Fix the Enrolled problem: class-specific confidence thresholds, a lower β, and tuning on "
       "balanced accuracy instead of macro-F1 of the pruned model. Re-check the rule-score "
       "confidence used for the coverage curve.")
bullet("Full 5×10 CV with all models, including RS-EF-classic; Wilcoxon + Holm and the "
       "Nadeau–Bengio corrected t-test.")
bullet("Sensitivity: k for equal-frequency, pruning thresholds (grid already saved), granulation grid.")
bullet("Dropout early-warning view (accept / defer / reject regions), then the write-up and oral-session slides.")

para("**Who does what**", after=1)
rows = [["Member", "Milestone", "Until the final report"],
        ["Md Pares Mahmud", "Implementation, running experiments, checking results",
         "Fix the Enrolled problem; full 5×10 CV runs"],
        ["Abu Hanif", "Milestone report write-up",
         "Significance tests; sensitivity analysis"],
        ["Shirsha Mitra", "Figures and presentation slides",
         "Dropout early-warning view; final slides"]]
t = table(rows, [2.2, 2.6, 2.3], size=8.5)

doc.save("milestone/milestone_report.docx")
print("saved")
