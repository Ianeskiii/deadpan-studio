import numpy as np, wave, soundfile as sf
SR = 48000; T = 16.0
def load(p):
    a, sr = sf.read(p, always_2d=True)
    if a.shape[1] == 1: a = np.repeat(a, 2, axis=1)
    if sr != SR:
        idx = np.arange(int(len(a) * SR / sr)) * sr / SR
        a = np.stack([np.interp(idx, np.arange(len(a)), a[:, c]) for c in (0, 1)], 1)
    return a
fr = lambda f: (f - 1) / 30
mus = load('music.wav')[:int(T * SR)] * 0.62
def onepole(x, a):
    y = np.zeros_like(x); acc = np.zeros(x.shape[1])
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def muffle(t0, t1, cutoff_a, gain, ramp=0.12):
    s0, s1 = int(t0 * SR), int(t1 * SR); seg = mus[s0:s1]; m = onepole(seg, cutoff_a) * gain
    n = int(ramp * SR); w = np.ones(len(seg)); w[:n] = np.linspace(0, 1, n); w[-n:] = np.linspace(1, 0, n)
    mus[s0:s1] = seg * (1 - w[:, None]) + m * w[:, None]
muffle(fr(181), fr(256), 0.06, 1.5)                 # slow-mo: dreamy, muffled
muffle(fr(434), fr(461), 0.25, 0.45, ramp=0.08)     # Doug lifts a headphone: his music drops away
out = mus.copy(); rng = np.random.default_rng(16)
def add(snd, t0, gain=1.0):
    i = int(t0 * SR); n = min(len(snd), len(out) - i); out[i:i + n] += gain * (snd[:n, None] if snd.ndim == 1 else snd[:n])
def lp(x, k): return np.convolve(x, np.ones(k) / k, 'same')
def swish(d, k=10):
    n = int(d * SR); return lp(rng.standard_normal(n), k) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 2.0
def thud(g=1.0):
    tt = np.arange(int(0.3 * SR)) / SR; return np.sin(2 * np.pi * (60 + 80 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 12) * g
def step():
    tt = np.arange(int(0.08 * SR)) / SR; return lp(rng.standard_normal(len(tt)), 6) * np.exp(-tt * 70) * 0.6
for f in range(40, 61, 7): add(step(), fr(f), 0.35)          # Green's footsteps walking in
add(swish(0.25), fr(150), 0.45)                               # grab
add(swish(0.9, 40), fr(181) - 0.13, 0.5)                      # into slow-mo
add(thud(0.9), fr(263), 0.6)                                  # foot stomp
add(swish(0.3), fr(256) - 0.05, 0.35)                         # out of slow-mo
add(swish(0.55, 14), fr(331), 0.55)                           # spin whoosh
add(thud(1.3), fr(350), 0.8); add(thud(0.5), fr(354), 0.4)    # lands on his butt
add(swish(0.2, 6), fr(430), 0.25)                             # headphone lifted
add(swish(0.2, 6), fr(459), 0.25)                             # headphone back on
for name, f in (('g1', 64), ('g2', 258), ('g3', 288), ('g4', 357), ('d1', 438)):
    v = load(f'vo6/{name}.wav'); add(v / np.abs(v).max() * 0.9, fr(f), 1.0)
# soft limiter to -1 dBFS (no hard clipping)
pk = np.abs(out).max(); ceil = 10 ** (-1 / 20)
out = np.tanh(out / pk * 1.15) / np.tanh(1.15) * ceil
with wave.open('ep11f_audio.wav', 'wb') as w_:
    w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((out * 32767).astype('<i2').tobytes())
print('audio ok, peak dBFS', round(20 * np.log10(np.abs(out).max()), 2))
