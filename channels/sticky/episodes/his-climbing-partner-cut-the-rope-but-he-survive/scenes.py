"""His Climbing Partner Cut the Rope… But He Survived — Joe Simpson (Siula Grande, Peru, June 1985).
Real people (Joe Simpson, Simon Yates) are plain stick figures with name cards. Non-graphic: the broken leg is an x-ray card,
the fall is a silhouette into darkness, no injuries shown."""
from core import *
from lib import _arm

STORM = C('#e2483b'); SNOWC = C('#f4f8fc'); ROPE = C('#e8c040'); ROPE2 = C('#e86a8a')

def namecard(cv, s, x, y, k, col=RED, size=78):
    if k <= 0: return
    f = skia.Font(skia.Typeface('Poppins', skia.FontStyle.Bold()), size); w = f.measureText(s)
    cv.save(); cv.translate(x, y); cv.scale(k, k)
    cv.drawRect(skia.Rect(-w / 2 - 50, -size * 0.95, w / 2 + 40, size * 0.5), fillp(CREAM)); cv.drawRect(skia.Rect(-w / 2 - 50, -size * 0.95, w / 2 + 40, size * 0.5), strokep(INK, 7))
    cv.drawRect(skia.Rect(-w / 2 - 50, -size * 0.95, -w / 2 - 22, size * 0.5), fillp(col))
    cv.drawString(s, -w / 2 + 6, 0, f, fillp(INK)); cv.restore()
def counter(cv, x, y, s, k=1.0, col=GOLD, size=120):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.scale(k, k)
    f = skia.Font(skia.Typeface('Poppins', skia.FontStyle.Bold()), size); w = f.measureText(s)
    cv.drawRoundRect(skia.Rect(-w / 2 - 40, -size, w / 2 + 40, size * 0.35), 30, 30, fillp(C('#14161e'))); cv.drawRoundRect(skia.Rect(-w / 2 - 40, -size, w / 2 + 40, size * 0.35), 30, 30, strokep(col, 8))
    cv.drawString(s, -w / 2, 0, f, fillp(col)); cv.restore()
def snow_seat(cv, x, y, T, slide=0.0, crumble=0.0):
    """Simon dug into a snow bucket seat on the slope; returns his waist point (rope anchor)."""
    p = poly([(x - 260, y + 40), (x - 220, y - 70), (x + 200, y - 30), (x + 300, y + 60), (x + 300, y + 200), (x - 260, y + 200)])
    cv.drawPath(p, fillp(C('#e8f0f8'))); cv.drawPath(p, strokep(INK, 5))
    if crumble > 0:
        rnd = random.Random(5)
        for i in range(int(14 * crumble)):
            bx = x + 120 + rnd.uniform(-60, 140); by = y + 20 + ((T * 260 + i * 60) % 260)
            cv.drawCircle(bx, by, rnd.uniform(8, 18), fillp(C('#f4f8fc'))); cv.drawCircle(bx, by, rnd.uniform(8, 18), strokep(C('#8aa0b8'), 3))
        for i in range(3):
            cv.drawPath(poly([(x - 80 + i * 70, y - 20), (x - 60 + i * 70, y + 20), (x - 90 + i * 70, y + 60)], close=False), strokep(C('#6a7a90'), 5, alpha=crumble))
    return (x + slide, y)

# ---------------------------------------------------------------- 0 hook: cliff, storm, the cut
def cliff_set(cv, t, dark=0.65):
    andes_sky(cv, dark=dark)
    snowfall(cv, t, 110, 520, seed=3, a=0.7)
    ice_wall(cv, 120, 820, 1000, 1700, t, seed=4, over=60)
    cv.drawRect(skia.Rect(-400, 1700, W + 400, H + 400), fillp(C('#04070e')))
    cv.drawPath(poly([(-400, 820), (1500, 820), (1500, 300), (900, 520), (500, 640), (-400, 700)]), fillp(C('#eef4fa')))
    cv.drawPath(poly([(-400, 700), (500, 640), (900, 520), (1500, 300)], close=False), strokep(INK, 6))
def shot_hook(cv, T, frozen=False):
    t = 0 if frozen else T
    cliff_set(cv, t)
    cut = wt(0, 'cut') + 0.15
    snapped = (not frozen) and T >= cut
    seat = snow_seat(cv, 300, 760, t)
    ch = character(cv, 'simon', 300, 780, 46, t=t, expr='strain', pose={'sit': True, 'hl': (0.55, 0.35), 'hr': (0.75, 0.2)}, look=(0.8, 0.5))
    lip = (760, 822)
    sway = math.sin(t * 1.3) * 18
    jx, jy = 640 + sway, 1240
    fall = 0 if not snapped else (T - cut) ** 2 * 1400
    if not snapped:
        rope(cv, [ch['hr'], lip, (jx + 20, jy - 300)], ROPE, 9)
    else:
        rope(cv, [ch['hr'], (ch['hr'][0] + 180, ch['hr'][1] + 30)], ROPE, 9)
        rope(cv, [lip, (jx + 20, jy - 300 + fall)], ROPE, 9)
    def joe(): character(cv, 'joe', jx, jy + fall, 52, t=t, expr='worried', pose={'hl': (0.1, -0.9), 'hr': (0.15, -0.95), 'dy': 0}, look=(0, -0.8))
    joe()
    if frozen: return
    knife(cv, ch['hr'][0] + 60, ch['hr'][1] - 30, 0.55, ang=-25, glint=pop(T, wt(0, 'cut') - 0.3, 0.3))
    if snapped:
        f = clamp(1 - (T - cut) / 0.35); cv.drawRect(skia.Rect(-400, -400, W + 400, H + 400), fillp(C('#ffffff'), alpha=f * 0.6))
    tag(cv, 'HIS PARTNER', 540, 300, CREAM, 54, INK, k=pop(T, wt(0, 'partner') - 0.15))
    tag(cv, 'CUT THE ROPE', 540, 430, RED, 66, k=pop(T, wt(0, 'cut') - 0.1))

def shot_dark(cv, T):
    crevasse_bg(cv, T, light=0.8)
    t0 = wt(0, 'fell'); k = clamp((T - t0 + 0.2) / 1.6)
    y = lerp(700, 1250, ease(k)); s = lerp(1.0, 0.45, ease(k))
    cv.drawRect(skia.Rect(-400, -400, W + 400, H + 400), fillp(C('#000000'), alpha=0.35 * k))
    character(cv, 'joe', 540, y, 60 * s, t=T, expr='shock', pose={'hl': (-0.9, -0.5), 'hr': (0.9, -0.5)})
    rope(cv, [(540, y - 200 * s), (560 + math.sin(T * 9) * 30, y - 600 * s)], ROPE, 7 * s + 2, alpha=1 - k * 0.6)
    for i in range(12):
        lx = 200 + i * 60; cv.drawLine(lx, (T * 1600 + i * 170) % 2000 - 100, lx, (T * 1600 + i * 170) % 2000 + 60, strokep(C('#9ad0f0'), 4, alpha=0.35))
    tag(cv, 'INTO THE DARK', 540, 1700, C('#1f2a44'), 58, CREAM, k=pop(T, wt(0, 'dark') - 0.15))

