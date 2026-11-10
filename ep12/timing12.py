"""Place each line by conversational gaps (end of previous speech -> start of next speech)."""
import soundfile as sf, numpy as np, json
def speech_span(p):
    a, sr = sf.read(p); h = sr // 100
    r = np.array([np.sqrt(np.mean(a[i:i + h] ** 2)) for i in range(0, len(a), h)]); on = np.where(r > 0.09 * r.max())[0]
    return on[0] / 100, (on[-1] + 1) / 100
ORDER = [('b1', 1.0), ('d1', 0.30), ('b2', 0.42), ('d2', 0.55), ('b3', 0.18), ('b4', 1.2), ('d3', 2.05), ('b5', 0.32), ('b6', 1.05)]
T = {}; end = 0
for name, gap in ORDER:
    s, e = speech_span(f'vo/{name}.wav')
    start_speech = gap if name == 'b1' else end + gap
    file_t = start_speech - s
    T[name] = dict(file_t=round(file_t, 3), s=round(start_speech, 3), e=round(file_t + e, 3),
                   f=int(round(file_t * 30)) + 1, fs=int(round(start_speech * 30)) + 1, fe=int(round((file_t + e) * 30)) + 1)
    end = file_t + e
T['END'] = round(end + 1.15, 2); T['N'] = int(round(T['END'] * 30))
json.dump(T, open('vo/timing.json', 'w'), indent=1)
for k, v in T.items(): print(k, v)
