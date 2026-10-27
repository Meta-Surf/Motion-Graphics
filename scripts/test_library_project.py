"""Integration tests for real WAV timing, layers, language versions and rights gates."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from asset_library import Library
from compile_library_project import compile_project
from render_library_project import require_hardware_render

class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.lib=Library(self.root/'library')
        image=self.root/'cutout.png'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue@0.5:s=32x32,format=rgba','-frames:v','1','-threads','1',str(image)],check=True)
        self.image=self.lib.import_file(image)
        wav=self.root/'voice.wav'
        with wave.open(str(wav),'wb') as w:w.setparams((1,2,8000,0,'NONE','none'));w.writeframes(b'\x01\x00'*64001)
        self.audio=self.lib.import_file(wav)
        self.plan=dict(schema_version=1,project_id='library-test',title='Test',video_type='short_9_16',fps=30,voices={'pt-BR':dict(profile_id='fixture',approval_evidence='test fixture')},scenes=[])
        for name in ['scene-one','scene-two']:
            self.lib.apply(self.image['id'],'library-test',name,'background',True)
            self.lib.apply(self.image['id'],'library-test',name,'object',True)
            self.plan['scenes'].append(dict(id=name,title='Test',objective='Verify real audio duration',template_id='photo_essay',narration={'pt-BR':dict(text='Fixture',asset_id=self.audio['id'])},resources_needed=['background','object'],new_generation_reason=''))
    def tearDown(self):self.lib.close();self.temp.cleanup()
    def compile(self,plan=None,preview=True):return compile_project(plan or self.plan,'pt-BR',self.lib,self.root/'public',preview)
    def test_audio_timing_export_and_provenance(self):
        props=self.compile();self.assertEqual(props['durationInFrames'],482)
        self.assertEqual(props['scenes'][1]['fromFrame'],241)
        self.assertEqual(len(props['scenes'][0]['layers']),1)
        with wave.open(str(self.root/'public'/props['audio'])) as w:
            self.assertEqual(w.getnframes(),round(482*8000/30));self.assertEqual(w.readframes(64001),b'\x01\x00'*64001)
        self.assertTrue((self.root/'public'/props['audio']).with_name('production.json').exists())
    def test_pending_rights_and_selection_do_not_become_production(self):
        with self.assertRaises(ValueError):self.compile(preview=False)
    def test_no_speech_truncation_or_bad_cues(self):
        plan=copy.deepcopy(self.plan);plan['scenes'][0]['duration_seconds']=7
        with self.assertRaises(ValueError):self.compile(plan)
        plan=copy.deepcopy(self.plan);plan['scenes'][0]['captions']={'pt-BR':[dict(text='bad',start_seconds=0,end_seconds=9)]}
        with self.assertRaises(ValueError):self.compile(plan)
    def test_gpu_guard_rejects_software_and_failed_diagnostic(self):
        good='\n'.join(f'{feature}: Hardware accelerated' for feature in ('Canvas','Compositing','Rasterization','WebGL'))
        self.assertIn('WebGL',require_hardware_render(0,good))
        for code,text in [(1,good),(0,good.replace('WebGL: Hardware accelerated','WebGL: Software only')),(0,'')]:
            with self.assertRaises(RuntimeError):require_hardware_render(code,text)
    def test_missing_language_and_duplicate_scenes(self):
        plan=copy.deepcopy(self.plan);plan['scenes'][0]['narration']={'en':plan['scenes'][0]['narration']['pt-BR']}
        with self.assertRaises(ValueError):self.compile(plan)
        plan=copy.deepcopy(self.plan);plan['scenes'][1]['id']=plan['scenes'][0]['id']
        with self.assertRaises(ValueError):self.compile(plan)

if __name__=='__main__':unittest.main()
