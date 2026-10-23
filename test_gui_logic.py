"""GUI data model regression tests; no display required."""
import tempfile
import unittest
from pathlib import Path
from gui_logic import scan, ScanResult, APP_VERSION

class GuiLogicTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.folder=Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def put(self, *items):
        for name in items:
            path=self.folder/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(name.encode('utf-8'))

    def test_gui_version(self):
        self.assertEqual(APP_VERSION, '3.1.0')

    def test_read_only_preview_and_report(self):
        self.put('Song.mp3','Song(1).mp3','Song(1).lrc')
        result=scan(self.folder,'MP3','LRC',False)
        self.assertEqual(len(result.groups),1)
        self.assertEqual(result.backups,1)
        self.assertEqual(result.renames,2)
        self.assertIn('[BACKUP]',result.report())
        self.assertTrue((self.folder/'Song(1).mp3').exists())

    def test_lyrics_survives_with_correct_contents(self):
        self.put('Song.mp3','Song(1).mp3','Song(1).lrc')
        result=scan(self.folder,'.mp3','.lrc',False)
        saved=result.apply()
        self.assertEqual((self.folder/'Song.mp3').read_bytes(),b'Song(1).mp3')
        self.assertEqual((self.folder/'Song.lrc').read_bytes(),b'Song(1).lrc')
        self.assertTrue((saved/'manifest.json').exists())

    def test_filters(self):
        self.put('A.mp3','A(1).mp3','A(1).lrc','B.mp3','B(1).mp3')
        result=scan(self.folder,'mp3','lrc',False)
        self.assertEqual(len(result.filter_groups(mode='With companion')),1)
        self.assertEqual(len(result.filter_groups(mode='Without companion')),1)
        self.assertEqual(result.filter_groups(query='b')[0].title,'B')
        self.assertEqual(result.filter_groups(query='notfound'),[])

    def test_types(self):
        self.put('Clip.mp4','Clip(1).mp4','Clip(1).srt')
        result=scan(self.folder,'mp4','srt',False)
        self.assertEqual(len(result.groups),1)
        self.assertEqual(result.with_companion,1)
        self.assertEqual(result.without_companion,0)

    def test_recursive_separation_and_unicode(self):
        self.put('Greek/Αγάπη.mp3','Greek/Αγάπη(1).mp3','Czech/Život.mp3','Czech/Život(1).mp3')
        r=scan(self.folder,'mp3','lrc',True)
        self.assertEqual(len(r.groups),2)
        self.assertEqual(r.backups,2)

    def test_stale_plan_fails_before_changes(self):
        self.put('Song.mp3','Song(1).mp3')
        result=scan(self.folder,'.mp3','.lrc',False)
        (self.folder/'Song.mp3').write_text('external change')
        with self.assertRaises(RuntimeError): result.apply()
        self.assertTrue((self.folder/'Song(1).mp3').exists())

    def test_invalid_filetypes_and_folder(self):
        with self.assertRaises(ValueError):scan(self.folder,'MP3','.mp3',False)
        with self.assertRaises(ValueError):scan(self.folder/'absent','mp3','lrc',False)

if __name__=='__main__': unittest.main()
