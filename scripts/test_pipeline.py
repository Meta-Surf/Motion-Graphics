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
 def test_reference_leakage_is_blocked(self):
  with self.assertRaises(RuntimeError):voice.check_transcript('Tudo para transformar dados em respostas.','Creators, tudo para transformar dados em respostas.')
  self.assertEqual(voice.check_transcript('Inteligência artificial.','Inteligencia artificial!'),1.0)
 def test_missing_voice_is_blocked(self):
  m={'format':{'duration':'60'},'streams':[{'codec_type':'video','codec_name':'h264','width':1080,'height':1920}]}
  self.assertTrue(any('AAC' in x for x in final.check_media(m)));self.assertEqual(final.check_media(m,False),[])
 def test_finalizer_accepts_both_new_format_limits(self):
  for kind,width,height,minimum,maximum in [('short_9_16',1080,1920,15,180),('long_16_9',1920,1080,480,1800)]:
   for duration in [minimum,maximum]:
    media={'format':{'duration':str(duration)},'streams':[{'codec_type':'video','codec_name':'h264','width':width,'height':height},{'codec_type':'audio','codec_name':'aac','duration':str(duration)}]}
    self.assertEqual(final.check_media(media,video_type=kind),[])
   media['format']['duration']=str(maximum+1)
   self.assertTrue(final.check_media(media,video_type=kind))
if __name__=='__main__':unittest.main()
