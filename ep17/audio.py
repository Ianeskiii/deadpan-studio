"""ep17 sound. No music. Doug's two takes (vo/m1.wav "Mamba out.", vo/a2.wav "...Alright.") + everything synthesized here:
quiet office ambience, typing, chair creaks, headset handling, the pen pick-up / mic-drop (hit + small bounce), a soft clock tick,
an ORIGINAL incoming-call ringtone (a soft two-bar mallet phrase, not any app's real ringtone) from the call to the cut,
ducked under "...Alright.", and a hard cut to silence on black."""
import os, sys, wave
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from beats import *
SR = 48000; DUR = N / 30; n = int(DUR * SR); t = np.arange(n) / SR
rng = np.random.default_rng(17)
def T(f): return (f - 1) / 30
def bp(x, lo, hi):
    F = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR); F[(fr < lo) | (fr > hi)] = 0; return np.fft.irfft(F, len(x))
def put(buf, s, t0, g=1.0):
    i = int(round(t0 * SR)); a = max(0, -i); m = min(len(s), n - i)
    if m > a: buf[i + a:i + m] += s[a:m] * g
def env_ad(m, a, d): tt = np.arange(m) / SR; return np.minimum(1, tt / max(a, 1e-4)) * np.exp(-tt / d)
fx = np.zeros(n)
room = bp(rng.standard_normal(n), 60, 900) * 0.004 + bp(rng.standard_normal(n), 1500, 5000) * 0.0006 + np.sin(2 * np.pi * 60 * t) * 0.0006
def click(g, lo=1500, hi=6000, d=0.006, dur=0.04):
    m = int(dur * SR); return bp(rng.standard_normal(m), lo, hi) * env_ad(m, 0.0005, d) * g
def thud(g, lo=60, hi=500, d=0.05, dur=0.25):
    m = int(dur * SR); return bp(rng.standard_normal(m), lo, hi) * env_ad(m, 0.002, d) * g
def rustle(g, dur):
    m = int(dur * SR); return bp(rng.standard_normal(m), 800, 5000) * np.sin(np.pi * np.arange(m) / m) ** 1.5 * g
def creak(g, dur=0.35, f0=420):
    m = int(dur * SR); tt = np.arange(m) / SR
    return np.sin(2 * np.pi * (f0 + 70 * np.sin(2 * np.pi * 11 * tt)) * tt) * np.exp(-tt / 0.12) * np.minimum(1, tt / 0.02) * g

# ---- typing (both hands, ~8 keys/s, the last key a little firmer)
k = T(TYPE[0]) + 0.05
while k < T(TYPE[1]) - 0.05:
    put(fx, click(0.05 * (0.7 + 0.5 * rng.random()), 1200, 5000, 0.008) + thud(0.012, 200, 900, 0.01, 0.04), k); k += 0.11 + 0.05 * rng.random()
put(fx, click(0.07, 1200, 5000, 0.01), T(TYPE[1]) - 0.03)
# ---- shoulders drop: chair settles
put(fx, creak(0.012, 0.4, 380), T(RELAX[0]) + 0.1)
# ---- headset off: plastic/fabric handling, set down softly on the desk
put(fx, rustle(0.012, 0.35), T(HS_OFF[0] + 6)); put(fx, click(0.02, 800, 3000, 0.01), T(HS_OFF[0] + 8))
put(fx, thud(0.06, 80, 900, 0.03, 0.15), T(HS_OFF[1] - 2)); put(fx, click(0.02, 1000, 4000, 0.01), T(HS_OFF[1] - 2))
# ---- pen picked up
put(fx, click(0.035, 2000, 7000, 0.004), T(PEN_PICK[0] + 6))
# ---- the mic drop: pen hits the desk, one small bounce, rattles still
hit = click(0.22, 1800, 9000, 0.012, 0.1) + thud(0.10, 150, 1200, 0.02, 0.1)
put(fx, hit, T(PEN_LAND)); put(fx, click(0.07, 2500, 9000, 0.008), T(PEN_LAND) + 0.10); put(fx, click(0.03, 3000, 9000, 0.005), T(PEN_LAND) + 0.16)
# ---- the clock ticks over (very soft)
put(fx, click(0.02, 2500, 6000, 0.003), T(CLK_59))
# ---- C: the reluctant reach, the pen picked up again
put(fx, rustle(0.006, 0.6), T(REACH[0] + 4)); put(fx, click(0.03, 2000, 7000, 0.004), T(REACH[1]))
# ---- D: pen set back down, headset picked up and put on, chair sinks
put(fx, click(0.05, 1800, 8000, 0.008, 0.05), T(PEN_BACK[1] - 2))
put(fx, click(0.02, 800, 3000, 0.01), T(HS_GRAB[1])); put(fx, rustle(0.012, 0.5), T(HS_ON[0] + 2)); put(fx, thud(0.02, 100, 600, 0.03, 0.1), T(HS_ON[1] - 3))
put(fx, creak(0.014, 0.5, 340), T(SINK[0] + 2))
put(fx, rustle(0.004, 0.7), T(CURSOR[0]))                       # mouse sliding on the pad

# ---- VO
dlg = np.zeros(n)
for path, f0, g in (('vo/m1.wav', M_F, 0.75), ('vo/a2.wav', A_F, 0.85)):
    v, vsr = sf.read(path); v = np.interp(np.arange(int(len(v) * SR / vsr)) / SR, np.arange(len(v)) / vsr, v); put(dlg, v, T(f0), g)

# ---- the ringtone (original): a soft mallet phrase G5 B5 D6 . D6 B5 . . , repeating every 2.4 s
def mallet(fr, d=0.5, g=1.0):
    m = int(d * SR); tt = np.arange(m) / SR
    x = np.sin(2 * np.pi * fr * tt) + 0.35 * np.sin(2 * np.pi * 4.0 * fr * tt) * np.exp(-tt / 0.03) + 0.2 * np.sin(2 * np.pi * 2 * fr * tt)
    return x * np.minimum(1, tt / 0.003) * np.exp(-tt / 0.18) * g
PHR = [(0.00, 783.99), (0.16, 987.77), (0.32, 1174.66), (0.64, 1174.66), (0.80, 987.77)]
ring = np.zeros(n); r0 = T(CALL) + 0.05
c = r0
while c < DUR:
    for dt, fr in PHR: put(ring, mallet(fr, 0.5, 1.0), c + dt)
    c += 2.4
ring = bp(ring, 300, 9000) * 0.075
duck = np.ones(n); d0, d1 = T(A_F) - 0.15, T(A_F) + 1.75
s_ = (t >= d0) & (t < d1); duck[s_] = 10 ** (-9 / 20)                 # -9 dB under "...Alright."
duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), 'same')
ring *= duck

mix = room + fx + dlg + ring
bi = int(T(BLACK) * SR); f_ = int(0.008 * SR); mix[bi - f_:bi] *= np.linspace(1, 0, f_); mix[bi:] = 0.0      # hard cut on black
pk = np.abs(mix).max(); mix = mix / max(1.0, pk / 0.9)
st = np.stack([mix, np.roll(mix, 120) * 0.97 + mix * 0.03], 1)
with wave.open('audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('audio', round(DUR, 2), 's | pen hit', round(T(PEN_LAND), 3), '| ring from', round(r0, 3), '| alright', round(T(A_F), 3),
      '| cut', round(T(BLACK), 3), '| peak', round(float(np.abs(mix).max()), 3))
