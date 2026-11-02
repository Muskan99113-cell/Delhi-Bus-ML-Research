"""Build the journal-style two-column PDF (A4) from paper_content.py using reportlab."""
import re, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image, Table, TableStyle,
                                FrameBreak, KeepTogether, NextPageTemplate, CondPageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PI
import paper_content as C
from config import OUT
F = "/usr/share/fonts/truetype/crosextra/Carlito-"
for n, f in [("Body", "Regular"), ("Body-B", "Bold"), ("Body-I", "Italic"), ("Body-BI", "BoldItalic")]:
    pdfmetrics.registerFont(TTFont(n, F + f + ".ttf"))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I", boldItalic="Body-BI")
NAVY = colors.HexColor("#1f3a68"); import os
BASE = float(os.environ.get('BASE', 10.1)); FS = float(os.environ.get('FS', 1.1)); LD = float(os.environ.get('LD', 1.26))
S = dict(
 body=ParagraphStyle("b", fontName="Body", fontSize=BASE, leading=BASE*LD, alignment=TA_JUSTIFY, spaceAfter=3.2, allowWidows=0, allowOrphans=0),
 h1=ParagraphStyle("h1", fontName="Body-B", fontSize=10.6, leading=12.5, textColor=NAVY, spaceBefore=6, spaceAfter=2.5),
 h2=ParagraphStyle("h2", fontName="Body-BI", fontSize=9.4, leading=11.4, spaceBefore=3.5, spaceAfter=1.8),
 cap=ParagraphStyle("c", fontName="Body", fontSize=BASE-1.0, leading=(BASE-1.0)*1.2, alignment=TA_JUSTIFY, spaceBefore=1.5, spaceAfter=5),
 tcap=ParagraphStyle("tc", fontName="Body", fontSize=BASE-1.0, leading=(BASE-1.0)*1.2, alignment=TA_JUSTIFY, spaceAfter=2),
 ref=ParagraphStyle("r", fontName="Body", fontSize=7.9, leading=9.3, alignment=TA_LEFT, leftIndent=14, firstLineIndent=-14, spaceAfter=1.8),
 cell=ParagraphStyle("cell", fontName="Body", fontSize=BASE-1.3, leading=(BASE-1.3)*1.17), cellb=ParagraphStyle("cellb", fontName="Body-B", fontSize=BASE-1.3, leading=(BASE-1.3)*1.17),
 title=ParagraphStyle("t", fontName="Body-B", fontSize=17, leading=20, alignment=TA_CENTER, textColor=NAVY, spaceAfter=4),
 auth=ParagraphStyle("a", fontName="Body-B", fontSize=11, leading=13, alignment=TA_CENTER, spaceAfter=1),
 aff=ParagraphStyle("af", fontName="Body", fontSize=8.2, leading=9.8, alignment=TA_CENTER, spaceAfter=1),
 abs=ParagraphStyle("ab", fontName="Body", fontSize=8.7, leading=10.4, alignment=TA_JUSTIFY, spaceBefore=5, spaceAfter=3),
 kw=ParagraphStyle("kw", fontName="Body", fontSize=8.5, leading=10, alignment=TA_JUSTIFY, spaceAfter=0),
 eq=ParagraphStyle("eq", fontName="Body-I", fontSize=8.6, leading=10.5, alignment=TA_CENTER),
)
HEAD = "Delhi City-Bus Interval Prediction — ML Application Assignment, B.Sc. (Hons.) Computer Science, Ramanujan College, University of Delhi"
W, H = A4; LM = RM = 1.45*cm; TM = 1.75*cm; BM = 1.55*cm; GAP = 0.6*cm
CW = (W - LM - RM - GAP) / 2
def deco(c, d):
    c.saveState(); c.setFont("Body-B", 7.6); c.setFillColor(NAVY); c.drawString(LM, H-1.05*cm, HEAD[:HEAD.index(" — ")] + " — " + "ML Application Assignment, B.Sc. (Hons.) CS, Ramanujan College, University of Delhi")
    c.setFont("Body", 7.6); c.drawRightString(W-RM, H-1.05*cm, "Journal-format submission"); c.setStrokeColor(NAVY); c.setLineWidth(.6); c.line(LM, H-1.2*cm, W-RM, H-1.2*cm)
    c.setStrokeColor(colors.grey); c.setLineWidth(.3); c.line(LM, 1.15*cm, W-RM, 1.15*cm); c.setFillColor(colors.grey); c.setFont("Body", 7.4)
    c.drawString(LM, 0.78*cm, "M. Sharma (Roll No. 24020570020) — Problem No. 49: Delhi city-bus travel-time prediction. Real data, real results (see Data availability).")
    c.drawRightString(W-RM, 0.78*cm, f"Page {d.page}"); c.restoreState()
