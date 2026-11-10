"""Shared helpers for sticky episode scenes. An episode's scenes.py starts with `from core import *`."""
import json, math, os, random
from lib import *
from lib import _arm

# Run from the episode folder (channels/sticky/episodes/<id>); timeline.json is made by timeline.py.
D = os.getcwd()
TL = json.load(open(os.path.join(D, 'timeline.json')))
LINES = TL['lines']
def lt0(i): return LINES[i]['t0']
def lt1(i): return LINES[i]['t1']
def wt(i, word, n=0):
    k = 0
    for w in LINES[i]['words']:
        if w['w'].lower().strip(',.?!:\'"“”').startswith(word):
            if k == n: return w['t0']
            k += 1
    raise KeyError(word)
def ck(i, j): return LINES[i]['chunks'][j][0]

SS = 1.5
_cache = {}
def cached(key, fn, w=W, h=H):
    if key not in _cache:
        surf = skia.Surface(int(w * SS), int(h * SS)); c = surf.getCanvas(); c.scale(SS, SS); fn(c)
        _cache[key] = surf.makeImageSnapshot()
    return _cache[key]
def blit(cv, img, r=None): cv.drawImageRect(img, r or skia.Rect(0, 0, W, H), skia.SamplingOptions(skia.FilterMode.kLinear))
def pop(T, t0, d=0.25): return back(clamp((T - t0) / d)) if T >= t0 else 0
def tag(cv, s, x, y, col, size=50, fg=C('#ffffff'), rot=0, k=1.0):
    if k <= 0: return
    f = skia.Font(skia.Typeface('Poppins', skia.FontStyle.Bold()), size); w = f.measureText(s)
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(k, k)
    r = skia.Rect(-w / 2 - 30, -size * 0.95, w / 2 + 30, size * 0.55)
    cv.drawRoundRect(r, size * 0.75, size * 0.75, fillp(col)); cv.drawRoundRect(r, size * 0.75, size * 0.75, strokep(INK, 6))
    cv.drawString(s, -w / 2, 0, f, fillp(fg)); cv.restore()
def full(cv, col): cv.drawRect(skia.Rect(-3000, -3000, 5000, 5000), fillp(col))
def dark_bg(cv, a=C('#1a1c26'), b=C('#07080c')):
    cv.drawRect(skia.Rect(0, 0, W, H), fillp(shader=rad((540, 900), 1100, [a, b])))
def bubble_txt(cv, x, y, lines, size=56, tail=(0, 0), k=1.0):
    if k <= 0: return
    f = skia.Font(skia.Typeface('Poppins', skia.FontStyle.Bold()), size)
    w = max(f.measureText(l) for l in lines); h = size * 1.25 * len(lines)
    cv.save(); cv.translate(x, y); cv.scale(k, k)
    r = skia.Rect(-w / 2 - 40, -h / 2 - 30, w / 2 + 40, h / 2 + 20)
    t = skia.Path(); t.moveTo(-30, r.bottom() - 4); t.lineTo(tail[0], tail[1]); t.lineTo(20, r.bottom() - 4); t.close()
    cv.drawPath(t, fillp(C('#ffffff'))); cv.drawPath(t, strokep(INK, 6))
    cv.drawRoundRect(r, 40, 40, fillp(C('#ffffff'))); cv.drawRoundRect(r, 40, 40, strokep(INK, 6))
    cv.drawRect(skia.Rect(-26, r.bottom() - 12, 16, r.bottom() + 2), fillp(C('#ffffff')))
    for i, l in enumerate(lines): cv.drawString(l, -f.measureText(l) / 2, -h / 2 + size * 1.05 + i * size * 1.25, f, fillp(INK))
    cv.restore()
def night(cv, T, seed=1):
    cv.drawRect(skia.Rect(0, 0, W, H), fillp(shader=lin((0, 0), (0, H), [C('#03050f'), C('#141c3a')])))
    rnd = random.Random(seed)
    for i in range(90): cv.drawCircle(rnd.uniform(0, W), rnd.uniform(0, 1300), rnd.uniform(1, 2.5), fillp(C('#ffffff'), alpha=rnd.uniform(0.3, 0.9)))
    cv.drawCircle(860, 300, 60, fillp(C('#eef1ff'), alpha=0.85))

