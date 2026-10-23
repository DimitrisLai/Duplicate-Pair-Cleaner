# Duplicate Pair Cleaner 3.5.0 — Windows Desktop User Guide

**Project:** https://github.com/DimitrisLai/Duplicate-Pair-Cleaner  
**Author:** DimitrisLai  
**License:** MIT  
**Platforms:** Windows 10 and Windows 11 (portable Windows EXE); Python 3.10+ (source version).

## 1. Start the new GUI
Download the `Duplicate-Pair-Cleaner-v3.5.0-Windows-Portable.zip` asset from GitHub Releases. Extract **all** files to a directory and double-click `DuplicatePairCleaner.exe` inside `DuplicatePairCleaner`. Do not run the executable from inside the ZIP. Windows SmartScreen may warn about unsigned open-source executables; inspect the published source and build workflow before permitting any program to run. The app does not require you to install Python separately.

For the source version, install Python 3.10+ with Tkinter and run `python gui_app.py`. The original command-line interface remains available as `file_pair_cleaner.py`.

## 2. Remembered folder and extensions
The app remembers your last valid folder, main and companion extension, selected preset, include-subfolders option and theme in a per-user local `settings.json` file (`%APPDATA%\DuplicatePairCleaner` on Windows). Invalid or missing saved folders are ignored. No file names, file contents, or automatic scan plans are stored. **Reopening never automatically scans or modifies files.** You must click Scan & preview again.

## 3. Choose a folder and extensions
Click **Browse folder** or type an absolute folder path. Select a preset (MP3/LRC, MP4/SRT, FLAC/LRC, JPG/XMP, WAV/TXT) or enter two distinct custom extensions. Main means the file to preserve; companion means the matching lyrics, subtitle, metadata, or other sidecar. **Include subfolders** is off by default; enable it if necessary. Each directory is treated independently.

## 4. Appearance: Light, Dark, or System
Use the **Appearance** dropdown at the top-right of the application. **Light** keeps the original light panels; **Dark** uses near-black panels and high-contrast text; **System** follows your Windows app-color preference (Windows Settings > Personalization > Colors). The selection is stored in your local user settings folder and remembered after reopening the program. Changing appearance does **not** restart a scan, clear the preview, or change your files. When System is selected, the app periodically checks for Windows light/dark setting changes. If saving your preference fails, the theme still changes for the current session.

## 5. Cancel a long scan
During Scan & preview, click **Cancel scan** to stop safely. Cancellation checks run throughout enumeration and group planning; partial scan results are discarded. The app never applies changes while scanning. If you close during a scan, confirm cancellation and the window closes after the scan worker stops. **Apply cleanup remains non-cancellable** after confirmation to preserve transactional rollback guarantees.

## 6. Scan and review
Click **Scan & preview**. This does not modify your files. The four summary tiles show affected groups, proposed backup moves, renames, and warnings. Click a row to see each original file and what will happen to it. Filter to groups with/without a companion or search by filename. **Export report** saves the complete, unfiltered preview to a UTF-8 text file.

**KEEP** means unchanged. **BACKUP** means an extra file will be moved to a dated backup folder. **RENAME** means a selected file will receive a clean name. The final expected filenames appear below each group. A warning means a group was skipped rather than guessed.

## 7. Include or exclude entire groups
Every group starts **included** (displayed as `[x]`). Select a row and click **Exclude selected** or press Space; the row changes to `[ ]` and its complete pair is excluded. Click **Include selected** to restore it. Use **Exclude all / Include all** to toggle all groups. Filters **Included** and **Excluded** affect visibility, not the selection. Summary counts and the Apply confirmation include only selected groups. **Excluded groups are completely untouched**, including their files, renames, and backups; this is deliberately a group-level option to prevent orphan lyrics/subtitles. Export report lists the exclusions too. Changing folder or extensions clears prior selection and requires a new scan.

