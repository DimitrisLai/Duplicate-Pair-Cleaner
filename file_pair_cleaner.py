#!/usr/bin/env python3
"""Duplicate Pair Cleaner: safely consolidate numbered copies, preferring matching sidecars.

Python 3.10+. Standard library only. Filename rules only, no content comparison.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

VERSION = "3.0.0"
BACKUP_PREFIX = "_File_Pair_Cleaner_Backup_"
OLD_BACKUP_PREFIX = "_MP3_LRC_Backup_"
# Numbered-copy suffixes at the END of a stem only. (Live), (2026), etc. are untouched.
COPY_SUFFIX = re.compile(r"^(?P<base>.+?)\s*\((?P<num>[1-9]\d{0,2})\)$")
EXT_PATTERN = re.compile(r"\.?[A-Za-z0-9][A-Za-z0-9_-]{0,14}\Z", re.ASCII)


@dataclass(frozen=True)
class PairType:
    main: str = ".mp3"
    sidecar: str = ".lrc"

    def __post_init__(self):
        main = parse_extension(self.main)
        sidecar = parse_extension(self.sidecar)
        if main == sidecar:
            raise ValueError("The two file extensions must be different.")
        object.__setattr__(self, "main", main)
        object.__setattr__(self, "sidecar", sidecar)


@dataclass(frozen=True)
class Item:
    path: Path
    base: str
    number: int
    ext: str
    size: int
    mtime_ns: int


@dataclass(frozen=True)
class Change:
    action: str   # "backup" or "rename"
    source: Path
    target: Path | None = None


@dataclass(frozen=True)
class Group:
    title: str
    items: tuple[Item, ...]
    main: Item
    sidecar: Item | None
    changes: tuple[Change, ...]
    final_main: Path
    final_sidecar: Path | None
    types: PairType

    @property
    def reason(self):
        sidecar_versions = {x.number for x in self.items if x.ext == self.types.sidecar}
        paired = sum(x.number in sidecar_versions for x in self.items if x.ext == self.types.main)
        if paired > 1 and self.main.number == 0:
            return "Multiple complete pairs: keeping the unnumbered pair."
        if self.sidecar and self.main.number == self.sidecar.number:
            return "Keeping the main file with its matching companion."
        if self.sidecar:
            return "Keeping the best main file and the available companion."
        return "No companion found: keeping the unnumbered main file if possible."


def parse_extension(raw: str) -> str:
    value = raw.strip()
    if not EXT_PATTERN.fullmatch(value):
        raise ValueError(f"Invalid extension {raw!r}. Use one extension such as .mp3 or srt.")
    return "." + value.lstrip(".").casefold()


def stem_parts(stem: str) -> tuple[str, int]:
    match = COPY_SUFFIX.fullmatch(stem)
    return (match.group("base").rstrip(), int(match.group("num"))) if match else (stem, 0)


def is_backup_dir(name: str) -> bool:
    folded = name.casefold()
    return folded.startswith(BACKUP_PREFIX.casefold()) or folded.startswith(OLD_BACKUP_PREFIX.casefold())


def iter_selected(folder: Path, recursive: bool, types: PairType):
    wanted = {types.main, types.sidecar}
    if recursive:
        def on_error(exc):
            raise exc
        for dirname, subdirs, names in os.walk(folder, onerror=on_error, followlinks=False):
            # Never enter backups (including backups produced by the previous releases).
            subdirs[:] = [name for name in subdirs
                          if name not in {".git", ".venv", "__pycache__"}
                          and not is_backup_dir(name)
                          and not (Path(dirname) / name).is_symlink()
                          and not (hasattr(os.path, "isjunction") and os.path.isjunction(str(Path(dirname) / name)))]
            for name in names:
                path = Path(dirname) / name
                if path.suffix.casefold() in wanted and path.is_file() and not path.is_symlink():
                    yield path
    else:
        for path in folder.iterdir():
            if path.suffix.casefold() in wanted and path.is_file() and not path.is_symlink():
                yield path


def build_plan(folder: Path, recursive: bool, types: PairType = PairType()):
    families: dict[tuple[Path, str], list[Item]] = defaultdict(list)
    for path in iter_selected(folder, recursive, types):
        stem, number = stem_parts(path.stem)
        stat = path.stat()
        families[(path.parent, stem.casefold())].append(
            Item(path, stem, number, path.suffix.casefold(), stat.st_size, stat.st_mtime_ns))

    groups: list[Group] = []
    changes: list[Change] = []
    warnings: list[str] = []
    destinations = set()
    occupied_by_directory: dict[Path, set[str]] = {}
    for (directory, family), items in sorted(families.items(), key=lambda p: (str(p[0][0]).casefold(), p[0][1])):
        mains = [i for i in items if i.ext == types.main]
        companions = [i for i in items if i.ext == types.sidecar]
        if not mains or not any(i.number for i in items):
            continue
        # A single Song(1).ext, or Song(1).main + Song(1).sidecar without
        # another variant, may be an intentional filename. Leave it alone.
        if len(mains) < 2 and len({i.number for i in items}) < 2:
            continue
        # Ambiguous when both 'Song (1)' and 'song(1)' exist on a case-sensitive FS.
        signatures = [(i.number, i.ext) for i in items]
        if len(signatures) != len(set(signatures)):
            warnings.append(f"Ambiguous duplicate filenames; skipped: {directory / family}")
            continue

        companion_numbers = {i.number for i in companions}
        main = min(mains, key=lambda i: (i.number not in companion_numbers,
                                        i.number != 0, i.number, i.path.name.casefold()))
        sidecar = min(companions, key=lambda i: (i.number != main.number,
                                                i.number != 0, i.number,
                                                i.path.name.casefold())) if companions else None
        stem = main.base  # Preserve selected file's spelling and capitalization.
        target_main = directory / (stem + types.main)
        target_sidecar = directory / (stem + types.sidecar)
        kept_paths = {main.path}
        if sidecar:
            kept_paths.add(sidecar.path)
        discarded = [i for i in items if i.path not in kept_paths]
        proposed = [Change("backup", i.path) for i in sorted(discarded, key=lambda i: i.path.name.casefold())]
        for chosen, target in ((main, target_main), (sidecar, target_sidecar)):
            if chosen and chosen.path != target:
                proposed.append(Change("rename", chosen.path, target))

        # Check collisions against ALL existing files, not only selected extensions.
        # A source that gets backed up or renamed is allowed to occupy a target now.
        vacated = {c.source.name.casefold() for c in proposed}
        # Cache directory contents once: scanning a large music folder is much faster.
        if directory not in occupied_by_directory:
            occupied_by_directory[directory] = {p.name.casefold() for p in directory.iterdir()}
        occupied = occupied_by_directory[directory]
        conflict = None
        for action in proposed:
            if action.action != "rename":
                continue
            target_key = (str(action.target.parent).casefold(), action.target.name.casefold())
            if action.target.name.casefold() in occupied and action.target.name.casefold() not in vacated:
                conflict = f"Destination already exists: {action.target}"
                break
            if target_key in destinations:
                conflict = f"Destination would be used twice: {action.target}"
                break
        if conflict:
            warnings.append(f"Skipped {directory / stem}: {conflict}")
            continue
        for action in proposed:
            if action.action == "rename":
                destinations.add((str(action.target.parent).casefold(), action.target.name.casefold()))
        if proposed:
            groups.append(Group(
                title=stem,
                items=tuple(sorted(items, key=lambda i: (i.number, i.ext != types.main, i.path.name.casefold()))),
                main=main,
                sidecar=sidecar,
                changes=tuple(proposed),
                final_main=target_main,
                final_sidecar=target_sidecar if sidecar else None,
                types=types,
            ))
            changes.extend(proposed)
    return groups, changes, warnings


def relative(path: Path, folder: Path) -> str:
    return str(path.relative_to(folder))


def intro_lines(folder: Path, recursive: bool, types: PairType, groups, changes) -> list[str]:
    return [
        "=" * 77,
        f"DUPLICATE PAIR CLEANER v{VERSION} | PREVIEW: NOTHING HAS CHANGED",
        f"Folder: {folder}",
        f"Main extension: {types.main} | Companion extension: {types.sidecar}",
        f"Include subfolders: {'YES (each folder handled separately)' if recursive else 'NO'}",
        f"Groups: {len(groups)} | Files to back up: {sum(c.action == 'backup' for c in changes)} | "
        f"Renames: {sum(c.action == 'rename' for c in changes)}",
        "Status: [KEEP] unchanged | [BACKUP] saved, not deleted | [RENAME] new filename",
        "=" * 77,
    ]


def group_lines(folder: Path, group: Group, index: int, count: int) -> list[str]:
    by_path = {c.source: c for c in group.changes}
    lines = ["", "-" * 77,
             f"GROUP {index:03d}/{count:03d} | {relative(group.main.path.parent / group.title, folder)}",
             "Why: " + group.reason, "CURRENT FILES / DECISIONS:"]
    for item in group.items:
        action = by_path.get(item.path)
        if action is None:
            lines.append(f"  [KEEP]   {relative(item.path, folder)}")
        elif action.action == "backup":
            lines.append(f"  [BACKUP] {relative(item.path, folder)}")
        else:
            lines.extend((f"  [RENAME] {relative(item.path, folder)}",
                          f"           -> {relative(action.target, folder)}"))
    lines.extend(("AFTER CLEANUP:",
                  f"  [MAIN {group.types.main}] {relative(group.final_main, folder)}",
                  f"  [PAIR {group.types.sidecar}] " +
                  (relative(group.final_sidecar, folder) if group.final_sidecar else "(not available)")))
    return lines


def footer_lines(groups, changes, warnings) -> list[str]:
    lines = ["", "=" * 77,
             f"TOTAL: {len(groups)} groups | {sum(c.action == 'backup' for c in changes)} files backed up | "
             f"{sum(c.action == 'rename' for c in changes)} renames",
             "All other files are untouched. This was a preview of the plan."]
    if warnings:
        lines.extend([f"WARNING: {len(warnings)} skipped/ambiguous group(s):"] + [" - " + w for w in warnings])
    return lines


def render_report(folder, recursive, types, groups, changes, warnings) -> str:
    lines = intro_lines(folder, recursive, types, groups, changes)
    if not changes:
        lines.append("No eligible numbered-copy groups found.")
    for index, group in enumerate(groups, 1):
        lines.extend(group_lines(folder, group, index, len(groups)))
    lines.extend(footer_lines(groups, changes, warnings))
    return "\n".join(lines) + "\n"


def print_plan(folder, recursive, types, groups, changes, warnings, page_size=5, paged=True) -> bool:
    print("\n".join(intro_lines(folder, recursive, types, groups, changes)))
    if not changes:
        print("No eligible numbered-copy groups found.")
    all_at_once = not paged or page_size <= 0
    for index, group in enumerate(groups, 1):
        print("\n".join(group_lines(folder, group, index, len(groups))))
        if not all_at_once and index % page_size == 0 and index < len(groups):
            try:
                answer = input(f"ENTER = next {page_size} groups | A = show all | Q = cancel: ").strip().upper()
            except EOFError:
                answer = "Q"
            if answer == "Q":
                print("Cancelled during review. No files changed.")
                return False
            if answer == "A":
                all_at_once = True
    print("\n".join(footer_lines(groups, changes, warnings)))
    return True


def apply_plan(folder: Path, groups: list[Group], changes: list[Change], types: PairType,
               permanent: bool = False) -> Path | None:
    """Stage renames; fail without overwriting files; best-effort rollback on failure."""
    if not changes:
        return None
    expected = {item.path: item for group in groups for item in group.items}
    for item in expected.values():
        if not item.path.is_file() or item.path.is_symlink():
            raise RuntimeError(f"File disappeared or became a symlink: {item.path}")
        stat = item.path.stat()
        if stat.st_size != item.size or stat.st_mtime_ns != item.mtime_ns:
            raise RuntimeError(f"A file changed since the preview. Start a new scan: {item.path}")

    # A destination can become occupied between review and approval. Refuse
    # the operation BEFORE moving any files if this happened.
    rename_actions = [change for change in changes if change.action == "rename"]
    vacated = {change.source for change in changes}
    for change in rename_actions:
        current = {entry.name.casefold(): entry for entry in change.target.parent.iterdir()}
        taken = current.get(change.target.name.casefold())
        if taken is not None and taken not in vacated:
            raise RuntimeError(f"Rename destination became occupied after preview: {change.target}")

    backup = folder / f"{BACKUP_PREFIX}{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    backup.mkdir(exist_ok=False)
    discarded_dir = backup / "duplicates"
    staging_dir = backup / "temporary"
    discarded_dir.mkdir()
    staging_dir.mkdir()
    moved: list[tuple[Path, Path]] = []
    staged: list[tuple[Path, Path, Path]] = []
    finished: list[tuple[Path, Path]] = []
    try:
        for action in changes:
            if action.action != "backup":
                continue
            saved = discarded_dir / action.source.relative_to(folder)
            saved.parent.mkdir(parents=True, exist_ok=True)
            action.source.rename(saved)
            moved.append((saved, action.source))
        for index, action in enumerate(x for x in changes if x.action == "rename"):
            tmp = staging_dir / f"{index:06d}_{uuid.uuid4().hex}{action.source.suffix}"
            action.source.rename(tmp)
            staged.append((tmp, action.source, action.target))
        for tmp, original, destination in staged:
            # Case-insensitive occupancy check prevents unintended overwrites on Windows.
            if any(p.name.casefold() == destination.name.casefold()
                   for p in destination.parent.iterdir()):
                raise RuntimeError(f"Rename destination became occupied: {destination}")
            tmp.rename(destination)
            finished.append((destination, original))

        # Verify the final files exist before recording a successful run.
        for group in groups:
            if not group.final_main.is_file() or (group.final_sidecar and not group.final_sidecar.is_file()):
                raise RuntimeError(f"Post-cleanup verification failed: {group.title}")

        manifest = {
            "app": "Duplicate Pair Cleaner", "version": VERSION,
            "folder": str(folder), "main_ext": types.main, "companion_ext": types.sidecar,
            "created": datetime.now().isoformat(timespec="seconds"),
            "moved_to_backup": [{"original": relative(original, folder),
                                 "backup": str(saved.relative_to(backup))}
                                for saved, original in moved],
            "renamed": [{"original": relative(original, folder),
                         "final": relative(final, folder)} for final, original in finished],
        }
        (backup / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        shutil.rmtree(staging_dir)
    except BaseException:
        # This also covers Ctrl+C (KeyboardInterrupt), not just OSError.
        # An abrupt power loss cannot be rolled back automatically.
        errors = []
        for final, original in reversed(finished):
            try:
                final.rename(original)
            except OSError as exc:
                errors.append(f"{final}: {exc}")
        for temp, original, _ in reversed(staged):
            if temp.exists():
                try:
                    temp.rename(original)
                except OSError as exc:
                    errors.append(f"{temp}: {exc}")
        for saved, original in reversed(moved):
            if saved.exists():
                try:
                    saved.rename(original)
                except OSError as exc:
                    errors.append(f"{saved}: {exc}")
        if errors:
            print("WARNING: Some files could not be restored. Inspect:", backup)
            for error in errors:
                print(" -", error)
        else:
            shutil.rmtree(backup)
        raise

    if permanent:
        # Explicit CLI option only. No permanent-delete option in supplied BAT launchers.
        try:
            shutil.rmtree(backup)
        except OSError as exc:
            print(f"WARNING: Cleanup succeeded; backup not completely removed: {exc}")
            print("Remaining files:", backup)
            return backup
        return None
    return backup


def choose_folder() -> Path | None:
    """Select a folder with Tk; typed path fallback if Tk isn't available."""
    root = None
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selection = filedialog.askdirectory(parent=root,
                                            title="Duplicate Pair Cleaner - Select a folder", mustexist=True)
        return Path(selection) if selection else None
    except Exception as exc:
        print(f"Folder picker unavailable ({exc}).")
    finally:
        if root is not None:
            root.destroy()
    try:
        answer = input('Type folder path instead (blank cancels): ').strip().strip('"')
    except (EOFError, KeyboardInterrupt):
        return None
    return Path(answer) if answer else None


