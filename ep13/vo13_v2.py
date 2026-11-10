"""V2 voices: same lines, same timing slots as vo13.py (vo/timing.json), but performed as a fight.
Kokoro has no emotion control, so the shout is built in two layers:
  1. phonemes: held final vowels and a hard cut-off at the end (anime shout endings), commas for a beat;
  2. WORLD vocoder: higher pitch, wider pitch swings with an arc that peaks mid-line, a little strain jitter,
     a brighter (shouted) spectrum, then time-fitted back into the original slot so the TV lip flaps still match.
Writes vo2/l<NN>.wav plus vo2/breath_<NN>.wav for the inhales in the early gaps."""
import sys, os, json, numpy as np, soundfile as sf, pyworld as pw
sys.path.insert(0, '.'); from jtts import G, K
SR = 24000
T = json.load(open('vo/timing.json')); L = T['lines']
os.makedirs('vo2', exist_ok=True)
rng = np.random.default_rng(7)

def ph(text):
    r = G(text); return r[0] if isinstance(r, tuple) else r

# (text for G2P, hold final vowel?, kokoro speed, pitch shift st, contour gain, arc st, brightness)
# Early lines: angry but still words; the barrage: barked, higher, clipped.
P = [
 ('お前には、負けない！',      True,  0.95, 2.5, 1.55, 2.0, 0.7),
 ('まだ、終わっていない！',    True,  1.0,  2.0, 1.5,  1.8, 0.6),
 ('なぜ、戦うんだ！',          True,  0.95, 2.0, 1.4,  1.8, 0.6),
 ('答える必要は、ない！',      True,  1.05, 2.0, 1.45, 1.6, 0.6),
 ('約束したからだ！',          True,  1.1,  3.0, 1.6,  2.2, 0.8),
 ('くだらない！',              True,  1.15, 2.5, 1.5,  2.0, 0.7),
 ('大事なんだ！',              True,  1.15, 3.5, 1.6,  2.4, 0.85),
 ('黙れ！',                    False, 1.05, 2.0, 1.35, 2.0, 0.6),
 ('嫌だ！',                    True,  1.1,  4.0, 1.6,  2.5, 0.9),
 ('行くぞ！',                  True,  1.1,  3.0, 1.5,  2.5, 0.8),
 ('今だ！',                    True,  1.1,  4.0, 1.6,  2.8, 0.9),
 ('させるか！',                True,  1.15, 3.5, 1.5,  2.5, 0.85),
 ('そこだ！',                  True,  1.1,  4.5, 1.6,  3.0, 0.95),
 ('まだだ！',                  True,  1.15, 4.0, 1.5,  3.0, 0.9),
 ('終わりだ！',                True,  1.1,  5.0, 1.7,  3.2, 1.0),
 ('負けない！',                True,  1.15, 4.5, 1.6,  3.0, 0.95),
 ('なにっ！',                  False, 1.1,  5.5, 1.5,  2.0, 1.0),
]
VOW = 'aiueoɯ'

def shout_phonemes(text, hold):
    p = ph(text).rstrip('!').rstrip('ʔ')
    if hold:  # hold the last vowel and cut it off hard: "makenaiː ʔ!"
        j = max(p.rfind(v) for v in VOW)
        if j >= 0 and (j + 1 >= len(p) or p[j + 1] != 'ː'): p = p[:j + 1] + 'ː' + p[j + 1:]
    return p + '!'   # no glottal stop: Kokoro turns it into a junk tail ("...desu")

