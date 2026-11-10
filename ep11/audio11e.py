import numpy as np, wave
SR = 48000; T = 16.0
def load(p):
    with wave.open(p) as w_:
        a = np.frombuffer(w_.readframes(w_.getnframes()), '<i2').astype(float) / 32768; ch = w_.getnchannels(); sr = w_.getframerate()
    a = a.reshape(-1, ch)
    if ch == 1: a = np.repeat(a, 2, axis=1)
    if sr != SR:
        idx = np.arange(int(len(a) * SR / sr)) * sr / SR
        a = np.stack([np.interp(idx, np.arange(len(a)), a[:, c]) for c in (0, 1)], 1)
    return a
mus = load('music.wav')[:int(T * SR)] * 0.8
def onepole(x, a):
    y = np.zeros_like(x); acc = np.zeros(x.shape[1])
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
fr = lambda f: (f - 1) / 30
s0, s1 = int(fr(196) * SR), int(fr(286) * SR)
seg = mus[s0:s1]; muff = onepole(seg, 0.06) * 1.6
fade = int(0.12 * SR); w = np.ones(len(seg)); w[:fade] = np.linspace(0, 1, fade); w[-fade:] = np.linspace(1, 0, fade)
mus[s0:s1] = seg * (1 - w[:, None]) + muff * w[:, None] * 0.9
out = mus.copy(); rng = np.random.default_rng(14)
def add(snd, t0, gain=1.0):
    i = int(t0 * SR); n = min(len(snd), len(out) - i); out[i:i + n] += gain * (snd[:n, None] if snd.ndim == 1 else snd[:n])
def lp(x, k): return np.convolve(x, np.ones(k) / k, 'same')
def swish(d, k=10):
    n = int(d * SR); return lp(rng.standard_normal(n), k) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 2.5
def thud():
    tt = np.arange(int(0.3 * SR)) / SR; return np.sin(2 * np.pi * (60 + 80 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 12) * 1.4
add(swish(0.25), fr(165), 0.6)                     # grab
add(swish(0.9, 40), fr(196) - 0.13, 0.7)           # into slow-mo
add(swish(0.6, 25), fr(258), 0.5)                  # slow arm whip
add(swish(0.3), fr(286) - 0.05, 0.5)               # snap back
add(swish(0.5, 14), fr(391), 0.7)                  # spin whoosh
add(thud(), fr(410), 0.85); add(thud(), fr(414), 0.3)
v = load('oof.wav')[:, 0]; add(v / np.abs(v).max(), fr(410), 0.5)
for wav, f in (('vo_demand.wav', 101), ('vo_giveup.wav', 424)):
    v = load(wav)[:, 0]; add(v / np.abs(v).max(), fr(f), 0.95)
out = np.clip(out, -0.98, 0.98)
with wave.open('ep11e_audio.wav', 'wb') as w_:
    w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((out * 32767).astype('<i2').tobytes())
print('audio ok')
