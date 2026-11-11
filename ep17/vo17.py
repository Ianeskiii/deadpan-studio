"""ep17 dialogue, Doug = am_fenrir (Kokoro), shaped with WORLD (pyworld) so the two lines carry different feelings:
  m = "Mamba out."   relieved, quietly pleased: a satisfied breath first, pitch lifted a touch with a playful rise on "Mam-"
  a = "...Alright."  defeated: a small breath, slower, lower, pitch sagging to the end, a little breathier
Writes vo/<take>.wav (24 kHz)."""
import os, sys, numpy as np, soundfile as sf, pyworld as pw
from kokoro_onnx import Kokoro
k = Kokoro('../tts/kokoro-q8.onnx', '../tts/voices.bin'); SR = 24000; rng = np.random.default_rng(17)
os.makedirs('vo', exist_ok=True)
def trim(a):
    nz = np.where(np.abs(a) > 0.008)[0]; return a[max(0, nz[0] - 240): nz[-1] + 900]
def tx(t, s): return trim(k.create(t, voice='am_fenrir', speed=s, lang='en-us')[0]).astype(np.float64)
def sil(s): return np.zeros(int(s * SR))
def breath(dur, amp, inhale=True):
    n = int(dur * SR); z = rng.standard_normal(n)
    b = np.convolve(z, np.ones(14) / 14, 'same') - np.convolve(z, np.ones(110) / 110, 'same')
    e = np.sin(np.linspace(0, np.pi, n)) ** (1.4 if inhale else 0.8)
    if not inhale: e *= np.linspace(1, 0.25, n)
    return b * e * amp / (np.abs(b).max() + 1e-9)
def shape(x, gain, curve, breathy=0.0):
    """WORLD resynthesis: f0 *= gain * curve(t in 0..1) on voiced frames; optional extra aperiodicity (breathiness)"""
    f0, t = pw.harvest(x, SR, f0_floor=60, f0_ceil=300, frame_period=5.0); sp = pw.cheaptrick(x, f0, t, SR); ap = pw.d4c(x, f0, t, SR)
    v = np.where(f0 > 0)[0]
    if len(v):
        u = np.clip((np.arange(len(f0)) - v[0]) / max(1, v[-1] - v[0]), 0, 1)
        f0 = f0 * gain * np.array([curve(q) for q in u])
    if breathy: ap = np.clip(ap + breathy * (1 - ap), 0, 1)
    y = pw.synthesize(f0, sp, ap, SR, 5.0); return y[:len(x)] if len(y) >= len(x) else np.pad(y, (0, len(x) - len(y)))
def fade(a, ms=8):
    n = int(ms * SR / 1000); a = a.copy(); a[:n] *= np.linspace(0, 1, n); a[-n:] *= np.linspace(1, 0, n); return a
def room(a, wet=0.06, rt=0.25):
    n = int(rt * 1.4 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-6.9 * t / rt); ir[:int(0.006 * SR)] = 0; ir /= np.sqrt(np.sum(ir ** 2))
    w = np.convolve(a, ir); return np.concatenate([a, np.zeros(len(w) - len(a))]) + wet * w
def build(name, parts, peak):
    a = np.concatenate([fade(p) if len(p) > 600 else p for p in parts]); a = room(a); a = a / np.abs(a).max() * peak
    sf.write(f'vo/{name}.wav', a, SR); print(name, round(len(a) / SR, 2))
T = sys.argv[1:] or ['m1', 'm2', 'a1', 'a2']
lift = lambda q: 1.0 + 0.10 * np.sin(np.pi * min(1, q / 0.45)) - 0.06 * q           # up on "Mam-", relaxed fall on "out"
sag = lambda q: 1.0 - 0.16 * q                                                      # pitch sinks through "alright"
if 'm1' in T: build('m1', [breath(0.22, 0.04), sil(0.02), breath(0.18, 0.05, False), sil(0.06), shape(tx('Mamba out.', 0.95), 1.09, lift)], 0.8)
if 'm2' in T: build('m2', [breath(0.22, 0.04), sil(0.02), breath(0.18, 0.05, False), sil(0.06), shape(tx('Mamba out.', 1.02), 1.06, lift)], 0.8)
if 'a1' in T: build('a1', [breath(0.3, 0.05), sil(0.12), shape(tx('Alright.', 0.82), 0.90, sag, 0.15)], 0.62)
if 'a2' in T: build('a2', [breath(0.3, 0.05), sil(0.12), shape(tx('Alright...', 0.78), 0.80, sag, 0.22)], 0.62)