# ---------------------------------------------------------------- 1-2 who, where
def shot_peru(cv, T):
    peru_map(cv, T, pin=clamp((T - wt(1, 'peru') + 0.15) / 0.3))
    calendar(cv, 760, 470, 0.72, 'JUNE', '1985', C('#2a4aa0'), k=pop(T, wt(1, 'june') - 0.2, 0.3), rot=5)
    tag(cv, 'THE ANDES', 400, 1700, CREAM, 50, INK, k=pop(T, wt(1, 'peru') + 0.1))

def shot_names(cv, T):
    andes_sky(cv, 0.0); range_bg(cv, T, 0.0, 1300)
    snow_ground(cv, 1450)
    spot(cv, 540, 1200, 600, 0.2)
    character(cv, 'joe', 330, 1850, 92, t=T, expr='grin', pose={'hr': (0.6, -0.5)}, look=(0.4, -0.1), blink_seed=1)
    character(cv, 'simon', 760, 1850, 92, t=T, expr='smile', pose={'hl': (-0.4, 0.6)}, look=(-0.4, -0.1), blink_seed=2)
    ice_axe(cv, 870, 1650, 0.9, -15)
    tag(cv, 'TWO BRITISH CLIMBERS', 540, 300, C('#2a4aa0'), 50, k=pop(T, wt(1, 'british') - 0.15))
    namecard(cv, 'JOE SIMPSON', 330, 470, pop(T, wt(1, 'joe') - 0.15, 0.3), C('#d8743a'), 58)
    namecard(cv, 'SIMON YATES', 760, 600, pop(T, wt(1, 'simon') - 0.15, 0.3), C('#3a8a7a'), 58)

def shot_peak(cv, T):
    andes_sky(cv, 0.0, dusk=0.2)
    spot(cv, 840, 300, 300, 0.5, C('#fff4c0'))
    range_bg(cv, T, 0.0, 1500)
    peak(cv, 540, 1600, 1.15)
    cv.drawRect(skia.Rect(-400, 1560, W + 400, H + 400), fillp(C('#eef4fa')))
    k = clamp((T - lt0(2)) / 2.4)
    for i, nm in enumerate(('joe', 'simon')):         # two tiny climbers topping out
        y = lerp(760, 470, ease(k)) + i * 40; x = 540 - 30 + i * 50
        character(cv, nm, x, y, 13, t=T, pose={'walk': 6 if k < 1 else 0}, blink_seed=i)
    if k >= 1: sparkle(cv, 540, 430, 40 * (0.6 + 0.4 * math.sin(T * 6)))
    tag(cv, 'THE WEST FACE', 540, 300, CREAM, 54, INK, k=pop(T, wt(2, 'west') - 0.15))
    namecard(cv, 'SIULA GRANDE', 540, 1750, pop(T, wt(2, 'siula') - 0.15, 0.3), RED, 70)

def shot_altitude(cv, T):
    andes_sky(cv, 0.1)
    for i in range(7):        # cloud sea far below
        cx = (i * 220 + T * 30) % 1500 - 200; cv.drawCircle(cx, 1500, 200, fillp(C('#ffffff'), alpha=0.85)); cv.drawCircle(cx + 90, 1440, 150, fillp(C('#f4f8fc'), alpha=0.85))
    cv.drawPath(poly([(-100, 1200), (380, 760), (540, 700), (720, 790), (1200, 1300), (-100, 1300)]), fillp(SNOWC)); cv.drawPath(poly([(-100, 1200), (380, 760), (540, 700), (720, 790), (1200, 1300)], close=False), strokep(INK, 6))
    character(cv, 'joe', 470, 735, 34, t=T, expr='happy', pose={'hr': (0.4, -0.9)}, look=(0.3, -0.2))
    character(cv, 'simon', 600, 725, 34, t=T, expr='smile', pose={'hl': (-0.4, -0.9)}, look=(-0.3, -0.2), blink_seed=3)
    v = int(money(T, wt(2, 'over'), wt(2, 'feet') + 0.2, 0, 20814) / 10) * 10
    counter(cv, 540, 420, f'{v:,} FT', pop(T, wt(2, 'over') - 0.15, 0.3), GOLD, 110)
    tag(cv, 'OVER 20,000 FEET', 540, 1720, C('#2a4aa0'), 52, k=pop(T, wt(2, 'thousand') - 0.1))

# ---------------------------------------------------------------- 3-4 the fall, the knee
def shot_descent(cv, T):
    andes_sky(cv, 0.15, dusk=0.6)
    range_bg(cv, T, 0.2, 1350)
    cv.drawPath(poly([(-200, 900), (1300, 1500), (1300, H + 300), (-200, H + 300)]), fillp(SNOWC)); cv.drawLine(-200, 900, 1300, 1500, strokep(INK, 6))
    k = clamp((T - lt0(3)) / 1.6)
    for i, (nm, off) in enumerate((('simon', 0), ('joe', 260))):
        x = lerp(150, 520, k) + off; y = 900 + (x + 200) * 600 / 1500
        character(cv, nm, x, y, 46, t=T, expr='neutral', pose={'walk': 5}, look=(0.6, 0.3), facing=1, blink_seed=i)
    rope(cv, [(lerp(150, 520, k) + 20, 900 + (lerp(150, 520, k) + 220) * 0.4 - 120), (lerp(150, 520, k) + 240, 900 + (lerp(150, 520, k) + 460) * 0.4 - 120)], ROPE, 6, slack=0.6)
    tag(cv, 'THE WAY DOWN', 540, 320, CREAM, 56, INK, k=pop(T, wt(3, 'way') - 0.15))

