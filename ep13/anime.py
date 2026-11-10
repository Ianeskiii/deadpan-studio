"""Original 2D 'anime' for the TV: two invented characters (Kaito: spiky navy hair, red scarf; Shiro: long silver hair, dark coat),
close-ups that cut with each line, speed lines + shake as it escalates, then a frozen silent stare. English subtitles burned in."""
import json, math, os, sys, random
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, SS = 960, 540, 2
T = json.load(open('vo/timing.json')); L = T['lines']
FPS = 30; NF = int(round(T['black'] * FPS))
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30 * SS)
os.makedirs('tv', exist_ok=True)
rng = random.Random(3)
# per-frame mouth envelope for each line
ENV = {}
for l in L:
    a, sr = sf.read(f"vo/l{l['i']:02d}.wav"); hop = sr // FPS
    r = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)]); r = r / (r.max() + 1e-9)
    f0 = int(round(l['t'] * FPS))
    for k, v in enumerate(r): ENV[f0 + k] = max(ENV.get(f0 + k, 0), min(1, max(0, (v - 0.08) / 0.5)))
def line_at(f):
    t = f / FPS; cur = None
    for l in L:
        if l['t'] - 0.1 <= t: cur = l
    return cur
def P(pts, ox, oy, s, flip=False):
    return [((-x if flip else x) * s * SS + ox * SS, y * s * SS + oy * SS) for x, y in pts]
def EL(d, pts, **kw):
    (x0, y0), (x1, y1) = pts; d.ellipse([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], **kw)
def grad(img, top, bot):
    d = ImageDraw.Draw(img); h = img.size[1]
    for y in range(h):
        t = y / h; d.line([(0, y), (img.size[0], y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bot)))
def speed_lines(img, cx, cy, n, col, seed):
    d = ImageDraw.Draw(img); r_ = random.Random(seed); w, h = img.size
    for i in range(n):
        a = r_.uniform(0, 2 * math.pi); r0 = r_.uniform(0.32, 0.45) * w; r1 = 1.2 * w
        wd = r_.uniform(0.004, 0.012)
        p = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a - wd), cy + r1 * math.sin(a - wd)), (cx + r1 * math.cos(a + wd), cy + r1 * math.sin(a + wd))]
        d.polygon(p, fill=col)
