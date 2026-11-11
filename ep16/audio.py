"""ep16 sound. No dialogue. Everything synthesized here except the FAHHH, which is the owner-supplied sound already used in
ep14 Front Camera V3 (ep14/sfx/fahhh_src.wav), trimmed the same way.
Room tone; tired footsteps; bag thud; brisker steps; couch plop; controller pick-up; button click; console wake + boot chime;
an original, quiet menu loop (Am-F-C-G pad + soft arpeggio) that keeps playing through the time skip and slowly drains
away as he falls asleep; ~0.43 s of total silence; FAHHH on the cut to the wide; ~0.3 s pause; gentle snoring on his breaths."""
import json, wave
import numpy as np, soundfile as sf
SR = 48000; B = json.load(open('beats.json')); N = B['N']
DUR = N / 30; n = int(DUR * SR); t = np.arange(n) / SR
rng = np.random.default_rng(16)
def T(f): return (f - 1) / 30
def I(f): return int(T(f) * SR)
def bp(x, lo, hi):
    F = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR); F[(fr < lo) | (fr > hi)] = 0; return np.fft.irfft(F, len(x))
def put(buf, s, t0, g=1.0):
    i = int(t0 * SR); m = min(len(s), n - i)
    if m > 0: buf[i:i + m] += s[:m] * g
def env_ad(m, a, d): tt = np.arange(m) / SR; return np.minimum(1, tt / max(a, 1e-4)) * np.exp(-tt / d)
fx = np.zeros(n); mus = np.zeros(n)
room = bp(rng.standard_normal(n), 80, 1200) * 0.0035 + np.sin(2 * np.pi * 58 * t) * 0.0008

# ---- footsteps (contacts at ph = k*pi in rig.walk)
def step(g):
    m = int(0.12 * SR); x = bp(rng.standard_normal(m), 70, 900) * env_ad(m, 0.004, 0.025) + np.sin(2 * np.pi * 85 * np.arange(m) / SR) * env_ad(m, 0.002, 0.03) * 0.6
    return x * g
for (f0, f1), steps, g in ((B['WALK1'], 3.4, 0.05), (B['WALK2'], 3.0, 0.065)):
    k = 0
    while k <= steps:
        put(fx, step(g * (0.85 + 0.3 * rng.random())), T(f0 + (f1 - f0) * k / steps)); k += 1
# ---- bag lands: soft fabric thump + a tiny buckle clink
m = int(0.3 * SR); thump = bp(rng.standard_normal(m), 60, 700) * env_ad(m, 0.003, 0.05) + np.sin(2 * np.pi * 70 * np.arange(m) / SR) * env_ad(m, 0.002, 0.06)
put(fx, thump * 0.14, T(B['BAG_LAND'])); m = int(0.08 * SR); put(fx, np.sin(2 * np.pi * 2900 * np.arange(m) / SR) * env_ad(m, 0.001, 0.012) * 0.02, T(B['BAG_LAND']) + 0.03)
# ---- plops onto the couch: cushion whump + spring creak
s0, s1 = B['SIT']; m = int(0.45 * SR); tt = np.arange(m) / SR
whump = bp(rng.standard_normal(m), 50, 400) * env_ad(m, 0.01, 0.09) + np.sin(2 * np.pi * 55 * tt) * env_ad(m, 0.01, 0.1) * 0.8
creak = np.sin(2 * np.pi * (340 + 60 * np.sin(2 * np.pi * 9 * tt)) * tt) * np.exp(-tt / 0.12) * 0.15
put(fx, (whump + creak) * 0.12, T(s0 + 7))
# ---- controller: plastic pick-up rattle, the home-button click
def click(g, hi=5000):
    m = int(0.04 * SR); return bp(rng.standard_normal(m), 1500, hi) * env_ad(m, 0.0005, 0.006) * g
put(fx, click(0.06), T(B['LIFT'][0])); put(fx, click(0.04), T(B['LIFT'][0]) + 0.05); put(fx, click(0.035), T(B['LIFT'][1]))
put(fx, click(0.08, 6000), T(B['PRESS']))
# ---- console wake: soft blip; TV power-on tick + a short original two-note boot chime
m = int(0.12 * SR); tt = np.arange(m) / SR; put(fx, np.sin(2 * np.pi * 1320 * tt) * env_ad(m, 0.003, 0.04) * 0.03, T(B['PRESS']) + 0.08)
put(fx, click(0.05, 3000), T(B['BOOT'][0]))
def tone(fr, d, g, a=0.02, dec=0.5):
    m = int(d * SR); tt = np.arange(m) / SR
    return (np.sin(2 * np.pi * fr * tt) + 0.3 * np.sin(2 * np.pi * 2 * fr * tt) + 0.12 * np.sin(2 * np.pi * 3 * fr * tt)) * np.minimum(1, tt / a) * np.exp(-tt / dec) * g
