# Changelog

## v3.5.0 — 2026-10-23 — Final planned feature release for 2026
- Restores the last valid folder, main/companion extensions, preset, and recursive choice without auto-scanning.
- Adds cooperative **Cancel scan** during preview and safely cancels before closing; never commits partial plans.
- Adds **Include/Exclude selected group**, **Include all/Exclude all**, and Included/Excluded filters. Only fully included groups are applied and backed up.
- Maintains the Light/Dark/System appearance options from v3.1.0, with settings persisted together.
- Adds dedicated safety tests for cancellation, settings and excluded groups, plus a real-Tk virtual desktop smoke test.
- Marks the project feature-complete / maintenance-only through December 31, 2026; critical fixes remain possible.

## v3.1.0 — 2026-10-23 — Appearance selection
- Added Light, Dark (near-black), and System appearance presets in the Windows GUI header.
- Dark colors apply across results, forms, action controls, headings, and detail panels.
- Saved theme choice in per-user settings, restored across launches; System follows the Windows app-color preference.
- Switching appearance does not invalidate an existing scan, change any file, or bypass the cleanup confirmation.
- Added theme regression tests and a virtual-desktop GUI smoke test; file-pair selection behavior unchanged.

## v3.0.0 — 2026-10-21 — Desktop GUI
- Added modern Windows GUI with folder selection, companion extension presets, grouped previews, filters, export, protected cleanup and backup opening.
- Kept original filename-selection algorithm, preview safeguards, dated backups and recovery logic.
- Added GUI-model regression tests and cross-platform checks.
- Added reproducible Windows PyInstaller release build and redesigned GUI user manual.
- No permanent file deletion option in the GUI.

## v2.2.0 — 2026-10-18 — Stable CLI release
- Original numbered-copy cleaner with custom extensions, grouped console preview, backups, collision checks and rollback.
- Shipped MIT license, tests, CLI scripts and documentation.

All prior releases remain available in GitHub Releases.
