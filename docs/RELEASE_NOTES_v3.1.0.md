# Duplicate Pair Cleaner v3.1.0 — Light, Dark and System Themes

A focused update to the stable v3 Windows GUI, with the original file-pair selection and backup logic unchanged.

## New
- **Light / Dark / System** appearance selector in the top-right of the GUI.
- Near-black Dark theme with high-contrast text and teal accents throughout the preview, controls and file details.
- System appearance follows the Windows application color preference (checked periodically).
- Theme preference saved locally and restored on subsequent launches.
- Changing appearance does not clear a preview, alter files or bypass confirmation.
- New theme preference tests, GUI smoke checks and an updated user manual.

## Install
1. Download the portable Windows ZIP and extract **all** files.
2. Open `DuplicatePairCleaner/DuplicatePairCleaner.exe`; Python installation is not required.
3. Choose your appearance, select a folder and extensions, then Scan & preview before applying.

**Safety:** The application compares filenames, not media contents. Duplicates are moved into dated backups, not permanently deleted.

License: MIT, by DimitrisLai. Previous v3.0.0 release remains available.
