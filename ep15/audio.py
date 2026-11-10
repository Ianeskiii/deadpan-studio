"""Mix: quiet living-room tone (fridge hum from the next room, faint street outside), foley, voices. No music:
the joke lives in the silences.  Writes audio.wav (48 kHz stereo)."""
import json, wave, numpy as np, soundfile as sf
SR = 48000; T = json.load(open('vo/timing.json')); B = json.load(open('beats.json')); N = T['N']; DUR = N / 30
SH = B['SHOTS']; rng = np.random.default_rng(15)
fr = lambda f: (f - 1) / 30
n = int(DUR * SR); t = np.arange(n) / SR
def load(p):
    a, sr = sf.read(p, always_2d=True); a = a.mean(1)
    if sr != SR: a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    return a
def bp(x, lo, hi):
    F = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); F[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(F, len(x))
def lp(x, k): return np.convolve(x, np.ones(k) / k, 'same')
# ---- room tone
hum = (np.sin(2 * np.pi * 60 * t) * 0.6 + np.sin(2 * np.pi * 120 * t) * 0.3) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.13 * t)) * 0.0035
air = bp(rng.standard_normal(n), 80, 900); air = air / np.abs(air).max() * 0.006
street = bp(rng.standard_normal(n), 120, 600) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t + 1)) ; street = street / np.abs(street).max() * 0.004
out = np.stack([hum + air + street, hum + np.roll(air, 700) + street * 0.7], 1)
def add(snd, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= n or i < 0: return
    m = min(len(snd), n - i); out[i:i + m, 0] += snd[:m] * g * (1 - max(0, pan)); out[i:i + m, 1] += snd[:m] * g * (1 + min(0, pan))
# ---- foley
def tap(g=0.5):
    tt = np.arange(int(0.07 * SR)) / SR; return bp(rng.standard_normal(len(tt)), 150, 2500) * np.exp(-tt * 70) * g
def clink(g=0.05, f0=3400):          # fork on a ceramic plate
    tt = np.arange(int(0.35 * SR)) / SR
    return sum(np.sin(2 * np.pi * f0 * k * tt) * np.exp(-tt * (14 + 8 * k)) / k for k in (1, 2.4, 4.1)) * g
def chew(d=0.16, g=0.03):            # soft, wet, closed-mouth
    m = int(d * SR); z = bp(rng.standard_normal(m), 200, 1800)
    return z * np.sin(np.linspace(0, np.pi, m)) ** 2 * g / (np.abs(z).max() + 1e-9) * 2
def creak(d=0.3, g=0.02):            # couch cushion as he stiffens
    tt = np.arange(int(d * SR)) / SR; f = 180 + 60 * np.sin(2 * np.pi * 7 * tt)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + bp(rng.standard_normal(len(tt)), 300, 3000)) * np.sin(np.pi * tt / d) * g
def pat(g=0.06):                     # the crumb lands
    tt = np.arange(int(0.05 * SR)) / SR; return bp(rng.standard_normal(len(tt)), 300, 3000) * np.exp(-tt * 120) * g
def rustle(d=0.18, g=0.03):
    m = int(d * SR); return bp(rng.standard_normal(m), 1500, 8000) * np.sin(np.linspace(0, np.pi, m)) * g
def swallow(g=0.025):
    tt = np.arange(int(0.22 * SR)) / SR; f = 160 - 60 * tt / 0.22
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.22) ** 2 * g
w0, w1 = B['WALK']
for j in range(1, 4): add(tap(0.3), fr(w0 + j * (w1 - w0) / 3.0), 1, -0.45)         # Doug's three steps in
add(clink(0.04), fr(13), 1, 0.2); add(clink(0.05, 3100), fr(17), 1, 0.2)           # fork taps the plate, stabs the next bite
for f in range(8, B['G_NOTICE'], 6): add(chew(), fr(f), 1, 0.2)                     # chewing ...
add(creak(), fr(B['G_FREEZE']), 1, 0.25)                                            # ... stops dead
add(swallow(), fr(B['G_HES1'] + 1), 1, 0.2)                                         # nervous swallow before the first lie
add(rustle(0.4, 0.02), fr(B['G_LOWER'][0]), 1, 0.2)                                 # sleeve as the fork goes down
add(clink(0.02, 3600), fr(B['G_LOWER'][1]), 1, 0.2)
add(chew(0.07, 0.012), fr(B['CRUMB'][0]), 1, 0.15)                                # tiny wet tick as it lets go of his lip
add(pat(0.085), fr(B['CRUMB'][1]), 1, 0.15)                                         # the crumb lands on his jacket (soft, clear)
add(swallow(0.02), fr(SH['H'][0] + 18), 1, 0.15)                                    # before "That's not mine."
# ---- voices
for k_, v in T.items():
    if not isinstance(v, dict): continue
    a = load(f'vo/{k_}.wav'); a = a / np.abs(a).max() * 0.85
    add(a, v['file_t'], 1.0, 0.15 if k_.startswith('g') else -0.15)
# ---- black at the end: everything fades out
fb = int(fr(B['BLACK'][0]) * SR); out[fb:] *= np.linspace(1, 0, n - fb)[:, None] ** 2
pk = np.abs(out).max(); ceil = 10 ** (-1 / 20)
out = np.tanh(out / pk * 1.2) / np.tanh(1.2) * ceil
with wave.open('audio.wav', 'wb') as w_:
    w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((out * 32767).astype('<i2').tobytes())
print('audio ok', round(DUR, 2), 's peak', round(20 * np.log10(np.abs(out).max()), 2))