def shot_slip(cv, T):
    andes_sky(cv, 0.2, dusk=0.5)
    ice_wall(cv, -100, 900, 560, 1300, T, seed=8)
    cv.drawRect(skia.Rect(-400, 1300, W + 400, H + 400), fillp(SNOWC)); cv.drawLine(-400, 1300, W + 400, 1300, strokep(INK, 6))
    t0 = wt(3, 'fell') - 0.1; k = clamp((T - t0) / 0.45)
    if T < t0:
        character(cv, 'joe', 420, 900, 50, t=T, expr='neutral', pose={'hr': (0.5, 0.2)}, look=(0.6, 0.4))
    else:
        x = lerp(420, 700, k); y = lerp(900, 1690, k * k)
        cv.save(); cv.rotate(lerp(0, 70, k), x, y - 150)
        character(cv, 'joe', x, y, 50, t=T, expr='shock', pose={'hl': (-0.9, -0.6), 'hr': (0.9, -0.6)}, look=(0, -0.5)); cv.restore()
        if k >= 1:
            cv.drawCircle(700, 1700, 120 * clamp((T - t0 - 0.45) / 0.2), strokep(C('#ffffff'), 10, alpha=1 - clamp((T - t0 - 0.45) / 0.5)))
    ice_axe(cv, 360 + (0 if T < t0 else (T - t0) * 500), 1000 - (0 if T < t0 else (T - t0) * 300), 0.7, -20 + (0 if T < t0 else (T - t0) * 400))
    tag(cv, 'JOE FELL', 540, 330, RED, 70, k=pop(T, wt(3, 'fell') - 0.1))

def shot_xray(cv, T):
    dark_bg(cv, C('#1a2a40'), C('#05080e'))
    crk = clamp((T - wt(3, 'broke') + 0.05) / 0.25)
    shake = 10 * math.sin(T * 60) * clamp(1 - (T - wt(3, 'broke')) / 0.4) if T > wt(3, 'broke') else 0
    bone_icon(cv, 540 + shake, 930, 1.35, crack=crk, k=eout(clamp((T - lt0(3) - 2.9) / 0.35)) if T < wt(3, 'leg') + 0.5 else 1.0)
    tag(cv, 'RIGHT LEG', 540, 330, CREAM, 56, INK, k=pop(T, wt(3, 'right') - 0.1))
    tag(cv, 'BROKEN AT THE KNEE', 540, 1700, RED, 54, k=pop(T, wt(3, 'knee') - 0.1))

def shot_sentence(cv, T):
    andes_sky(cv, 0.55, dusk=0.3)
    range_bg(cv, T, 0.6, 1300)
    snow_ground(cv, 1500, C('#c8d4e4'), C('#7a8aa4'))
    snowfall(cv, T, 60, 200, seed=8, a=0.5)
    character(cv, 'joe', 380, 1820, 70, t=T, expr='sad', pose={'sit': True, 'hl': (-0.2, 0.6), 'hr': (0.5, 0.6)}, look=(0.4, 0.2))
    character(cv, 'simon', 760, 1840, 76, t=T, expr='worried', pose={'hl': (-0.3, 0.7)}, look=(-0.7, 0.4), blink_seed=2)
    cv.drawRect(skia.Rect(-400, -400, W + 400, H + 400), fillp(C('#000010'), alpha=0.25))
    tag(cv, 'UP THERE...', 540, 330, CREAM, 56, INK, k=pop(T, wt(4, 'up') - 0.1))
    stamp(cv, 540, 520, 'DEATH SENTENCE', 74, RED, -8, k=pop(T, wt(4, 'death') - 0.1, 0.18))

# ---------------------------------------------------------------- 5 the lowering
def shot_knot(cv, T):
    desk_bg(cv, lamp=False) if False else dark_bg(cv, C('#2a3a54'), C('#0a0e18'))
    k = ease(clamp((T - wt(5, 'tied') + 0.1) / 0.6))
    rope(cv, [(-100, lerp(820, 960, k)), (lerp(380, 520, k), 960)], ROPE, 22)
    rope(cv, [(1180, lerp(1100, 960, k)), (lerp(700, 560, k), 960)], ROPE2, 22)
    if k >= 1:
        cv.drawOval(skia.Rect(470, 900, 610, 1020), fillp(ROPE)); cv.drawOval(skia.Rect(470, 900, 610, 1020), strokep(INK, 7))
        cv.drawPath(poly([(500, 930), (580, 990)], close=False), strokep(ROPE2, 16)); cv.drawPath(poly([(500, 990), (580, 930)], close=False), strokep(shade(ROPE, 0.7), 12))
    character(cv, 'simon', 820, 1640, 64, t=T, expr='stern', pose={'hl': (-0.6, -0.3)}, look=(-0.7, -0.4), blink_seed=4)
    tag(cv, 'TWO ROPES', 540, 330, GOLD, 64, INK, k=pop(T, wt(5, 'two') - 0.1))
    counter(cv, 540, 560, '2 x 150 FT', pop(T, wt(5, 'together') - 0.1), CREAM, 70)

def slope_y(x): return 300 + x * 0.95
def shot_lower(cv, T):
    andes_sky(cv, 0.3, dusk=0.3)
    cv.drawPath(poly([(-300, slope_y(-300)), (1400, slope_y(1400)), (1400, H + 300), (-300, H + 300)]), fillp(SNOWC)); cv.drawLine(-300, slope_y(-300), 1400, slope_y(1400), strokep(INK, 6))
    seat = snow_seat(cv, 230, slope_y(230) - 10, T)
    ch = character(cv, 'simon', 230, slope_y(230), 46, t=T, expr='strain', pose={'sit': True, 'hl': (0.5, 0.3), 'hr': (0.7, 0.4)}, look=(0.8, 0.6))
    k = clamp((T - wt(5, 'lowered')) / 3.4); x = lerp(330, 860, ease(k))
    cv.save(); cv.rotate(-35, x, slope_y(x))
    lying(cv, 'joe', x, slope_y(x) - 30, 40, T, expr='strain', look=(-0.6, 0.5)); cv.restore()
    rope(cv, [ch['hr'], (x - 20, slope_y(x) - 70)], ROPE, 7, slack=0.1)
    tag(cv, 'LOWERED HIM', 540, 330, CREAM, 56, INK, k=pop(T, wt(5, 'lowered') - 0.1))
    counter(cv, 700, 1720, '300 FT', pop(T, wt(5, 'three') - 0.15), GOLD, 90)

def shot_steps(cv, T):
    paper_bg(cv, C('#e6eef6'))
    prof = [(80, 360), (300, 560), (420, 820), (620, 1020), (760, 1300), (980, 1560)]
    cv.drawPath(poly(prof + [(1100, 1700), (1100, 1900), (-50, 1900), (-50, 360)]), fillp(C('#cfdcea'))); cv.drawPath(poly(prof, close=False), strokep(INK, 8))
    n = int(clamp((T - wt(5, 'three') + 0.3) / 1.8) * 5.999)
    for i in range(min(n, 5)):
        a, b = prof[i], prof[i + 1]
        map_arrow(cv, (a[0] + 30, a[1] - 30), (b[0] + 30, b[1] - 30), k=1.0, col=C('#e2483b'), w=12, bend=-40)
        text(cv, '300 FT', (a[0] + b[0]) / 2 + 130, (a[1] + b[1]) / 2 - 10, 40, C('#2a4aa0'))
    tag(cv, 'AGAIN AND AGAIN', 540, 300, C('#2a4aa0'), 56, k=pop(T, wt(5, 'at', 0) - 0.1))

