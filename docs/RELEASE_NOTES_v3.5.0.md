# Duplicate Pair Cleaner v3.5.0 — Final Planned Feature Release for 2026

**Feature-complete / maintenance-only** through December 31, 2026. The public MIT project remains available, welcomes issues and pull requests, and may receive urgent security, bug, compatibility or signing updates. Feature work may be reconsidered in 2027.

## New in v3.5.0
- **Remembered preferences:** the last valid folder, file-type preset, custom main and companion extensions, include-subfolders choice and appearance mode persist in per-user settings. No scan starts automatically.
- **Safe cancel scan:** Cancel scan stops an ongoing read-only scan cooperatively, discards partial results and leaves files intact. Closing during a scan can request cancellation. Cleanup itself cannot be interrupted mid-transaction.
- **Selective group cleanup:** every group starts included. Select a group to exclude/include it, or toggle all. Included/Excluded filters never silently change selections. Only included groups contribute to actions, confirmation totals, backups and manifest.
- **Appearance:** retains v3.1.0 Light, Dark and System modes.
- **Testing:** core regression, preference/cancellation/exclusion tests and interactive virtual desktop smoke test; Windows/Linux CI matrix.

## Distribution
- Portable Windows ZIP with standalone `DuplicatePairCleaner.exe` and bundled Python runtime (extract first).
- Full source ZIP for independent review and offline backup.
- Nine-page PDF manual and `SHA256SUMS.txt` download-integrity checks.

## Safety
The cleaner compares filenames rather than media contents. It rechecks selected files before applying, avoids overwrites, and moves extras to dated backups. Preserve independent copies of valuable data.

## Project status — Feature-complete for 2026
**v3.5.0 is the final planned feature release for 2026.** As of October 23, 2026, no further feature updates or scheduled releases are planned through **December 31, 2026**.

The project remains **public, available to download, and MIT-licensed**. Issues and pull requests can still be submitted, but there is no commitment to a feature roadmap or a regular update schedule. Important security or critical bug fixes, compatibility corrections, or code-signing changes may be published if necessary. Development may be reconsidered in **2027**.

This is a **feature-complete / maintenance-only status**, not an archived or abandoned repository.