def face(img, who, mouth, blink, ox, oy, s, intense):
    d = ImageDraw.Draw(img)
    hero = who == 'H'; fl = not hero            # hero turned slightly to his left (screen right), rival mirrored
    skin, shade = ((246, 214, 186), (222, 180, 152)) if hero else ((250, 232, 226), (226, 200, 204))
    hair = (34, 42, 92) if hero else (226, 228, 240); hair_s = (20, 24, 60) if hero else (180, 182, 205)
    iris = (226, 150, 40) if hero else (150, 92, 214)
    # shoulders / clothes
    d.polygon(P([(-2.2, 3.4), (-1.0, 1.55), (1.0, 1.55), (2.2, 3.4)], ox, oy, s, fl), fill=(60, 64, 80) if hero else (36, 30, 52))
    if hero:   # red scarf
        d.polygon(P([(-1.05, 1.5), (1.05, 1.5), (1.25, 2.05), (-1.25, 2.05)], ox, oy, s, fl), fill=(206, 44, 52))
        d.polygon(P([(0.75, 1.9), (1.35, 1.95), (1.7, 3.3), (1.15, 3.2)], ox, oy, s, fl), fill=(176, 30, 40))
    else:      # high coat collar
        d.polygon(P([(-1.2, 1.2), (-0.55, 1.65), (0, 2.6), (-1.6, 2.4)], ox, oy, s, fl), fill=(58, 46, 84))
        d.polygon(P([(1.2, 1.2), (0.55, 1.65), (0, 2.6), (1.6, 2.4)], ox, oy, s, fl), fill=(70, 56, 100))
    # back hair
    if hero:
        d.polygon(P([(-1.25, -0.4), (-1.35, 0.6), (-0.9, 0.2), (0.9, 0.2), (1.35, 0.6), (1.25, -0.4)], ox, oy, s, fl), fill=hair_s)
    else:
        d.polygon(P([(-1.3, -0.6), (-1.55, 2.6), (-0.8, 2.2), (0.8, 2.2), (1.55, 2.6), (1.3, -0.6)], ox, oy, s, fl), fill=hair_s)
    # neck + face
    d.polygon(P([(-0.32, 0.9), (0.32, 0.9), (0.38, 1.6), (-0.38, 1.6)], ox, oy, s, fl), fill=shade)
    jaw = [(-1.0, -0.6), (-1.02, 0.25), (-0.72, 0.9), (-0.12, 1.32), (0.18, 1.3), (0.78, 0.82), (1.0, 0.2), (1.0, -0.6)]
    d.polygon(P(jaw, ox, oy, s, fl), fill=skin)
    d.polygon(P([(0.55, -0.3), (1.0, -0.55), (1.0, 0.2), (0.78, 0.82), (0.45, 1.05)], ox, oy, s, fl), fill=shade)
    # eyes (big anime eyes), angled brows
    for side in (-1, 1):
        cx_ = 0.45 * side + 0.06; cy_ = 0.02
        ew, eh = 0.33, 0.24 * (1 - blink)
        if eh > 0.02:
            EL(d, P([(cx_ - ew, cy_ - eh), (cx_ + ew, cy_ + eh)], ox, oy, s, fl), fill=(255, 255, 255))
            ir = 0.17; icx = cx_ + 0.03
            box_ = P([(icx - ir, cy_ - min(eh, 0.2)), (icx + ir, cy_ + min(eh, 0.2) + 0.02)], ox, oy, s, fl)
            d.ellipse([min(box_[0][0], box_[1][0]), box_[0][1], max(box_[0][0], box_[1][0]), box_[1][1]], fill=iris)
            pb = P([(icx - 0.08, cy_ - 0.09), (icx + 0.08, cy_ + 0.1)], ox, oy, s, fl)
            d.ellipse([min(pb[0][0], pb[1][0]), pb[0][1], max(pb[0][0], pb[1][0]), pb[1][1]], fill=(20, 14, 20))
            hb = P([(icx - 0.11, cy_ - 0.13), (icx - 0.03, cy_ - 0.05)], ox, oy, s, fl)
            d.ellipse([min(hb[0][0], hb[1][0]), hb[0][1], max(hb[0][0], hb[1][0]), hb[1][1]], fill=(255, 255, 255))
        # upper lash line (angry tilt)
        tilt = 0.1 + 0.06 * intense
        d.line(P([(cx_ - ew * side, cy_ - eh - 0.02 + tilt * (side < 0)), (cx_ + ew * side, cy_ - eh - 0.02 + tilt * (side > 0))], ox, oy, s, fl), fill=(30, 20, 26), width=int(0.07 * s * SS))
        bt = 0.16 + 0.08 * intense
        d.line(P([(cx_ - 0.36 * side, cy_ - 0.42 - bt * 0.3), (cx_ + 0.3 * side, cy_ - 0.3 + bt * 0.6 * (1 if side > 0 else -1) * 0)], ox, oy, s, fl), fill=hair_s, width=int(0.09 * s * SS))
    # nose + mouth
    d.line(P([(0.12, 0.42), (0.18, 0.55)], ox, oy, s, fl), fill=shade, width=int(0.04 * s * SS))
    mx, my = 0.06, 0.88
    if mouth > 0.06:
        mh = 0.08 + 0.3 * mouth; mw = 0.2 + 0.08 * mouth
        d.polygon(P([(mx - mw, my), (mx, my - 0.04), (mx + mw, my), (mx + mw * 0.6, my + mh), (mx - mw * 0.6, my + mh)], ox, oy, s, fl), fill=(110, 30, 40))
        d.polygon(P([(mx - mw * 0.5, my + mh * 0.7), (mx + mw * 0.5, my + mh * 0.7), (mx + mw * 0.4, my + mh), (mx - mw * 0.4, my + mh)], ox, oy, s, fl), fill=(214, 96, 110))
    else:
        d.line(P([(mx - 0.16, my + 0.02), (mx + 0.16, my - 0.01)], ox, oy, s, fl), fill=(120, 60, 60), width=int(0.04 * s * SS))
    # front hair
    if hero:
        spikes = [(-1.15, -0.35), (-1.45, -1.25), (-0.7, -0.85), (-0.85, -1.85), (-0.2, -1.05), (0.05, -2.0), (0.35, -1.0), (0.95, -1.75), (0.85, -0.8),
                  (1.5, -1.1), (1.15, -0.35), (0.9, -0.15), (0.6, -0.55), (0.35, -0.12), (0.05, -0.6), (-0.25, -0.1), (-0.55, -0.55), (-0.85, -0.1)]
    else:
        spikes = [(-1.25, -0.25), (-1.2, -1.15), (-0.4, -1.6), (0.5, -1.55), (1.25, -1.05), (1.3, -0.2), (1.1, 0.4), (0.85, -0.35), (0.55, 0.05),
                  (0.3, -0.45), (0.0, 0.1), (-0.35, -0.4), (-0.6, 0.15), (-0.9, -0.3), (-1.1, 0.55)]
    d.polygon(P(spikes, ox, oy, s, fl), fill=hair)
    if hero:
        d.polygon(P([(-1.08, -0.62), (1.08, -0.62), (1.1, -0.42), (-1.1, -0.42)], ox, oy, s, fl), fill=(206, 44, 52))   # headband
