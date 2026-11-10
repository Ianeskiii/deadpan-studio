"""Example episode as delivered in the original session (virginia-hall). Shots, ACTS grade and scenes() list.
Run from this folder: python3 ../../render.py still 1.0 ..."""
from core import *
from lib import _arm


# ---------------- helpers for Virginia Hall ----------------
RED = C('#c8281e'); CREAM = C('#f4efe2'); GOLD = C('#e8b84a'); TEAL = C('#7ad7ff')
def limp(t, sp=5.0, u=100):
    # uneven gait: a hitch on one side
    return {'walk': sp, 'dy': -u * 0.09 * max(0, math.sin(t * sp)) ** 3}
def fadek(T, t1, d=0.25): return 1 - clamp((T - t1) / d)
def spot(cv, x, y, r=520, a=0.35, col=C('#fff2c8')):
    cv.drawCircle(x, y, r, fillp(col, alpha=a, blur=r * 0.35))
def corner_label(cv, s, T, t0, col=CREAM):
    k = clamp((T - t0) / 0.3)
    if k <= 0: return
    f = skia.Font(skia.Typeface('Courier New', skia.FontStyle.Bold()), 40)
    n = int(len(s) * clamp((T - t0) / 0.6))
    cv.drawRect(skia.Rect(60, 1610, 60 + f.measureText(s) + 40, 1680), fillp(C('#0a0a0e'), alpha=0.6 * k))
    cv.drawString(s[:n], 80, 1660, f, fillp(col, alpha=k))
def footprints(cv, T, t0, n=8, y0=1750, col=C('#2a2a30'), a=0.8, x0=100, dx=120):
    for i in range(n):
        if T < t0 + i * 0.22: break
        x = x0 + i * dx; y = y0 - (i % 2) * 70
        big = i % 2 == 0
        if big: cv.drawOval(skia.Rect(x - 24, y - 52, x + 24, y + 30), fillp(col, alpha=a))
        else: cv.drawOval(skia.Rect(x - 16, y - 34, x + 16, y + 40), fillp(col, alpha=a)); cv.drawLine(x, y + 44, x + 30, y + 64, strokep(col, 10, alpha=a * 0.7))
def morse(cv, x, y, T, t0, col=C('#7cf29a')):
    pat = '.-- .. .-. . ...'
    n = int(clamp((T - t0) / 1.5) * len(pat)); cx = x
    for ch in pat[:n]:
        if ch == '.': cv.drawCircle(cx, y, 9, fillp(col)); cx += 30
        elif ch == '-': cv.drawRoundRect(skia.Rect(cx - 9, y - 9, cx + 34, y + 9), 9, 9, fillp(col)); cx += 54
        else: cx += 30
def flag_france_silhouette(cv, pts, col): cv.drawPath(poly(pts), fillp(col)); cv.drawPath(poly(pts), strokep(INK, 6))
FRANCE = [(380, 560), (520, 500), (640, 560), (700, 700), (660, 860), (700, 1000), (600, 1060), (480, 1080), (360, 1040), (300, 900), (240, 800), (160, 740), (240, 680), (340, 660)]
BRITAIN = [(300, 160), (380, 120), (420, 260), (470, 380), (440, 470), (300, 480), (240, 430), (300, 340), (250, 250)]
SPAIN = [(300, 1100), (480, 1090), (620, 1080), (700, 1160), (640, 1420), (420, 1520), (180, 1480), (120, 1300), (160, 1140)]
def europe_map(cv, T, occupied=0.0, sea=C('#2e5670'), land=C('#d8c49a')):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(sea))
    for i in range(-300, W + 300, 60): cv.drawLine(i, -300, i, H + 300, strokep(shade(sea, 1.12), 2))
    for j in range(-300, H + 300, 60): cv.drawLine(-300, j, W + 300, j, strokep(shade(sea, 1.12), 2))
    cont = [(560, 380), (800, 300), (1400, 260), (1400, 1300), (900, 1250), (720, 1150), (700, 1000), (660, 860), (700, 700), (640, 560)]
    cv.drawPath(poly(cont), fillp(shade(land, 0.93))); cv.drawPath(poly(cont), strokep(INK, 6))
    fr = mix(land, C('#5a3a3a'), occupied)
    flag_france_silhouette(cv, FRANCE, fr); flag_france_silhouette(cv, BRITAIN, land); flag_france_silhouette(cv, SPAIN, shade(land, 0.9))
    for p, n in (((470, 800), 'FRANCE'), ((350, 330), 'BRITAIN'), ((420, 1300), 'SPAIN')): text(cv, n, p[0], p[1], 40, shade(INK, 1.6))
def lyon_room(cv, T, lamp=True):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#4a3a40'), C('#2a2028')])))
    for i in range(-2, 16): cv.drawLine(i * 90, -300, i * 90, 1450, strokep(C('#3e3036'), 4))
    cv.drawRect(skia.Rect(-300, 1450, W + 300, H + 300), fillp(C('#3a2a22')))
    for i in range(-3, 14): cv.drawLine(i * 120, 1450, i * 120 - 200, H + 50, strokep(C('#2a1e18'), 4))
    if lamp: spot(cv, 540, 700, 700, 0.18)

def shot_hook(cv, T, frozen=False):
    t = 0 if frozen else T
    lyon_street(cv, t)
    wanted_poster(cv, 840, 980, 0.62, 4)
    # searchlight sweep
    a = math.sin(t * 0.9) * 22 - 4
    cv.save(); cv.rotate(a, 540, -200)
    cv.drawPath(poly([(510, -200), (570, -200), (760, 1700), (320, 1700)]), fillp(C('#fff4c8'), alpha=0.13, blur=20)); cv.restore()
    # gestapo shadows far behind
    def g():
        for i, x in enumerate((240, 380)): character(cv, 'gest', x + t * 14, 1470, 46, t=t, pose={'walk': 4}, blink_seed=i)
    silhouette(cv, g)
    character(cv, 'vh_coat', 560 + t * 18, 1700, 100, t=t, expr='worried', pose=limp(t, 4.5), look=(-0.5, 0), facing=1)
    if frozen: return
    tag(cv, 'MOST DANGEROUS SPY', 540, 300, RED, 60, k=pop(T, wt(0, 'dangerous') - 0.2))
    tag(cv, 'IN ALL OF FRANCE', 540, 420, CREAM, 46, INK, k=pop(T, wt(0, 'france') - 0.15))

def shot_leg(cv, T):
    dark_bg(cv, C('#3a2a1e'), C('#0a0604'))
    spot(cv, 540, 900, 560, 0.3)
    soft_shadow(cv, 560, 1240, 260, 30, 0.5)
    k = eout(clamp((T - 4.2) / 0.6))
    cuthbert(cv, 520, lerp(1400, 1240, k), 1.25, rot=lerp(12, 0, k))
    for i in range(5): particles(cv, T, 18, seed=9, col=C('#ffd8a0')) if i == 0 else None
    tag(cv, 'A WOODEN LEG', 540, 330, GOLD, 64, INK, k=pop(T, wt(0, 'wooden') - 0.15))

