#!/usr/bin/env python3
"""Build an editorial A4 PDF handbook. ReportLab is a build-time dependency only."""
from __future__ import annotations
from pathlib import Path
from textwrap import wrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'dist'
OUT.mkdir(exist_ok=True)
PDF=OUT/'Duplicate-Pair-Cleaner-v3.5.0-User-Manual.pdf'
W,H=A4
NAVY=HexColor('#0B172B');DARK=HexColor('#142A43');TEAL=HexColor('#07988B')
INK=HexColor('#1A2B3F');MUTED=HexColor('#66788B');PALE=HexColor('#F2F6F8')
BORDER=HexColor('#DAE3EA');CYAN=HexColor('#45C6B7')

folder=Path('/usr/share/fonts/truetype/dejavu')
if (folder/'DejaVuSans.ttf').exists():
    pdfmetrics.registerFont(TTFont('DPC',(folder/'DejaVuSans.ttf').as_posix()))
    pdfmetrics.registerFont(TTFont('DPC-Bold',(folder/'DejaVuSans-Bold.ttf').as_posix()))
    pdfmetrics.registerFont(TTFont('DPC-Mono',(folder/'DejaVuSansMono.ttf').as_posix()))
    REG='DPC';BOLD='DPC-Bold';MONO='DPC-Mono'
else:
    REG='Helvetica';BOLD='Helvetica-Bold';MONO='Courier'

c=canvas.Canvas(PDF.as_posix(),pagesize=A4,pageCompression=1)
c.setTitle('Duplicate Pair Cleaner v3.5.0 — Windows GUI User Manual')
c.setAuthor('DimitrisLai')
c.setSubject('Complete illustrated manual for the final Duplicate Pair Cleaner Windows GUI')
LEFT=46;RIGHT=W-46;WIDTH=RIGHT-LEFT


def label(x,y,text,size=9,color=INK,bold=False):
    c.setFillColor(color);c.setFont(BOLD if bold else REG,size);c.drawString(x,y,text)

def para(text,x,y,width=WIDTH,size=9.5,leading=16,color=INK,bold=False):
    sty=ParagraphStyle('p',fontName=BOLD if bold else REG,fontSize=size,leading=leading,textColor=color)
    obj=Paragraph(text,sty);_,height=obj.wrap(width,650);obj.drawOn(c,x,y-height);return y-height-7

def panel(x,y,width,height,fill=PALE,stroke=BORDER,r=8):
    c.setStrokeColor(stroke);c.setFillColor(fill);c.roundRect(x,y,width,height,r,stroke=1,fill=1)

def rule(y):
    c.setStrokeColor(BORDER);c.setLineWidth(.7);c.line(LEFT,y,RIGHT,y)

def header(num,title,kicker):
    c.setFillColor(NAVY);c.rect(0,H-67,W,67,fill=1,stroke=0)
    label(LEFT,H-26,'DUPLICATE PAIR CLEANER',10,white,True)
    label(RIGHT-119,H-26,'WINDOWS GUI   ·   v3.5.0',7.6,CYAN)
    label(LEFT,H-109,kicker.upper(),8,TEAL,True)
    label(LEFT,H-145,title,21,NAVY,True)
    c.setStrokeColor(TEAL);c.setLineWidth(2.1);c.line(LEFT,H-158,LEFT+61,H-158)
    c.setStrokeColor(BORDER);c.setLineWidth(.5);c.line(LEFT,45,RIGHT,45)
    label(LEFT,29,'github.com/DimitrisLai/Duplicate-Pair-Cleaner',7.6,MUTED)
    label(RIGHT-25,29,f'{num:02d} / 09',8,MUTED,True)

def new_page():
    c.showPage()

def info_box(y,headline,body,fill=PALE,height=89):
    panel(LEFT,y-height,WIDTH,height,fill=fill)
    label(LEFT+14,y-24,headline,11,TEAL,True)
    return para(body,LEFT+14,y-33,WIDTH-30,8.8,13,INK)

def section(y,title,body):
    label(LEFT,y,title,11,TEAL,True)
    return para(body,LEFT,y-9,WIDTH,9.3,15)-14