## 8. Understand the matching rules
Only trailing duplicate suffixes `(1)` through `(999)` are recognized. Text like `(Live)` or `(2026)` is preserved. A single numbered file (or a lone numbered complete pair) is left alone. The cleaner compares filenames case-insensitively but does not compare media contents, hashes, bitrate, quality or metadata. The main file with a matching companion is preferred; when multiple matched pairs exist, the unnumbered one wins. Otherwise choose the lowest numbered matched pair. Without a matched pair, prefer the unnumbered main file. Retain at most one companion, renaming it to the selected main's base filename. Orphan companions without any main file remain untouched.

**Example A: a numbered MP3 is the only one with lyrics**

Before: `Song.mp3`, `Song(1).mp3`, `Song(1).lrc`  
After: `Song.mp3` *(content previously in Song(1).mp3)* and `Song.lrc`.  
The old `Song.mp3` goes to backup.

**Example B: both copies have lyrics**

Before: `Song.mp3`, `Song.lrc`, `Song(1).mp3`, `Song(1).lrc`  
After: `Song.mp3`, `Song.lrc`. Both numbered copies are backed up.

**Example C: no LRC file**

Before: `Song.mp3`, `Song(1).mp3`  
After: `Song.mp3`. The numbered MP3 goes to backup.

## 9. Apply cleanup
Only after reviewing every affected group, click **Apply cleanup**. The confirmation dialog lists only included groups and how many files will be backed up or renamed and which folder is affected. Clicking No cancels without changes. Clicking Yes starts the filesystem transaction. Do not close or force-end the app during cleanup. The app blocks window closing during the operation. It revalidates file sizes/timestamps and destination occupancy before it moves files. If a file changed after your preview, the operation is refused and you should scan again.

There is **no permanent-delete option** in the GUI. The original command-line script has an advanced `--permanent` flag, not used by the GUI.

## 10. Backups and recovery
Successful cleanups leave a folder named `_File_Pair_Cleaner_Backup_<timestamp>` within the scanned directory. Extra files are under `duplicates/` and `manifest.json` lists original and final paths. Click **Open last backup** to inspect it. Restoration is a manual process: inspect the manifest, check that the original name isn't occupied, and copy backed-up files back to their original paths. Keep your own independent backup for important files. Rollback is attempted on errors; unexpected loss of power or unusual filesystem failures may still require manual recovery.

## 11. Safety and privacy
All scans and actions occur locally. The application does not upload media, require accounts, or use telemetry. Symlinked files and folders, Git folders, virtual environments and existing cleaner backup directories are excluded from recursive scans. Filename similarity is not proof that contents are identical. Review the preview when files may represent distinct versions or edits.

## 12. Troubleshooting
- **Cancel scan:** No changes are applied and any partial preview is discarded; scan again when ready.
- **Excluded groups:** Use the Included / Excluded filter and Include selected to restore a group.
- **No affected groups:** Check selected extensions and whether filenames actually end in `(1)`, `(2)`, etc.
- **Folder missing / access denied:** Select an accessible location and close other programs using those files.
- **Extensions identical:** Choose two different extensions such as `.mp4` and `.srt`.
- **Filename collision or modified file:** No automatic overwrite occurs. Inspect conflicts, rescan and try again.
- **Unexpected warnings:** Review the warning dialog; skipped groups require manual inspection.
- **Antivirus/SmartScreen warning:** The release is unsigned. Verify the repository and build; do not bypass security warnings blindly.
- **Startup fails:** Fully extract the portable ZIP; keep all EXE support files together.
- **Need CLI:** See `python file_pair_cleaner.py --help`.

## 13. Technical verification and support
The core cleaning rules are intentionally inherited from v2.2.0. The GUI adds only orchestration and presentation. Automated tests cover matching, backup and rollback behaviors, and UI data-model validation. The published Windows build is produced through GitHub Actions on a Windows runner. A live Windows desktop smoke test (select folder, scan, confirm, inspect backup) is still advisable.

Issues: https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/issues. Use only invented filenames when reporting bugs; do not upload private media lists.

## Project status — Feature-complete for 2026

**v3.5.0 is the final planned feature release for 2026.** No further feature updates or scheduled releases are planned through December 31, 2026. The public, MIT-licensed repository remains active for contributions and critical fixes. New features may be considered again in 2027.
