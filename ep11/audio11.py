import numpy as np, wave
SR = 48000; T = 16.0
def load(p):
    with wave.open(p) as w_:
        a = np.frombuffer(w_.readframes(w_.getnframes()), '<i2').astype(float) / 32768; sr = w_.getframerate(); ch = w_.getnchannels()
    a = a.reshape(-1, ch)
    if ch == 1: a = np.repeat(a, 2, axis=1)
    if sr != SR:
        idx = np.arange(int(len(a)*SR/sr))*sr/SR
        a = np.stack([np.interp(idx, np.arange(len(a)), a[:, c]) for c in (0, 1)], 1)
    return a
out = load('music.wav')[:int(SR*T)] * 0.85
rng = np.random.default_rng(11)
def add(snd, at, gain=1.0):
    i = int(at*SR); n = min(len(snd), len(out)-i); out[i:i+n] += gain*snd[:n, None] if snd.ndim == 1 else gain*snd[:n]
def lp(x, k): return np.convolve(x, np.ones(k)/k, 'same')
def swish(d):
    n = int(d*SR); return lp(rng.standard_normal(n), 10) * np.sin(np.linspace(0, np.pi, n))**2 * 2.5
def thud():
    tt = np.arange(int(0.3*SR))/SR; return np.sin(2*np.pi*(60 + 80*np.exp(-tt*20))*tt) * np.exp(-tt*12) * 1.4
def tweet(f0):
    tt = np.arange(int(0.12*SR))/SR; return np.sin(2*np.pi*(f0 + 1500*np.sin(np.pi*tt/0.12))*tt) * np.sin(np.pi*tt/0.12) * 0.5
add(swish(0.25), 142/30, 0.5)            # grab
add(swish(0.45), 331/30, 0.6)            # spin whoosh
add(thud(), 349/30, 0.8); add(thud(), 357/30, 0.35)
v = load('oof.wav')[:, 0]; add(v / np.abs(v).max(), 350/30, 0.55)
for k in range(8): add(tweet(2600 + 300*(k % 3)), 12.1 + k*0.33, 0.12)
out = np.clip(out, -0.98, 0.98)
with wave.open('ep11_audio.wav', 'wb') as w_:
    w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((out*32767).astype('<i2').tobytes())
print('audio ok')
