import numpy as np, soundfile as sf
def f0(seg, sr):
    seg = seg - seg.mean(); c = np.correlate(seg, seg, 'full')[len(seg) - 1:]
    lo, hi = int(sr / 300), int(sr / 70); i = lo + np.argmax(c[lo:hi]); return sr / i if c[i] > 0.3 * c[0] else None
for n in ('g1', 'g2', 'g3', 'g4', 'd1'):
    a, sr = sf.read(f'vo6/{n}.wav'); hop = int(0.05 * sr); fs = []
    for i in range(0, len(a) - 2 * hop, hop):
        seg = a[i:i + 2 * hop]
        if np.sqrt(np.mean(seg ** 2)) > 0.04: fs.append(f0(seg, sr))
    v = [x for x in fs if x]
    q = np.array(v); thirds = np.array_split(q, 3)
    print(n, 'peak %.2f' % np.abs(a).max(), 'f0 median %.0f Hz, range %.0f-%.0f, by thirds' % (np.median(q), np.percentile(q, 10), np.percentile(q, 90)), [int(np.median(t)) for t in thirds])
