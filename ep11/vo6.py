"""Build performed dialogue from phrase-level TTS: per-phrase speed/pitch, breaths, pauses, groan/sigh, EQ, room."""
import sys, numpy as np, soundfile as sf
sys.path.insert(0, '../tts')
from kokoro_onnx import Kokoro
k = Kokoro('../tts/kokoro-q8.onnx', '../tts/voices.bin')
SR = 24000
rng = np.random.default_rng(6)
def tts(text, voice, speed):
    a, sr = k.create(text, voice=voice, speed=speed, lang='en-us'); assert sr == SR
    nz = np.where(np.abs(a) > 0.01)[0]                     # trim leading/trailing silence
    return a[max(0, nz[0] - 200): nz[-1] + 600] if len(nz) else a
def pitch(a, semis):
    """duration-preserving pitch shift via ffmpeg asetrate + atempo"""
    if abs(semis) < 0.01: return a
    import subprocess, tempfile, os
    r = 2 ** (semis / 12)
    with tempfile.TemporaryDirectory() as td:
        i, o = os.path.join(td, 'i.wav'), os.path.join(td, 'o.wav'); sf.write(i, a, SR)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', i, '-af', f'asetrate={SR * r:.1f},aresample={SR},atempo={1 / r:.5f}', o], check=True)
        b, _ = sf.read(o)
    return b
def gain(a, g): return a * g
def silence(s): return np.zeros(int(s * SR))
def breath(dur=0.28, amp=0.06, inhale=True):
    n = int(dur * SR); nz = rng.standard_normal(n)
    b = np.convolve(nz, np.ones(18) / 18, 'same') - np.convolve(nz, np.ones(120) / 120, 'same')
    e = np.sin(np.linspace(0, np.pi, n)) ** (1.5 if inhale else 0.8)
    if not inhale: e *= np.linspace(1, 0.2, n)
    return b * e * amp / (np.abs(b).max() + 1e-9)
def fade(a, ms=8):
    n = int(ms * SR / 1000); a = a.copy(); a[:n] *= np.linspace(0, 1, n); a[-n:] *= np.linspace(1, 0, n); return a
def eq_room(a):
    # high-pass ~90 Hz, gentle presence lift, light compression, short outdoor slap/room
    from numpy.fft import rfft, irfft, rfftfreq
    n = len(a) + 4096; F = rfft(a, n); f = rfftfreq(n, 1 / SR)
    H = 1 / np.sqrt(1 + (90 / np.maximum(f, 1)) ** 4) * (1 + 0.35 * np.exp(-((f - 3200) / 1400) ** 2))
    a = irfft(F * H, n)[:len(a)]
    ir = np.zeros(int(0.25 * SR)); ir[0] = 1
    for d, g in ((0.011, 0.18), (0.023, 0.12), (0.041, 0.08), (0.087, 0.05), (0.13, 0.03)): ir[int(d * SR)] += g
    tail = rng.standard_normal(len(ir)) * np.exp(-np.arange(len(ir)) / (0.05 * SR)) * 0.015; ir += tail
    a = np.convolve(a, ir)[:len(a) + int(0.2 * SR)]
    a = np.tanh(a / (np.abs(a).max() + 1e-9) * 1.6) / np.tanh(1.6)
    return a * 0.89
def build(name, parts):
    seq = []
    for p in parts: seq.append(fade(p) if len(p) > 400 else p)
    a = eq_room(np.concatenate(seq)); sf.write(f'vo6/{name}.wav', a, SR); print(name, round(len(a) / SR, 2), 's')
G = 'am_michael'   # Green (Ricky): street-smart, gets more and more frustrated
DG = 'am_onyx'     # Doug: low, calm, deadpan
# Green 1 - confident demand that escalates: "Hey. ...Hey! Gimme the bag."
build('g1', [breath(0.22, 0.05), gain(pitch(tts('Hey.', G, 1.0), -0.5), 0.8), silence(0.32),
             gain(pitch(tts('Hey!', G, 1.1), 2.0), 1.0), silence(0.12), pitch(tts('Gimme the bag.', G, 1.08), 0.8)])
# Green 2 - straining: "Come ON—"
build('g2', [breath(0.18, 0.08), gain(pitch(tts('Come on!', G, 1.2), 3.5), 1.0)])
# Green 3 - full effort: "Let... GO!"
build('g3', [breath(0.2, 0.09), pitch(tts('Let...', G, 1.15), 1.5), silence(0.06), gain(pitch(tts('go!', G, 1.1), 4.5), 1.05)])
# Green 4 - annoyed, defeated: "Ugh— you know what? Forget it."
build('g4', [pitch(tts('Ugh.', G, 0.92), -1.5), silence(0.1), breath(0.14, 0.05),
             pitch(tts('You know what?', G, 1.18), 1.2), silence(0.22),
             gain(pitch(tts('Forget it.', G, 0.95), -2.8), 0.8), breath(0.32, 0.05, inhale=False)])
# Doug - deadpan check-in: "...You good?"
build('d1', [silence(0.05), pitch(tts('You good?', DG, 0.85), -0.8)])
