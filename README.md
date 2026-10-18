# Duplicate Pair Cleaner

**Safely remove numbered duplicate files while preserving matching companion files.**

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![MIT License](https://img.shields.io/badge/License-MIT-green)
[![Tests](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/actions/workflows/tests.yml/badge.svg)](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/actions/workflows/tests.yml)

Duplicate Pair Cleaner is a lightweight open-source Python utility that cleans filenames ending in **(1)**, **(2)**, **(3)**, etc. Unlike simple duplicate cleaners, it prefers copies with matching companion files, such as song lyrics, subtitles, or photo metadata.

**No third-party Python dependencies. No ads, tracking, file uploads, or internet connection.**

## Features

- Pick **any two extensions**: default `.mp3 + .lrc`, or choose `.mp4 + .srt`, `.jpg + .xmp`, `.flac + .lrc`, and many more.
- Choose **any folder** with a Windows folder browser; no copying the script into each folder.
- Optional recursive scanning. Each subfolder is handled independently.
- **Grouped previews** showing KEEP, BACKUP, RENAME and final filenames.
- Keep the main file with a matching companion when possible; otherwise prefer an unnumbered file.
- **Back up duplicates by default**, with a JSON manifest and rollback attempts on errors.
- Safe Windows launchers, a command-line interface, and a 34-test regression suite.

## Quick start (Windows)

1. Download the [Windows ZIP for v2.2.0](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/releases/download/v2.2.0/Duplicate-Pair-Cleaner-v2.2.0-Windows.zip). Alternatively, download the source repository ZIP using **Code > Download ZIP**.
2. Install [Python 3.10 or newer](https://www.python.org/downloads/) and **extract** the ZIP first.
3. Double-click **Preview_Only.bat** to see a report with **no changes to selected files**.
4. Select your folder, pick the two file extensions and choose whether to include subfolders.
5. Review the grouped results. To apply, double-click **Run_Cleaner.bat**, repeat the review and type exactly **YES**.

**Review keys:** Enter = next five groups; A = show all remaining groups; Q = cancel.

## Example

**Before:**
```text
Morning Lights - Demo Artist.mp3
Morning Lights - Demo Artist(1).mp3
Morning Lights - Demo Artist(1).lrc
```

**After:**
```text
Morning Lights - Demo Artist.mp3
Morning Lights - Demo Artist.lrc
```

The kept MP3 contains the **former (1) copy**. The old unnumbered MP3 is moved into a dated backup folder. The matching LRC is renamed. If both complete pairs exist, the unnumbered pair wins. If neither MP3 has an LRC, the unnumbered MP3 wins.

## Rules and limitations

1. Recognizes copy suffixes `(1)` through `(999)` at the **end** of a filename stem, optionally preceded by a space. Ordinary parentheses such as `(Live)` or `(2026)` are not considered duplicate numbering.
2. Groups names **case-insensitively** but preserves the selected filename's capitalization.
3. Chooses a main file with a matching companion first; prefers unnumbered pairs, then lower copy numbers.
4. Keeps one companion where available, even when its number does not match any main file.
5. Single `(1)` files or single complete `(1)` pairs are left alone, because the suffix may be intentional.
6. Only the two selected file extensions are modified. Extra files and unrelated formats are untouched.
7. Scan results are based on **filenames, not file contents or hashes**. Two recordings with the same title could actually be different. Always review the preview first.

**Backups:** Unwanted files are moved to `_File_Pair_Cleaner_Backup_<timestamp>/duplicates/`. The folder contains `manifest.json` recording moved and renamed files. Restore manually as needed; no automatic restore command is provided. Keep an additional backup for important data. Power loss may interrupt filesystem operations.

The included BAT files **do not enable permanent deletion**. The optional advanced `--permanent` flag exists only on the command line, and is not recommended.

## Command line

```sh
# Read-only preview
python file_pair_cleaner.py --folder "/path/to/files" --preview

# Choose extensions and scan subfolders
python file_pair_cleaner.py --folder "/path/to/videos" --main-ext mp4 --companion-ext srt --recursive --preview

# Windows folder picker with prompts
python file_pair_cleaner.py --select-folder --ask-extensions --ask-subfolders

# Help, version and tests
python file_pair_cleaner.py --help
python file_pair_cleaner.py --version
python -m unittest -v test_cleaner.py
```

## Documentation

- [Download the illustrated 9-page PDF manual](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/releases/download/v2.2.0/Duplicate-Pair-Cleaner-v2.2.0-User-Manual.pdf) · [Read the text guide](docs/USER_GUIDE.md)
- [Example of grouped cleanup decisions](docs/EXAMPLE_PREVIEW.txt)
- [Changelog](CHANGELOG.md) and [v2.2.0 release notes](docs/RELEASE_NOTES_v2.2.0.md)
- [Contributing](CONTRIBUTING.md) | [Security](SECURITY.md)
- [Open an issue](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/issues) with **fictional filenames**, not a personal file inventory.

## License

Copyright © 2026 **DimitrisLai**. Released under the [MIT License](LICENSE). The program is provided as-is, without warranty.
