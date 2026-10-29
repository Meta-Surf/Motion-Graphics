"""Regression tests for routing, approval boundaries, actual media and partial invalidation."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from production_workflow import classify,validate_request,plan_request,delivery_report
from video_contract import read_json
import render_chunks as chunks
from gpu_resources import gpu_lease


class ProcedureTest(unittest.TestCase):
    def setUp(self):
        self.request=read_json(ROOT/'examples/production-request.synthetic.json')
        self.caps={tool:dict(state='sampled',evidence='local smoke report') for tool in ('hyperframes','remotion','voicestudio','editonny')}

    def test_classifies_six_task_types(self):
        for text,expected in [('Criar vídeo','creation'),('Editar material','edit'),('Fazer corte','cut'),('Criar motion graphics','motion'),('Revisar vídeo','review'),('Atualizar vídeo','update')]:
            self.assertEqual(classify(text),expected)

    def test_only_missing_decisions_and_subsequent_editonny_reply(self):
        self.request['kind']='edit';self.request['brief']['purpose']=None
        plan=plan_request(self.request,self.caps)
        self.assertEqual(set(plan['questions']),{'purpose','sources.selected_media'})
        self.assertTrue(any('subsequent explicit reply' in g for g in plan['gates']))
        self.request['approvals']['editonny_card']=dict(summary='actual displayed card',shown_at='2026-10-28T19:00:00-03:00',reply='ok',replied_at='2026-10-28T19:00:00-03:00',message_id='user-message')
        with self.assertRaisesRegex(ValueError,'subsequent'):validate_request(self.request)

    def test_preferred_hyperframes_and_supported_remotion_exception(self):
        route=lambda:next(r for r in plan_request(self.request,self.caps)['routes'] if r['stage']=='motion')
        self.assertEqual(route()['tool'],'hyperframes')
        self.request['scenes'][0]['template_id']='object3d'
        self.assertEqual(route()['tool'],'remotion')
        self.request['scenes'][0]['template_id']='titles'
        self.assertTrue(route()['blocked'])
        self.request['scenes'][0]['template_id']='layers';self.request['kind']='update'
        self.assertEqual(route()['tool'],'remotion')

    def test_installation_does_not_establish_capability(self):
        self.caps['hyperframes']=dict(state='installed',evidence='binary exists')
        p=plan_request(self.request,self.caps)
        self.assertEqual(next(r for r in p['routes'] if r['stage']=='motion')['tool'],'remotion')
        self.assertEqual(next(r for r in p['routes'] if r['stage']=='timeline')['tool'],'native-project')

    def test_external_generation_requires_named_budget(self):
        s=self.request['scenes'][0];s.update(asset_strategy='external',provider='cloudflare')
        route=lambda:next(r for r in plan_request(self.request,self.caps)['routes'] if r['stage'].startswith('assets:'))
        self.assertTrue(route()['blocked'])
        self.request['brief']['external'].update(allowed=True,providers=['other'],max_cost=5)
        self.assertTrue(route()['blocked'])
        self.request['brief']['external']['providers']=['cloudflare']
        self.assertFalse(route()['blocked'])

    def test_manifest_rejects_unknown_fields_assets_and_unsubstantiated_review(self):
        for change in (lambda d:d.update(command='execute'),lambda d:d['scenes'][0].update(assets=['missing']),lambda d:d['reviews']['visual'].update(status='passed')):
            d=copy.deepcopy(self.request);change(d)
            with self.assertRaises(ValueError):validate_request(d)

    def test_pending_approval_never_becomes_ready(self):
        p=plan_request(self.request,self.caps)
        self.assertEqual(p['status'],'needs_decisions')
        self.assertEqual(p['questions'],[])
        self.assertTrue(p['gates'])

    def test_shared_lease_blocks_other_worktrees_and_releases_on_failure(self):
        with tempfile.TemporaryDirectory() as t,patch.dict(os.environ,{'MOTION_GPU_LOCK':str(Path(t)/'gpu.lock')}):
            p=Path(t)/'gpu.lock';p.write_text('other job')
            with self.assertRaisesRegex(RuntimeError,'GPU reserved'):
                with gpu_lease('test'):pass
            self.assertEqual(p.read_text(),'other job');p.unlink()
            with self.assertRaises(ValueError):
                with gpu_lease('test'):
                    with gpu_lease('nested'):self.assertTrue(p.exists())
                    raise ValueError('interrupted task')
            self.assertFalse(p.exists())

    def test_block_cache_changes_only_for_visible_dependencies(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'remotion/src').mkdir(parents=True)
            for n in ('package.json','package-lock.json'):(root/'remotion'/n).write_text('{}')
            (root/'remotion/src/index.ts').write_text('source')
            for n in ('a.png','b.png','voice.wav'):(root/n).write_bytes(n.encode())
            props=dict(width=1080,height=1920,fps=30,durationInFrames=5400,audio='voice.wav',scenes=[dict(id='one',image='a.png',fromFrame=0,durationInFrames=2700,title='one'),dict(id='two',image='b.png',fromFrame=2700,durationInFrames=2700,title='two')])
            with patch.object(chunks,'ROOT',root),patch.object(chunks,'public_asset',side_effect=lambda s:root/s):
                key=lambda a,b:chunks.block_fingerprint(props,a,b,1)
                first,second=key(0,2699),key(2700,5399)
                props['scenes'][1]['title']='revised'
                self.assertEqual(first,key(0,2699));self.assertNotEqual(second,key(2700,5399))
                (root/'voice.wav').write_bytes(b'new voice');self.assertEqual(first,key(0,2699))
                (root/'a.png').write_bytes(b'changed');self.assertNotEqual(first,key(0,2699))

    def test_real_decode_rejects_wrong_audio_and_does_not_invent_editorial_review(self):
        with tempfile.TemporaryDirectory() as t:
            video=Path(t)/'sample.mp4'
            subprocess.run(['ffmpeg','-nostdin','-v','error','-f','lavfi','-i','color=c=blue:s=64x64:r=24','-f','lavfi','-i','sine=frequency=220:sample_rate=48000','-t','1','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(video)],check=True)
            self.request['brief']['duration_seconds']=1
            self.request['brief']['format'].update(width=64,height=64)
            report=delivery_report(video,self.request)
            self.assertEqual(report['technical'],'passed');self.assertEqual(report['delivery'],'blocked')
            self.assertIn('playback',report['pending'])
            self.request['brief']['format']['audio_codec']=None
            self.assertEqual(delivery_report(video,self.request)['technical'],'failed')

if __name__=='__main__':unittest.main()