# ---------------------------------------------------------------- 6-8 storm, ice cliff, hanging
def shot_storm(cv, T):
    storm_sky(cv, 1400)
    lit = pop(T, wt(6, 'storm') - 0.05, 0.12) * clamp(1 - (T - wt(6, 'storm')) / 0.5)
    if lit > 0: bolt(cv, 640, -50, 420, 900, seed=4, alpha=lit)
    range_bg(cv, T, 0.75, 1500)
    snow_ground(cv, 1550, C('#9aa8c0'), C('#4a5670'))
    snowfall(cv, T, 220, 900, seed=6, a=0.8)
    if lit > 0: cv.drawRect(skia.Rect(-400, -400, W + 400, H + 400), fillp(C('#ffffff'), alpha=lit * 0.35))
    tag(cv, 'A STORM HIT', 540, 330, STORM, 66, k=pop(T, wt(6, 'storm') - 0.05))

def shot_over(cv, T):
    andes_sky(cv, 0.7)
    snowfall(cv, T, 150, 800, seed=9, a=0.7)
    cv.drawPath(poly([(-400, 400), (700, 1000), (700, 1060), (-400, 1060)]), fillp(SNOWC)); cv.drawLine(-400, 400, 700, 1000, strokep(INK, 6))
    ice_wall(cv, 300, 1000, 700, 1900, T, seed=2, over=0)
    cv.drawRect(skia.Rect(700, 1000, W + 400, H + 400), fillp(C('#0a1020'), alpha=0.6))
    k = clamp((T - wt(6, 'lowered')) / 1.8)
    if k < 0.6:
        x = lerp(380, 690, k / 0.6); y = 400 + (x + 400) * 600 / 1100 - 30
        cv.save(); cv.rotate(-28, x, y); lying(cv, 'joe', x, y, 38, T, expr='worried', look=(0.6, 0.6)); cv.restore()
    else:
        f = (k - 0.6) / 0.4; x = 760; y = lerp(1000, 1500, ease(f))
        character(cv, 'joe', x, y, 40, t=T, expr='shock', pose={'hl': (0, -0.95), 'hr': (0.2, -0.9)}, look=(0, -0.7))
    rope(cv, [(-200, 290), (700, 1002), (760 if k >= 0.6 else 640, 1000 if k < 0.6 else lerp(1000, 1500, ease((k - 0.6) / 0.4)) - 260)], ROPE, 7)
    tag(cv, 'OVER AN ICE CLIFF', 540, 330, CREAM, 56, INK, k=pop(T, wt(6, 'cliff') - 0.2))

def shot_hanging(cv, T):
    andes_sky(cv, 0.8)
    snowfall(cv, T, 130, 700, seed=12, a=0.6)
    ice_wall(cv, -300, 300, 360, 1900, T, seed=5, over=-40)
    cv.drawRect(skia.Rect(-400, 1750, W + 400, H + 400), fillp(C('#03060c')))
    sw = math.sin(T * 1.6) * 9
    cv.save(); cv.rotate(sw, 640, -100)
    rope(cv, [(640, -200), (640, 900)], ROPE, 9)
    character(cv, 'joe', 640, 1380, 74, t=T, expr='worried', pose={'hl': (0.0, -0.95), 'hr': (0.15, -0.9)}, look=(-0.6, -0.2))
    cv.restore()
    tag(cv, 'IN MIDAIR', 540, 300, CREAM, 62, INK, k=pop(T, wt(7, 'midair') - 0.2))

def shot_unable(cv, T):
    andes_sky(cv, 0.85)
    snowfall(cv, T, 200, 1100, seed=13, a=0.75)
    ice_wall(cv, -300, -200, 250, 2200, T, seed=6)
    reach = 0.5 + 0.5 * math.sin(T * 3)
    rope(cv, [(700, -200), (700, 1000)], ROPE, 9)
    character(cv, 'joe', 700, 1500, 90, t=T, expr='strain', pose={'hl': (lerp(-0.6, -1.0, reach), -0.2), 'hr': (0.1, -0.95)}, look=(-1, 0))
    cv.drawLine(330, 1180, 440, 1180, strokep(C('#e2483b'), 8, alpha=0.8))
    for i in range(9):
        y = 300 + i * 150; x = (T * 1800 + i * 330) % 1600 - 300
        cv.drawLine(x, y, x + 260, y - 12, strokep(C('#ffffff'), 6, alpha=0.5))
    cross(cv, 820, 520, 70, k=pop(T, wt(7, 'hear') - 0.1)) if T > wt(7, 'hear') - 0.1 else None
    tag(cv, "CAN'T CLIMB", 540, 300, RED, 60, k=pop(T, wt(7, 'climb') - 0.15) * fadek(T, wt(7, 'unable', 1) - 0.05, 0.15))
    tag(cv, "CAN'T HEAR", 540, 300, C('#2a4aa0'), 60, k=pop(T, wt(7, 'hear') - 0.15))
    if T > wt(7, 'hear') - 0.2:
        cv.save(); cv.translate(820, 520)
        p = skia.Path(); p.moveTo(-20, -60); p.quadTo(50, -80, 50, -10); p.quadTo(50, 30, 10, 40); p.quadTo(0, 70, -25, 60)
        cv.drawPath(p, strokep(INK, 12)); cv.restore()

def shot_hour(cv, T):
    andes_sky(cv, 0.75)
    snowfall(cv, T, 160, 700, seed=14, a=0.7)
    cv.drawPath(poly([(-300, 900), (1400, 1300), (1400, H + 300), (-300, H + 300)]), fillp(C('#dde6f0'))); cv.drawLine(-300, 900, 1400, 1300, strokep(INK, 6))
    seat = snow_seat(cv, 420, 1010, T)
    ch = character(cv, 'simon', 420, 1030, 66, t=T, expr='strain', pose={'sit': True, 'hl': (0.6, 0.3), 'hr': (0.8, 0.25)}, look=(0.7, 0.5))
    rope(cv, [ch['hr'], (1300, 1290)], ROPE, 9)
    fr = clamp((T - wt(8, 'hour') + 0.3) / 3.0)
    hourglass(cv, 830, 560, 0.62, frac=fr, T=T)
    tag(cv, 'ABOUT AN HOUR', 400, 330, GOLD, 56, INK, k=pop(T, wt(8, 'hour') - 0.2))
    tag(cv, 'HOLDING ON', 540, 1740, CREAM, 52, INK, k=pop(T, wt(8, 'held') - 0.1))

