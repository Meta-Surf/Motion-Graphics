"""Offline contract and filesystem regression tests; never call paid providers."""
import copy, hashlib, importlib.util, json, sys, tempfile, unittest, wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from hyperframes_bridge import compile_hyperframes,group_words,safe_asset
from hyperframes_models import verify,install
from hyperframes_cli import main as local_cli

def props():
    return dict(schema_version=1,project_id='offline-probe',title='Offline',video_type='short_9_16',fps=24,width=1080,height=1920,durationInFrames=360,audio='generated/probe/voice.wav',scenes=[dict(id='scene-one',template_id='photo_essay',title='<script>alert("x")</script>',fromFrame=0,durationInFrames=360,image='generated/probe/photo.svg',labels=[])])

class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.public=self.root/'public';self.media=self.public/'generated/probe';self.media.mkdir(parents=True)
        (self.media/'photo.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920"><rect width="1080" height="1920" fill="#124355"/></svg>')
        with wave.open(str(self.media/'voice.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(b'\0\0'*16000*15)
        self.gsap=self.root/'gsap.js';self.gsap.write_text('// fixture runtime')
        self.out=self.root/'project'
    def tearDown(self):self.temp.cleanup()
    def compile(self,p=None,**kwargs):return compile_hyperframes(p or props(),self.public,self.out,self.gsap,**kwargs)
    def test_compiles_escaped_scene_and_separate_caption_track(self):
        self.compile(words=[dict(text='measured',start=.2,end=1)])
        s=(self.out/'compositions/scene-000.html').read_text();self.assertIn('&lt;script&gt;',s);self.assertNotIn('<script>alert',s)
        self.assertIn('data-track-kind="captions"',(self.out/'index.html').read_text())
    def test_reuses_content_hash_for_identical_assets(self):
        p=props();other=copy.deepcopy(p['scenes'][0]);other.update(id='scene-two',fromFrame=180,durationInFrames=180);p['scenes'][0]['durationInFrames']=180;p['scenes'].append(other)
        self.compile(p);self.assertEqual(json.loads((self.out/'production.json').read_text())['unique_assets'],2)
    def test_foregrounds_use_contained_safe_stage(self):
        p=props();p['scenes'][0]['template_id']='layers';p['scenes'][0]['layers']=[dict(id='foreground',image='generated/probe/photo.svg',x=.5,y=.5,width=.68,depth=1)]
        self.compile(p);self.assertIn('object-fit:contain',(self.out/'compositions/scene-000.html').read_text())
    def test_foreground_outside_safe_stage_is_rejected(self):
        p=props();p['scenes'][0]['template_id']='layers';p['scenes'][0]['layers']=[dict(id='foreground',image='generated/probe/photo.svg',x=.9,y=.5,width=.68,depth=1)]
        with self.assertRaisesRegex(ValueError,'protected hero'):self.compile(p)
        self.assertFalse(self.out.exists())
    def test_preflight_rejects_parent_traversal_without_output(self):
        p=props();p['scenes'][0]['image']='generated/probe/../../../outside.png'
        with self.assertRaises(ValueError):self.compile(p)
        self.assertFalse(self.out.exists())
    def test_rejects_external_and_windows_paths(self):
        for path in ['https://example.org/a.png','C:\\secret.png','/etc/passwd']:
            with self.assertRaises(ValueError):safe_asset(self.public,path)
    def test_refuses_existing_destination(self):
        self.out.mkdir();(self.out/'keep').write_text('private')
        with self.assertRaises(ValueError):self.compile()
        self.assertEqual((self.out/'keep').read_text(),'private')
    def test_does_not_silently_convert_3d(self):
        p=props();p['scenes'][0]['template_id']='object3d'
        with self.assertRaisesRegex(ValueError,'requires Remotion'):self.compile(p)
        self.assertFalse(self.out.exists())
    def test_audio_determines_duration(self):
        p=props();p['durationInFrames']=384;p['scenes'][0]['durationInFrames']=384
        with self.assertRaisesRegex(ValueError,'WAV duration'):self.compile(p)
    def test_words_reject_nan_negative_and_reverse(self):
        for start,end in [(-1,.1),(1,.5),(0,float('nan')),(0,16)]:
            with self.assertRaises(ValueError):group_words([dict(text='word',start=start,end=end)],15)
    def test_words_respect_pauses_word_limit_and_punctuation(self):
        words=[dict(text=str(i),start=i*.2,end=i*.2+.1) for i in range(8)]
        self.assertEqual([len(g['text'].split()) for g in group_words(words,15)], [5,3])
        self.assertEqual(len(group_words([dict(text='First.',start=0,end=.2),dict(text='Next',start=.2,end=.4)],15)),2)
    def test_overlapping_words_are_rejected_at_cue_gate(self):
        with self.assertRaises(ValueError):self.compile(words=[dict(text='First.',start=.1,end=1),dict(text='Next',start=.5,end=.6)])
    def test_local_cli_blocks_cloud_and_publishing(self):
        for command in ['cloud','lambda','cloudrun','publish']:
            with self.assertRaisesRegex(ValueError,'local-only'):local_cli([command])
    def test_model_checksum_validation(self):
        p=self.root/'weight';p.write_bytes(b'abc');spec=dict(bytes=3,sha256=hashlib.sha256(b'abc').hexdigest())
        self.assertTrue(verify(p,spec));p.write_bytes(b'abd');self.assertFalse(verify(p,spec))
    def test_model_download_must_be_explicit(self):
        with self.assertRaisesRegex(ValueError,'explicitly'):install('u2netp',self.root/'models')
        self.assertFalse((self.root/'models').exists())
    def test_invalid_model_never_overwrites_cache(self):
        cache=self.root/'models';cache.mkdir();p=cache/'u2netp.onnx';p.write_bytes(b'user-data')
        with self.assertRaisesRegex(ValueError,'not overwritten'):install('u2netp',cache)
        self.assertEqual(p.read_bytes(),b'user-data')
if __name__=='__main__':unittest.main()
