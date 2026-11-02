"""Build a clean A4, two-column research paper from paper_content.py.
Uses only saved CSV/JSON outputs and existing figure PNGs; does not rerun ML.
"""

import os
import re
import shutil
import sys
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image,
    Table, TableStyle, FrameBreak, NextPageTemplate, KeepTogether,
)

import paper_content as C
from config import OUT, ROOT

# ------------------------------------------------------------------
# Fonts: use Windows Arial where available; otherwise DejaVu/Liberation.
# ------------------------------------------------------------------
def register_fonts():
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    candidates = [
        (windir / "Fonts", ("arial.ttf", "arialbd.ttf", "ariali.ttf", "arialbi.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu"), ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf", "DejaVuSans-BoldOblique.ttf")),
        (Path("/usr/share/fonts/truetype/liberation2"), ("LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf", "LiberationSans-Italic.ttf", "LiberationSans-BoldItalic.ttf")),
    ]
    for folder, files in candidates:
        paths = [folder / f for f in files]
        if all(p.is_file() for p in paths):
            for name, path in zip(("Body", "Body-B", "Body-I", "Body-BI"), paths):
                pdfmetrics.registerFont(TTFont(name, str(path)))
            pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I", boldItalic="Body-BI")
            return
    from reportlab.pdfbase.pdfmetrics import Font
    for name, base in (("Body", "Helvetica"), ("Body-B", "Helvetica-Bold"), ("Body-I", "Helvetica-Oblique"), ("Body-BI", "Helvetica-BoldOblique")):
        pdfmetrics.registerFont(Font(name, base, "WinAnsiEncoding"))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I", boldItalic="Body-BI")

register_fonts()

# ------------------------------------------------------------------
# Page geometry and styles.
# ------------------------------------------------------------------
PAGE_W, PAGE_H = A4
LEFT = RIGHT = 1.45 * cm
TOP = 1.72 * cm
BOTTOM = 1.5 * cm
GAP = 0.62 * cm
FULL_W = PAGE_W - LEFT - RIGHT
COL_W = (FULL_W - GAP) / 2
CONTENT_H = PAGE_H - TOP - BOTTOM
NAVY = colors.HexColor("#1f3a68")
PALE = colors.HexColor("#e8edf5")
BASE = float(os.environ.get("BASE", "9.2"))

S = {
    "body": ParagraphStyle("body", fontName="Body", fontSize=BASE, leading=BASE * 1.23, alignment=TA_JUSTIFY, spaceAfter=3.5, allowWidows=0, allowOrphans=0),
    "h1": ParagraphStyle("h1", fontName="Body-B", fontSize=10.4, leading=12.4, textColor=NAVY, spaceBefore=6, spaceAfter=2.5, keepWithNext=True),
    "h2": ParagraphStyle("h2", fontName="Body-BI", fontSize=9.2, leading=11, spaceBefore=4, spaceAfter=2, keepWithNext=True),
    "caption": ParagraphStyle("caption", fontName="Body", fontSize=7.4, leading=8.8, alignment=TA_JUSTIFY, spaceBefore=2, spaceAfter=4),
    "table_caption": ParagraphStyle("table_caption", fontName="Body", fontSize=7.5, leading=9, alignment=TA_LEFT, spaceAfter=3, keepWithNext=True),
    "cell": ParagraphStyle("cell", fontName="Body", fontSize=6.6, leading=8, alignment=TA_LEFT, splitLongWords=0, spaceAfter=0),
    "cellb": ParagraphStyle("cellb", fontName="Body-B", fontSize=6.6, leading=8, alignment=TA_LEFT, splitLongWords=0, spaceAfter=0),
    "title": ParagraphStyle("title", fontName="Body-B", fontSize=16.5, leading=19.5, alignment=TA_CENTER, textColor=NAVY, spaceAfter=4),
    "author": ParagraphStyle("author", fontName="Body-B", fontSize=10.5, leading=12.5, alignment=TA_CENTER, spaceAfter=2),
    "aff": ParagraphStyle("aff", fontName="Body", fontSize=7.8, leading=9.4, alignment=TA_CENTER, spaceAfter=1.5),
    "abstract": ParagraphStyle("abstract", fontName="Body", fontSize=8.3, leading=10, alignment=TA_JUSTIFY, spaceBefore=4, spaceAfter=3),
    "keywords": ParagraphStyle("keywords", fontName="Body", fontSize=8.1, leading=9.7, alignment=TA_JUSTIFY, spaceAfter=1),
    "ref": ParagraphStyle("ref", fontName="Body", fontSize=7.5, leading=8.9, alignment=TA_LEFT, leftIndent=13, firstLineIndent=-13, spaceAfter=2),
    "eq": ParagraphStyle("eq", fontName="Body-I", fontSize=8, leading=9.8, alignment=TA_CENTER),
}

# ------------------------------------------------------------------
# Header/footer: short, non-overlapping labels in separate positions.
# ------------------------------------------------------------------
def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.setFont("Body-B", 7.2)
    canvas.drawString(LEFT, PAGE_H - 1.03 * cm, "Delhi Bus ML Research | Problem No. 49")
    canvas.setFont("Body", 7.2)
    canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 1.03 * cm, "Ramanujan College, DU")
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(0.55)
    canvas.line(LEFT, PAGE_H - 1.18 * cm, PAGE_W - RIGHT, PAGE_H - 1.18 * cm)
    canvas.setStrokeColor(colors.grey)
    canvas.setLineWidth(0.3)
    canvas.line(LEFT, 1.12 * cm, PAGE_W - RIGHT, 1.12 * cm)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.setFont("Body", 7)
    canvas.drawString(LEFT, 0.76 * cm, "Muskan Sharma | Exam Roll No. 24020570020")
    canvas.drawRightString(PAGE_W - RIGHT, 0.76 * cm, f"Page {doc.page}")
    canvas.restoreState()