def shot_giving(cv, T):
    andes_sky(cv, 0.8)
    snowfall(cv, T, 160, 800, seed=15, a=0.7)
    cr = clamp((T - wt(8, 'snow') + 0.1) / 0.8)
    sl = math.sin(T * 30) * 6 * cr + cr * 60
    cv.drawPath(poly([(-300, 1000), (1400, 1400), (1400, H + 300), (-300, H + 300)]), fillp(C('#dde6f0'))); cv.drawLine(-300, 1000, 1400, 1400, strokep(INK, 6))
    cv.save(); cv.translate(sl, sl * 0.25)
    seat = snow_seat(cv, 440, 1110, T, crumble=cr)
    ch = character(cv, 'simon', 440, 1130, 80, t=T, expr='shock', pose={'sit': True, 'hl': (0.6, 0.2), 'hr': (0.8, 0.2)}, look=(0.5, 0.7))
    cv.restore()
    rope(cv, [(ch['hr'][0] + sl, ch['hr'][1] + sl * 0.25), (1300, 1390)], ROPE, 10)
    tag(cv, 'THE SNOW GAVE WAY', 540, 330, RED, 54, k=pop(T, wt(8, 'gave') - 0.2))

# ---------------------------------------------------------------- 9 the knife
def shot_knife(cv, T):
    dark_bg(cv, C('#1e2a40'), C('#06080e'))
    snowfall(cv, T, 120, 900, seed=16, a=0.5)
    rope(cv, [(-100, 1040), (1180, 1000)], ROPE, 30)
    t0 = wt(9, 'knife') - 0.2; k = eout(clamp((T - t0) / 0.5))
    knife(cv, lerp(1100, 560, k), lerp(1500, 960, k), 1.5, ang=lerp(40, -10, k), glint=pop(T, wt(9, 'knife'), 0.3))
    cv.drawCircle(lerp(1180, 600, k), lerp(1560, 1020, k), 90, fillp(C('#3a8a7a'))) if False else None
    tag(cv, 'HIS KNIFE', 540, 330, CREAM, 62, INK, k=pop(T, wt(9, 'took') - 0.1))

def shot_cut(cv, T):
    dark_bg(cv, C('#1e2a40'), C('#06080e'))
    t0 = wt(9, 'cut') - 0.02; k = clamp((T - t0) / 0.6)
    if T < t0:
        rope(cv, [(-100, 1040), (1180, 1000)], ROPE, 30)
    else:
        rope(cv, [(-100, 1040), (lerp(520, 420, k), 1020 + 60 * k)], ROPE, 30)
        rope(cv, [(1180, 1000), (lerp(560, 760, k), 1020 + 500 * k * k)], ROPE, 30)
        for i in range(10):
            a = i / 10 * math.tau; r = 40 + 260 * eout(k)
            cv.drawLine(540 + math.cos(a) * r * 0.5, 1020 + math.sin(a) * r * 0.5, 540 + math.cos(a) * r, 1020 + math.sin(a) * r, strokep(C('#ffe04a'), 10, alpha=1 - k))
    knife(cv, 540, 940, 1.5, ang=-10 if T < t0 else lerp(-10, 20, k))
    k2 = pop(T, t0, 0.2)
    if k2 > 0:
        cv.save(); cv.translate(540, 470); cv.scale(k2, k2); cv.rotate(-6)
        star = [(math.cos(a / 16 * math.tau) * (260 if a % 2 == 0 else 170), math.sin(a / 16 * math.tau) * (160 if a % 2 == 0 else 105)) for a in range(16)]
        cv.drawPath(poly(star), fillp(C('#ffe04a'))); cv.drawPath(poly(star), strokep(INK, 7)); text(cv, 'SNAP', 0, 34, 104, RED); cv.restore()

# ---------------------------------------------------------------- 10 crevasse
def shot_fall2(cv, T):
    crevasse_bg(cv, T, light=0.7)
    t0 = lt0(10); k = clamp((T - t0) / 1.7)
    y = lerp(-100, 1250, k); spin = k * 200
    for i in range(14):
        lx = 260 + i * 40; yy = (T * 2400 + i * 230) % 2200 - 200
        cv.drawLine(lx, yy, lx, yy + 160, strokep(C('#cfefff'), 4, alpha=0.4))
    cv.save(); cv.rotate(spin, 540, y - 120)
    character(cv, 'joe', 540, y, 46, t=T, expr='shock', pose={'hl': (-0.9, -0.5), 'hr': (0.9, -0.5)}); cv.restore()
    rope(cv, [(540, y - 220), (540 + math.sin(T * 7) * 60, y - 700)], ROPE, 6)
    tag(cv, 'A DEEP CREVASSE', 540, 1720, C('#1f3a6a'), 56, CREAM, k=pop(T, wt(10, 'deep') - 0.15))

def shot_ledge(cv, T):
    crevasse_bg(cv, T, light=0.5)
    t0 = wt(10, 'landed') - 0.05; k = clamp((T - t0) / 0.25)
    ice_ledge(cv, 540, 1250, 560)
    if T < t0:
        character(cv, 'joe', 520, lerp(600, 1250, clamp((T - t0 + 0.4) / 0.4)), 60, t=T, expr='shock', pose={'hl': (-0.9, -0.5), 'hr': (0.9, -0.5)})
    else:
        lying(cv, 'joe', 470, 1240, 52, T, expr='sleep' if T < t0 + 0.6 else 'strain', look=(0, -0.4))
        r = 200 * eout(clamp((T - t0) / 0.4))
        for i in range(8):
            a = math.pi + i / 7 * math.pi; cv.drawLine(540 + math.cos(a) * r * 0.6, 1250 + math.sin(a) * r * 0.25, 540 + math.cos(a) * r * 1.6, 1250 + math.sin(a) * r * 0.6, strokep(C('#ffffff'), 8, alpha=1 - clamp((T - t0) / 0.5)))
    cv.drawRect(skia.Rect(-400, 1400, W + 400, H + 400), fillp(C('#000000'), alpha=0.6))
    tag(cv, 'A LEDGE OF ICE', 540, 330, C('#7ad7ff'), 60, INK, k=pop(T, wt(10, 'ledge') - 0.15))

# ---------------------------------------------------------------- 11 Simon alone
def shot_edge(cv, T):
    andes_sky(cv, 0.1, dusk=0.7)
    cv.drawRect(skia.Rect(-400, 1000, W + 400, H + 400), fillp(SNOWC)); cv.drawLine(-400, 1000, W + 400, 1000, strokep(INK, 6))
    cv.drawPath(poly([(380, 1150), (760, 1120), (680, 1400), (450, 1420)]), fillp(C('#0a1a30'))); cv.drawPath(poly([(380, 1150), (760, 1120), (680, 1400), (450, 1420)]), strokep(INK, 6))
    character(cv, 'simon', 860, 1160, 62, t=T, expr='sad', pose={'hl': (-0.4, 0.6)}, look=(-0.8, 0.8))
    rope(cv, [(800, 1060), (720, 1100), (640, 1124)], ROPE, 7)
    spot(cv, 840, 320, 300, 0.4, C('#ffd8a0'))
    tag(cv, 'THE NEXT DAY', 540, 330, CREAM, 56, INK, k=pop(T, wt(11, 'next') - 0.1))
    tag(cv, 'NO ANSWER', 540, 1720, C('#1f2a44'), 52, CREAM, k=pop(T, wt(11, 'believed') - 0.1))

