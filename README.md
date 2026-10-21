# Duplicate Pair Cleaner

**Smart, safe duplicate cleanup. Now with a real Windows interface.**

[![Python tests](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/actions/workflows/tests.yml/badge.svg)](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/actions/workflows/tests.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-07988B)](LICENSE)
[![Windows](https://img.shields.io/badge/platform-Windows%2010%2F11-0B172B)](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/releases)

Duplicate Pair Cleaner consolidates numbered duplicates like `Song(1).mp3` while **keeping the version with matching lyrics, subtitles or other companion files**. It protects your files using previews, explicit confirmation and dated backup folders.

## Download

**Windows GUI v3.0.0 is built and verified**, but permanent GitHub Release publishing currently requires repository workflow write permission. Until that is enabled, open [the Windows GUI build workflow](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/actions/workflows/publish_gui.yml), select the latest build, and download the `windows-portable-v3.0.0` artifact from its **Artifacts** section (sign-in may be required; build artifacts expire). Extract the portable ZIP and run `DuplicatePairCleaner.exe` inside the `DuplicatePairCleaner` folder. **No separate Python installation is needed.** The build is unsigned and may trigger Windows SmartScreen.

The older [v2.2.0 command-line release](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/releases/tag/v2.2.0) remains available.

## What you can do

- Select any folder using the Windows folder browser; optionally include subfolders.
- Choose preset pairs `.mp3 + .lrc`, `.mp4 + .srt`, `.flac + .lrc`, `.jpg + .xmp`, `.wav + .txt`, or enter your own extensions.
- **Scan & preview** safely before touching your files.
- Review every affected file group, with KEEP, BACKUP, RENAME and final names.
- Search and filter by whether a matching companion is present.
- Export an unfiltered text preview report.
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
- [Download the permanent nine-page PDF manual](docs/Duplicate-Pair-Cleaner-v3.0.0-User-Manual.pdf)
- [Changelog](CHANGELOG.md) / [Release notes](docs/RELEASE_NOTES_v3.0.0.md)
- [Report an issue](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/issues) with synthetic filenames only

Licensed under [MIT](LICENSE), by **DimitrisLai**.
