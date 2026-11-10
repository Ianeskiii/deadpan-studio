"""Example episode as delivered in the original session (kara-robinson). Shots, ACTS grade and scenes() list.
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

def shot_hook(cv, T, frozen=False):
    t = 0 if frozen else T
    apartment(cv, t, dark=0.55, lamp_on=True)
    character(cv, 'kara', 560, 1760, 105, t=t, expr='worried', pose={'sit': True}, look=(math.sin(t * 2.2) * 0.8, -0.2))
    bracket(cv, 780, 545, 380, 450, k=1.0 if frozen else clamp((T - 1.0) / 0.3), label='WINDOW')
    bracket(cv, 240, 1100, 320, 700, k=1.0 if frozen else clamp((T - 1.6) / 0.3), label='DOOR')
    if frozen: return
    bracket(cv, 800, 1060, 300, 220, k=clamp((T - 2.3) / 0.3), label='TV')
    tag(cv, 'TRAPPED', 540, 300, RED, 72, k=pop(T, wt(0, 'trapped') - 0.2))

def shot_panic(cv, T):
    dark_bg(cv, C('#2a2030'), C('#08060c'))
    spot(cv, 540, 960, 520, 0.25)
    cv.save(); cv.translate(540, 1050); cv.scale(2.3, 2.3); cv.translate(-540, -1050)
    character(cv, 'kara', 540, 1700, 110, t=T, expr='stern', look=(math.sin(T * 5) * 0.9, 0))
    cv.restore()
    k = pop(T, wt(0, 'panicking') - 0.2)
    if k > 0:
        cv.save(); cv.translate(540, 360); cv.scale(k, k)
        text(cv, 'PANIC', 0, 30, 120, CREAM, stroke=INK, sw=10)
        cv.drawLine(-200, 30, 200, -20, strokep(RED, 22)); cv.restore()

def shot_memorize(cv, T):
    full(cv, C('#0e1420'))
    for i in range(-2, 22): cv.drawLine(-300, i * 90, W + 300, i * 90, strokep(C('#16243a'), 2))
    for i in range(-2, 14): cv.drawLine(i * 90, -300, i * 90, H + 300, strokep(C('#16243a'), 2))
    cv.drawCircle(540, 1300, 230, fillp(C('#ff9fb0'), alpha=0.9)); cv.drawCircle(540, 1300, 230, strokep(INK, 8))
    brain_icon(cv, 540, 1300, 1.6)
    items = [('DOOR', 200, 500), ('WINDOW', 860, 520), ('LAMP', 180, 860), ('TV', 880, 880), ('BED', 540, 400)]
    for i, (n, x, y) in enumerate(items):
        t0 = 5.3 + i * 0.28; f = ease(clamp((T - t0) / 0.6))
        if T < t0: continue
        px, py = lerp(x, 540, f), lerp(y, 1300, f)
        tag(cv, n, px, py, CREAM, 44, INK, k=1 - f * 0.7)
    tag(cv, 'MEMORIZING EVERYTHING', 540, 1700, GREEN, 50, k=pop(T, wt(0, 'memorizing') - 0.2))

def shot_name(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (W, H), [C('#2a6a5a'), C('#0e2a2a')])))
    for i in range(14): cv.drawLine(-300, i * 160 - (T * 40 % 160), W + 300, i * 160 + 300 - (T * 40 % 160), strokep(C('#2e7a68'), 30, alpha=0.4))
    spot(cv, 540, 980, 520, 0.25)
    character(cv, 'kara', 540, 1700, 135, t=T, expr='smile', look=(0.1, -0.1))
    k = pop(T, wt(1, 'kara') - 0.2, 0.35)
    if k > 0:
        cv.save(); cv.translate(540, 360); cv.scale(k, k)
        cv.drawRect(skia.Rect(-430, -110, 430, 110), fillp(CREAM)); cv.drawRect(skia.Rect(-430, -110, 430, 110), strokep(INK, 7))
        cv.drawRect(skia.Rect(-430, -110, -400, 110), fillp(GREEN)); text(cv, 'KARA ROBINSON', 15, 30, 84, INK); cv.restore()
    tag(cv, 'AGE 15', 540, 560, GOLD, 50, INK, k=pop(T, 8.9))

def shot_date(cv, T):
    pos = us_map(cv, T)
    map_pin(cv, pos['SC'][0], pos['SC'][1] - 20, pop(T, wt(1, 'south') - 0.2))
    calendar(cv, 300, 420, 0.75, 'JUNE', '2002', C('#2a5a4a'), k=pop(T, wt(1, 'june') - 0.25, 0.3), rot=-4)

def shot_yard(cv, T):
    day_sky(cv, C('#6ab8f0'), C('#e8f4fa'), h=1300, sun=(860, 260))
    house_ext(cv, 560, 1280, 1.0, col=C('#c8a080'))
    cv.drawRect(skia.Rect(-300, 1280, W + 300, H + 300), fillp(C('#6aa85a')))
    flowers(cv, 40, 1040, 1380, T)
    character(cv, 'kara', 380, 1760, 100, t=T, expr='happy', pose={'hr': (0.7, 0.2)}, look=(0.6, 0.3))
    watering_can(cv, 560, 1440, 0.8, tilt=25, T=T)
    tag(cv, 'WATERING FLOWERS', 540, 300, GREEN, 54, k=pop(T, wt(1, 'watering') - 0.2))
    tag(cv, "A FRIEND'S FRONT YARD", 540, 420, CREAM, 44, INK, k=pop(T, wt(1, "friend's") - 0.15))

def shot_stranger(cv, T):
    day_sky(cv, C('#6ab8f0'), C('#e8f4fa'), h=1300, sun=(860, 260))
    cv.drawRect(skia.Rect(-300, 1280, W + 300, H + 300), fillp(C('#6aa85a')))
    flowers(cv, 40, 1040, 1380, T, seed=5)
    x = lerp(1150, 760, ease(clamp((T - 15.6) / 1.6)))
    def m():
        character(cv, 'evo', x, 1760, 105, t=T, expr='smile', pose={'walk': 5 if T < 17.2 else 0, 'hl': (-0.6, 0.0)})
    silhouette(cv, m)
    magazines(cv, x - 120, 1330, 0.7, -10)
    character(cv, 'kara', 300, 1760, 100, t=T, expr='neutral', look=(1, 0))
    tag(cv, 'A STRANGER', 540, 300, C('#3a3a40'), 56, k=pop(T, wt(2, 'man') - 0.15))
    tag(cv, '"SELLING MAGAZINES"', 540, 420, CREAM, 46, INK, k=pop(T, wt(2, 'magazines') - 0.2))

def shot_threat(cv, T):
    full(cv, C('#120608'))
    cv.drawCircle(540, 900, 900, fillp(C('#7a1418'), alpha=0.45, blur=200))
    # looming shadow
    cv.save(); cv.translate(780, 2000); cv.scale(2.4, 2.4); cv.translate(-780, -1800)
    evo_sil(cv, 780, 1800, 120, T)
    cv.restore()
    character(cv, 'kara', 380, 1760, 120, t=T, expr='shock', look=(0.8, -0.2))
    k = pop(T, wt(2, 'gun') - 0.15, 0.2)
    if k > 0: cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#ff2a2a'), alpha=0.35 * fadek(T, wt(2, 'gun'), 0.5)))
    tag(cv, 'A GUN TO HER NECK', 540, 320, RED, 58, k=k)

def shot_car(cv, T):
    day_sky(cv, C('#6ab8f0'), C('#e8f4fa'), h=1300, sun=(860, 260))
    house_ext(cv, 300, 1280, 0.8, col=C('#c8a080'))
    cv.drawRect(skia.Rect(-300, 1280, W + 300, 1500), fillp(C('#6aa85a')))
    cv.drawRect(skia.Rect(-300, 1500, W + 300, H + 300), fillp(C('#4a4c54')))
    flowers(cv, 20, 600, 1380, T, seed=5)
    watering_can(cv, 420, 1450, 0.7, tilt=95, T=T, flow=True)
    x = lerp(620, 1500, clamp((T - 21.4) / 1.2) ** 2)
    plain_car(cv, x, 1700, 1.2, col=C('#3a3e46'))
    tag(cv, 'FORCED INTO HIS CAR', 540, 300, RED, 52, k=pop(T, wt(3, 'forced') - 0.15))

def shot_tub(cv, T):
    full(cv, C('#0e0e12'))
    cv.drawRoundRect(skia.Rect(60, 700, 1020, 1400), 60, 60, fillp(C('#2a2a32'))); cv.drawRoundRect(skia.Rect(60, 700, 1020, 1400), 60, 60, strokep(INK, 10))
    cv.drawRect(skia.Rect(100, 740, 980, 1360), fillp(C('#1a1a20')))
    spot(cv, 540, 1100, 400, 0.18)
    lid = ease(clamp((T - wt(3, 'locked') + 0.1) / 0.5))
    tub(cv, 540, 1250, 1.3, lid=lid)
    if lid > 0.95:
        k = pop(T, wt(3, 'locked') + 0.4, 0.2)
        for sx in (-1, 1): cv.drawRoundRect(skia.Rect(540 + sx * 300 - 20, 960, 540 + sx * 300 + 20, 1040), 8, 8, fillp(C('#e8e0d0'), alpha=k))
    tag(cv, 'PLASTIC STORAGE TUB', 540, 400, CREAM, 50, INK, k=pop(T, wt(3, 'plastic') - 0.2))
    tag(cv, 'LOCKED INSIDE', 540, 520, RED, 52, k=pop(T, wt(3, 'locked') - 0.1))

def shot_drive(cv, T):
    road_night(cv, T, 1.0)
    apt_building(cv, lerp(1300, 760, ease(clamp((T - 25.8) / 1.6))), 1250, 0.7, T=T)
    plain_car(cv, 360, 1560, 1.0, col=C('#3a3e46'))
    cv.drawPath(poly([(650, 1500), (1300, 1380), (1300, 1660)]), fillp(C('#fff2b0'), alpha=0.25, blur=12))
    tag(cv, 'HIS APARTMENT', 540, 300, CREAM, 56, INK, k=pop(T, wt(4, 'apartment') - 0.2))

def shot_hours(cv, T):
    dark_bg(cv, C('#2a1a20'), C('#08060a'))
    f = clamp((T - 27.6) / 2.4)
    wall_clock(cv, 540, 900, 300, f * 18 * 3600 / 60)
    for i in range(8): cv.drawCircle(540 + math.cos(i / 8 * math.tau + T) * 400, 900 + math.sin(i / 8 * math.tau + T) * 400, 6, fillp(GOLD, alpha=0.6))
    n = int(f * 18)
    text(cv, f'{n} HOURS', 540, 360, 120, CREAM, stroke=INK, sw=10)
    tag(cv, 'HIS PRISONER', 540, 1700, RED, 56, k=pop(T, wt(4, 'prisoner') - 0.2))

def shot_decision(cv, T):
    apartment(cv, T, dark=0.75, lamp_on=False)
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#000000'), alpha=0.4))
    k = ease(clamp((T - wt(5, 'decision') + 0.3) / 0.4))
    spot(cv, 540, 1250, 420 * (0.4 + k * 0.6), 0.45 * k)
    character(cv, 'kara', 540, 1760, 120, t=T, expr='stern' if k > 0.5 else 'worried', look=(0, -0.1))
    tag(cv, 'SHE MADE A DECISION', 540, 320, GOLD, 56, INK, k=pop(T, wt(5, 'decision') - 0.2))

def shot_rules(cv, T):
    paper_bg(cv, C('#efe6d0'))
    for i in range(-2, 18): cv.drawLine(-300, 260 + i * 110, W + 300, 260 + i * 110, strokep(C('#a8c0d8'), 3, alpha=0.6))
    cv.drawLine(170, -300, 170, H + 300, strokep(C('#e28a8a'), 4))
    text(cv, 'THE PLAN', 560, 380, 90, INK)
    rows = [('STAY CALM', wt(5, 'calm')), ('ACT COOPERATIVE', wt(5, 'act')), ('STUDY EVERYTHING', wt(5, 'study'))]
    for i, (s_, t0) in enumerate(rows):
        y = 640 + i * 260
        if T >= t0 - 0.25:
            n = int(len(s_) * clamp((T - t0 + 0.25) / 0.45))
            text(cv, f'{i + 1}. ' + s_[:n], 210, y, 58, C('#2a3a6a'), align='left')
        check(cv, 970, y - 22, pop(T, t0 + 0.35, 0.2))

def shot_prints(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#1a1030'), C('#0a0818')])))
    cv.drawRect(skia.Rect(-300, 1300, W + 300, H + 300), fillp(C('#140c22')))
    cv.drawRoundRect(skia.Rect(120, 1100, 960, 1300), 20, 20, fillp(C('#2a1a3a'))); cv.drawRoundRect(skia.Rect(120, 1100, 960, 1300), 20, 20, strokep(C('#6a4a9a'), 6))
    cv.drawRect(skia.Rect(640, 300, 940, 900), strokep(C('#6a4a9a'), 6)); cv.drawCircle(680, 620, 14, fillp(C('#6a4a9a')))
    pts = [(260, 1180, -10), (480, 1220, 15), (760, 1170, -5), (720, 480, 20), (860, 700, -15), (200, 560, 8), (380, 820, -20), (880, 1240, 12)]
    for i, (x, y, r) in enumerate(pts):
        k = pop(T, 37.2 + i * 0.32, 0.25)
        fingerprint(cv, x, y, 0.9, k, col=C('#b88aff'), a=0.9, rot=r)
        if k > 0: cv.drawCircle(x, y, 120, fillp(C('#b88aff'), alpha=0.12 * k, blur=30))
    tag(cv, 'FINGERPRINTS', 540, 260, C('#8a5ad8'), 60, k=pop(T, wt(6, 'fingerprints') - 0.2))
    tag(cv, 'ON EVERY SURFACE', 540, 380, CREAM, 46, INK, k=pop(T, wt(6, 'surface') - 0.15))

def shot_proof(cv, T):
    desk_bg(cv)
    doc(cv, 540, 900, 640, 820, rot=2, lines=0, title='EVIDENCE', seed=2)
    fingerprint(cv, 540, 960, 2.2, 1.0, col=C('#3a3a48'), a=0.8)
    mx = 540 + math.sin(T * 1.4) * 140; my = 980 + math.cos(T * 1.1) * 80
    cv.drawCircle(mx, my, 160, fillp(C('#cfe8ff'), alpha=0.25)); cv.drawCircle(mx, my, 160, strokep(C('#2a2a30'), 20)); cv.drawLine(mx + 115, my + 115, mx + 240, my + 240, strokep(C('#3a2a1a'), 30))
    stamp(cv, 540, 1450, 'PROOF SHE WAS HERE', 62, RED, -8, k=pop(T, wt(6, 'proof') - 0.1, 0.2))
    tag(cv, "IF SHE DIDN'T SURVIVE…", 540, 300, CREAM, 48, INK, k=pop(T, wt(6, 'survive') - 0.3))

def shot_room(cv, T):
    apartment(cv, T, dark=0.3)
    character(cv, 'kara', 760, 1760, 95, t=T, expr='stern', pose={'sit': True}, look=(-0.7, -0.4))
    marks = [(780, 545, 380, 450, 'WINDOW', 43.4), (240, 1100, 320, 700, 'DOOR', 43.8), (500, 1020, 140, 140, 'LAMP', 44.75), (800, 1060, 300, 220, 'TV', 45.0), (230, 1560, 600, 220, 'BED', 45.25)]
    for x, y, w, h, n, t0 in marks: bracket(cv, x, y, w, h, k=clamp((T - t0) / 0.25), label=n)
    tag(cv, 'THE ROOM', 540, 260, GREEN, 54, k=pop(T, wt(7, 'room') - 0.2) * fadek(T, 44.6))
    tag(cv, 'THE OBJECTS', 540, 260, GREEN, 54, k=pop(T, wt(7, 'objects') - 0.15))

def shot_him(cv, T):
    full(cv, C('#0c1018'))
    for i in range(-2, 22): cv.drawLine(-300, i * 90, W + 300, i * 90, strokep(C('#141c2a'), 2))
    cv.drawRect(skia.Rect(140, 520, 620, 1240), fillp(C('#1a2230'))); cv.drawRect(skia.Rect(140, 520, 620, 1240), strokep(C('#7cf29a'), 5))
    cv.save(); cv.clipRect(skia.Rect(140, 520, 620, 1240)); evo_sil(cv, 380, 1480, 130, T); cv.restore()
    for i, (s_, t0) in enumerate((('FACE', 45.8), ('VOICE', 46.1), ('CAR', 46.4), ('HABITS', 46.7))):
        y = 620 + i * 160
        if T > t0:
            text(cv, s_, 680, y + 20, 56, C('#7cf29a'), font='Courier New', align='left')
            check(cv, 960, y, pop(T, t0 + 0.15, 0.2), s=0.8)
    yy = 520 + ((T * 400) % 720)
    cv.drawLine(140, yy, 620, yy, strokep(C('#7cf29a'), 4, alpha=0.7))
    tag(cv, 'EVERY DETAIL ABOUT HIM', 540, 300, C('#2a6a4a'), 50, k=pop(T, wt(7, 'every') - 0.2))

def shot_night(cv, T):
    night_sky(cv, C('#03050f'), C('#141c3a'), h=1500, moon=(700, 520))
    apt_building(cv, 540, 1600, 1.0, lit=[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], night=True)
    cv.drawRect(skia.Rect(-300, 1600, W + 300, H + 300), fillp(C('#0a0c12')))
    tag(cv, 'MIDDLE OF THE NIGHT', 540, 300, C('#2a3a6a'), 52, k=pop(T, wt(8, 'middle') - 0.2))

def shot_asleep(cv, T):
    apartment(cv, T, dark=0.85, lamp_on=False, tv=False)
    sleeper(cv, T, 230, 1500, 70)
    for i in range(3):
        f = ((T * 0.7 + i / 3) % 1)
        text(cv, 'Z', 380 + f * 120, 1300 - f * 260, 50 + i * 16, CREAM)
    character(cv, 'kara', 760, 1760, 100, t=T, expr='worried', pose={'sit': True}, look=(-0.9, 0))
    tag(cv, 'HE FELL ASLEEP', 540, 300, TEAL, 56, INK, k=pop(T, wt(8, 'asleep') - 0.2))

def shot_cuff(cv, T):
    dark_bg(cv, C('#1a2030'), C('#05060a'))
    spot(cv, 540, 1000, 500, 0.25, C('#cfe0ff'))
    o = ease(clamp((T - 51.2) / 0.7))
    handcuff(cv, 540, 1000, 1.6, open_=o, rot=-8)
    # hand silhouette sliding out of right cuff
    hx = 540 + 225 + o * 150
    cv.drawRoundRect(skia.Rect(hx - 60, 940, hx + 140, 1060), 50, 50, fillp(C('#f4f4f0'))); cv.drawRoundRect(skia.Rect(hx - 60, 940, hx + 140, 1060), 50, 50, strokep(INK, 7))
    for i in range(3):
        if o > 0.3: cv.drawLine(hx - 120 - i * 30, 920 + i * 60, hx - 200 - i * 30, 920 + i * 60, strokep(CREAM, 6, alpha=o))
    tag(cv, 'ONE HAND FREE', 540, 320, GOLD, 60, INK, k=pop(T, wt(9, 'hand') - 0.2))

def shot_sneak(cv, T):
    apartment(cv, T, dark=0.85, lamp_on=False, tv=False)
    sleeper(cv, T, 230, 1500, 70)
    x = lerp(860, 330, ease(clamp((T - 52.7) / 1.6)))
    character(cv, 'kara', x, 1760, 100, t=T, expr='strain', pose={'walk': 3}, look=(-1, 0))
    k = pop(T, wt(9, 'quietly') - 0.1)
    if k > 0: text(cv, 'shhh…', x, 1200, 60 * k, CREAM, rot=-6)
    tag(cv, 'QUIETLY', 540, 300, TEAL, 56, INK, k=k)

def shot_run(cv, T):
    full(cv, C('#fff4d8'))
    for i in range(16):
        a = i / 16 * math.tau
        cv.drawLine(540, 1000, 540 + math.cos(a) * 1500, 1000 + math.sin(a) * 1500, strokep(C('#ffe0a0'), 40, alpha=0.6))
    for i in range(10):
        y = 500 + i * 130; x = ((i * 290 + T * 2200) % 1500) - 200
        cv.drawLine(x, y, x - 260, y, strokep(C('#e8c890'), 10))
    character(cv, 'kara', 540, 1700, 120, t=T * 2, expr='strain', pose={'walk': 9, 'hl': (-0.6, -0.2), 'hr': (0.6, 0.2)}, look=(1, 0))
    tag(cv, 'RUN!', 540, 360, RED, 96, k=pop(T, wt(9, 'ran') - 0.15))

def shot_flag(cv, T):
    day_sky(cv, C('#e8a070'), C('#fff0d8'), h=1300, sun=(200, 700))
    apt_building(cv, 230, 1300, 0.6, night=False)
    cv.drawRect(skia.Rect(-300, 1300, W + 300, H + 300), fillp(C('#4a4c54')))
    for i in range(8): cv.drawRect(skia.Rect(-100 + i * 180, 1560, -20 + i * 180, 1580), fillp(C('#f4f4f0')))
    cx = lerp(1500, 760, eout(clamp((T - 55.9) / 1.4)))
    plain_car(cv, cx, 1650, 1.05, col=C('#c8483a'))
    character(cv, 'kara', 330, 1760, 100, t=T, expr='shock', pose={'hl': (-0.3, -1.0), 'hr': (0.4, -1.1)}, look=(1, -0.2))
    tag(cv, 'FLAGGED DOWN A CAR', 540, 300, GOLD, 52, INK, k=pop(T, wt(10, 'flagged') - 0.2))

def shot_station(cv, T):
    day_sky(cv, C('#5a9ad8'), C('#dff0fa'), h=1350, sun=None)
    cv.drawRect(skia.Rect(80, 600, 1000, 1350), fillp(C('#c8c0b0'))); cv.drawRect(skia.Rect(80, 600, 1000, 1350), strokep(INK, 8))
    cv.drawRect(skia.Rect(80, 600, 1000, 720), fillp(C('#2a3a6a'))); text(cv, 'POLICE', 540, 690, 80, CREAM)
    for c in range(4): cv.drawRect(skia.Rect(140 + c * 220, 800, 260 + c * 220, 960), fillp(C('#9ac8e8'))); cv.drawRect(skia.Rect(140 + c * 220, 800, 260 + c * 220, 960), strokep(INK, 5))
    cv.drawRect(skia.Rect(-300, 1350, W + 300, H + 300), fillp(C('#5a5c64')))
    x = lerp(-300, 560, eout(clamp((T - 57.6) / 1.2)))
    plain_car(cv, x, 1650, 1.0, col=C('#c8483a'))
    tag(cv, 'RUSHED TO POLICE', 540, 300, C('#2a3a6a'), 54, k=pop(T, wt(10, 'rushed') - 0.2))

def shot_interview(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#5a6470'), C('#2a3038')])))
    cv.drawRect(skia.Rect(-300, 1450, W + 300, H + 300), fillp(C('#3a3e46')))
    character(cv, 'kara', 260, 1430, 95, t=T, expr='stern', pose={'hr': (0.8, 0.0)}, look=(0.8, 0))
    character(cv, 'cop', 820, 1430, 100, t=T, expr='shock', pose={'hl': (-0.5, 0.3)}, look=(-0.8, 0))
    table(cv, 540, 1330, 820, 120, 220, col=C('#6a6a72'))
    doc(cv, 700, 1250, 220, 160, rot=-6, lines=3, seed=4)
    tag(cv, 'WHAT HAPPENED', 540, 300, CREAM, 52, INK, k=pop(T, wt(11, 'happened') - 0.2) * fadek(T, 61.4))

def shot_where(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#e8e2d4')))
    for i in range(-2, 14):
        cv.drawRect(skia.Rect(i * 180 - 20, -300, i * 180 + 20, H + 300), fillp(C('#ffffff'))); cv.drawRect(skia.Rect(-300, i * 220 - 20, W + 300, i * 220 + 20), fillp(C('#ffffff')))
    rnd = random.Random(5)
    for i in range(-1, 7):
        for j in range(-1, 10):
            cv.drawRect(skia.Rect(i * 180 + 30, j * 220 + 30, i * 180 + 150, j * 220 + 190), fillp(C('#c8d8c0') if rnd.random() < 0.3 else C('#d8d0c0')))
    route = skia.Path(); route.moveTo(180, 1760); route.lineTo(180, 1320); route.lineTo(540, 1320); route.lineTo(540, 880); route.lineTo(900, 880); route.lineTo(900, 640)
    meas = skia.PathMeasure(route, False); Lr = meas.getLength(); seg = skia.Path(); meas.getSegment(0, Lr * clamp((T - 61.6) / 1.4), seg, True)
    cv.drawPath(seg, strokep(INK, 26)); cv.drawPath(seg, strokep(RED, 16))
    apt_building(cv, 900, 640, 0.32, night=False)
    map_pin(cv, 900, 470, pop(T, wt(11, 'exactly') - 0.1))
    tag(cv, 'EXACTLY WHERE', 540, 300, RED, 60, k=pop(T, wt(11, 'exactly') - 0.2))

def shot_raid(cv, T):
    road_night(cv, T, 1.6)
    for i in range(2): police_car(cv, 300 + i * 480, 1600 - i * 40, 0.9 - i * 0.1, T)
    siren_glow(cv, T)
    tag(cv, 'POLICE RACED IN', 540, 300, C('#2a3a6a'), 56, k=pop(T, wt(12, 'raced') - 0.2))

def shot_gone(cv, T):
    apartment(cv, T, dark=0.4, door_open=1.0, lamp_on=False, empty=True)
    cv.drawPath(poly([(110, 1450), (370, 1450), (560, 1900), (-60, 1900)]), fillp(C('#fff2c8'), alpha=0.3))
    for i, x in enumerate((180, 320)): character(cv, 'cop', x, 1760, 95, t=T, expr='shock', look=(1, 0), blink_seed=i)
    k = pop(T, wt(12, 'gone') - 0.15)
    tag(cv, 'GONE', 540, 320, RED, 90, k=k)
    siren_glow(cv, T, a=0.2)

def shot_evo(cv, T):
    full(cv, C('#16161c'))
    for i in range(8):
        y = 500 + i * 130; cv.drawLine(150, y, 930, y, strokep(C('#3a3a44'), 4)); text(cv, f"{6 + i * 0.5:.1f}'" if i % 2 == 0 else '', 110, y + 14, 30, C('#6a6a74'))
    evo_sil(cv, 540, 1600, 145, T, expr='neutral')
    k = pop(T, wt(13, 'richard') - 0.2, 0.3)
    if k > 0:
        cv.save(); cv.translate(540, 1690); cv.scale(k, k)
        cv.drawRect(skia.Rect(-400, -70, 400, 70), fillp(CREAM)); cv.drawRect(skia.Rect(-400, -70, 400, 70), strokep(INK, 7))
        text(cv, 'RICHARD EVONITZ', 0, 22, 66, INK); cv.restore()
    tag(cv, 'THE KIDNAPPER', 540, 300, RED, 56, k=pop(T, wt(13, 'name') - 0.2))

def shot_florida(cv, T):
    pos = us_map(cv, T)
    map_pin(cv, pos['SC'][0], pos['SC'][1] - 10, 1.0, col=C('#3a3a40'))
    map_arrow(cv, pos['SC'], (pos['FL'][0] + 60, pos['FL'][1] + 80), k=clamp((T - 70.2) / 1.4), col=RED, w=16, bend=-60)
    calendar(cv, 780, 560, 0.65, '+3 DAYS', 'JUN 27', C('#5a2a2a'), k=pop(T, wt(13, 'three') - 0.2), rot=4)

def shot_chase(cv, T):
    road_night(cv, T, 2.6)
    plain_car(cv, 760 + math.sin(T * 9) * 10, 1620, 0.9, col=C('#3a3e46'))
    police_car(cv, 260 + math.sin(T * 7) * 12, 1640, 0.85, T)
    for i in range(12):
        y = 1400 + i * 30; x = ((i * 233 + T * 3000) % 1500) - 200
        cv.drawLine(x, y, x - 300, y, strokep(C('#ffffff'), 4, alpha=0.4))
    siren_glow(cv, T, a=0.25)
    tag(cv, 'HIGH-SPEED CHASE', 540, 300, RED, 56, k=pop(T, wt(13, 'chased') - 0.2))

def shot_end(cv, T):
    road_night(cv, T, 0.0)
    for i in range(3): police_car(cv, 200 + i * 340, 1640 - (i % 2) * 40, 0.75, T)
    siren_glow(cv, T, a=0.22)
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#000000'), alpha=0.25))
    tag(cv, 'THE CHASE WAS OVER', 540, 300, CREAM, 52, INK, k=pop(T, wt(13, 'chase', 1) - 0.2))

def shot_search(cv, T):
    apartment(cv, T, dark=0.7, lamp_on=False, empty=True, door_open=1.0)
    for i, (x, nm) in enumerate(((320, 'inv'), (760, 'inv2'))):
        character(cv, nm, x, 1760, 95, t=T, expr='stern', pose={'hr': (0.7, -0.3)}, look=(0.5 if i == 0 else -0.5, -0.2), blink_seed=i)
        a = math.sin(T * 1.3 + i * 2) * 0.6
        beam(cv, x + 110, 1340, x + 110 + math.cos(a - 0.6) * 700, 1340 + math.sin(a - 0.6) * 700, w=0.22, a=80)
    tag(cv, 'INVESTIGATORS', 540, 300, C('#2a3a5a'), 56, k=pop(T, wt(14, 'investigators') - 0.2))

def shot_box(cv, T):
    full(cv, C('#0a0a0e'))
    o = ease(clamp((T - 76.9) / 0.7))
    cv.drawCircle(540, 1150, 600 * o + 1, fillp(C('#fff2c8'), alpha=0.35 * o, blur=120))
    cv.drawRect(skia.Rect(240, 1150, 840, 1550), fillp(C('#a07a48'))); cv.drawRect(skia.Rect(240, 1150, 840, 1550), strokep(INK, 8))
    text(cv, 'EVIDENCE', 540, 1380, 64, INK)
    cv.save(); cv.rotate(-150 * o, 240, 1150); cv.drawRect(skia.Rect(240, 1100, 840, 1150), fillp(C('#8a6a3a'))); cv.drawRect(skia.Rect(240, 1100, 840, 1150), strokep(INK, 7)); cv.restore()
    for i in range(4):
        k = clamp((T - 77.2 - i * 0.15) / 0.5)
        if k > 0: doc(cv, 400 + i * 90, 1150 - k * 420, 200, 260, rot=(i - 1.5) * 10, lines=4, seed=i, k=1)
    tag(cv, 'A HORRIFYING DISCOVERY', 540, 300, RED, 50, k=pop(T, wt(14, 'horrifying') - 0.2))

def shot_board(cv, T):
    pos = us_map(cv, T)
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#0a0a10'), alpha=0.25))
    map_pin(cv, pos['VA'][0], pos['VA'][1] - 10, pop(T, wt(15, 'virginia') - 0.2))
    map_pin(cv, pos['SC'][0], pos['SC'][1] - 10, 1.0, col=C('#3a3a40'))
    map_arrow(cv, pos['SC'], pos['VA'], k=clamp((T - 79.3) / 1.0), col=GOLD, w=12, bend=-100)
    k = pop(T, wt(15, 'three') - 0.2, 0.35)
    if k > 0:
        cv.save(); cv.translate(540, 1660); cv.scale(k, k)
        cv.drawRoundRect(skia.Rect(-360, -230, 360, 230), 30, 30, fillp(C('#14141a'), alpha=0.85))
        for i in range(3): candle(cv, -200 + i * 200, 100, 140, T=T, seed=i)
        text(cv, '3 GIRLS', 0, -140, 64, CREAM); cv.restore()
    tag(cv, 'LINKED TO MURDERS', 540, 300, RED, 54, k=pop(T, wt(15, 'linked') - 0.2))

def shot_cold(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#2a3a5a'), C('#0e1420')])))
    snowfall(cv, T, n=80, wind=60, a=0.6, seed=3)
    for i in range(3): case_file(cv, 280 + i * 260, 1000 + (i % 2) * 120, 0.7, rot=(i - 1) * 7, label='1996' if i == 0 else '1997', k=pop(T, 82.4 + i * 0.2), frost=clamp((T - 83.2) / 1.0))
    tag(cv, 'YEARS EARLIER', 540, 300, CREAM, 52, INK, k=pop(T, wt(15, 'years') - 0.2) * fadek(T, 83.2))
    tag(cv, 'COLD CASES', 540, 300, TEAL, 64, INK, k=pop(T, wt(15, 'cases') - 0.15))

def shot_saved(cv, T):
    day_sky(cv, C('#f0a060'), C('#fff0d0'), h=1450, sun=(540, 1200))
    cv.drawCircle(540, 1200, 240, fillp(C('#ffe8a0'), alpha=0.8, blur=40))
    cv.drawRect(skia.Rect(-300, 1450, W + 300, H + 300), fillp(C('#5a6a4a')))
    character(cv, 'kara', 540, 1760, 125, t=T, expr='smile', look=(0, -0.2))
    tag(cv, 'SHE SAVED HERSELF', 540, 300, GOLD, 58, INK, k=pop(T, wt(16, 'save') - 0.2))

def shot_solved(cv, T):
    desk_bg(cv)
    for i in range(3):
        case_file(cv, 280 + i * 260, 1000 + (i % 2) * 120, 0.7, rot=(i - 1) * 7, label='1996' if i == 0 else '1997')
        stamp(cv, 280 + i * 260, 1060 + (i % 2) * 120, 'SOLVED', 64, GREEN, -14 + i * 6, k=pop(T, wt(16, 'solved') - 0.1 + i * 0.25, 0.18))
    tag(cv, "A SERIAL KILLER'S CRIMES", 540, 300, RED, 50, k=pop(T, wt(16, 'serial') - 0.2))

def shot_back(cv, T):
    apartment(cv, T, dark=0.55 * clamp((T - 89.3) / 0.8) + 0.2, lamp_on=True)
    character(cv, 'kara', 560, 1760, 105, t=T, expr='worried', pose={'sit': True}, look=(math.sin(T * 2.2) * 0.8, -0.2))
    tag(cv, 'IT ALL STARTED…', 540, 300, CREAM, 56, INK, k=pop(T, wt(16, 'happened') - 0.2) * fadek(T, 90.4, 0.2))
    end = TL['total']
    b = clamp((T - (end - 0.62)) / 0.6)
    if b > 0:
        surf = skia.Surface(W, H); c2 = surf.getCanvas(); shot_hook(c2, 0.0, frozen=True)
        p = skia.Paint(); p.setAlphaf(b)
        cv.save(); cv.resetMatrix(); cv.drawImage(surf.makeImageSnapshot(), 0, 0, skia.SamplingOptions(), p); cv.restore()

ACTS = [(0, C('#1a2a5a'), 0.10), (12.6, C('#8a6a2a'), 0.07), (18.4, C('#6a1a1a'), 0.10), (30.8, C('#2a5a5a'), 0.08),
        (47.4, C('#1a2a6a'), 0.12), (55.2, C('#8a6a2a'), 0.06), (64.0, C('#1a2a5a'), 0.10), (74.3, C('#3a3a4a'), 0.10),
        (84.9, C('#8a6a1a'), 0.08), (89.3, C('#1a2a5a'), 0.10)]
def overlay(cv, T): grade(cv, T, ACTS)

def scenes():
    end = TL['total']
    Z = (1.0, 540, 960)
    def z(a, cx=540, cy=960): return (a, cx, cy)
    L = [
        (0.0, shot_hook, (Z, z(1.12, 560, 1150)), 'cut'),
        (3.6, shot_panic, (Z, z(1.06)), 'zoom'),
        (5.1, shot_memorize, (z(1.1), Z), 'whip'),
        (7.6, shot_name, (Z, z(1.08, 540, 900)), 'flash'),
        (9.8, shot_date, (Z, z(1.2, 520, 950)), 'wipe'),
        (12.65, shot_yard, (Z, z(1.08, 460, 1300)), 'fade'),
        (15.5, shot_stranger, (Z, z(1.08, 600, 1250)), 'whip'),
        (18.45, shot_threat, (z(1.12, 400, 1200), Z), 'flash'),
        (20.85, shot_car, (Z, z(1.06)), 'cut'),
        (22.55, shot_tub, (Z, z(1.12, 540, 1100)), 'zoom'),
        (25.7, shot_drive, (Z, z(1.08, 640, 1300)), 'wipe'),
        (27.4, shot_hours, (Z, z(1.1)), 'fade'),
        (30.8, shot_decision, (Z, z(1.15, 540, 1250)), 'fade'),
        (32.55, shot_rules, (Z, z(1.05)), 'whip'),
        (36.95, shot_prints, (Z, z(1.08)), 'flash'),
        (40.1, shot_proof, (z(1.1), Z), 'zoom'),
        (43.15, shot_room, (Z, z(1.06)), 'wipe'),
        (45.6, shot_him, (Z, z(1.08)), 'cut'),
        (47.4, shot_night, (Z, z(1.15, 540, 1000)), 'fade'),
        (49.1, shot_asleep, (Z, z(1.1, 400, 1400)), 'fade'),
        (50.3, shot_cuff, (z(1.15), Z), 'zoom'),
        (52.65, shot_sneak, (Z, z(1.06)), 'cut'),
        (54.25, shot_run, (Z, z(1.1)), 'flash'),
        (55.25, shot_flag, (Z, z(1.06, 540, 1200)), 'whip'),
        (57.65, shot_station, (Z, z(1.06)), 'wipe'),
        (59.6, shot_interview, (Z, z(1.06, 540, 1100)), 'fade'),
        (61.55, shot_where, (z(1.0), z(1.25, 760, 800)), 'zoom'),
        (64.05, shot_raid, (Z, z(1.06)), 'whip'),
        (65.8, shot_gone, (Z, z(1.1, 400, 1050)), 'flash'),
        (67.25, shot_evo, (Z, z(1.08)), 'cut'),
        (69.45, shot_florida, (Z, z(1.1, 520, 1100)), 'wipe'),
        (71.0, shot_chase, (Z, z(1.06)), 'whip'),
        (72.45, shot_end, (Z, z(1.08)), 'fade'),
        (74.3, shot_search, (Z, z(1.08, 540, 1100)), 'fade'),
        (76.7, shot_box, (Z, z(1.12, 540, 1150)), 'zoom'),
        (78.85, shot_board, (Z, z(1.1, 520, 900)), 'wipe'),
        (82.3, shot_cold, (Z, z(1.08)), 'fade'),
        (84.95, shot_saved, (Z, z(1.08)), 'flash'),
        (86.85, shot_solved, (z(1.1), Z), 'whip'),
        (89.3, shot_back, (z(1.0), z(1.0)), 'fade'),
    ]
    out = []
    for i, (s0, fn, cam, tr) in enumerate(L):
        s1 = L[i + 1][0] if i + 1 < len(L) else end
        out.append((s0, s1, fn, cam, tr))
    return out
