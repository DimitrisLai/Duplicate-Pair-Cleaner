#!/usr/bin/env python3
"""Build the downloadable Windows ZIP and printable PDF user manual.

Release-builder dependency: ReportLab. The cleaner itself uses only stdlib.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
import re

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "dist"
VERSION = "2.2.0"
FILES = [
    "file_pair_cleaner.py", "Run_Cleaner.bat", "Preview_Only.bat",
    "README.md", "LICENSE", "CHANGELOG.md", "SECURITY.md",
    "docs/USER_GUIDE.md", "docs/EXAMPLE_PREVIEW.txt",
]

def make_zip(pdf):
    target = DEST / f"Duplicate-Pair-Cleaner-v{VERSION}-Windows.zip"
    with ZipFile(target, "w", ZIP_DEFLATED, compresslevel=9) as z:
        for rel in FILES:
            z.write(ROOT / rel, rel)
        z.write(pdf, "docs/" + pdf.name)
    return target

def make_pdf():
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

    target = DEST / f"Duplicate-Pair-Cleaner-v{VERSION}-User-Manual.pdf"
    navy = colors.HexColor("#172A42")
    blue = colors.HexColor("#287CB2")
    grey = colors.HexColor("#526274")
    body = ParagraphStyle("Body", fontName="Helvetica", fontSize=10.2,
                          leading=15.3, textColor=navy, spaceAfter=9)
    heading = ParagraphStyle("Heading", parent=body, fontName="Helvetica-Bold",
                             fontSize=15, leading=20, spaceBefore=17,
                             spaceAfter=10, textColor=blue)
    note = ParagraphStyle("Note", parent=body, fontSize=9.3, leading=14,
                          leftIndent=12)
    code = ParagraphStyle("Code", parent=body, fontName="Courier", fontSize=8.7,
                          leading=13, textColor=grey, leftIndent=9)
    title = ParagraphStyle("Cover", parent=body, fontName="Helvetica-Bold",
                           fontSize=31, leading=39, textColor=navy, spaceAfter=15)
    subtitle = ParagraphStyle("Subtitle", parent=body, fontSize=15.5,
                              leading=24, textColor=grey)

    def footer(canvas, doc):
        canvas.saveState()
        w, h = A4
        canvas.setStrokeColor(colors.HexColor("#DBE4EF"))
        canvas.line(22 * mm, 17.8 * mm, w - 22 * mm, 17.8 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(grey)
        canvas.drawString(22 * mm, 13.4 * mm, "DUPLICATE PAIR CLEANER | VERSION " + VERSION)
        canvas.drawRightString(w - 22 * mm, 13.4 * mm, f"{doc.page:02d}")
        canvas.restoreState()

    def markup(value):
        value = escape(value).replace(chr(96), "")
        return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)

    doc = SimpleDocTemplate(str(target), pagesize=A4, leftMargin=22 * mm,
                            rightMargin=22 * mm, topMargin=21 * mm,
                            bottomMargin=24 * mm,
                            title="Duplicate Pair Cleaner - User Manual",
                            author="DimitrisLai")
    story = [
        Spacer(1, 16 * mm),
        Paragraph("DUPLICATE<br/>PAIR CLEANER", title),
        HRFlowable(width="42%", thickness=3, color=blue,
                   spaceBefore=5, spaceAfter=20),
        Paragraph("Your files, your rules.<br/>Keep the right copy and its companion.", subtitle),
        Spacer(1, 15 * mm),
        Paragraph("<b>PUBLIC USER MANUAL</b> | v2.2.0 | Python 3.10+", body),
        Paragraph("Choose two file types, preview every change in groups, then clean numbered duplicates with a dated backup by default.", body),
        Paragraph("MP3/LRC, MP4/SRT, JPG/XMP, and other file pairs.", body),
        Spacer(1, 22 * mm),
        Paragraph("<b>Open-source utility by DimitrisLai</b>", body),
        Paragraph("github.com/DimitrisLai/Duplicate-Pair-Cleaner", note),
    ]
    lines = (ROOT / "docs/USER_GUIDE.md").read_text(encoding="utf-8").splitlines()
    for line in lines[2:]:
        value = line.strip()
        if not value:
            story.append(Spacer(1, 4))
        elif value.startswith("## "):
            story.append(Paragraph(markup(value[3:]), heading))
        elif value.startswith("### "):
            story.append(Paragraph(markup(value[4:]), heading))
        elif value.startswith(chr(96) * 3) or value.startswith("~~~"):
            continue
        elif value.startswith("- "):
            story.append(Paragraph("&#8226; " + markup(value[2:]), note))
        else:
            style = code if value.startswith("python ") else body
            story.append(Paragraph(markup(value), style))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return target

if __name__ == "__main__":
    DEST.mkdir(exist_ok=True)
    pdf = make_pdf()
    archive = make_zip(pdf)
    print("PDF:", pdf, pdf.stat().st_size, "bytes")
    print("ZIP:", archive, archive.stat().st_size, "bytes")
