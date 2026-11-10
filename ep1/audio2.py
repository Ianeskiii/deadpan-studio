import numpy as np, wave, json, os
SR = 48000; T = 18.2
t = np.arange(int(SR*T)) / SR
rng = np.random.default_rng(3)
def env(a, b, fade=0.05):
    e = np.zeros_like(t); e[(t >= a) & (t < b)] = 1
    k = int(fade*SR)
    return np.convolve(e, np.ones(k)/k, 'same') if k else e
noise = rng.standard_normal(len(t))
fan = np.convolve(noise, np.ones(40)/40, 'same')
hum = (0.22*np.sin(2*np.pi*120*t) + 0.10*np.sin(2*np.pi*240*t) + 0.05*np.sin(2*np.pi*360*t) + 0.9*fan) * (1 + 0.08*np.sin(2*np.pi*0.7*t))
room = np.convolve(noise, np.ones(200)/200, 'same') * 3
out = hum * (0.55*env(0, 7.8) + 0.18*env(7.8, 9.55, 0.02) + 0.55*env(17.4, 18.3, 0.01)) + room * 0.05
def add(snd, at, gain=1.0):
    i = int(at*SR); n = min(len(snd), len(out)-i); out[i:i+n] += gain*snd[:n]
def tone(f, d):
    tt = np.arange(int(d*SR))/SR
    return (np.sign(np.sin(2*np.pi*f*tt))*0.6 + 0.4*np.sin(2*np.pi*f*tt)) * np.minimum(1, np.minimum(tt/0.003, (d-tt)/0.003))
def thud(f0=140, d=0.12):
    tt = np.arange(int(d*SR))/SR
    return np.sin(2*np.pi*(f0*np.exp(-tt*12))*tt) * np.exp(-tt*35)
def squeak(f=900, d=0.07):
    tt = np.arange(int(d*SR))/SR
    return np.sin(2*np.pi*(f + 500*tt/d)*tt) * np.sin(np.pi*tt/d) * 0.5
def click(d=0.03):
    tt = np.arange(int(d*SR))/SR
    return rng.standard_normal(len(tt)) * np.exp(-tt*250)
def load(p):
    with wave.open(p) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768; sr = w.getframerate()
    return np.interp(np.arange(int(len(a)*SR/sr))*sr/SR, np.arange(len(a)), a)
for k, f in enumerate(json.load(open('frames/S4/steps.json'))): add(squeak(850 + 60*(k % 2)), 5.0 + (f-1)/30, 0.35)
add(click(), 9.52, 0.9); add(thud(400, 0.05), 9.52, 0.5); add(tone(2050, 0.11), 9.56, 0.32)
for f in json.load(open('frames/S8/steps.json')): add(thud(), 15.0 + (f-1)/30, 0.6)
out = out / np.max(np.abs(out)) * 0.55
vt, vd = load('vo/tina.wav'), load('vo/doug.wav')
add(vt / np.abs(vt).max() * 0.85, 9.4 + 15/30)
add(vd / np.abs(vd).max() * 0.9, 11.6 + 15/30)
out = np.clip(out, -0.98, 0.98)
st = np.stack([out, out], 1)
with wave.open('ep1_audio_v2.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
print('audio ok')