def shot_alone(cv, T):
    andes_sky(cv, 0.25, dusk=0.8)
    range_bg(cv, T, 0.3, 1250)
    snow_ground(cv, 1300)
    k = clamp((T - wt(11, 'went') + 0.3) / 1.6)
    silhouette(cv, lambda: character(cv, 'simon', lerp(380, 700, k), 1500, 60, t=T, pose={'walk': 4}, facing=1))
    footprints = [(lerp(380, 700, k) - 80 - i * 70, 1505 + (i % 2) * 12) for i in range(int(k * 6) + 1)]
    for fx, fy in footprints: cv.drawOval(skia.Rect(fx - 16, fy - 8, fx + 16, fy + 8), fillp(C('#9aaac0')))
    tag(cv, 'ALONE', 540, 330, CREAM, 70, INK, k=pop(T, wt(11, 'alone') - 0.15))

# ---------------------------------------------------------------- 12 alive
def shot_alive(cv, T):
    full(cv, C('#020408'))
    k = pop(T, wt(12, 'alive') - 0.3, 0.3)
    spot(cv, 540, 900, 380, 0.25 * k, C('#7ad7ff'))
    eyes_dark(cv, 540, 900, 2.0, T, blink=True) if k > 0 else None
    tag(cv, 'BUT JOE WAS', 540, 380, CREAM, 56, INK, k=pop(T, wt(12, 'joe') - 0.1))
    tag(cv, 'ALIVE', 540, 1700, GREEN, 96, k=pop(T, wt(12, 'alive') - 0.1, 0.3))

def shot_deeper(cv, T):
    crevasse_bg(cv, T, light=0.35)
    k = clamp((T - wt(12, 'lowered') + 0.1) / 1.4)
    y = lerp(700, 1350, ease(k))
    rope(cv, [(540, -200), (540, y - 200)], ROPE, 7)
    character(cv, 'joe', 540, y, 56, t=T, expr='stern', pose={'hl': (0.0, -0.95), 'hr': (0.1, -0.6)}, look=(0, 0.8))
    map_arrow(cv, (820, 700), (820, 1300), k=pop(T, wt(12, 'deeper') - 0.2, 0.3), col=C('#e2483b'), w=18, bend=0)
    tag(cv, 'DEEPER, NOT UP', 540, 330, GOLD, 56, INK, k=pop(T, wt(12, 'deeper') - 0.15))

def shot_sunlight(cv, T):
    crevasse_bg(cv, T, light=1.0)
    k = clamp((T - wt(12, 'found') + 0.1) / 1.4)
    cv.drawPath(poly([(760, 200), (1000, 160), (900, 1400), (500, 1400)]), fillp(C('#fff2c0'), alpha=0.25 + 0.3 * k, blur=20))
    spot(cv, 840, 300, 260, 0.6 * k + 0.2, C('#fff4c0'))
    cv.drawPath(poly([(-100, 1500), (1180, 1100), (1180, H + 300), (-100, H + 300)]), fillp(C('#cfe6f5'))); cv.drawLine(-100, 1500, 1180, 1100, strokep(INK, 6))
    x = lerp(240, 700, ease(k)); y = 1500 - (x + 100) * 400 / 1280
    crawler(cv, 'joe', x, y, 44, T, speed=3, expr='strain', look=(0.8, -0.6))
    for i in range(5): sparkle(cv, 860 + math.sin(i * 2.1) * 120, 260 + i * 70, 24 * k, a=k)
    tag(cv, 'INTO THE SUNLIGHT', 540, 1730, GOLD, 56, INK, k=pop(T, wt(12, 'sunlight') - 0.2))

# ---------------------------------------------------------------- 13 the crawl
def shot_crawl(cv, T):
    andes_sky(cv, 0.0, dusk=0.3)
    range_bg(cv, T, 0.1, 1200)
    moraine(cv, T, 1150, seed=5)
    crawler(cv, 'joe', 300 + (T - lt0(13)) * 40, 1560, 56, T, speed=3.5, expr='strain', look=(1, 0.1))
    tag(cv, 'HE CRAWLED', 540, 330, CREAM, 64, INK, k=pop(T, wt(13, 'crawled') - 0.15))

def shot_days(cv, T):
    dark_bg(cv, C('#3a2a1a'), C('#0e0a06'))
    d = 1 + int(clamp((T - wt(13, 'three') + 0.4) / 0.6) * 2.999)
    for i in range(d):
        calendar(cv, 300 + i * 240, 900 + (i % 2) * 40, 0.5, 'DAY', str(i + 1), C('#8a5a2a'), k=pop(T, wt(13, 'three') - 0.4 + i * 0.2, 0.25), rot=-6 + i * 6)
    sun = (T * 2.4) % (2 * math.pi)
    cv.drawCircle(540 + math.cos(sun) * 360, 520 - abs(math.sin(sun)) * 120, 60, fillp(GOLD if math.sin(sun) > 0 else C('#dfe6ff')))
    tag(cv, 'ABOUT 3 DAYS', 540, 1720, GOLD, 60, INK, k=pop(T, wt(13, 'days') - 0.15))

def shot_route(cv, T):
    paper_bg(cv, C('#e9e2cc'))
    for i in range(7):
        cv.drawPath(poly([(i * 180 - 100, 640 + (i % 2) * 60), (i * 180 - 10, 380 + (i % 3) * 40), (i * 180 + 80, 640 + (i % 2) * 60)]), fillp(C('#c8bfa8'))); cv.drawPath(poly([(i * 180 - 100, 640 + (i % 2) * 60), (i * 180 - 10, 380 + (i % 3) * 40), (i * 180 + 80, 640 + (i % 2) * 60)]), strokep(INK, 4))
    pts = [(220, 760), (320, 900), (280, 1060), (460, 1180), (560, 1340), (720, 1400), (820, 1560)]
    k = clamp((T - wt(13, 'over') + 0.2) / 1.2); n = k * (len(pts) - 1)
    for i in range(int(n)):
        p = strokep(C('#e2483b'), 12); p.setPathEffect(skia.DashPathEffect.Make([24, 18], 0)); cv.drawLine(*pts[i], *pts[i + 1], p)
    text(cv, 'GLACIER', 220, 720, 34, INK); text(cv, 'CAMP', 840, 1640, 40, INK)
    tent(cv, 840, 1540, 0.3)
    counter(cv, 540, 360, '5+ MILES', pop(T, wt(13, 'miles') - 0.15), RED, 96)

