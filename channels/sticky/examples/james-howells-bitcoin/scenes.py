"""Example episode as delivered in the original session (james-howells-bitcoin). Shots, ACTS grade and scenes() list.
Run from this folder: python3 ../../render.py still 1.0 ..."""
from core import *
from lib import _arm


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

def money(T, t0, t1, v0, v1):
    return lerp(v0, v1, ease(clamp((T - t0) / max(0.01, t1 - t0))))
def fmt_usd(v):
    if v >= 1e6: return f'${v / 1e6:,.0f} MILLION'
    if v >= 1e3: return f'${v:,.0f}'
    return f'${v:,.2f}'

def shot_hook(cv, T, frozen=False):
    t = 0 if frozen else T
    landfill(cv, t, night=False)
    cv.drawRect(skia.Rect(-300, 1500, W + 300, H + 300), fillp(C('#4a4438')))
    for i in range(6):
        gx = 100 + i * 180; cv.drawLine(gx, 1500, gx, 1380, strokep(C('#5a5f6a'), 8))
    cv.drawLine(-300, 1400, W + 300, 1400, strokep(C('#7a7f8a'), 4)); cv.drawLine(-300, 1450, W + 300, 1450, strokep(C('#7a7f8a'), 4))
    cv.drawCircle(560, 1180, 70, fillp(BTC_GOLD, alpha=0.35 + 0.15 * math.sin(t * 3), blur=30))
    if frozen: return
    tag(cv, 'A MOUNTAIN OF TRASH', 540, 300, C('#5a4a40'), 54, k=pop(T, wt(0, 'mountain') - 0.2))
    tag(cv, 'WALES', 540, 420, CREAM, 50, INK, k=pop(T, wt(0, 'wales') - 0.15))

def shot_inside(cv, T, frozen=False):
    t = T
    section(cv, t, depth_glow=1.0, dark=0.35, scan=1.0)
    landfill_top = [(-300, 640), (100, 520), (400, 470), (700, 500), (1000, 560), (1380, 640)]
    cv.drawPath(poly(landfill_top + [(1380, 660), (-300, 660)]), fillp(C('#6a5a4c')))
    for i in range(3): bx = 200 + i * 300 + math.sin(t * 2 + i) * 30; cv.drawPath(poly([(bx - 26, 300 + i * 40), (bx, 310 + i * 40), (bx + 26, 300 + i * 40)], close=False), strokep(INK, 5))
    k = pop(T, wt(0, '800') - 0.2, 0.3)
    if k > 0:
        cv.save(); cv.translate(540, 330); cv.scale(k, k)
        cv.drawRoundRect(skia.Rect(-400, -100, 400, 80), 30, 30, fillp(BTC_GOLD)); cv.drawRoundRect(skia.Rect(-400, -100, 400, 80), 30, 30, strokep(INK, 8))
        text(cv, '$800 MILLION', 0, 20, 96, INK); cv.restore()
    bracket(cv, 560, 1420, 220, 180, k=clamp((T - 3.2) / 0.3), col=BTC_GOLD, label='HARD DRIVE')

def shot_fence(cv, T):
    landfill(cv, T)
    cv.drawRect(skia.Rect(-300, 1350, W + 300, H + 300), fillp(C('#5a5a50')))
    for i in range(-1, 14): cv.drawLine(i * 90, 1000, i * 90, 1500, strokep(C('#5a5f6a'), 8))
    for j in range(8): cv.drawLine(-300, 1000 + j * 70, W + 300, 1000 + j * 70, strokep(C('#7a7f8a'), 3))
    for i in range(-2, 30): cv.drawLine(i * 50, 1000, i * 50 + 500, 1500, strokep(C('#8a8f9a'), 2, alpha=0.6)); cv.drawLine(i * 50 + 500, 1000, i * 50, 1500, strokep(C('#8a8f9a'), 2, alpha=0.6))
    cv.save(); cv.translate(760, 1150); cv.rotate(-3)
    cv.drawRect(skia.Rect(-170, -90, 170, 90), fillp(C('#c8281e'))); cv.drawRect(skia.Rect(-170, -90, 170, 90), strokep(INK, 6)); text(cv, 'NO ENTRY', 0, 20, 62, CREAM); cv.restore()
    character(cv, 'james', 360, 1760, 110, t=T, expr='sad', pose={'hl': (0.1, -0.9), 'hr': (0.3, -0.85)}, look=(0.2, -0.6))
    tag(cv, 'NOT ALLOWED TO DIG', 540, 300, RED, 56, k=pop(T, wt(0, 'allowed') - 0.2))

