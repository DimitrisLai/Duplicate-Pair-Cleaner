"""Tests for Light / Dark / System appearance settings."""
import json
import tempfile
from pathlib import Path
from unittest import TestCase, mock

import theme_prefs as appearance


class ThemeTests(TestCase):
    def test_modes_and_invalid_preferences(self):
        self.assertEqual(appearance.MODES, ('System', 'Light', 'Dark'))
        self.assertEqual(appearance.normalize_mode('Dark'), 'Dark')
        self.assertEqual(appearance.normalize_mode('dark'), 'System')
        self.assertEqual(appearance.normalize_mode(None), 'System')

    def test_system_resolution(self):
        self.assertEqual(appearance.resolve_mode('System', system_dark=True), 'Dark')
        self.assertEqual(appearance.resolve_mode('System', system_dark=False), 'Light')
        self.assertEqual(appearance.resolve_mode('Light', system_dark=True), 'Light')
        self.assertEqual(appearance.resolve_mode('Dark', system_dark=False), 'Dark')

    def test_black_background_and_high_contrast(self):
        self.assertEqual(appearance.recolor('#F4F7FA', 'Dark'), '#0B0F17')
        self.assertEqual(appearance.recolor('#FFFFFF', 'Dark'), '#192332')
        self.assertEqual(appearance.recolor('#17283C', 'Dark'), '#EAF0F8')
        self.assertEqual(appearance.recolor('#FFFFFF', 'Light'), '#FFFFFF')
        self.assertEqual(appearance.recolor('#123456', 'Dark'), '#123456')

    def test_saved_theme_and_restore(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'settings.json'
            self.assertEqual(appearance.load_theme(path), 'System')
            appearance.save_theme('Dark',path)
            self.assertEqual(json.loads(path.read_text())['theme'], 'Dark')
            self.assertEqual(appearance.load_theme(path), 'Dark')
            appearance.save_theme('Light',path)
            self.assertEqual(appearance.load_theme(path), 'Light')
            appearance.save_theme('weird',path)
            self.assertEqual(appearance.load_theme(path), 'System')

    def test_corrupt_settings_do_not_crash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'settings.json'
            p.write_text('{ definitely not JSON')
            self.assertEqual(appearance.load_theme(p), 'System')
            p.write_text('[]')
            self.assertEqual(appearance.load_theme(p), 'System')

    def test_windows_missing_registry_graceful(self):
        with mock.patch.dict('sys.modules', {'winreg': None}):
            self.assertFalse(appearance.detect_system_dark(platform='win32'))

    def test_linux_system_gtk_theme(self):
        with mock.patch.dict('os.environ', {'GTK_THEME': 'Adwaita:dark', 'COLOR_SCHEME': ''}):
            self.assertTrue(appearance.detect_system_dark(platform='linux'))
        with mock.patch.dict('os.environ', {'GTK_THEME': 'Adwaita', 'COLOR_SCHEME': ''}):
            self.assertFalse(appearance.detect_system_dark(platform='linux'))
