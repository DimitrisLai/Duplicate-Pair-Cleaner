"""v3.5 final-feature regression tests: preferences, cancellation, per-group choice."""
from __future__ import annotations
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import file_pair_cleaner as core
from gui_logic import scan, APP_VERSION
from gui_prefs import load_preferences, save_preferences
from theme_prefs import load_theme, save_theme


class FinalReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def put(self, *paths):
        for name in paths:
            p=self.root/name
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(name.encode())

    def test_version(self):
        self.assertEqual(APP_VERSION,'3.5.0')
        self.assertEqual(core.VERSION,'3.5.0')

    def test_round_trip_prefs_and_theme(self):
        cfg=self.root/'prefs/settings.json'
        save_theme('Dark',cfg)
        save_preferences(str(self.root),'MP4','SRT','Video + subtitles',True,cfg)
        prefs=load_preferences(cfg)
        self.assertEqual(prefs,{'folder':str(self.root),'main':'.mp4','sidecar':'.srt',
                                'preset':'Video + subtitles','recursive':True})
        self.assertEqual(load_theme(cfg),'Dark')
        save_theme('Light',cfg)
        self.assertEqual(load_preferences(cfg),prefs)
        self.assertNotIn('Song.mp3',cfg.read_text())

    def test_invalid_prefs_are_safe(self):
        cfg=self.root/'prefs/settings.json'
        cfg.parent.mkdir()
        cfg.write_text('{ broken json',encoding='utf-8')
        self.assertEqual(load_preferences(cfg)['main'],'.mp3')
        cfg.write_text(json.dumps({'last_folder':'Z:/not-real','main_extension':'.mp3',
                                   'companion_extension':'mp3','recursive':'yes','preset':'bogus'}))
        pref=load_preferences(cfg)
        self.assertEqual(pref['folder'],'')
        self.assertEqual((pref['main'],pref['sidecar']),('.mp3','.lrc'))
        self.assertFalse(pref['recursive'])
        with self.assertRaises(ValueError):
            save_preferences(str(self.root),'mp3','mp3','Music + lyrics',False,cfg)

    def test_cancel_before_scan(self):
        self.put('A.mp3','A(1).mp3')
        event=threading.Event();event.set()
        before=sorted(p.name for p in self.root.iterdir())
        with self.assertRaises(core.ScanCancelled):
            scan(self.root,'mp3','lrc',False,event)
        self.assertEqual(before,sorted(p.name for p in self.root.iterdir()))

    def test_cancel_mid_scan_never_returns_partial_plan(self):
        self.put(*[f'Song_{i}.mp3' for i in range(120)],
                 *[f'Song_{i}(1).mp3' for i in range(120)])
        event=threading.Event()
        orig=core.iter_selected
        def interrupt(*args):
            for index,path in enumerate(orig(*args)):
                if index==30: event.set()
                yield path
        with patch.object(core,'iter_selected',side_effect=interrupt):
            with self.assertRaises(core.ScanCancelled):
                scan(self.root,'mp3','lrc',False,event)
        self.assertEqual(len(list(self.root.iterdir())),240)
        self.assertFalse(any(p.name.startswith(core.BACKUP_PREFIX) for p in self.root.iterdir()))

    def test_cancel_during_group_planning(self):
        self.put('A.mp3','A(1).mp3')
        calls=0
        def flag():
            nonlocal calls
            calls+=1
            return calls>=6
        with self.assertRaises(core.ScanCancelled):
            core.build_plan(self.root,False,core.PairType(),should_cancel=flag)
        self.assertEqual(len(list(self.root.iterdir())),2)

    def test_exclude_one_complete_group(self):
        self.put('A.mp3','A(1).mp3','A(1).lrc','B.mp3','B(1).mp3','B(1).lrc')
        result=scan(self.root,'mp3','lrc',False)
        excluded={next(g.main.path for g in result.groups if g.title=='A')}
        groups, changes=result.selected_plan(excluded)
        self.assertEqual([g.title for g in groups],['B'])
        self.assertEqual(len(changes),3)
        text=result.selection_report(excluded)
        self.assertIn('EXCLUDED GROUPS',text)
        self.assertIn('A(1).mp3',text)
        backup=result.apply(excluded)
        self.assertEqual((self.root/'A.mp3').read_bytes(),b'A.mp3')
        self.assertEqual((self.root/'A(1).mp3').read_bytes(),b'A(1).mp3')
        self.assertEqual((self.root/'A(1).lrc').read_bytes(),b'A(1).lrc')
        self.assertEqual((self.root/'B.mp3').read_bytes(),b'B(1).mp3')
        self.assertEqual((self.root/'B.lrc').read_bytes(),b'B(1).lrc')
        manifest=json.loads((backup/'manifest.json').read_text())
        self.assertFalse(any('A' in str(x) for field in ('moved_to_backup','renamed') for x in manifest[field]))

    def test_exclude_all_keeps_everything(self):
        self.put('A.mp3','A(1).mp3','B.mp3','B(1).mp3')
        result=scan(self.root,'mp3','lrc',False)
        excluded={g.main.path for g in result.groups}
        self.assertEqual(result.selected_plan(excluded),((),()))
        self.assertIsNone(result.apply(excluded))
        self.assertEqual(len(list(self.root.iterdir())),4)

    def test_recursive_same_name_exclusions_are_directory_specific(self):
        self.put('One/Song.mp3','One/Song(1).mp3',
                 'Two/Song.mp3','Two/Song(1).mp3')
        result=scan(self.root,'mp3','lrc',True)
        excluded={g.main.path for g in result.groups if g.main.path.parent.name=='Two'}
        backup=result.apply(excluded)
        self.assertTrue(backup.exists())
        self.assertTrue((self.root/'One/Song.mp3').exists())
        self.assertFalse((self.root/'One/Song(1).mp3').exists())
        self.assertTrue((self.root/'Two/Song(1).mp3').exists())

    def test_stale_included_group_still_blocks_transaction(self):
        self.put('A.mp3','A(1).mp3','B.mp3','B(1).mp3')
        result=scan(self.root,'mp3','lrc',False)
        exclude={g.main.path for g in result.groups if g.title=='A'}
        (self.root/'B.mp3').write_text('modified after preview')
        with self.assertRaises(RuntimeError):result.apply(exclude)
        self.assertTrue((self.root/'A(1).mp3').exists())
        self.assertTrue((self.root/'B(1).mp3').exists())

if __name__=='__main__':unittest.main()
