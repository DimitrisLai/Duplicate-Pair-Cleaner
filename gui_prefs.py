"""Validated GUI folder/file-extension preferences (local only, no scan on startup)."""
from __future__ import annotations
import json
import os
from pathlib import Path
from file_pair_cleaner import PairType
from theme_prefs import config_path

PRESET_NAMES = ('Music + lyrics', 'Video + subtitles', 'FLAC + lyrics',
                'Photo + metadata', 'Audio + notes', 'Custom extensions')


def read_settings(path: Path | None = None) -> dict:
    try:
        value = json.loads((path or config_path()).read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def load_preferences(path: Path | None = None) -> dict:
    """Corrupted/missing or outdated preferences revert safely to defaults."""
    values = read_settings(path)
    saved_path = values.get('last_folder', '')
    folder = saved_path if isinstance(saved_path, str) and Path(saved_path).is_dir() else ''
    main, sidecar = '.mp3', '.lrc'
    try:
        pair = PairType(values.get('main_extension', '.mp3'),
                        values.get('companion_extension', '.lrc'))
        main, sidecar = pair.main, pair.sidecar
    except (ValueError, AttributeError, TypeError):
        pass
    preset = values.get('preset', PRESET_NAMES[0])
    if preset not in PRESET_NAMES:
        preset = PRESET_NAMES[-1]
    return {'folder': folder, 'main': main, 'sidecar': sidecar,
            'preset': preset, 'recursive': values.get('recursive') is True}


def save_preferences(folder: str, main: str, sidecar: str,
                     preset: str, recursive: bool, path: Path | None = None) -> None:
    """Write only a validated directory and pair; preserve unrelated/theme settings."""
    pair = PairType(main, sidecar)
    p = path or config_path()
    data = read_settings(p)
    data.update({'last_folder': str(Path(folder).expanduser().resolve()) if Path(folder).is_dir() else '',
                 'main_extension': pair.main, 'companion_extension': pair.sidecar,
                 'preset': preset if preset in PRESET_NAMES else PRESET_NAMES[-1],
                 'recursive': bool(recursive)})
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    os.replace(tmp, p)