def shot_empty(cv, T):
    moraine(cv, T, 900, seed=9, dark=0.2)
    andes_sky(cv, 0.0) if False else None
    cv.drawRect(skia.Rect(-400, -400, W + 400, 900), fillp(shader=lin((0, 0), (0, 900), [C('#d89a60'), C('#f4d8a8')])))
    cv.save(); cv.translate(380, 1200); cv.rotate(-70)
    cv.drawRoundRect(skia.Rect(-60, -160, 60, 160), 30, 30, fillp(C('#8ab0d0'))); cv.drawRoundRect(skia.Rect(-60, -160, 60, 160), 30, 30, strokep(INK, 7))
    cv.drawRect(skia.Rect(-30, -200, 30, -160), fillp(C('#3a3a44'))); cv.restore()
    for i in range(3): cv.drawCircle(560 + i * 40, 1240 - i * 10, 7, fillp(C('#8ab0d0'), alpha=0.5))
    crawler(cv, 'joe', 760, 1380, 50, T, speed=1.5, expr='sad', look=(-0.8, 0.5)) if False else character(cv, 'joe', 780, 1500, 64, t=T, expr='sad', pose={'sit': True, 'hl': (-0.6, 0.3)}, look=(-0.7, 0.4))
    tag(cv, 'NO FOOD', 330, 330, RED, 54, k=pop(T, wt(13, 'food') - 0.15))
    tag(cv, 'NO WATER', 720, 460, C('#2a4aa0'), 54, k=pop(T, wt(13, 'water') - 0.15))

# ---------------------------------------------------------------- 14-15 camp at night
def shot_camp(cv, T):
    night_sky(cv, h=1300, moon=(820, 300))
    moraine(cv, T, 1250, seed=11, dark=0.7)
    tent(cv, 760, 1420, 0.9, lit=False, col=C('#c08a30'))
    tent(cv, 420, 1380, 0.6, lit=False, col=C('#5a7aa0'))
    crawler(cv, 'joe', 120 + (T - lt0(14)) * 50, 1700, 50, T, speed=2.5, expr='strain', look=(1, -0.2))
    cv.drawRect(skia.Rect(-400, -400, W + 400, H + 400), fillp(C('#000010'), alpha=0.25))
    tag(cv, 'CAMP', 540, 330, GOLD, 62, INK, k=pop(T, wt(14, 'camp') - 0.15))
    clk = pop(T, wt(14, 'night') - 0.2)
    if clk > 0: wall_clock(cv, 860, 560, 90 * clk, 0.0)

def shot_leaving(cv, T):
    night_sky(cv, h=1300, moon=(220, 300), seed=3)
    moraine(cv, T, 1300, seed=12, dark=0.6)
    for i, (x, col) in enumerate(((330, C('#c86a3a')), (560, C('#3a6a8a')), (790, C('#6a8a3a')))):
        cv.drawRoundRect(skia.Rect(x - 70, 1380, x + 70, 1600), 30, 30, fillp(col)); cv.drawRoundRect(skia.Rect(x - 70, 1380, x + 70, 1600), 30, 30, strokep(INK, 6))
        cv.drawRoundRect(skia.Rect(x - 40, 1430, x + 40, 1500), 14, 14, strokep(INK, 5))
    stopwatch(cv, 540, 820, 170, clamp((T - wt(14, 'hours')) / 1.5) * 0.9, label=None)
    tag(cv, 'PACKED TO LEAVE', 540, 330, CREAM, 54, INK, k=pop(T, wt(14, 'others') - 0.2))
    tag(cv, 'HOURS TO SPARE', 540, 1730, RED, 54, k=pop(T, wt(14, 'hours') - 0.1))

def shot_wake(cv, T):
    full(cv, C('#0e0a10'))
    cv.drawPath(poly([(-200, 1700), (540, 300), (1280, 1700)]), fillp(C('#3a2a1a'))); cv.drawPath(poly([(-200, 1700), (540, 300), (1280, 1700)]), strokep(INK, 8))
    k = clamp((T - wt(15, 'woke') + 0.1) / 0.4)
    lying(cv, 'simon_bare', 300, 1120, 80, T, expr='sleep' if k < 0.5 else 'shock', look=(0.8, -0.6))
    cv.drawRoundRect(skia.Rect(-60, 1090, 360, 1280), 60, 60, fillp(C('#4a6a8a'))); cv.drawRoundRect(skia.Rect(-60, 1090, 360, 1280), 60, 60, strokep(INK, 6))
    v = pop(T, wt(15, 'voice') - 0.2)
    for i in range(3):
        r = 60 + i * 50 + (T * 80) % 50
        cv.drawArc(skia.Rect(980 - r, 700 - r, 980 + r, 700 + r), 150, 60, False, strokep(C('#fff2c8'), 8, alpha=0.6 * v * (1 - i * 0.25)))
    tag(cv, 'A WEAK VOICE', 540, 330, CREAM, 56, INK, k=pop(T, wt(15, 'weak') - 0.15))

def shot_found(cv, T):
    night_sky(cv, h=1300, moon=(860, 260), seed=4)
    moraine(cv, T, 1250, seed=13, dark=0.75)
    k = clamp((T - lt0(15) - 2.4) / 0.6)
    cv.drawPath(poly([(820, 1250), (180, 1500), (320, 1720)]), fillp(C('#fff2c0'), alpha=0.35 * k, blur=10))
    crawler(cv, 'joe', 300, 1640, 52, T, speed=0.8, expr='strain', look=(1, -0.3))
    character(cv, 'simon_bare', 840, 1300, 50, t=T, expr='shock', pose={'hl': (-0.8, -0.1)}, look=(-0.9, 0.5))
    cv.drawCircle(780, 1250, 16, fillp(C('#fff8d8')))
    tag(cv, 'CALLING HIS NAME', 540, 330, GOLD, 54, INK, k=pop(T, wt(15, 'calling') - 0.15))

# ---------------------------------------------------------------- 16-17 the right call, loop
def shot_call(cv, T):
    paper_bg(cv, C('#e8e2d4'))
    spot(cv, 540, 1100, 600, 0.25)
    character(cv, 'joe_bare', 340, 1850, 92, t=T, expr='neutral_smile', pose={'hr': (0.5, 0.3)}, look=(0.6, 0))
    character(cv, 'simon_bare', 760, 1850, 92, t=T, expr='neutral_smile', look=(-0.6, 0), blink_seed=5)
    tag(cv, 'JOE LATER SAID', 540, 300, CREAM, 52, INK, k=pop(T, wt(16, 'later') - 0.15))
    k = pop(T, wt(16, 'right') - 0.15, 0.3)
    if k > 0:
        cv.save(); cv.translate(540, 480); cv.scale(k, k)
        cv.drawRoundRect(skia.Rect(-420, -80, 420, 70), 30, 30, fillp(C('#1f3a6a'))); cv.drawRoundRect(skia.Rect(-420, -80, 420, 70), 30, 30, strokep(GOLD, 8))
        text(cv, 'THE RIGHT CALL', 0, 26, 70, GOLD); cv.restore()
        check(cv, 540, 660, k)