def ask_extensions(defaults: PairType) -> PairType | None:
    print("\nChoose your TWO file types. Press ENTER to accept the default.")
    print("Examples: .mp3 + .lrc | .mp4 + .srt | .jpg + .xmp")
    while True:
        try:
            main_raw = input(f"MAIN file extension [{defaults.main}]: ").strip() or defaults.main
            companion_raw = input(f"COMPANION file extension [{defaults.sidecar}]: ").strip() or defaults.sidecar
        except (EOFError, KeyboardInterrupt):
            return None
        try:
            return PairType(main_raw, companion_raw)
        except ValueError as exc:
            print("Invalid selection:", exc, "Please try again.\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Keep one main file and preferably its matching companion among numbered copies.")
    parser.add_argument("--version", action="version", version=f"Duplicate Pair Cleaner {VERSION}")
    location = parser.add_mutually_exclusive_group()
    location.add_argument("--folder", type=Path, help="Folder to scan (default: current working folder)")
    location.add_argument("--select-folder", action="store_true", help="Open the folder picker")
    parser.add_argument("--main-ext", default=".mp3", help="Main extension (default: .mp3)")
    parser.add_argument("--companion-ext", default=".lrc", help="Companion extension (default: .lrc)")
    parser.add_argument("--ask-extensions", action="store_true", help="Ask to select two file extensions")
    parser.add_argument("--recursive", action="store_true", help="Scan subfolders independently")
    parser.add_argument("--ask-subfolders", action="store_true", help="Ask whether to scan subfolders")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="Only preview; never modify the selected files")
    mode.add_argument("--apply", action="store_true", help="Non-interactive apply, no YES prompt (advanced)")
    parser.add_argument("--permanent", action="store_true",
                        help="Permanently remove backed-up duplicates AFTER successful cleanup (advanced)")
    parser.add_argument("--page-size", type=int, default=5, metavar="N",
                        help="Review N groups at a time in interactive mode (0 = show all)")
    parser.add_argument("--save-report", type=Path, help="Write the full preview as a UTF-8 text file")
    args = parser.parse_args(argv)
    try:
        types = PairType(args.main_ext, args.companion_ext)
    except ValueError as exc:
        parser.error(str(exc))
    if args.permanent and args.preview:
        parser.error("--permanent cannot be combined with --preview")
    if args.page_size < 0:
        parser.error("--page-size cannot be negative")

    if args.select_folder:
        selection = choose_folder()
        if selection is None:
            print("Folder selection cancelled. No files changed.")
            return 0
        folder = selection.expanduser().resolve()
    else:
        folder = (args.folder or Path.cwd()).expanduser().resolve()
    if not folder.is_dir():
        parser.error(f"Folder does not exist: {folder}")

    if args.ask_extensions:
        choice = ask_extensions(types)
        if choice is None:
            print("Cancelled while selecting extensions. No files changed.")
            return 0
        types = choice
    recursive = args.recursive
    if args.ask_subfolders and not args.recursive:
        try:
            recursive = input(f"Selected folder: {folder}\nInclude subfolders? [y/N]: ").strip().casefold() in {"y", "yes"}
        except (KeyboardInterrupt, EOFError):
            print("Cancelled. No files changed.")
            return 0

    try:
        print(f"\nScanning {folder} for {types.main} + {types.sidecar} ...")
        groups, changes, warnings = build_plan(folder, recursive, types)
        if args.save_report:
            report_file = args.save_report.expanduser().resolve()
            report_file.parent.mkdir(parents=True, exist_ok=True)
            report_file.write_text(render_report(folder, recursive, types, groups, changes, warnings),
                                   encoding="utf-8-sig")
            print("Full preview saved:", report_file)
        if not print_plan(folder, recursive, types, groups, changes, warnings,
                          page_size=args.page_size, paged=(not args.preview and not args.apply and sys.stdin.isatty())):
            return 0
        if not changes or args.preview:
            return 0
        if not args.apply:
            print("\nDefault protection: extra files are MOVED into a dated backup folder.")
            if args.permanent:
                print("WARNING: --permanent means no retained backup after cleanup.")
            try:
                answer = input("Type YES to make the changes (anything else cancels): ").strip()
            except (KeyboardInterrupt, EOFError):
                answer = ""
            if answer != "YES":
                print("Cancelled. No files changed.")
                return 0
        saved = apply_plan(folder, groups, changes, types, permanent=args.permanent)
        print("\nDONE. Selected files have been consolidated into unnumbered pairs.")
        print("Backup:", saved if saved else "No backup retained (--permanent).")
        return 0
    except (OSError, RuntimeError, KeyboardInterrupt) as exc:
        print("\nERROR:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
