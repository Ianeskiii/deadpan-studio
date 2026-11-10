"""Example episode as delivered in the original session (coughing-major). Shots, ACTS grade and scenes() list.
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

def money(T, t0, t1, v0, v1): return lerp(v0, v1, ease(clamp((T - t0) / max(0.01, t1 - t0))))
BLANK = ['- - - -', '- - - -', '- - - -', '- - - -']
FINALQ = 'A NUMBER ONE FOLLOWED BY 100 ZEROS\nIS KNOWN BY WHAT NAME?'
FINALA = ['GOOGOL', 'MEGATRON', 'GIGABIT', 'NANOMOLE']

def shot_hook(cv, T, frozen=False):
    t = 0 if frozen else T
    studio(cv, t)
    hot_chair(cv, 540, 1720, 1.2)
    character(cv, 'charles', 540, 1560, 100, t=t, expr='happy', pose={'sit': True, 'hl': (-0.5, -0.9), 'hr': (0.5, -0.9)}, look=(0, -0.4))
    cv.drawRoundRect(skia.Rect(140, 420, 940, 760), 40, 40, fillp(C('#08082a'))); cv.drawRoundRect(skia.Rect(140, 420, 940, 760), 40, 40, strokep(QGOLD, 8))
    text(cv, '£1,000,000', 540, 640, 140, QGOLD)
    if frozen: return
    rnd = random.Random(1)
    for i in range(40):
        f = ((T * 0.5 + rnd.random()) % 1)
        cv.save(); cv.translate(rnd.uniform(0, W), -50 + f * 2000); cv.rotate(T * 200 * rnd.uniform(-1, 1)); cv.drawRect(skia.Rect(-10, -16, 10, 16), fillp(rnd.choice([QGOLD, C('#ffffff'), C('#7a5aff')]))); cv.restore()
    tag(cv, 'ON TV', 540, 300, C('#7a5aff'), 56, k=pop(T, wt(0, 'tv') - 0.2))

def shot_penny(cv, T):
    dark_bg(cv, C('#2a2a3a'), C('#08080e'))
    cheque(cv, 540, 1000, 0.95, rot=-4)
    k = pop(T, wt(0, 'penny') - 0.15, 0.2)
    stamp(cv, 540, 1000, 'NOT PAID', 120, C('#e2483b'), -14, k=k)
    tag(cv, 'NOT A SINGLE PENNY', 540, 360, CREAM, 52, INK, k=pop(T, wt(0, 'never') - 0.15))

def shot_cough(cv, T):
    full(cv, C('#06060e'))
    t0 = wt(0, 'cough') - 0.1
    waveform(cv, 60, 1000, 960, 600, T, spikes=(60,) if T > t0 else (), prog=1.0)
    cough_burst(cv, 540, 600, pop(T, t0, 0.18), 1.1)
    if T > t0: cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#ffffff'), alpha=0.25 * fadek(T, t0, 0.3)))
    tag(cv, 'ONE COUGH', 540, 1500, C('#e2483b'), 60, k=pop(T, wt(0, 'one', 1) - 0.15))

def shot_date(cv, T):
    studio(cv, T, lights=0.5, dark=0.3)
    calendar(cv, 540, 900, 1.0, 'SEPTEMBER', '2001', QBLUE, k=pop(T, wt(1, 'september') - 0.25, 0.3), rot=-3)

def shot_name(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (W, H), [C('#3a4a2a'), C('#141a0e')])))
    for i in range(14): cv.drawLine(-300, i * 160 - (T * 40 % 160), W + 300, i * 160 + 300 - (T * 40 % 160), strokep(C('#4a5a34'), 30, alpha=0.4))
    spot(cv, 540, 980, 520, 0.25)
    character(cv, 'charles', 540, 1700, 135, t=T, expr='smug', look=(0.1, -0.1))
    k = pop(T, wt(1, 'major') - 0.2, 0.35)
    if k > 0:
        cv.save(); cv.translate(540, 360); cv.scale(k, k)
        cv.drawRect(skia.Rect(-450, -130, 450, 130), fillp(CREAM)); cv.drawRect(skia.Rect(-450, -130, 450, 130), strokep(INK, 7))
        cv.drawRect(skia.Rect(-450, -130, -420, 130), fillp(C('#5a6a3a'))); text(cv, 'MAJOR', 15, -30, 54, C('#5a6a3a')); text(cv, 'CHARLES INGRAM', 15, 70, 76, INK); cv.restore()
    tag(cv, 'BRITISH ARMY OFFICER', 540, 600, C('#5a6a3a'), 46, k=pop(T, wt(1, 'army') - 0.15))

def shot_seat(cv, T):
    studio(cv, T)
    hot_chair(cv, 320, 1720, 1.1); hot_chair(cv, 760, 1720, 1.1)
    character(cv, 'charles', 320, 1570, 95, t=T, expr='neutral', pose={'sit': True}, look=(1, 0))
    silhouette(cv, lambda: character(cv, 'host', 760, 1570, 95, t=T, pose={'sit': True}))
    spot(cv, 320, 1250, 300, 0.25)
    tag(cv, 'THE HOT SEAT', 540, 300, QGOLD, 58, INK, k=pop(T, wt(1, 'hot') - 0.2))
    tag(cv, '"WHO WANTS TO BE A MILLIONAIRE?"', 540, 420, C('#1a2a7a'), 38, k=pop(T, wt(1, 'wants') - 0.15))

def shot_disaster(cv, T):
    studio(cv, T, lights=0.6, dark=0.2)
    lvl = money(T, 16.0, 19.6, 0, 6)
    lvl = lvl + math.sin(T * 9) * 0.15 * (1 - clamp((T - 19.4) / 0.3))
    money_ladder(cv, 540, 1600, round(lvl), T)
    tag(cv, 'NIGHT ONE: A DISASTER', 540, 260, C('#e2483b'), 50, k=pop(T, wt(2, 'disaster') - 0.2))

def shot_lifelines(cv, T):
    studio(cv, T, lights=0.5, dark=0.3)
    for i in range(3):
        cr = clamp((T - wt(2, 'burned') - i * 0.35) / 0.25) if i < 2 else 0
        lifeline(cv, 540, 600 + i * 300, i, 1.6, crossed=cr)
    character(cv, 'charles', 540, 1780, 80, t=T, expr='worried', look=(0, -0.5))
    tag(cv, '2 OF 3 LIFELINES GONE', 540, 300, C('#e2483b'), 48, k=pop(T, wt(2, 'lifelines') - 0.15))

def shot_nextday(cv, T):
    studio(cv, T, lights=clamp((T - 22.6) / 1.0))
    calendar(cv, 540, 900, 0.95, 'NIGHT', 'TWO', C('#5a2a8a'), k=pop(T, wt(3, 'next') - 0.25, 0.3), rot=3)
    tag(cv, 'HE CAME BACK', 540, 320, CREAM, 54, INK, k=pop(T, wt(3, 'came') - 0.15))

def shot_changed(cv, T):
    studio(cv, T)
    hot_chair(cv, 540, 1720, 1.2)
    cv.save(); cv.translate(540, 1400); s = lerp(1.0, 1.25, ease(clamp((T - 24.6) / 1.2))); cv.scale(s, s); cv.translate(-540, -1400)
    character(cv, 'charles', 540, 1570, 105, t=T, expr='smug', pose={'sit': True}, look=(0.2, -0.2))
    cv.restore()
    tag(cv, 'SOMETHING CHANGED', 540, 300, C('#7a5aff'), 56, k=pop(T, wt(3, 'changed') - 0.2))

def shot_loud(cv, T):
    studio(cv, T, dark=0.2)
    hi = int((T - 27.7) / 0.45) % 4 if T > 27.7 else None
    qpanel(cv, 540, 560, 960, 'QUESTION 8', BLANK, T, hi=hi, hicol=C('#3a4aa0'))
    character(cv, 'charles', 300, 1760, 100, t=T, expr='neutral', pose={'hr': (0.5, -0.6)}, look=(0.6, -0.6))
    bubble_txt(cv, 640, 1020, ['"HMM… IS IT A?', '…OR MAYBE B?"'], 44, tail=(-200, 150), k=pop(T, wt(4, 'thinking') - 0.15, 0.3))
    tag(cv, 'THINKING OUT LOUD', 540, 280, CREAM, 50, INK, k=pop(T, wt(4, 'thinking') - 0.25))

def shot_audience(cv, T):
    studio(cv, T, lights=0.5, dark=0.5)
    h = clamp((T - wt(5, 'someone') + 0.1) / 0.3)
    audience(cv, T, y0=950, rows=4, hi_seat=(2, 5), hi=h)
    sx = lerp(100, 5 * 140 + 20, ease(clamp((T - 30.0) / 1.6)))
    cv.drawCircle(sx, 1290 - 80, 180, fillp(C('#ffffff'), alpha=0.1, blur=30))
    cough_burst(cv, 740, 900, pop(T, wt(5, 'coughed') - 0.1, 0.2), 0.7)
    tag(cv, 'IN THE AUDIENCE', 540, 300, CREAM, 52, INK, k=pop(T, wt(5, 'audience') - 0.2))

def shot_right(cv, T):
    studio(cv, T, dark=0.2)
    hi = 2 if T > wt(6, 'right') - 0.3 else None
    qpanel(cv, 540, 560, 960, 'QUESTION 10', BLANK, T, hi=hi, hicol=QORANGE)
    k = pop(T, wt(6, 'cough') - 0.1, 0.2)
    cough_burst(cv, 540, 1180, k, 0.8)
    check(cv, 900, 800, pop(T, wt(6, 'cough') + 0.1), s=1.4)
    tag(cv, 'RIGHT ANSWER', 540, 280, QGREEN, 52, k=pop(T, wt(6, 'right') - 0.2))

def shot_wrong(cv, T):
    studio(cv, T, dark=0.55)
    qpanel(cv, 540, 560, 960, 'QUESTION 10', BLANK, T, hi=1 if T > wt(6, 'wrong') - 0.3 else None, hicol=C('#5a5a7a'))
    k = pop(T, wt(6, 'silence') - 0.15, 0.3)
    if k > 0: text(cv, '. . .', 540, 1150, 160 * k, C('#8a8aaa'))
    cv.drawLine(780, 690, 900, 790, strokep(C('#e2483b'), 14, alpha=k)); cv.drawLine(900, 690, 780, 790, strokep(C('#e2483b'), 14, alpha=k))
    tag(cv, 'SILENCE', 540, 280, C('#5a5a7a'), 60, k=k)

def shot_climb(cv, T):
    studio(cv, T)
    lvl = 9 if T < wt(7, '125') - 0.2 else (11 if T < wt(7, 'half') - 0.2 else 13)
    lvl_f = lvl if T > wt(7, '32') - 0.2 else 7
    money_ladder(cv, 540, 1650, lvl_f, T)
    for i, (w_, v) in enumerate((('32', '£32,000'), ('125', '£125,000'), ('half', '£500,000'))):
        k = pop(T, wt(7, w_) - 0.2) * (fadek(T, wt(7, ('125', 'half', 'half')[i]) - 0.25, 0.15) if i < 2 else 1)
        tag(cv, v, 540, 270, QGOLD, 72, INK, k=k)

def shot_final(cv, T):
    studio(cv, T, lights=0.4, dark=0.5)
    spot(cv, 540, 900, 600, 0.2, C('#7a8aff'))
    k = pop(T, wt(8, 'final') - 0.2, 0.35)
    if k > 0:
        cv.save(); cv.translate(540, 820); cv.scale(k, k)
        cv.drawRoundRect(skia.Rect(-440, -200, 440, 200), 50, 50, fillp(C('#08082a'))); cv.drawRoundRect(skia.Rect(-440, -200, 440, 200), 50, 50, strokep(QGOLD, 10))
        text(cv, 'THE £1,000,000', 0, -30, 80, QGOLD); text(cv, 'QUESTION', 0, 80, 90, C('#ffffff')); cv.restore()

def shot_zeros(cv, T):
    full(cv, C('#06061a'))
    n = int(clamp((T - 47.8) / 1.4) * 100)
    s_ = '1' + '0' * n
    f = skia.Font(skia.Typeface('Courier New', skia.FontStyle.Bold()), 54)
    per = 16
    for r in range(0, len(s_), per):
        f_line = s_[r:r + per]
        cv.drawString(f_line, 540 - f.measureText('0' * per) / 2, 360 + (r // per) * 76, f, fillp(QGOLD))
    tag(cv, '100 ZEROS', 540, 1700, C('#7a5aff'), 60, k=pop(T, wt(8, 'zeros') - 0.2))

def shot_googol(cv, T):
    studio(cv, T, dark=0.3)
    hi = 0 if T > wt(8, 'googol') - 0.2 else None
    qpanel(cv, 540, 700, 980, FINALQ, FINALA, T, hi=hi, qscale=0.82)
    cough_burst(cv, 760, 1300, pop(T, wt(8, 'googol') + 0.05, 0.2), 0.6)

def shot_final_answer(cv, T):
    studio(cv, T)
    lock = T > wt(9, 'picked') - 0.1
    win = T > wt(9, 'won') - 0.15
    qpanel(cv, 540, 700, 980, FINALQ, FINALA, T, hi=0 if lock else None, correct=0 if win else None, qscale=0.82)
    tag(cv, '"FINAL ANSWER."', 540, 300, QORANGE, 56, k=pop(T, wt(9, 'picked') - 0.2) * fadek(T, wt(9, 'won') - 0.2, 0.15))
    if win:
        tag(cv, 'CORRECT!', 540, 300, QGREEN, 64, k=pop(T, wt(9, 'won') - 0.15))
        cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#ffffff'), alpha=0.35 * fadek(T, wt(9, 'won') - 0.1, 0.3)))

def shot_win(cv, T):
    studio(cv, T)
    rnd = random.Random(3)
    for i in range(70):
        f = ((T * 0.6 + rnd.random()) % 1)
        cv.save(); cv.translate(rnd.uniform(0, W), -50 + f * 2000); cv.rotate(T * 300 * rnd.uniform(-1, 1)); cv.drawRect(skia.Rect(-12, -18, 12, 18), fillp(rnd.choice([QGOLD, C('#ffffff'), C('#7a5aff'), QGREEN]))); cv.restore()
    character(cv, 'charles', 540, 1760, 120, t=T, expr='happy', pose={'hl': (-0.6, -1.1), 'hr': (0.6, -1.1)}, look=(0, -0.3))
    v = money(T, 51.9, 53.2, 500000, 1000000)
    text(cv, f'£{v:,.0f}', 540, 520, 130, QGOLD, stroke=INK, sw=12)

def shot_backstage(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#1a1e24'), C('#0a0c10')])))
    for i in range(3):
        cv.drawRoundRect(skia.Rect(80 + i * 320, 300, 360 + i * 320, 520), 16, 16, fillp(C('#0a1a2a'))); cv.drawRoundRect(skia.Rect(80 + i * 320, 300, 360 + i * 320, 520), 16, 16, strokep(C('#3a4a5a'), 5))
        cv.save(); cv.clipRect(skia.Rect(80 + i * 320, 300, 360 + i * 320, 520)); studio(cv, T) if False else cv.drawRect(skia.Rect(80 + i * 320, 300, 360 + i * 320, 520), fillp(C('#14145a'))); cv.restore()
    cv.drawRect(skia.Rect(-300, 1150, W + 300, 1500), fillp(C('#2a2e36'))); cv.drawRect(skia.Rect(-300, 1150, W + 300, 1500), strokep(INK, 6))
    for i in range(16):
        x = 60 + i * 62; yk = 1220 + (math.sin(T * 1.5 + i) + 1) * 60
        cv.drawLine(x, 1210, x, 1380, strokep(C('#0a0a0e'), 8)); cv.drawRoundRect(skia.Rect(x - 18, yk - 12, x + 18, yk + 12), 4, 4, fillp(C('#c8ccd4')))
    waveform(cv, 100, 820, 880, 300, T, spikes=(30, 70, 95) if T > 55.5 else (), col=C('#3fbf6b'))
    character(cv, 'tech', 540, 1780, 95, t=T, expr='shock', look=(0, -0.6))
    cv.drawArc(skia.Rect(540 - 110, 1780 - 95 * 4.7, 540 + 110, 1780 - 95 * 3.4), 180, 180, False, strokep(INK, 14))
    tag(cv, 'BACKSTAGE', 540, 230, C('#3a4a5a'), 54, k=pop(T, wt(10, 'backstage') - 0.2))

def shot_count(cv, T):
    full(cv, C('#0a0a10'))
    n = int(money(T, 57.6, 59.6, 0, 192))
    text(cv, str(n), 540, 760, 300, C('#ffffff'), stroke=INK, sw=14)
    text(cv, 'COUGHS', 540, 920, 90, C('#e2483b'))
    rnd = random.Random(9)
    for i in range(min(n, 192)):
        x = 80 + (i % 24) * 38; y = 1100 + (i // 24) * 70
        cv.drawLine(x, y, x, y + 46, strokep(C('#8a8aa0'), 6))
    tag(cv, 'THEY COUNTED', 540, 300, CREAM, 52, INK, k=pop(T, wt(11, 'counted') - 0.2))

def shot_19(cv, T):
    full(cv, C('#0a0a10'))
    hi = set(range(0, 120, 6)[:19]) if T > wt(11, '19') - 0.2 else set()
    waveform(cv, 60, 760, 960, 500, T, spikes=set(range(0, 120, 6)) | {3, 15, 40, 77, 101}, hi=hi)
    text(cv, '19', 540, 1280, 220, C('#e2483b'), stroke=INK, sw=12)
    tag(cv, 'FROM ONE MAN', 540, 1560, CREAM, 56, INK, k=pop(T, wt(11, 'one') - 0.15))

def shot_whit(cv, T):
    studio(cv, T, lights=0.6, dark=0.3)
    for i in range(5):
        x = 140 + i * 200
        if i == 2: character(cv, 'whit', x, 1700, 95, t=T, expr='smug', look=(0.4, -0.2))
        else: silhouette(cv, lambda x=x, i=i: character(cv, 'host', x, 1700, 90, t=T, blink_seed=i))
    spot(cv, 540, 1250, 300, 0.3)
    k = pop(T, wt(12, 'tecwen') - 0.2, 0.35)
    if k > 0:
        cv.save(); cv.translate(540, 380); cv.scale(k, k)
        cv.drawRect(skia.Rect(-420, -100, 420, 100), fillp(CREAM)); cv.drawRect(skia.Rect(-420, -100, 420, 100), strokep(INK, 7))
        cv.drawRect(skia.Rect(-420, -100, -390, 100), fillp(C('#e2483b'))); text(cv, 'TECWEN WHITTOCK', 15, 26, 70, INK); cv.restore()
    tag(cv, 'COLLEGE LECTURER', 540, 580, C('#3a5a3a'), 46, k=pop(T, wt(12, 'college') - 0.15))
    tag(cv, "IN THE CONTESTANTS' SEATS", 540, 690, CREAM, 40, INK, k=pop(T, wt(12, 'contestants') - 0.15))

def shot_frozen(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#2a4a6a'), C('#0a1420')])))
    snowfall(cv, T, n=60, wind=40, a=0.5, seed=2)
    cheque(cv, 540, 980, 0.95, rot=3, frost=clamp((T - wt(13, 'froze') + 0.1) / 0.5))
    tag(cv, 'CHEQUE FROZEN', 540, 360, TEAL, 58, INK, k=pop(T, wt(13, 'froze') - 0.15))

def shot_police(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#0a0e1a'), C('#1a1e2a')])))
    cv.drawRect(skia.Rect(-300, 1300, W + 300, H + 300), fillp(C('#2a2c34')))
    police_car(cv, lerp(-200, 540, eout(clamp((T - 68.9) / 0.9))), 1650, 1.2, T)
    siren_glow(cv, T, a=0.3)
    tag(cv, 'POLICE WERE CALLED', 540, 300, C('#2a3a6a'), 54, k=pop(T, wt(13, 'police') - 0.2))

def shot_court(cv, T):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [C('#5a3a28'), C('#2a1a12')])))
    for i in range(-1, 12): cv.drawRect(skia.Rect(i * 110, 200, i * 110 + 60, 1100), fillp(C('#6a4a32')))
    cv.drawRect(skia.Rect(-300, 1100, W + 300, H + 300), fillp(C('#3a2618')))
    for i, (x, nm) in enumerate(((240, 'charles'), (540, 'diana'), (840, 'whit'))):
        character(cv, nm, x, 1500, 90, t=T, expr='worried' if T < wt(14, 'guilty') else 'shock', look=(0, -0.2), blink_seed=i)
    cv.drawRect(skia.Rect(60, 1300, 1020, 1520), fillp(C('#7a4a2a'))); cv.drawRect(skia.Rect(60, 1300, 1020, 1520), strokep(INK, 8))
    for i, (x, nm) in enumerate(((240, 'charles'), (540, 'diana'), (840, 'whit'))):
        stamp(cv, x, 1420, 'GUILTY', 56, C('#e2483b'), -12 + i * 6, k=pop(T, wt(14, 'guilty') - 0.1 + i * 0.22, 0.18))
    tag(cv, 'DECEPTION', 380, 380, C('#e2483b'), 58, k=pop(T, wt(14, 'deception') - 0.2))

def shot_army(cv, T):
    dark_bg(cv, C('#3a4a2a'), C('#0e120a'))
    doc(cv, 540, 950, 640, 820, rot=-2, lines=7, title='RESIGNATION', seed=5)
    f = clamp((T - 76.6) / 1.0)
    cv.save(); cv.translate(760, lerp(600, 1450, f * f)); cv.rotate(f * 140)
    cv.drawPath(poly([(0, -80), (60, -20), (40, 70), (-40, 70), (-60, -20)]), fillp(QGOLD)); cv.drawPath(poly([(0, -80), (60, -20), (40, 70), (-40, 70), (-60, -20)]), strokep(INK, 6))
    cv.drawCircle(0, 0, 22, fillp(C('#c8281e'))); cv.restore()
    tag(cv, 'RESIGNED FROM THE ARMY', 540, 300, C('#5a6a3a'), 48, k=pop(T, wt(15, 'resign') - 0.2))

def shot_gone(cv, T):
    dark_bg(cv, C('#2a2a3a'), C('#06060a'))
    f = clamp((T - 78.9) / 1.4)
    cv.save(); cv.clipRect(skia.Rect(-300, -300, W + 300, lerp(1250, 700, f)))
    cheque(cv, 540, 980, 0.95, rot=-3)
    cv.restore()
    rnd = random.Random(5)
    for i in range(int(f * 60)):
        y = lerp(1250, 700, f) + rnd.uniform(-20, 20); x = rnd.uniform(100, 980)
        d = (T - 78.9) * 300 * rnd.uniform(0.3, 1)
        cv.drawRect(skia.Rect(x - 8, y - d * 0.5 - 8, x + 8, y - d * 0.5 + 8), fillp(C('#d8e0e8'), alpha=max(0, 1 - d / 500)))
    tag(cv, 'GONE FOREVER', 540, 360, C('#e2483b'), 62, k=pop(T, wt(15, 'gone') - 0.2))

def shot_innocent(cv, T):
    night_sky(cv, C('#04060e'), C('#1a2238'), h=1500, moon=(820, 300))
    cv.drawRect(skia.Rect(-300, 1500, W + 300, H + 300), fillp(C('#0e1018')))
    character(cv, 'charles', 420, 1760, 115, t=T, expr='stern', look=(0.4, -0.3))
    bubble_txt(cv, 680, 900, ['"I AM', 'INNOCENT."'], 64, tail=(-150, 260), k=pop(T, wt(16, 'innocent') - 0.3, 0.3))
    tag(cv, 'TO THIS DAY', 540, 300, CREAM, 54, INK, k=pop(T, wt(16, 'day') - 0.2))

def shot_back(cv, T):
    studio(cv, T, dark=0.4 * (1 - clamp((T - 82.8) / 0.8)))
    hot_chair(cv, 540, 1720, 1.2)
    character(cv, 'charles', 540, 1560, 100, t=T, expr='happy', pose={'sit': True, 'hl': (-0.5, -0.9), 'hr': (0.5, -0.9)}, look=(0, -0.4))
    cough_burst(cv, 540, 600, pop(T, wt(16, 'came') - 0.2, 0.2) * fadek(T, 83.6, 0.25), 0.9)
    end = TL['total']
    b = clamp((T - (end - 0.62)) / 0.6)
    if b > 0:
        surf = skia.Surface(W, H); c2 = surf.getCanvas(); shot_hook(c2, 0.0, frozen=True)
        p = skia.Paint(); p.setAlphaf(b)
        cv.save(); cv.resetMatrix(); cv.drawImage(surf.makeImageSnapshot(), 0, 0, skia.SamplingOptions(), p); cv.restore()


def shot_half(cv, T):
    studio(cv, T)
    hot_chair(cv, 540, 1720, 1.2)
    character(cv, 'charles', 540, 1560, 100, t=T, expr='smug', pose={'sit': True}, look=(0.3, -0.3))
    for i, t0 in enumerate((42.7, 43.6, 44.3)):
        cough_burst(cv, (180, 880, 300)[i], (1250, 1100, 900)[i], pop(T, t0, 0.18) * fadek(T, t0 + 0.6, 0.2), 0.5, rot=(-8, 6, -4)[i])
    k = pop(T, wt(7, 'half') - 0.2, 0.3)
    if k > 0:
        cv.save(); cv.translate(540, 520); cv.scale(k, k)
        cv.drawRoundRect(skia.Rect(-400, -110, 400, 90), 40, 40, fillp(C('#08082a'))); cv.drawRoundRect(skia.Rect(-400, -110, 400, 90), 40, 40, strokep(QGOLD, 8))
        text(cv, '£500,000', 0, 30, 120, QGOLD); cv.restore()
    tag(cv, 'HALF A MILLION', 540, 280, CREAM, 50, INK, k=pop(T, wt(7, 'half') - 0.1))

def shot_courthouse(cv, T):
    day_sky(cv, C('#8a98a8'), C('#d8dce0'), h=1350, sun=None)
    council_bldg(cv, 540, 1350, 1.0)
    cv.drawRect(skia.Rect(-300, 1350, W + 300, H + 300), fillp(C('#7a7a7a')))
    cv.drawRect(skia.Rect(240, 770, 840, 820), fillp(C('#5a2a2a'))); text(cv, 'CROWN COURT', 540, 810, 42, CREAM)
    for i in range(6):
        x = 100 + i * 180
        silhouette(cv, lambda x=x, i=i: character(cv, 'host', x, 1780, 70, t=T, pose={'hr': (0.5, -0.7)} if i % 2 else None, blink_seed=i))
    for i in range(5):
        f = ((T * 3 + i * 0.37) % 1)
        if f < 0.12: cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#ffffff'), alpha=0.25))
    calendar(cv, 540, 420, 0.75, 'YEAR', '2003', C('#5a2a2a'), k=pop(T, wt(14, '2003') - 0.25), rot=-3)

ACTS = [(0, C('#2a1a6a'), 0.08), (7.6, C('#3a3a2a'), 0.07), (15.6, C('#6a1a2a'), 0.08), (22.5, C('#2a1a6a'), 0.08),
        (29.9, C('#1a1a3a'), 0.12), (38.7, C('#6a5a1a'), 0.07), (45.8, C('#1a1a5a'), 0.10), (50.6, C('#6a5a1a'), 0.08),
        (53.8, C('#1a3a2a'), 0.10), (67.1, C('#1a3a5a'), 0.10), (70.3, C('#5a2a1a'), 0.10), (80.5, C('#1a1a3a'), 0.10), (82.8, C('#2a1a6a'), 0.08)]
def overlay(cv, T): grade(cv, T, ACTS)

def scenes():
    end = TL['total']
    Z = (1.0, 540, 960)
    def z(a, cx=540, cy=960): return (a, cx, cy)
    L = [
        (0.0, shot_hook, (Z, z(1.08, 540, 1000)), 'cut'),
        (3.4, shot_penny, (Z, z(1.1)), 'whip'),
        (5.65, shot_cough, (Z, z(1.08)), 'flash'),
        (7.6, shot_date, (Z, z(1.1)), 'wipe'),
        (9.65, shot_name, (Z, z(1.08, 540, 900)), 'whip'),
        (12.55, shot_seat, (Z, z(1.1, 400, 1200)), 'fade'),
        (15.6, shot_disaster, (Z, z(1.06, 540, 1100)), 'zoom'),
        (20.0, shot_lifelines, (Z, z(1.06)), 'cut'),
        (22.45, shot_nextday, (Z, z(1.08)), 'wipe'),
        (24.45, shot_changed, (Z, z(1.08, 540, 1200)), 'flash'),
        (25.95, shot_loud, (Z, z(1.06, 540, 900)), 'whip'),
        (29.8, shot_audience, (Z, z(1.12, 700, 1200)), 'fade'),
        (32.85, shot_right, (Z, z(1.06)), 'zoom'),
        (35.8, shot_wrong, (Z, z(1.06)), 'cut'),
        (38.65, shot_climb, (Z, z(1.08, 540, 1100)), 'wipe'),
        (44.2, shot_half, (Z, z(1.1, 540, 1100)), 'flash'),
        (45.75, shot_final, (z(1.15), Z), 'fade'),
        (47.55, shot_zeros, (Z, z(1.06, 540, 700)), 'cut'),
        (49.05, shot_googol, (Z, z(1.08, 540, 900)), 'zoom'),
        (50.55, shot_final_answer, (Z, z(1.06, 540, 900)), 'cut'),
        (52.3, shot_win, (Z, z(1.08)), 'flash'),
        (53.75, shot_backstage, (Z, z(1.08, 540, 1100)), 'whip'),
        (57.0, shot_count, (Z, z(1.06)), 'zoom'),
        (60.6, shot_19, (Z, z(1.08)), 'cut'),
        (63.0, shot_whit, (Z, z(1.06, 540, 1000)), 'wipe'),
        (67.1, shot_frozen, (Z, z(1.08)), 'zoom'),
        (68.85, shot_police, (Z, z(1.06)), 'whip'),
        (70.25, shot_courthouse, (Z, z(1.08, 540, 1000)), 'wipe'),
        (71.5, shot_court, (Z, z(1.06, 540, 1100)), 'flash'),
        (75.85, shot_army, (Z, z(1.08)), 'wipe'),
        (77.95, shot_gone, (Z, z(1.08)), 'fade'),
        (80.5, shot_innocent, (Z, z(1.08, 500, 1100)), 'fade'),
        (82.75, shot_back, (z(1.0), z(1.0)), 'whip'),
    ]
    out = []
    for i, (s0, fn, cam, tr) in enumerate(L):
        s1 = L[i + 1][0] if i + 1 < len(L) else end
        out.append((s0, s1, fn, cam, tr))
    return out
