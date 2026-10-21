# Duplicate Pair Cleaner v3.0.0 — Final Windows GUI Release

The original filename-aware duplicate cleaner, now with a **proper Windows desktop interface**, while preserving its proven MP3/LRC and other file-pair selection rules.

### New in v3.0.0
- Portable Windows `.exe` built using PyInstaller on Windows GitHub Actions; **no separate Python installation required** for users of the portable ZIP.
- Navy/teal Tkinter interface with native folder browser, preset or custom paired extensions, optional recursive scanning.
- Responsive background scanning, detailed grouped preview, search and companion filters, summary counts and warning notifications.
- Complete text-report export, explicit confirmation before applying, permanently disabled deletion in GUI, backup-folder shortcut.
- New GUI state tests alongside the existing 34 core tests; CLI and v2.2.0 release remain available.
- Rewritten illustrated user guide and full PDF manual.

### Install
1. Download and extract `Duplicate-Pair-Cleaner-v3.0.0-Windows-Portable.zip` from this release.
2. Open the `DuplicatePairCleaner` directory, then launch `DuplicatePairCleaner.exe`.
3. Choose a folder and two extensions, then **Scan & preview**. Review the results before applying.

### Important safety note
The program compares **file names, not file contents**. It cannot determine whether two numbered files contain identical audio, video, image or metadata. Extra files are moved to dated backups by default. Review changes and maintain a separate backup for irreplaceable data.

### Verification scope
The core and GUI model are tested on Python 3.10 and 3.13. The portable EXE is packaged by GitHub Actions on Windows. The final hands-on GUI smoke test on the user's own Windows PC remains recommended; the release is unsigned.

MIT License — DimitrisLai.
