import numpy as np, wave
from edit11d import edit_time, TOTAL
SR = 48000; T = TOTAL
def load(p):
    with wave.open(p) as w_:
        a = np.frombuffer(w_.readframes(w_.getnframes()), '<i2').astype(float) / 32768; ch = w_.getnchannels()
    a = a.reshape(-1, ch)
    return np.repeat(a, 2, axis=1) if ch == 1 else a
m = load('music.wav'); reps = int(np.ceil(T * SR / len(m)))
mus = np.concatenate([m] * reps)[:int(T * SR)] * 0.85
def onepole(x, a):
    y = np.zeros_like(x); acc = np.zeros(x.shape[1])
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
s0, s1 = int(edit_time(103) * SR), int((edit_time(189) + 1 / 30) * SR)    # slow-mo: muffled & dreamy
seg = mus[s0:s1]; muff = onepole(seg, 0.06) * 1.6
fade = int(0.12 * SR); w = np.ones(len(seg)); w[:fade] = np.linspace(0, 1, fade); w[-fade:] = np.linspace(1, 0, fade)
mus[s0:s1] = seg * (1 - w[:, None]) + muff * w[:, None] * 0.9
out = mus.copy(); rng = np.random.default_rng(13)
def add(snd, gf, gain=1.0, at=None):
    t0 = at if at is not None else edit_time(gf)
    if t0 is None: return
    i = int(t0 * SR); n = min(len(snd), len(out) - i); out[i:i + n] += gain * (snd[:n, None] if snd.ndim == 1 else snd[:n])
def lp(x, k): return np.convolve(x, np.ones(k) / k, 'same')
def swish(d, k=10):
    n = int(d * SR); return lp(rng.standard_normal(n), k) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 2.5
def thud():
    tt = np.arange(int(0.3 * SR)) / SR; return np.sin(2 * np.pi * (60 + 80 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 12) * 1.4
def tip():
    tt = np.arange(int(0.09 * SR)) / SR; return np.sin(2 * np.pi * 520 * tt) * np.exp(-tt * 45) * 0.8
def twang():
    tt = np.arange(int(0.35 * SR)) / SR; f = 180 + 60 * np.exp(-tt * 10)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9) * np.sign(np.sin(2 * np.pi * 9 * tt) + 0.2) * 0.9
for gf in (484, 491, 499, 506): add(tip(), gf, 0.45)          # tiptoe plinks
add(swish(0.25), 515, 0.6)                                    # snatch
add(twang(), 552, 0.8)                                        # strap snaps taut
add(swish(0.25), 69, 0.5)                                     # (original grab)
add(swish(0.9, 40), None, 0.7, at=edit_time(103) - 0.13)       # into slow-mo
add(swish(0.6, 25), 153, 0.5)                                 # slow arm whip
add(swish(0.3), None, 0.5, at=edit_time(189) - 0.05)           # snap back
add(swish(0.3), 349, 0.4)
add(thud(), 360, 0.85); add(thud(), 364, 0.3)
v = load('oof.wav')[:, 0]; add(v / np.abs(v).max(), 360, 0.55)
add(swish(0.35), 386, 0.55)
out = np.clip(out, -0.98, 0.98)
with wave.open('ep11d_audio.wav', 'wb') as w_:
    w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((out * 32767).astype('<i2').tobytes())
print('audio ok', round(T, 2))
