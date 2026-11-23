"""Build milestone/milestone_slides.pptx (run from gc_project/).
Numbers come from results/quick/summary.md and
results/quick/extra_RS-EF-classic_folds.csv."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

FIG = "results/quick/figures/"
NAVY = RGBColor(0x1F, 0x3A, 0x5F)
BLUE = RGBColor(0x2A, 0x78, 0xD6)
ORANGE = RGBColor(0xEB, 0x68, 0x34)
INK = RGBColor(0x1A, 0x1A, 0x1A)
GREY = RGBColor(0x5A, 0x5A, 0x5A)
LIGHT = RGBColor(0xEE, 0xF3, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FILL_IN = RGBColor(0xC0, 0x39, 0x2B)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
W = prs.slide_width


def textbox(slide, x, y, w, h, lines, size=18, color=INK, bold=False,
            align=PP_ALIGN.LEFT, bullets=False, space=6):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    for i, line in enumerate(lines if isinstance(lines, list) else [lines]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.space_after = Pt(space)
        parts = (("• " if bullets else "") + line).split("**")
        for k, part in enumerate(parts):
            if not part: continue
            r = p.add_run(); r.text = part
            r.font.size = Pt(size); r.font.color.rgb = color
            r.font.bold = bold or (k % 2 == 1); r.font.name = "Calibri"
    return tb


PRESENTER = {**{n: "Md Pares Mahmud" for n in (1, 2, 3, 4)},
             **{n: "Abu Hanif" for n in (5, 6, 7)},
             **{n: "Shirsha Mitra" for n in (8, 9, 10)}}


def slide(title, number, notes=""):
    s = prs.slides.add_slide(BLANK)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, Inches(0.12))
    bar.fill.solid(); bar.fill.fore_color.rgb = NAVY; bar.line.fill.background()
    textbox(s, 0.6, 0.35, 12, 0.8, title, size=30, color=NAVY, bold=True)
    textbox(s, 12.2, 7.0, 1, 0.4, str(number), size=11, color=GREY,
            align=PP_ALIGN.RIGHT)
    textbox(s, 0.6, 7.0, 8, 0.4,
            f"Rough-set rules for student dropout prediction · Milestone · Presenter: {PRESENTER[number]}",
            size=11, color=GREY)
    if notes:
        s.notes_slide.notes_text_frame.text = f"Presenter: {PRESENTER[number]}. " + notes
    return s


def box(s, x, y, w, h, text, fill=LIGHT, color=INK, size=16, bold=False):
    b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y),
                           Inches(w), Inches(h))
    b.fill.solid(); b.fill.fore_color.rgb = fill; b.line.fill.background()
    tf = b.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = line; r.font.size = Pt(size if i == 0 else size - 4)
        r.font.color.rgb = color; r.font.bold = bold if i == 0 else False
        r.font.name = "Calibri"
    return b


def table(s, x, y, w, rows, col_w, size=14, highlight=()):
    t = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y),
                           Inches(w), Inches(0.42 * len(rows))).table
    for j, cw in enumerate(col_w):
        t.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = t.cell(i, j); c.text = str(v)
            c.fill.solid()
            c.fill.fore_color.rgb = NAVY if i == 0 else (LIGHT if i in highlight else WHITE)
            for p in c.text_frame.paragraphs:      # cells may hold several lines
                p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
                for r in p.runs:
                    f = r.font; f.size = Pt(size); f.name = "Calibri"
                    f.color.rgb = WHITE if i == 0 else INK
                    f.bold = (i == 0) or (i in highlight)
    return t


# 1 ------------------------------------------------------------ title
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
textbox(s, 0.9, 2.0, 11.5, 1.6,
        "Rough-Set Decision Rules for Early Prediction of Student Dropout",
        size=40, color=WHITE, bold=True)
textbox(s, 0.9, 3.9, 11.5, 0.6, "Information Granular Computing · Milestone presentation",
        size=22, color=RGBColor(0xC8, 0xD6, 0xE8))
textbox(s, 0.9, 4.7, 11.5, 1.6, ["Md Pares Mahmud",
                                  "Abu Hanif",
                                  "Shirsha Mitra"],
        size=20, color=WHITE, space=2)
s.notes_slide.notes_text_frame.text = (
    "Presenter: Md Pares Mahmud (slides 1-4). Introduce the team and the question: can we extract readable "
    "IF-THEN rules that warn early about students who will drop out?")

# 2 ------------------------------------------------------------ problem & data
s = slide("Problem and data", 2,
          "Early-warning setting: we only use what is known after the 1st semester. "
          "2nd-semester grades would make the task easy but too late to help.")
textbox(s, 0.6, 1.4, 6.6, 5, [
    "**Goal:** predict early which students will drop out, with **readable IF–THEN rules**",
    "**Data:** UCI “Predict Students' Dropout and Academic Success” (Realinho et al.)",
    "4,424 students, 3 classes",
    "**Early warning:** only enrollment data + 1st-semester results; all 2nd-semester columns removed",
    "**30 condition attributes** (27 without the finance attributes)",
], size=20, bullets=True, space=12)
n = {"Graduate": 2209, "Dropout": 1421, "Enrolled": 794}
y0 = 1.9
for i, (k, v) in enumerate(n.items()):
    textbox(s, 7.7, y0 + i * 1.3, 1.6, 0.5, k, size=18, color=INK, bold=True)
    w = 2.6 * v / 2209
    b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(9.3), Inches(y0 + i * 1.3 + 0.05),
                           Inches(w), Inches(0.45))
    b.fill.solid(); b.fill.fore_color.rgb = ORANGE if k == "Dropout" else BLUE
    b.line.fill.background()
    textbox(s, 9.3 + w + 0.1, y0 + i * 1.3, 1.3, 0.5, f"{v:,}", size=18, color=GREY)
textbox(s, 7.7, 5.8, 5, 0.5, "Students per class", size=14, color=GREY)

# 3 ------------------------------------------------------------ pipeline
s = slide("Method: rough-set pipeline", 3,
          "Everything is fit inside each training fold, so nothing leaks into the test fold. "
          "Implemented in Python ourselves, because the R package RoughSets has no "
          "entropy-based discretization.")
steps = [("Discretize", "Equal-Frequency (k=4)\nor MDLP entropy"),
         ("Reduct", "QuickReduct on\ndependency γ"),
         ("Rules", "LEM2: certain (lower)\n+ possible (upper)"),
         ("Prune", "support ≥ 5\nconfidence ≥ 0.6"),
         ("Classify", "LERS voting\n+ partial matching"),
         ("3-way decision", "accept / defer\nuncertain students")]
bw, gap = 1.85, 0.25
for i, (a, b) in enumerate(steps):
    x = 0.6 + i * (bw + gap)
    box(s, x, 1.8, bw, 1.6, f"{a}\n{b}", size=18, bold=True,
        fill=NAVY if i in (1, 5) else LIGHT, color=WHITE if i in (1, 5) else INK)
    if i < len(steps) - 1:
        ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + bw + 0.02),
                                Inches(2.45), Inches(gap - 0.04), Inches(0.3))
        ar.fill.solid(); ar.fill.fore_color.rgb = GREY; ar.line.fill.background()
textbox(s, 0.6, 4.0, 12, 3, [
    "**Our granular-computing change:** a granule only counts toward the positive region if it holds "
    "at least **s** students, with VPRS precision **β** (Ziarko 1993); s and β tuned inside each fold",
    "**Evaluation:** stratified 10-fold CV (1 repeat for the milestone), vs. Decision Tree, "
    "Random Forest, Naive Bayes",
    "**6 unit tests** check the core on a hand-computed decision table — all pass",
], size=18, bullets=True, space=10)

# 4 ------------------------------------------------------------ classic vs ours
s = slide("Classical reducts overfit", 4,
          "The classical Pawlak reduct keeps many-valued attributes like parents' occupation: "
          "tiny granules are trivially consistent. Result: over a thousand rules, each covering "
          "about 4 students. Our version needs only a handful of rules. Be honest: classic still "
          "has higher macro-F1, because it predicts some Enrolled students (next slides).")
table(s, 0.6, 1.5, 12.1, [
    ["Model", "Attributes in reduct", "Rules", "Mean rule length", "Students per rule",
     "Accuracy", "MCC", "Macro-F1"],
    ["Classical Pawlak (RS-EF-classic)", "13.2", "1,337", "4.5", "4", ".635", ".379", ".524"],
    ["Ours: granule-size-aware + pruned (RS-EF-pruned)", "2.8", "8.2", "1.9", "436", ".669", ".448", ".480"],
], [3.9, 1.35, 1.0, 1.35, 1.35, 1.05, 1.0, 1.1], size=15, highlight=(2,))
box(s, 0.6, 3.4, 3.8, 1.6, "160× fewer rules\nfrom 1,337 to about 8", fill=NAVY, color=WHITE,
    size=26, bold=True)
box(s, 4.75, 3.4, 3.8, 1.6, "Higher accuracy & MCC\n.635 → .669   ·   .379 → .448", size=24, bold=True)
box(s, 8.9, 3.4, 3.8, 1.6, "But lower macro-F1\n.524 → .480 (Enrolled lost)", size=24, bold=True,
    fill=RGBColor(0xFD, 0xED, 0xE6))
textbox(s, 0.6, 5.4, 12, 1.2,
        "Classical reduct example (fold 1): course, application mode, mother's qualification, "
        "both parents' occupations, … → granules of a few students that look “certain” but do not generalize.",
        size=16, color=GREY)

# 5 ------------------------------------------------------------ results
s = slide("Preliminary results (1×10 CV)", 5,
          "The pruned rough-set models are significantly below the baselines on macro-F1 "
          "(and on balanced accuracy, the other metric tested): Wilcoxon p = 0.002 for every comparison, "
          "the smallest possible with 10 folds; Holm 0.035; corrected t-test p < 0.01. Plain accuracy was "
          "not tested: there RS-EF-pruned (.669) is about equal to the Decision Tree (.667). "
          "RS-EF-classic is not in the quick run; we ran it separately on the same 10 folds.")
table(s, 0.6, 1.4, 6.6, [
    ["Model", "Accuracy", "Macro-F1", "MCC", "Recall Enrolled"],
    ["RS-EF-classic", ".635", ".524", ".379", ".164"],
    ["RS-EF-pruned", ".669", ".480", ".448", ".000"],
    ["RS-MDLP-pruned", ".660", ".472", ".431", ".000"],
    ["Decision Tree", ".667", ".601", ".459", ".343"],
    ["Random Forest", ".743", ".644", ".572", ".252"],
    ["Naive Bayes", ".691", ".598", ".485", ".234"],
], [2.0, 1.1, 1.1, 1.0, 1.4], size=15, highlight=(2, 3))
textbox(s, 0.6, 4.6, 6.6, 2.2, [
    "Plain accuracy: RS-EF-pruned **.669** ≈ Decision Tree **.667**",
    "Macro-F1 is 0.12–0.17 lower: the pruned rough-set models **never predict Enrolled**",
    "The macro-F1 gap vs. every baseline is statistically significant",
], size=17, bullets=True, space=8)
s.shapes.add_picture(FIG + "models_macro_f1.png", Inches(7.4), Inches(1.4), width=Inches(5.5))

# 6 ------------------------------------------------------------ rules
s = slide("What the rules say", 6,
          "These rules are fit on all data, for interpretation only (not for the CV numbers). "
          "Grades are on the Portuguese 0–20 scale. Support = number of students the rule matches; "
          "confidence = share of them that really have that outcome.")
table(s, 0.6, 1.5, 12.1, [
    ["Rule (MDLP discretization)", "Students", "Confidence"],
    ["IF tuition fees up to date AND 1st-sem grade ≥ 13.3  →  Graduate", "1,156", "0.80"],
    ["IF 1st-sem grade < 9.9  →  Dropout", "719", "0.79"],
    ["IF tuition fees NOT up to date  →  Dropout", "528", "0.87"],
    ["IF tuition NOT up to date AND 10.5 ≤ 1st-sem grade < 12.3  →  Dropout", "160", "0.89"],
], [9.1, 1.5, 1.5], size=17)
textbox(s, 0.6, 4.3, 12, 2.2, [
    "Short rules (1–2 conditions) that a student advisor can check by hand",
    "These rules use **1st-semester grade average** and **tuition fees** only",
    "Across the CV folds the reducts also use units approved (40–50 % of folds) and "
    "scholarship (EF 70 %, MDLP 20 %)",
], size=19, bullets=True, space=10)

# 7 ------------------------------------------------------------ three-way
s = slide("Three-way decision: defer uncertain students", 7,
          "The diamond is the rough-set three-way decision: accept only when certain rules of "
          "a single class match. It decides 75.6% of students at 76.9% accuracy, vs 66.9% when "
          "forced to decide everyone. But Random Forest is better at about the same coverage (83.6% at 75%), and the "
          "rough-set curve is flat, so its vote is not a good confidence score yet.")
s.shapes.add_picture(FIG + "coverage_accuracy.png", Inches(0.5), Inches(1.3), width=Inches(7.6))
box(s, 8.5, 1.5, 4.3, 1.4, "76% decided\nat 77% accuracy (vs 67% for all)", fill=NAVY,
    color=WHITE, size=26, bold=True)
textbox(s, 8.5, 3.2, 4.4, 3.5, [
    "The other 24% are deferred to an advisor",
    "Random Forest at 75% coverage: **84%**",
    "Rough-set curve is flat → the LERS vote does not rank confidence well yet",
], size=17, bullets=True, space=10)

# 8 ------------------------------------------------------------ issues
s = slide("Findings and open issues", 8,
          "Main message: the method works and is interpretable, but the Enrolled class is the "
          "weak point and we know why.")
items = [
    ("“Enrolled” is never predicted",
     "Enrolled-majority granules are rare and tiny (≤ 6 students); other Enrolled rules reach ≤ 0.40 "
     "confidence. Pruning removes all Enrolled rules in 19 of 20 fold models; the one left is outvoted."),
    ("Leakage check: finance attributes",
     "Without Debtor / Tuition / Scholarship: RF .644 → .613, RS-EF-pruned .480 → .468. "
     "Tuition is in 70% of EF reducts → we need to check when it was measured."),
    ("Tuning hits the edge of the grid",
     "The most common choice, s = 10 and β = 0.6, is the smallest value tried → extend the grid (s = 5, β = 0.5)."),
    ("Tool change",
     "Python instead of R RoughSets, which has no entropy-based discretization."),
]
for i, (h, b) in enumerate(items):
    y = 1.4 + i * 1.35
    acc = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(y), Inches(0.12), Inches(1.1))
    acc.fill.solid(); acc.fill.fore_color.rgb = ORANGE if i == 0 else BLUE; acc.line.fill.background()
    textbox(s, 0.9, y - 0.05, 11.8, 0.5, h, size=20, bold=True, color=NAVY)
    textbox(s, 0.9, y + 0.42, 11.8, 0.7, b, size=16, color=INK)

# 9 ------------------------------------------------------------ plan
s = slide("Plan until the final report (Dec 10)", 9,
          "Each member owns one part of the remaining work (table on the right).")
textbox(s, 0.6, 1.4, 6.8, 5, [
    "**Fix Enrolled:** class-specific confidence thresholds, lower β, tune on balanced accuracy",
    "**Full 5×10 CV** incl. classic model; Wilcoxon + Holm, corrected t-test",
    "**Sensitivity:** k for equal-frequency, pruning thresholds, granulation grid",
    "**Dropout early-warning view:** accept / defer / reject regions",
    "Final write-up and oral-session slides",
], size=18, bullets=True, space=12)
t = table(s, 7.6, 1.5, 5.2, [
    ["Member", "Milestone", "Until Dec 10"],
    ["Md Pares Mahmud", "Code, experiments", "Fix Enrolled, 5×10 CV"],
    ["Abu Hanif", "Report write-up", "Significance, sensitivity"],
    ["Shirsha Mitra", "Figures, slides", "Dropout view, final slides"],
], [1.9, 1.5, 1.8], size=13)

# 10 ----------------------------------------------------------- end
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, W, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
textbox(s, 0.9, 2.6, 11.5, 1, "Thank you — questions?", size=44, color=WHITE, bold=True)
textbox(s, 0.9, 3.8, 11.5, 1.5, [
    "Readable rules: 1,337 → about 8, accuracy on par with a Decision Tree",
    "Next: make rough sets recognize the “Enrolled” students",
], size=22, color=RGBColor(0xC8, 0xD6, 0xE8), bullets=True)

s.notes_slide.notes_text_frame.text = "Presenter: Shirsha Mitra. Sum up and take questions; all three answer questions on their own part."
prs.save("milestone/milestone_slides.pptx")
print("saved", len(prs.slides), "slides")
