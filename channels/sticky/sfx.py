"""Music bed, sound effects and the final mix for sticky episodes (pure numpy, no samples).

An episode's audio.py looks like:

    from sfx import *
    begin()                                    # reads timeline.json, voice.wav and the episode's scenes()
    music_bed(calm=[(lt0(10), lt0(11))], bright=[(lt0(7), lt0(8))])
    transition_sfx()                           # whoosh / thud on each scene transition
    thud(wt(0, 'penny') - 0.05, 0.5)           # ...story beats, timed with wt()/lt0()
    finish()                                   # ducks the music under the voice, writes mix.wav

Run it from the episode folder:  python3 audio.py
"""
import json, os, sys
import numpy as np, soundfile as sf

sys.path.insert(0, os.getcwd()); sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))
SR = 44100
rng = np.random.default_rng(1)
TL = json.load(open('timeline.json'))
LINES = TL['lines']
total = TL['total']
N = int(total * SR) + SR
mus = np.zeros(N); sfx = np.zeros(N)
SC = []

def lt0(i): return LINES[i]['t0']
def lt1(i): return LINES[i]['t1']
def wt(i, word, n=0):
    k = 0
    for w in LINES[i]['words']:
        if w['w'].lower().strip(',.?!:\'"“”').startswith(word):
            if k == n: return w['t0']
            k += 1
    raise KeyError(word)

def begin():
    global SC
    import scenes
    SC = scenes.scenes()
    return SC

def add(buf, t, x):
    i = max(0, int(t * SR)); j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[:j - i]
mid = lambda m: 440 * 2 ** ((m - 69) / 12)
def noise(d): return rng.standard_normal(int(d * SR))
def note(f, d, amp=0.2, dec=6):
    t = np.arange(int(d * SR)) / SR
    return amp * np.exp(-dec * t) * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-12 * t) + 0.12 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-20 * t))
def pad(f, d, amp=0.05):
    t = np.arange(int(d * SR)) / SR; env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.6)
    return amp * env * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.003 * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t))

