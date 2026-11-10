"""TV audio (JP dialogue + original dramatic score) heard in a quiet living room; everything on the TV stops dead at the silence."""
import numpy as np, json, wave, os, soundfile as sf
VO = os.environ.get('VO', 'vo'); OUT = os.environ.get('OUT', 'anime_audio.wav')   # V2: VO=vo2 OUT=anime_audio_v2.wav
SR = 48000; T = json.load(open('vo/timing.json')); B = json.load(open('beats.json'))
N = B['N']; DUR = N / 30; n = int(DUR * SR); t = np.arange(n) / SR
STOP = (B['F_SILENCE'] - 1) / 30; BLACK = (B['F_BLACK'] - 1) / 30
rng = np.random.default_rng(13)
def bp(x, lo, hi):
    F = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); F[(f < lo) | (f > hi)] = 0; return np.fft.irfft(F, len(x))
def lp(x, k): return np.convolve(x, np.ones(k) / k, 'same')
def load(p):
    a, sr = sf.read(p, always_2d=True); a = a.mean(1)
    return np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a) if sr != SR else a
tv = np.zeros(n)
# ---- original score: low string drone (minor), taiko-style hits that speed up with the argument
def note(f0, dur, g, attack=0.3):
    tt = np.arange(int(dur * SR)) / SR
    s = sum(np.sin(2 * np.pi * f0 * k * tt + rng.random() * 6) / k ** 1.3 for k in range(1, 7))
    return s * np.minimum(1, tt / attack) * np.minimum(1, (dur - tt) / 0.4) * g
def put(buf, s, t0, g=1.0):
    i = int(t0 * SR); m = min(len(s), n - i)
    if m > 0: buf[i:i + m] += s[:m] * g
chords = [[110.0, 130.81, 164.81], [98.0, 116.54, 146.83], [87.31, 110.0, 130.81], [98.0, 123.47, 146.83]]   # Am - Gm - F - G (dark)
tc = 0.0; k = 0
while tc < STOP:
    for f0 in chords[k % 4]: put(tv, note(f0, 2.2, 0.05), tc); put(tv, note(f0 * 2, 2.2, 0.018), tc)
    tc += 2.0; k += 1
def taiko(g):
    m = int(0.45 * SR); tt = np.arange(m) / SR
    return (np.sin(2 * np.pi * (70 * np.exp(-tt * 3) + 45) * tt) * np.exp(-tt * 9) + bp(rng.standard_normal(m), 200, 2500) * np.exp(-tt * 40) * 0.3) * g
lines = T['lines']; esc = lines[4]['t']; bar = lines[10]['t']
tb = 0.4
while tb < STOP:
    period = 1.0 if tb < esc else (0.5 if tb < bar else 0.25)
    g = 0.22 if tb < esc else (0.28 if tb < bar else 0.32)
    put(tv, taiko(g), tb); tb += period
# rising string tremolo through the barrage
for tt0 in np.arange(bar, STOP, 0.125):
    put(tv, note(220 * 2 ** ((tt0 - bar) * 0.8 / 12), 0.12, 0.03, attack=0.01), tt0)
# ---- dialogue: dry, a little hot (anime mix)
for l in lines:
    a = load(f"{VO}/l{l['i']:02d}.wav"); hot = 2.2 if VO != 'vo' else 1.6   # shouted takes are driven a bit harder
    a = np.tanh(a / np.abs(a).max() * hot) / np.tanh(hot)
    put(tv, a, l['t'], 0.62)
if os.path.exists(f'{VO}/breaths.json'):
    for b in json.load(open(f'{VO}/breaths.json')): put(tv, load(f"{VO}/breath_{b['i']:02d}.wav"), b['t'], 0.5)
tv[int(STOP * SR):] = 0                                   # the TV goes silent at once
# ---- TV speaker + room: band-limit, small-room reflection
tv = bp(tv, 110, 7500)
ir_n = int(0.35 * SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 18); ir[:int(0.004 * SR)] = 0
ir = lp(ir, 5); ir /= np.sqrt((ir ** 2).sum())
tvr = tv + 0.12 * np.convolve(tv, ir)[:n]
# ---- living room: very quiet tone (fridge hum + air) that stays through the silence
room = bp(rng.standard_normal(n), 60, 900) * 0.0045 + np.sin(2 * np.pi * 60 * t) * 0.0012 + np.sin(2 * np.pi * 120 * t) * 0.0008
mix = tvr + room
mix[int(BLACK * SR):] *= np.linspace(1, 0, n - int(BLACK * SR)) ** 2   # fade the room out over the black
pk = np.abs(mix).max(); mix = mix / pk * 10 ** (-1.5 / 20)
st = np.stack([mix, np.roll(mix, 240) * 0.98 + mix * 0.02], 1)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('audio', round(DUR, 2), 's; TV stops at', round(STOP, 2), 's; black at', round(BLACK, 2))