def shot_name(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (W, H), [C('#2a3a6a'), C('#0e1428')])))
    for i in range(14): cv.drawLine(-300, i * 160 - (T * 40 % 160), W + 300, i * 160 + 300 - (T * 40 % 160), strokep(C('#30447a'), 30, alpha=0.4))
    spot(cv, 540, 980, 520, 0.25)
    character(cv, 'james', 540, 1700, 135, t=T, expr='smile', look=(0.1, -0.1))
    k = pop(T, wt(1, 'james') - 0.2, 0.35)
    if k > 0:
        cv.save(); cv.translate(540, 360); cv.scale(k, k)
        cv.drawRect(skia.Rect(-430, -110, 430, 110), fillp(CREAM)); cv.drawRect(skia.Rect(-430, -110, 430, 110), strokep(INK, 7))
        cv.drawRect(skia.Rect(-430, -110, -400, 110), fillp(BTC_GOLD)); text(cv, 'JAMES HOWELLS', 15, 30, 84, INK); cv.restore()

def shot_wales(cv, T):
    p = uk_map(cv, T)
    map_pin(cv, p[0], p[1], pop(T, wt(1, 'newport') - 0.2))
    text(cv, 'NEWPORT', p[0] + 150, p[1] - 30, 44, CREAM, stroke=INK, sw=8)
    tag(cv, 'IT ENGINEER', 540, 300, C('#2a3a6a'), 58, k=pop(T, wt(1, 'it') - 0.15))

def shot_2009(cv, T):
    paper_bg(cv, C('#e8e2d4'))
    calendar(cv, 540, 560, 0.85, 'YEAR', '2009', C('#2a4a7a'), k=pop(T, wt(2, '2009') - 0.25, 0.3), rot=-3)
    for i, (x, nm) in enumerate(((200, 'driver'), (540, 'clerk'), (880, 'gf'))):
        character(cv, nm, x, 1760, 85, t=T, expr='meh', look=(0, -0.3), blink_seed=i)
        k = pop(T, wt(2, 'bitcoin') - 0.1 + i * 0.12)
        if k > 0: text(cv, '?', x + 60, 1200 + math.sin(T * 4 + i) * 10, 110 * k, BTC_GOLD, stroke=INK, sw=8)
    coin(cv, 540, 1000, 80, spin=T * 2, a=pop(T, wt(2, 'bitcoin') - 0.2))
    tag(cv, '"BIT-WHAT?"', 540, 300, CREAM, 52, INK, k=pop(T, wt(2, 'nobody') - 0.15))

