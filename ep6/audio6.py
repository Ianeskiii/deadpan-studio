import numpy as np, wave, json
SR = 48000; T = 14.8
t = np.arange(int(SR*T)) / SR; rng = np.random.default_rng(5)
out = np.zeros_like(t)
def env(a, b, fade=0.08):
    e = np.zeros_like(t); e[(t >= a) & (t < b)] = 1; k = int(fade*SR)
    return np.convolve(e, np.ones(k)/k, 'same')
def add(snd, at, gain=1.0):
    i = int(at*SR); n = min(len(snd), len(out)-i); out[i:i+n] += gain*snd[:n]
def lp(x, k): return np.convolve(x, np.ones(k)/k, 'same')
noise = rng.standard_normal(len(t))
# day street: low rumble + traffic swells + birds
street = lp(noise, 120) * 6 * (0.7 + 0.3*np.sin(2*np.pi*0.23*t)**2)
day = env(0, 3.2) + env(14.0, 14.9, 0.02)
out += street * day * 0.5
def chirp(f0, f1, d):
    tt = np.arange(int(d*SR))/SR; return np.sin(2*np.pi*(f0 + (f1-f0)*tt/d)*tt) * np.sin(np.pi*tt/d)
for at in (0.3, 0.55, 1.9, 2.15, 14.2): add(chirp(3200, 4200, 0.09), at, 0.12)
# night: quieter street + crickets
out += street * env(7.6, 14.0) * 0.18
def cricket():
    tt = np.arange(int(0.18*SR))/SR
    return np.sin(2*np.pi*4600*tt) * (np.sin(2*np.pi*30*tt) > 0) * np.sin(np.pi*tt/0.18)
c = 7.65
while c < 14.0:
    add(cricket(), c, 0.08); add(cricket(), c + 0.25, 0.05); c += 0.9 + rng.uniform(-0.1, 0.1)
# spa music 3.2-7.6: soft pad + pentatonic chimes + water
seg = env(3.2, 7.6, 0.15)
pad = sum(np.sin(2*np.pi*f*t) * a for f, a in ((220, .25), (277.2, .2), (329.6, .2), (440, .1)))
out += pad * seg * 0.35 * (0.8 + 0.2*np.sin(2*np.pi*0.5*t))
def bell(f, d=1.2):
    tt = np.arange(int(d*SR))/SR; return (np.sin(2*np.pi*f*tt) + 0.3*np.sin(2*np.pi*2*f*tt)) * np.exp(-tt*3)
for k, f in enumerate((659.3, 880, 740, 987.8, 880, 659.3, 554.4)): add(bell(f), 3.3 + k*0.6, 0.18)
out += lp(noise, 30) * seg * 0.12
# pings, whoosh, sigh, time-card hit
def ping():
    a = bell(1318.5, 0.25); b = bell(1760, 0.35); s = np.zeros(int(0.5*SR)); s[:len(a)] += a; s[int(0.09*SR):int(0.09*SR)+len(b)] += b; return s
add(ping(), 1.6 + 13/30, 0.5); add(ping(), 9.8 + 15/30, 0.5)
w = lp(rng.standard_normal(int(0.35*SR)), 8) * np.sin(np.linspace(0, np.pi, int(0.35*SR)))**2; add(w, 5.2 + 56/30, 0.6)
hit_t = np.arange(int(0.6*SR))/SR; add(np.sin(2*np.pi*70*hit_t)*np.exp(-hit_t*6), 7.6, 0.5)
sig = lp(rng.standard_normal(int(0.8*SR)), 25) * np.concatenate([np.linspace(0, 1, int(0.15*SR)), np.linspace(1, 0, int(0.65*SR))]); add(sig, 11.6 + 46/30, 0.9)
out = out / np.max(np.abs(out)) * 0.6
def load(p):
    with wave.open(p) as w_:
        a = np.frombuffer(w_.readframes(w_.getnframes()), '<i2').astype(float) / 32768; sr = w_.getframerate()
    return np.interp(np.arange(int(len(a)*SR/sr))*sr/SR, np.arange(len(a)), a)
v = load('vo/tina.wav'); add(v / np.abs(v).max() * 0.85, 5.2 + 11/30)
out = np.clip(out, -0.98, 0.98); st = np.stack([out, out], 1)
with wave.open('ep6_audio.wav', 'wb') as w_:
    w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((st*32767).astype('<i2').tobytes())
print('audio ok')
