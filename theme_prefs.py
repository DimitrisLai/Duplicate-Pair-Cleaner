"""Light/Dark/System appearance settings for Duplicate Pair Cleaner.

No external dependencies. Theme choice persists locally; it is not telemetry.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

MODES = ('System', 'Light', 'Dark')

# The original v3.0.0 palette is retained for the Light theme.
# Dark uses deliberately near-black backgrounds, readable text, and teal accents.
DARK_COLORS = {
    '#0b172b': '#080E1B',  # header
    '#142a43': '#162638',
    '#07988b': '#30D5C2',  # teal controls/sections
    '#f4f7fa': '#0B0F17',  # application background
    '#dae3ea': '#303C4D',
    '#17283c': '#EAF0F8',  # main text
    '#657589': '#AABACC',  # secondary text
    '#ffffff': '#192332',  # panels
    '#a73142': '#FF98A0',
    '#93641c': '#F2BE65',
    '#e9f0f5': '#26374A',  # secondary buttons
    '#dce9f2': '#344B61',
    '#086c68': '#178E82',
    '#fceff0': '#4E303A',  # danger button
    '#def3ef': '#174D45',  # selected row
    '#edf3f7': '#25364B',  # tree heading
    '#e5ecef': '#243448',  # progress trough
    '#e8edf2': '#2C4054',  # sash
    '#f7fafb': '#111B29',  # detail panel
    '#a26a16': '#F6BD64',  # rename
    '#067e6d': '#61E6C7',  # keep
    '#31c6b8': '#43E1D2',  # header logo
    '#b4c8d8': '#B4CADB',
    '#8ddace': '#A1ECDA',
}


def normalize_mode(mode: str | None) -> str:
    """Normalize stored or user-selected modes; never execute arbitrary settings."""
    return mode if mode in MODES else 'System'


def detect_system_dark(platform: str | None = None) -> bool:
    """Respect Windows' per-user app setting. Safe fallbacks on other systems."""
    platform = platform or sys.platform
    if platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize') as key:
                value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                return int(value) == 0
        except (OSError, ImportError, ValueError):
            return False
    if platform == 'darwin':
        try:
            return subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                                  capture_output=True, text=True, timeout=2,
                                  check=False).stdout.strip().casefold() == 'dark'
        except (OSError, subprocess.TimeoutExpired):
            return False
    return any('dark' in os.getenv(key, '').lower()
               for key in ('GTK_THEME', 'COLOR_SCHEME'))


def resolve_mode(mode: str, *, system_dark: bool | None = None) -> str:
    mode = normalize_mode(mode)
    if mode != 'System':
        return mode
    return 'Dark' if (detect_system_dark() if system_dark is None else system_dark) else 'Light'


def config_path() -> Path:
    if sys.platform == 'win32':
        root = Path(os.getenv('APPDATA', str(Path.home() / 'AppData' / 'Roaming')))
    else:
        root = Path(os.getenv('XDG_CONFIG_HOME', str(Path.home() / '.config')))
    return root / 'DuplicatePairCleaner' / 'settings.json'


def load_theme(path: Path | None = None) -> str:
    try:
        data = json.loads((path or config_path()).read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            return 'System'
        return normalize_mode(data.get('theme'))
    except (OSError, ValueError, TypeError):
        return 'System'


def save_theme(theme: str, path: Path | None = None) -> None:
    """Save only appearance preference; an atomic replacement avoids a half-written file."""
    theme = normalize_mode(theme)
    p = path or config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.tmp')
    try:
        existing = json.loads(p.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        existing = {}
    if not isinstance(existing, dict):
        existing = {}
    existing['theme'] = theme
    tmp.write_text(json.dumps(existing, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, p)


def recolor(original: str, mode: str) -> str:
    if mode != 'Dark':
        return original
    return DARK_COLORS.get(original.lower(), original)