def shot_name(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (W, H), [C('#1c2a44'), C('#0a0e1a')])))
    for i in range(14): cv.drawLine(-300, i * 160 - (T * 40 % 160), W + 300, i * 160 + 300 - (T * 40 % 160), strokep(C('#24365a'), 30, alpha=0.5))
    spot(cv, 540, 980, 520, 0.25)
    character(cv, 'vh', 540, 1700, 135, t=T, expr='smile', pose={'hr': (0.5, 0.5)}, look=(0.15, -0.1))
    k = pop(T, wt(1, 'virginia') - 0.2, 0.35)
    if k > 0:
        cv.save(); cv.translate(540, 360); cv.scale(k, k)
        cv.drawRect(skia.Rect(-420, -110, 420, 110), fillp(CREAM)); cv.drawRect(skia.Rect(-420, -110, 420, 110), strokep(INK, 7))
        cv.drawRect(skia.Rect(-420, -110, -390, 110), fillp(RED))
        text(cv, 'VIRGINIA HALL', 15, 30, 92, INK); cv.restore()
    tag(cv, 'AMERICAN', 540, 560, C('#3a5a9a'), 48, k=pop(T, wt(1, 'american') - 0.15))

def shot_diplomat(cv, T):
    lyon_room(cv, T)
    window_back(cv, 160, 300, 300, 420)
    table(cv, 600, 1250, 600, 120, 200)
    character(cv, 'vh', 380, 1700, 100, t=T, expr='happy', pose={'hl': (-0.3, -0.4), 'hr': (0.4, 0.5)}, look=(0.4, -0.6))
    k = pop(T, wt(1, 'dreamed') - 0.25, 0.4)
    for i, (x, y, r) in enumerate(((480, 840, 16), (530, 760, 24))):
        cv.drawCircle(x, y, r * k, fillp(C('#ffffff'))); cv.drawCircle(x, y, r * k, strokep(INK, 5))
    if k > 0:
        cv.save(); cv.translate(700, 560); cv.scale(k, k)
        cv.drawOval(skia.Rect(-300, -200, 300, 200), fillp(C('#ffffff'))); cv.drawOval(skia.Rect(-300, -200, 300, 200), strokep(INK, 6))
        cv.drawCircle(-140, 0, 90, fillp(C('#5a9ad8'))); cv.drawCircle(-140, 0, 90, strokep(INK, 5))
        for d in (-50, 0, 50): cv.drawLine(-230, d, -50, d, strokep(C('#3a7a3a'), 10))
        cv.drawOval(skia.Rect(-175, -90, -105, 90), strokep(INK, 4))
        doc(cv, 120, 10, 200, 260, rot=6, lines=4, title='VISA', seed=3)
        cv.restore()
    tag(cv, 'DREAM: DIPLOMAT', 540, 300, CREAM, 56, INK, k=pop(T, wt(1, 'diplomat') - 0.2))

def shot_turkey(cv, T):
    europe_map(cv, T)
    tk = [(1000, 820), (1200, 790), (1400, 820), (1400, 960), (1160, 990), (1000, 960)]
    cv.drawPath(poly(tk), fillp(C('#c89a6a'))); cv.drawPath(poly(tk), strokep(INK, 6))
    pin = pop(T, wt(2, 'turkey') - 0.2)
    if pin > 0:
        cv.save(); cv.translate(1060, 880); cv.scale(pin, pin)
        cv.drawPath(poly([(0, 0), (-30, -60), (30, -60)]), fillp(RED)); cv.drawCircle(0, -80, 36, fillp(RED)); cv.drawCircle(0, -80, 36, strokep(INK, 5)); cv.drawCircle(0, -80, 12, fillp(CREAM)); cv.restore()
    calendar(cv, 540, 420, 0.75, 'YEAR', '1933', C('#7a3a2a'), k=pop(T, wt(2, '1933') - 0.25, 0.3), rot=-4)

def shot_hunt(cv, T):
    woods(cv, T, off=T * 30)
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#1a2a1a'), alpha=0.35))
    bang = wt(2, 'accident') - 0.1
    def sil():
        character(cv, 'vh', 520, 1700, 100, t=T, expr='neutral', pose={'hl': (0.5, 0.1), 'hr': (0.8, 0.0)}, look=(1, 0))
    silhouette(cv, sil)
    cv.save(); cv.translate(600, 1240); cv.rotate(-8 if T < bang else lerp(-8, 70, ease(clamp((T - bang) / 0.6))))
    cv.drawRoundRect(skia.Rect(-60, -14, 300, 14), 7, 7, fillp(C('#0e0e10'))); cv.restore()
    f = clamp(1 - (T - bang) / 0.5) if T >= bang else 0
    if f > 0: cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(RED, alpha=f * 0.55))
    k = pop(T, bang, 0.2)
    if k > 0:
        cv.save(); cv.translate(540, 520); cv.scale(k, k); cv.rotate(-6)
        star = [(math.cos(a / 16 * math.tau) * (230 if a % 2 == 0 else 150), math.sin(a / 16 * math.tau) * (150 if a % 2 == 0 else 100)) for a in range(16)]
        cv.drawPath(poly(star), fillp(C('#ffe04a'))); cv.drawPath(poly(star), strokep(INK, 7)); text(cv, 'BANG!', 0, 30, 96, RED); cv.restore()
    tag(cv, 'HUNTING ACCIDENT', 540, 290, CREAM, 52, INK, k=pop(T, wt(2, 'hunting') - 0.15))