def world_shout(x, st, gain, arc, bright, target_len):
    x = x.astype(np.float64)
    f0, t = pw.harvest(x, SR, f0_floor=60, f0_ceil=700, frame_period=5.0)
    sp = pw.cheaptrick(x, f0, t, SR); ap = pw.d4c(x, f0, t, SR)
    v = f0 > 0
    lf = np.log2(np.where(v, f0, 1))
    if v.sum() > 3:
        m = lf[v].mean(); n = len(f0); pos = np.linspace(0, 1, n)
        # arc: the pitch climbs into the line and peaks around 40-60%, like someone shouting it
        arc_c = arc / 12 * np.sin(np.pi * np.clip(pos * 1.1, 0, 1)) ** 0.8
        jit = np.convolve(rng.standard_normal(n), np.ones(4) / 4, 'same') * 0.012   # strain
        lf2 = m + (lf - m) * gain + st / 12 + arc_c + jit
        f0 = np.where(v, 2 ** lf2, 0)
    # shouted voice: more energy in 1-4 kHz, slightly less "breathy"
    fr = np.linspace(0, SR / 2, sp.shape[1])
    tilt = (1 + bright * 1.6 * np.exp(-((fr - 2600) / 1500) ** 2)) * (1 + bright * 0.25 * (fr / (SR / 2)))
    sp = sp * tilt[None, :] ** 2
    ap = np.clip(ap * (1 - 0.15 * bright), 0.001, 1)
    # time-fit by resampling WORLD frames (pitch is kept)
    n0 = len(f0); n1 = max(4, int(round(target_len / 0.005)))
    idx = np.linspace(0, n0 - 1, n1)
    i0 = np.floor(idx).astype(int); i1 = np.minimum(i0 + 1, n0 - 1); w = (idx - i0)[:, None]
    sp2 = sp[i0] * (1 - w) + sp[i1] * w; ap2 = ap[i0] * (1 - w) + ap[i1] * w
    f02 = np.where((f0[i0] > 0) & (f0[i1] > 0), f0[i0] * (1 - w[:, 0]) + f0[i1] * w[:, 0], f0[np.round(idx).astype(int)])
    y = pw.synthesize(np.ascontiguousarray(f02), np.ascontiguousarray(sp2), np.ascontiguousarray(ap2), SR, 5.0)
    # attack: a hard onset reads as effort
    a = int(0.012 * SR); y[:a] *= np.linspace(0, 1, a)
    r = int(0.03 * SR); y[-r:] *= np.linspace(1, 0, r)
    return y

def breath(dur, g, hi=True):
    n = int(dur * SR); x = rng.standard_normal(n)
    F = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR); F *= np.exp(-((f - (1800 if hi else 1100)) / 900) ** 2); x = np.fft.irfft(F, n)
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5 * np.linspace(0.6, 1, n)
    return x / np.abs(x).max() * env * g

for i, (l, p) in enumerate(zip(L, P)):
    text, hold, spd, st, gain, arc, bright = p
    phs = shout_phonemes(text, hold)
    # if the shout would need squashing hard into its slot, say it faster / without the held vowel instead
    for h, sp_ in ((hold, spd), (hold, spd * 1.2), (False, spd * 1.2), (False, spd * 1.4), (False, spd * 1.6), (False, spd * 1.8)):
        phs = shout_phonemes(text, h)
        a, _ = K.create(phs, voice=l['spk'], speed=sp_, is_phonemes=True)
        nz = np.where(np.abs(a) > 0.012)[0]; a = a[max(0, nz[0] - 100): nz[-1] + 120]
        if len(a) / SR <= l['d'] * 1.08: break
    # slot: the original line length; early lines may spill a little into their long gaps
    nxt = L[i + 1]['t'] if i + 1 < len(L) else l['t'] + l['d'] + 0.3
    room = nxt - l['t'] - 0.04
    natural = len(a) / SR
    tgt = min(max(natural * 0.97, l['d'] * 0.92), room, l['d'] * 1.15, natural)
    y = world_shout(a, st, gain, arc, bright, tgt)
    y = y / (np.abs(y).max() + 1e-9) * 0.9
    sf.write(f'vo2/l{i:02d}.wav', y, SR)
    print(f"{i:2d} {l['spk']:8s} {phs:28s} slot {l['d']:.2f} natural {natural:.2f} -> {len(y)/SR:.2f}")
# inhales before the lines that have room for one (gap >= 0.35 s)
B = []
for i, l in enumerate(L):
    gap = l['t'] - (L[i - 1]['t'] + L[i - 1]['d'] if i else 0)
    if gap >= 0.35:
        d = min(0.32, gap - 0.08); sf.write(f'vo2/breath_{i:02d}.wav', breath(d, 0.5 if l['spk'] == 'jm_kumo' else 0.4, l['spk'] != 'jm_kumo'), SR)
        B.append(dict(i=i, t=round(l['t'] - d - 0.02, 3)))
json.dump(B, open('vo2/breaths.json', 'w'))
print('breaths', B)
