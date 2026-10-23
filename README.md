# Duplicate Pair Cleaner

**Smart, safe duplicate cleanup. Now with a real Windows interface.**

[![Python tests](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/actions/workflows/tests.yml/badge.svg)](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/actions/workflows/tests.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-07988B)](LICENSE)
[![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-0B172B)](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/releases)

Duplicate Pair Cleaner consolidates numbered duplicates like `Song(1).mp3` while **keeping the version with matching lyrics, subtitles or other companion files**. It protects your files using previews, explicit confirmation and dated backup folders.

## Project status — Feature-complete for 2026

**v3.5.0 is the final planned feature release for 2026.** As of October 23, 2026, no further feature updates or scheduled releases are planned through **December 31, 2026**.

The project remains **public, available to download, and MIT-licensed**. Issues and pull requests can still be submitted, but there is no commitment to a feature roadmap or a regular update schedule. Important security or critical bug fixes, compatibility corrections, or code-signing changes may be published if necessary. Development may be reconsidered in **2027**.

This is a **feature-complete / maintenance-only status**, not an archived or abandoned repository.

## Download

**[Download the latest Windows GUI (v3.5.0)](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/releases/tag/v3.5.0)**. Download the portable Windows ZIP, **extract everything**, then run `DuplicatePairCleaner.exe` inside the extracted `DuplicatePairCleaner` folder. **No Python installation required** for the compiled EXE. Unsigned releases may trigger Windows SmartScreen.

The previous [v3.0.0 GUI release](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/releases/tag/v3.0.0) and the older [v2.2.0 command-line release](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/releases/tag/v2.2.0) remain available.

## What you can do

- **Appearance:** choose Light, Dark (near-black), or System (follows Windows), with your preference remembered between launches. Changing the theme never changes a cleanup plan.
- **Remembered choices:** last valid folder, pair extensions, preset, subfolder setting, and theme are restored between launches. Opening the app never starts a scan automatically.
- **Cancel scan:** safely cancel a large read-only scan or request cancellation before closing, with no partial results or file changes.
- **Selective cleanup:** exclude or include complete duplicate groups, filter by inclusion, or toggle all. Only included groups are backed up or renamed.
- Select any folder using the Windows folder browser; optionally include subfolders.
- Choose preset pairs `.mp3 + .lrc`, `.mp4 + .srt`, `.flac + .lrc`, `.jpg + .xmp`, `.wav + .txt`, or enter your own extensions.
- **Scan & preview** safely before touching your files.
- Review every affected file group, with KEEP, BACKUP, RENAME and final names.
- Search and filter by whether a matching companion is present.
- Export a text preview report listing selected changes and explicitly excluded groups.
- Confirm changes deliberately and keep automatic backups. Open the backup folder after completion.
- Run offline, without accounts, ads or telemetry.

## Example

**Before:**

```text
Song - Demo Artist.mp3
Song - Demo Artist(1).mp3
Song - Demo Artist(1).lrc
```

**After:**

```text
Song - Demo Artist.mp3  # formerly Song - Demo Artist(1).mp3
Song - Demo Artist.lrc  # formerly Song - Demo Artist(1).lrc
```

The previously unnumbered MP3 is stored in the dated backup folder, **not deleted**.

## How the selection works

The algorithm prefers a main file with a companion bearing the same suffix number; it prefers the unnumbered pair if both are complete, otherwise the lowest numbered complete pair. If no matched pair exists, it prefers the unnumbered main file while keeping at most one available companion. A lone `Song(1).mp3`, or a lone numbered complete pair, is left untouched. Descriptive parentheses such as `(Live)` or `(2026)` are not duplicate suffixes. Files are grouped case-insensitively within **each directory separately**.

**Important:** filenames are compared, not media contents or hashes. Always inspect your preview first. Keep a separate backup of irreplaceable files.

## Source and development

Python 3.10+ and Tkinter are the only requirements for running source GUI:

```bash
python gui_app.py
```

The classic CLI is still available:

```bash
python file_pair_cleaner.py --folder "C:/Music" --main-ext mp3 --companion-ext lrc --preview
```

Run all automated tests:

```bash
python -m unittest discover -v -p 'test*.py'
```

The GUI source, GUI state model, cleaning core, manual generator and Windows packaging workflow are committed to this repository. The executable is built **on a Windows GitHub runner**, not cross-compiled on Linux.

## Documentation and help

- [Graphical interface guide](docs/GUI_USER_GUIDE.md)
- [Download the nine-page v3.5.0 PDF manual](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/releases/download/v3.5.0/Duplicate-Pair-Cleaner-v3.5.0-User-Manual.pdf) · [Repository text guide](docs/GUI_USER_GUIDE.md)
- [Changelog](CHANGELOG.md) / [Release notes](docs/RELEASE_NOTES_v3.5.0.md)
- [Report an issue](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/issues) with synthetic filenames only

Copyright © 2026 **Dimitris Laidis**. Licensed under [MIT](LICENSE).
