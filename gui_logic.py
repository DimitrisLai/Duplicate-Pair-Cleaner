"""Pure, testable application state for the desktop UI.

The cleanup algorithm lives in file_pair_cleaner.py and is reused unchanged.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from threading import Event
import file_pair_cleaner as core

APP_VERSION = '3.5.0'

@dataclass(frozen=True)
class ScanResult:
    folder: Path
    recursive: bool
    types: core.PairType
    groups: tuple[core.Group, ...]
    changes: tuple[core.Change, ...]
    warnings: tuple[str, ...]

    @property
    def backups(self) -> int:
        return sum(change.action == 'backup' for change in self.changes)

    @property
    def renames(self) -> int:
        return sum(change.action == 'rename' for change in self.changes)

    @property
    def with_companion(self) -> int:
        return sum(group.sidecar is not None for group in self.groups)

    @property
    def without_companion(self) -> int:
        return len(self.groups) - self.with_companion

    def filter_groups(self, query: str = '', mode: str = 'All') -> list[core.Group]:
        query = query.casefold().strip()
        result = []
        for group in self.groups:
            if mode == 'With companion' and group.sidecar is None:
                continue
            if mode == 'Without companion' and group.sidecar is not None:
                continue
            if query and query not in group.title.casefold() and not any(query in item.path.name.casefold() for item in group.items):
                continue
            result.append(group)
        return result

    def selected_plan(self, excluded: frozenset[Path] | set[Path] | None = None):
        """Select complete groups, never partial actions or partial companion pairs."""
        excluded = excluded or set()
        groups = tuple(g for g in self.groups if g.main.path not in excluded)
        changes = tuple(change for g in groups for change in g.changes)
        return groups, changes

    def selection_report(self, excluded: frozenset[Path] | set[Path] | None = None) -> str:
        groups, changes = self.selected_plan(excluded)
        text = core.render_report(self.folder, self.recursive, self.types, groups, changes, self.warnings)
        hidden = [g for g in self.groups if g.main.path in (excluded or set())]
        if hidden:
            text += '\nEXCLUDED GROUPS (left untouched):\n' + ''.join(
                ' - ' + str(g.main.path.relative_to(self.folder)) + '\n' for g in hidden)
        return text

    def report(self) -> str:
        return core.render_report(self.folder, self.recursive, self.types,
                                  self.groups, self.changes, self.warnings)

    def apply(self, excluded: frozenset[Path] | set[Path] | None = None) -> Path | None:
        # Only complete, included groups reach the transaction. Permanent mode stays disabled.
        groups, changes = self.selected_plan(excluded)
        return core.apply_plan(self.folder, list(groups), list(changes),
                               self.types, permanent=False)


def scan(folder: str | Path, main: str, sidecar: str, recursive: bool,
         cancel_event: Event | None = None) -> ScanResult:
    folder = Path(folder).expanduser().resolve()
    if not folder.is_dir():
        raise ValueError(f'This folder does not exist: {folder}')
    types = core.PairType(main, sidecar)
    groups, changes, warnings = core.build_plan(
        folder, recursive, types, should_cancel=cancel_event.is_set if cancel_event else None)
    return ScanResult(folder, recursive, types, tuple(groups), tuple(changes), tuple(warnings))