def shot_back(cv, T):
    dark_bg(cv, C('#1e2a40'), C('#06080e'))
    snowfall(cv, T, 120, 900, seed=16, a=0.5)
    rope(cv, [(-100, 1040), (1180, 1000)], ROPE, 30)
    knife(cv, 600, 960, 1.5, ang=-10, glint=pop(T, wt(17, 'moment') - 0.2, 0.3))
    tag(cv, 'IT ALL STARTED...', 540, 330, CREAM, 56, INK, k=pop(T, lt0(17)) * fadek(T, TL['total'] - 0.7, 0.2))
    end = TL['total']
    b = clamp((T - (end - 0.62)) / 0.6)
    if b > 0:
        surf = skia.Surface(W, H); c2 = surf.getCanvas(); shot_hook(c2, 0.0, frozen=True)
        p = skia.Paint(); p.setAlphaf(b)
        cv.save(); cv.resetMatrix(); cv.drawImage(surf.makeImageSnapshot(), 0, 0, skia.SamplingOptions(), p); cv.restore()

# ---- per-act colour grade + film grain + vignette ----
ACTS = [(0, C('#1a2a5a'), 0.10), (lt0(1), C('#8a6a2a'), 0.08), (lt0(3), C('#5a3a5a'), 0.08), (lt0(6), C('#1a2a4a'), 0.12),
        (lt0(10), C('#0a3a6a'), 0.10), (wt(12, 'found'), C('#8a6a1a'), 0.09), (lt0(14), C('#1a1a4a'), 0.10), (lt0(16), C('#8a5a2a'), 0.08),
        (lt0(17), C('#1a2a5a'), 0.10)]
def overlay(cv, T): grade(cv, T, ACTS)

def scenes():
    end = TL['total']
    Z = (1.0, 540, 960)
    def z(a, cx=540, cy=960): return (a, cx, cy)
    L = [
        (0.0, shot_hook, (Z, z(1.1, 520, 1000)), 'cut'),
        (wt(0, 'fell') - 0.25, shot_dark, (z(1.0), z(1.15, 540, 1100)), 'flash'),
        (lt0(1), shot_peru, (z(1.0), z(1.15, 460, 820)), 'whip'),
        (wt(1, 'two') - 0.1, shot_names, (Z, z(1.08, 540, 1000)), 'wipe'),
        (lt0(2), shot_peak, (z(1.0), z(1.15, 540, 900)), 'fade'),
        (wt(2, 'over') - 0.15, shot_altitude, (z(1.15, 540, 1000), Z), 'zoom'),
        (lt0(3), shot_descent, (Z, z(1.1, 600, 1100)), 'whip'),
        (wt(3, 'joe') - 0.15, shot_slip, (Z, z(1.12, 560, 1200)), 'cut'),
        (wt(3, 'his') - 0.1, shot_xray, (z(1.0), z(1.12)), 'flash'),
        (lt0(4), shot_sentence, (Z, z(1.1, 540, 1150)), 'fade'),
        (lt0(5), shot_knot, (z(1.1), Z), 'wipe'),
        (wt(5, 'and') - 0.1, shot_lower, (Z, z(1.12, 600, 1000)), 'whip'),
        (wt(5, 'three') - 0.15, shot_steps, (z(1.0), z(1.1, 540, 1000)), 'zoom'),
        (lt0(6), shot_storm, (Z, z(1.1, 540, 900)), 'flash'),
        (wt(6, 'and') - 0.1, shot_over, (Z, z(1.12, 640, 1000)), 'cut'),
        (lt0(7) - 0.2, shot_hanging, (z(1.15, 640, 1100), Z), 'fade'),
        (wt(7, 'unable') - 0.1, shot_unable, (Z, z(1.1, 600, 1000)), 'whip'),
        (lt0(8) - 0.2, shot_hour, (Z, z(1.1, 500, 1000)), 'wipe'),
        (wt(8, 'as') - 0.1, shot_giving, (z(1.05, 540, 960), z(1.12, 520, 1000)), 'cut'),
        (lt0(9) - 0.2, shot_knife, (Z, z(1.15, 600, 1000)), 'fade'),
        (wt(9, 'and') - 0.05, shot_cut, (z(1.15), z(1.05)), 'cut'),
        (lt0(10) - 0.15, shot_fall2, (Z, z(1.1, 540, 1100)), 'flash'),
        (wt(10, 'and') - 0.05, shot_ledge, (z(1.15, 540, 1150), Z), 'cut'),
        (lt0(11) - 0.2, shot_edge, (Z, z(1.12, 600, 1100)), 'fade'),
        (wt(11, 'and') - 0.05, shot_alone, (Z, z(1.08, 560, 1300)), 'wipe'),
        (lt0(12) - 0.2, shot_alive, (z(1.0), z(1.15)), 'cut'),
        (wt(12, 'he') - 0.1, shot_deeper, (Z, z(1.1, 540, 1100)), 'zoom'),
        (wt(12, 'and') - 0.1, shot_sunlight, (Z, z(1.12, 640, 900)), 'fade'),
        (lt0(13), shot_crawl, (Z, z(1.12, 500, 1300)), 'whip'),
        (wt(13, 'for') - 0.1, shot_days, (z(1.1), Z), 'zoom'),
        (wt(13, 'over') - 0.15, shot_route, (Z, z(1.1, 540, 1100)), 'wipe'),
        (wt(13, 'almost') - 0.15, shot_empty, (Z, z(1.1, 540, 1200)), 'cut'),
        (lt0(14) - 0.2, shot_camp, (Z, z(1.12, 500, 1200)), 'fade'),
        (wt(14, 'hours') - 0.15, shot_leaving, (z(1.1), Z), 'whip'),
        (lt0(15) - 0.2, shot_wake, (Z, z(1.1, 540, 1200)), 'cut'),
        (wt(15, 'calling') - 0.3, shot_found, (Z, z(1.12, 500, 1350)), 'zoom'),
        (lt0(16) - 0.2, shot_call, (Z, z(1.08, 540, 1000)), 'wipe'),
        (lt0(17) - 0.15, shot_back, (Z, Z), 'fade'),
    ]
    out = []
    for i, (s0, fn, cam, tr) in enumerate(L):
        s1 = L[i + 1][0] if i + 1 < len(L) else end
        out.append((s0, s1, fn, cam, tr))
    return out
