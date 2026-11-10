import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[1], device='cpu', compute_type='int8', cpu_threads=2)
for p in sys.argv[2:]:
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout
    segs, info = m.transcribe(np.frombuffer(raw, np.float32), language='ja', beam_size=5, condition_on_previous_text=False)
    print(p.split('/')[-1], '|', ''.join(s.text for s in segs).strip(), '|', round(info.duration, 2), flush=True)