def paragraph(text, style=None):
    # Preserve ReportLab markup tags while escaping stray ampersands.
    text = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;)", "&amp;", str(text))
    return Paragraph(text, style or S["body"])


def make_table(headings, rows, widths, font_size=6.6):
    head_style = ParagraphStyle("th", parent=S["cellb"], fontSize=font_size, leading=font_size + 1.4)
    body_style = ParagraphStyle("td", parent=S["cell"], fontSize=font_size, leading=font_size + 1.4)
    data = [[paragraph(v, head_style) for v in headings]]
    data.extend([[paragraph(v, body_style) for v in row] for row in rows])
    total = float(sum(widths))
    col_widths = [COL_W * float(w) / total for w in widths]
    table = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT", splitByRow=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
        ("LINEABOVE", (0, 0), (-1, 0), 0.75, NAVY),
        ("LINEBELOW", (0, 0), (-1, 0), 0.45, NAVY),
        ("LINEBELOW", (0, -1), (-1, -1), 0.65, NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def make_figure(path, caption, preferred_width_cm):
    image_path = Path(path)
    if not image_path.is_file():
        raise FileNotFoundError(f"Required project figure is missing: {image_path}")
    with PILImage.open(image_path) as im:
        iw, ih = im.size
    width = min(float(preferred_width_cm) * cm, COL_W)
    height = width * ih / iw
    # Avoid a single very tall figure forcing excessive whitespace.
    max_height = CONTENT_H * 0.72
    if height > max_height:
        scale = max_height / height
        width *= scale
        height *= scale
    img = Image(str(image_path), width=width, height=height)
    cap = paragraph(caption, S["caption"])
    return KeepTogether([img, cap])


def build(output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    title_flowables = [
        paragraph(C.TITLE, S["title"]),
        paragraph(C.AUTHOR, S["author"]),
        paragraph(C.AFFIL, S["aff"]),
        paragraph(C.COURSE, S["aff"]),
        paragraph(C.ABSTRACT, S["abstract"]),
        paragraph(C.KEYWORDS, S["keywords"]),
    ]

    # Measure title block at its actual full-page width. This is the key
    # fix: the title/abstract frame is sized from its real wrapped height,
    # so abstract text cannot spill into the first content column.
    title_height = 0
    for flow in title_flowables:
        _, h = flow.wrap(FULL_W, 100000)
        title_height += h + flow.getSpaceBefore() + flow.getSpaceAfter()
    title_height += 0.30 * cm
    title_height = min(title_height, CONTENT_H * 0.62)

    first_column_height = CONTENT_H - title_height
    if first_column_height < 5.0 * cm:
        raise RuntimeError("Title and abstract occupy too much of page one; reduce title font or abstract length.")

    doc = BaseDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=LEFT, rightMargin=RIGHT,
        topMargin=TOP, bottomMargin=BOTTOM,
        title=C.TITLE, author=C.AUTHOR,
        subject="Machine Learning Assignment, Problem No. 49",
    )

    first_template = PageTemplate(
        id="first",
        frames=[
            Frame(LEFT, PAGE_H - TOP - title_height, FULL_W, title_height,
                  id="title", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            Frame(LEFT, BOTTOM, COL_W, first_column_height,
                  id="first_left", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            Frame(LEFT + COL_W + GAP, BOTTOM, COL_W, first_column_height,
                  id="first_right", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
        ], onPage=draw_page,
    )
    later_template = PageTemplate(
        id="later",
        frames=[
            Frame(LEFT, BOTTOM, COL_W, CONTENT_H,
                  id="left", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            Frame(LEFT + COL_W + GAP, BOTTOM, COL_W, CONTENT_H,
                  id="right", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
        ], onPage=draw_page,
    )
    doc.addPageTemplates([first_template, later_template])

    story = list(title_flowables)
    story.append(FrameBreak())
    story.append(NextPageTemplate("later"))

    # Body blocks in original order. Normal ReportLab flow handles column
    # transitions; no custom column packer or forced empty columns.
    for block in C.B:
        kind = block[0]
        if kind == "h1":
            story.append(paragraph(block[1], S["h1"]))
        elif kind == "h2":
            story.append(paragraph(block[1], S["h2"]))
        elif kind == "p":
            story.append(paragraph(block[1]))
        elif kind == "fig":
            story.append(make_figure(block[1], block[2], block[3]))
        elif kind == "eq":
            eq_table = Table(
                [[paragraph(block[1], S["eq"]), paragraph(block[2])]],
                colWidths=[COL_W - 0.9 * cm, 0.9 * cm],
            )
            eq_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 1),
                ("RIGHTPADDING", (0, 0), (-1, -1), 1),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(eq_table)
        elif kind == "table":
            caption = paragraph(block[1], S["table_caption"])
            table = make_table(block[2], block[3], block[4])
            # Caption stays with the table start; the table itself can split
            # across columns/pages and repeats its header row.
            story.append(KeepTogether([caption, table]))
            story.append(Spacer(1, 4))

    # References
    story.append(paragraph("References", S["h1"]))
    for i, ref in enumerate(C.REFS, 1):
        story.append(paragraph(f"[{i}] {ref}", S["ref"]))

    # Appendix A
    app_title, app_head, app_rows = C.APPX
    story.append(paragraph(app_title, S["h1"]))
    story.append(paragraph(
        "Validation scores (fit on a Month_1 subset, evaluated on a Month_2 subset); the test month was not used.",
        S["table_caption"],
    ))
    story.append(make_table(app_head, app_rows, [2.3, 2.9, 1.0, 1.1, 1.0], font_size=5.9))

    # Appendix B supports both old 3-column and updated 2-column content.
    app_b = C.APPX_B
    app_title_b, app_desc_b, app_head_b, app_rows_b = app_b
    story.append(paragraph(app_title_b, S["h1"]))
    story.append(paragraph(app_desc_b, S["table_caption"]))
    story.append(make_table(app_head_b, app_rows_b, [1.4] * len(app_head_b), font_size=6.3))

    # Appendix C
    story.append(paragraph(C.APPX_C[0], S["h1"]))
    story.append(paragraph(C.APPX_C[1]))

    doc.build(story)
    return doc.page


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = Path(sys.argv[1]).resolve()
        pages = build(target)
        print(f"PDF generated: {target}")
        print(f"Pages: {pages}")
    else:
        root_pdf = Path(ROOT) / "paper.pdf"
        pages = build(root_pdf)
        OUT.mkdir(parents=True, exist_ok=True)
        output_pdf = Path(OUT) / "paper.pdf"
        shutil.copy2(root_pdf, output_pdf)
        print("PDF generated successfully")
        print(f"Pages: {pages}")
        print(f"Main PDF: {root_pdf}")
        print(f"Output PDF: {output_pdf}")
