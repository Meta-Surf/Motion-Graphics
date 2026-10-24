import importlib.util,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,root/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
voice=module('voice','src/providers/voicestudio.py');final=module('final','scripts/finalize_short.py')
class PipelineTest(unittest.TestCase):
 def test_gpu_refuses_cpu_and_accepts_amd_rocm(self):
  with self.assertRaises(RuntimeError):voice.require_gpu({'status':'ok','device':'cpu'})
  voice.require_gpu({'status':'ok','device':'cuda (AMD Radeon RX 7800 XT)'})
 def test_short_chunks_preserve_every_word(self):
  text='Primeira frase. '+('Outra palavra '*25)+'. Final.'
  chunks=voice.split_text(text,70);self.assertEqual(' '.join(chunks).split(),text.split());self.assertTrue(all(len(c)<=70 for c in chunks))
 def test_missing_voice_is_blocked(self):
  m={'format':{'duration':'60'},'streams':[{'codec_type':'video','codec_name':'h264','width':1080,'height':1920}]}
  self.assertTrue(any('AAC' in x for x in final.check_media(m)));self.assertEqual(final.check_media(m,False),[])
if __name__=='__main__':unittest.main()
