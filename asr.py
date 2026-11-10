import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[1], device='cpu', compute_type='int8', cpu_threads=2)
def load16(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)
for p in sys.argv[2:]:
    segs, info = m.transcribe(load16(p), language='en', beam_size=5, word_timestamps=True, condition_on_previous_text=False, vad_filter=False)
    words = [(w.word.strip(), round(w.start, 2), round(w.end, 2), round(w.probability, 2)) for s in segs for w in s.words]
    print(p.split('/')[-1], '|', ' '.join(w[0] for w in words), '|', words, flush=True)
