import numpy as np, wave
SR = 48000; T = 11.4
t = np.arange(int(SR*T)) / SR; rng = np.random.default_rng(10)
out = np.zeros_like(t)
def add(snd, at, gain=1.0):
    i = int(at*SR); n = min(len(snd), len(out)-i); out[i:i+n] += gain*snd[:n]
def lp(x, k): return np.convolve(x, np.ones(k)/k, 'same')
room = lp(rng.standard_normal(len(t)), 150) * 5
out += room * 0.12
def chirp(f0, f1, d):
    tt = np.arange(int(d*SR))/SR; return np.sin(2*np.pi*(f0 + (f1-f0)*tt/d)*tt) * np.sin(np.pi*tt/d)
for at in (0.4, 0.62, 1.8, 2.05, 3.5, 5.2, 5.45, 6.6): add(chirp(3600, 4600, 0.08), at, 0.06)
def pluck(f, d=0.15):
    tt = np.arange(int(d*SR))/SR; return np.sin(2*np.pi*f*tt) * np.exp(-tt*30)
add(pluck(660), 29/30, 0.15)
def swish(d):
    n = int(d*SR); return lp(rng.standard_normal(n), 25) * np.sin(np.linspace(0, np.pi, n)) * 3
add(swish(0.8), 50/30, 0.5)
def tok():
    tt = np.arange(int(0.1*SR))/SR; return np.sin(2*np.pi*260*tt) * np.exp(-tt*45) + lp(rng.standard_normal(len(tt)), 6)*np.exp(-tt*80)*0.5
add(tok(), 84/30, 0.6); add(swish(0.4), 3.2, 0.3); add(tok(), 3.2 + 46/30, 0.5)
def phew(d):
    n = int(d*SR); return lp(rng.standard_normal(n), 30) * np.linspace(1, 0, n)**1.4 * 3
add(phew(0.6), 4.05, 0.45)
def beep():
    tt = np.arange(int(0.075*SR))/SR; return np.sign(np.sin(2*np.pi*2800*tt)) * 0.6 * np.minimum(1, np.minimum(tt/0.002, (0.075-tt)/0.002))
a0 = 7.2 + 2/30
k = a0
while k < T:
    for b in range(4): add(beep(), k + b*0.14, 0.45)
    k += 0.95
out = np.clip(out, -0.9, 0.9)
def load(p):
    with wave.open(p) as w_:
        a = np.frombuffer(w_.readframes(w_.getnframes()), '<i2').astype(float) / 32768; sr = w_.getframerate()
    return np.interp(np.arange(int(len(a)*SR/sr))*sr/SR, np.arange(len(a)), a)
g = load('vo/shout.wav'); add(g / np.abs(g).max() * 0.9, 8.4 + 2/30)
out = out / np.max(np.abs(out)) * 0.9
st = np.stack([out, out], 1)
with wave.open('ep10_audio.wav', 'wb') as w_:
    w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((st*32767).astype('<i2').tobytes())
print('audio ok')