put(fx, tone(523.25, 1.2, 0.03, 0.05, 0.5), T(B['BOOT'][0] + 5)); put(fx, tone(783.99, 1.2, 0.03, 0.05, 0.6), T(B['BOOT'][0] + 11))
# ---- menu loop: 84 bpm, Am - F - C - G, a pad and a soft plucked arpeggio (original)
bpm = 84; beat = 60 / bpm; bar = 4 * beat
CH = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (130.81, 164.81, 196.0), (196.0, 246.94, 293.66)]
M0 = T(B['MENU_ON']); LEN = DUR - M0
loop = np.zeros(int(LEN * SR) + SR)
k = 0; tb = 0.0
while tb < LEN:
    ch = CH[k % 4]; m = int(bar * SR); tt = np.arange(m) / SR
    pad = sum(np.sin(2 * np.pi * fq * tt) + 0.25 * np.sin(2 * np.pi * fq * 2.003 * tt) for fq in ch)
    pad *= np.minimum(1, tt / 0.6) * np.minimum(1, (bar - tt) / 0.5) * 0.010
    i0 = int(tb * SR); loop[i0:i0 + m] += pad[:len(loop) - i0]
    for j in range(8):          # eighth-note arpeggio, up an octave
        fq = ch[j % 3] * 2 * (2 if j in (3, 7) else 1); mm = int(0.45 * SR); t2 = np.arange(mm) / SR
        pl = (np.sin(2 * np.pi * fq * t2) + 0.2 * np.sin(2 * np.pi * 2 * fq * t2)) * env_ad(mm, 0.004, 0.16) * 0.012
        ia = i0 + int(j * beat / 2 * SR); ln = min(mm, len(loop) - ia)
        if ln > 0: loop[ia:ia + ln] += pl[:ln]
    k += 1; tb += bar
loop = loop[:n - int(M0 * SR)]
# level: full in C, a touch lower after the time skip, drains away as he falls asleep, gone for the silence
lv = np.ones(len(loop)); tl = M0 + np.arange(len(loop)) / SR
def ramp(ta, tb_, va, vb):
    s = (tl >= ta) & (tl < tb_); lv[s] = va + (vb - va) * (tl[s] - ta) / (tb_ - ta)
lv[:] = 1.0
lv[tl < M0 + 0.4] = np.linspace(0, 1, (tl < M0 + 0.4).sum())
ramp(T(B['CARD'][1]), T(B['CARD'][1]) + 0.01, 0.75, 0.75); lv[tl >= T(B['CARD'][1])] = 0.75
ramp(T(B['CLOSE'][0]), T(B['SILENCE'][0]), 0.75, 0.0); lv[tl >= T(B['SILENCE'][0])] = 0.0
loop *= 2.0
mus[int(M0 * SR):int(M0 * SR) + len(loop)] = loop * lv
# ---- the reveal
src, _ = sf.read('../ep14/sfx/fahhh_src.wav')
if src.ndim > 1: src = src.mean(1)
e = np.convolve(np.abs(src), np.ones(240) / 240, 'same'); on = int(np.argmax(e > e.max() * 0.08)); src = src[max(0, on - 96):]
src = src / np.abs(src).max()
fa = src[:int(0.95 * SR)].copy(); fm = int(0.30 * SR); fa[-fm:] *= np.linspace(1, 0, fm) ** 1.5
fa *= 10 ** (-3.5 / 20)
F_END = T(B['REVEAL']) + len(fa) / SR
# ---- snoring on his breaths (build.py: breath = sin(2pi (f - ASLEEP) / 66), inhale = the rising half)
def snore(dur, g):
    m = int(dur * SR); tt = np.arange(m) / SR; ph = tt / dur
    flutter = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * (27 + 4 * ph) * tt)) * np.abs(np.sin(2 * np.pi * (27 + 4 * ph) * tt)) ** 0.5   # soft palate flutter
    x = bp(rng.standard_normal(m), 90, 900) * flutter + 0.6 * np.sin(2 * np.pi * (95 + 10 * ph) * tt) * flutter
    env = np.sin(np.pi * np.clip(ph * 1.05, 0, 1)) ** 1.2
    return x * env * g
def exhale(dur, g):
    m = int(dur * SR); ph = np.arange(m) / m
    return bp(rng.standard_normal(m), 300, 2500) * np.sin(np.pi * ph) ** 2 * (1 - 0.4 * ph) * g
P = 66; first = B['SNORE0']      # build.py: the inhale (chest rising) starts here and every 66 frames
sn = np.zeros(n)
for c in [first, first + P]:
    put(sn, snore(1.05, 0.11), T(c) + 0.02); put(sn, exhale(0.75, 0.035), T(c) + 1.15)
# ---- mix
bed = room + fx + mus * 0.9
sl0, sl1 = I(B['SILENCE'][0]), I(B['REVEAL'])
bed[sl0:sl1] = 0.0                                              # total silence before the cut
k0 = I(B['REVEAL']); bed[k0:] *= 0.55                           # wide: the room is just a little quieter under the snoring
mus2 = np.zeros(n); i2 = int((T(first) - 0.2) * SR)             # the menu loop creeps back under the snores (still waiting)
seg = loop[i2 - int(M0 * SR):]; mus2[i2:i2 + len(seg)] = seg[:n - i2] * np.minimum(1, np.arange(min(len(seg), n - i2)) / SR / 1.0) * 0.28
mix = bed + mus2 + sn
put(mix, fa, T(B['REVEAL']))
BLACK = T(B['G_BLACK']); bi = int(BLACK * SR)
mix[bi:] *= np.linspace(1, 0, n - bi) ** 1.5
mix = np.clip(mix, -0.98, 0.98)
st = np.stack([mix, np.roll(mix, 160) * 0.97 + mix * 0.03], 1)
with wave.open('audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('audio', round(DUR, 2), 's | FAHHH', round(T(B['REVEAL']), 3), '-', round(F_END, 3), '| first snore', round(T(first) + 0.02, 3),
      '| silence', round(T(B['SILENCE'][0]), 3), '-', round(T(B['REVEAL']), 3), '| peak', round(float(np.abs(mix).max()), 3))