class Group(KeepTogether):
    """KeepTogether that can report its own height before being placed in a frame."""
    def __init__(self, content):
        super().__init__(content); self.parts = content
    def height(self):
        tot = 0
        for p in self.parts:
            w, h = p.wrap(CW, 10**6); tot += h + (p.getSpaceBefore() + p.getSpaceAfter() if hasattr(p, "getSpaceBefore") else 0)
        return tot
def mk(markup): return Paragraph(re.sub(r"&(?!amp;|lt;|gt;)", "&amp;", markup), S["body"])
def build(path):
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
                          title=C.TITLE, author=C.AUTHOR, subject="ML Application Assignment, Problem 49")
    fh = H - TM - BM
    tfl = [Paragraph(C.TITLE, S['title']), Paragraph(C.AUTHOR, S['auth']), Paragraph(C.AFFIL, S['aff']), Paragraph(C.COURSE, S['aff']), Paragraph(C.ABSTRACT, S['abs']), Paragraph(C.KEYWORDS, S['kw'])]
    ttl = sum(f.wrap(W-LM-RM, 1000)[1] + f.getSpaceBefore() + f.getSpaceAfter() for f in tfl) + 0.35*cm
    first = PageTemplate("first", [Frame(LM, H-TM-ttl, W-LM-RM, ttl, id="t", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
        Frame(LM, BM, CW, fh-ttl, id="l1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
        Frame(LM+CW+GAP, BM, CW, fh-ttl, id="r1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)
    later = PageTemplate("later", [Frame(LM, BM, CW, fh, id="l", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
        Frame(LM+CW+GAP, BM, CW, fh, id="r", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)
    doc.addPageTemplates([first, later])
    items = []   # (kind, flowable)
    for bi_, bk in enumerate(C.B):
        k = bk[0]
        if k == "h1": items.append(("h", Paragraph(bk[1], S["h1"])))
        elif k == "h2": items.append(("h", Paragraph(bk[1], S["h2"])))
        elif k == "p": items.append(("p", mk(bk[1])))
        elif k == "eq":
            t = Table([[Paragraph(bk[1], S["eq"]), Paragraph(bk[2], S["body"])]], colWidths=[CW-1.0*cm, 1.0*cm]); t.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("TOPPADDING", (0,0), (-1,-1), 1), ("BOTTOMPADDING", (0,0), (-1,-1), 3)])); items.append(("t", t))
        elif k == "fig":
            w = min(bk[3]*FS*cm, CW); iw, ih = PI.open(bk[1]).size
            items.append(("f", Group([Image(bk[1], width=w, height=w*ih/iw), Paragraph(bk[2], S["cap"])])))
        elif k == "table":
            cap, head, rows, cw = bk[1], bk[2], bk[3], bk[4]; boldrow = bk[5] if len(bk) > 5 else None
            data = [[Paragraph(h, S["cellb"]) for h in head]] + [[Paragraph(str(x), S["cell"]) for x in r] for r in rows]
            if boldrow:
                bi = min(range(3, 8), key=lambda i: float(rows[i][2])); data[bi+1] = [Paragraph(str(x), S["cellb"]) for x in rows[bi]]
            sc = CW / (sum(cw)*cm); t = Table(data, colWidths=[c*cm*sc for c in cw], repeatRows=1)
            t.setStyle(TableStyle([("LINEABOVE", (0,0), (-1,0), .8, NAVY), ("LINEBELOW", (0,0), (-1,0), .5, NAVY), ("LINEBELOW", (0,-1), (-1,-1), .8, NAVY),
                                   ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8edf5")), ("TOPPADDING", (0,0), (-1,-1), 1.4), ("BOTTOMPADDING", (0,0), (-1,-1), 1.4), ("LEFTPADDING", (0,0), (-1,-1), 2.5), ("RIGHTPADDING", (0,0), (-1,-1), 2.5), ("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
            items.append(("f", Group([Paragraph(cap, S["tcap"]), t, Spacer(1, 5)])))
    items.append(("h", Paragraph("References", S["h1"])))
    for i, r in enumerate(C.REFS, 1): items.append(("p", Paragraph(f"[{i}] " + r, S["ref"])))
    title, head, rows = C.APPX
    items.append(("h", Paragraph(title, S["h1"])))
    items.append(("p", Paragraph("Validation scores (fit on a Month_1 subset, evaluated on a Month_2 subset) for every grid setting; the test month was not used.", S["tcap"])))
    data = [[Paragraph(h, S["cellb"]) for h in head]] + [[Paragraph(str(x), S["cell"]) for x in r] for r in rows]
    cw = [2.3, 2.9, 1.0, 1.1, 1.0]; sc = CW / (sum(cw)*cm); t = Table(data, colWidths=[c*cm*sc for c in cw])
    t.setStyle(TableStyle([("LINEABOVE", (0,0), (-1,0), .8, NAVY), ("LINEBELOW", (0,0), (-1,0), .5, NAVY), ("LINEBELOW", (0,-1), (-1,-1), .8, NAVY), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8edf5")),
                           ("TOPPADDING", (0,0), (-1,-1), .8), ("BOTTOMPADDING", (0,0), (-1,-1), .8), ("LEFTPADDING", (0,0), (-1,-1), 2), ("RIGHTPADDING", (0,0), (-1,-1), 2)]))
    items.append(("f", Group([t])))
    tB, capB, headB, rowsB = C.APPX_B
    items.append(("h", Paragraph(tB, S["h1"]))); items.append(("p", Paragraph(capB, S["tcap"])))
    dB = [[Paragraph(h, S["cellb"]) for h in headB]] + [[Paragraph(str(x), S["cell"]) for x in r] for r in rowsB]
    tb = Table(dB, colWidths=[CW*0.3, CW*0.35, CW*0.35]); tb.setStyle(TableStyle([("LINEABOVE", (0,0), (-1,0), .8, NAVY), ("LINEBELOW", (0,0), (-1,0), .5, NAVY), ("LINEBELOW", (0,-1), (-1,-1), .8, NAVY), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#e8edf5")), ("TOPPADDING", (0,0), (-1,-1), .6), ("BOTTOMPADDING", (0,0), (-1,-1), .6), ("LEFTPADDING", (0,0), (-1,-1), 2)]))
    items.append(("f", Group([tb])))
    items.append(("h", Paragraph(C.APPX_C[0], S["h1"]))); items.append(("p", Paragraph(C.APPX_C[1], ParagraphStyle("al", parent=S["body"], alignment=TA_LEFT))))
    # ---- greedy column packer: figures/tables float to the next column if they do not fit; text fills the gap
    SAFE = 3.0
    frame_h = [fh - ttl - 0.0, fh - ttl] + [fh, fh] * 10
    def hh(fl):
        if isinstance(fl, Group): return fl.height()
        w, h = fl.wrap(CW, 10**6); return h + fl.getSpaceBefore() + fl.getSpaceAfter()
    out, pending, fi, avail, top = [FrameBreak(), NextPageTemplate("later")][:0], [], 0, frame_h[0] - SAFE, True
    out = []
    def newframe():
        nonlocal fi, avail, top
        out.append(FrameBreak()); fi += 1; avail = frame_h[fi] - SAFE; top = True
        keep = []
        for fl in pending:
            h = hh(fl)
            if h <= avail: out.append(fl); avail -= h; top = False
            else: keep.append(fl)
        pending[:] = keep
    queue = list(items); qi = 0
    while qi < len(queue):
        kind, fl = queue[qi]; h = hh(fl)
        if kind in ("f", "t"):
            if h <= avail: out.append(fl); avail -= h; top = False
            else: pending.append(fl)
            qi += 1; continue
        need = h + (2.4*BASE*LD if kind == "h" else 0)       # headings keep company with the next lines
        if kind == "h":
            if need <= avail: out.append(fl); avail -= h; top = False; qi += 1
            else: newframe()
            continue
        if h <= avail: out.append(fl); avail -= h; top = False; qi += 1; continue
        parts = fl.split(CW, avail) if avail > 3*BASE*LD else []
        if len(parts) == 2: out.append(parts[0]); queue[qi] = ("p", parts[1]); newframe()
        else: newframe()
    while pending: newframe()
    st = tfl + [FrameBreak(), NextPageTemplate("later")] + out
    doc.build(st); return doc.page
if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else str(OUT / "paper.pdf"); print("pages:", build(out))
