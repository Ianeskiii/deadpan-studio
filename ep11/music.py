"""Original upbeat funk-house loop: 120 BPM, 8 bars (16 s), F major. Loops seamlessly."""
import numpy as np, wave
SR = 48000; BPM = 120; BEAT = 60 / BPM; BARS = 8; T = BARS * 4 * BEAT
N = int(SR * T); t = np.arange(N) / SR
rng = np.random.default_rng(42)
mix = np.zeros((N, 2))
def place(sig, at, gain=1.0, pan=0.0):
    i = int(round(at * SR)) % N; n = len(sig)
    l, r = gain * (1 - pan) / 2 * 2, gain * (1 + pan) / 2 * 2
    seg = np.arange(i, i + n) % N               # wrap -> seamless loop
    mix[seg, 0] += sig * min(1, l); mix[seg, 1] += sig * min(1, r)
def note(n): return 440 * 2 ** ((n - 69) / 12)
def env_adsr(n, a=0.005, d=0.08, s=0.6, r=0.05):
    e = np.ones(n); A, Dd, R = int(a*SR), int(d*SR), int(r*SR)
    e[:A] = np.linspace(0, 1, A); e[A:A+Dd] = np.linspace(1, s, Dd); e[A+Dd:] = s
    e[-R:] *= np.linspace(1, 0, R); return e
def onepole(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def saw(f, d):
    tt = np.arange(int(d*SR)) / SR; return 2 * ((tt * f) % 1) - 1
# drums
def kick():
    tt = np.arange(int(0.35*SR)) / SR; f = 45 + 95 * np.exp(-tt * 28)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-tt * 9) * 1.1
def clap():
    tt = np.arange(int(0.22*SR)) / SR; nz = rng.standard_normal(len(tt))
    e = np.exp(-tt*28) + 0.6*np.exp(-((tt-0.012)%0.011)*400)*(tt < 0.035)
    return (nz - onepole(nz, 0.25)) * e * 0.5
def hat(open_=False):
    d = 0.18 if open_ else 0.04; tt = np.arange(int(d*SR)) / SR; nz = rng.standard_normal(len(tt))
    return (nz - onepole(nz, 0.6)) * np.exp(-tt * (14 if open_ else 90)) * (0.14 if open_ else 0.10)
K, C, HC, HO = kick(), clap(), hat(), hat(True)
for b in range(BARS * 4):
    at = b * BEAT
    place(K, at, 0.9)
    if b % 2 == 1: place(C, at, 0.55, 0.05)
    place(HO, at + BEAT / 2, 0.8, 0.2)
    place(HC, at + BEAT / 4, 0.7, -0.25); place(HC, at + 3 * BEAT / 4, 0.6, -0.25)
# sidechain envelope (pumping)
duck = np.ones(N)
for b in range(BARS * 4):
    i = int(b * BEAT * SR); L = int(0.22 * SR)
    duck[i:i+L] = np.minimum(duck[i:i+L], 0.35 + 0.65 * (np.arange(L) / L) ** 0.7)
# harmony: Fmaj7 | Em7 | Dm7 | C(add9)  x2
prog = [(53, [65, 69, 72, 76]), (52, [64, 67, 71, 74]), (50, [62, 65, 69, 72]), (48, [64, 67, 72, 74])] * 2
bassline = [0, None, 12, 0, None, 0, 10, 12]          # eighth-note offsets per beat-pair
music = np.zeros(N)
for bar, (root, chord) in enumerate(prog):
    b0 = bar * 4 * BEAT
    for k in range(8):                                   # bass in eighths
        off = bassline[k]
        if off is None: continue
        d = BEAT / 2 * 0.9; f = note(root - 12 + off)
        s = saw(f, d) * env_adsr(int(d*SR), 0.003, 0.06, 0.5, 0.02)
        s = onepole(s, 0.12) * 0.55 + np.sin(2*np.pi*f*np.arange(len(s))/SR) * 0.35 * env_adsr(len(s), 0.003, 0.06, 0.5, 0.02)
        place(s, b0 + k * BEAT / 2, 0.85)
    for hit in (0.5, 1.5, 2.5, 3.25, 3.75):             # chord stabs on offbeats
        d = 0.16
        st = sum(saw(note(n) * (1 + dt), d) for n in chord for dt in (-0.004, 0.004))
        st = onepole(st * env_adsr(int(d*SR), 0.002, 0.07, 0.25, 0.04), 0.35) * 0.09
        for pan in (-0.4, 0.4): place(st, b0 + hit * BEAT, 0.6, pan)
# lead hook (bars 2-4 and 6-8), square-ish pluck
hook = [(0, 77, .5), (.5, 76, .5), (1, 72, .5), (1.75, 74, .25), (2, 72, .5), (2.5, 69, .5), (3, 72, 1)]
def pluck(f, d):
    n = int(d*SR); tt = np.arange(n) / SR
    s = np.sign(np.sin(2*np.pi*f*tt)) * 0.5 + np.sin(2*np.pi*2*f*tt) * 0.3
    return onepole(s, 0.3) * np.exp(-tt * 5) * env_adsr(n, 0.004, 0.05, 0.8, 0.03)
for bar in (1, 2, 3, 5, 6, 7):
    for (bt, n, d) in hook:
        tr = 0 if bar % 4 != 3 else 2
        place(pluck(note(n + tr), d * BEAT * 0.95) * 0.16, (bar * 4 + bt) * BEAT, 1.0, 0.1)
# pad for warmth
pad = np.zeros(N)
for bar, (root, chord) in enumerate(prog):
    i0 = int(bar * 4 * BEAT * SR); n = int(4 * BEAT * SR); tt = np.arange(n) / SR
    s = sum(np.sin(2*np.pi*note(c)*tt) for c in chord) * 0.03
    pad[i0:i0+n] += s
mix[:, 0] *= duck; mix[:, 1] *= duck
for ch in (0, 1): mix[:, ch] += pad * duck
# simple stereo delay for space (wraps for seamless loop)
d = int(BEAT * 0.75 * SR)
wet = np.roll(mix, d, axis=0) * 0.18; wet[:, [0, 1]] = wet[:, [1, 0]]
mix += wet
mix /= np.max(np.abs(mix)); mix *= 0.92
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype('<i2').tobytes())
print('music', round(T, 2), 's')
