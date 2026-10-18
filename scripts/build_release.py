#!/usr/bin/env python3
"""Build a polished 9-page PDF manual and the public Windows ZIP (CI only).

ReportLab is only needed by this release builder; the cleaner remains stdlib-only.
"""
from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table,
    TableStyle, Preformatted, KeepTogether,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist"
VERSION = "2.2.0"
NAME = "Duplicate Pair Cleaner"
REPO = "github.com/DimitrisLai/Duplicate-Pair-Cleaner"
NAVY = colors.HexColor("#0B1528")
INK = colors.HexColor("#16233A")
MUTED = colors.HexColor("#536277")
TEAL = colors.HexColor("#0B9C91")
LIGHT = colors.HexColor("#EAF0FB")
PALETEAL = colors.HexColor("#E9F7F5")
LINE = colors.HexColor("#DCE4EC")
W, H = A4

def fonts():
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/local/share/fonts"),
    ]
    for folder in candidates:
        if (folder / "DejaVuSans.ttf").exists():
            pdfmetrics.registerFont(TTFont("ManualSans", str(folder / "DejaVuSans.ttf")))
            pdfmetrics.registerFont(TTFont("ManualBold", str(folder / "DejaVuSans-Bold.ttf")))
            pdfmetrics.registerFont(TTFont("ManualMono", str(folder / "DejaVuSansMono.ttf")))
            return
    raise RuntimeError("DejaVu fonts not found on build runner")

def p(text, style="body"):
    return Paragraph(text, STYLES[style])

def h1(text):
    return p(text, "h1")

def h2(text):
    return p(text, "h2")

def h3(text):
    return p(text, "h3")

def bullet(text):
    return p("&#8226; " + text, "bullet")

def panel(title, body, bg=PALETEAL):
    t = Table([[h3(title)], [p(body, "small")]], colWidths=[490])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), bg),
        ("BOX", (0,0),(-1,-1), 0.35, LINE),
        ("LEFTPADDING",(0,0),(-1,-1),12),
        ("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,0),7),
        ("BOTTOMPADDING",(0,0),(-1,0),0),
        ("TOPPADDING",(0,1),(-1,1),0),
        ("BOTTOMPADDING",(0,1),(-1,1),8),
    ]))
    return t

def code(value):
    mono = Preformatted(value.strip("\n"), STYLES["mono"], maxLineLength=83)
    t = Table([[mono]], colWidths=[490])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),LIGHT),
        ("BOX",(0,0),(-1,-1),0.4,LINE),
        ("LEFTPADDING",(0,0),(-1,-1),13),
        ("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,-1),12),
        ("BOTTOMPADDING",(0,0),(-1,-1),12),
    ]))
    return t

def grid(rows, widths=None):
    cells = [
        [p(escape(str(v)), "cellhead" if i == 0 else "cell")
         for v in row]
        for i, row in enumerate(rows)
    ]
    t = Table(cells, colWidths=widths or [490 / len(rows[0])] * len(rows[0]), repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),
         [colors.white,colors.HexColor("#F4F7FA")]),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),9),
        ("RIGHTPADDING",(0,0),(-1,-1),9),
        ("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LINEBELOW",(0,-1),(-1,-1),0.3,LINE),
    ]))
    return t

def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0,0,W,H,fill=1,stroke=0)
    canvas.setFillColor(colors.HexColor("#102947"))
    canvas.circle(W+20,H-150,220,fill=1,stroke=0)
    canvas.setFillColor(colors.HexColor("#133F4B"))
    canvas.circle(W-30,-15,185,fill=1,stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0,H-12*mm,W,12*mm,fill=1,stroke=0)
    canvas.setFillColor(colors.HexColor("#28C4B6"))
    canvas.setFont("ManualBold",10)
    canvas.drawString(22*mm,33*mm,"v2.2.0  /  OPEN SOURCE  /  PYTHON 3.10+")
    canvas.setFillColor(colors.HexColor("#C1D5DF"))
    canvas.setFont("ManualSans",8.8)
    canvas.drawString(22*mm,22*mm,REPO)
    canvas.restoreState()

