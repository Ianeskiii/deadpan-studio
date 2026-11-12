"""Phase 0: decode the owner's five MP3s (as-is: no TTS, no speed or pitch change) to vo/<name>.wav (48 kHz mono),
measure the speech window of each (RMS at -40 dBFS) and check the words with faster-whisper in Tagalog, once with
no hint and once with the script as a hint.  Writes vo/measure.json."""
import json, subprocess, numpy as np, soundfile as sf, os
from faster_whisper import WhisperModel
SRC = '../shorts/mama-fake-news'
LINES = [('mom_dialogue_1', 'NAK! PATAY NA SI JACKIE CHAN!'), ('doug_dialogue_1', "Ma, fake news 'yan. Buhay pa 'yan."),
         ('mom_dialogue_2', 'Hindi ah! Nasa Facebook oh!'), ('doug_dialogue_2', "Ma... 2016 pa 'tong post."),
         ('mom_dialogue_3', 'AY GANUN? MATAGAL NA PALANG PATAY?!')]
os.makedirs('vo', exist_ok=True)
m = WhisperModel('../whisper_small', device='cpu', compute_type='int8', cpu_threads=4)
out = {}
for name, txt in LINES:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{SRC}/{name}.mp3', '-ac', '1', '-ar', '48000', f'vo/{name}.wav'], check=True)
    a, sr = sf.read(f'vo/{name}.wav'); h = sr // 100
    r = np.array([np.sqrt(np.mean(a[i:i + h] ** 2)) for i in range(0, len(a) - h, h)])
    db = 20 * np.log10(r + 1e-9); on = np.where(db > -40)[0]
    s, e = on[0] / 100, (on[-1] + 1) / 100
    a16 = np.interp(np.arange(int(len(a) * 16000 / sr)) * sr / 16000, np.arange(len(a)), a).astype(np.float32)
    res = {}
    for k, prompt in (('plain', None), ('hint', txt)):
        segs, _ = m.transcribe(a16, language='tl', beam_size=5, word_timestamps=True, condition_on_previous_text=False, initial_prompt=prompt)
        res[k] = ' '.join(w.word.strip() for sg in segs for w in sg.words)
    out[name] = dict(text=txt, dur=round(len(a) / sr, 3), s=s, e=e, peak_db=round(20 * np.log10(np.abs(a).max()), 1), **res)
    print(name, out[name], flush=True)
json.dump(out, open('vo/measure.json', 'w'), indent=1)