def codepanel(y,text,height=84):
    panel(LEFT,y-height,WIDTH,height,PALE)
    for i,line in enumerate(text.splitlines()):
        label(LEFT+15,y-22-i*14,line,8.7,INK,False)
    return y-height-14

# Page 1 / branded cover
c.setFillColor(NAVY);c.rect(0,0,W,H,stroke=0,fill=1)
c.setFillColor(DARK);c.circle(W+55,H-155,244,stroke=0,fill=1)
c.setFillColor(HexColor('#0F4852'));c.circle(W-5,-80,205,stroke=0,fill=1)
c.setFillColor(TEAL);c.rect(0,H-18,W,18,stroke=0,fill=1)
label(LEFT,H-128,'USER HANDBOOK  /  FINAL GUI RELEASE',11,CYAN,True)
label(LEFT,H-235,'DUPLICATE',35,white,True)
label(LEFT,H-285,'PAIR CLEANER',35,white,True)
label(LEFT,H-342,'Keep the right copy.',16,white)
label(LEFT,H-372,'Keep its matching companion.',16,white)
label(LEFT,H-407,'Review changes before they happen.',11,HexColor('#B9CCD7'))
rule_color=HexColor('#4B8089');c.setStrokeColor(rule_color);c.setLineWidth(2);c.line(LEFT,H-457,LEFT+110,H-457)
label(LEFT,H-493,'REAL WINDOWS DESKTOP APP',9,CYAN,True)
label(LEFT,H-513,'Folder browser  /  Grouped previews  /  Safe backups',9,HexColor('#C8DBE4'))
label(LEFT,91,'VERSION 3.5.0    ·    OCTOBER 2026    ·    MIT LICENSE',9,CYAN,True)
label(LEFT,66,'Created by DimitrisLai',9,HexColor('#D2E4EA'))
new_page()

# Page 2
header(2,'Welcome to the new interface','what has changed')
y=H-190
y=para('Duplicate Pair Cleaner is now a <b>graphical Windows application</b>. It keeps the selected file and its optional matching companion, even when that means replacing the unnumbered copy with the one that has lyrics.',LEFT,y,size=10,leading=17)-13
label(LEFT,y,'THE ACTUAL APPLICATION',10,TEAL,True)
y-=21
image=ROOT/'assets'/'GUI_Preview.webp'
if image.is_file():
    height=WIDTH*900/1180
    panel(LEFT,y-height-7,WIDTH,height+14,white)
    c.drawImage(ImageReader(image.as_posix()),LEFT+4,y-height+4,width=WIDTH-8,height=height-8,preserveAspectRatio=False,mask='auto')
    y-=height+24
else:
    y=info_box(y,'GUI screenshot', 'The live application preview is embedded in the source release.',height=70)-25
y=para('<b>Visual walkthrough:</b> the upper section selects the folder and extensions. The Light-theme screenshot shows file groups, backups, renames and warnings. Use the Appearance dropdown for Dark or System mode. The lower section shows group decisions; Include/Exclude controls protect selected groups. The bottom bar supports Preview, Cancel scan, Export and Apply.',LEFT,y,size=8.9,leading=15)
new_page()

# Page 3
header(3,'Install and launch','quick start')
y=H-184
y=info_box(y,'NO PYTHON INSTALLATION REQUIRED','The Windows portable ZIP contains a compiled executable and its support files. Extract everything first, then start the EXE.',height=86)-25
for idx,(title,body) in enumerate([
('Download the portable ZIP','Open GitHub v3.5.0 Releases and download the Windows-Portable ZIP.'),
('Extract all files','Right-click the ZIP and choose Extract All. Keep the DuplicatePairCleaner folder intact.'),
('Launch the application','Double-click DuplicatePairCleaner.exe inside the extracted DuplicatePairCleaner folder.'),
('Choose your folder','Click Browse or paste a path. Your last valid folder and extensions are remembered.'),
('Select file types','Use a preset or custom file types. Subfolders are optional. Choose Light, Dark or System in the header.'),
('Preview, then confirm','Click Scan & preview, exclude groups if needed, then confirm cleanup.')],1):
    c.setFillColor(TEAL);c.circle(LEFT+11,y-9,11,stroke=0,fill=1)
    label(LEFT+7.5,y-12,str(idx),9,white,True)
    label(LEFT+32,y-3,title,11,NAVY,True)
    y=para(body,LEFT+32,y-13,WIDTH-38,9.1,15)-13
