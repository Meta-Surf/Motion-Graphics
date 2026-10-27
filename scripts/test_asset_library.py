"""Offline integrity, idempotency, recovery, FTS and gallery boundary tests."""
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from asset_library import Library, restore, sha
from library_server import server

class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.home = Path(self.temp.name)
        self.source = self.home / 'original.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=red@0.5:s=32x32,format=rgba', '-frames:v', '1', '-threads', '1', str(self.source)], check=True)
        self.lib = Library(self.home / 'library')
    def tearDown(self): self.lib.close(); self.temp.cleanup()
    def add(self): return self.lib.import_file(self.source, dict(description='Objeto vermelho', tags=['fino', 'teste']))
    def test_import_deduplicates_and_preserves_sources(self):
        before = sha(self.source); a = self.add(); other = self.home / 'duplicate.png'; shutil.copyfile(self.source, other)
        b = self.lib.import_file(other)
        self.assertEqual(a['id'], b['id']); self.assertEqual(len(b['sources']), 2)
        self.assertEqual(sha(self.source), before); self.assertEqual(len(self.lib.search('vermelho fino')), 1)
        self.assertEqual(a['metadata']['alpha'], 'transparent'); self.assertTrue(a['metadata']['alpha_partial'])
        self.assertEqual(self.lib.verify()['assets'], 1)
    def test_changed_source_gets_new_identity(self):
        a = self.add()
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=blue:s=32x32', '-frames:v', '1', '-threads', '1', str(self.source)], check=True)
        b = self.add(); self.assertNotEqual(a['id'], b['id']); self.assertEqual(b['metadata']['alpha'], 'opaque')
    def test_review_apply_export_and_corruption(self):
        a = self.add()
        with self.assertRaises(ValueError): self.lib.apply(a['id'], 'project', 'scene', 'object')
        with self.assertRaises(ValueError): self.lib.review(a['id'], 'approved', 'unknown', 'unknown', 'ok')
        self.lib.apply(a['id'], 'project', 'scene', 'object', preview=True)
        self.lib.review(a['id'], 'approved', 'fixture-owned', 'generated locally for this test', 'edges checked')
        self.lib.apply(a['id'], 'project', 'scene', 'object')
        rel = self.lib.export(a['id'], self.home / 'public')
        self.assertEqual(sha(self.home / 'public' / rel), a['sha256'])
        self.lib.path(a['file']).write_bytes(b'broken')
        self.assertFalse(self.lib.verify()['ok'])
        with self.assertRaises(ValueError): self.lib.export(a['id'], self.home / 'public')
        with self.assertRaises(ValueError): self.add()
    def test_backup_restore_and_tamper_rejection(self):
        a = self.add(); self.lib.apply(a['id'], 'project', 'scene', 'object', True)
        self.lib.backup(self.home / 'snapshot'); self.assertTrue(restore(self.home / 'snapshot', self.home / 'restored')['ok'])
        restored = Library(self.home / 'restored')
        try:
            self.assertEqual(restored.get(a['id'])['sha256'], a['sha256'])
            self.assertTrue((restored.root / 'projects/project/resources.json').exists())
        finally: restored.close()
        (self.home / 'snapshot' / a['file']).write_bytes(b'tamper')
        with self.assertRaises(ValueError): restore(self.home / 'snapshot', self.home / 'bad')
        self.assertFalse((self.home / 'bad').exists())
    def test_variants_and_lock(self):
        a = self.add()
        with self.assertRaises(ValueError): self.lib.link(a['id'], a['id'], 'mask')
        with self.lib.lock():
            with self.assertRaises(FileExistsError): self.add()
        with self.assertRaises(ValueError): self.lib.path('../escape')
        self.assertEqual(self.lib.search('" OR *'), [])
    def test_component_reference_and_future_schema(self):
        ref=self.home/'layers.motionref'
        ref.write_text(json.dumps(dict(kind='remotion-component',source='remotion/src/MotionTemplates.tsx',template_id='layers')),encoding='utf-8')
        item=self.lib.import_file(ref,category='component')
        self.assertEqual(item['metadata']['component']['template_id'],'layers')
        ref.write_text(json.dumps(dict(kind='remotion-component',source='../outside')),encoding='utf-8')
        with self.assertRaises(ValueError):self.lib.import_file(ref,category='component')
        future=self.home/'future';future.mkdir()
        conn=sqlite3.connect(future/'catalog.sqlite');conn.execute('PRAGMA user_version=999');conn.close()
        with self.assertRaises(ValueError):Library(future)
    def test_gallery_boundaries_and_apply(self):
        a = self.add(); service = server(self.lib.root, 0)
        thread = threading.Thread(target=service.serve_forever, daemon=True); thread.start()
        url = f'http://127.0.0.1:{service.server_port}'
        try:
            with urllib.request.urlopen(url + '/') as r: page = r.read().decode()
            token = page.split("const token='")[1].split("'")[0]
            with urllib.request.urlopen(url + '/api/assets?q=vermelho') as r: self.assertEqual(len(json.load(r)), 1)
            payload = json.dumps(dict(asset_id=a['id'], project='pilot', scene='one', layer='object', preview=True)).encode()
            for headers in ({'Content-Type':'application/json'}, {'Content-Type':'application/json', 'X-Motion-Token':token, 'Origin':'http://evil.invalid'}):
                with self.assertRaises(urllib.error.HTTPError) as error: urllib.request.urlopen(urllib.request.Request(url + '/api/apply', data=payload, headers=headers))
                self.assertEqual(error.exception.code, 403)
            with urllib.request.urlopen(urllib.request.Request(url + '/api/apply', data=payload, headers={'Content-Type':'application/json', 'X-Motion-Token':token})) as r:
                self.assertIn('one', json.load(r)['scenes'])
        finally: service.shutdown(); service.server_close(); thread.join()

if __name__ == '__main__': unittest.main()
