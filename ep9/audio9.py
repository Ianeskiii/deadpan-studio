import numpy as np, wave
SR = 48000; T = 19.0
SH = 4.0  # inserted ceiling + bored shots after 4.8s
t = np.arange(int(SR*T)) / SR; rng = np.random.default_rng(9)
out = np.zeros_like(t)
def add(snd, at, gain=1.0):
    i = int(at*SR); n = min(len(snd), len(out)-i); out[i:i+n] += gain*snd[:n]
def lp(x, k): return np.convolve(x, np.ones(k)/k, 'same')
noise = rng.standard_normal(len(t))
out += (lp(noise, 60) * 4 + 0.05*np.sin(2*np.pi*100*t)) * 0.35          # bathroom fan
def pat():
    tt = np.arange(int(0.08*SR))/SR; return lp(rng.standard_normal(len(tt)), 12) * np.exp(-tt*60) * 3
for at in (0.3, 0.7, 1.1): add(pat(), at, 0.8)
def drip():
    tt = np.arange(int(0.25*SR))/SR; f = 900 + 900*np.exp(-tt*40)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-tt*22)
for at in (2.6, 3.3, 4.0, 4.7, 6.9, 7.9, 8.6, 7.3 + SH, 8.6 + SH, 14.5 + SH): add(drip(), at, 0.35)
fan2 = lp(rng.standard_normal(int(1.6*SR)), 30) * 2.5 * np.sin(np.linspace(0, np.pi, int(1.6*SR)))**0.5; add(fan2, 4.8, 0.6)
def breath(d, up=True):
    n = int(d*SR); e = np.linspace(0, 1, n) if up else np.linspace(1, 0, n)**1.5
    return lp(rng.standard_normal(n), 18 if up else 30) * e * np.sin(np.linspace(0, np.pi, n))**0.3
add(breath(0.35), 6.4 + 14/30, 0.5); add(breath(0.75, False), 6.4 + 24/30, 1.2)
def tok():
    tt = np.arange(int(0.1*SR))/SR; return np.sin(2*np.pi*320*tt) * np.exp(-tt*50) + lp(rng.standard_normal(len(tt)), 6)*np.exp(-tt*80)*0.5
add(tok(), 4.8 + SH + 44/30, 0.7)
out = out / np.max(np.abs(out)) * 0.4
def load(p):
    with wave.open(p) as w_:
        a = np.frombuffer(w_.readframes(w_.getnframes()), '<i2').astype(float) / 32768; sr = w_.getframerate()
    return np.interp(np.arange(int(len(a)*SR/sr))*sr/SR, np.arange(len(a)), a)
for p, at in (('vo/doug1.wav', 9.2 + SH + 11/30), ('vo/doug2.wav', 12.4 + SH + 17/30)):
    v = load(p); add(v / np.abs(v).max() * 0.9, at)
out = np.clip(out, -0.98, 0.98); st = np.stack([out, out], 1)
with wave.open('ep9_audio.wav', 'wb') as w_:
    w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((st*32767).astype('<i2').tobytes())
print('audio ok')
