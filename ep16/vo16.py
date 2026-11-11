"""v2 dialogue: Doug (am_fenrir) - a happy inhale, "Hah...", "FINALLY!". Writes vo/<take>.wav (24 kHz)."""
import os, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro('../tts/kokoro-q8.onnx', '../tts/voices.bin'); SR = 24000; rng = np.random.default_rng(16)
os.makedirs('vo', exist_ok=True)
def trim(a):
    nz = np.where(np.abs(a) > 0.008)[0]; return a[max(0, nz[0] - 240): nz[-1] + 900]
def tx(t, s, ph=False): return trim(k.create(t, voice='am_fenrir', speed=s, lang='en-us', is_phonemes=ph)[0])
def sil(s): return np.zeros(int(s * SR))
def breath(dur, amp, inhale=True):
    n = int(dur * SR); z = rng.standard_normal(n)
    b = np.convolve(z, np.ones(14) / 14, 'same') - np.convolve(z, np.ones(110) / 110, 'same')
    e = np.sin(np.linspace(0, np.pi, n)) ** (1.4 if inhale else 0.8)
    if not inhale: e *= np.linspace(1, 0.25, n)
    return b * e * amp / (np.abs(b).max() + 1e-9)
def fade(a, ms=8):
    n = int(ms * SR / 1000); a = a.copy(); a[:n] *= np.linspace(0, 1, n); a[-n:] *= np.linspace(1, 0, n); return a
def room(a, wet=0.07, rt=0.28):
    n = int(rt * 1.4 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-6.9 * t / rt); ir[:int(0.006 * SR)] = 0; ir /= np.sqrt(np.sum(ir ** 2))
    w = np.convolve(a, ir); return np.concatenate([a, np.zeros(len(w) - len(a))]) + wet * w
def build(name, parts):
    a = np.concatenate([fade(p) if len(p) > 600 else p for p in parts]); a = room(a); a = a / np.abs(a).max() * 0.89
    sf.write(f'vo/{name}.wav', a, SR); print(name, round(len(a) / SR, 2))
T = sys.argv[1:] or ['a', 'b', 'c', 'd']
# hah = a breathy, smiling exhale-laugh; FINALLY delivered whole-word with "!" for the lift
if 'a' in T: build('a', [breath(0.32, 0.05), sil(0.04), tx('Hah...', 0.9), sil(0.18), tx('Finally!', 0.88)])
if 'b' in T: build('b', [breath(0.32, 0.05), sil(0.04), tx('Haah.', 0.85), sil(0.2), tx('Finally!', 0.92)])
if 'c' in T: build('c', [breath(0.3, 0.06), sil(0.03), breath(0.34, 0.11, False), sil(0.1), tx('Finally!', 0.85)])
if 'd' in T: build('d', [breath(0.32, 0.05), sil(0.04), tx('Hah... Finally!', 0.88)])
