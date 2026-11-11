"""ep16 v2 sound (11.5 s). Doug's take vo/c.wav (happy inhale, breathy "hah", "Finally!"); everything else synthesized here
except the Vine Boom, the owner-supplied sfx/vine_boom_src.wav (from vine-boom.mp3), used once, unstretched, its own decay.
Room tone + the quiet original menu loop from frame 1; soft controller clicks on the re-grip; the time-skip card is a hard cut
(no whoosh); the menu loop sinks while he falls asleep; Vine Boom with its transient on the reveal frame; quiet; snoring from 8.2 s."""
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
    i = int(round(t0 * SR)); a = max(0, -i); m = min(len(s), n - i)
    if m > a: buf[i + a:i + m] += s[a:m] * g
def env_ad(m, a, d): tt = np.arange(m) / SR; return np.minimum(1, tt / max(a, 1e-4)) * np.exp(-tt / d)
fx = np.zeros(n); mus = np.zeros(n)
room = bp(rng.standard_normal(n), 80, 1200) * 0.0035 + np.sin(2 * np.pi * 58 * t) * 0.0008

# ---- Doug: the take (24 kHz -> 48 kHz)
vo, vsr = sf.read('vo/c.wav')
vo = np.interp(np.arange(int(len(vo) * SR / vsr)) / SR, np.arange(len(vo)) / vsr, vo)
dlg = np.zeros(n); put(dlg, vo, T(B['VO_F']), 0.62)

# ---- controller: the re-grip (plastic shuffle) and the thumb landing near (not on) the buttons
def click(g, hi=5000):
    m = int(0.04 * SR); return bp(rng.standard_normal(m), 1500, hi) * env_ad(m, 0.0005, 0.006) * g
r0, r1 = B['REGRIP']
put(fx, click(0.05), T(r0)); put(fx, click(0.035), T(r0) + 0.06); put(fx, click(0.03), T(r0 + 6)); put(fx, click(0.04), T(r1))
m = int(0.25 * SR); put(fx, bp(rng.standard_normal(m), 900, 4000) * np.sin(np.pi * np.arange(m) / m) * 0.006, T(r0) + 0.02)   # grip rub
put(fx, click(0.022, 7000), T(B['THUMB'][1] - 2))          # thumb settles on the stick: a tiny tick, no button press
put(fx, click(0.018), T(B['CATCH'][1]))                     # the catch: hands tighten on the plastic

# ---- menu loop: 84 bpm, Am - F - C - G, a pad and a soft plucked arpeggio (original)
bpm = 84; beat = 60 / bpm; bar = 4 * beat
CH = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (130.81, 164.81, 196.0), (196.0, 246.94, 293.66)]
loop = np.zeros(n + SR)
k = 0; tb = -1.3 * bar                                    # already playing when we cut in (mid-phrase)
while tb < DUR:
    ch = CH[k % 4]; m = int(bar * SR); tt = np.arange(m) / SR
    pad = sum(np.sin(2 * np.pi * fq * tt) + 0.25 * np.sin(2 * np.pi * fq * 2.003 * tt) for fq in ch)
    pad *= np.minimum(1, tt / 0.6) * np.minimum(1, (bar - tt) / 0.5) * 0.010
    put(loop, pad, tb)
    for j in range(8):
        fq = ch[j % 3] * 2 * (2 if j in (3, 7) else 1); mm = int(0.45 * SR); t2 = np.arange(mm) / SR
        pl = (np.sin(2 * np.pi * fq * t2) + 0.2 * np.sin(2 * np.pi * 2 * fq * t2)) * env_ad(mm, 0.004, 0.16) * 0.012
        put(loop, pl, tb + j * beat / 2)
    k += 1; tb += bar
loop = loop[:n] * 2.0
lv = np.interp(t, [0, T(B['SH']['C'][1]), T(B['CARD'][1]) + 0.04, T(B['DROOP'][0]), T(B['CLOSE'][1]), T(B['REVEAL']), DUR],
                  [0.55, 0.55, 0.38, 0.30, 0.10, 0.0, 0.0])                   # low under the line; sinks as he falls asleep
mus = loop * lv * 0.9

# ---- the reveal: the supplied Vine Boom, once, transient on the reveal frame
src, ssr = sf.read('sfx/vine_boom_src.wav')
if src.ndim > 1: src = src.mean(1)
e = np.convolve(np.abs(src), np.ones(48) / 48, 'same'); hit = int(np.argmax(e > e.max() * 0.25))     # the boom's attack
boom = src / np.abs(src).max() * 10 ** (-4.0 / 20)
B_T0 = T(B['REVEAL']) - hit / SR; B_END = B_T0 + len(boom) / SR

# ---- snoring on his breaths (build.py: inhale starts at SNORE0 and every 66 frames)
def snore(dur, g):
    m = int(dur * SR); tt = np.arange(m) / SR; ph = tt / dur
    fl = np.sin(2 * np.pi * (27 + 4 * ph) * tt); flutter = 0.55 + 0.45 * np.sign(fl) * np.abs(fl) ** 0.5     # soft palate flutter: "hrrrr"
    x = bp(rng.standard_normal(m), 90, 900) * flutter + 0.6 * np.sin(2 * np.pi * (95 + 10 * ph) * tt) * flutter
    return x * np.sin(np.pi * np.clip(ph * 1.05, 0, 1)) ** 1.2 * g
def exhale(dur, g):                                                                                      # "khhh"
    m = int(dur * SR); ph = np.arange(m) / m
    return bp(rng.standard_normal(m), 300, 2500) * np.sin(np.pi * ph) ** 2 * (1 - 0.4 * ph) * g
sn = np.zeros(n); P = 66; first = B['SNORE0']
put(sn, snore(1.0, 0.11), T(first) + 0.02); put(sn, exhale(0.7, 0.035), T(first) + 1.08)
put(sn, snore(1.0, 0.10), T(first + P) + 0.02)

# ---- mix
bed = room + fx + mus
k0 = I(B['REVEAL']); bed[k0:] *= 0.55                     # the wide: just a very quiet room
mix = bed + dlg + sn
put(mix, boom, B_T0)
fe = int(0.12 * SR); mix[-fe:] *= np.linspace(1, 0, fe)   # clean end (no black card)
mix = np.clip(mix, -0.98, 0.98)
st = np.stack([mix, np.roll(mix, 160) * 0.97 + mix * 0.03], 1)
with wave.open('audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('audio', round(DUR, 2), 's | boom file', round(B_T0, 3), '-', round(B_END, 3), '(hit at', round(T(B['REVEAL']), 3), ') | first snore',
      round(T(first) + 0.02, 3), '| peak', round(float(np.abs(mix).max()), 3))