def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0,H-17*mm,W,17*mm,fill=1,stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("ManualBold",8)
    canvas.drawString(18*mm,H-10*mm,"DUPLICATE PAIR CLEANER")
    canvas.setFillColor(colors.HexColor("#B6D7DB"))
    canvas.setFont("ManualSans",8)
    canvas.drawRightString(W-18*mm,H-10*mm,"USER MANUAL  /  v2.2.0")
    canvas.setStrokeColor(LINE)
    canvas.line(18*mm,14*mm,W-18*mm,14*mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("ManualSans",7.7)
    canvas.drawString(18*mm,10*mm,"DimitrisLai / Duplicate-Pair-Cleaner  /  MIT License")
    canvas.drawRightString(W-18*mm,10*mm,f"{doc.page:02d}")
    canvas.restoreState()

def styles():
    global STYLES
    STYLES = {}
    STYLES["body"] = ParagraphStyle("manual-body",fontName="ManualSans",
        fontSize=9.4,leading=15,textColor=INK,spaceAfter=8)
    STYLES["small"] = ParagraphStyle("manual-small",parent=STYLES["body"],
        fontSize=8,leading=12,spaceAfter=5)
    STYLES["h1"] = ParagraphStyle("manual-h1",fontName="ManualBold",
        fontSize=22,leading=29,textColor=NAVY,spaceAfter=13)
    STYLES["h2"] = ParagraphStyle("manual-h2",fontName="ManualBold",
        fontSize=12,leading=18,textColor=NAVY,spaceBefore=12,spaceAfter=7)
    STYLES["h3"] = ParagraphStyle("manual-h3",fontName="ManualBold",
        fontSize=9.8,leading=15,textColor=TEAL,spaceBefore=8,spaceAfter=4)
    STYLES["cell"] = ParagraphStyle("manual-cell",fontName="ManualSans",
        fontSize=8,leading=12,textColor=INK)
    STYLES["cellhead"] = ParagraphStyle("manual-cellhead",fontName="ManualBold",
        fontSize=8,leading=12,textColor=colors.white)
    STYLES["mono"] = ParagraphStyle("manual-mono",fontName="ManualMono",
        fontSize=7.7,leading=12,textColor=NAVY)
    STYLES["bullet"] = ParagraphStyle("manual-bullet",parent=STYLES["body"],
        leftIndent=14,firstLineIndent=-10,spaceAfter=5)
    STYLES["coverk"] = ParagraphStyle("manual-coverk",fontName="ManualBold",
        fontSize=11,leading=16,textColor=colors.HexColor("#4ADACD"),spaceAfter=18)
    STYLES["covert"] = ParagraphStyle("manual-covert",fontName="ManualBold",
        fontSize=36,leading=45,textColor=colors.white,spaceAfter=18)
    STYLES["coverb"] = ParagraphStyle("manual-coverb",fontName="ManualSans",
        fontSize=13,leading=21,textColor=colors.HexColor("#D6E5F0"),spaceAfter=18)
    STYLES["covers"] = ParagraphStyle("manual-covers",fontName="ManualSans",
        fontSize=9,leading=15,textColor=colors.HexColor("#B7CEDD"))

def make_manual():
    fonts()
    styles()
    dest = OUT / f"Duplicate-Pair-Cleaner-v{VERSION}-User-Manual.pdf"
    doc = SimpleDocTemplate(str(dest),pagesize=A4,
        leftMargin=18*mm,rightMargin=18*mm,topMargin=25*mm,bottomMargin=22*mm,
        title="Duplicate Pair Cleaner - User Manual v2.2.0",
        subject="A nine-page illustrated guide with safety and usage instructions",
        author="DimitrisLai")
    s = [
        Spacer(1,57*mm),
        p("USER MANUAL  /  OCTOBER 2026","coverk"),
        p("Duplicate<br/>Pair Cleaner","covert"),
        p("Keep the right copy.<br/>Keep its matching companion.<br/>Review everything before making changes.","coverb"),
        Spacer(1,19*mm),
        p("Windows folder picker  /  Grouped preview  /  Backups by default","covers"),
        PageBreak(),
    ]
    # Page 2: Getting started
    s += [
        h1("01  /  Get started"),
        p("Duplicate Pair Cleaner removes unnecessary <b>numbered filename variants</b> such as (1) and (2), while preferring a version that has the corresponding companion file."),
        panel("REQUIREMENTS","Windows with <b>Python 3.10+</b>. No additional Python packages. The script also works from a terminal on macOS/Linux."),
        h2("Six easy steps"),
        bullet("<b>Download</b> the Windows ZIP from the GitHub Releases page, then extract all files."),
        bullet("<b>Double-click Preview_Only.bat</b> to inspect changes without modifying your selected file pairs."),
        bullet("<b>Select a folder</b> with the Windows folder picker; no copying the program into every directory."),
        bullet("<b>Choose two extensions</b>, or press Enter to use .mp3 and .lrc."),
        bullet("<b>Choose subfolders</b> if needed. Each folder is processed independently."),
        bullet("<b>Review the report</b>. When satisfied, launch Run_Cleaner.bat and type YES to apply."),
        h2("Two launchers, two purposes"),
        grid([["Launcher","What it does"],
              ["Preview_Only.bat","Generates a text report with no selected file pairs modified."],
              ["Run_Cleaner.bat","Shows grouped decisions; changes files only after an exact YES."]],[148,342]),
        Spacer(1,10),
        panel("START SAFELY","Run the preview first, and keep a separate backup of important files.",LIGHT),
        PageBreak(),
    ]
    # Page 3: Grouped preview
    s += [
        h1("02  /  Understand the preview"),
        p("Every proposed change appears in a separate group for one base filename, even when copies use different capitalization."),
        code("""GROUP 001/001 | Song
Why: Keeping the main file with its matching companion.
CURRENT FILES / DECISIONS:
  [BACKUP] Song.mp3
  [RENAME] Song(1).mp3
           -> Song.mp3
  [RENAME] Song(1).lrc
           -> Song.lrc
AFTER CLEANUP:
  [MAIN .mp3] Song.mp3
  [PAIR .lrc] Song.lrc"""),
        h2("What each label means"),
        grid([["Label","Meaning"],
              ["[KEEP]","Stays in place, with the same name."],
              ["[BACKUP]","Extra copy is moved to a dated backup folder."],
              ["[RENAME]","Selected file receives its final clean filename."]],[140,350]),
        h2("Review controls"),
        grid([["Key","Action"],
              ["Enter","Show the next five groups"],
              ["A","Show all remaining groups"],
              ["Q","Cancel without applying changes"],
              ["YES","Approve after review (uppercase, exact match)"]],[140,350]),
        PageBreak(),
    ]
    # Page 4: Selection logic
    s += [
        h1("03  /  How the cleaner decides"),
        p("The <b>main file</b> is the one you want to preserve, and the <b>companion</b> is a matching sidecar such as lyrics, subtitles, or metadata."),
        h2("Priority order"),
        bullet("Prefer a main file with a companion of the same copy number."),
        bullet("If several complete pairs exist, choose the unnumbered pair; otherwise the lowest copy number."),
        bullet("If no matched pair exists, prefer the unnumbered main file (or lowest numbered copy)."),
        bullet("Keep at most one available companion; renamed main and companion receive matching base names."),
        h2("Example A - only the numbered copy has lyrics"),
        code("""Before:                     After:
Song.mp3                    Song.mp3  <- from Song(1).mp3
Song(1).mp3                 Song.lrc
Song(1).lrc
Original Song.mp3 is backed up."""),
        h2("Example B - both copies have lyrics"),
        code("""Before:                     After:
Song.mp3                    Song.mp3
Song.lrc                    Song.lrc
Song(1).mp3
Song(1).lrc
Both numbered files are backed up."""),
        h2("Example C - no companion"),
        p("Song.mp3 + Song(1).mp3 becomes just Song.mp3. The numbered MP3 is backed up."),
        PageBreak(),
    ]
    # Page 5: File patterns
    s += [
        h1("04  /  Supported filename patterns"),
        grid([["Main extension","Companion","Typical scenario"],
              [".mp3",".lrc","Music and synced lyrics (default)"],
              [".mp4",".srt","Video files and subtitles"],
              [".flac",".lrc","Lossless music and lyrics"],
              [".jpg",".xmp","Photographs and metadata sidecars"],
              [".wav",".txt","Audio recordings and notes"]],[124,124,242]),
        h2("Suffixes recognized"),
        p("The program recognizes a positive 1-to-3-digit copy number in final parentheses as a duplicate suffix: Song(1), Song (2), or Song(123). Capitalization does not affect matching."),
        h2("Suffixes deliberately ignored"),
        p("Song (Live), Song (2026), and other descriptive parentheses within the filename are <b>not</b> considered duplicates. A single numbered main file or a single complete numbered pair is left alone to avoid renaming legitimate titles."),
        panel("NOT CONTENT DEDUPLICATION",
              "The app does not read file hashes, audio quality, subtitles, or metadata. Files with the same base name might be different recordings, edits, or releases.",LIGHT),
        h2("Recursive scanning"),
        p("When enabled, every directory is a separate workspace. Album A/Song.mp3 is never mixed with Album B/Song.mp3. Existing backup folders and common development folders are excluded."),
        PageBreak(),
    ]
    # Page 6: Backup
    s += [
        h1("05  /  Backups and recovery"),
        p("By default, unnecessary files are <b>moved, not permanently deleted</b>. A new dated backup folder is created in the selected directory for every applied cleanup."),
        code("""Music/
  Song.mp3
  Song.lrc
  _File_Pair_Cleaner_Backup_20261018_213000_123456/
     manifest.json
     duplicates/
        Song.mp3   <- original extra file"""),
        h2("What is manifest.json?"),
        p("This file records the originals, backup locations, and final renamed paths. Keep it if you need to restore items manually."),
        h2("Manual restoration"),
        bullet("Close programs that might be using the directory."),
        bullet("Open the backup folder and read manifest.json."),
        bullet("Check whether a final filename is occupied; move or rename the survivor first if needed."),
        bullet("Copy backed-up items from the duplicates directory back to the recorded original paths."),
        panel("SAFETY NOTE",
              "There is no one-click restore tool. Automatic rollback is attempted after normal errors and Ctrl+C, but sudden power loss or unusual filesystem conditions can require manual recovery. Do not delete backups until you have checked the results.",LIGHT),
        PageBreak(),
    ]
    # Page 7: CLI
    s += [
        h1("06  /  Command-line use"),
        p("Windows users can use the BAT launchers. Python also offers a direct command line for automation or other operating systems."),
        h2("Preview a folder"),
        code('python file_pair_cleaner.py --folder "C:/My Music" --preview'),
        h2("Preview videos and subtitles, including subfolders"),
        code('python file_pair_cleaner.py --folder "C:/Videos" --main-ext mp4 --companion-ext srt --recursive --preview'),
        h2("Run with the Windows folder picker"),
        code("python file_pair_cleaner.py --select-folder --ask-extensions --ask-subfolders"),
        h2("Save a complete text report"),
        code('python file_pair_cleaner.py --folder "C:/My Music" --preview --save-report preview.txt'),
        h2("Help, version, and tests"),
        code("""python file_pair_cleaner.py --help
python file_pair_cleaner.py --version
python -m unittest -v test_cleaner.py"""),
        panel("ADVANCED FLAGS",
              "The --apply option skips interactive confirmation; --permanent removes backups after successful cleanup. Neither option is enabled by the supplied Windows launchers.",LIGHT),
        PageBreak(),
    ]
    # Page 8: troubleshooting
    s += [
        h1("07  /  Troubleshooting"),
        grid([["Symptom","What to check"],
              ["Python not found","Install Python 3.10+; try py -3 or python in Command Prompt."],
              ["Folder picker does not open","Install Tkinter for your Python build or supply --folder."],
              ["No duplicate groups found","Check extensions and whether names end with (1) or (2)."],
              ["Unexpected group skipped","Read warnings for case collisions or destination conflicts."],
              ["Access denied or file in use","Close editors/players, review permissions, rescan."],
              ["Need to undo an operation","Consult the dated backup and manifest.json."]],[166,324]),
        h2("Frequently asked questions"),
        h3("Will it compare MP3 contents or bitrate?"),
        p("No. Selection follows filenames and matching companion availability only."),
        h3("Will it rename a lone Song(1).mp3?"),
        p("No. It requires sufficient duplicate variants to justify changing the name."),
        h3("Can an unnumbered original be backed up?"),
        p("Yes, when a numbered copy has a matching companion and wins the selection. Inspect the preview first."),
        PageBreak(),
    ]
    # Page 9: Project
    s += [
        h1("08  /  Project information"),
        p("<b>Project:</b> Duplicate Pair Cleaner"),
        p("<b>Version:</b> 2.2.0   /   <b>Python:</b> 3.10+   /   <b>Runtime dependencies:</b> standard library only"),
        p('<b>GitHub:</b> <link href="https://github.com/DimitrisLai/Duplicate-Pair-Cleaner" color="#0B9C91">github.com/DimitrisLai/Duplicate-Pair-Cleaner</link>'),
        h2("MIT open-source license"),
        p("Copyright (c) 2026 DimitrisLai. You may use, copy, modify and distribute the software under the included LICENSE terms. The program is provided without warranty."),
        h2("Contributing and issue reports"),
        p("Report problems through GitHub Issues, using invented filenames rather than private personal files, file paths, or complete music inventories."),
        h2("Validated for this release"),
        bullet("Automated cross-platform tests for pair selection, backups, folder options, conflicts, and simulated failures."),
        bullet("A documented read-only preview and optional real cleanup with exact YES confirmation."),
        bullet("Published release ZIP and PDF manual, assembled from repository sources."),
        panel("WINDOWS DISCLAIMER",
              "Automated tests run on Windows and Linux. Actual double-click behavior and the graphical folder picker should also be smoke-tested on a real Windows desktop.",LIGHT),
        Spacer(1,16),
        p("Duplicate Pair Cleaner   /   v2.2.0   /   Safe, transparent file-pair cleanup by default.","small"),
    ]
    doc.build(s,onFirstPage=draw_cover,onLaterPages=draw_page)
    return dest

def make_zip(pdf):
    dest = OUT / f"Duplicate-Pair-Cleaner-v{VERSION}-Windows.zip"
    relpaths = [
        "file_pair_cleaner.py", "Run_Cleaner.bat", "Preview_Only.bat",
        "README.md", "LICENSE", "CHANGELOG.md", "SECURITY.md",
        "docs/USER_GUIDE.md", "docs/EXAMPLE_PREVIEW.txt",
    ]
    with ZipFile(dest, "w", ZIP_DEFLATED, compresslevel=9) as z:
        for rel in relpaths:
            z.write(ROOT / rel, rel)
        z.write(pdf, "docs/" + pdf.name)
    return dest

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    manual = make_manual()
    package = make_zip(manual)
    print(f"PDF: {manual} ({manual.stat().st_size} bytes)")
    print(f"ZIP: {package} ({package.stat().st_size} bytes)")