def shot_hospital(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#d8e4e8'), C('#9aaab4')])))
    cv.drawRect(skia.Rect(-300, 1350, W + 300, H + 300), fillp(C('#7a8a94')))
    window_back(cv, 640, 360, 320, 420)
    cv.drawRoundRect(skia.Rect(100, 1250, 900, 1330), 20, 20, fillp(C('#f4f4f2'))); cv.drawRoundRect(skia.Rect(100, 1250, 900, 1330), 20, 20, strokep(INK, 6))
    for x in (130, 870): cv.drawLine(x, 1330, x, 1560, strokep(C('#5a6470'), 14))
    cv.drawLine(110, 1100, 110, 1330, strokep(C('#5a6470'), 14))
    lying(cv, 'vh', 380, 1250, 80, T, expr='sad', look=(0.3, -0.5))
    blanket = skia.Path(); blanket.addRoundRect(skia.Rect(420, 1150, 900, 1290), 50, 50)
    cv.drawPath(blanket, fillp(C('#8ab0d0'))); cv.drawPath(blanket, strokep(INK, 6))
    character(cv, 'doctor', 860, 1700, 95, t=T, expr='sad', pose={'hl': (-0.4, 0.4)}, look=(-0.6, 0.2))
    doc(cv, 760, 1520, 160, 210, rot=-8, lines=3, title='CHART', seed=5)
    tag(cv, 'AMPUTATED', 540, 300, RED, 60, k=pop(T, wt(2, 'amputated') - 0.2))
    tag(cv, 'BELOW THE KNEE', 540, 420, CREAM, 44, INK, k=pop(T, wt(2, 'knee') - 0.15))

def shot_prosthetic(cv, T):
    paper_bg(cv, C('#e8dcc4'))
    for i in range(-2, 12): cv.drawLine(-300, 300 + i * 140, W + 300, 300 + i * 140, strokep(C('#a8c0d8'), 3, alpha=0.6))
    # blueprint lines
    cv.drawLine(220, 500, 220, 1250, strokep(C('#3a6aa0'), 4)); text(cv, '15 in', 160, 880, 34, C('#3a6aa0'), rot=-90)
    k = eout(clamp((T - 19.9) / 0.5))
    cuthbert(cv, 560, 1230, lerp(0.5, 1.15, k))
    for i in range(4): sparkle(cv, 700 + math.sin(i * 2 + T * 2) * 120, 700 + i * 120, 26)
    tag(cv, 'PROSTHETIC LEG', 540, 330, C('#3a6aa0'), 60, k=pop(T, wt(3, 'prosthetic') - 0.2))

def shot_cuthbert(cv, T):
    lyon_room(cv, T)
    character(cv, 'vh', 320, 1720, 100, t=T, expr='grin', pose={'hr': (0.8, -0.2)}, look=(0.7, 0))
    cuthbert(cv, 700, 1600, 0.9, bow=T > wt(3, 'cuthbert') - 0.2, tag_=False)
    k = pop(T, wt(3, 'cuthbert') - 0.2, 0.35)
    if k > 0:
        cv.save(); cv.translate(720, 560); cv.scale(k, k); cv.rotate(-5)
        cv.drawRoundRect(skia.Rect(-330, -110, 330, 110), 30, 30, fillp(CREAM)); cv.drawRoundRect(skia.Rect(-330, -110, 330, 110), 30, 30, strokep(INK, 8))
        cv.drawCircle(-290, 0, 18, strokep(INK, 6)); cv.drawLine(-290, 18, -150, 500, strokep(INK, 4))
        text(cv, 'CUTHBERT', 20, 34, 96, INK); cv.restore()
    tag(cv, 'SHE NAMED IT', 400, 300, GOLD, 52, INK, k=pop(T, wt(3, 'name') - 0.15))

def shot_rejected(cv, T):
    desk_bg(cv)
    doc(cv, 540, 860, 640, 820, rot=-3, lines=10, title='U.S. STATE DEPT.', seed=8, k=eout(clamp((T - 24.05) / 0.35)))
    stamp(cv, 540, 900, 'REJECTED', 110, RED, -14, k=pop(T, wt(4, 'rejected') - 0.1, 0.18))
    tag(cv, 'BECAUSE OF HER LEG', 540, 320, CREAM, 48, INK, k=pop(T, wt(4, 'because') - 0.15))

def shot_war(cv, T):
    occ = clamp((T - 27.3) / 1.0)
    europe_map(cv, T, occupied=occ)
    for i in range(6):
        k = clamp((T - 27.2 - i * 0.12) / 0.5)
        map_arrow(cv, (1300, 300 + i * 120), (760 - i * 20, 520 + i * 90), k=k, col=C('#3a3a40'), w=14, bend=-60)
    calendar(cv, 820, 1700, 0.62, 'WAR', '1939', C('#3a3a40'), k=pop(T, wt(4, 'world') - 0.2), rot=5)
    tag(cv, 'WORLD WAR II', 540, 300, RED, 64, k=pop(T, wt(4, 'world') - 0.2))

def shot_door(cv, T):
    full(cv, C('#0a0a0e'))
    o = ease(clamp((T - 28.8) / 0.8))
    cv.drawRect(skia.Rect(340, 500, 740, 1450), fillp(C('#1a1a20')))
    cv.drawRect(skia.Rect(340, 500, 340 + 400 * o, 1450), fillp(C('#fff2c8')))
    cv.drawPath(poly([(340, 1450), (340 + 400 * o, 1450), (340 + 700 * o, 1900), (340 - 200 * o, 1900)]), fillp(C('#fff2c8'), alpha=0.4))
    door(cv, 340, 500, 400, 950, openf=o, col=C('#4a3a30'))
    def sil(): character(cv, 'vh_coat', 540, lerp(1800, 1460, ease(clamp((T - 29.2) / 1.2))), lerp(110, 70, ease(clamp((T - 29.2) / 1.2))), t=T, pose=limp(T, 4))
    if T > 29.0: silhouette(cv, sil)
    tag(cv, 'ANOTHER WAY IN', 540, 300, GOLD, 58, INK, k=pop(T, wt(4, 'another') - 0.2))

def shot_soe(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#3a4048'), C('#1c2026')])))
    window_back(cv, 640, 260, 340, 480)
    cv.drawPath(poly([(760, 740), (760, 420), (790, 380), (820, 420), (820, 740)]), fillp(C('#2a3040')))
    cv.drawCircle(790, 470, 18, fillp(C('#f4e8b0')))
    for i in range(3): doc(cv, 160 + i * 30, 560 + i * 20, 220, 290, rot=-6 + i * 5, lines=4, seed=i, title='SECRET' if i == 2 else None)
    character(cv, 'soe', 760, 1420, 95, t=T, expr='smug', pose={'hl': (-0.6, 0.0)}, look=(-0.8, 0))
    table(cv, 540, 1320, 760, 120, 220, col=C('#5a3a28'))
    character(cv, 'vh_coat', 300, 1720, 100, t=T, expr='smile', look=(0.6, -0.2))
    tag(cv, "BRITAIN'S SECRET SPY AGENCY", 540, 300, C('#2a3a5a'), 46, k=pop(T, wt(5, "britain's") - 0.15))
    tag(cv, 'S.O.E.', 540, 430, RED, 60, k=pop(T, wt(5, 'recruited') - 0.15))

def shot_1941(cv, T):
    europe_map(cv, T, occupied=1.0)
    k = clamp((T - 33.4) / 1.0)
    map_arrow(cv, (360, 400), (520, 820), k=k, col=GOLD, w=18, bend=-60)
    text(cv, 'LONDON', 350, 120, 44, CREAM, stroke=INK, sw=8)
    text(cv, 'VICHY FRANCE', 520, 960, 44, CREAM, stroke=INK, sw=8)
    calendar(cv, 820, 520, 0.7, 'YEAR', '1941', C('#2a4a7a'), k=pop(T, wt(5, '1941') - 0.25), rot=4)

def shot_undercover(cv, T):
    lyon_street(cv, T, night=False)
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#c8a070'), alpha=0.12))
    character(cv, 'vh_coat', 540, 1750, 120, t=T, expr='smug', pose={'hr': (0.6, -0.1), 'hl': (-0.2, 0.9)}, look=(0.3, 0))
    # press badge + notebook
    cv.save(); cv.translate(500, 1450); cv.rotate(-4)
    cv.drawRoundRect(skia.Rect(-70, -40, 70, 40), 8, 8, fillp(CREAM)); cv.drawRoundRect(skia.Rect(-70, -40, 70, 40), 8, 8, strokep(INK, 4)); text(cv, 'PRESS', 0, 14, 36, RED); cv.restore()
    cv.save(); cv.translate(720, 1370); cv.rotate(10)
    cv.drawRect(skia.Rect(-60, -80, 60, 80), fillp(C('#f6f0dc'))); cv.drawRect(skia.Rect(-60, -80, 60, 80), strokep(INK, 4))
    for i in range(4): cv.drawLine(-40, -50 + i * 30, 40, -50 + i * 30, strokep(C('#6a6050'), 4))
    cv.restore()
    tag(cv, 'UNDERCOVER', 540, 300, C('#2a2a30'), 64, k=pop(T, wt(5, 'undercover') - 0.2))
    tag(cv, 'FAKE JOB: REPORTER', 540, 430, CREAM, 46, INK, k=pop(T, wt(5, 'newspaper') - 0.2))

def shot_network(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#5a4028')))
    cv.drawRect(skia.Rect(80, 260, 1000, 1560), fillp(C('#b88a5a'))); cv.drawRect(skia.Rect(80, 260, 1000, 1560), strokep(INK, 8))
    rnd = random.Random(4)
    for i in range(160): cv.drawCircle(rnd.uniform(90, 990), rnd.uniform(270, 1550), rnd.uniform(2, 6), fillp(C('#8a6a40'), alpha=0.5))
    nodes = [(540, 700), (250, 480), (820, 470), (220, 960), (860, 950), (380, 1250), (720, 1260), (540, 1060)]
    for j, (a, b) in enumerate(((0, 1), (0, 2), (0, 3), (0, 4), (3, 5), (4, 6), (0, 7), (7, 5), (7, 6), (1, 3), (2, 4))):
        k = clamp((T - 40.0 - j * 0.18) / 0.3)
        if k > 0:
            p0, p1 = nodes[a], nodes[b]
            cv.drawLine(p0[0], p0[1], lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k), strokep(RED, 6))
    for i, (x, y) in enumerate(nodes):
        k = pop(T, 39.8 + i * 0.15, 0.25)
        if k <= 0: continue
        cv.save(); cv.translate(x, y); cv.scale(k, k); cv.rotate((i % 3 - 1) * 5)
        cv.drawRect(skia.Rect(-80, -100, 80, 100), fillp(C('#f4efe2'))); cv.drawRect(skia.Rect(-80, -100, 80, 100), strokep(INK, 5))
        cv.save(); cv.clipRect(skia.Rect(-70, -90, 70, 70))
        nm = 'vh_coat' if i == 0 else ('fighter1' if i % 2 else 'fighter2')
        character(cv, nm, 0, 210, 52, t=0, expr='neutral', blink_seed=i)
        cv.restore()
        cv.drawCircle(0, -100, 12, fillp(RED)); cv.restore()
    tag(cv, 'SPY NETWORKS', 540, 180, CREAM, 58, INK, k=pop(T, wt(6, 'networks') - 0.2))

def shot_escape(cv, T):
    night_sky(cv, C('#060a18'), C('#1a2238'), h=1200, moon=(200, 260))
    cv.drawRect(skia.Rect(-300, 600, W + 300, 1450), fillp(C('#4a4a52'))); cv.drawRect(skia.Rect(-300, 600, W + 300, 1450), strokep(INK, 6))
    for r in range(8):
        for c in range(-1, 10): cv.drawRect(skia.Rect(c * 140 + (r % 2) * 70, 600 + r * 106, c * 140 + (r % 2) * 70 + 140, 706 + r * 106), strokep(C('#3a3a42'), 3))
    for x in range(-100, W + 100, 50): cv.drawLine(x, 600, x + 25, 560, strokep(C('#6a6a72'), 4))
    cv.drawRect(skia.Rect(-300, 1450, W + 300, H + 300), fillp(C('#1e2a1e')))
    cv.drawLine(560, 580, 600, 1450, strokep(C('#c8b080'), 8))
    k = clamp((T - 42.4) / 1.4)
    character(cv, 'fighter2', 590, lerp(1700, 1460, k) if k < 0.6 else 1700, 80, t=T, expr='worried', pose={'hl': (0.1, -1.0), 'hr': (0.2, -0.9)}, look=(0, -0.6))
    character(cv, 'fighter1', lerp(820, 1100, k), 1700, 80, t=T, expr='happy', pose={'walk': 7}, look=(1, 0), blink_seed=2)
    beam(cv, 980, 200, lerp(200, 900, (math.sin(T * 1.5) + 1) / 2), 1450, w=0.18, a=60)
    tag(cv, 'PRISONERS ESCAPE', 540, 300, GOLD, 56, INK, k=pop(T, wt(6, 'prisoners') - 0.2))

def shot_radio(cv, T):
    lyon_room(cv, T, lamp=False)
    spot(cv, 540, 1100, 520, 0.28, C('#ffcf80'))
    table(cv, 540, 1320, 800, 120, 220, col=C('#4a3020'))
    character(cv, 'vh', 300, 1420, 95, t=T, expr='stern', pose={'hr': (0.9, 0.2), 'sit': False}, look=(0.7, 0.2))
    cv.drawArc(skia.Rect(300 - 115, 1420 - 95 * 4.6, 300 + 115, 1420 - 95 * 3.3), 180, 180, False, strokep(INK, 14))
    radio_set(cv, 690, 1160, 0.8, T)
    morse(cv, 200, 560, T, 44.0)
    tag(cv, 'SECRETS TO LONDON', 540, 300, C('#2a6a4a'), 54, k=pop(T, wt(6, 'london') - 0.2))

def shot_gestapo(cv, T):
    full(cv, C('#120c0c'))
    cv.drawCircle(540, 1000, 900, fillp(C('#7a1a14'), alpha=0.35, blur=200))
    table(cv, 540, 1250, 860, 150, 260, col=C('#3a2a22'))
    cv.save(); cv.translate(540, 1180); cv.scale(0.55, 0.16); cv.translate(-540, -960); europe_map(cv, T, occupied=1.0); cv.restore()
    cv.drawLine(400, 1740, 400, 1220, strokep(C('#ffcf80'), 1, alpha=0))
    for i, x in enumerate((220, 540, 860)):
        def sil(x=x, i=i): character(cv, 'gest', x, 1720 if i != 1 else 1100, 100 if i != 1 else 85, t=T, pose={'hl': (0.4, 0.2)} if i == 0 else None, blink_seed=i)
        silhouette(cv, sil, glint=[(x - 16, (1720 if i != 1 else 1100) - (100 if i != 1 else 85) * 3.3), (x + 16, (1720 if i != 1 else 1100) - (100 if i != 1 else 85) * 3.3)])
    # magnifier sweeping the map
    mx = 540 + math.sin(T * 1.6) * 200
    cv.drawCircle(mx, 1180, 70, strokep(C('#c8c8d0'), 12)); cv.drawLine(mx + 50, 1230, mx + 130, 1310, strokep(C('#3a2a1a'), 18))
    tag(cv, 'THE GESTAPO', 540, 300, RED, 64, k=pop(T, wt(7, 'gestapo') - 0.2))
    tag(cv, 'HUNTING HER', 540, 430, CREAM, 48, INK, k=pop(T, wt(7, 'hunting') - 0.15))

def shot_posters(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#5a5048')))
    for r in range(14):
        for c in range(-1, 9): cv.drawRect(skia.Rect(c * 150 + (r % 2) * 75, r * 130, c * 150 + (r % 2) * 75 + 150, r * 130 + 130), strokep(C('#4a4038'), 4))
    pos = [(270, 560, -6), (780, 520, 5), (540, 980, -2), (230, 1500, 7), (850, 1460, -8)]
    for i, (x, y, r) in enumerate(pos):
        wanted_poster(cv, x, y, 0.95 if i == 2 else 0.72, r, k=pop(T, 48.35 + i * 0.32, 0.25))
    tag(cv, 'WANTED', 540, 200, RED, 70, k=pop(T, wt(7, 'wanted') - 0.2))

def shot_limping(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#1a1e2a'), C('#2a2a30')])))
    cv.drawRect(skia.Rect(-300, 1000, W + 300, H + 300), fillp(C('#3a3a40')))
    footprints(cv, T, 50.0, n=9, y0=1700, col=C('#c8c0b0'), a=0.6, x0=80, dx=115)
    beam(cv, 1200, 300, lerp(200, 980, clamp((T - 50.0) / 2.0)), 1650, w=0.2, a=90)
    k = pop(T, wt(7, 'limping') - 0.2, 0.35)
    if k > 0:
        cv.save(); cv.translate(540, 600); cv.scale(k, k); cv.rotate(-3)
        cv.drawRect(skia.Rect(-420, -170, 420, 170), fillp(CREAM)); cv.drawRect(skia.Rect(-420, -170, 420, 170), strokep(INK, 8))
        text(cv, '"THE LIMPING', 0, -20, 86, INK); text(cv, 'LADY"', 0, 100, 86, RED); cv.restore()

def shot_quote(cv, T):
    full(cv, C('#0e0a0a'))
    cv.drawRect(skia.Rect(-300, 900, W + 300, H + 300), fillp(shader=lin((0, 900), (0, H), [C('#2a1a18'), C('#0e0a0a')])))
    def sil(): character(cv, 'gest', 540, 1800, 150, t=T, expr='stern', pose={'hl': (0.3, 0.3), 'hr': (0.6, -0.3)})
    silhouette(cv, sil, glint=[(516, 1800 - 150 * 3.3), (564, 1800 - 150 * 3.3)])
    q = '"SHE IS THE MOST\nDANGEROUS OF ALL\nALLIED SPIES."'
    n = int(len(q) * clamp((T - 52.6) / 2.6))
    for i, ln in enumerate(q[:n].split('\n')): text(cv, ln, 540, 330 + i * 100, 74, CREAM if i != 1 else RED)
    tag(cv, 'GESTAPO OFFICER', 540, 1660, C('#3a3a40'), 40, k=pop(T, 52.3))

def shot_destroy(cv, T):
    desk_bg(cv)
    k = eout(clamp((T - 57.3) / 0.3))
    cv.save(); cv.translate(540, 900); cv.rotate(-4); cv.scale(k, k)
    cv.drawRect(skia.Rect(-330, -460, 330, 460), fillp(C('#d8c49a'))); cv.drawRect(skia.Rect(-330, -460, 330, 460), strokep(INK, 7))
    cv.drawRect(skia.Rect(-120, -500, 120, -460), fillp(C('#c8b080'))); cv.drawRect(skia.Rect(-120, -500, 120, -460), strokep(INK, 5))
    text(cv, 'FILE: "LA DAME', 0, -350, 46, INK); text(cv, 'QUI BOITE"', 0, -290, 46, INK)
    cv.save(); cv.clipRect(skia.Rect(-150, -230, 150, 110)); cv.drawRect(skia.Rect(-150, -230, 150, 110), fillp(C('#b8a880')))
    silhouette(cv, lambda: character(cv, 'vh_coat', 0, 400, 100, t=0)); cv.restore()
    for i in range(4): cv.drawLine(-260, 180 + i * 60, 220 - i * 40, 180 + i * 60, strokep(C('#6a6050'), 8))
    cv.restore()
    stamp(cv, 540, 1150, 'FIND & DESTROY', 92, RED, -12, k=pop(T, wt(8, 'find') - 0.1, 0.18))
    s = pop(T, wt(8, 'destroy') - 0.1, 0.18)
    if s > 0: cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(RED, alpha=0.18 * fadek(T, wt(8, 'destroy') + 0.1, 0.4)))

def shot_close(cv, T):
    lyon_room(cv, T, lamp=False)
    night_window(cv, 640, 420, 320, 460, T=T)
    door(cv, 80, 820, 300, 630, openf=0.0, col=C('#4a3a30'))
    kk = clamp((T - 60.6) / 0.6)
    cv.drawRect(skia.Rect(80, 1430, 380, 1450), fillp(C('#ffe0a0'), alpha=0.8))
    for i in range(2):
        x = 160 + i * 120 + math.sin(T * 6 + i) * 6
        cv.drawRect(skia.Rect(x, 1438, x + 50, 1450), fillp(C('#000000'), alpha=0.9 * kk))
    character(cv, 'vh_coat', lerp(560, 800, ease(clamp((T - 61.4) / 1.0))), 1720, 100, t=T, expr='shock', pose=limp(T, 6), look=(-0.7, 0))
    k = pop(T, 60.7, 0.2)
    if k > 0: text(cv, 'KNOCK KNOCK', 230, 760, 54 * k, RED, stroke=CREAM, sw=8, rot=-6)
    calendar(cv, 840, 300, 0.6, 'YEAR', '1942', C('#5a2a2a'), k=pop(T, wt(9, '1942') - 0.2), rot=4)
    tag(cv, 'ALMOST CAUGHT', 360, 300, RED, 50, k=pop(T, wt(9, 'almost') - 0.15))

def shot_climb(cv, T):
    mountains_snow(cv, T, dark=0.25)
    character(cv, 'guide', 760, 1420 - 0, 70, t=T, expr='stern', pose={'walk': 4}, look=(1, -0.3), blink_seed=3)
    character(cv, 'vh_coat', 420, 1560, 92, t=T, expr='strain', pose=limp(T, 3.2, 92), look=(1, -0.3))
    snowfall(cv, T, n=150, wind=420, a=0.85, size=(3, 8))
    tag(cv, 'ESCAPE ON FOOT', 540, 300, TEAL, 56, INK, k=pop(T, wt(9, 'escaped') - 0.2))

def shot_pyrenees(cv, T):
    europe_map(cv, T, occupied=1.0)
    for i in range(9):
        x = 160 + i * 65; y = 1090 + math.sin(i) * 14
        cv.drawPath(poly([(x - 50, y + 30), (x, y - 50), (x + 50, y + 30)]), fillp(C('#8a8478'))); cv.drawPath(poly([(x - 18, y - 22), (x, y - 50), (x + 18, y - 22)]), fillp(C('#ffffff')))
    map_arrow(cv, (520, 860), (360, 1300), k=clamp((T - 64.2) / 1.6), col=GOLD, w=16, bend=-40)
    text(cv, '~50 MILES', 760, 1240, 46, CREAM, stroke=INK, sw=8)
    tag(cv, 'THE PYRENEES', 540, 300, C('#3a5a7a'), 62, k=pop(T, wt(9, 'pyrenees') - 0.2))

def shot_legsnow(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#5a6a88'), C('#c8d4e4')])))
    cv.drawPath(poly([(-300, 1300), (1380, 1150), (1380, H + 300), (-300, H + 300)]), fillp(C('#f0f4fa')))
    cuthbert(cv, 520, 1420, 1.25, rot=-6)
    cv.drawPath(poly([(300, 1440), (700, 1400), (800, 1520), (250, 1560)]), fillp(C('#f4f8fc')))
    for i in range(5): cv.drawCircle(450 + i * 30, 1180 - i * 120, 10, fillp(C('#e8f4ff')))
    snowfall(cv, T, n=170, wind=500, a=0.9, size=(3, 9), seed=8)
    tag(cv, 'ON A PROSTHETIC LEG', 540, 320, TEAL, 52, INK, k=pop(T, wt(9, 'prosthetic') - 0.2))

def shot_message1(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#26304a'), C('#0e1220')])))
    snowfall(cv, T, n=70, wind=300, a=0.5, seed=2)
    radio_set(cv, 300, 1550, 0.65, T)
    character(cv, 'vh_coat', 760, 1760, 80, t=T, expr='strain', pose={'hl': (-0.7, -0.1)}, look=(-0.6, 0.3))
    telegram(cv, 540, 700, 'CUTHBERT IS\nGIVING ME\nTROUBLE.', T, wt(10, 'cuthbert') - 0.1, dur=1.4, head='TO: LONDON')
    tag(cv, 'RADIO MESSAGE', 540, 260, C('#2a6a4a'), 48, k=pop(T, wt(10, 'radioed') - 0.15))

def shot_london(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#4a4e58'), C('#22252c')])))
    window_back(cv, 140, 300, 320, 440)
    character(cv, 'official', 520, 1430, 100, t=T, expr='meh', pose={'hl': (0.2, -0.3), 'hr': (0.5, 0.1)}, look=(0, 0.4))
    table(cv, 540, 1330, 820, 120, 220, col=C('#5a3a28'))
    doc(cv, 780, 1240, 260, 180, rot=4, lines=3, title='CUTHBERT?', seed=9)
    for i in range(3):
        k = pop(T, 72.4 + i * 0.3)
        text(cv, '?', 420 + i * 120, 740 - (i % 2) * 70 + math.sin(T * 4 + i) * 8, 120 * k, GOLD, stroke=INK, sw=8)
    tag(cv, 'WHO IS CUTHBERT??', 540, 300, CREAM, 54, INK, k=pop(T, wt(11, 'knowing') - 0.2))

def shot_message2(cv, T):
    desk_bg(cv)
    telegram(cv, 540, 780, 'IF CUTHBERT\nTROUBLESOME,\nELIMINATE HIM.', T, wt(11, 'replied') - 0.05, dur=2.2, head='FROM: LONDON', rot=2)
    k = pop(T, wt(11, 'eliminate') - 0.1, 0.2)
    stamp(cv, 760, 1180, 'OFFICIAL', 60, C('#2a4a8a'), 10, k=k)
    cuthbert(cv, 200, 1760, 0.55, rot=lerp(0, -16, k))
    if k > 0:
        for i in range(3): cv.drawCircle(300 + i * 26, 1530 - i * 30, 10, fillp(TEAL))

def shot_quit(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#e8a060'), C('#3a2a3a')])))
    cv.drawCircle(540, 1100, 300, fillp(C('#ffd890'), alpha=0.7, blur=40))
    cv.drawRect(skia.Rect(-300, 1450, W + 300, H + 300), fillp(C('#2a2028')))
    def sil(): character(cv, 'vh_coat', 540, 1720, 130, t=T, expr='stern', pose={'hl': (-0.3, 0.9), 'hr': (0.3, 0.9)})
    silhouette(cv, sil)
    tag(cv, "SHE DIDN'T QUIT", 540, 320, GOLD, 64, INK, k=pop(T, wt(12, 'quit') - 0.2))

def shot_boat(cv, T):
    night_sky(cv, C('#04060e'), C('#1a2238'), h=1100, moon=(820, 260))
    waves(cv, T, y=1100, amp=30, col=C('#122030'))
    cv.drawPath(poly([(-300, 1150), (200, 1050), (500, 1110), (500, 1200), (-300, 1300)]), fillp(C('#1a1a14')))
    x = lerp(1000, 640, ease(clamp((T - 79.3) / 2.6)))
    cv.save(); cv.translate(x, 1260 + math.sin(T * 2) * 10); cv.rotate(math.sin(T * 1.6) * 3)
    cv.drawPath(poly([(-200, -20), (200, -20), (150, 60), (-150, 60)]), fillp(C('#3a2a1e'))); cv.drawPath(poly([(-200, -20), (200, -20), (150, 60), (-150, 60)]), strokep(INK, 6))
    cv.restore()
    def sil():
        character(cv, 'vh_coat', x - 60, 1250 + math.sin(T * 2) * 10, 60, t=T)
        character(cv, 'fighter1', x + 70, 1250 + math.sin(T * 2) * 10, 60, t=T, blink_seed=2)
    silhouette(cv, sil)
    calendar(cv, 300, 520, 0.7, 'YEAR', '1944', C('#2a4a3a'), k=pop(T, wt(12, '1944') - 0.25), rot=-4)
    tag(cv, 'BACK INTO FRANCE', 640, 820, CREAM, 48, INK, k=pop(T, wt(12, 'back') - 0.15))

def shot_disguise(cv, T):
    lyon_room(cv, T)
    cv.drawRoundRect(skia.Rect(560, 360, 960, 1000), 180, 180, fillp(C('#b8c8d4'))); cv.drawRoundRect(skia.Rect(560, 360, 960, 1000), 180, 180, strokep(C('#6a4a2a'), 18))
    sw = wt(13, 'grey') - 0.1
    nm = 'vh' if T < sw else 'vh_old'
    character(cv, nm, 360, 1720, 115, t=T, expr='neutral' if T < sw else 'smug', look=(0.7, 0))
    cv.save(); cv.clipRect(skia.Rect(580, 380, 940, 980))
    character(cv, nm, 760, 1000, 90, t=T, expr='neutral' if T < sw else 'smug', look=(-0.7, 0), flip=True)
    cv.restore()
    k = clamp(1 - abs(T - sw) / 0.35)
    if k > 0:
        rnd = random.Random(3)
        for i in range(14): cv.drawCircle(360 + rnd.uniform(-200, 200), 1300 + rnd.uniform(-300, 200), rnd.uniform(30, 70) * k, fillp(C('#f4f4f0'), alpha=0.85 * k))
    tag(cv, 'HAIR DYED GREY', 540, 260, C('#8a8a8a'), 52, k=pop(T, wt(13, 'grey') - 0.15))
    tag(cv, 'DISGUISED', 540, 380, C('#2a2a30'), 56, k=pop(T, wt(13, 'disguised') - 0.15))

def shot_farm(cv, T):
    countryside(cv, T)
    for i in range(7): cv.drawLine(80 + i * 140, 1200, 80 + i * 140, 1300, strokep(C('#6a4a2a'), 12))
    cv.drawLine(40, 1230, 1000, 1230, strokep(C('#6a4a2a'), 10)); cv.drawLine(40, 1270, 1000, 1270, strokep(C('#6a4a2a'), 10))
    cow(cv, 800, 1500, 1.1, T=T)
    x = lerp(220, 460, clamp((T - 85.6) / 3.2))
    character(cv, 'vh_old', x, 1750, 100, t=T, expr='neutral', pose={'walk': 2.4, 'hr': (0.3, 0.9)}, look=(1, 0))
    cv.save(); cv.translate(x + 70, 1520); cv.drawPath(poly([(-36, -50), (36, -50), (28, 30), (-28, 30)]), fillp(C('#9aa0aa'))); cv.drawPath(poly([(-36, -50), (36, -50), (28, 30), (-28, 30)]), strokep(INK, 5)); cv.restore()
    def g(): character(cv, 'gest', lerp(1100, 700, clamp((T - 86.5) / 2.4)), 1400, 60, t=T, pose={'walk': 4}, look=(-1, 0))
    silhouette(cv, g)
    tag(cv, 'OLD FARM WOMAN', 540, 300, C('#6a8a3a'), 56, k=pop(T, wt(13, 'farm') - 0.2))
    tag(cv, 'NO LIMP', 540, 420, CREAM, 46, INK, k=pop(T, wt(13, 'shuffling') - 0.15))

def shot_training(cv, T):
    woods(cv, T)
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#0a1420'), alpha=0.55))
    lantern(cv, 540, 1380, 1.0, T=T)
    spot(cv, 540, 1380, 600, 0.25, C('#ffcf80'))
    for i, (x, nm) in enumerate(((160, 'fighter1'), (330, 'fighter2'), (750, 'fighter2'), (920, 'fighter1'))):
        character(cv, nm, x, 1760, 75, t=T, expr='stern', look=(0.5 if x < 540 else -0.5, -0.1), blink_seed=i)
    character(cv, 'vh_old', 540, 1600, 85, t=T, expr='stern', pose={'hr': (0.8, -0.6)}, look=(0.3, 0))
    kh = pop(T, wt(14, 'hundreds') - 0.15, 0.3)
    if kh > 0: text(cv, 'HUNDREDS', 540, 420, 130 * kh, GOLD, stroke=INK, sw=12)
    tag(cv, 'RESISTANCE FIGHTERS TRAINED', 540, 560, CREAM, 42, INK, k=pop(T, wt(14, 'trained') - 0.15))

def shot_bridge(cv, T):
    b = wt(14, 'bridges') - 0.15
    night_sky(cv, C('#0a0a18'), C('#2a2238'), h=1200, moon=None)
    cv.drawRect(skia.Rect(-300, 1200, W + 300, H + 300), fillp(C('#14202a')))
    sh = math.sin(T * 60) * 10 * clamp(1 - (T - b) / 0.6) if T > b else 0
    cv.save(); cv.translate(sh, 0)
    for x in (180, 540, 900): cv.drawRect(skia.Rect(x - 40, 1000, x + 40, 1250), fillp(C('#4a4440'))); cv.drawRect(skia.Rect(x - 40, 1000, x + 40, 1250), strokep(INK, 5))
    if T < b + 0.1:
        cv.drawRect(skia.Rect(-100, 940, W + 100, 1010), fillp(C('#5a5450'))); cv.drawRect(skia.Rect(-100, 940, W + 100, 1010), strokep(INK, 6))
    else:
        f = ease(clamp((T - b) / 0.8))
        cv.drawRect(skia.Rect(-100, 940, 420, 1010), fillp(C('#5a5450')))
        cv.save(); cv.rotate(28 * f, 660, 1000); cv.drawRect(skia.Rect(660, 940 + f * 120, W + 100, 1010 + f * 120), fillp(C('#5a5450'))); cv.restore()
    cv.restore()
    if T > b:
        e = clamp((T - b) / 1.4)
        cv.drawCircle(540, 960, 120 + e * 500, fillp(C('#ffb040'), alpha=(1 - e) * 0.8, blur=60))
        cv.drawCircle(540, 960, 60 + e * 260, fillp(C('#fff0c0'), alpha=(1 - e), blur=30))
        rnd = random.Random(5)
        for i in range(14):
            a = rnd.uniform(-math.pi, 0); sp = rnd.uniform(300, 700)
            cv.drawRect(skia.Rect(540 + math.cos(a) * sp * e - 12, 960 + math.sin(a) * sp * e + 500 * e * e - 12, 540 + math.cos(a) * sp * e + 12, 960 + math.sin(a) * sp * e + 500 * e * e + 12), fillp(C('#2a2420')))
        cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#fff0c0'), alpha=0.5 * clamp(1 - (T - b) / 0.25)))
    tag(cv, 'BRIDGES DESTROYED', 540, 300, C('#e8742a'), 56, k=pop(T, wt(14, 'bridges') - 0.1))

def shot_dday(cv, T):
    europe_map(cv, T, occupied=1.0)
    for i in range(5):
        k = clamp((T - 92.7 - i * 0.2) / 0.8)
        map_arrow(cv, (330 + i * 30, 470), (300 + i * 60, 620), k=k, col=C('#3a7ad8'), w=14, bend=-20)
    for i in range(6): sparkle(cv, 260 + i * 50, 640 + math.sin(T * 5 + i) * 10, 22)
    tag(cv, 'ALLIED INVASION', 540, 1700, C('#3a7ad8'), 56, k=pop(T, wt(14, 'invasion') - 0.2))
    tag(cv, 'D-DAY • JUNE 1944', 540, 1820, CREAM, 42, INK, k=pop(T, wt(14, 'invasion') + 0.1))

def shot_civilian(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#1a1a2a'), C('#3a2a3a')])))
    cv.drawPath(poly([(440, -100), (640, -100), (900, 1760), (180, 1760)]), fillp(C('#fff2c8'), alpha=0.22, blur=20))
    cv.drawOval(skia.Rect(180, 1700, 900, 1820), fillp(C('#fff2c8'), alpha=0.3))
    character(cv, 'vh_coat', 540, 1760, 115, t=T, expr='neutral_smile', look=(0, -0.1))
    tag(cv, 'THE ONLY', 540, 300, CREAM, 56, INK, k=pop(T, wt(15, 'only') - 0.15))
    tag(cv, 'CIVILIAN WOMAN', 540, 420, GOLD, 60, INK, k=pop(T, wt(15, 'civilian') - 0.15))
    tag(cv, 'IN ALL OF WWII', 540, 540, C('#3a3a50'), 46, k=pop(T, wt(15, 'world') - 0.15))

def shot_medal(cv, T):
    dark_bg(cv, C('#2a3a6a'), C('#0a0e1a'))
    for i in range(14):
        a = i / 14 * math.tau + T * 0.2
        cv.drawPath(poly([(540, 900), (540 + math.cos(a) * 1600, 900 + math.sin(a) * 1600), (540 + math.cos(a + 0.12) * 1600, 900 + math.sin(a + 0.12) * 1600)]), fillp(C('#f8d880'), alpha=0.07))
    k = eout(clamp((T - 99.1) / 0.5))
    dsc_medal(cv, 540, lerp(1300, 1000, k), lerp(0.6, 1.5, k), T)
    particles(cv, T, 40, seed=7, col=C('#f8d880'))
    k2 = pop(T, wt(15, 'distinguished') - 0.15, 0.35)
    if k2 > 0:
        cv.save(); cv.translate(540, 330); cv.scale(k2, k2)
        cv.drawRoundRect(skia.Rect(-460, -120, 460, 120), 30, 30, fillp(C('#1f3a6a'))); cv.drawRoundRect(skia.Rect(-460, -120, 460, 120), 30, 30, strokep(GOLD, 8))
        text(cv, 'DISTINGUISHED', 0, -10, 70, GOLD); text(cv, 'SERVICE CROSS', 0, 70, 56, CREAM); cv.restore()

def shot_modest(cv, T):
    lyon_room(cv, T)
    character(cv, 'vh_old', 380, 1430, 95, t=T, expr='neutral_smile', pose={'hr': (0.7, 0.4)}, look=(0.5, 0.4))
    o = 1 - ease(clamp((T - 102.2) / 0.6))
    table(cv, 540, 1330, 820, 120, 220, col=C('#5a3a28'))
    cv.drawRect(skia.Rect(560, 1360, 900, 1460), fillp(C('#4a3020'))); cv.drawRect(skia.Rect(560, 1360, 900, 1460), strokep(INK, 5))
    if o > 0.05:
        cv.save(); cv.clipRect(skia.Rect(560, 1200, 900, 1360)); dsc_medal(cv, 720, 1360 + (1 - o) * 160, 0.35, T); cv.restore()
    tag(cv, 'NEVER BRAGGED', 540, 300, CREAM, 58, INK, k=pop(T, wt(16, 'bragged') - 0.2))

def shot_back(cv, T):
    full(cv, C('#0a0a10'))
    f = clamp((T - 103.3) / 1.6)
    lyon_street(cv, 0)
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#000000'), alpha=0.35 * (1 - f)))
    wanted_poster(cv, 840, 980, lerp(1.4, 0.62, ease(f)), 4)
    tag(cv, 'NEVER FORGOT HER', 540, 300, RED, 58, k=pop(T, wt(16, 'forgot') - 0.2) * fadek(T, 105.0, 0.2))
    end = TL['total']
    b = clamp((T - (end - 0.62)) / 0.6)
    if b > 0:
        surf = skia.Surface(W, H); c2 = surf.getCanvas(); shot_hook(c2, 0.0, frozen=True)
        p = skia.Paint(); p.setAlphaf(b)
        cv.save(); cv.resetMatrix(); cv.drawImage(surf.makeImageSnapshot(), 0, 0, skia.SamplingOptions(), p); cv.restore()

# ---- per-act colour grade + film grain + vignette ----
ACTS = [(0, C('#1a2a5a'), 0.10), (12.1, C('#8a5a2a'), 0.10), (30.3, C('#2a5a5a'), 0.08), (45.8, C('#6a1a1a'), 0.10),
        (62.4, C('#2a4a7a'), 0.10), (77.6, C('#8a5a2a'), 0.08), (82.1, C('#4a5a2a'), 0.08), (94.7, C('#8a6a1a'), 0.09), (103.2, C('#1a2a5a'), 0.10)]
def overlay(cv, T): grade(cv, T, ACTS)

def scenes():
    end = TL['total']
    Z = (1.0, 540, 960)
    def z(a, cx=540, cy=960): return (a, cx, cy)
    L = [
        (0.0, shot_hook, (Z, z(1.12, 560, 1100)), 'cut'),
        (4.15, shot_leg, (z(1.15, 540, 1000), z(1.0)), 'zoom'),
        (6.9, shot_name, (Z, z(1.08, 540, 900)), 'whip'),
        (9.3, shot_diplomat, (Z, z(1.1, 600, 800)), 'fade'),
        (12.15, shot_turkey, (z(1.0), z(1.25, 800, 800)), 'wipe'),
        (13.0, shot_hunt, (Z, z(1.1, 540, 1100)), 'cut'),
        (16.4, shot_hospital, (Z, z(1.08, 500, 1200)), 'flash'),
        (19.8, shot_prosthetic, (Z, z(1.1, 540, 1000)), 'zoom'),
        (21.6, shot_cuthbert, (Z, z(1.08, 600, 1000)), 'whip'),
        (24.0, shot_rejected, (z(1.15), Z), 'cut'),
        (26.9, shot_war, (Z, z(1.2, 700, 800)), 'wipe'),
        (28.7, shot_door, (Z, z(1.15, 540, 1000)), 'fade'),
        (30.35, shot_soe, (Z, z(1.08, 540, 1100)), 'flash'),
        (33.2, shot_1941, (Z, z(1.2, 450, 700)), 'wipe'),
        (34.9, shot_undercover, (z(1.15, 540, 1200), Z), 'whip'),
        (39.6, shot_network, (z(1.1), z(1.0)), 'zoom'),
        (42.3, shot_escape, (Z, z(1.08, 600, 1100)), 'cut'),
        (43.9, shot_radio, (Z, z(1.12, 500, 1100)), 'fade'),
        (45.8, shot_gestapo, (Z, z(1.1, 540, 1000)), 'flash'),
        (48.2, shot_posters, (z(1.0), z(1.12, 540, 1000)), 'cut'),
        (50.0, shot_limping, (Z, z(1.06)), 'whip'),
        (52.1, shot_quote, (Z, z(1.1, 540, 800)), 'fade'),
        (57.2, shot_destroy, (z(1.1), Z), 'cut'),
        (59.6, shot_close, (Z, z(1.1, 540, 1100)), 'whip'),
        (62.6, shot_climb, (Z, z(1.12, 560, 1200)), 'fade'),
        (64.3, shot_pyrenees, (Z, z(1.2, 450, 900)), 'wipe'),
        (66.3, shot_legsnow, (z(1.12, 540, 1200), Z), 'zoom'),
        (68.0, shot_message1, (Z, z(1.08, 540, 900)), 'cut'),
        (72.15, shot_london, (Z, z(1.1, 540, 1000)), 'whip'),
        (74.0, shot_message2, (Z, z(1.1, 540, 900)), 'cut'),
        (77.7, shot_quit, (z(1.15, 540, 1200), Z), 'flash'),
        (79.3, shot_boat, (Z, z(1.12, 640, 1100)), 'fade'),
        (82.2, shot_disguise, (Z, z(1.06)), 'wipe'),
        (85.5, shot_farm, (Z, z(1.1, 400, 1300)), 'whip'),
        (88.9, shot_training, (Z, z(1.08, 540, 1100)), 'fade'),
        (91.3, shot_bridge, (Z, z(1.08)), 'cut'),
        (93.0, shot_dday, (z(1.0), z(1.3, 360, 600)), 'wipe'),
        (94.75, shot_civilian, (Z, z(1.08, 540, 1100)), 'fade'),
        (99.1, shot_medal, (Z, z(1.08)), 'flash'),
        (101.6, shot_modest, (Z, z(1.08, 500, 1200)), 'whip'),
        (103.3, shot_back, (Z, Z), 'fade'),
    ]
    out = []
    for i, (s0, fn, cam, tr) in enumerate(L):
        s1 = L[i + 1][0] if i + 1 < len(L) else end
        out.append((s0, s1, fn, cam, tr))
    return out
