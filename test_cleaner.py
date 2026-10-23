"""Run with: python -m unittest -v test_cleaner.py"""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import file_pair_cleaner as c


class PairCleanerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.folder = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def put(self, *filenames):
        for name in filenames:
            path = self.folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(name.encode('utf-8'))

    def names(self):
        return {p.name for p in self.folder.iterdir() if p.is_file()}

    def process(self, types=c.PairType(), recursive=False, permanent=False):
        groups, changes, warnings = c.build_plan(self.folder, recursive, types)
        self.assertEqual([], warnings)
        saved = c.apply_plan(self.folder, groups, changes, types, permanent) if changes else None
        return groups, changes, saved

    def test_main_lyric_found_only_on_numbered_variant_case_insensitive(self):
        self.put('Morning Lights - Demo Artist(1).mp3', 'Morning Lights - Demo Artist(1).lrc',
                 'Morning lights - Demo Artist.mp3')
        _, actions, backup = self.process()
        self.assertEqual({'Morning Lights - Demo Artist.mp3', 'Morning Lights - Demo Artist.lrc'}, self.names())
        self.assertEqual(3, len(actions))
        self.assertTrue((backup / 'duplicates' / 'Morning lights - Demo Artist.mp3').exists())

    def test_both_paired_prefers_unnumbered(self):
        self.put('First Light - Example Band.mp3', 'First Light - Example Band.lrc',
                 'First Light - Example Band(1).mp3', 'First Light - Example Band(1).lrc')
        groups, actions, backup = self.process()
        self.assertEqual({'First Light - Example Band.mp3', 'First Light - Example Band.lrc'}, self.names())
        self.assertEqual(2, sum(a.action == 'backup' for a in actions))
        self.assertTrue((backup / 'manifest.json').is_file())

    def test_no_companion_prefers_unnumbered(self):
        self.put('Track.mp3', 'Track(1).mp3', 'Track(2).mp3')
        self.process()
        self.assertEqual({'Track.mp3'}, self.names())

    def test_space_before_suffix_handled(self):
        self.put('Movie.mp4', 'Movie (1).mp4', 'Movie (1).srt')
        self.process(c.PairType('MP4', 'srt'))
        self.assertEqual({'Movie.mp4', 'Movie.srt'}, self.names())
        self.assertEqual(b'Movie (1).mp4', (self.folder / 'Movie.mp4').read_bytes())

    def test_non_default_image_sidecar(self):
        self.put('Photo.jpg', 'Photo(1).jpg', 'Photo(1).xmp')
        _, actions, backup = self.process(c.PairType('JPG', '.XMP'))
        self.assertEqual({'Photo.jpg', 'Photo.xmp'}, self.names())
        self.assertEqual(b'Photo(1).jpg', (self.folder / 'Photo.jpg').read_bytes())
        info = json.loads((backup / 'manifest.json').read_text('utf-8'))
        self.assertEqual('.jpg', info['main_ext'])
        self.assertEqual('.xmp', info['companion_ext'])

    def test_keep_main_with_matching_companion_over_more_preferred_base(self):
        self.put('Song.wav', 'Song(1).wav', 'Song(2).wav', 'Song(2).txt')
        self.process(c.PairType('.wav', '.txt'))
        self.assertEqual({'Song.wav', 'Song.txt'}, self.names())
        self.assertEqual(b'Song(2).wav', (self.folder / 'Song.wav').read_bytes())

    def test_sidecar_without_exact_version_still_retained(self):
        self.put('Song.mp4', 'Song(1).mp4', 'Song(2).srt')
        self.process(c.PairType('mp4', 'srt'))
        self.assertEqual({'Song.mp4', 'Song.srt'}, self.names())
        self.assertEqual(b'Song.mp4', (self.folder / 'Song.mp4').read_bytes())

    def test_one_main_and_other_version_companion_cleaned(self):
        self.put('Song.mp3', 'Song(1).lrc')
        self.process()
        self.assertEqual({'Song.mp3', 'Song.lrc'}, self.names())

    def test_orphan_companions_untouched(self):
        self.put('Track(1).srt', 'Track.srt', 'another(2).srt')
        groups, changes, warnings = c.build_plan(self.folder, False, c.PairType('.mp4', '.srt'))
        self.assertEqual([], groups)
        self.assertEqual([], changes)
        self.assertEqual(3, len(self.names()))

    def test_only_one_numbered_pair_untouched(self):
        self.put('Song(1).jpg', 'Song(1).xmp')
        groups, changes, warnings = c.build_plan(self.folder, False, c.PairType('.jpg', '.xmp'))
        self.assertEqual([], changes)

    def test_only_one_numbered_main_untouched(self):
        self.put('Song (1).wav')
        groups, changes, warnings = c.build_plan(self.folder, False, c.PairType('.wav', '.txt'))
        self.assertEqual([], changes)

    def test_year_and_other_parentheses_not_deduplicated(self):
        self.put('Album.mp3', 'Album (2026).mp3', 'Album (Live).mp3',
                 'Name(1).mp3', 'Unrelated.mp3')
        groups, changes, warnings = c.build_plan(self.folder, False)
        self.assertEqual([], changes)

    def test_scan_only_selected_extensions(self):
        self.put('Song.mp3', 'Song(1).mp3', 'Song(1).lrc', 'Song (1).flac', 'notes.txt')
        self.process()
        self.assertIn('Song (1).flac', self.names())
        self.assertIn('notes.txt', self.names())

    def test_subfolders_independent(self):
        self.put('Disc A/Track.mp3', 'Disc A/Track(1).mp3',
                 'Disc B/Track.mp3', 'Disc B/Track(1).mp3')
        group, actions, saved = self.process(recursive=True)
        self.assertEqual(2, len(group))
        self.assertTrue((self.folder / 'Disc A/Track.mp3').exists())
        self.assertFalse((self.folder / 'Disc A/Track(1).mp3').exists())
        self.assertTrue((self.folder / 'Disc B/Track.mp3').exists())
        self.assertTrue((saved / 'duplicates' / 'Disc A/Track(1).mp3').exists())
        self.assertTrue((saved / 'duplicates' / 'Disc B/Track(1).mp3').exists())

    def test_nonrecursive_ignores_subfolders(self):
        self.put('sub/Song.mp3', 'sub/Song(1).mp3')
        groups, actions, warnings = c.build_plan(self.folder, False)
        self.assertEqual([], actions)

    def test_backup_folders_never_scanned(self):
        self.put('_File_Pair_Cleaner_Backup_OLD/Song.mp3',
                 '_File_Pair_Cleaner_Backup_OLD/Song(1).mp3',
                 '_MP3_LRC_Backup_OLD/Track.mp3',
                 '_MP3_LRC_Backup_OLD/Track(1).mp3')
        self.assertEqual([], c.build_plan(self.folder, True)[1])

    def test_report_contains_extensions_and_actions(self):
        self.put('S.jpg', 'S(1).jpg', 'S(1).xmp')
        types = c.PairType('jpg', 'xmp')
        groups, actions, warnings = c.build_plan(self.folder, False, types)
        report = c.render_report(self.folder, False, types, groups, actions, warnings)
        for word in ['GROUP 001/001', '[BACKUP]', '[RENAME]', '[MAIN .jpg]', '[PAIR .xmp]',
                     'Main extension: .jpg', 'AFTER CLEANUP']:
            self.assertIn(word, report)
        self.assertTrue((self.folder / 'S(1).jpg').is_file())  # preview really is read-only

    def test_page_q_can_cancel_before_apply(self):
        self.put('A.mp3', 'A(1).mp3', 'B.mp3', 'B(1).mp3')
        types = c.PairType()
        groups, actions, warnings = c.build_plan(self.folder, False, types)
        with patch('builtins.input', return_value='Q'), redirect_stdout(io.StringIO()) as output:
            result = c.print_plan(self.folder, False, types, groups, actions, warnings, page_size=1)
        self.assertFalse(result)
        self.assertIn('GROUP 001/002', output.getvalue())
        self.assertNotIn('GROUP 002/002', output.getvalue())
        self.assertTrue((self.folder / 'A(1).mp3').exists())

    def test_parse_extension_validation(self):
        self.assertEqual('.mp3', c.parse_extension('  MP3 '))
        self.assertEqual('.srt', c.parse_extension(' .SRT '))
        for invalid in ['', '.', '../txt', '*.mp3', 'A.B', '.foo/bar', 'reallyverylongextension']:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                c.parse_extension(invalid)
        with self.assertRaises(ValueError):
            c.PairType('.mp3', 'MP3')

    def test_interactive_ext_defaults_and_retry(self):
        with patch('builtins.input', side_effect=['wav', 'wav', 'MP4', '.srt']), redirect_stdout(io.StringIO()):
            result = c.ask_extensions(c.PairType())
        self.assertEqual(c.PairType('.mp4', '.srt'), result)
        with patch('builtins.input', side_effect=['', '']):
            self.assertEqual(c.PairType(), c.ask_extensions(c.PairType()))

    def test_preview_cli_custom_extensions(self):
        self.put('Song.mp4', 'Song (1).mp4', 'Song (1).srt')
        report = self.folder / 'preview.txt'
        with redirect_stdout(io.StringIO()):
            code = c.main(['--folder', str(self.folder), '--main-ext', 'mp4', '--companion-ext', 'SRT',
                           '--preview', '--save-report', str(report)])
        self.assertEqual(0, code)
        self.assertIn('[MAIN .mp4]', report.read_text(encoding='utf-8-sig'))
        self.assertTrue((self.folder / 'Song (1).mp4').exists())

    def test_folder_dialog_cancel(self):
        with patch.object(c, 'choose_folder', return_value=None), redirect_stdout(io.StringIO()) as output:
            code = c.main(['--select-folder'])
        self.assertEqual(0, code)
        self.assertIn('cancelled', output.getvalue())

    def test_cli_interactive_selects_extensions_and_subfolders(self):
        self.put('sub/Photo.jpg', 'sub/Photo(1).jpg', 'sub/Photo(1).xmp')
        with patch.object(c, 'choose_folder', return_value=self.folder), \
             patch('builtins.input', side_effect=['jpg', 'xmp', 'y']), \
             redirect_stdout(io.StringIO()) as output:
            result = c.main(['--select-folder', '--ask-extensions', '--ask-subfolders', '--preview'])
        self.assertEqual(0, result)
        self.assertIn('GROUP 001/001', output.getvalue())
        self.assertTrue((self.folder / 'sub/Photo(1).jpg').exists())

    def test_detect_changed_files_since_preview(self):
        self.put('S.mp3', 'S(1).mp3')
        types = c.PairType()
        groups, actions, warnings = c.build_plan(self.folder, False, types)
        (self.folder / 'S.mp3').write_bytes(b'changed')
        with self.assertRaisesRegex(RuntimeError, 'changed since the preview'):
            c.apply_plan(self.folder, groups, actions, types)
        self.assertTrue((self.folder / 'S(1).mp3').exists())

    def test_permanent_mode_only_when_requested(self):
        self.put('S.mp3', 'S(1).mp3')
        groups, actions, saved = self.process(permanent=True)
        self.assertIsNone(saved)
        self.assertEqual({'S.mp3'}, self.names())
        self.assertFalse(any(p.is_dir() for p in self.folder.iterdir()))

    def test_no_overwrites_with_conflicting_name_case(self):
        # Only possible on a case-sensitive filesystem; planner must skip ambiguous families.
        self.put('A.mp3', 'A(1).mp3', 'a(1).mp3')
        # Windows default filesystem is case-insensitive: these two variants
        # cannot coexist and so cannot form an ambiguous duplicate family.
        if len(list(self.folder.glob('*(1).mp3'))) < 2:
            self.skipTest('Case-conflicting duplicate names cannot coexist on this filesystem')
        groups, changes, warnings = c.build_plan(self.folder, False)
        self.assertEqual([], changes)
        self.assertTrue(warnings)

    def test_version_flag(self):
        with redirect_stdout(io.StringIO()) as output, self.assertRaises(SystemExit) as result:
            c.main(['--version'])
        self.assertEqual(0, result.exception.code)
        self.assertIn('3.5.0', output.getvalue())

    def test_skip_git_and_virtualenv_directories(self):
        self.put('.git/Song.mp3', '.git/Song(1).mp3',
                 '.venv/Track.mp3', '.venv/Track(1).mp3',
                 '__pycache__/Noise.mp3', '__pycache__/Noise(1).mp3')
        self.assertEqual([], c.build_plan(self.folder, True)[1])

    def test_numbered_multiple_versions_prefers_lowest_with_companion(self):
        self.put('Demo.mp3', 'Demo(1).mp3', 'Demo(2).mp3', 'Demo(2).lrc')
        self.process()
        self.assertEqual(b'Demo(2).mp3', (self.folder / 'Demo.mp3').read_bytes())
        self.assertTrue((self.folder / 'Demo.lrc').exists())

    def test_preview_only_keeps_all_files(self):
        self.put('Clip.mp4', 'Clip(1).mp4', 'Clip(1).srt')
        with redirect_stdout(io.StringIO()):
            result = c.main(['--folder', str(self.folder), '--main-ext', 'mp4',
                             '--companion-ext', 'srt', '--preview'])
        self.assertEqual(0, result)
        self.assertEqual({'Clip.mp4', 'Clip(1).mp4', 'Clip(1).srt'}, self.names())

    def test_ctrl_c_during_rename_rolls_back_every_file(self):
        self.put('Song.mp3', 'Song(1).mp3', 'Song(1).lrc')
        groups, actions, warnings = c.build_plan(self.folder, False)
        self.assertFalse(warnings)
        original_rename = Path.rename
        tripped = False

        def interrupt_on_final_mp3(path, target):
            nonlocal tripped
            if not tripped and Path(target) == self.folder / 'Song.mp3' and path.name.endswith('.mp3'):
                tripped = True
                raise KeyboardInterrupt()
            return original_rename(path, target)

        with patch.object(Path, 'rename', interrupt_on_final_mp3):
            with self.assertRaises(KeyboardInterrupt):
                c.apply_plan(self.folder, groups, actions, c.PairType())
        self.assertEqual({'Song.mp3', 'Song(1).mp3', 'Song(1).lrc'}, self.names())
        self.assertFalse(any(p.name.startswith(c.BACKUP_PREFIX) for p in self.folder.iterdir()))

    def test_destination_created_after_preview_fails_before_changes(self):
        self.put('Song.mp3', 'Song(1).mp3', 'Song(1).lrc')
        groups, actions, warnings = c.build_plan(self.folder, False)
        self.assertFalse(warnings)
        # A previously nonexistent target is newly created by another program.
        (self.folder / 'Song.lrc').write_text('new independent file')
        with self.assertRaisesRegex(RuntimeError, 'occupied after preview'):
            c.apply_plan(self.folder, groups, actions, c.PairType())
        self.assertEqual({'Song.mp3', 'Song(1).mp3', 'Song(1).lrc', 'Song.lrc'}, self.names())
        self.assertFalse(any(p.name.startswith(c.BACKUP_PREFIX) for p in self.folder.iterdir()))

    def test_rename_failure_rolls_back_originals(self):
        self.put('Song.mp3', 'Song(1).mp3', 'Song(1).lrc')
        groups, actions, warnings = c.build_plan(self.folder, False)
        original_rename = Path.rename
        triggered = False

        def fail_once(path, target):
            nonlocal triggered
            if not triggered and Path(target) == self.folder / 'Song.mp3' and path.name.endswith('.mp3'):
                triggered = True
                raise OSError('simulated file rename failure')
            return original_rename(path, target)

        with patch.object(Path, 'rename', fail_once):
            with self.assertRaisesRegex(OSError, 'simulated file rename failure'):
                c.apply_plan(self.folder, groups, actions, c.PairType())
        self.assertEqual({'Song.mp3', 'Song(1).mp3', 'Song(1).lrc'}, self.names())
        self.assertFalse(any(p.name.startswith(c.BACKUP_PREFIX) for p in self.folder.iterdir()))

    def test_unsupported_arguments_error(self):
        with self.assertRaises(SystemExit):
            c.main(['--main-ext', 'mp3', '--companion-ext', '.MP3'])
        with self.assertRaises(SystemExit):
            c.main(['--preview', '--apply'])


if __name__ == '__main__':
    unittest.main()