def cam_lerp(a, b, f): return tuple(lerp(x, y, ease(f)) for x, y in zip(a, b))


RED = C('#e2483b'); CREAM = C('#f4efe2'); GOLD = C('#e8b84a'); TEAL = C('#7ad7ff'); GREEN = C('#3fbf6b')
def fadek(T, t1, d=0.25): return 1 - clamp((T - t1) / d)
def spot(cv, x, y, r=520, a=0.35, col=C('#fff2c8')): cv.drawCircle(x, y, r, fillp(col, alpha=a, blur=r * 0.35))
def bracket(cv, x, y, w, h, k=1.0, col=C('#7cf29a'), label=None):
    if k <= 0: return
    w *= lerp(1.6, 1, k); h *= lerp(1.6, 1, k); L = 36
    p = strokep(col, 8, alpha=min(1, k * 1.3))
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = x + sx * w / 2, y + sy * h / 2
            cv.drawLine(cx, cy, cx - sx * L, cy, p); cv.drawLine(cx, cy, cx, cy - sy * L, p)
    if label and k > 0.6:
        f = skia.Font(skia.Typeface('Courier New', skia.FontStyle.Bold()), 34); tw = f.measureText(label)
        cv.drawRect(skia.Rect(x - w / 2, y - h / 2 - 54, x - w / 2 + tw + 24, y - h / 2 - 8), fillp(col))
        cv.drawString(label, x - w / 2 + 12, y - h / 2 - 20, f, fillp(INK))
def check(cv, x, y, k=1.0, col=GREEN, s=1.0):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.scale(k * s, k * s)
    cv.drawCircle(0, 0, 40, fillp(col)); cv.drawCircle(0, 0, 40, strokep(INK, 5))
    cv.drawPath(poly([(-18, 0), (-5, 15), (20, -15)], close=False), strokep(C('#ffffff'), 9)); cv.restore()
def evo_sil(cv, x, y, u, T, **kw):
    silhouette(cv, lambda: character(cv, 'evo', x, y, u, t=T, **kw))
def sleeper(cv, T, x=240, y=1500, u=70):
    silhouette(cv, lambda: lying(cv, 'evo', x, y, u, T, expr='neutral'))


def money(T, t0, t1, v0, v1): return lerp(v0, v1, ease(clamp((T - t0) / max(0.01, t1 - t0))))

# ---- per-act colour grade + film grain + vignette (call from the episode's overlay) ----
_GRAIN = []
def _grain():
    if not _GRAIN:
        rng = random.Random(11)
        for k in range(6):
            s = skia.Surface(540, 960); c = s.getCanvas()
            for i in range(2600):
                v = rng.random(); c.drawRect(skia.Rect.MakeXYWH(rng.uniform(0, 540), rng.uniform(0, 960), 1.4, 1.4), fillp(C('#ffffff') if v > 0.5 else C('#000000'), alpha=0.18))
            _GRAIN.append(s.makeImageSnapshot())
    return _GRAIN
def grade(cv, T, ACTS):
    """ACTS = [(start_seconds, tint_colour, strength), ...]. The last act should match the first so the loop is seamless."""
    i = max(k for k, a in enumerate(ACTS) if a[0] <= T)
    col, a = ACTS[i][1], ACTS[i][2]
    if i > 0:
        f = clamp((T - ACTS[i][0]) / 0.5)
        col = mix(ACTS[i - 1][1], col, f); a = lerp(ACTS[i - 1][2], a, f)
    p = fillp(col, alpha=a); p.setBlendMode(skia.BlendMode.kSoftLight)
    cv.drawRect(skia.Rect(0, 0, W, H), p)
    vignette(cv, 0.42)
    cv.drawImageRect(_grain()[int(T * 12) % 6], skia.Rect(0, 0, W, H), skia.SamplingOptions())
