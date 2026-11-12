"""ep19 sound. No music, no laugh track, no sting. The owner's five recordings, as-is (no TTS, no speed or pitch change),
placed at beats.FILE; only a level match (Doug's takes were recorded ~9 dB quieter than Mom's).
Under it: a quiet room tone and the soft whirr of the stand fan. Nothing after Mom's punchline but that room tone,
then a hard cut to silence on black."""
import os, sys, wave
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from beats import *
SR = 48000; DUR = N / 30; n = int(DUR * SR); t = np.arange(n) / SR
rng = np.random.default_rng(19)
def T(f): return (f - 1) / 30
def bp(x, lo, hi):
    F = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR); F[(fr < lo) | (fr > hi)] = 0; return np.fft.irfft(F, len(x))
def put(buf, s, t0, g=1.0):
    i = int(round(t0 * SR)); a = max(0, -i); m = min(len(s), n - i)
    if m > a: buf[i + a:i + m] += s[a:m] * g
room = bp(rng.standard_normal(n), 60, 700) * 0.0035 + bp(rng.standard_normal(n), 1500, 5000) * 0.0004
fan = bp(rng.standard_normal(n), 180, 1400) * 0.0028 * (1 + 0.15 * np.sin(2 * np.pi * 2.2 * t)) + np.sin(2 * np.pi * 110 * t) * 0.0007
# dialogue: speech RMS of each take -> Mom lines to one level, Doug lines ~3 dB under hers (calm, not shouting)
takes = {}
for k in LINES:
    v, vsr = sf.read(f'vo/{k}.wav')
    if v.ndim > 1: v = v.mean(1)
    if vsr != SR: v = np.interp(np.arange(int(len(v) * SR / vsr)) / SR, np.arange(len(v)) / vsr, v)
    takes[k] = v
def srms(v): x = v[np.abs(v) > 0.02]; return np.sqrt(np.mean(x ** 2)) if len(x) else 1e-3
ref = np.mean([srms(takes[k]) for k in LINES if k.startswith('mom')])
dlg = np.zeros(n); gains = {}
for k in LINES:
    tgt = ref * (1.0 if k.startswith('mom') else 10 ** (-3 / 20))
    g = tgt / srms(takes[k]); g = min(g, 0.97 / np.abs(takes[k]).max()); gains[k] = round(20 * np.log10(g), 1)
    put(dlg, takes[k], T(FILE[k]), g)
mix = room + fan + dlg * 0.8
bi = int(T(BLACK) * SR); f_ = int(0.008 * SR); mix[bi - f_:bi] *= np.linspace(1, 0, f_); mix[bi:] = 0.0      # hard cut on black
pk = np.abs(mix).max(); mix = mix / max(1.0, pk / 0.9)
st = np.stack([mix, np.roll(mix, 96) * 0.97 + mix * 0.03], 1)
with wave.open('audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('audio', round(DUR, 2), 's | gains dB', gains, '| cut', round(T(BLACK), 3), '| peak', round(float(np.abs(mix).max()), 3))