# ---------------- music bed ----------------
MINOR = [(40, [52, 55, 59]), (36, [52, 55, 60]), (38, [50, 54, 57]), (35, [51, 54, 59])]      # tense (Kara, Howells, Ingram)
NOIR = [(45, [57, 60, 64]), (41, [57, 60, 65]), (38, [57, 62, 65]), (40, [56, 59, 64])]       # spy noir (Virginia Hall)
def music_bed(prog=MINOR, bpm=100, calm=(), bright=(), hero=(), light_notes=(64, 67, 71, 76)):
    """Pulsing bass + pads + brushed hats. calm/bright = lighter sections, hero = big major pads. Each is a list of (t0, t1)."""
    beat = 60 / bpm; t = 0; k = 0
    inside = lambda rs: any(a <= t < b for a, b in rs)
    while t < total:
        root, ch = prog[(k // 8) % len(prog)]
        if inside(hero):
            if k % 8 == 0:
                for m in (48, 55, 60, 64, 67): add(mus, t, pad(mid(m), beat * 4.2, 0.035))
            if k % 2 == 0: add(mus, t, note(mid([72, 76, 79, 84][(k // 2) % 4]), 0.5, 0.04, 5))
        elif inside(calm) or inside(bright):
            if k % 2 == 0: add(mus, t, note(mid(light_notes[(k // 2) % len(light_notes)]), 0.5, 0.05, 5))
            if k % 8 == 0:
                for m in (48, 55, 64): add(mus, t, pad(mid(m), beat * 4.2, 0.03))
        else:
            if k % 2 == 0: add(mus, t, note(mid(root), 0.45, 0.2, 6))
            if k % 8 == 0:
                for m in ch: add(mus, t, pad(mid(m), beat * 4.1, 0.022))
            if k % 4 == 2: add(mus, t, note(mid(ch[(k // 4) % 3] + 12), 0.3, 0.035, 9))
            x = noise(0.04); x = x - np.convolve(x, np.ones(4) / 4, 'same'); add(mus, t, 0.025 * x * np.exp(-np.arange(len(x)) / SR * 80))
            if k % 4 == 0: tt = np.arange(int(0.25 * SR)) / SR; add(mus, t, 0.18 * np.sin(2 * np.pi * 55 * tt) * np.exp(-18 * tt))
        t += beat / 2; k += 1

def transition_sfx():
    for s_ in SC[1:]:
        tr = s_[4] if len(s_) > 4 else 'fade'
        if tr in ('whip', 'zoom', 'wipe'): whoosh(s_[0] + 0.12, 0.32, 0.07)
        elif tr == 'flash': thud(s_[0], 0.25)

# ---------------- effects ----------------
def whoosh(t, d=0.3, a=0.06):
    x = noise(d); env = np.sin(np.linspace(0, np.pi, len(x))) ** 2
    x = np.convolve(x, np.ones(30) / 30, 'same'); add(sfx, t - d / 2, a * x * env * 3)
def thud(t, a=0.5):
    tt = np.arange(int(0.35 * SR)) / SR; add(sfx, t, a * np.sin(2 * np.pi * 70 * tt) * np.exp(-14 * tt) + 0.15 * np.convolve(noise(0.35), np.ones(60) / 60, 'same') * np.exp(-20 * tt))
def tick(t, a=0.15):
    tt = np.arange(int(0.03 * SR)) / SR; add(sfx, t, a * np.sin(2 * np.pi * 2400 * tt) * np.exp(-150 * tt))
def type_(t, a=0.12):
    x = noise(0.03) * np.exp(-np.arange(int(0.03 * SR)) / SR * 200); add(sfx, t, a * x)
def beep(t, f=800, d=0.08, a=0.07):
    tt = np.arange(int(d * SR)) / SR; env = np.minimum(1, np.minimum(tt, d - tt) / 0.005); add(sfx, t, a * env * np.sin(2 * np.pi * f * tt))
def pop(t, a=0.35):
    tt = np.arange(int(0.12 * SR)) / SR; f = 500 + 900 * tt / 0.12
    add(sfx, t, a * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-30 * tt))
def gulp(t, a=0.35):
    tt = np.arange(int(0.18 * SR)) / SR; f = 300 - 200 * tt / 0.18; add(sfx, t, a * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-12 * tt))
def step(t, a=0.12, low=False):
    tt = np.arange(int(0.09 * SR)) / SR; x = np.convolve(noise(0.09), np.ones(25) / 25, 'same') * 4
    add(sfx, t, a * (x * np.exp(-40 * tt) + 0.6 * np.sin(2 * np.pi * (90 if low else 130) * tt) * np.exp(-30 * tt)))
def limp_steps(t0, t1, a=0.1, per=0.62):
    t = t0; i = 0
    while t < t1: step(t, a, low=i % 2 == 0); t += per * (0.38 if i % 2 == 0 else 0.62); i += 1
def wind(t0, d, a=0.05):
    x = np.convolve(noise(d), np.ones(120) / 120, 'same') * 9; tt = np.arange(len(x)) / SR
    env = np.minimum(1, np.minimum(tt, d - tt) / 0.4); add(sfx, t0, a * x * env * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * tt)))
def boom(t, a=0.7, d=1.6):
    tt = np.arange(int(d * SR)) / SR; x = np.convolve(noise(d), np.ones(80) / 80, 'same') * 6
    add(sfx, t, a * (x * np.exp(-3 * tt) + np.sin(2 * np.pi * 45 * tt) * np.exp(-4 * tt)))
def bang(t, a=0.6):
    tt = np.arange(int(0.5 * SR)) / SR; add(sfx, t, a * (noise(0.5) * np.exp(-25 * tt) * 0.6 + np.sin(2 * np.pi * 80 * tt) * np.exp(-12 * tt)))
def knock(t, a=0.35):
    for i in range(3):
        tt = np.arange(int(0.08 * SR)) / SR; add(sfx, t + i * 0.16, a * np.sin(2 * np.pi * 180 * tt) * np.exp(-50 * tt))
def chime(t, a=0.1):
    for i, m in enumerate([79, 84, 88, 91]): add(sfx, t + i * 0.07, note(mid(m), 1.0, a, 4))
def waves_(t0, d, a=0.03):
    x = np.convolve(noise(d), np.ones(200) / 200, 'same') * 12; tt = np.arange(len(x)) / SR; add(sfx, t0, a * x * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * tt)))
def heart(t, a=0.35):
    for d in (0, 0.18):
        tt = np.arange(int(0.15 * SR)) / SR; add(sfx, t + d, a * (1 if d == 0 else 0.7) * np.sin(2 * np.pi * 55 * tt) * np.exp(-25 * tt))
def clink(t, a=0.15):
    for f in (2200, 3300): tt = np.arange(int(0.2 * SR)) / SR; add(sfx, t, a * np.sin(2 * np.pi * f * tt) * np.exp(-30 * tt) / 2)
def siren(t, d=2.0, a=0.05):
    tt = np.arange(int(d * SR)) / SR; f = 650 + 250 * np.sin(2 * np.pi * 1.5 * tt); add(sfx, t, a * np.sin(2 * np.pi * np.cumsum(f) / SR))
def engine(t0, d, a=0.05):
    tt = np.arange(int(d * SR)) / SR; add(sfx, t0, a * np.sin(2 * np.pi * (60 + 20 * np.sin(2 * np.pi * 0.3 * tt)) * tt) * np.minimum(1, np.minimum(tt, d - tt) / 0.3))
def birds(t0, d, a=0.03):
    t = t0
    while t < t0 + d:
        tt = np.arange(int(0.12 * SR)) / SR; add(sfx, t, a * np.sin(2 * np.pi * (3000 + 800 * np.sin(2 * np.pi * 20 * tt)) * tt) * np.exp(-20 * tt)); t += 0.35 + 0.3 * rng.random()
def cash(t, a=0.12):
    for i, m in enumerate([88, 91, 96]): add(sfx, t + i * 0.05, note(mid(m), 0.4, a, 10))
def coinclink(t, a=0.08):
    tt = np.arange(int(0.15 * SR)) / SR; add(sfx, t, a * (np.sin(2 * np.pi * 3100 * tt) + np.sin(2 * np.pi * 4700 * tt)) * np.exp(-28 * tt))
def rustle(t, d=0.6, a=0.06):
    x = noise(d); x = x - np.convolve(x, np.ones(6) / 6, 'same'); add(sfx, t, a * x * np.sin(np.linspace(0, np.pi, len(x))))
def cough(t, a=0.35):
    for d, amp in ((0, 1.0), (0.16, 0.7)):
        x = noise(0.14); x = np.convolve(x, np.ones(8) / 8, 'same') * 3; tt = np.arange(len(x)) / SR
        add(sfx, t + d, a * amp * x * np.exp(-18 * tt) * (1 + 0.5 * np.sin(2 * np.pi * 140 * tt)))
def applause(t0, d, a=0.06):
    x = noise(d); x = x - np.convolve(x, np.ones(3) / 3, 'same'); tt = np.arange(len(x)) / SR
    add(sfx, t0, a * x * np.minimum(1, np.minimum(tt, d - tt) / 0.3) * (0.7 + 0.3 * rng.random(len(x))))
def sting(t, a=0.12, up=True):
    for i, m in enumerate([57, 60, 64, 69] if up else [57, 56, 53, 50]): add(sfx, t + i * 0.04, note(mid(m), 1.2, a, 2.5))
def hiss(t, d=1.0, a=0.08):
    x = noise(d); x = x - np.convolve(x, np.ones(3) / 3, 'same'); add(sfx, t, a * x * np.sin(np.linspace(0, np.pi, len(x))))
def clang(t, a=0.3):
    for f in (220, 330, 523): tt = np.arange(int(0.9 * SR)) / SR; add(sfx, t, a * np.sin(2 * np.pi * f * tt) * np.exp(-4 * tt) / 3)
def crowd(t0, d, a=0.05):
    x = np.convolve(noise(d), np.ones(40) / 40, 'same') * 5; tt = np.arange(len(x)) / SR; add(sfx, t0, a * x * (0.6 + 0.4 * np.sin(2 * np.pi * 1.3 * tt)))
def hum(t0, d, a=0.03):
    tt = np.arange(int(d * SR)) / SR; add(sfx, t0, a * np.sin(2 * np.pi * 120 * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * tt)))

# ---------------- mix ----------------
def finish(out='mix.wav', music=0.5, effects=0.8):
    v, vsr = sf.read('voice.wav')
    if v.ndim > 1: v = v.mean(1)
    vi = np.interp(np.arange(int(len(v) * SR / vsr)) / SR, np.arange(len(v)) / vsr, v)
    voice = np.zeros(N); voice[:min(N, len(vi))] = vi[:N]
    env = np.abs(voice); win = int(0.15 * SR); env = np.convolve(env, np.ones(win) / win, 'same'); duck = 1 - 0.45 * np.clip(env / 0.03, 0, 1)
    m = voice * 1.0 + mus * music * duck + sfx * effects
    m = m[:int(total * SR)]
    fade = int(0.03 * SR); m[-fade:] *= np.linspace(1, 0, fade)
    m /= max(1, np.abs(m).max() / 0.95)
    sf.write(out, m, SR)
    print('mix ok', out)