def shot_mining(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#2a2a3a'), C('#14141c')])))
    table(cv, 540, 1300, 860, 140, 260, col=C('#5a3a28'))
    def scr(c, r):
        for i in range(6):
            y = r.top() + 30 + ((T * 120 + i * 50) % 300)
            c.drawRect(skia.Rect(r.left() + 30, y, r.left() + 30 + 60 + (i * 37) % 280, y + 18), fillp(C('#3fbf6b'), alpha=0.8))
    laptop(cv, 560, 1290, 1.0, 1.0, scr, T)
    character(cv, 'james', 220, 1560, 95, t=T, expr='happy', pose={'hr': (0.9, 0.2)}, look=(0.8, 0.2))
    for i in range(6):
        f = ((T * 0.9 + i / 6) % 1)
        coin(cv, 560 + math.sin(i * 2.1) * 260 * f, 900 - f * 500, 40, spin=T * 3 + i, a=1 - f)
    tag(cv, 'MINING ON A LAPTOP', 540, 300, GREEN, 54, k=pop(T, wt(2, 'mining') - 0.2))

def shot_8000(cv, T):
    dark_bg(cv, C('#3a2a14'), C('#0a0804'))
    n = int(money(T, 20.4, 22.9, 0, 8000))
    rnd = random.Random(2)
    cnt = int(n / 8000 * 90)
    for i in range(cnt):
        x = 540 + rnd.uniform(-1, 1) * (380 - i * 2.5); y = 1650 - (i ** 0.8) * 9
        coin(cv, x, y, 55, rot=rnd.uniform(-20, 20), spin=1.2)
    text(cv, f'{n:,}', 540, 500, 200, BTC_GOLD, stroke=INK, sw=14)
    text(cv, 'BITCOINS', 540, 620, 72, CREAM)
    tag(cv, 'IN JUST A FEW WEEKS', 540, 260, CREAM, 46, INK, k=pop(T, wt(3, 'few') - 0.15))

def shot_nothing(cv, T):
    paper_bg(cv, C('#e8e2d4'))
    cv.drawLine(540, 900, 540, 1500, strokep(INK, 16)); cv.drawPath(poly([(440, 1500), (640, 1500), (600, 1460), (480, 1460)]), fillp(C('#5a5a62')))
    tilt = math.sin(T * 2) * 3
    cv.save(); cv.rotate(tilt, 540, 900)
    cv.drawLine(220, 900, 860, 900, strokep(INK, 14))
    for x in (260, 820):
        cv.drawLine(x, 900, x - 80, 1080, strokep(INK, 5)); cv.drawLine(x, 900, x + 80, 1080, strokep(INK, 5))
        cv.drawArc(skia.Rect(x - 120, 1020, x + 120, 1140), 0, 180, False, strokep(INK, 10))
    coin(cv, 260, 1030, 60, spin=0.2)
    cv.save(); cv.translate(820, 1020); cv.rotate(-30); cv.drawOval(skia.Rect(-80, -16, 80, 16), fillp(C('#f4f4f0'))); cv.drawOval(skia.Rect(-80, -16, 80, 16), strokep(INK, 5)); cv.drawLine(-90, 0, 90, 0, strokep(INK, 4)); cv.restore()
    cv.restore()
    v = money(T, 24.4, 25.8, 1.0, 0.0008)
    text(cv, f'1 BTC = ${v:.4f}' if v < 0.1 else f'1 BTC = ${v:.2f}', 540, 600, 74, C('#2a3a6a'))
    tag(cv, 'WORTH ALMOST NOTHING', 540, 300, C('#8a8a8a'), 52, k=pop(T, wt(3, 'nothing') - 0.2))

def shot_stop(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#2a2a3a'), C('#14141c')])))
    table(cv, 540, 1300, 860, 140, 260, col=C('#5a3a28'))
    o = 1 - ease(clamp((T - 27.0) / 0.5))
    laptop(cv, 540, 1290, 1.1, o, None, T)
    tag(cv, 'HE STOPPED MINING', 540, 300, CREAM, 54, INK, k=pop(T, wt(4, 'stopped') - 0.2))

def shot_drive(cv, T):
    dark_bg(cv, C('#2a3040'), C('#0a0c12'))
    spot(cv, 540, 980, 500, 0.3)
    k = eout(clamp((T - 28.1) / 0.5))
    hdd(cv, 540, 1000, lerp(0.6, 1.6, k), rot=lerp(20, -4, k), glow=0.6)
    kk = pop(T, wt(4, 'wallet') - 0.15)
    if kk > 0:
        cv.save(); cv.translate(540, 560); cv.scale(kk, kk)
        cv.drawRoundRect(skia.Rect(-300, -80, 300, 80), 24, 24, fillp(C('#14141a'))); cv.drawRoundRect(skia.Rect(-300, -80, 300, 80), 24, 24, strokep(BTC_GOLD, 6))
        cv.drawCircle(-200, 0, 34, strokep(BTC_GOLD, 10)); cv.drawLine(-166, 0, -40, 0, strokep(BTC_GOLD, 10)); cv.drawLine(-80, 0, -80, 30, strokep(BTC_GOLD, 10))
        text(cv, 'WALLET KEY', 90, 18, 48, CREAM); cv.restore()
    tag(cv, 'A SMALL HARD DRIVE', 540, 300, C('#5a6a8a'), 54, k=pop(T, wt(4, 'small') - 0.15))

def shot_drawer(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#5a4a3a')))
    cv.drawRect(skia.Rect(140, 700, 940, 1700), fillp(C('#8a6040'))); cv.drawRect(skia.Rect(140, 700, 940, 1700), strokep(INK, 8))
    for j in range(3): cv.drawRect(skia.Rect(170, 1050 + j * 210, 910, 1240 + j * 210), fillp(C('#7a5436'))); cv.drawRect(skia.Rect(170, 1050 + j * 210, 910, 1240 + j * 210), strokep(INK, 5)); cv.drawRoundRect(skia.Rect(480, 1130 + j * 210, 600, 1160 + j * 210), 10, 10, fillp(C('#c8a060')))
    o = 1 - ease(clamp((T - 30.7) / 0.5))
    dy = -260 * o
    cv.save(); cv.translate(0, dy * 0)
    cv.drawRect(skia.Rect(170 - 30 * o, 760 + dy * 0.2, 910 + 30 * o, 1030), fillp(C('#6a4a30'))); 
    if o > 0.2: hdd(cv, 540, 870, 0.5 * (0.6 + 0.4 * o), rot=10)
    cv.drawRect(skia.Rect(160 - 40 * o, 900 + 60 * o, 920 + 40 * o, 1040 + 60 * o), fillp(C('#9a6a46'))); cv.drawRect(skia.Rect(160 - 40 * o, 900 + 60 * o, 920 + 40 * o, 1040 + 60 * o), strokep(INK, 6))
    cv.drawRoundRect(skia.Rect(480, 950 + 60 * o, 600, 980 + 60 * o), 10, 10, fillp(C('#c8a060')))
    cv.restore()
    tag(cv, 'TOSSED IN A DRAWER', 540, 300, CREAM, 52, INK, k=pop(T, wt(4, 'tossed') - 0.2))

def shot_clean(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#c8b8a0')))
    cv.drawRect(skia.Rect(-300, 1450, W + 300, H + 300), fillp(C('#8a6a50')))
    window_back(cv, 620, 340, 320, 420)
    for i, (x, y, w, h) in enumerate(((160, 1450, 260, 200), (420, 1450, 220, 160), (300, 1290, 200, 160), (820, 1450, 240, 240))):
        cv.drawRect(skia.Rect(x - w / 2, y - h, x + w / 2, y), fillp(C('#c8a070'))); cv.drawRect(skia.Rect(x - w / 2, y - h, x + w / 2, y), strokep(INK, 6))
        cv.drawLine(x - w / 2, y - h + 30, x + w / 2, y - h + 30, strokep(C('#a07a48'), 6))
    rnd = random.Random(3)
    for i in range(20):
        f = ((T * 0.4 + i / 20) % 1); cv.drawCircle(rnd.uniform(100, 980), 1400 - f * 900, rnd.uniform(4, 10), fillp(C('#ffffff'), alpha=0.4 * (1 - f)))
    calendar(cv, 300, 520, 0.7, 'YEAR', '2013', C('#7a3a2a'), k=pop(T, wt(5, '2013') - 0.25), rot=-4)
    tag(cv, 'CLEANING OUT THE HOUSE', 540, 840, CREAM, 46, INK, k=pop(T, wt(5, 'cleaning') - 0.15))

def shot_bag(cv, T):
    dark_bg(cv, C('#3a3a40'), C('#0e0e12'))
    spot(cv, 540, 1200, 500, 0.25)
    f = clamp((T - 35.2) / 0.9)
    yb = lerp(400, 1250, f * f)
    junk_bag(cv, 540, 1650, 1.6, T, tied=T > 36.4)
    if T < 36.4:
        cv.save(); cv.clipRect(skia.Rect(-300, -300, W + 300, 1180 + 60 if f >= 1 else H)); hdd(cv, 540 + math.sin(T * 8) * 20 * (1 - f), yb, 0.45, rot=T * 200 * (1 - f)); cv.restore()
    for i, (x, y, r) in enumerate(((380, 1100, 30), (720, 1080, -20), (620, 1150, 10))):
        cv.save(); cv.translate(x, y); cv.rotate(r); cv.drawRect(skia.Rect(-40, -30, 40, 30), fillp(C('#8a7a6a'))); cv.drawRect(skia.Rect(-40, -30, 40, 30), strokep(INK, 4)); cv.restore()
    tag(cv, 'A BAG OF JUNK', 540, 300, C('#5a5a62'), 58, k=pop(T, wt(5, 'bag') - 0.2))

def shot_dump(cv, T):
    day_sky(cv, C('#8aa8c0'), C('#e8e4d8'), h=1300, sun=None)
    for i in range(6): cv.drawPath(poly([(i * 220 - 100, 1300), (i * 220 + 10, 1150 - (i % 2) * 60), (i * 220 + 120, 1300)]), fillp(C('#7a9a6a')))
    cv.drawRect(skia.Rect(-300, 1300, W + 300, H + 300), fillp(C('#4a4c54')))
    for i in range(10):
        x = ((i * 200 + T * 600) % 2200) - 300; cv.drawRect(skia.Rect(x, 1560, x + 110, 1576), fillp(C('#f4f4f0')))
    cv.save(); cv.translate(960, 1300); cv.drawRect(skia.Rect(-10, -300, 10, 0), fillp(C('#3a3a40'))); cv.drawRect(skia.Rect(-160, -340, 160, -230), fillp(C('#2a6a3a'))); cv.drawRect(skia.Rect(-160, -340, 160, -230), strokep(INK, 5)); text(cv, 'LANDFILL', 0, -268, 48, CREAM); cv.restore()
    x = 460 + math.sin(T * 3) * 6
    junk_bag(cv, x - 40, 1530, 0.45, T)
    plain_car(cv, x, 1700, 1.0, col=C('#5a7aa0'))
    silhouette(cv, lambda: character(cv, 'gf', x + 40, 1580, 34, t=T))
    tag(cv, 'TO THE LOCAL DUMP', 540, 300, C('#2a6a3a'), 54, k=pop(T, wt(6, 'dump') - 0.2))
    tag(cv, 'HIS GIRLFRIEND AT THE TIME', 540, 420, CREAM, 42, INK, k=pop(T, wt(6, 'girlfriend') - 0.15))

def shot_boom(cv, T):
    full(cv, C('#0a0e12'))
    end = price_chart(cv, 80, 500, 920, 900, T, 41.6, 1.2)
    k = pop(T, wt(7, 'exploded') - 0.1, 0.25)
    if k > 0:
        cv.drawCircle(end[0], end[1], 160 * k, fillp(GREEN, alpha=0.4 * fadek(T, 42.8, 0.6), blur=40))
    tag(cv, 'BITCOIN EXPLODED', 540, 300, GREEN, 62, k=k)
    tag(cv, '2013', 540, 1600, CREAM, 50, INK, k=pop(T, 41.0))

def shot_millions(cv, T):
    dark_bg(cv, C('#3a2a10'), C('#0a0804'))
    rnd = random.Random(8)
    for i in range(36):
        sp = rnd.uniform(0.6, 1.3); f = ((T * 0.45 * sp + rnd.random()) % 1)
        coin(cv, rnd.uniform(60, 1020), -100 + f * 2100, rnd.uniform(35, 70), rot=rnd.uniform(-30, 30), spin=T * 4 * sp + i)
    v = money(T, 43.9, 45.9, 8000 * 0.1, 8000 * 1000)
    cv.drawRoundRect(skia.Rect(90, 820, 990, 1060), 40, 40, fillp(C('#0a0a0e'), alpha=0.85)); cv.drawRoundRect(skia.Rect(90, 820, 990, 1060), 40, 40, strokep(BTC_GOLD, 8))
    text(cv, fmt_usd(v) if v < 1e6 else f'${v / 1e6:.1f} MILLION', 540, 980, 92, BTC_GOLD)
    tag(cv, 'SUDDENLY WORTH MILLIONS', 540, 300, BTC_GOLD, 52, INK, k=pop(T, wt(7, 'millions') - 0.2))

def shot_race(cv, T):
    landfill(cv, T)
    for i in range(10):
        y = 1300 + i * 50; x = ((i * 190 + T * 1800) % 1500) - 200
        cv.drawLine(x, y, x - 220, y, strokep(C('#ffffff'), 6, alpha=0.5))
    x = lerp(150, 620, ease(clamp((T - 46.5) / 1.6)))
    character(cv, 'james', x, 1760, 105, t=T * 2, expr='strain', pose={'walk': 9, 'hl': (-0.6, -0.2), 'hr': (0.6, 0.2)}, look=(1, 0))
    tag(cv, 'RACED TO THE LANDFILL', 540, 300, RED, 52, k=pop(T, wt(8, 'raced') - 0.2))

def shot_buried(cv, T):
    f = ease(clamp((T - 48.4) / 3.0))
    full(cv, C('#1e1818'))
    cv.save(); cv.translate(0, -f * 380)
    section(cv, T, depth_glow=0.9, dark=0.2)
    cv.restore()
    d = int(f * 15)
    cv.drawRect(skia.Rect(40, 500, 110, 1700), fillp(C('#0a0a0e'), alpha=0.6))
    cv.drawRect(skia.Rect(40, 1700 - f * 1200, 110, 1700), fillp(BTC_GOLD, alpha=0.8))
    text(cv, f'{d} m', 210, 1700 - f * 1200, 44, CREAM, stroke=INK, sw=6)
    tag(cv, 'BURIED', 540, 300, C('#5a4a40'), 66, k=pop(T, wt(8, 'buried') - 0.2) * fadek(T, 50.3))
    tag(cv, 'THOUSANDS OF TONNES', 540, 300, RED, 54, k=pop(T, wt(8, 'thousands') - 0.15))
    tag(cv, 'OF GARBAGE', 540, 420, CREAM, 46, INK, k=pop(T, wt(8, 'garbage') - 0.15))

def shot_council(cv, T):
    day_sky(cv, C('#9ab0c4'), C('#e8e4dc'), h=1350, sun=None)
    council_bldg(cv, 540, 1350, 1.0)
    cv.drawRect(skia.Rect(-300, 1350, W + 300, H + 300), fillp(C('#8a8a8a')))
    for i in range(5): cv.drawRect(skia.Rect(240 - i * 30, 1350 + i * 40, 840 + i * 30, 1390 + i * 40), fillp(shade(C('#b8b0a0'), 1 - i * 0.05))); cv.drawRect(skia.Rect(240 - i * 30, 1350 + i * 40, 840 + i * 30, 1390 + i * 40), strokep(INK, 3))
    character(cv, 'james', 540, 1800, 100, t=T, expr='worried', pose={'hl': (0.3, -0.4), 'hr': (-0.3, -0.4)}, look=(0, -0.6))
    tag(cv, 'PLEASE LET ME SEARCH', 540, 300, CREAM, 50, INK, k=pop(T, wt(9, 'begged') - 0.15))

def shot_no(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#2a2a34')))
    character(cv, 'clerk', 540, 1430, 110, t=T, expr='stern', pose={'hl': (-0.5, 0.1)}, look=(0, 0.1))
    table(cv, 540, 1330, 860, 120, 220, col=C('#5a3a28'))
    k = pop(T, wt(9, 'no') - 0.12, 0.2)
    if k > 0:
        cv.save(); cv.translate(540, 560); cv.scale(k, k); cv.rotate(-6)
        cv.drawCircle(0, 0, 220, fillp(RED)); cv.drawCircle(0, 0, 220, strokep(INK, 10)); text(cv, 'NO', 0, 55, 170, CREAM); cv.restore()

def shot_toxic(cv, T):
    section(cv, T, depth_glow=0.3, dark=0.3)
    rnd = random.Random(6)
    for i in range(14):
        f = ((T * 0.3 + rnd.random()) % 1); cv.drawCircle(rnd.uniform(0, W), 1700 - f * 1100, rnd.uniform(30, 80), fillp(C('#9aff6a'), alpha=0.22 * (1 - f), blur=20))
    k = pop(T, wt(9, 'environmental') - 0.2, 0.3)
    if k > 0:
        cv.save(); cv.translate(540, 420); cv.scale(k, k)
        cv.drawPath(poly([(0, -170), (190, 150), (-190, 150)]), fillp(C('#f0c020'))); cv.drawPath(poly([(0, -170), (190, 150), (-190, 150)]), strokep(INK, 12))
        text(cv, '!', 0, 120, 220, INK); cv.restore()
    tag(cv, 'ENVIRONMENTAL DISASTER', 540, 1700, C('#4a8a2a'), 50, k=pop(T, wt(9, 'disaster') - 0.15))

def shot_offer(cv, T):
    desk_bg(cv)
    doc(cv, 540, 980, 700, 900, rot=-2, lines=0, title='THE OFFER', seed=1)
    f = ease(clamp((T - 60.3) / 0.8))
    cv.drawCircle(540, 1020, 220, fillp(C('#d8d0c0'))); cv.drawCircle(540, 1020, 220, strokep(INK, 6))
    cv.drawArc(skia.Rect(320, 800, 760, 1240), -90, 360 * 0.25 * f, True, fillp(BTC_GOLD)); cv.drawArc(skia.Rect(320, 800, 760, 1240), -90, 360 * 0.25 * f, True, strokep(INK, 6))
    if f > 0.9: text(cv, 'SHARE FOR', 540, 1300, 48, INK); text(cv, 'THE CITY', 540, 1360, 48, INK)
    tag(cv, 'HE MADE AN OFFER', 540, 300, BTC_GOLD, 54, INK, k=pop(T, wt(10, 'offer') - 0.2))

def shot_tech(cv, T):
    landfill(cv, T)
    cv.drawRect(skia.Rect(-300, 1400, W + 300, H + 300), fillp(C('#5a5040')))
    k1 = pop(T, wt(10, 'robots') - 0.2); k2 = pop(T, wt(10, 'ai') - 0.2); k3 = pop(T, wt(10, 'professional') - 0.2)
    if k1 > 0: cv.save(); cv.translate(230, 1760); cv.scale(k1, k1); robot_dog(cv, 0, 0, 0.9, T); cv.restore()
    if k2 > 0: drone(cv, 560, lerp(200, 620, k2) + math.sin(T * 2) * 20, 1.2, T, beam_to=(560, 1300))
    if k3 > 0: cv.save(); cv.translate(800, 1760); cv.scale(k3, k3); excavator(cv, 0, 0, 0.8, T, arm=(math.sin(T * 1.5) + 1) / 2); cv.restore()
    tag(cv, 'ROBOTS', 230, 1290, C('#e8c040'), 44, INK, k=k1)
    tag(cv, 'AI SCANNERS', 560, 420, GREEN, 46, k=k2)
    tag(cv, 'EXCAVATION TEAM', 760, 1290, C('#f0b020'), 40, INK, k=k3)

def shot_stillno(cv, T):
    full(cv, C('#14080a'))
    cv.drawCircle(540, 900, 900, fillp(C('#7a1418'), alpha=0.4, blur=200))
    k = pop(T, wt(11, 'no') - 0.15, 0.25)
    text(cv, 'STILL', 540, 640, 110, CREAM)
    if k > 0:
        cv.save(); cv.translate(540, 1000); cv.scale(k * 1.4, k * 1.4); text(cv, 'NO.', 0, 80, 260, RED, stroke=INK, sw=14); cv.restore()
    character(cv, 'james', 540, 1800, 80, t=T, expr='sad', look=(0, -0.3))

def shot_lawsuit(cv, T):
    desk_bg(cv)
    doc(cv, 540, 900, 760, 980, rot=2, lines=6, title='LAWSUIT', seed=5)
    v = money(T, 71.0, 72.9, 0, 495e6)
    text(cv, f'£{v:,.0f}', 540, 1240, 78, RED)
    tag(cv, 'NEARLY £500 MILLION', 540, 300, RED, 56, k=pop(T, wt(12, '500') - 0.2))

def shot_court(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#5a3a28'), C('#2a1a12')])))
    for i in range(-1, 12): cv.drawRect(skia.Rect(i * 110, 200, i * 110 + 60, 1200), fillp(C('#6a4a32')))
    cv.drawRect(skia.Rect(-300, 1200, W + 300, H + 300), fillp(C('#3a2618')))
    character(cv, 'judge', 540, 1340, 100, t=T, expr='stern', look=(0, 0.2))
    cv.drawRect(skia.Rect(100, 1150, 980, 1500), fillp(C('#7a4a2a'))); cv.drawRect(skia.Rect(100, 1150, 980, 1500), strokep(INK, 8))
    hit = wt(13, 'threw') - 0.05
    ang = -50 if T < hit - 0.2 else lerp(-50, 10, ease(clamp((T - hit + 0.2) / 0.2)))
    gavel(cv, 760, 1050, 0.9, ang)
    stamp(cv, 540, 1700, 'CASE DISMISSED', 76, RED, -6, k=pop(T, wt(13, 'out') - 0.1, 0.2))

def shot_closed(cv, T):
    cov = ease(clamp((T - 77.6) / 2.4))
    section(cv, T, depth_glow=0.8 * (1 - cov * 0.5), cover=cov, dark=0.2 + 0.3 * cov)
    k = pop(T, wt(14, 'closed') - 0.2)
    if k > 0:
        cv.save(); cv.translate(760, 480); cv.scale(k, k); cv.drawRect(skia.Rect(-10, 0, 10, 150), fillp(C('#3a3a40'))); cv.drawRect(skia.Rect(-170, -100, 170, 20), fillp(RED)); cv.drawRect(skia.Rect(-170, -100, 170, 20), strokep(INK, 6)); text(cv, 'CLOSED', 0, -20, 64, CREAM); cv.restore()

def shot_climb(cv, T):
    full(cv, C('#0a0e12'))
    end = price_chart(cv, 80, 600, 920, 800, T, 82.0, 2.0, seed=9)
    v = money(T, 82.0, 84.0, 3e8, 8e8)
    text(cv, f'${v / 1e6:,.0f} MILLION', 540, 460, 84, BTC_GOLD, stroke=INK, sw=10)
    tag(cv, 'EVERY YEAR IT CLIMBS', 540, 300, GREEN, 50, k=pop(T, wt(15, 'every') - 0.15))

def shot_valuable(cv, T):
    dark_bg(cv, C('#2a2010'), C('#050402'))
    g = 0.6 + 0.4 * clamp((T - 84.1) / 2.0)
    hdd(cv, 540, 1000, 1.5, rot=-6, glow=g * (0.8 + 0.2 * math.sin(T * 4)))
    for i in range(10):
        a = i / 10 * math.tau + T * 0.6; r = 420 + math.sin(T * 2 + i) * 30
        coin(cv, 540 + math.cos(a) * r, 1000 + math.sin(a) * r * 1.2, 40, spin=T * 2 + i)
    tag(cv, 'EVEN MORE VALUABLE', 540, 300, BTC_GOLD, 54, INK, k=pop(T, wt(15, 'valuable') - 0.2))

def shot_dark(cv, T):
    section(cv, T, depth_glow=1.0, dark=0.6, scan=0.4)
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#000000'), alpha=0.35))
    k = pop(T, wt(16, 'eight') - 0.2, 0.3)
    if k > 0:
        cv.save(); cv.translate(540, 360); cv.scale(k, k); text(cv, '8,000 BTC', 0, 40, 130, BTC_GOLD, stroke=INK, sw=12); cv.restore()
    tag(cv, 'SITTING IN THE DARK', 540, 520, CREAM, 48, INK, k=pop(T, wt(16, 'sitting') - 0.15) * fadek(T, 90.2, 0.25))
    end = TL['total']
    b = clamp((T - (end - 0.62)) / 0.6)
    if b > 0:
        surf = skia.Surface(W, H); c2 = surf.getCanvas(); shot_hook(c2, 0.0, frozen=True)
        p = skia.Paint(); p.setAlphaf(b)
        cv.save(); cv.resetMatrix(); cv.drawImage(surf.makeImageSnapshot(), 0, 0, skia.SamplingOptions(), p); cv.restore()


def shot_sue(cv, T):
    day_sky(cv, C('#9ab0c4'), C('#e8e4dc'), h=1350, sun=None)
    council_bldg(cv, 700, 1350, 0.8)
    cv.drawRect(skia.Rect(-300, 1350, W + 300, H + 300), fillp(C('#8a8a8a')))
    x = lerp(-100, 300, ease(clamp((T - 68.8) / 1.4)))
    character(cv, 'james', x, 1760, 105, t=T, expr='stern', pose={'walk': 5 if T < 70.2 else 0, 'hr': (0.3, 0.8)}, look=(1, 0))
    briefcase(cv, x + 90, 1560, 0.5)
    calendar(cv, 300, 520, 0.65, 'YEAR', '2024', C('#2a3a6a'), k=pop(T, wt(12, '2024') - 0.25), rot=-4)
    tag(cv, 'HE SUED THE COUNCIL', 540, 300, RED, 54, k=pop(T, wt(12, 'sued') - 0.2))

def shot_appeal(cv, T):
    desk_bg(cv)
    doc(cv, 540, 950, 700, 900, rot=-3, lines=8, title='APPEAL', seed=7, k=eout(clamp((T - 75.45) / 0.3)))
    stamp(cv, 540, 1000, 'REJECTED', 120, RED, -14, k=pop(T, wt(13, 'rejected') - 0.1, 0.18))
    tag(cv, 'APPEAL REJECTED TOO', 540, 300, CREAM, 52, INK, k=pop(T, wt(13, 'appeal') - 0.15))

def shot_forever(cv, T):
    day_sky(cv, C('#7ab0d8'), C('#e8f0e0'), h=1200, sun=(820, 300))
    hill = [(-300, 1400), (-100, 900), (200, 760), (520, 700), (820, 780), (1100, 900), (1380, 1300), (1380, H + 300), (-300, H + 300)]
    cv.drawPath(poly(hill), fillp(C('#5a9a4a'))); cv.drawPath(poly(hill), strokep(INK, 7))
    g = clamp((T - 80.6) / 1.3)
    for i, x in enumerate((120, 330, 700, 900, 520)):
        h = 200 * clamp(g * 1.4 - i * 0.12)
        if h > 0:
            y = 1050 + (i % 2) * 120
            cv.drawLine(x, y, x, y - h, strokep(C('#6a4a2a'), 14)); cv.drawCircle(x, y - h, h * 0.45, fillp(C('#3a7a3a'))); cv.drawCircle(x, y - h, h * 0.45, strokep(INK, 5))
    yr = 2026 + int(g * 30)
    text(cv, str(yr), 540, 560, 120, CREAM, stroke=INK, sw=10)
    tag(cv, 'POSSIBLY FOREVER', 540, 300, C('#2a5a3a'), 56, k=pop(T, wt(14, 'possibly') - 0.15))

ACTS = [(0, C('#2a2a5a'), 0.10), (9.7, C('#2a3a6a'), 0.07), (14.2, C('#2a5a3a'), 0.08), (31.7, C('#8a6a3a'), 0.08),
        (40.6, C('#8a6a1a'), 0.10), (46.3, C('#5a4a3a'), 0.08), (52.4, C('#3a4a6a'), 0.08), (58.5, C('#8a6a1a'), 0.07),
        (66.7, C('#6a1a1a'), 0.10), (77.2, C('#2a4a3a'), 0.08), (81.9, C('#8a6a1a'), 0.10), (86.9, C('#2a2a5a'), 0.10)]
def overlay(cv, T): grade(cv, T, ACTS)

def scenes():
    end = TL['total']
    Z = (1.0, 540, 960)
    def z(a, cx=540, cy=960): return (a, cx, cy)
    L = [
        (0.0, shot_hook, (Z, z(1.1, 560, 1100)), 'cut'),
        (2.85, shot_inside, (z(1.0), z(1.15, 560, 1250)), 'zoom'),
        (6.75, shot_fence, (Z, z(1.08, 460, 1200)), 'whip'),
        (9.7, shot_name, (Z, z(1.08, 540, 900)), 'flash'),
        (11.7, shot_wales, (Z, z(1.3, 560, 1100)), 'wipe'),
        (14.2, shot_2009, (Z, z(1.06)), 'fade'),
        (18.0, shot_mining, (Z, z(1.1, 520, 1100)), 'whip'),
        (20.1, shot_8000, (Z, z(1.08)), 'zoom'),
        (24.1, shot_nothing, (Z, z(1.06)), 'wipe'),
        (26.5, shot_stop, (z(1.1, 540, 1100), Z), 'cut'),
        (28.05, shot_drive, (Z, z(1.12, 540, 1000)), 'zoom'),
        (30.15, shot_drawer, (Z, z(1.08, 540, 1000)), 'whip'),
        (31.75, shot_clean, (Z, z(1.06)), 'fade'),
        (34.95, shot_bag, (Z, z(1.1, 540, 1300)), 'cut'),
        (37.45, shot_dump, (Z, z(1.06, 500, 1250)), 'wipe'),
        (40.65, shot_boom, (Z, z(1.08, 700, 800)), 'flash'),
        (43.7, shot_millions, (Z, z(1.08)), 'zoom'),
        (46.35, shot_race, (Z, z(1.06, 560, 1200)), 'whip'),
        (48.3, shot_buried, (Z, Z), 'cut'),
        (52.45, shot_council, (Z, z(1.08, 540, 1200)), 'wipe'),
        (54.95, shot_no, (z(1.1), Z), 'flash'),
        (55.95, shot_toxic, (Z, z(1.06)), 'fade'),
        (58.55, shot_offer, (Z, z(1.08)), 'whip'),
        (62.35, shot_tech, (Z, z(1.05, 540, 1100)), 'wipe'),
        (66.75, shot_stillno, (z(1.12), Z), 'flash'),
        (68.7, shot_sue, (Z, z(1.06, 400, 1200)), 'wipe'),
        (70.95, shot_lawsuit, (Z, z(1.1, 540, 1100)), 'zoom'),
        (73.65, shot_court, (Z, z(1.06)), 'cut'),
        (75.35, shot_appeal, (z(1.1), Z), 'whip'),
        (77.2, shot_closed, (Z, z(1.08)), 'fade'),
        (80.5, shot_forever, (Z, z(1.08)), 'wipe'),
        (81.9, shot_climb, (Z, z(1.08, 700, 900)), 'whip'),
        (84.0, shot_valuable, (Z, z(1.12)), 'zoom'),
        (87.1, shot_dark, (z(1.0), z(1.0)), 'fade'),
    ]
    out = []
    for i, (s0, fn, cam, tr) in enumerate(L):
        s1 = L[i + 1][0] if i + 1 < len(L) else end
        out.append((s0, s1, fn, cam, tr))
    return out