def two_shot(img, f, still):
    d = ImageDraw.Draw(img); w, h = img.size
    grad(img, (255, 160, 90), (120, 50, 120))
    d.ellipse([w * 0.38, h * 0.18, w * 0.62, h * 0.18 + w * 0.24], fill=(255, 220, 150))       # sun
    d.polygon([(0, h * 0.72), (w * 0.3, h * 0.66), (w * 0.7, h * 0.68), (w, h * 0.63), (w, h), (0, h)], fill=(50, 26, 50))
    for k, (x, col, hair_c, hero) in enumerate([(0.28, (40, 30, 60), (34, 42, 92), True), (0.72, (30, 24, 44), (226, 228, 240), False)]):
        cx = w * x; base = h * 0.7; sc = h * 0.0032 * SS / SS
        bob = 0 if still else 2 * math.sin(f / 7 + k)
        d.rectangle([cx - 22 * sc * 10 / 10, base - 150 * sc * 10 / 10 + bob, cx + 22 * sc, base], fill=col)
        d.ellipse([cx - 24 * sc, base - 200 * sc + bob, cx + 24 * sc, base - 148 * sc + bob], fill=(246, 214, 186) if hero else (250, 232, 226))
        if hero:
            d.polygon([(cx - 28 * sc, base - 180 * sc), (cx - 10 * sc, base - 230 * sc), (cx, base - 195 * sc), (cx + 14 * sc, base - 232 * sc), (cx + 30 * sc, base - 182 * sc)], fill=hair_c)
            d.polygon([(cx + 18 * sc, base - 140 * sc), (cx + 70 * sc, base - 130 * sc + 6 * math.sin(f / 5)), (cx + 20 * sc, base - 125 * sc)], fill=(206, 44, 52))
        else:
            d.polygon([(cx - 28 * sc, base - 182 * sc), (cx, base - 210 * sc), (cx + 28 * sc, base - 182 * sc), (cx + 26 * sc, base - 100 * sc), (cx - 26 * sc, base - 100 * sc)], fill=hair_c)
            d.ellipse([cx - 24 * sc, base - 196 * sc, cx + 24 * sc, base - 150 * sc], fill=(250, 232, 226))
def subtitle(img, text):
    d = ImageDraw.Draw(img); w, h = img.size
    tw = d.textlength(text, font=FONT)
    d.text(((w - tw) / 2, h - 70 * SS), text, font=FONT, fill=(255, 255, 255), stroke_width=4 * SS, stroke_fill=(0, 0, 0))
SUB = {}                                   # frame -> subtitle text (exactly while each line is on)
for i, l in enumerate(L):
    a = int(round(l['t'] * FPS)); b = int(round((l['t'] + l['d']) * FPS))
    nxt = int(round(L[i + 1]['t'] * FPS)) if i + 1 < len(L) else b
    hold = min(nxt, b + (8 if i < 4 else 2))
    for f in range(a, hold): SUB[f] = l['sub']
json.dump({str(k): v for k, v in SUB.items()}, open('vo/subs_by_frame.json', 'w'), ensure_ascii=False)
OWNER = {}                                 # picture cuts exactly when the subtitle changes
for i, l in enumerate(L):
    a = int(round(l['t'] * FPS)); nxt = int(round(L[i + 1]['t'] * FPS)) if i + 1 < len(L) else int(round(T['end_talk'] * FPS))
    for f in range(a, nxt): OWNER[f] = l
END_TALK = int(round(T['end_talk'] * FPS))
for f in range(1, NF + 1):
    img = Image.new('RGB', (W * SS, H * SS)); fi = f - 1
    l = OWNER.get(fi)
    if l is None or fi >= END_TALK:
        two_shot(img, fi, still=fi >= END_TALK)
    else:
        idx = l['i']; who = 'H' if l['spk'] == 'jm_kumo' else 'R'
        intense = 0 if idx < 4 else (1 if idx < 10 else 2)
        if who == 'H': grad(img, (250, 150, 80), (160, 60, 90))
        else: grad(img, (60, 70, 160), (20, 16, 50))
        if intense: speed_lines(img, W * SS * (0.35 if who == 'H' else 0.65), H * SS * 0.45, 60 + 50 * intense, (255, 255, 255) if who == 'H' else (180, 200, 255), seed=fi // (3 if intense == 1 else 2))
        shake = (0, 0) if intense == 0 else (rng.uniform(-1, 1) * 6 * intense, rng.uniform(-1, 1) * 4 * intense)
        ox = W * (0.42 if who == 'H' else 0.58) + shake[0]; oy = H * 0.5 + shake[1]
        zoom = 1.0 + 0.02 * intense * ((fi - int(l['t'] * FPS)) / 10)
        blink = 1.0 if (fi % 97) in (0, 1) and intense == 0 else 0.0
        face(img, who, ENV.get(fi, 0.0), blink, ox, oy, 118 * zoom, intense)
        if intense == 2 and fi - int(l['t'] * FPS) < 2:     # impact flash on every cut in the final barrage
            img = Image.blend(img, Image.new('RGB', img.size, (255, 255, 255)), 0.55)
    if fi in SUB: subtitle(img, SUB[fi])
    img = img.resize((W, H), Image.LANCZOS)
    img.save(f'tv/tv_{f:04d}.png')
print('frames', NF)
