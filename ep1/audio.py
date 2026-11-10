import numpy as np, wave
SR = 48000; T = 12.4
t = np.arange(int(SR*T)) / SR
rng = np.random.default_rng(3)
def env(a, b, fade=0.05):
    e = np.zeros_like(t); m = (t >= a) & (t < b); e[m] = 1
    k = int(fade*SR); 
    if k: e = np.convolve(e, np.ones(k)/k, 'same')
    return e
# microwave hum: mains buzz + fan noise + slow wobble
noise = rng.standard_normal(len(t))
fan = np.convolve(noise, np.ones(40)/40, 'same')            # low-passed hiss
hum = (0.22*np.sin(2*np.pi*120*t) + 0.10*np.sin(2*np.pi*240*t) + 0.05*np.sin(2*np.pi*360*t)
       + 0.9*fan) * (1 + 0.08*np.sin(2*np.pi*0.7*t))
level = 0.55*env(0, 7.8) + 0.18*env(7.8, 9.55, 0.02) + 0.55*env(11.6, 12.5, 0.01)
out = hum * level
def add(snd, at, gain=1.0):
    i = int(at*SR); n = min(len(snd), len(out)-i); out[i:i+n] += gain*snd[:n]
def tone(f, d, shape='sq'):
    tt = np.arange(int(d*SR))/SR
    s = np.sign(np.sin(2*np.pi*f*tt)) * 0.6 + 0.4*np.sin(2*np.pi*f*tt)
    return s * np.minimum(1, np.minimum(tt/0.003, (d-tt)/0.003))
def thud(f0=140, d=0.12):
    tt = np.arange(int(d*SR))/SR
    return np.sin(2*np.pi*(f0*np.exp(-tt*12))*tt) * np.exp(-tt*35)
def squeak(f=900, d=0.07):
    tt = np.arange(int(d*SR))/SR
    return np.sin(2*np.pi*(f + 500*tt/d)*tt) * np.sin(np.pi*tt/d) * 0.5
def click(d=0.03):
    tt = np.arange(int(d*SR))/SR
    return rng.standard_normal(len(tt)) * np.exp(-tt*250)
# Tina's toy footsteps (S4 starts 5.0s)
for k in range(6): add(squeak(850 + 60*(k%2)), 5.05 + k*0.25, 0.35)
# S6 starts 9.4s: latch click, beep cut short, Doug's thuds
add(click(), 9.52, 0.9); add(thud(400, 0.05), 9.52, 0.5)
add(tone(2050, 0.11), 9.56, 0.32)
for k in range(5): add(thud(), 10.05 + k*0.24, 0.6)
out = out / np.max(np.abs(out)) * 0.8
st = np.stack([out, out], 1)
with wave.open('ep1_audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st*32767).astype('<i2').tobytes())
print('audio ok')
