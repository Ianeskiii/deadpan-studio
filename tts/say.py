import sys, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro('kokoro-q8.onnx', 'voices.bin')
voice, speed, text, out = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
a, sr = k.create(text, voice=voice, speed=speed, lang='en-us')
sf.write(out, a, sr); print(out, round(len(a)/sr, 2), 's')
