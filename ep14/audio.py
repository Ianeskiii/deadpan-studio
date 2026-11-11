"""No dialogue. Quiet living room; soft screen taps; a small camera-open sound; silence for the reaction;
a muffled phone set-down; blanket rustle; room tone fades out over the black."""
import numpy as np, json, wave
SR = 48000; B = json.load(open('beats.json'))
N = B['N']; DUR = N / 30; n = int(DUR * SR); t = np.arange(n) / SR
rng = np.random.default_rng(14)
def T(f): return (f - 1) / 30
def bp(x, lo, hi):
    F = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR); F[(fr < lo) | (fr > hi)] = 0; return np.fft.irfft(F, len(x))
def put(buf, s, t0, g=1.0):
    i = int(t0 * SR); m = min(len(s), n - i)
    if m > 0: buf[i:i + m] += s[:m] * g
mix = np.zeros(n)
# room tone: air + faint fridge hum from the next room
mix += bp(rng.standard_normal(n), 80, 1200) * 0.004 + np.sin(2 * np.pi * 58 * t) * 0.0009 + np.sin(2 * np.pi * 116 * t) * 0.0005
def tap(g=1.0):
    m = int(0.05 * SR); tt = np.arange(m) / SR
    click = bp(rng.standard_normal(m), 1800, 7000) * np.exp(-tt * 260)
    knock = np.sin(2 * np.pi * 900 * tt) * np.exp(-tt * 180) * 0.4
    return (click + knock) * g
def swipe(g=1.0):
    m = int(0.14 * SR); tt = np.arange(m) / SR; env = np.sin(np.pi * tt / tt[-1]) ** 2
    return bp(rng.standard_normal(m), 2500, 9000) * env * g
for s in B['SWIPES']:
    put(mix, tap(0.05), T(s)); put(mix, swipe(0.02), T(s) + 0.01)
put(mix, tap(0.07), T(B['TAP_CAM']))
if B.get('SWIPE_CAM'): put(mix, tap(0.045), T(B['SWIPE_CAM'])); put(mix, swipe(0.02), T(B['SWIPE_CAM']) + 0.01)
# camera opening: a soft rising blip + a tiny mechanical tick (original, synthetic)
m = int(0.16 * SR); tt = np.arange(m) / SR
blip = np.sin(2 * np.pi * (700 * tt + 2600 * tt * tt)) * np.minimum(1, tt / 0.01) * np.exp(-tt * 18)
put(mix, blip * 0.06, T(B['CAM_ON'])); put(mix, tap(0.05), T(B['CAM_ON']) + 0.12)
# screen off: lock click
m = int(0.06 * SR); tt = np.arange(m) / SR
put(mix, (np.sin(2 * np.pi * 1600 * tt) * np.exp(-tt * 120) + bp(rng.standard_normal(m), 2000, 6000) * np.exp(-tt * 300)) * 0.06, T(B['TAP_OFF']))
# phone set face down on the cushion: muffled, soft
m = int(0.25 * SR); tt = np.arange(m) / SR
thud = bp(rng.standard_normal(m), 60, 500) * np.exp(-tt * 30) + np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 25) * 0.5
put(mix, thud * 0.10, T(B['PUT_DOWN']))
# small arm/fabric movements when the phone goes up and down
for a, b in B['RAISE'] + B['LOWER']:
    m = int((b - a) / 30 * SR); tt = np.arange(m) / SR; env = np.sin(np.pi * tt / tt[-1]) ** 2
    put(mix, bp(rng.standard_normal(m), 600, 4000) * env * 0.006, T(a))
# blanket: grab, the big pull over the head, settle
def rustle(f0, f1, g):
    m = int((f1 - f0) / 30 * SR); tt = np.arange(m) / SR; ph = tt / tt[-1]
    env = np.sin(np.pi * ph) ** 1.5 * (0.7 + 0.3 * np.abs(np.sin(2 * np.pi * 7 * tt + rng.random())))
    x = bp(rng.standard_normal(m), 250, 6000) + 0.5 * bp(rng.standard_normal(m), 3000, 10000)
    return x * env * g
put(mix, rustle(B['GRAB'] - 4, B['GRAB'] + 6, 0.03), T(B['GRAB'] - 4))
put(mix, rustle(B['GRAB'] + 4, B['COVERED'] + 4, 0.06), T(B['GRAB'] + 4))
put(mix, rustle(B['COVERED'], B['COVERED'] + 14, 0.02), T(B['COVERED']))
BLACK = T(B['F_BLACK'])
mix[int(BLACK * SR):] *= np.linspace(1, 0, n - int(BLACK * SR)) ** 2
pk = np.abs(mix).max(); mix = mix / pk * 10 ** (-9 / 20)        # v3: the room sits 6 dB lower so the FAHHHs land on top
# ---------------------------------------------------------------- v3: FAHHH on every bad-selfie reveal (the owner's supplied sound)
import soundfile as sf
src, sr0 = sf.read('sfx/fahhh_src.wav')                             # mono 48 kHz copy of the owner's Fahhh.mp3
if src.ndim > 1: src = src.mean(1)
env = np.convolve(np.abs(src), np.ones(240) / 240, 'same')
on = int(np.argmax(env > env.max() * 0.08)); src = src[max(0, on - 96):]  # trim the lead-in: the attack starts on the frame
src = src / np.abs(src).max()
def fahhh(length, fade, g):
    x = src[:int(length * SR)].copy(); m = int(fade * SR); x[-m:] *= np.linspace(1, 0, m) ** 1.5; return x * g
R = B['REVEALS']
put(mix, fahhh(0.95, 0.30, 10 ** (-3.5 / 20)), T(R[0]))            # 1: the accident
put(mix, fahhh(0.95, 0.30, 10 ** (-3.5 / 20)), T(R[1]))            # 2: too close
CUT = 0.42                                                          # 3: the worst - hotter, and chopped mid-scream
x3 = src[:int(CUT * SR)] * 10 ** (-1.5 / 20); x3[-int(0.004 * SR):] *= np.linspace(1, 0, int(0.004 * SR))
i3 = int(T(R[2]) * SR); mix[i3:i3 + len(x3)] = mix[i3:i3 + len(x3)] * 0.3 + x3
# dead silence after the chop (no room tone), then the room creeps back in
s0 = i3 + len(x3); s1 = s0 + int(0.55 * SR); s2 = s1 + int(0.35 * SR)
mix[s0:s1] = 0; mix[s1:s2] *= np.linspace(0, 1, s2 - s1) ** 2
print('FAHHH at', [round(T(r), 3) for r in R], 'silence', round(s0 / SR, 2), '-', round(s1 / SR, 2))
mix = np.clip(mix, -0.98, 0.98)
st = np.stack([mix, np.roll(mix, 180) * 0.97 + mix * 0.03], 1)
with wave.open('audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('audio', round(DUR, 2), 's')
