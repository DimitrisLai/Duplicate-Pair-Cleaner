# Duplicate Pair Cleaner — User Guide (v2.2.0)

## 1. What does it do?
The tool consolidates filenames ending in duplicate numbers. You choose one **main** extension and one **companion** extension. It keeps a single main file and a single corresponding companion where possible.

## 2. Setup
Windows: Install Python 3.10+, extract the downloaded ZIP, and double-click `Preview_Only.bat` first. The folder picker opens. Choose the extensions (press Enter to keep `.mp3` / `.lrc`) and optionally include subfolders. For changes, use `Run_Cleaner.bat`.

## 3. Example
**Before:** `Song.mp3`, `Song(1).mp3`, `Song(1).lrc`

**After:** `Song.mp3` (contents of old `Song(1).mp3`), `Song.lrc`.

The old main copy is moved to the dated backup.

## 4. Decision priority
- Prefer a main file whose duplicate number has a matching companion.
- Prefer a complete unnumbered pair over numbered pairs.
- If no matching pair exists, keep the unnumbered main file if available, with one suitable companion if any exists.
- Keep a lone numbered copy unchanged; never confuse `(Live)` or `(2026)` with a duplicate marker.
- Each subfolder is cleaned separately; no file is moved across music or video subdirectories.

## 5. Grouped preview
Every affected song or item has its own numbered block. `[KEEP]` means no change; `[BACKUP]` means an extra file is moved safely into a backup folder; `[RENAME]` shows old and final names. The display advances in groups of five. Choose **Q** to exit without modifying files. **Only typing YES confirms** the actual operation.

## 6. Backup and recovery
Backups use a name like `_File_Pair_Cleaner_Backup_20261018_210000_000000` inside your selected folder, with discarded items in `duplicates/` and a `manifest.json` listing paths and renames. Restore manually using the manifest and check the final items before deleting any backup. A separate copy of important files remains strongly recommended.

## 7. Advanced use
For a safe command-line preview:
```sh
python file_pair_cleaner.py --folder "C:/Music" --preview
```
For videos and subtitles:
```sh
python file_pair_cleaner.py --folder "C:/Videos" --main-ext mp4 --companion-ext srt --recursive --preview
```
Use `--help` for every option. Avoid `--permanent` unless you understand that duplicates will be deleted rather than retained in a backup.

## 8. Troubleshooting
- **Python not found:** Install Python from python.org, then reopen the launcher.
- **No duplicate groups:** The filenames may not match the supported copy-number suffix rules. Check the two selected extensions.
- **Folder picker not working:** Launch from a terminal and use `--folder` to specify a directory.
- **Destination occupied / changed source:** Re-run a fresh preview; the program deliberately avoids overwriting unexpected files.
- **Windows security prompt:** Inspect source code before running. This is a Python script using standard-library modules; no external services.

## 9. Safety & privacy
All analysis is local; filenames are compared, not audio/video contents. The app does not send your files online. Don't paste private filenames or directories into public bug reports.

For a printable, designed nine-page PDF version, see the attached release kit and [Releases](https://github.com/DimitrisLai/Duplicate-Pair-Cleaner/releases) once its binary assets are published.
