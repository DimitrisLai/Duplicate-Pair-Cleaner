# Duplicate Pair Cleaner v2.2.0 — First Public Release

Clean numbered file duplicates while keeping matching companions. Choose extensions (.mp3/.lrc, .mp4/.srt, .jpg/.xmp and more), select any folder in Windows, and review grouped changes before approving cleanup.

### Highlights
- Configurable main/companion extensions and recursive scans
- Read-only grouped preview launcher and interactive review
- Prefer matching pairs; keep the unnumbered pair when equally suitable
- Dated backup with manifest instead of deleting duplicates
- Ctrl+C rollback handling, preflight destination checks, final verification
- No external Python packages, account, network services or telemetry
- 34 automated tests on supported Python versions

### Install
1. Download and extract `Duplicate-Pair-Cleaner-v2.2.0-Windows.zip` (when attached to this release).
2. Install Python 3.10+ if needed.
3. Run `Preview_Only.bat` first, then `Run_Cleaner.bat` to approve changes.

**Safety:** This tool compares filenames, not file contents. Review changes and make your own backup of important files.

[README](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner#readme) · [User guide](../USER_GUIDE.md)
