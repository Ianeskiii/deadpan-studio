"""Mix: cafe room tone (murmur, clinks), soft lo-fi bed ducked under dialogue, foley, voices."""
import numpy as np, json, wave, soundfile as sf
SR = 48000; T = json.load(open('vo/timing.json')); N = T['N']; DUR = N / 30
rng = np.random.default_rng(7)
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
# ---- room tone: distant chatter (syllable-modulated band noise from several tables) + HVAC hum
murmur = np.zeros(n)
for i in range(7):
    z = bp(rng.standard_normal(n), 250 + 60 * i, 1700 + 120 * i)
    syl = np.clip(np.sin(2 * np.pi * (3.2 + 0.6 * rng.random()) * t + rng.random() * 6) + 0.3 * np.sin(2 * np.pi * 0.31 * t + i), 0, None)
    talk = (np.sin(2 * np.pi * (0.09 + 0.05 * rng.random()) * t + rng.random() * 6) > -0.2).astype(float)
    murmur += z * lp(syl * talk, 2400)
murmur = murmur / np.abs(murmur).max() * 0.035
air = bp(rng.standard_normal(n), 60, 400); air = air / np.abs(air).max() * 0.008
L = murmur + air; R = np.roll(murmur, 900) + air
def clink(g=0.05, f0=None):
    f0 = f0 or rng.uniform(2400, 4200); tt = np.arange(int(0.5 * SR)) / SR
    return sum(np.sin(2 * np.pi * f0 * k * tt) * np.exp(-tt * (9 + 6 * k)) / k for k in (1, 2.76, 5.4)) * g
out = np.stack([L, R], 1)
def add(snd, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= n: return
    m = min(len(snd), n - i); out[i:i + m, 0] += snd[:m] * g * (1 - max(0, pan)); out[i:i + m, 1] += snd[:m] * g * (1 + min(0, pan))
for tc in rng.uniform(0.5, DUR - 0.5, 9): add(clink(0.03), tc, 1, rng.uniform(-0.8, 0.8))     # cups and spoons around the room
# ---- music bed: soft electric-piano chords + upright bass + brushes, 84 BPM
bpm = 84; beat = 60 / bpm
chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]   # Fmaj7 Em7 Dm7 Cmaj7
bass = [41, 40, 38, 36]
mus = np.zeros(n)
def ep(note, dur, g):
    tt = np.arange(int(dur * SR)) / SR; f = 440 * 2 ** ((note - 69) / 12)
    s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 3) + 0.08 * np.sin(6 * np.pi * f * tt) * np.exp(-tt * 6))
    return s * np.exp(-tt * 1.1) * (1 - np.exp(-tt * 200)) * (1 + 0.15 * np.sin(2 * np.pi * 5 * tt)) * g
bar = 4 * beat; k = 0; tb = 0.0
while tb < DUR:
    c = chords[k % 4]
    for j, off in enumerate((0, 1.5 * beat, 2.5 * beat)):
        for q in c: 
            s = ep(q, 1.6, 0.05 if j == 0 else 0.035); i = int((tb + off + 0.01 * rng.random()) * SR); m = min(len(s), n - i)
            if m > 0: mus[i:i + m] += s[:m]
    for j, off in enumerate((0, 2 * beat, 3 * beat + beat / 2)):
        s = ep(bass[k % 4] + (7 if j == 2 else 0), 0.7, 0.12); i = int((tb + off) * SR); m = min(len(s), n - i)
        if m > 0: mus[i:i + m] += lp(s, 8)[:m]
    for j in range(8):
        tt = np.arange(int(0.12 * SR)) / SR; s = bp(rng.standard_normal(len(tt)), 2000, 9000) * np.exp(-tt * 30) * (0.02 if j % 2 else 0.035)
        i = int((tb + j * beat / 2) * SR); m = min(len(s), n - i)
        if m > 0: mus[i:i + m] += s[:m]
    tb += bar; k += 1
mus = lp(mus, 3) / np.abs(mus).max() * 0.11
# duck the music under every line
env = np.ones(n)
for k_, v in T.items():
    if isinstance(v, dict):
        a, b = int((v['s'] - 0.15) * SR), int((v['e'] + 0.25) * SR); env[a:b] = 0.55
env = lp(env, 4800)
out[:, 0] += mus * env; out[:, 1] += mus * env
# ---- foley
def bell():
    tt = np.arange(int(1.4 * SR)) / SR
    return sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, d in ((2093, 2.2), (2637, 2.8), (3520, 4))) * 0.05
def tap(g=0.5):
    tt = np.arange(int(0.07 * SR)) / SR; return bp(rng.standard_normal(len(tt)), 150, 2500) * np.exp(-tt * 70) * g
def rustle(d=0.18, g=0.08):
    m = int(d * SR); return bp(rng.standard_normal(m), 1500, 8000) * np.sin(np.linspace(0, np.pi, m)) * g
def squeak(d=0.25):
    tt = np.arange(int(d * SR)) / SR; f = 2600 + 500 * np.sin(2 * np.pi * 9 * tt)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + bp(rng.standard_normal(len(tt)), 3000, 9000)) * np.sin(np.pi * tt / d) * 0.035
def hiss(d):
    m = int(d * SR); e = np.minimum(1, np.minimum(np.arange(m) / (0.08 * SR), (m - np.arange(m)) / (0.15 * SR)))
    return bp(rng.standard_normal(m), 3000, 11000) * e * 0.06 + bp(rng.standard_normal(m), 80, 300) * e * 0.05
add(bell(), 0.0, 1.0, -0.6)                                             # door chime as Doug walks in
def steps(f0, f1, k, g=0.35, pan=0.0):
    for j in range(1, int(k) + 1): add(tap(g), fr(f0 + j * (f1 - f0) / k), 1, pan)
steps(1, 30, 3.2, pan=-0.4); steps(305, 327, 2.2, 0.28, -0.3); steps(404, 425, 2.2, 0.3, -0.2); steps(527, 562, 3.0, 0.32, -0.3); steps(580, N, 2.0, 0.34, -0.3)
add(rustle(0.2), fr(36), 1, 0.4)                                        # cup off the stack
add(tap(0.15), fr(46), 1, 0.4)                                          # marker uncapped
for c in (187, 203, 224, 245): add(squeak(0.32), fr(c + 8), 1, 0.4)     # writing each letter
add(hiss(1.0), fr(311), 1, 0.5)                                         # espresso machine
add(tap(0.25), fr(513), 1, 0.1); add(rustle(0.12, 0.05), fr(519), 1, -0.1)   # cup down, Doug picks it up
# ---- voices (barista slightly right, Doug slightly left; last call is from across the shop)
for k_, v in T.items():
    if not isinstance(v, dict): continue
    a = load(f'vo/{k_}.wav'); a = a / np.abs(a).max() * (0.62 if k_ == 'b6' else 0.85)
    add(a, v['file_t'], 1.0, 0.18 if k_.startswith('b') else -0.18)
pk = np.abs(out).max(); ceil = 10 ** (-1 / 20)
out = np.tanh(out / pk * 1.2) / np.tanh(1.2) * ceil
with wave.open('ep12_audio.wav', 'wb') as w_:
    w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((out * 32767).astype('<i2').tobytes())
print('audio ok', round(DUR, 2), 's peak', round(20 * np.log10(np.abs(out).max()), 2))