info_box(y+3,'WINDOWS SECURITY NOTE','This is an unsigned open-source build. If Windows warns about an unknown publisher, confirm that the file came from the verified GitHub release and review the source before running it.',height=89)
new_page()

# Page 4
header(4,'Select the right file types','configure')
y=H-188
y=para('The <b>Main extension</b> is what you want to keep: music, video, photo, or recording. The <b>Companion extension</b> is its matching file, such as lyrics, subtitles, XMP metadata or notes.',LEFT,y,size=10,leading=17)-26
rows=[('.mp3','.lrc','Music and synchronized lyrics'),('.mp4','.srt','Video and subtitles'),('.flac','.lrc','Lossless music and lyrics'),('.jpg','.xmp','Photos and metadata'),('.wav','.txt','Audio recordings and notes')]
for i,(a,b,desc) in enumerate(rows):
    top=y-i*55
    if i%2==0:panel(LEFT,top-40,WIDTH,47,PALE)
    label(LEFT+16,top-14,a,12,TEAL,True)
    label(LEFT+119,top-14,b,12,NAVY,True)
    label(LEFT+216,top-14,desc,9.1,INK)
y-=len(rows)*55+26
y=info_box(y,'VALIDATION AND RECURSIVE MODE','Choose two different extensions (with or without a leading dot). Subfolder scanning is off by default. If enabled, the same song name in two different subdirectories is never mixed.',height=96)-26
y=section(y,'What the tool does not analyze','No audio or video quality analysis. No hashes, content fingerprinting, music metadata, or automatic guessing that two differently named tracks sound alike.')
new_page()

# Page 5
header(5,'Preview every change','understand the results')
y=H-188
y=para('The preview displays changes <b>grouped by base filename</b>. Click a row to see its decisions; exclude a whole group if needed. Search/filter by companion or inclusion, or export the preview without changing files. Cancel scan stops an ongoing preview safely.',LEFT,y,size=9.6,leading=17)-15
y=codepanel(y,'Song - Demo Artist\n[BACKUP]  Song - Demo Artist.mp3\n[RENAME]  Song - Demo Artist(1).mp3\n       -> Song - Demo Artist.mp3\n[RENAME]  Song - Demo Artist(1).lrc',height=132)
for i,(tag,meaning) in enumerate([('KEEP','Existing file is retained unchanged.'),('BACKUP','Extra file will be moved to a dated backup.'),('RENAME','Selected file will receive a cleaned-up name.')]):
    top=y-i*57
    panel(LEFT,top-43,WIDTH,50,PALE)
    label(LEFT+15,top-22,tag,10,TEAL if i==0 else (MUTED if i==1 else DARK),True)
    label(LEFT+139,top-22,meaning,9.2,INK)
y-=210
y=info_box(y,'NO FILE CHANGES DURING PREVIEW','Scan & preview reads filenames and file statistics only. Export report writes a text file wherever you choose; it does not rename or delete any selected media.',height=93)
new_page()

# Page 6
header(6,'Which copy wins?','selection rules')
y=H-188
y=section(y,'Rule 1  /  Prefer matching companions','Keep a main file whose numbered suffix has a matching companion: e.g. Song(1).mp3 + Song(1).lrc.')
y=section(y,'Rule 2  /  Unnumbered wins when both pairs exist','Song.mp3 + Song.lrc wins over Song(1).mp3 + Song(1).lrc. The numbered pair goes into backup.')
y=section(y,'Rule 3  /  No companion available','Keep the unnumbered main file, if present, otherwise the lowest numbered main file.')
y=section(y,'Rule 4  /  Preserve legitimate names','Only trailing (1) through (999) are considered duplicate suffixes. Descriptive (Live), (Remix), (2026), etc. are not removed.')
y=section(y,'Rule 5  /  Avoid uncertain situations','A lone numbered copy or numbered complete pair is left unchanged. Groups with ambiguous case collisions are skipped, and no unrelated extensions are touched.')
y=info_box(y,'THE ORIGINAL EXAMPLE','Before: Song.mp3 + Song(1).mp3 + Song(1).lrc. After: Song.mp3 (the former numbered MP3) + Song.lrc. The former unnumbered MP3 is backed up.',height=96)
new_page()

