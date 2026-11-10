"""Natural dialogue: phrase-level Kokoro takes, small pitch moves only, breaths, mouth noise, cafe room."""
import sys, subprocess, tempfile, os, numpy as np, soundfile as sf
sys.path.insert(0, '../tts')
from kokoro_onnx import Kokoro
k = Kokoro('../tts/kokoro-q8.onnx', '../tts/voices.bin')
SR = 24000; rng = np.random.default_rng(12)
B, DG = 'af_heart', 'am_onyx'          # barista: bright, friendly / Doug: low, flat
def tts(text, voice, speed):
    a, sr = k.create(text, voice=voice, speed=speed, lang='en-us')
    nz = np.where(np.abs(a) > 0.008)[0]
    return a[max(0, nz[0] - 240): nz[-1] + 900] if len(nz) else a
def pitch(a, semis):
    if abs(semis) < 0.01: return a
    r = 2 ** (semis / 12)
    with tempfile.TemporaryDirectory() as td:
        i, o = os.path.join(td, 'i.wav'), os.path.join(td, 'o.wav'); sf.write(i, a, SR)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', i, '-af', f'asetrate={SR*r:.1f},aresample={SR},atempo={1/r:.5f}', o], check=True)
        return sf.read(o)[0]
def sil(s): return np.zeros(int(s * SR))
def breath(dur=0.26, amp=0.05, inhale=True):
    n = int(dur * SR); z = rng.standard_normal(n)
    b = np.convolve(z, np.ones(14) / 14, 'same') - np.convolve(z, np.ones(110) / 110, 'same')
    e = np.sin(np.linspace(0, np.pi, n)) ** (1.4 if inhale else 0.8)
    if not inhale: e *= np.linspace(1, 0.25, n)
    return b * e * amp / (np.abs(b).max() + 1e-9)
def click(amp=0.03):   # lip smack / mouth-open click before speaking
    n = int(0.012 * SR); return rng.standard_normal(n) * np.exp(-np.arange(n) / 40) * amp
def fade(a, ms=10):
    n = int(ms * SR / 1000); a = a.copy(); a[:n] *= np.linspace(0, 1, n); a[-n:] *= np.linspace(1, 0, n); return a
def tone(a, presence=0.25, lowcut=85):
    from numpy.fft import rfft, irfft, rfftfreq
    n = len(a) + 2048; F = rfft(a, n); f = rfftfreq(n, 1 / SR)
    H = 1 / np.sqrt(1 + (lowcut / np.maximum(f, 1)) ** 4) * (1 + presence * np.exp(-((f - 3000) / 1500) ** 2)) * (1 + 0.15 * np.exp(-((f - 220) / 120) ** 2))
    return irfft(F * H, n)[:len(a)]
def room(a, wet=0.12, rt=0.35):
    n = int(rt * 1.4 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-6.9 * t / rt); ir[:int(0.006 * SR)] = 0
    ir = np.convolve(ir, np.ones(6) / 6, 'same'); ir /= np.sqrt(np.sum(ir ** 2))
    w = np.convolve(a, ir)[:len(a) + n]; d = np.concatenate([a, np.zeros(len(w) - len(a))])
    return d + wet * w
def comp(a, drive=1.4):
    return np.tanh(a / (np.abs(a).max() + 1e-9) * drive) / np.tanh(drive) * 0.89
def build(name, parts, wet=0.12, presence=0.25):
    a = np.concatenate([fade(p) if len(p) > 600 else p for p in parts])
    a = comp(room(tone(a, presence), wet)); sf.write(f'vo/{name}.wav', a, SR)
    print(name, round(len(a) / SR, 2))
# ---- barista: warm and upbeat, slightly fast, lifts on questions
build('b1', [click(), breath(0.18, 0.035), tts('Awesome!', B, 1.08), sil(0.16), breath(0.12, 0.03), tts('Can I get a name for the order?', B, 1.1)])
build('d1', [click(0.02), pitch(tts('Doug.', DG, 0.92), -0.5)])
build('b2', [breath(0.16, 0.03), pitch(tts('Sorry, how do you spell that?', B, 1.04), 0.3)])
# patient spelling: even rhythm, each letter its own take, last one drops
letters = [('Dee.', 0.0, 1.05), ('Oh.', 0.2, 1.05), ('You.', 0.1, 1.05), ('Gee.', -0.9, 0.98)]
parts = [click(0.02), breath(0.2, 0.035)]
for i, (t, p, s) in enumerate(letters):
    parts.append(pitch(tts(t, DG, s), p - 0.5))
    if i < 3: parts.append(sil((0.12, 0.14, 0.2)[i]))
build('d2', parts)
build('b3', [pitch(tts('Perfect.', B, 1.05), 0.4), sil(0.1), pitch(tts('Got it!', B, 1.1), 0.8)])
# announcement across the shop: projected, a little more room
build('b4', [breath(0.22, 0.05), pitch(tts('Coffee for...', B, 1.0), 0.5), sil(0.18), pitch(tts('Dog!', B, 0.95), 1.6)], wet=0.2, presence=0.35)
build('d3', [breath(0.3, 0.04, inhale=False), sil(0.12), pitch(tts('I literally spelled it.', DG, 0.88), -0.6)])
build('b5', [pitch(tts('Yeah?', B, 1.0), 0.5)])
build('b6', [pitch(tts('Have a nice day, Dog!', B, 1.04), 0.8)], wet=0.24)
