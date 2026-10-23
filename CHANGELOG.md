# Changelog

## v3.1.0 — 2026-10-23 — Appearance selection
- Added Light, Dark (near-black), and System appearance choices in the GUI.
- Theme is saved per user and reapplied between launches; System follows Windows app appearance.
- Theme changes do not invalidate an existing preview or alter files.
- Added preference tests and local GUI smoke tests; core selection/backup rules unchanged.

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
