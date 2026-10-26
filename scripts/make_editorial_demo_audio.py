"""Create a deterministic test signal for audio-driven motion. No voice is used."""
from pathlib import Path
import array,math,wave

output=Path(__file__).resolve().parents[1]/'remotion/public/editorial-demo/signal.wav'
output.parent.mkdir(parents=True,exist_ok=True)
rate=24000;data=array.array('h')
for i in range(rate*3):
    t=i/rate;envelope=(.12+.88*(.5+.5*math.sin(2*math.pi*1.8*t))**3)*min(1,t/.08,(3-t)/.1)
    value=sum(math.sin(2*math.pi*f*t)*a for f,a in [(130.81,.35),(261.63,.25),(523.25,.20),(1046.5,.1),(2093,.05)])
    data.append(round(32767*.35*envelope*value))
with wave.open(str(output),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(data.tobytes())
print(output)