# Page 7
header(7,'Apply safely and recover','backup workflow')
y=H-189
y=para('After preview, <b>Apply cleanup</b> opens a confirmation showing only included groups and backup/rename totals. Clicking No changes nothing. Clicking Yes starts the operation.',LEFT,y,size=10,leading=17)-24
y=codepanel(y,'C:/Music/\n  Song.mp3\n  Song.lrc\n  _File_Pair_Cleaner_Backup_20261021_123000_123456/\n    manifest.json\n    duplicates/\n      Song.mp3',height=153)
y=section(y,'What is inside the backup?','Extra files are moved under duplicates/. The JSON manifest records their original paths and all rename operations. Use Open last backup from the GUI after the cleanup.')
y=section(y,'How to restore','Close other programs, read manifest.json, check for occupied final names and copy the selected original files back. There is no automatic restore button.')
y=info_box(y,'INTERRUPTION SAFETY','The application rechecks selected files and refuses occupied destinations. Excluded groups are untouched. Best-effort rollback is attempted after failures; abrupt power loss can still require manual recovery.',height=87)
new_page()

# Page 8
header(8,'Troubleshooting and privacy','help and safety')
y=H-188
for title,body in [
('No duplicate groups found','Check selected extensions and the final (1), (2) duplicate-number suffix.'),
('Folder picker or folder unavailable','Choose another accessible folder. Close players, editors or software locking files.'),
('Warnings about ambiguous names','Some groups were intentionally skipped instead of risking an overwrite.'),
('A file changed after scanning','Run Scan & preview again. Apply requires a fresh, safe plan.'),
('An antivirus warns about the EXE','This program is unsigned. Check that it came from the GitHub release and review the public source.'),
('The executable will not start','Extract the complete ZIP and keep all support files alongside DuplicatePairCleaner.exe.')]:
    y=section(y,title,body)
y=info_box(y+8,'PRIVACY BY DESIGN','This tool runs locally and does not upload file names, media, logs or other personal information. It does not use analytics, advertising or cloud services.',height=83)
new_page()

# Page 9
header(9,'Project and release information','open source')
y=H-188
y=para('<b>Duplicate Pair Cleaner 3.5.0</b> is open-source software by DimitrisLai. The core matching algorithm is preserved; v3.5 adds remembered settings, safe scan cancellation, selective groups and Light/Dark/System appearance.',LEFT,y,size=10,leading=17)-30
for title,desc in [
('Source and license','MIT License. All Python source, tests, build scripts, workflows and release notes are published on GitHub.'),
('Technical requirements','For the Windows portable EXE, Python is included in the bundle. Source version requires Python 3.10+ with Tkinter.'),
('Development verification','Regression tests cover file-selection priorities, backup and rollback behavior and GUI data model. Windows EXE packaging is performed by GitHub Actions on Windows.'),
('Windows test disclaimer','You should still test Browse, Preview, Apply and Open backup on your own Windows computer before using it on irreplaceable libraries.')]:
    y=section(y,title,desc)
y-=5
panel(LEFT,y-106,WIDTH,106,PALE)
label(LEFT+17,y-26,'OFFICIAL PROJECT',11,TEAL,True)
label(LEFT+17,y-49,'github.com/DimitrisLai/Duplicate-Pair-Cleaner',9.2,INK)
label(LEFT+17,y-76,'FEATURE-COMPLETE 2026  ·  3.5.0  ·  MIT',9,INK,True)
c.save()
print(f'Manual: {PDF} | {PDF.stat().st_size} bytes')
