import soundfile as sf, numpy as np, json
def spans(p, thr=0.1):
    a, sr = sf.read(p); h = sr // 100
    r = np.array([np.sqrt(np.mean(a[i:i + h] ** 2)) for i in range(0, len(a), h)]); on = r > thr * r.max()
    segs, s = [], None
    for i, v in enumerate(on):
        if v and s is None: s = i
        if not v and s is not None:
            if i - s > 4: segs.append((s / 100, i / 100))
            s = None
    return segs
ORDER = [('b1', 1.85), ('d1', 0.6), ('b2', 0.8), ('d2', 0.85), ('b3', 0.5), ('b4', 3.6), ('d3', 2.3), ('b5', 0.7)]
T = {}; end = 0
for name, gap in ORDER:
    sg = spans(f'vo2/{name}.wav'); s, e = sg[0][0], sg[-1][1]
    st = gap if name == 'b1' else end + gap; ft = st - s
    T[name] = dict(file_t=round(ft, 3), s=round(st, 3), e=round(ft + e, 3), f=int(round(ft * 30)) + 1,
                   fs=int(round(st * 30)) + 1, fe=int(round((ft + e) * 30)) + 1,
                   words=[int(round((ft + a) * 30)) + 1 for a, b in sg])
    end = ft + e
T['END'] = round(end + 3.1, 2); T['N'] = int(round(T['END'] * 30))
json.dump(T, open('vo2/timing.json', 'w'), indent=1)
for k, v in T.items(): print(k, v)
