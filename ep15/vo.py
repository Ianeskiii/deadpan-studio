"""Dialogue takes: Doug = am_fenrir (calm, mildly suspicious), Green = am_michael (casual, confident, small hitches).
Whole-phrase Kokoro takes, light EQ + small living-room reverb, breaths. Writes vo/<line>.wav (24 kHz)."""
import os, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro('../tts/kokoro-q8.onnx', '../tts/voices.bin')
SR = 24000; rng = np.random.default_rng(15)
DG, GR = 'am_fenrir', 'am_michael'
os.makedirs('vo', exist_ok=True)
def trim(a):
    nz = np.where(np.abs(a) > 0.008)[0]; return a[max(0, nz[0] - 240): nz[-1] + 900]
def tx(t, v, s): return trim(k.create(t, voice=v, speed=s, lang='en-us')[0])
def sil(s): return np.zeros(int(s * SR))
def breath(dur=0.24, amp=0.03, inhale=True):
    n = int(dur * SR); z = rng.standard_normal(n)
    b = np.convolve(z, np.ones(14) / 14, 'same') - np.convolve(z, np.ones(110) / 110, 'same')
    e = np.sin(np.linspace(0, np.pi, n)) ** (1.4 if inhale else 0.8)
    if not inhale: e *= np.linspace(1, 0.25, n)
    return b * e * amp / (np.abs(b).max() + 1e-9)
def fade(a, ms=8):
    n = int(ms * SR / 1000); a = a.copy(); a[:n] *= np.linspace(0, 1, n); a[-n:] *= np.linspace(1, 0, n); return a
def tone(a, presence=0.2, lowcut=85):
    from numpy.fft import rfft, irfft, rfftfreq
    n = len(a) + 2048; F = rfft(a, n); f = rfftfreq(n, 1 / SR)
    H = 1 / np.sqrt(1 + (lowcut / np.maximum(f, 1)) ** 4) * (1 + presence * np.exp(-((f - 3000) / 1500) ** 2))
    return irfft(F * H, n)[:len(a)]
def room(a, wet=0.08, rt=0.28):
    n = int(rt * 1.4 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-6.9 * t / rt); ir[:int(0.006 * SR)] = 0
    ir = np.convolve(ir, np.ones(6) / 6, 'same'); ir /= np.sqrt(np.sum(ir ** 2))
    w = np.convolve(a, ir); return np.concatenate([a, np.zeros(len(w) - len(a))]) + wet * w
def norm(a): return a / (np.abs(a).max() + 1e-9) * 0.89
def build(name, parts, wet=0.08):
    a = np.concatenate([fade(p) if len(p) > 600 else p for p in parts])
    a = norm(room(tone(a), wet)); sf.write(f'vo/{name}.wav', a, SR); print(name, round(len(a) / SR, 2))
LINES = sys.argv[1:] or ['d1', 'g1', 'g2', 'g3', 'g4']
if 'd1' in LINES: build('d1', [breath(0.2, 0.02), tx('Did you eat my cake?', DG, 0.9)])
if 'g1' in LINES: build('g1', [tx('What?', GR, 1.05), sil(0.34), tx('No.', GR, 1.0)])
if 'g2' in LINES: build('g2', [breath(0.16, 0.025), tx("I haven't even seen your cake.", GR, 1.02)])
if 'g3' in LINES: build('g3', [tx('Why are you looking at me like that?', GR, 1.0)])
if 'g4' in LINES: build('g4', [breath(0.3, 0.03), sil(0.1), tx("That's not mine.", GR, 0.9)])
