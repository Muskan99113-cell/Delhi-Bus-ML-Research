"""Editable two-column DOCX version of the paper (same content module as the PDF)."""
import re, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import paper_content as C
from config import OUT
NAVY = RGBColor(0x1F, 0x3A, 0x68)
def runs(p, markup, size=None, bold=False, italic=False):
    markup = markup.replace("&amp;", "&")
    for tok in re.split(r"(</?(?:b|i|sub|super)>)", markup):
        if not tok: continue
        m = re.fullmatch(r"<(/?)(b|i|sub|super)>", tok)
        if m:
            st = globals().setdefault("_st", {"b": 0, "i": 0, "sub": 0, "super": 0}); st[m.group(2)] = 0 if m.group(1) else 1; continue
        st = globals().setdefault("_st", {"b": 0, "i": 0, "sub": 0, "super": 0})
        r = p.add_run(tok); r.bold = bool(st["b"]) or bold; r.italic = bool(st["i"]) or italic
        r.font.subscript = bool(st["sub"]); r.font.superscript = bool(st["super"])
        if size: r.font.size = Pt(size)
    globals()["_st"] = {"b": 0, "i": 0, "sub": 0, "super": 0}
def cols(section, n):
    sp = section._sectPr; c = sp.find(qn("w:cols"))
    if c is None: c = OxmlElement("w:cols"); sp.append(c)
    c.set(qn("w:num"), str(n)); c.set(qn("w:space"), "340")
def shade(cell, hexcol):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcol); tcPr.append(sh)
def para(doc, markup, size=9.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=4, bold=False, italic=False, color=None, before=0):
    p = doc.add_paragraph(); p.alignment = align; pf = p.paragraph_format; pf.space_after = Pt(after); pf.space_before = Pt(before)
    runs(p, markup, size, bold, italic)
    if color:
        for r in p.runs: r.font.color.rgb = color
    return p
def table(doc, head, rows, widths_cm, size=8, boldrow=None):
    t = doc.add_table(rows=1, cols=len(head)); t.style = "Table Grid"; t.autofit = False
    tot = sum(widths_cm); sc = 8.2 / tot
    tp = t._tbl.tblPr; lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tp.append(lay)
    tw = tp.find(qn("w:tblW"))
    if tw is None: tw = OxmlElement("w:tblW"); tp.append(tw)
    tw.set(qn("w:type"), "dxa"); tw.set(qn("w:w"), str(int(8.2 / 2.54 * 1440)))
    for i, w in enumerate(widths_cm): t.columns[i].width = Cm(w * sc)
    for i, h in enumerate(head):
        c = t.rows[0].cells[i]; c.width = Cm(widths_cm[i]*sc); c.text = ""; runs(c.paragraphs[0], h, size, bold=True); shade(c, "E8EDF5")
    for ri, r in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].width = Cm(widths_cm[i]*sc); cells[i].text = ""; runs(cells[i].paragraphs[0], str(v), size, bold=(boldrow == ri))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
def build(path):
    doc = Document(); st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(9.5)
    s0 = doc.sections[0]; s0.page_width, s0.page_height = Cm(21.0), Cm(29.7)
    for a in ("left_margin", "right_margin"): setattr(s0, a, Cm(1.45))
    s0.top_margin, s0.bottom_margin = Cm(1.8), Cm(1.6)
    hp = s0.header.paragraphs[0]; hp.text = "Delhi City-Bus Interval Prediction — ML Application Assignment, B.Sc. (Hons.) CS, Ramanujan College, University of Delhi | Journal-format submission"
    for r in hp.runs: r.font.size = Pt(7.5); r.font.color.rgb = NAVY; r.bold = True
    fp = s0.footer.paragraphs[0]; fp.text = "M. Sharma (Roll No. 24020570020) — Problem No. 49. Real data, real results (see Data availability)."
    for r in fp.runs: r.font.size = Pt(7.5); r.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
    para(doc, C.TITLE, 17, WD_ALIGN_PARAGRAPH.CENTER, 4, bold=True, color=NAVY)
    para(doc, C.AUTHOR, 11, WD_ALIGN_PARAGRAPH.CENTER, 1, bold=True)
    para(doc, C.AFFIL, 8.5, WD_ALIGN_PARAGRAPH.CENTER, 1); para(doc, C.COURSE, 8.5, WD_ALIGN_PARAGRAPH.CENTER, 4)
    para(doc, C.ABSTRACT, 9, before=4, after=3); para(doc, C.KEYWORDS, 8.8, after=4)
    s1 = doc.add_section(WD_SECTION.CONTINUOUS); cols(s1, 2)
    for b in C.B:
        k = b[0]
        if k == "h1": para(doc, b[1], 11, WD_ALIGN_PARAGRAPH.LEFT, 2, bold=True, color=NAVY, before=6).paragraph_format.keep_with_next = True
        elif k == "h2": para(doc, b[1], 9.8, WD_ALIGN_PARAGRAPH.LEFT, 2, bold=True, italic=True, before=3).paragraph_format.keep_with_next = True
        elif k == "p": para(doc, b[1])
        elif k == "eq": para(doc, b[1] + "      " + b[2], 9, WD_ALIGN_PARAGRAPH.CENTER, 4, italic=True)
        elif k == "fig":
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True; p.add_run().add_picture(b[1], width=Cm(min(b[3], 8.4)))
            para(doc, b[2], 8.3, after=6)
        elif k == "table":
            para(doc, b[1], 8.3, after=2).paragraph_format.keep_with_next = True
            bi = None
            if len(b) > 5 and b[5]: bi = min(range(3, 8), key=lambda i: float(b[3][i][2]))
            table(doc, b[2], b[3], b[4], 8, bi)
    para(doc, "References", 11, WD_ALIGN_PARAGRAPH.LEFT, 2, bold=True, color=NAVY, before=6)
    for i, r in enumerate(C.REFS, 1): para(doc, f"[{i}] " + r, 8.3, WD_ALIGN_PARAGRAPH.LEFT, 2)
    t, h, rows = C.APPX; para(doc, t, 11, WD_ALIGN_PARAGRAPH.LEFT, 2, bold=True, color=NAVY, before=6)
    para(doc, "Validation scores (fit on a Month_1 subset, evaluated on a Month_2 subset); the test month was not used.", 8.3, after=2); table(doc, h, rows, [2.3, 2.9, 1.0, 1.1, 1.0], 7.5)
    tB, capB, hB, rB = C.APPX_B; para(doc, tB, 11, WD_ALIGN_PARAGRAPH.LEFT, 2, bold=True, color=NAVY, before=6); para(doc, capB, 8.3, after=2); table(doc, hB, rB, [1, 1.2, 1.2], 7.5)
    para(doc, C.APPX_C[0], 11, WD_ALIGN_PARAGRAPH.LEFT, 2, bold=True, color=NAVY, before=6); para(doc, C.APPX_C[1], 9, WD_ALIGN_PARAGRAPH.LEFT)
    doc.core_properties.title = C.TITLE; doc.core_properties.author = C.AUTHOR
    doc.save(path)
if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else str(OUT / "paper.docx")); print("docx saved")
