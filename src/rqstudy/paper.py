"""Typeset the dated, source-linked study report using the underlying result tables."""

from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape
import matplotlib
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

RQ = "https://arxiv.org/html/2606.26294v3#A2.SS4"
HA = "https://arxiv.org/pdf/2603.19461v2#page=60"
BASE = "https://github.com/DreamFallenFlowers/OpenRQGM/tree/feecb32d9fbdd1c60749ade9ecb47f971e12666e"
G = "https://github.com/BurnyCoder/red-queen-godel-machine-with-evolvable-parent-selection"
SRC = "https://github.com/facebookresearch/HyperAgents/blob/59a68f672dfb92c74aeb7e61535d776fb36e172d/utils/gl_utils.py#L571-L584"


def link(label, url):
    return f'<link href="{url}" color="#086c66"><u>{label}</u></link>'


def make_paper(
    project, status, scores, searches, contrasts, examples, computes, routes, runs
):
    """Keep the preliminary protocol readable and insert outcomes only when observed."""
    rl_config.invariant = 1
    fonts = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    for alias, name in (
        ("Study", "DejaVuSans.ttf"),
        ("StudyBold", "DejaVuSans-Bold.ttf"),
        ("StudySerif", "DejaVuSerif.ttf"),
    ):
        if alias not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(alias, str(fonts / name)))
    ink = colors.HexColor("#193535")
    styles = {
        key: ParagraphStyle(
            key,
            fontName=font,
            fontSize=size,
            leading=leading,
            textColor=ink,
            spaceAfter=after,
            keepWithNext=key == "h",
        )
        for key, font, size, leading, after in (
            ("title", "StudySerif", 23, 28, 12),
            ("h", "StudyBold", 13, 16, 6),
            ("body", "Study", 9, 13, 7),
            ("small", "Study", 7.5, 10, 5),
            ("cell", "Study", 7, 9, 0),
            ("th", "StudyBold", 7, 9, 0),
        )
    }
    out = project / "reports" / "paper.pdf"
    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=17 * mm,
        bottomMargin=18 * mm,
        title="Editable expansion-parent selection in the Red Queen Gödel Machine",
        author="Libor “Burny” Burian",
    )
    story = []

    def p(value, style="body"):
        story.append(Paragraph(value, styles[style]))

    def heading(value):
        p(value, "h")

    def tab(head, body, widths):
        cells = [
            [Paragraph(escape(str(v)), styles["th" if i == 0 else "cell"]) for v in row]
            for i, row in enumerate([head, *body])
        ]
        obj = Table(
            cells, colWidths=[mm * x for x in widths], repeatRows=1, hAlign="LEFT"
        )
        obj.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6f1ed")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f7f9f8")],
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.extend([obj, Spacer(1, 8)])

    p("Editable expansion-parent selection in the Red Queen Gödel Machine", "title")
    p(
        "Libor “Burny” Burian · " + datetime.now().astimezone().strftime("%d %B %Y"),
        "small",
    )
    heading("Abstract")
    p(
        "Can a system improve its paper reviewer by rewriting the rule for choosing which archived agent to edit? We use a frozen local Qwen3.5-4B to evolve writer, reviewer, meta-agent and selector programs. The primary comparison holds the validation budget fixed and pairs search seeds across editable and native clade Thompson selection. The outcome is agreement with historical conference decisions on sealed manuscripts. "
        + status
    )
    heading("Motivation and related work")
    p(
        "RQGM evaluates writers under an incumbent reviewer that can change after an anchored election. Useful ancestors can therefore change as search proceeds. HyperAgents gave the latest agent control over parent selection. Its combined paper-review and robotics experiment did not establish a statistically significant ranking of its three selection methods. We test the intervention under a changing evaluator with native RQGM as the primary comparator. "
        + link("RQGM Algorithm 1", RQ)
        + " · "
        + link("HyperAgents Appendix E.5", HA)
        + "."
    )
    heading("Method")
    p(
        "Each expansion executes the newest valid selector against a snapshot. The selected parent supplies all four programs to its editor. The child enters the archive after validation. Native expansion pools successes and failures over descendants. All arms choose evaluation nodes from their own evidence, balance eligible roles and tasks, and collect lineage training feedback on first expansion. A reviewer election uses distinct human judgments and the lower fifth percentile of a Beta posterior. A new incumbent invalidates dependent writer scores. "
        + link("OpenRQGM base", BASE)
        + " · "
        + link(
            "Registered local choices", G + "/blob/5454789/reports/preregistration.md"
        )
        + "."
    )
    image = project / "docs" / "figures" / "architecture.png"
    story.append(Image(str(image), width=164 * mm, height=59 * mm))
    p(
        "Figure 1. Workspace inheritance and the reviewer election. Human decisions anchor reviewers throughout search.",
        "small",
    )
    story.append(PageBreak())
    heading("Experimental design and analysis")
    p(
        "The corpus is grouped by manuscript version before splitting. Each main split contains 100 papers balanced by historical outcome. A separate balanced pilot has 24 papers. The writer sees the title and abstract. The reviewer sees the cleaned text or fixed-reader notes covering every chunk. Test identities are frozen jointly before scoring. The preregistration allocates eight paired primary seeds and five for each secondary control. Pilot throughput alone sets their common budget. The paper-stratified crossed bootstrap resamples seed blocks and shared paper IDs. "
        + link(
            "Released paper data",
            "https://github.com/facebookresearch/HyperAgents/tree/59a68f672dfb92c74aeb7e61535d776fb36e172d/domains/paper_review",
        )
        + " · "
        + link("Crossed bootstrap", "https://artowen.su.domains/reports/pbs2.pdf")
        + "."
    )
    heading("Results")
    p(status)
    if scores:
        tab(
            ["Split", "Frozen reviewer", "Scored", "Correct", "Accuracy", "Status"],
            scores,
            [17, 55, 18, 21, 24, 27],
        )
    else:
        tab(
            ["Condition", "Registered evaluation"],
            [
                [
                    "Editable / native",
                    "Paired sealed comparison at the pilot-selected budget.",
                ],
                [
                    "Uniform / handcrafted",
                    "Secondary fixed controls evaluated on the same papers.",
                ],
                ["Root", "Unevolved reviewer, scored directly."],
                [
                    "Midpoint fork",
                    "Seed-one editable state, continued with native parent choice.",
                ],
            ],
            [52, 110],
        )
    for key, c in contrasts.items():
        p(
            f"{key.replace('_', ' ').capitalize()}: {c['mean_pp']:+.2f} pp, 95% interval [{c['low']:+.2f}, {c['high']:+.2f}]."
        )
        tab(
            ["Paired seed", "Editable minus native (pp)"],
            [[s, f"{v:+.2f}"] for s, v in zip(c["seeds"], c["per_seed_pp"])],
            [48, 75],
        )
    endpoint_fig = project / "docs" / "figures" / "endpoints.png"
    if endpoint_fig.exists() and scores:
        story.append(Image(str(endpoint_fig), width=158 * mm, height=62 * mm))
        p(
            "Endpoint accuracy by evaluation split. Points represent individual completed evaluations; coincident values overlap.",
            "small",
        )
    heading("Mechanism and interpretation")
    p(
        "Source changes alone cannot establish that the selector changed the trajectory. The event ledger identifies the owner, executed source, parent and child. Replaying the two handcrafted formulas isolates differences in individual choices on fixed snapshots. Continuing the first editable midpoint under native selection measures a single trajectory intervention. "
        + link("Released weighting code", SRC)
        + "."
    )
    if searches:
        tab(
            [
                "Search",
                "Validation",
                "Nodes",
                "Selector edits",
                "Invalid",
                "Fallbacks",
                "Swaps",
                "Erased",
                "Replay diff.",
            ],
            searches,
            [43, 20, 13, 16, 12, 16, 13, 13, 18],
        )
        for r in runs:
            if r["complete"] and (r["stage"] == "pilot" or r["arm"] == "fork-native"):
                story.append(
                    KeepTogether(
                        [
                            Image(
                                str(
                                    project / "docs" / "figures" / (r["name"] + ".png")
                                ),
                                width=154 * mm,
                                height=53 * mm,
                            ),
                            Paragraph(
                                escape(r["name"])
                                + ". Valid-record accuracy and reward; dotted lines show reviewer replacement. The adjacent tree records parentage.",
                                styles["small"],
                            ),
                        ]
                    )
                )
    heading("Limitations and conclusions")
    p(
        "Historical acceptance reflects decisions made by a conference. Interpretation is conditional on the public corpus, model, input cleaning, fixed-reader compression, constrained program interface and local search budget. Pretraining familiarity is unknown. An eight-paper election packet can give noisy rankings or ties. Agreement on that packet is development evidence. Per-route sealed results quantify a possible long-document confound. "
        + link("Methodological review", G + "/blob/main/reports/reviews/methods.md")
        + "."
    )
    p(
        status
        + " The study reports invalid edits, low turnover and negative effects as observed."
    )
    if computes or routes or examples:
        story.append(PageBreak())
        heading("Appendix · Compute, reading routes and outputs")
        if computes:
            tab(
                [
                    "Run",
                    "Calls",
                    "Actual calls",
                    "Logical input",
                    "Logical output",
                    "Actual input",
                    "Actual output",
                    "GPU svc h",
                    "Failures",
                ],
                computes,
                [43, 13, 15, 17, 17, 17, 17, 14, 12],
            )
            p(
                "GPU service time sums actual Ollama request durations while the model resides on the GPU. Shared-prefix costs are included in fork comparisons. Logical totals include cache hits.",
                "small",
            )
        if routes:
            tab(
                ["Endpoint", "Reading route", "Papers", "Accuracy"],
                routes,
                [74, 38, 25, 25],
            )
        for arm, roles in examples.items():
            for role, ex in roles.items():
                heading(escape(arm + " · " + role))
                p(escape(ex["text"][:1100]), "small")
                p(
                    escape(
                        f"{ex['run']} · paper {ex['id']} · decision {ex['decision']}. The full output is retained in the result file."
                    ),
                    "small",
                )
    heading("Reproducibility")
    p(
        link("Source, tests and published results", G)
        + " · "
        + link(
            "Evolved program collection",
            "https://huggingface.co/collections/BurnyCoder/rqgm-with-editable-parent-selection-6affcf0378cae9548869a3f0",
        )
        + " · "
        + link(
            "Literature and source audit", G + "/blob/main/reports/literature-review.md"
        )
        + ". Regenerate this report and its figures with uv run --locked rqgm-study report."
    )
    heading("AI authorship statement")
    p(
        "Codex wrote this study codebase and paper from the exact specification provided by a human. Human cleanup and rewriting are in progress.",
        "small",
    )

    def footer(canvas, document):
        canvas.setFont("Study", 7)
        canvas.setFillColor(colors.HexColor("#516560"))
        canvas.drawString(20 * mm, 10 * mm, "RQGM  /  Editable parent selection")
        canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, str(document.page))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
