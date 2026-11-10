import skia, math, random, os
# Fonts are bundled in channels/sticky/fonts so renders look the same everywhere (Actions, fresh workspaces).
# 'Courier New' has always resolved to Liberation Mono Bold in this pipeline, so it is pinned to that file.
_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
_FONT_FILES = {'poppins': 'Poppins-Bold.ttf', 'courier new': 'LiberationMono-Bold.ttf', 'liberation mono': 'LiberationMono-Bold.ttf'}
_Typeface = skia.Typeface
_TF_CACHE = {}
def _typeface(name='', style=None):
    f = _FONT_FILES.get((name or '').lower())
    if f:
        if f not in _TF_CACHE: _TF_CACHE[f] = _Typeface.MakeFromFile(os.path.join(_FONT_DIR, f))
        return _TF_CACHE[f]
    return _Typeface(name, style) if style is not None else _Typeface(name)
_typeface.MakeFromFile = _Typeface.MakeFromFile
skia.Typeface = _typeface
W, H = 1080, 1920
INK = 0xFF1B1B22

def C(hexs, a=255):
    hexs = hexs.lstrip('#'); r, g, b = int(hexs[0:2], 16), int(hexs[2:4], 16), int(hexs[4:6], 16)
    return skia.Color(r, g, b, a)

def mix(c1, c2, t):
    a = [skia.ColorGetR(c1), skia.ColorGetG(c1), skia.ColorGetB(c1), skia.ColorGetA(c1)]
    b = [skia.ColorGetR(c2), skia.ColorGetG(c2), skia.ColorGetB(c2), skia.ColorGetA(c2)]
    return skia.Color(*[int(x + (y - x) * t) for x, y in zip(a, b)])

def shade(c, k):  # k<1 darker, >1 lighter
    if k < 1: return mix(c, skia.Color(20, 20, 40), 1 - k)
    return mix(c, skia.Color(255, 255, 255), k - 1)

def fillp(color=None, shader=None, blur=0, blend=None, alpha=None):
    p = skia.Paint(AntiAlias=True)
    if color is not None: p.setColor(color)
    if shader is not None: p.setShader(shader)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend is not None: p.setBlendMode(blend)
    if alpha is not None: p.setAlphaf(alpha)
    return p

def strokep(color=INK, w=6, cap=skia.Paint.kRound_Cap, blur=0, alpha=None):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, Color=color,
                   StrokeCap=cap, StrokeJoin=skia.Paint.kRound_Join)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if alpha is not None: p.setAlphaf(alpha)
    return p

def poly(pts, close=True):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if close: p.close()
    return p

def lin(p0, p1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], cols, pos)

def rad(c, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*c), r, cols, pos)

def lerp(a, b, t): return a + (b - a) * t
def clamp(x, a=0, b=1): return max(a, min(b, x))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def eout(t): t = clamp(t); return 1 - (1 - t) ** 3
def back(t):  # overshoot
    t = clamp(t); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

# ------------------------------------------------------------------ rooms
def room(cv, back, wall, floor, ceil=None, side=None, bricks=True, tiles=True, brick_h=46,
         floor_tile=None, light_from=-1, ao=0.55, ceiling_light=True, w=W, h=H, trim=None):
    x0, y0, x1, y1 = back
    vp = ((x0 + x1) / 2, (y0 + y1) / 2)
    side = side or shade(wall, 0.86); ceil = ceil or shade(wall, 0.93)
    planes = {
        'ceil': [(0, 0), (w, 0), (x1, y0), (x0, y0)],
        'floor': [(0, h), (w, h), (x1, y1), (x0, y1)],
        'left': [(0, 0), (x0, y0), (x0, y1), (0, h)],
        'right': [(w, 0), (x1, y0), (x1, y1), (w, h)],
    }
    cv.drawPath(poly(planes['ceil']), fillp(shader=lin((0, 0), (0, y0), [shade(ceil, 0.8), ceil])))
    lf = 1.06 if light_from < 0 else 0.88; rf = 1.06 if light_from > 0 else 0.88
    cv.drawPath(poly(planes['left']), fillp(shader=lin((0, 0), (x0, 0), [shade(side, 0.82 * lf), shade(side, lf)])))
    cv.drawPath(poly(planes['right']), fillp(shader=lin((w, 0), (x1, 0), [shade(side, 0.82 * rf), shade(side, rf)])))
    cv.drawRect(skia.Rect(x0, y0, x1, y1), fillp(shader=lin((0, y0), (0, y1), [shade(wall, 1.05), shade(wall, 0.93)])))
    cv.drawPath(poly(planes['floor']), fillp(shader=lin((0, y1), (0, h), [shade(floor, 0.97), shade(floor, 0.78)])))
    if trim:  # baseboard / wainscot on back wall
        th = (y1 - y0) * trim[1]
        cv.drawRect(skia.Rect(x0, y1 - th, x1, y1), fillp(trim[0]))
        for side_pts, xe in ((planes['left'], 0), (planes['right'], w)):
            xb = x0 if xe == 0 else x1
            k = (vp[0] - xe) / (vp[0] - xb)
            yb_top = y1 - th; ye_top = vp[1] + (yb_top - vp[1]) * k; ye_bot = vp[1] + (y1 - vp[1]) * k
            cv.drawPath(poly([(xb, yb_top), (xe, ye_top), (xe, ye_bot), (xb, y1)]), fillp(shade(trim[0], 0.85)))
    if bricks:
        bp = strokep(shade(wall, 0.84), 2.2)
        rows = int((y1 - y0) / brick_h)
        for r in range(rows + 1):
            y = y0 + r * brick_h
            if trim and y > y1 - (y1 - y0) * trim[1]: break
            cv.drawLine(x0, y, x1, y, bp)
            off = (brick_h * 1.1) if r % 2 else 0
            x = x0 + off
            while x < x1 and r < rows:
                cv.drawLine(x, y, x, y + brick_h, bp); x += brick_h * 2.2
        sp = strokep(shade(side, 0.8), 2.4)
        for xb, xe in ((x0, 0), (x1, w)):
            k = (vp[0] - xe) / (vp[0] - xb)
            for r in range(-40, rows + 40):
                y = y0 + r * brick_h
                if y < y0 or y > y1: continue
                if trim and y > y1 - (y1 - y0) * trim[1]: continue
                ye = vp[1] + (y - vp[1]) * k
                cv.drawLine(xb, y, xe, ye, sp)
    if tiles and floor_tile:
        tp = strokep(shade(floor, 0.86), 2.5)
        n = floor_tile
        for i in range(-n, 2 * n + 1):
            xb = x0 + (x1 - x0) * i / n
            k = (h - vp[1]) / (y1 - vp[1])
            xe = vp[0] + (xb - vp[0]) * k
            cv.drawLine(xb, y1, xe, h, tp)
        D = 4.0
        for j in range(1, 14):
            s = j / 13
            wgt = 1 / (1 + (1 - s) * (D - 1)) ; yy = vp[1] + (h - vp[1]) * wgt
            if yy > y1: cv.drawLine(0, yy, w, yy, tp)
    # ambient occlusion along the back-wall seams
    aop = strokep(skia.Color(10, 10, 30, int(255 * ao * 0.5)), 26, blur=16)
    cv.drawLine(x0, y1, x1, y1, aop); cv.drawLine(x0, y0, x0, y1, aop); cv.drawLine(x1, y0, x1, y1, aop)
    cv.drawLine(x0, y0, x1, y0, aop)
    for pts in ([(x0, y1), (0, h)], [(x1, y1), (w, h)], [(x0, y0), (0, 0)], [(x1, y0), (w, 0)]):
        cv.drawLine(*pts[0], *pts[1], strokep(skia.Color(10, 10, 30, int(255 * ao * 0.35)), 30, blur=18))
    if ceiling_light:
        cx = vp[0]; cy = y0 - (y0) * 0.45
        fl = poly([(cx - 150, cy - 18), (cx + 150, cy - 18), (cx + 120, cy + 18), (cx - 120, cy + 18)])
        cv.drawPath(fl, fillp(C('#d9dde3'))); cv.drawPath(fl, strokep(C('#6c7380'), 4))
        cv.drawRect(skia.Rect(cx - 105, cy - 6, cx + 105, cy + 12), fillp(C('#ffffff')))
        cv.drawCircle(cx, cy + 60, 260, fillp(shader=rad((cx, cy + 60), 260, [skia.Color(255, 255, 240, 70), skia.Color(255, 255, 240, 0)])))
    return vp

def window_back(cv, x, y, w, h, frame=C('#e9ecef'), sky=C('#bfe3ff'), bars=False):
    cv.drawRect(skia.Rect(x - 10, y - 10, x + w + 10, y + h + 10), fillp(shade(frame, 0.8)))
    cv.drawRect(skia.Rect(x, y, x + w, y + h), fillp(shader=lin((0, y), (0, y + h), [shade(sky, 1.15), sky])))
    cv.drawRect(skia.Rect(x, y, x + w, y + h), strokep(frame, 10))
    if bars:
        for i in range(1, 6): cv.drawLine(x + w * i / 6, y, x + w * i / 6, y + h, strokep(C('#4a4f5a'), 7))
    else:
        cv.drawLine(x + w / 2, y, x + w / 2, y + h, strokep(frame, 8)); cv.drawLine(x, y + h / 2, x + w, y + h / 2, strokep(frame, 8))
    cv.drawPath(poly([(x + w * 0.15, y + h), (x + w * 0.45, y), (x + w * 0.6, y), (x + w * 0.3, y + h)]), fillp(skia.Color(255, 255, 255, 60)))

def light_shaft(cv, src, dst, alpha=70, col=(255, 248, 225)):
    cv.drawPath(poly(src + dst[::-1]), fillp(shader=lin(src[0], dst[0], [skia.Color(*col, alpha), skia.Color(*col, 0)]), blur=22, blend=skia.BlendMode.kScreen))

def floor_patch(cv, pts, alpha=90, col=(255, 246, 215)):
    cv.drawPath(poly(pts), fillp(skia.Color(*col, alpha), blur=14, blend=skia.BlendMode.kScreen))

def vignette(cv, strength=0.45, col=(10, 8, 25)):
    cv.drawRect(skia.Rect(0, 0, W, H), fillp(shader=rad((W / 2, H * 0.48), H * 0.72, [skia.Color(*col, 0), skia.Color(*col, 0), skia.Color(*col, int(255 * strength))], [0, 0.55, 1])))

def soft_shadow(cv, x, y, rx, ry, a=0.35):
    cv.drawOval(skia.Rect(x - rx, y - ry, x + rx, y + ry), fillp(skia.Color(15, 10, 30, int(255 * a)), blur=max(2, ry * 0.6)))

def text(cv, s, x, y, size, color=INK, font='Poppins-Bold', align='center', stroke=None, sw=0, rot=0):
    tf = skia.Typeface(font.replace('-', ' ').replace(' Bold', ''), skia.FontStyle.Bold()) if font else None
    f = skia.Font(tf, size)
    wdt = f.measureText(s)
    dx = {'center': -wdt / 2, 'left': 0, 'right': -wdt}[align]
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    if stroke is not None:
        cv.drawString(s, dx, 0, f, strokep(stroke, sw))
    cv.drawString(s, dx, 0, f, fillp(color))
    cv.restore(); return wdt

# ------------------------------------------------------------------ props
def table(cv, cx, top_y, w, d, h, col=C('#c98a52'), leg=C('#8a5a33')):
    # simple frontal table with a perspective top
    tl = (cx - w / 2 + d * 0.35, top_y - d); tr = (cx + w / 2 - d * 0.35, top_y - d)
    br = (cx + w / 2, top_y); bl = (cx - w / 2, top_y)
    soft_shadow(cv, cx, top_y + h + 6, w * 0.55, 22, 0.32)
    lw = w * 0.05
    for lx in (cx - w / 2 + lw * 1.2, cx + w / 2 - lw * 1.2):
        cv.drawRect(skia.Rect(lx - lw / 2, top_y, lx + lw / 2, top_y + h), fillp(shader=lin((lx - lw, 0), (lx + lw, 0), [shade(leg, 1.1), shade(leg, 0.8)])))
        cv.drawRect(skia.Rect(lx - lw / 2, top_y, lx + lw / 2, top_y + h), strokep(INK, 4))
    cv.drawPath(poly([tl, tr, br, bl]), fillp(shader=lin((0, tl[1]), (0, bl[1]), [shade(col, 1.12), col])))
    cv.drawRect(skia.Rect(bl[0], bl[1], br[0], bl[1] + 26), fillp(shade(col, 0.72)))
    cv.drawPath(poly([tl, tr, br, (br[0], br[1] + 26), (bl[0], bl[1] + 26), bl]), strokep(INK, 5))
    return (tl, tr, br, bl)

def chair_back(cv, cx, y, w, h, col=C('#5b7fb8')):
    cv.drawRoundRect(skia.Rect(cx - w / 2, y, cx + w / 2, y + h), 14, 14, fillp(shader=lin((0, y), (0, y + h), [shade(col, 1.1), shade(col, 0.85)])))
    cv.drawRoundRect(skia.Rect(cx - w / 2, y, cx + w / 2, y + h), 14, 14, strokep(INK, 5))

def plate(cv, x, y, r, mallow=True, bite=False, mcount=1):
    soft_shadow(cv, x, y + r * 0.12, r * 1.05, r * 0.3, 0.3)
    cv.drawOval(skia.Rect(x - r, y - r * 0.32, x + r, y + r * 0.32), fillp(C('#f4f1ea')))
    cv.drawOval(skia.Rect(x - r, y - r * 0.32, x + r, y + r * 0.32), strokep(INK, max(2.5, r * 0.05)))
    cv.drawOval(skia.Rect(x - r * 0.62, y - r * 0.19, x + r * 0.62, y + r * 0.19), strokep(C('#d6d0c4'), max(2, r * 0.035)))
    if mallow:
        offs = [0] if mcount == 1 else [-0.33, 0.33]
        for o in offs: marshmallow(cv, x + o * r, y - r * 0.05, r * 0.42, bite)

def marshmallow(cv, x, y, s, bite=False):
    # cylinder: body + elliptical top
    body = skia.Rect(x - s, y - s * 1.25, x + s, y)
    p = skia.Path(); p.addRect(body); p.addOval(skia.Rect(x - s, y - s * 0.35, x + s, y + s * 0.35))
    cv.drawPath(p, fillp(shader=lin((x - s, 0), (x + s, 0), [C('#ffffff'), C('#f6efe9'), C('#d8cfc8')], [0, 0.55, 1])))
    top = skia.Rect(x - s, y - s * 1.25 - s * 0.35, x + s, y - s * 1.25 + s * 0.35)
    cv.drawOval(top, fillp(C('#ffffff')))
    outline = skia.Path(); outline.moveTo(x - s, y - s * 1.25); outline.lineTo(x - s, y)
    outline.arcTo(skia.Rect(x - s, y - s * 0.35, x + s, y + s * 0.35), 180, -180, False); outline.lineTo(x + s, y - s * 1.25)
    cv.drawPath(outline, strokep(INK, max(2.5, s * 0.1)))
    cv.drawOval(top, strokep(INK, max(2.5, s * 0.1)))
    cv.drawOval(skia.Rect(x - s * 0.5, y - s * 1.45, x + s * 0.1, y - s * 1.25), fillp(skia.Color(255, 255, 255, 230)))
    if bite:
        cv.drawCircle(x + s * 0.9, y - s * 1.3, s * 0.55, fillp(C('#f3ece6')))

def stopwatch(cv, x, y, r, frac, label=None, col=C('#e8e8ec')):
    cv.drawRect(skia.Rect(x - r * 0.15, y - r * 1.32, x + r * 0.15, y - r * 1.05), fillp(C('#9aa0aa')))
    cv.drawRect(skia.Rect(x - r * 0.28, y - r * 1.42, x + r * 0.28, y - r * 1.28), fillp(C('#c7ccd4')))
    cv.drawCircle(x, y, r * 1.08, fillp(C('#b9bec7'))); cv.drawCircle(x, y, r * 1.08, strokep(INK, r * 0.07))
    cv.drawCircle(x, y, r * 0.92, fillp(shader=rad((x - r * 0.3, y - r * 0.3), r * 1.2, [C('#ffffff'), col])))
    cv.drawCircle(x, y, r * 0.92, strokep(INK, r * 0.05))
    sweep = 360 * frac
    if sweep > 0:
        cv.drawArc(skia.Rect(x - r * 0.8, y - r * 0.8, x + r * 0.8, y + r * 0.8), -90, sweep, True, fillp(skia.Color(255, 90, 90, 90)))
    for i in range(12):
        a = i / 12 * 2 * math.pi; cv.drawLine(x + math.sin(a) * r * 0.75, y - math.cos(a) * r * 0.75, x + math.sin(a) * r * 0.86, y - math.cos(a) * r * 0.86, strokep(INK, r * 0.04))
    a = frac * 2 * math.pi
    cv.drawLine(x, y, x + math.sin(a) * r * 0.72, y - math.cos(a) * r * 0.72, strokep(C('#e23b3b'), r * 0.06))
    cv.drawCircle(x, y, r * 0.07, fillp(INK))
    if label:
        text(cv, label, x, y + r * 1.62, r * 0.55, C('#ffffff'), stroke=INK, sw=r * 0.12)

def door(cv, x, y, w, h, openf=0.0, col=C('#7d8fa6'), frame=C('#59657a'), window=True, hinge='left'):
    cv.drawRect(skia.Rect(x - 12, y - 12, x + w + 12, y + h), fillp(frame))
    cv.drawRect(skia.Rect(x, y, x + w, y + h), fillp(C('#20232d')))
    ow = w * (1 - openf * 0.85)
    if hinge == 'left':
        r = skia.Rect(x, y, x + ow, y + h)
    else:
        r = skia.Rect(x + w - ow, y, x + w, y + h)
    cv.drawRect(r, fillp(shader=lin((r.left(), 0), (r.right(), 0), [shade(col, 1.08), shade(col, 0.9)])))
    cv.drawRect(r, strokep(INK, 5))
    if window and ow > w * 0.4:
        wr = skia.Rect(r.left() + ow * 0.25, y + h * 0.12, r.right() - ow * 0.25, y + h * 0.32)
        cv.drawRect(wr, fillp(C('#cfe6f5'))); cv.drawRect(wr, strokep(INK, 4))
    kx = r.right() - ow * 0.12 if hinge == 'left' else r.left() + ow * 0.12
    cv.drawCircle(kx, y + h * 0.55, 9, fillp(C('#d8c27a'))); cv.drawCircle(kx, y + h * 0.55, 9, strokep(INK, 3))

def wall_clock(cv, x, y, r, t):
    cv.drawCircle(x, y, r, fillp(C('#ffffff'))); cv.drawCircle(x, y, r, strokep(INK, r * 0.12))
    for i in range(12):
        a = i / 12 * 2 * math.pi; cv.drawLine(x + math.sin(a) * r * 0.72, y - math.cos(a) * r * 0.72, x + math.sin(a) * r * 0.84, y - math.cos(a) * r * 0.84, strokep(INK, r * 0.06))
    a = t * 2 * math.pi
    cv.drawLine(x, y, x + math.sin(a) * r * 0.72, y - math.cos(a) * r * 0.72, strokep(C('#dd3333'), r * 0.06))
    cv.drawLine(x, y, x + math.sin(a / 12 + 1) * r * 0.45, y - math.cos(a / 12 + 1) * r * 0.45, strokep(INK, r * 0.09))

def crayon(cv, x, y, l, w, col, ang=0, broken=False):
    cv.save(); cv.translate(x, y); cv.rotate(ang)
    body = skia.Rect(-w / 2, -l, w / 2, 0)
    cv.drawRect(body, fillp(shader=lin((-w / 2, 0), (w / 2, 0), [shade(col, 1.15), shade(col, 0.8)])))
    cv.drawRect(skia.Rect(-w / 2, -l * 0.7, w / 2, -l * 0.25), fillp(skia.Color(0, 0, 0, 40)))
    if not broken:
        tip = poly([(-w / 2, -l), (w / 2, -l), (0, -l - w * 0.9)]); cv.drawPath(tip, fillp(shade(col, 0.95))); cv.drawPath(tip, strokep(INK, 3))
    else:
        jag = poly([(-w / 2, -l), (-w / 6, -l - w * 0.3), (w / 8, -l + w * 0.05), (w / 2, -l - w * 0.2)], close=False)
        cv.drawPath(jag, strokep(INK, 3))
    cv.drawRect(body, strokep(INK, 3.5))
    cv.restore()

def sparkle(cv, x, y, s, a=1.0, col=C('#fff6b0')):
    p = skia.Path(); p.moveTo(x, y - s)
    for i, (dx, dy) in enumerate([(0.18, -0.18), (1, 0), (0.18, 0.18), (0, 1), (-0.18, 0.18), (-1, 0), (-0.18, -0.18), (0, -1)]):
        p.lineTo(x + dx * s, y + dy * s)
    cv.drawPath(p, fillp(col, alpha=a))

def bubble(cv, x, y, w, h, tail_to, a=1.0):
    p = skia.Paint(AntiAlias=True, Color=C('#ffffff')); p.setAlphaf(a)
    cv.drawRoundRect(skia.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2), h * 0.4, h * 0.4, p)
    cv.drawRoundRect(skia.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2), h * 0.4, h * 0.4, strokep(INK, 6, alpha=a))
    for i, k in enumerate((0.35, 0.65)):
        bx = lerp(x, tail_to[0], k + 0.1); by = lerp(y + h / 2, tail_to[1], k + 0.1); r = 16 - i * 6
        cv.drawCircle(bx, by, r, p); cv.drawCircle(bx, by, r, strokep(INK, 4, alpha=a))

# ------------------------------------------------------------------ characters
CHARS = {
    'prof':   dict(adult=True, shirt=C('#f5f5f2'), coat=True, tie=C('#7a3b2e'), hair='bald_grey', glasses=True, pants=C('#4a4f63')),
    'res':    dict(adult=True, shirt=C('#f5f5f2'), coat=True, tie=None, inner=C('#5aa6a0'), hair='pony', glasses=False, pants=C('#2f3b55'), badge=True),
    'kidA':   dict(adult=False, shirt=C('#ef8a3c'), stripe=C('#ffd27a'), hair='cowlick', pants=C('#3d5a9a')),
    'kidB':   dict(adult=False, shirt=C('#58b368'), stripe=None, hair='bob', pants=C('#5b4a8a')),
    'kidC':   dict(adult=False, shirt=C('#e85d75'), stripe=C('#ffffff'), hair='curly', pants=C('#38465f')),
    'kidD':   dict(adult=False, shirt=C('#4f8fd6'), stripe=None, hair='spiky', pants=C('#444444')),
    'teen':   dict(adult=True, shirt=C('#ef8a3c'), stripe=C('#ffd27a'), hair='cowlick', pants=C('#3d5a9a')),
    'teen2':  dict(adult=True, shirt=C('#7d8a99'), stripe=None, hair='spiky', pants=C('#444444')),
    'mom':    dict(adult=True, shirt=C('#b56fc7'), stripe=None, hair='bun', pants=C('#3b3550')),
}
HEAD = C('#f7f5ef')

def _arm(cv, sx, sy, hx, hy, bend, lw, col=INK):
    mx, my = (sx + hx) / 2, (sy + hy) / 2
    dx, dy = hx - sx, hy - sy; L = math.hypot(dx, dy) or 1
    cx, cy = mx - dy / L * bend, my + dx / L * bend
    p = skia.Path(); p.moveTo(sx, sy); p.quadTo(cx, cy, hx, hy)
    cv.drawPath(p, strokep(col, lw))
    cv.drawCircle(hx, hy, lw * 0.95, fillp(col))

def face(cv, x, y, u, expr, blink, look):
    lx, ly = look
    ex = 0.33 * u; ey = -0.02 * u
    fx = x + lx * u * 0.18; fy = y + ly * u * 0.12
    ink = fillp(INK)
    def eye(cx, cy, kind):
        if blink or kind == 'closed':
            cv.drawLine(cx - u * 0.12, cy, cx + u * 0.12, cy, strokep(INK, u * 0.07)); return
        if kind == 'happy':
            p = skia.Path(); p.moveTo(cx - u * 0.13, cy + u * 0.04); p.quadTo(cx, cy - u * 0.14, cx + u * 0.13, cy + u * 0.04)
            cv.drawPath(p, strokep(INK, u * 0.07)); return
        if kind == 'wide':
            cv.drawOval(skia.Rect(cx - u * 0.16, cy - u * 0.2, cx + u * 0.16, cy + u * 0.2), fillp(C('#ffffff')))
            cv.drawOval(skia.Rect(cx - u * 0.16, cy - u * 0.2, cx + u * 0.16, cy + u * 0.2), strokep(INK, u * 0.045))
            cv.drawCircle(cx, cy, u * 0.07, ink); return
        rw, rh = u * 0.085, u * 0.12
        if kind == 'half':
            cv.save(); cv.clipRect(skia.Rect(cx - u, cy - u * 0.02, cx + u, cy + u)); cv.drawOval(skia.Rect(cx - rw, cy - rh, cx + rw, cy + rh), ink); cv.restore()
            cv.drawLine(cx - u * 0.14, cy - u * 0.02, cx + u * 0.14, cy - u * 0.02, strokep(INK, u * 0.05)); return
        cv.drawOval(skia.Rect(cx - rw, cy - rh, cx + rw, cy + rh), ink)
        cv.drawCircle(cx + rw * 0.35, cy - rh * 0.4, u * 0.03, fillp(C('#ffffff')))
    E = {'neutral': 'dot', 'smile': 'dot', 'grin': 'happy', 'happy': 'happy', 'sad': 'dot', 'shock': 'wide', 'smug': 'half',
         'worried': 'dot', 'tempted': 'dot', 'puffed': 'closed', 'meh': 'half', 'stern': 'dot', 'o': 'wide', 'tears': 'dot', 'sorry': 'dot', 'strain': 'closed', 'sleep': 'closed'}
    k = E.get(expr, 'dot')
    eye(fx - ex, fy + ey, k); eye(fx + ex, fy + ey, k)
    bw = strokep(INK, u * 0.06)
    by = fy - 0.27 * u
    if expr in ('sad', 'worried', 'tears', 'sorry'):
        cv.drawLine(fx - ex - u * 0.13, by + u * 0.02, fx - ex + u * 0.12, by - u * 0.06, bw); cv.drawLine(fx + ex + u * 0.13, by + u * 0.02, fx + ex - u * 0.12, by - u * 0.06, bw)
    elif expr in ('stern', 'strain'):
        cv.drawLine(fx - ex - u * 0.13, by - u * 0.06, fx - ex + u * 0.12, by + u * 0.03, bw); cv.drawLine(fx + ex + u * 0.13, by - u * 0.06, fx + ex - u * 0.12, by + u * 0.03, bw)
    elif expr in ('shock', 'o'):
        cv.drawLine(fx - ex - u * 0.1, by - u * 0.1, fx - ex + u * 0.1, by - u * 0.12, bw); cv.drawLine(fx + ex - u * 0.1, by - u * 0.12, fx + ex + u * 0.1, by - u * 0.1, bw)
    elif expr in ('smug', 'tempted'):
        cv.drawLine(fx - ex - u * 0.12, by, fx - ex + u * 0.1, by - u * 0.02, bw); cv.drawLine(fx + ex - u * 0.1, by - u * 0.1, fx + ex + u * 0.12, by - u * 0.06, bw)
    my = fy + 0.33 * u; mw = 0.22 * u
    m = skia.Path(); sp = strokep(INK, u * 0.06)
    if expr in ('smile', 'neutral_smile'):
        m.moveTo(fx - mw, my - u * 0.03); m.quadTo(fx, my + u * 0.12, fx + mw, my - u * 0.03); cv.drawPath(m, sp)
    elif expr in ('grin', 'happy'):
        m.moveTo(fx - mw * 1.3, my - u * 0.06); m.quadTo(fx, my + u * 0.32, fx + mw * 1.3, my - u * 0.06); m.close()
        cv.drawPath(m, fillp(C('#4a1f25'))); cv.drawPath(m, strokep(INK, u * 0.05))
        cv.save(); cv.clipPath(m, doAntiAlias=True); cv.drawCircle(fx, my + u * 0.25, u * 0.13, fillp(C('#e8707a'))); cv.restore()
    elif expr in ('sad', 'tears'):
        m.moveTo(fx - mw, my + u * 0.06); m.quadTo(fx, my - u * 0.08, fx + mw, my + u * 0.06); cv.drawPath(m, sp)
    elif expr in ('shock', 'o'):
        cv.drawOval(skia.Rect(fx - u * 0.1, my - u * 0.05, fx + u * 0.1, my + u * 0.17), fillp(C('#4a1f25'))); cv.drawOval(skia.Rect(fx - u * 0.1, my - u * 0.05, fx + u * 0.1, my + u * 0.17), strokep(INK, u * 0.05))
    elif expr in ('smug',):
        m.moveTo(fx - mw * 0.6, my + u * 0.02); m.quadTo(fx + mw * 0.4, my + u * 0.06, fx + mw * 1.1, my - u * 0.07); cv.drawPath(m, sp)
    elif expr in ('worried', 'sorry'):
        m.moveTo(fx - mw, my + u * 0.03)
        for i in range(1, 5): m.lineTo(fx - mw + mw * 2 * i / 4, my + (u * 0.03 if i % 2 == 0 else -u * 0.03))
        cv.drawPath(m, sp)
    elif expr == 'tempted':
        m.moveTo(fx - mw, my); m.quadTo(fx, my + u * 0.05, fx + mw, my - u * 0.02); cv.drawPath(m, sp)
        cv.drawOval(skia.Rect(fx + mw * 0.6, my + u * 0.0, fx + mw * 0.95, my + u * 0.18), fillp(C('#8fd0ff')))  # drool
    elif expr == 'puffed':
        cv.drawCircle(fx - u * 0.42, my - u * 0.02, u * 0.2, fillp(C('#ffd0d0', 200))); cv.drawCircle(fx + u * 0.42, my - u * 0.02, u * 0.2, fillp(C('#ffd0d0', 200)))
        m.moveTo(fx - mw * 0.5, my); m.lineTo(fx + mw * 0.5, my); cv.drawPath(m, sp)
    elif expr == 'strain':
        r = skia.Rect(fx - mw * 1.2, my - u * 0.07, fx + mw * 1.2, my + u * 0.09)
        cv.drawRoundRect(r, u * 0.04, u * 0.04, fillp(C('#ffffff'))); cv.drawRoundRect(r, u * 0.04, u * 0.04, strokep(INK, u * 0.05))
        for i in range(1, 4): cv.drawLine(r.left() + r.width() * i / 4, r.top(), r.left() + r.width() * i / 4, r.bottom(), strokep(INK, u * 0.03))
        cv.drawLine(r.left(), my + u * 0.01, r.right(), my + u * 0.01, strokep(INK, u * 0.03))
    else:  # neutral / meh / stern
        m.moveTo(fx - mw * 0.8, my); m.lineTo(fx + mw * 0.8, my + (u * 0.02 if expr == 'meh' else 0)); cv.drawPath(m, sp)
    if expr == 'tears':
        cv.drawOval(skia.Rect(fx - ex - u * 0.05, fy + u * 0.08, fx - ex + u * 0.05, fy + u * 0.24), fillp(C('#7cc6ff')))
    if expr in ('worried', 'strain'):
        cv.drawOval(skia.Rect(x + u * 0.62, y - u * 0.55, x + u * 0.78, y - u * 0.3), fillp(C('#8fd0ff'))); cv.drawOval(skia.Rect(x + u * 0.62, y - u * 0.55, x + u * 0.78, y - u * 0.3), strokep(INK, u * 0.03))

def hair(cv, x, y, u, kind, back=False):
    ol = strokep(INK, u * 0.08)
    if kind == 'bald_grey' and not back:
        for s in (-1, 1):
            p = skia.Path(); p.moveTo(x + s * u * 0.78, y - u * 0.45)
            for i in range(5):
                a = -0.3 + i * 0.32
                p.quadTo(x + s * (u * 1.18), y - u * 0.4 + i * u * 0.18, x + s * u * 0.92, y - u * 0.25 + i * u * 0.16)
            p.lineTo(x + s * u * 0.85, y + u * 0.2); p.close()
            cv.drawPath(p, fillp(C('#cfd3d8'))); cv.drawPath(p, ol)
    if kind == 'pony':
        if back:
            p = skia.Path(); p.moveTo(x + u * 0.6, y - u * 0.5); p.quadTo(x + u * 1.6, y - u * 0.4, x + u * 1.25, y + u * 0.7); p.quadTo(x + u * 1.1, y + u * 0.1, x + u * 0.5, y - u * 0.2); p.close()
            cv.drawPath(p, fillp(C('#5a3a28'))); cv.drawPath(p, ol)
        else:
            p = skia.Path(); p.addArc(skia.Rect(x - u * 1.02, y - u * 1.0, x + u * 1.02, y + u * 0.9), 180, 180)
            p.quadTo(x + u * 0.4, y - u * 0.75, x - u * 0.1, y - u * 0.55); p.quadTo(x - u * 0.6, y - u * 0.4, x - u * 1.02, y - u * 0.05); p.close()
            cv.drawPath(p, fillp(C('#6b4430'))); cv.drawPath(p, ol)
    if kind == 'bun' and not back:
        cv.drawCircle(x, y - u * 1.05, u * 0.38, fillp(C('#2e2a33'))); cv.drawCircle(x, y - u * 1.05, u * 0.38, ol)
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.02, y - u * 0.98, x + u * 1.02, y + u * 0.9), 180, 180); p.quadTo(x, y - u * 0.5, x - u * 1.02, y - u * 0.04); p.close()
        cv.drawPath(p, fillp(C('#2e2a33'))); cv.drawPath(p, ol)
    if kind == 'cowlick' and not back:
        p = skia.Path(); p.moveTo(x - u * 0.85, y - u * 0.45)
        p.quadTo(x - u * 0.6, y - u * 1.15, x + u * 0.1, y - u * 1.0); p.quadTo(x + u * 0.25, y - u * 1.45, x + u * 0.55, y - u * 1.3)
        p.quadTo(x + u * 0.35, y - u * 1.1, x + u * 0.45, y - u * 0.98); p.quadTo(x + u * 0.9, y - u * 0.85, x + u * 0.9, y - u * 0.45)
        p.quadTo(x + u * 0.3, y - u * 0.7, x - u * 0.85, y - u * 0.45); p.close()
        cv.drawPath(p, fillp(C('#7a4a26'))); cv.drawPath(p, ol)
    if kind == 'bob' and not back:
        p = skia.Path(); p.moveTo(x - u * 1.08, y + u * 0.35); p.quadTo(x - u * 1.25, y - u * 1.25, x, y - u * 1.08)
        p.quadTo(x + u * 1.25, y - u * 1.25, x + u * 1.08, y + u * 0.35); p.lineTo(x + u * 0.8, y + u * 0.35)
        p.quadTo(x + u * 0.85, y - u * 0.4, x + u * 0.2, y - u * 0.5); p.lineTo(x - u * 0.8, y - u * 0.35); p.quadTo(x - u * 0.85, y, x - u * 0.8, y + u * 0.35); p.close()
        cv.drawPath(p, fillp(C('#1f1d24'))); cv.drawPath(p, ol)
    if kind == 'curly' and not back:
        pts = [(-0.85, -0.45), (-0.7, -0.85), (-0.35, -1.05), (0.05, -1.12), (0.45, -1.02), (0.78, -0.8), (0.9, -0.42)]
        for (a, b) in pts: cv.drawCircle(x + a * u, y + b * u, u * 0.3, fillp(C('#c6622c')))
        for (a, b) in pts: cv.drawCircle(x + a * u, y + b * u, u * 0.3, strokep(INK, u * 0.06))
        for (a, b) in pts: cv.drawCircle(x + a * u, y + b * u, u * 0.26, fillp(C('#c6622c')))
        cv.drawCircle(x + 0.0 * u, y - 0.75 * u, u * 0.35, fillp(C('#c6622c')))
    if kind == 'spiky' and not back:
        p = skia.Path(); p.moveTo(x - u * 0.9, y - u * 0.35)
        for i, (a, b) in enumerate([(-0.85, -1.05), (-0.45, -0.8), (-0.25, -1.3), (0.05, -0.85), (0.35, -1.25), (0.5, -0.8), (0.9, -1.0), (0.88, -0.35)]):
            p.lineTo(x + a * u, y + b * u)
        p.quadTo(x, y - u * 0.65, x - u * 0.9, y - u * 0.35); p.close()
        cv.drawPath(p, fillp(C('#e9c35a'))); cv.drawPath(p, ol)

def character(cv, name, x, y, u, t=0.0, expr='neutral', pose=None, look=(0, 0), blink_seed=0, facing=0, flip=False):
    """x,y = feet position (ground contact). u = head radius."""
    spec = CHARS[name]; pose = pose or {}
    adult = spec['adult']
    lw = u * 0.085
    sit = pose.get('sit', False)
    legL = (1.75 if adult else 0.85) * u
    torso_h = (1.45 if adult else 0.95) * u
    torso_w = (1.05 if adult else 0.95) * u
    bob = math.sin(t * 2.4 + blink_seed) * u * 0.025 + pose.get('dy', 0)
    walk = pose.get('walk', 0)  # phase speed; 0 = standing
    hip_y = y - (legL if not sit else legL * 0.35) + bob
    if walk: hip_y -= abs(math.sin(t * walk)) * u * 0.08
    soft_shadow(cv, x, y + 2, u * 0.95, u * 0.17, 0.33)
    # legs
    lp = strokep(INK, lw)
    if sit:
        for s in (-1, 1):
            hx = x + s * torso_w * 0.22
            kx = hx + s * u * 0.08; ky = hip_y + u * 0.12
            path = skia.Path(); path.moveTo(hx, hip_y); path.lineTo(kx, ky + u * 0.02); path.lineTo(kx, y)
            cv.drawPath(path, lp); cv.drawLine(kx, y, kx + s * u * 0.12, y, lp)
    else:
        for s in (-1, 1):
            hx = x + s * torso_w * 0.2
            sw = math.sin(t * walk + (0 if s < 0 else math.pi)) * u * 0.45 if walk else 0
            fx = hx + sw + facing * u * 0.05
            fy = y - (max(0, math.sin(t * walk + (0 if s < 0 else math.pi))) * u * 0.18 if walk else 0)
            cv.drawLine(hx, hip_y, fx, fy, lp)
            cv.drawLine(fx, fy, fx + (facing or s) * u * 0.13, fy, lp)
    # torso
    top = hip_y - torso_h
    body = skia.Path()
    body.moveTo(x - torso_w * 0.42, top + u * 0.05)
    body.quadTo(x - torso_w * 0.6, top + torso_h * 0.55, x - torso_w * 0.5, hip_y)
    body.lineTo(x + torso_w * 0.5, hip_y)
    body.quadTo(x + torso_w * 0.6, top + torso_h * 0.55, x + torso_w * 0.42, top + u * 0.05)
    body.close()
    shirt = spec['shirt']
    # pants band
    pants_h = torso_h * (0.18 if adult else 0.26)
    cv.drawPath(body, fillp(shader=lin((x - torso_w * 0.6, 0), (x + torso_w * 0.6, 0), [shade(shirt, 1.06), shade(shirt, 0.86)])))
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    if spec.get('inner') is not None:
        cv.drawPath(poly([(x - torso_w * 0.18, top), (x + torso_w * 0.18, top), (x + torso_w * 0.1, hip_y), (x - torso_w * 0.1, hip_y)]), fillp(spec['inner']))
    if spec.get('coat'):
        cv.drawPath(poly([(x - torso_w * 0.22, top), (x, top + torso_h * 0.42), (x + torso_w * 0.22, top)]), fillp(C('#dfe6ea') if spec.get('inner') is None else spec['inner']))
        cv.drawLine(x, top + torso_h * 0.42, x, hip_y, strokep(C('#c9cfd6'), u * 0.04))
        cv.drawLine(x - torso_w * 0.22, top, x - torso_w * 0.02, top + torso_h * 0.45, strokep(C('#c9cfd6'), u * 0.05))
        cv.drawLine(x + torso_w * 0.22, top, x + torso_w * 0.02, top + torso_h * 0.45, strokep(C('#c9cfd6'), u * 0.05))
        cv.drawRect(skia.Rect(x + torso_w * 0.15, top + torso_h * 0.55, x + torso_w * 0.38, top + torso_h * 0.7), strokep(C('#c9cfd6'), u * 0.035))
        cv.drawLine(x + torso_w * 0.2, top + torso_h * 0.5, x + torso_w * 0.2, top + torso_h * 0.6, strokep(C('#3a6ec2'), u * 0.04))
        if spec.get('tie') is not None:
            cv.drawPath(poly([(x - u * 0.07, top + u * 0.03), (x + u * 0.07, top + u * 0.03), (x + u * 0.1, top + torso_h * 0.38), (x, top + torso_h * 0.45), (x - u * 0.1, top + torso_h * 0.38)]), fillp(spec['tie']))
        if spec.get('badge'):
            cv.drawRoundRect(skia.Rect(x - torso_w * 0.4, top + torso_h * 0.3, x - torso_w * 0.18, top + torso_h * 0.46), 4, 4, fillp(C('#ffffff')))
            cv.drawRoundRect(skia.Rect(x - torso_w * 0.4, top + torso_h * 0.3, x - torso_w * 0.18, top + torso_h * 0.46), 4, 4, strokep(C('#3a6ec2'), u * 0.03))
    elif spec.get('stripe') is not None:
        for k in (0.35, 0.6):
            cv.drawRect(skia.Rect(x - torso_w, top + torso_h * k, x + torso_w, top + torso_h * (k + 0.1)), fillp(spec['stripe']))
    cv.drawRect(skia.Rect(x - torso_w, hip_y - pants_h, x + torso_w, hip_y + 2), fillp(spec['pants']))
    cv.restore()
    cv.drawPath(body, strokep(INK, lw * 0.9))
    # arms
    sl = (x - torso_w * 0.44, top + u * 0.22); sr = (x + torso_w * 0.44, top + u * 0.22)
    armL = (1.4 if adult else 0.95) * u
    hl = pose.get('hl', (-0.22, 0.95)); hr = pose.get('hr', (0.22, 0.95))
    if 'hlA' in pose: hl = pose['hlA']
    else: hl = (sl[0] + hl[0] * armL, sl[1] + hl[1] * armL)
    if 'hrA' in pose: hr = pose['hrA']
    else: hr = (sr[0] + hr[0] * armL, sr[1] + hr[1] * armL)
    def draw_arms():
        _arm(cv, *sl, *hl, pose.get('bl', -u * 0.15), lw)
        _arm(cv, *sr, *hr, pose.get('br', u * 0.15), lw)
    if not pose.get('arms_front', False): draw_arms()
    # head
    hy = top - u * 0.82
    hx = x + pose.get('hdx', 0)
    tilt = pose.get('tilt', 0)
    cv.save(); cv.rotate(tilt, hx, hy + u * 0.8)
    hair(cv, hx, hy, u, spec['hair'], back=True)
    hr_ = skia.Rect(hx - u * 1.0, hy - u * 0.95, hx + u * 1.0, hy + u * 0.92)
    cv.drawOval(hr_, fillp(shader=rad((hx - u * 0.35, hy - u * 0.4), u * 1.6, [C('#ffffff'), HEAD, C('#d9d6cf')], [0, 0.55, 1])))
    cv.drawOval(hr_, strokep(INK, lw))
    hair(cv, hx, hy, u, spec['hair'])
    blink = ((t + blink_seed * 1.7) % 3.3) < 0.12 if pose.get('blink', True) else False
    face(cv, hx, hy, u, expr, blink, look)
    if spec.get('glasses'):
        gl = strokep(INK, u * 0.05); fx = hx + look[0] * u * 0.18; fy = hy + look[1] * u * 0.12
        for s in (-1, 1): cv.drawCircle(fx + s * u * 0.33, fy - u * 0.02, u * 0.22, gl)
        cv.drawLine(fx - u * 0.11, fy - u * 0.04, fx + u * 0.11, fy - u * 0.04, gl)
    cv.restore()
    if pose.get('arms_front', False): draw_arms()
    return dict(sl=sl, sr=sr, hl=hl, hr=hr, head=(hx, hy), top=top, hip=hip_y)

# ---- additions for the Japan story
CHARS.update({
    'man':   dict(adult=True, shirt=C('#7d8f6e'), stripe=None, hair='short', pants=C('#5a4a3a')),
    'woman': dict(adult=True, shirt=C('#b9a68c'), stripe=None, hair='bun_grey', pants=C('#6b5f57')),
    'cop':   dict(adult=True, shirt=C('#2f3f66'), stripe=None, tie=None, hair='cap', pants=C('#232f4d')),
    'cop2':  dict(adult=True, shirt=C('#2f3f66'), stripe=None, hair='cap', pants=C('#232f4d')),
})
_hair_old = hair
def hair(cv, x, y, u, kind, back=False):
    ol = strokep(INK, u * 0.08)
    if kind == 'short':
        if back: return
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.02, y - u * 0.97, x + u * 1.02, y + u * 0.9), 180, 180)
        p.lineTo(x + u * 0.98, y - u * 0.2); p.quadTo(x + u * 0.6, y - u * 0.55, x + u * 0.1, y - u * 0.52)
        p.lineTo(x - u * 0.2, y - u * 0.62); p.quadTo(x - u * 0.7, y - u * 0.5, x - u * 0.98, y - u * 0.2); p.close()
        cv.drawPath(p, fillp(C('#26232b'))); cv.drawPath(p, ol)
        # grey temples
        cv.drawCircle(x - u * 0.9, y - u * 0.25, u * 0.1, fillp(C('#9a9aa2'))); cv.drawCircle(x + u * 0.9, y - u * 0.25, u * 0.1, fillp(C('#9a9aa2')))
        return
    if kind == 'bun_grey':
        if back: return
        cv.drawCircle(x + u * 0.1, y - u * 1.08, u * 0.36, fillp(C('#a7a4a8'))); cv.drawCircle(x + u * 0.1, y - u * 1.08, u * 0.36, ol)
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.03, y - u * 0.98, x + u * 1.03, y + u * 0.9), 180, 180)
        p.lineTo(x + u * 1.0, y + u * 0.05); p.quadTo(x + u * 0.5, y - u * 0.6, x - u * 0.05, y - u * 0.55); p.quadTo(x - u * 0.6, y - u * 0.55, x - u * 1.0, y + u * 0.05); p.close()
        cv.drawPath(p, fillp(C('#b8b5b9'))); cv.drawPath(p, ol)
        for i in range(3): cv.drawLine(x - u * 0.6 + i * u * 0.35, y - u * 0.8, x - u * 0.45 + i * u * 0.35, y - u * 0.5, strokep(C('#8d8a90'), u * 0.04))
        return
    if kind == 'cap':
        if back: return
        p = skia.Path(); p.moveTo(x - u * 0.95, y - u * 0.45); p.quadTo(x - u * 1.0, y - u * 1.25, x, y - u * 1.22)
        p.quadTo(x + u * 1.0, y - u * 1.25, x + u * 0.95, y - u * 0.45); p.close()
        cv.drawPath(p, fillp(C('#243256'))); cv.drawPath(p, ol)
        brim = skia.Rect(x - u * 1.05, y - u * 0.58, x + u * 1.05, y - u * 0.36)
        cv.drawRoundRect(brim, u * 0.1, u * 0.1, fillp(C('#151c33'))); cv.drawRoundRect(brim, u * 0.1, u * 0.1, ol)
        cv.drawCircle(x, y - u * 0.85, u * 0.16, fillp(C('#e6c04a'))); cv.drawCircle(x, y - u * 0.85, u * 0.16, strokep(INK, u * 0.04))
        return
    return _hair_old(cv, x, y, u, kind, back)

def lying(cv, name, x, y, u, t, expr='shock', look=(0, 0), lift=0):
    """character lying on its back; x,y = where the hips rest; head to the right."""
    cv.save(); cv.translate(x, y); cv.rotate(90 - lift)
    character(cv, name, 0, u * 1.75, u, t=t, expr=expr, look=look, pose={'hl': (-0.3, 0.9), 'hr': (0.3, 0.9), 'blink': True})
    cv.restore()

# ---- additions for the Dagsa story
CHARS.update({
    'dagsa': dict(adult=True, shirt=C('#f4f4f0'), stripe=None, hair='short_black', pants=C('#3b4a6b')),
    'wife':  dict(adult=True, shirt=C('#e86a8a'), stripe=None, hair='long', pants=C('#3b3550')),
    'girl':  dict(adult=False, shirt=C('#ffd166'), stripe=C('#ff8fa3'), hair='pigtails', pants=C('#5b7fb8')),
    'mil':   dict(adult=True, shirt=C('#7ec4b8'), stripe=None, hair='bun_grey', pants=C('#4b4a5a')),
    'gunman':dict(adult=True, shirt=C('#2a2f3d'), stripe=None, hair='bcap', pants=C('#1c202b')),
    'sus1':  dict(adult=True, shirt=C('#c96b5b'), stripe=None, hair='spiky', pants=C('#3a3a44')),
    'sus2':  dict(adult=True, shirt=C('#8a9a5b'), stripe=None, hair='short', pants=C('#3a3a44')),
    'gf':    dict(adult=True, shirt=C('#9b6fc7'), stripe=None, hair='long', pants=C('#2f2f3a')),
})
_hair_old2 = hair
def hair(cv, x, y, u, kind, back=False):
    ol = strokep(INK, u * 0.08)
    if kind == 'short_black':
        if back: return
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.02, y - u * 0.97, x + u * 1.02, y + u * 0.9), 180, 180)
        p.lineTo(x + u * 0.98, y - u * 0.25); p.quadTo(x + u * 0.3, y - u * 0.75, x - u * 0.3, y - u * 0.55); p.quadTo(x - u * 0.8, y - u * 0.45, x - u * 0.98, y - u * 0.2); p.close()
        cv.drawPath(p, fillp(C('#18161c'))); cv.drawPath(p, ol); return
    if kind == 'long':
        col = C('#2b1d18')
        if back:
            p = skia.Path(); p.moveTo(x - u * 1.0, y - u * 0.3); p.quadTo(x - u * 1.3, y + u * 1.0, x - u * 0.85, y + u * 1.45)
            p.lineTo(x + u * 0.85, y + u * 1.45); p.quadTo(x + u * 1.3, y + u * 1.0, x + u * 1.0, y - u * 0.3); p.close()
            cv.drawPath(p, fillp(col)); cv.drawPath(p, ol); return
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.04, y - u * 1.0, x + u * 1.04, y + u * 0.9), 180, 180)
        p.lineTo(x + u * 1.02, y + u * 0.15); p.quadTo(x + u * 0.75, y - u * 0.5, x + u * 0.05, y - u * 0.62); p.quadTo(x - u * 0.7, y - u * 0.5, x - u * 1.02, y + u * 0.15); p.close()
        cv.drawPath(p, fillp(col)); cv.drawPath(p, ol); return
    if kind == 'pigtails':
        col = C('#2b1d18')
        if back:
            for s in (-1, 1):
                cv.drawCircle(x + s * u * 1.15, y - u * 0.35, u * 0.38, fillp(col)); cv.drawCircle(x + s * u * 1.15, y - u * 0.35, u * 0.38, ol)
            return
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.03, y - u * 0.98, x + u * 1.03, y + u * 0.9), 180, 180)
        p.quadTo(x + u * 0.4, y - u * 0.6, x, y - u * 0.4); p.quadTo(x - u * 0.4, y - u * 0.6, x - u * 1.03, y - u * 0.04); p.close()
        cv.drawPath(p, fillp(col)); cv.drawPath(p, ol)
        for s in (-1, 1): cv.drawCircle(x + s * u * 0.92, y - u * 0.55, u * 0.1, fillp(C('#ff5c8a')))
        return
    if kind == 'bcap':
        if back: return
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.02, y - u * 1.12, x + u * 1.02, y + u * 0.3), 180, 180); p.close()
        cv.drawPath(p, fillp(C('#2a5bd7'))); cv.drawPath(p, ol)
        brim = poly([(x - u * 0.2, y - u * 0.44), (x + u * 1.45, y - u * 0.5), (x + u * 1.4, y - u * 0.3), (x - u * 0.2, y - u * 0.3)])
        cv.drawPath(brim, fillp(C('#1f47aa'))); cv.drawPath(brim, ol)
        cv.drawCircle(x + u * 0.1, y - u * 0.78, u * 0.2, fillp(C('#e2483b'))); cv.drawCircle(x + u * 0.1, y - u * 0.78, u * 0.2, strokep(INK, u * 0.04))
        return
    return _hair_old2(cv, x, y, u, kind, back)

def silhouette(cv, fn, glint=None):
    """draw fn() fully darkened (keeps shape), optional eye glints."""
    p = skia.Paint(); p.setColorFilter(skia.ColorFilters.Matrix([0.1,0,0,0,0.04, 0,0.1,0,0,0.05, 0,0,0.12,0,0.09, 0,0,0,1,0]))
    cv.saveLayer(None, p); fn(); cv.restore()
    if glint:
        for gx, gy in glint: cv.drawCircle(gx, gy, 4, fillp(C('#ffffff')))

def gun(cv, x, y, s=1.0, ang=0):
    cv.save(); cv.translate(x, y); cv.rotate(ang); cv.scale(s, s)
    cv.drawPath(poly([(-8, -14), (62, -14), (62, 2), (14, 2), (12, 28), (-6, 28), (-8, 2)]), fillp(C('#15171d'))); cv.drawPath(poly([(-8, -14), (62, -14), (62, 2), (14, 2), (12, 28), (-6, 28), (-8, 2)]), strokep(C('#4a4f5a'), 2))
    cv.restore()

def cam_compact(cv, x, y, s=1.0, back_view=False, screen_fn=None):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    body = skia.Rect(-110, -70, 110, 70)
    cv.drawRoundRect(body, 18, 18, fillp(shader=lin((0, -70), (0, 70), [C('#5a5f6a'), C('#2c2f36')]))); cv.drawRoundRect(body, 18, 18, strokep(INK, 6))
    if not back_view:
        cv.drawCircle(10, 5, 52, fillp(C('#1b1d24'))); cv.drawCircle(10, 5, 52, strokep(C('#9aa0aa'), 8)); cv.drawCircle(10, 5, 28, fillp(C('#2f4a7a'))); cv.drawCircle(-2, -8, 9, fillp(C('#cfe3ff')))
        cv.drawRect(skia.Rect(60, -55, 95, -35), fillp(C('#e9eef3')))
    else:
        sc = skia.Rect(-95, -55, 55, 55); cv.drawRect(sc, fillp(C('#0b0d12')))
        if screen_fn: cv.save(); cv.clipRect(sc); screen_fn(sc); cv.restore()
        cv.drawRect(sc, strokep(INK, 4))
        for i in range(3): cv.drawCircle(80, -35 + i * 35, 10, fillp(C('#8a8f99')))
    cv.drawRect(skia.Rect(40, -86, 85, -70), fillp(C('#3a3e47')))
    cv.restore()

CHARS.update({
    'wife':  dict(adult=True, shirt=C('#e8553a'), stripe=None, hair='long', pants=C('#3b3550')),
    'girl':  dict(adult=False, shirt=C('#f4a6c8'), stripe=C('#fbd3e4'), hair='long', pants=C('#5b7fb8')),
    'girl_p':dict(adult=True, shirt=C('#f4a6c8'), stripe=None, hair='long', pants=C('#5b7fb8')),
    'mil':   dict(adult=True, shirt=C('#3a8fd6'), stripe=None, hair='bun_grey', pants=C('#4b4a5a')),
    'bystander': dict(adult=True, shirt=C('#f1f1ee'), stripe=None, hair='short_black', pants=C('#3a3a44')),
})

# ---- Malloy story
CHARS.update({
    'malloy': dict(adult=True, shirt=C('#7a5a3a'), stripe=None, hair='flatcap', pants=C('#4a3a2a')),
    'marino': dict(adult=True, shirt=C('#7a2a2a'), stripe=None, hair='slick', pants=C('#2a2a33')),
    'pasqua': dict(adult=True, shirt=C('#26262e'), stripe=None, tie=C('#b8b8c0'), coat=False, hair='short', pants=C('#1a1a22')),
    'murphy': dict(adult=True, shirt=C('#f1efe6'), stripe=None, hair='bald_grey', pants=C('#3a3a44')),
    'kries':  dict(adult=True, shirt=C('#5a7a4a'), stripe=None, hair='cowlick', pants=C('#3a3a33')),
    'cabbie': dict(adult=True, shirt=C('#c9a440'), stripe=None, hair='flatcap_dark', pants=C('#3a3a44')),
    'agent':  dict(adult=True, shirt=C('#4a5a7a'), stripe=None, hair='short', glasses=True, pants=C('#2a2f3d')),
})
_hair_old3 = hair
def hair(cv, x, y, u, kind, back=False):
    ol = strokep(INK, u * 0.08)
    if kind in ('flatcap', 'flatcap_dark'):
        if back: return
        col = C('#8a6a48') if kind == 'flatcap' else C('#3a3a44')
        p = skia.Path(); p.moveTo(x - u * 1.0, y - u * 0.35); p.quadTo(x - u * 0.9, y - u * 1.2, x + u * 0.1, y - u * 1.1)
        p.quadTo(x + u * 1.2, y - u * 1.0, x + u * 1.35, y - u * 0.45); p.lineTo(x + u * 1.0, y - u * 0.35); p.close()
        cv.drawPath(p, fillp(col)); cv.drawPath(p, ol)
        cv.drawLine(x - u * 0.95, y - u * 0.4, x + u * 1.25, y - u * 0.45, strokep(shade(col, 0.7), u * 0.06))
        cv.drawLine(x - u * 0.2, y - u * 1.08, x - u * 0.1, y - u * 0.5, strokep(shade(col, 0.8), u * 0.04))
        return
    if kind == 'slick':
        if back: return
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.02, y - u * 0.97, x + u * 1.02, y + u * 0.9), 180, 180)
        p.lineTo(x + u * 1.0, y - u * 0.3); p.quadTo(x + u * 0.2, y - u * 0.4, x - u * 0.35, y - u * 0.72); p.quadTo(x - u * 0.8, y - u * 0.5, x - u * 1.0, y - u * 0.3); p.close()
        cv.drawPath(p, fillp(C('#121014'))); cv.drawPath(p, ol)
        cv.drawLine(x - u * 0.4, y - u * 0.85, x + u * 0.5, y - u * 0.55, strokep(C('#4a4a5a'), u * 0.05))
        return
    return _hair_old3(cv, x, y, u, kind, back)

def malloy_extras(cv, ch, u, nose=True, stubble=True, bandage=False, snow=False):
    hx, hy = ch['head']
    if stubble:
        rnd = random.Random(3)
        for i in range(22):
            a = rnd.uniform(0.15, 0.85) * math.pi; r = rnd.uniform(0.55, 0.85) * u
            cv.drawCircle(hx + math.cos(a) * r * 0.95, hy + math.sin(a) * r * 0.75 + u * 0.1, u * 0.025, fillp(C('#6a6a70')))
    if nose:
        cv.drawCircle(hx, hy + u * 0.16, u * 0.13, fillp(C('#e86a6a'))); cv.drawCircle(hx, hy + u * 0.16, u * 0.13, strokep(INK, u * 0.04))
        cv.drawCircle(hx - u * 0.48, hy + u * 0.2, u * 0.13, fillp(C('#ff9a9a'), alpha=0.55)); cv.drawCircle(hx + u * 0.48, hy + u * 0.2, u * 0.13, fillp(C('#ff9a9a'), alpha=0.55))
    if bandage:
        cv.save(); cv.rotate(-18, hx, hy)
        cv.drawRect(skia.Rect(hx - u * 1.02, hy - u * 0.62, hx + u * 1.02, hy - u * 0.36), fillp(C('#f6f3ea'))); cv.drawRect(skia.Rect(hx - u * 1.02, hy - u * 0.62, hx + u * 1.02, hy - u * 0.36), strokep(INK, u * 0.04))
        cv.restore()
        cv.drawRect(skia.Rect(hx + u * 0.3, hy + u * 0.35, hx + u * 0.65, hy + u * 0.48), fillp(C('#f6e3c8'))); cv.drawRect(skia.Rect(hx + u * 0.3, hy + u * 0.35, hx + u * 0.65, hy + u * 0.48), strokep(INK, u * 0.03))
        cv.drawLine(hx + u * 0.38, hy + u * 0.35, hx + u * 0.38, hy + u * 0.48, strokep(INK, u * 0.02)); cv.drawLine(hx + u * 0.56, hy + u * 0.35, hx + u * 0.56, hy + u * 0.48, strokep(INK, u * 0.02))
    if snow:
        for (dx, dy, r) in ((-0.6, -1.1, 0.22), (0.1, -1.18, 0.26), (0.8, -0.95, 0.2)):
            cv.drawCircle(hx + dx * u, hy + dy * u, r * u, fillp(C('#ffffff'))); cv.drawCircle(hx + dx * u, hy + dy * u, r * u, strokep(INK, u * 0.03))
        cv.drawPath(poly([(hx - u * 0.06, hy + u * 0.25), (hx + u * 0.06, hy + u * 0.25), (hx, hy + u * 0.55)]), fillp(C('#cfefff'))); cv.drawPath(poly([(hx - u * 0.06, hy + u * 0.25), (hx + u * 0.06, hy + u * 0.25), (hx, hy + u * 0.55)]), strokep(INK, u * 0.025))

def glass(cv, x, y, s=1.0, fill=0.7, col=C('#d9a441')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    body = poly([(-34, -90), (34, -90), (28, 0), (-28, 0)])
    cv.save(); cv.clipPath(body, doAntiAlias=True)
    cv.drawRect(skia.Rect(-40, -90 * fill, 40, 0), fillp(col)); cv.drawRect(skia.Rect(-40, -90 * fill, 40, -90 * fill + 8), fillp(shade(col, 1.25)))
    cv.restore()
    cv.drawPath(body, fillp(skia.Color(255, 255, 255, 50))); cv.drawPath(body, strokep(INK, 5))
    cv.drawLine(-22, -78, -18, -12, strokep(C('#ffffff'), 5, alpha=0.6))
    cv.restore()

def bottle(cv, x, y, s=1.0, label='WHISKEY', col=C('#7a4a1e'), skull=False, lab_col=C('#f3e6c4')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    p = skia.Path(); p.moveTo(-16, -260); p.lineTo(16, -260); p.lineTo(16, -190); p.quadTo(60, -170, 60, -120); p.lineTo(60, 0); p.lineTo(-60, 0); p.lineTo(-60, -120); p.quadTo(-60, -170, -16, -190); p.close()
    cv.drawPath(p, fillp(shader=lin((-60, 0), (60, 0), [shade(col, 1.2), col, shade(col, 0.7)])))
    cv.drawPath(p, strokep(INK, 6))
    cv.drawRect(skia.Rect(-20, -280, 20, -255), fillp(C('#c9a46a'))); cv.drawRect(skia.Rect(-20, -280, 20, -255), strokep(INK, 4))
    r = skia.Rect(-50, -105, 50, -25); cv.drawRect(r, fillp(lab_col)); cv.drawRect(r, strokep(INK, 4))
    if skull:
        cv.drawCircle(0, -78, 18, fillp(INK)); cv.drawRect(skia.Rect(-10, -66, 10, -56), fillp(INK))
        cv.drawCircle(-7, -80, 5, fillp(lab_col)); cv.drawCircle(7, -80, 5, fillp(lab_col))
        cv.drawLine(-26, -50, 26, -34, strokep(INK, 6)); cv.drawLine(26, -50, -26, -34, strokep(INK, 6))
        text(cv, label, 0, -112, 16, C('#c0392b'))
    else:
        text(cv, label, 0, -58, 20, INK)
    cv.drawLine(-38, -170, -30, -20, strokep(C('#ffffff'), 6, alpha=0.35))
    cv.restore()

# ---- Gage story
CHARS.update({
    'gage':    dict(adult=True, shirt=C('#4f78b0'), stripe=None, hair='sidepart', pants=C('#5a4a3a')),
    'doctor':  dict(adult=True, shirt=C('#26262e'), stripe=None, hair='tophat', pants=C('#1a1a22'), glasses=True),
    'mother':  dict(adult=True, shirt=C('#8a5a7a'), stripe=None, hair='bun_grey', pants=C('#4a3a4a')),
    'worker1': dict(adult=True, shirt=C('#b05a3a'), stripe=None, hair='flatcap', pants=C('#4a3a2a')),
    'worker2': dict(adult=True, shirt=C('#6a8a4a'), stripe=None, hair='spiky', pants=C('#3a3a33')),
    'historian': dict(adult=True, shirt=C('#7a6a8a'), stripe=None, hair='bald_grey', glasses=True, pants=C('#3a3a44')),
})
_hair_old4 = hair
def hair(cv, x, y, u, kind, back=False):
    ol = strokep(INK, u * 0.08)
    if kind == 'sidepart':
        if back: return
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.03, y - u * 0.98, x + u * 1.03, y + u * 0.9), 180, 180)
        p.lineTo(x + u * 1.0, y - u * 0.15); p.quadTo(x + u * 0.8, y - u * 0.55, x - u * 0.25, y - u * 0.62)
        p.quadTo(x - u * 0.8, y - u * 0.5, x - u * 1.0, y - u * 0.15); p.close()
        cv.drawPath(p, fillp(C('#5a3a22'))); cv.drawPath(p, ol)
        cv.drawLine(x - u * 0.35, y - u * 0.95, x - u * 0.25, y - u * 0.62, strokep(C('#3a2412'), u * 0.05))
        return
    if kind == 'tophat':
        if back: return
        cv.drawRoundRect(skia.Rect(x - u * 1.3, y - u * 0.82, x + u * 1.3, y - u * 0.6), u * 0.1, u * 0.1, fillp(C('#16161c'))); cv.drawRoundRect(skia.Rect(x - u * 1.3, y - u * 0.82, x + u * 1.3, y - u * 0.6), u * 0.1, u * 0.1, ol)
        cv.drawRect(skia.Rect(x - u * 0.75, y - u * 1.9, x + u * 0.75, y - u * 0.78), fillp(C('#16161c'))); cv.drawRect(skia.Rect(x - u * 0.75, y - u * 1.9, x + u * 0.75, y - u * 0.78), ol)
        cv.drawRect(skia.Rect(x - u * 0.75, y - u * 1.05, x + u * 0.75, y - u * 0.88), fillp(C('#7a2a2a')))
        for s in (-1, 1): cv.drawCircle(x + s * u * 0.92, y - u * 0.3, u * 0.14, fillp(C('#d8d8dc')))
        return
    return _hair_old4(cv, x, y, u, kind, back)

def eyepatch(cv, ch, u):
    hx, hy = ch['head']; ex = hx + u * 0.33; ey = hy - u * 0.02
    cv.drawLine(hx - u * 0.95, hy - u * 0.45, hx + u * 0.98, hy + u * 0.15, strokep(INK, u * 0.06))
    cv.drawOval(skia.Rect(ex - u * 0.22, ey - u * 0.2, ex + u * 0.22, ey + u * 0.2), fillp(C('#18161c')))

def head_bandage(cv, ch, u):
    hx, hy = ch['head']
    cv.drawRect(skia.Rect(hx - u * 1.02, hy - u * 0.72, hx + u * 1.02, hy - u * 0.42), fillp(C('#f6f3ea'))); cv.drawRect(skia.Rect(hx - u * 1.02, hy - u * 0.72, hx + u * 1.02, hy - u * 0.42), strokep(INK, u * 0.04))
    cv.drawOval(skia.Rect(hx - u * 0.35, hy - u * 1.05, hx + u * 0.35, hy - u * 0.62), fillp(C('#f6f3ea'))); cv.drawOval(skia.Rect(hx - u * 0.35, hy - u * 1.05, hx + u * 0.35, hy - u * 0.62), strokep(INK, u * 0.04))
    cv.drawRect(skia.Rect(hx + u * 0.15, hy + u * 0.2, hx + u * 0.55, hy + u * 0.36), fillp(C('#f6e3c8'))); cv.drawRect(skia.Rect(hx + u * 0.15, hy + u * 0.2, hx + u * 0.55, hy + u * 0.36), strokep(INK, u * 0.03))

def rod(cv, x0, y0, x1, y1, w=16, alpha=1.0):
    cv.drawLine(x0, y0, x1, y1, strokep(C('#3a3e47'), w + 6, cap=skia.Paint.kRound_Cap, alpha=alpha))
    cv.drawLine(x0, y0, x1, y1, strokep(C('#8a909c'), w, alpha=alpha))
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy) or 1
    cv.drawLine(x0 - dy / L * w * 0.25, y0 + dx / L * w * 0.25, x1 - dy / L * w * 0.25, y1 + dx / L * w * 0.25, strokep(C('#c9ced8'), w * 0.25, alpha=alpha))

def skull(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawOval(skia.Rect(-110, -130, 110, 70), fillp(C('#efe6cf'))); cv.drawRoundRect(skia.Rect(-60, 40, 60, 120), 20, 20, fillp(C('#efe6cf')))
    cv.drawOval(skia.Rect(-110, -130, 110, 70), strokep(INK, 6)); cv.drawRoundRect(skia.Rect(-60, 40, 60, 120), 20, 20, strokep(INK, 6))
    for sx in (-1, 1): cv.drawOval(skia.Rect(sx * 45 - 30, -30, sx * 45 + 30, 25), fillp(C('#2a2420')))
    cv.drawPath(poly([(-10, 40), (10, 40), (0, 15)]), fillp(C('#2a2420')))
    for i in range(5): cv.drawLine(-44 + i * 22, 80, -44 + i * 22, 118, strokep(INK, 4))
    cv.drawCircle(-30, -100, 18, fillp(C('#3a3028')))  # exit hole on top, left side
    cv.restore()

# ---- Okene story
CHARS.update({
    'okene':  dict(adult=True, shirt=C('#f4f4f0'), stripe=None, hair='short_black', pants=C('#3a4a6b')),
    'diver':  dict(adult=True, shirt=C('#1c1f26'), stripe=C('#f0c020'), hair='divehelm', pants=C('#1c1f26')),
    'crew':   dict(adult=True, shirt=C('#e86a2a'), stripe=None, hair='flatcap_dark', pants=C('#3a3a44')),
})
_hair_old5 = hair
def hair(cv, x, y, u, kind, back=False):
    if kind == 'divehelm':
        if back:
            cv.drawCircle(x, y, u * 1.32, fillp(C('#e8b020'))); cv.drawCircle(x, y, u * 1.32, strokep(INK, u * 0.09)); return
        r = skia.Rect(x - u * 0.92, y - u * 0.85, x + u * 0.92, y + u * 0.85)
        cv.drawOval(r, fillp(skia.Color(160, 220, 255, 70))); cv.drawOval(r, strokep(C('#3a3e47'), u * 0.16)); cv.drawOval(r, strokep(INK, u * 0.05))
        cv.drawLine(x - u * 0.5, y - u * 0.55, x - u * 0.2, y - u * 0.65, strokep(C('#ffffff'), u * 0.07, alpha=0.6))
        cv.drawRoundRect(skia.Rect(x - u * 0.3, y - u * 1.55, x + u * 0.3, y - u * 1.25), u * 0.08, u * 0.08, fillp(C('#3a3e47'))); cv.drawCircle(x, y - u * 1.4, u * 0.12, fillp(C('#fff6c0')))
        cv.drawRect(skia.Rect(x + u * 1.1, y - u * 0.2, x + u * 1.45, y + u * 0.2), fillp(C('#3a3e47')))
        return
    return _hair_old5(cv, x, y, u, kind, back)

def beam(cv, x, y, tx, ty, w=0.4, a=120):
    ang = math.atan2(ty - y, tx - x); L = math.hypot(tx - x, ty - y)
    px, py = -math.sin(ang), math.cos(ang)
    cv.drawPath(poly([(x + px * 14, y + py * 14), (tx + px * L * w, ty + py * L * w), (tx - px * L * w, ty - py * L * w), (x - px * 14, y - py * 14)]),
                fillp(shader=lin((x, y), (tx, ty), [skia.Color(230, 250, 255, a), skia.Color(200, 240, 255, 0)]), blur=18, blend=skia.BlendMode.kScreen))

def bubbles(cv, T, x, y, n=8, spread=40, speed=160, seed=0, a=0.8):
    rnd = random.Random(seed)
    for i in range(n):
        ph = rnd.random(); r = rnd.uniform(5, 16)
        t = (T * speed / 600 + ph) % 1
        bx = x + rnd.uniform(-spread, spread) + math.sin(T * 3 + i) * 10; by = y - t * 600
        cv.drawCircle(bx, by, r, strokep(C('#dff6ff'), 3, alpha=a * (1 - t)))

def particles(cv, T, n=70, seed=3, col=C('#bfe8e0')):
    rnd = random.Random(seed)
    for i in range(n):
        x = (rnd.uniform(0, W) + T * rnd.uniform(-8, 8)) % W; y = (rnd.uniform(0, H) + T * rnd.uniform(-15, 5)) % H
        cv.drawCircle(x, y, rnd.uniform(1.5, 4), fillp(col, alpha=rnd.uniform(0.15, 0.5)))

def glove_arm(cv, x0, y0, x1, y1, s=1.0):
    cv.drawLine(x0, y0, x1, y1, strokep(C('#1c1f26'), 70 * s)); cv.drawLine(x0, y0, x1, y1, strokep(C('#f0c020'), 12 * s))
    cv.drawCircle(x1, y1, 58 * s, fillp(C('#2a2e38'))); cv.drawCircle(x1, y1, 58 * s, strokep(INK, 6 * s))
    for i in range(3): cv.drawLine(x1 - 30 * s + i * 30 * s, y1 + 20 * s, x1 - 30 * s + i * 30 * s, y1 + 62 * s, strokep(C('#2a2e38'), 22 * s))

def tug(cv, x, y, s=1.0, rot=0):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    hull = skia.Path(); hull.moveTo(-330, -40); hull.lineTo(330, -60); hull.quadTo(300, 80, 180, 110); hull.lineTo(-260, 110); hull.quadTo(-330, 60, -330, -40); hull.close()
    cv.drawPath(hull, fillp(C('#1f2a3a'))); cv.drawPath(hull, strokep(INK, 7))
    cv.drawRect(skia.Rect(-330, 20, 320, 60), fillp(C('#c0392b')))
    cv.drawRect(skia.Rect(-200, -190, 120, -45), fillp(C('#f4f1ea'))); cv.drawRect(skia.Rect(-200, -190, 120, -45), strokep(INK, 6))
    cv.drawRect(skia.Rect(-120, -290, 60, -190), fillp(C('#f4f1ea'))); cv.drawRect(skia.Rect(-120, -290, 60, -190), strokep(INK, 6))
    for k in range(3): cv.drawRect(skia.Rect(-105 + k * 55, -270, -70 + k * 55, -225), fillp(C('#9fd0f0')))
    for k in range(4): cv.drawCircle(-160 + k * 75, -115, 18, fillp(C('#9fd0f0'))); 
    cv.drawRect(skia.Rect(140, -250, 190, -50), fillp(C('#e2483b'))); cv.drawRect(skia.Rect(140, -250, 190, -50), strokep(INK, 5))
    for k in range(6): cv.drawCircle(-300 + k * 110, 30, 16, fillp(C('#2a2a2a')))
    cv.restore()

def cola(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    p = skia.Path(); p.moveTo(-18, -320); p.lineTo(18, -320); p.lineTo(20, -240); p.quadTo(70, -200, 66, -120); p.quadTo(50, -60, 62, 0); p.lineTo(-62, 0); p.quadTo(-50, -60, -66, -120); p.quadTo(-70, -200, -20, -240); p.close()
    cv.drawPath(p, fillp(shader=lin((-66, 0), (66, 0), [C('#5a2a1a'), C('#2a1208'), C('#4a2010')]))); cv.drawPath(p, strokep(INK, 6))
    cv.drawRect(skia.Rect(-64, -150, 64, -80), fillp(C('#d8283a'))); text(cv, 'COLA', 0, -100, 40, C('#ffffff'))
    cv.drawRect(skia.Rect(-22, -340, 22, -318), fillp(C('#d8283a'))); cv.drawLine(-40, -220, -32, -30, strokep(C('#ffffff'), 6, alpha=0.4))
    cv.restore()

# ---- heist story
CHARS.update({
    'leo':    dict(adult=True, shirt=C('#3a3f52'), stripe=None, tie=C('#a8322a'), coat=False, hair='bald_grey', glasses=True, pants=C('#2a2f3d')),
    'guard':  dict(adult=True, shirt=C('#2a3a5a'), stripe=None, hair='cap', pants=C('#1a2238')),
    'thief1': dict(adult=True, shirt=C('#1c1c22'), stripe=None, hair='beanie', pants=C('#111116')),
    'thief2': dict(adult=True, shirt=C('#22222a'), stripe=None, hair='beanie', pants=C('#111116')),
    'cop':    CHARS['cop'],
})
_hair_old6 = hair
def hair(cv, x, y, u, kind, back=False):
    if kind == 'beanie':
        if back: return
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.05, y - u * 1.15, x + u * 1.05, y + u * 0.6), 180, 180); p.close()
        cv.drawPath(p, fillp(C('#1a1a22'))); cv.drawPath(p, strokep(INK, u * 0.08))
        cv.drawRoundRect(skia.Rect(x - u * 1.08, y - u * 0.4, x + u * 1.08, y - u * 0.2), u * 0.08, u * 0.08, fillp(C('#2a2a33'))); cv.drawRoundRect(skia.Rect(x - u * 1.08, y - u * 0.4, x + u * 1.08, y - u * 0.2), u * 0.08, u * 0.08, strokep(INK, u * 0.06))
        return
    return _hair_old6(cv, x, y, u, kind, back)

def diamond(cv, x, y, s=1.0, col=C('#cfefff'), sparkle_t=None):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    top = poly([(-50, -20), (-25, -45), (25, -45), (50, -20)]); bot = poly([(-50, -20), (50, -20), (0, 50)])
    cv.drawPath(top, fillp(shade(col, 1.08))); cv.drawPath(bot, fillp(shader=lin((-50, 0), (50, 0), [shade(col, 1.1), shade(col, 0.8)])))
    for x0 in (-25, 0, 25): cv.drawLine(x0, -20, 0, 50, strokep(shade(col, 0.75), 2))
    cv.drawLine(-25, -45, -10, -20, strokep(shade(col, 0.75), 2)); cv.drawLine(25, -45, 10, -20, strokep(shade(col, 0.75), 2))
    cv.drawPath(top, strokep(INK, 4)); cv.drawPath(bot, strokep(INK, 4))
    cv.restore()
    if sparkle_t is not None: sparkle(cv, x + 30 * s, y - 40 * s, 18 * s * (0.5 + 0.5 * math.sin(sparkle_t * 6 + x)))

def vault_door(cv, x, y, r, openf=0.0, T=0):
    soft_shadow(cv, x, y + r + 20, r * 1.1, 40, 0.5)
    cv.drawCircle(x, y, r * 1.12, fillp(C('#3a3e47'))); cv.drawCircle(x, y, r * 1.12, strokep(INK, 10))
    cv.drawCircle(x, y, r * 1.0, fillp(C('#0a0a0e')))
    if openf > 0:
        cv.drawCircle(x, y, r * 0.95, fillp(C('#ffe7a0'), alpha=min(1, openf * 1.2), blur=10))
    cv.save(); cv.translate(x - r * 1.0 * openf * 1.7, y); cv.scale(1 - openf * 0.75, 1)
    cv.drawCircle(0, 0, r * 0.96, fillp(shader=rad((-r * 0.3, -r * 0.3), r * 1.5, [C('#c9ced8'), C('#7a808c'), C('#4a4f5a')])))
    cv.drawCircle(0, 0, r * 0.96, strokep(INK, 8))
    cv.drawCircle(0, 0, r * 0.75, strokep(C('#5a5f6a'), 10))
    for i in range(12):
        a = i / 12 * math.pi * 2; cv.drawCircle(math.cos(a) * r * 0.86, math.sin(a) * r * 0.86, r * 0.035, fillp(C('#3a3e47')))
    a0 = T * 0.4
    for i in range(3):
        a = a0 + i / 3 * math.pi * 2; cv.drawLine(0, 0, math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, strokep(C('#4a4f5a'), r * 0.07))
        cv.drawCircle(math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, r * 0.06, fillp(C('#c9ced8'))); cv.drawCircle(math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, r * 0.06, strokep(INK, 4))
    cv.drawCircle(0, 0, r * 0.18, fillp(C('#c9a46a'))); cv.drawCircle(0, 0, r * 0.18, strokep(INK, 6))
    for i in range(24):
        a = i / 24 * math.pi * 2 + T * 0.2; cv.drawLine(math.cos(a) * r * 0.13, math.sin(a) * r * 0.13, math.cos(a) * r * 0.18, math.sin(a) * r * 0.18, strokep(INK, 2))
    cv.restore()

def laser_grid(cv, T, alpha=1.0, y0=300, y1=1700, n=7, seed=0):
    for i in range(n):
        y = lerp(y0, y1, (i + 0.5) / n) + math.sin(T * 1.3 + i) * 20
        cv.drawLine(-50, y - 120 + i * 30, W + 50, y + 120 - i * 30, strokep(C('#ff2a2a'), 5, alpha=alpha))
        cv.drawLine(-50, y - 120 + i * 30, W + 50, y + 120 - i * 30, strokep(C('#ff2a2a'), 18, blur=8, alpha=0.4 * alpha))

# ---- Sullivan story
CHARS.update({
    'roy':  dict(adult=True, shirt=C('#8a8a5a'), stripe=None, hair='ranger', pants=C('#4a4a33')),
    'royfire': dict(adult=True, shirt=C('#8a8a5a'), stripe=None, hair='short_black', pants=C('#4a4a33')),
})
_hair_old7 = hair
def hair(cv, x, y, u, kind, back=False):
    if kind == 'ranger':
        if back: return
        cv.drawOval(skia.Rect(x - u * 1.55, y - u * 0.92, x + u * 1.55, y - u * 0.58), fillp(C('#a8844a'))); cv.drawOval(skia.Rect(x - u * 1.55, y - u * 0.92, x + u * 1.55, y - u * 0.58), strokep(INK, u * 0.07))
        p = skia.Path(); p.moveTo(x - u * 0.8, y - u * 0.8); p.lineTo(x - u * 0.6, y - u * 1.6); p.lineTo(x - u * 0.15, y - u * 1.45); p.lineTo(x, y - u * 1.7)
        p.lineTo(x + u * 0.15, y - u * 1.45); p.lineTo(x + u * 0.6, y - u * 1.6); p.lineTo(x + u * 0.8, y - u * 0.8); p.close()
        cv.drawPath(p, fillp(C('#b8945a'))); cv.drawPath(p, strokep(INK, u * 0.07))
        cv.drawRect(skia.Rect(x - u * 0.78, y - u * 0.98, x + u * 0.78, y - u * 0.82), fillp(C('#5a4a2a')))
        return
    return _hair_old7(cv, x, y, u, kind, back)

def bolt(cv, x0, y0, x1, y1, seed=0, w=14, alpha=1.0, branches=True):
    rnd = random.Random(seed)
    pts = [(x0, y0)]; n = 9
    for i in range(1, n):
        t = i / n; pts.append((lerp(x0, x1, t) + rnd.uniform(-70, 70), lerp(y0, y1, t) + rnd.uniform(-20, 20)))
    pts.append((x1, y1))
    p = poly(pts, close=False)
    cv.drawPath(p, strokep(C('#7ab8ff'), w * 4, blur=w * 2, alpha=0.7 * alpha))
    cv.drawPath(p, strokep(C('#dff0ff'), w, alpha=alpha)); cv.drawPath(p, strokep(C('#ffffff'), w * 0.4, alpha=alpha))
    if branches:
        for k in (3, 5):
            bx, by = pts[k]; q = [(bx, by)]
            for j in range(3): q.append((q[-1][0] + rnd.uniform(-90, 90), q[-1][1] + rnd.uniform(40, 90)))
            cv.drawPath(poly(q, close=False), strokep(C('#dff0ff'), w * 0.45, alpha=alpha))

def storm_sky(c, h=1100, lit=0):
    c.drawRect(skia.Rect(0, 0, W, h), fillp(shader=lin((0, 0), (0, h), [C('#141a2e'), C('#3a4660')])))
    rnd = random.Random(1)
    for i in range(14):
        x = rnd.uniform(-50, W + 50); y = rnd.uniform(60, 480); r = rnd.uniform(120, 220)
        c.drawCircle(x, y, r, fillp(C('#232b42'), alpha=0.9)); c.drawCircle(x - 30, y - 30, r * 0.8, fillp(C('#2e3854'), alpha=0.6))

def bear(cv, x, y, s=1.0, T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    soft_shadow(cv, 0, 0, 220, 30, 0.4)
    cv.drawOval(skia.Rect(-200, -320, 200, 0), fillp(C('#2a1e18'))); cv.drawOval(skia.Rect(-200, -320, 200, 0), strokep(INK, 8))
    cv.drawCircle(0, -360, 130, fillp(C('#2a1e18'))); cv.drawCircle(0, -360, 130, strokep(INK, 8))
    for sx in (-1, 1): cv.drawCircle(sx * 95, -460, 42, fillp(C('#2a1e18'))); cv.drawCircle(sx * 95, -460, 42, strokep(INK, 7)); cv.drawCircle(sx * 95, -460, 20, fillp(C('#5a3e30')))
    cv.drawOval(skia.Rect(-60, -340, 60, -270), fillp(C('#8a6a50')))
    cv.drawCircle(0, -330, 18, fillp(INK))
    for sx in (-1, 1): cv.drawCircle(sx * 50, -390, 13, fillp(C('#ffffff'))); cv.drawCircle(sx * 50, -390, 7, fillp(INK))
    cv.drawArc(skia.Rect(-30, -310, 30, -280), 0, 180, False, strokep(INK, 5))
    for sx in (-1, 1): cv.drawLine(sx * 150, -150, sx * 220, -230 + math.sin(T * 6) * 20, strokep(C('#2a1e18'), 50))
    cv.restore()

# ---- Amazon story
CHARS.update({
    'lesly':   dict(adult=False, shirt=C('#e2483b'), stripe=None, hair='long', pants=C('#3b4a6b')),
    'soleiny': dict(adult=False, shirt=C('#ffd166'), stripe=None, hair='pigtails', pants=C('#5b4a8a')),
    'tien':    dict(adult=False, shirt=C('#4b8be9'), stripe=None, hair='short_black', pants=C('#3a3a44')),
    'soldier': dict(adult=True, shirt=C('#4a5a33'), stripe=None, hair='helmet_army', pants=C('#3a4a2a')),
    'volunteer': dict(adult=True, shirt=C('#c96b5b'), stripe=None, hair='short_black', pants=C('#3a3a33')),
    'grandma': dict(adult=True, shirt=C('#7ec4b8'), stripe=None, hair='bun_grey', pants=C('#4b4a5a')),
})
_hair_old8 = hair
def hair(cv, x, y, u, kind, back=False):
    if kind == 'helmet_army':
        if back: return
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.12, y - u * 1.2, x + u * 1.12, y + u * 0.55), 180, 180); p.close()
        cv.drawPath(p, fillp(C('#5a6a3a'))); cv.drawPath(p, strokep(INK, u * 0.08))
        cv.drawLine(x - u * 1.15, y - u * 0.34, x + u * 1.15, y - u * 0.34, strokep(C('#3a4a2a'), u * 0.12))
        for i in range(5): cv.drawCircle(x - u * 0.7 + i * u * 0.35, y - u * 0.75, u * 0.09, fillp(C('#3a4a22')))
        return
    return _hair_old8(cv, x, y, u, kind, back)

def baby(cv, x, y, u, expr='sleep', t=0):
    cv.drawOval(skia.Rect(x - u * 1.3, y - u * 0.4, x + u * 1.3, y + u * 1.6), fillp(C('#f4d6c8'))); cv.drawOval(skia.Rect(x - u * 1.3, y - u * 0.4, x + u * 1.3, y + u * 1.6), strokep(INK, u * 0.08))
    cv.drawCircle(x, y, u, fillp(shader=rad((x - u * 0.3, y - u * 0.3), u * 1.6, [C('#ffffff'), C('#f7f5ef'), C('#d9d6cf')], [0, 0.55, 1]))); cv.drawCircle(x, y, u, strokep(INK, u * 0.08))
    cv.drawPath(poly([(x - u * 0.15, y - u * 0.95), (x, y - u * 1.25), (x + u * 0.12, y - u * 0.95)], close=False), strokep(INK, u * 0.07))
    face(cv, x, y, u, expr, False, (0, 0))

def dog(cv, x, y, s=1.0, T=0, wag=True):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    soft_shadow(cv, 0, 0, 160, 20, 0.35)
    step = math.sin(T * 8) * 14
    for lx, ph in ((-90, 0), (-55, 1), (60, 1), (95, 0)):
        cv.drawLine(lx, -70, lx + (step if ph else -step), 0, strokep(C('#2a1e14'), 16))
    cv.drawOval(skia.Rect(-130, -150, 130, -50), fillp(C('#8a5a2a'))); cv.drawOval(skia.Rect(-130, -150, 130, -50), strokep(INK, 6))
    cv.drawOval(skia.Rect(-60, -150, 100, -100), fillp(C('#2a1e14')))
    tail = math.sin(T * 14) * 25 if wag else 0
    cv.drawLine(-125, -120, -190, -170 + tail, strokep(C('#6a4422'), 18))
    cv.drawOval(skia.Rect(90, -230, 210, -130), fillp(C('#8a5a2a'))); cv.drawOval(skia.Rect(90, -230, 210, -130), strokep(INK, 6))
    cv.drawOval(skia.Rect(170, -190, 240, -150), fillp(C('#2a1e14'))); cv.drawCircle(238, -172, 10, fillp(INK))
    for ex in (110, 165): cv.drawPath(poly([(ex, -215), (ex + 12, -275), (ex + 36, -210)]), fillp(C('#2a1e14'))); cv.drawPath(poly([(ex, -215), (ex + 12, -275), (ex + 36, -210)]), strokep(INK, 5))
    cv.drawCircle(170, -195, 8, fillp(INK)); cv.drawCircle(173, -198, 3, fillp(C('#ffffff')))
    cv.drawRect(skia.Rect(85, -150, 120, -128), fillp(C('#e2483b')))
    cv.restore()

def plane(cv, x, y, s=1.0, rot=0, smoke_t=None):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    body = skia.Path(); body.addRoundRect(skia.Rect(-260, -50, 230, 50), 50, 50)
    cv.drawPath(body, fillp(C('#f4f4f0'))); cv.drawPath(body, strokep(INK, 7))
    cv.drawPath(poly([(-200, -40), (-280, -150), (-230, -150), (-150, -40)]), fillp(C('#e2483b'))); cv.drawPath(poly([(-200, -40), (-280, -150), (-230, -150), (-150, -40)]), strokep(INK, 6))
    cv.drawPath(poly([(-60, 0), (60, 0), (20, 140), (-30, 140)]), fillp(C('#d8d8d4'))); cv.drawPath(poly([(-60, 0), (60, 0), (20, 140), (-30, 140)]), strokep(INK, 6))
    for i in range(5): cv.drawCircle(-150 + i * 60, -10, 14, fillp(C('#9fd0f0')))
    cv.drawRect(skia.Rect(225, -18, 250, 18), fillp(C('#3a3e47')))
    cv.drawLine(250, -70, 250, 70, strokep(C('#9aa0aa'), 8))
    cv.drawRect(skia.Rect(-260, 10, 230, 22), fillp(C('#4b8be9')))
    cv.restore()

# ---- Fitbit case
CHARS.update({
    'doug':   dict(adult=True, shirt=C('#6a7a8a'), stripe=None, hair='cowlick', pants=C('#2f3b55')),
    'nicole': dict(adult=True, shirt=C('#2ab0a0'), stripe=None, hair='long', pants=C('#3b3550')),
    'burch':  dict(adult=True, shirt=C('#3a3a40'), stripe=None, hair='bcap', pants=C('#22222a')),
    'judge':  dict(adult=True, shirt=C('#15151a'), stripe=None, hair='bald_grey', glasses=True, pants=C('#15151a')),
})

def tracker(cv, x, y, s=1.0, steps=None, label=None, T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-70, -260, 70, 260), 40, 40, fillp(C('#2a2e38'))); cv.drawRoundRect(skia.Rect(-70, -260, 70, 260), 40, 40, strokep(INK, 6))
    cv.drawRoundRect(skia.Rect(-120, -110, 120, 110), 36, 36, fillp(C('#111318'))); cv.drawRoundRect(skia.Rect(-120, -110, 120, 110), 36, 36, strokep(INK, 7))
    cv.drawRoundRect(skia.Rect(-100, -90, 100, 90), 24, 24, fillp(C('#06080c')))
    if steps is not None:
        text(cv, str(steps), 0, 20, 70, C('#7cf29a'), font='DejaVu Sans Mono-Bold')
        text(cv, 'STEPS', 0, 62, 26, C('#9aa0aa'))
    if label: text(cv, label, 0, -40, 26, C('#7ad7ff'))
    cv.drawCircle(0, -70, 8, fillp(C('#7cf29a'), alpha=0.5 + 0.5 * math.sin(T * 4)))
    cv.restore()

# ---- Flight 593
CHARS.update({
    'pilot':   dict(adult=True, shirt=C('#f4f4f0'), stripe=None, tie=C('#1f2a4a'), coat=False, hair='pilotcap', pants=C('#1f2a4a')),
    'copilot': dict(adult=True, shirt=C('#f4f4f0'), stripe=None, hair='short', pants=C('#1f2a4a')),
    'eldar':   dict(adult=False, shirt=C('#3a6ab0'), stripe=None, hair='sidepart', pants=C('#2a2f3d')),
    'yana':    dict(adult=False, shirt=C('#ff8fa3'), stripe=None, hair='long', pants=C('#5b4a8a')),
})
_hair_old9 = hair
def hair(cv, x, y, u, kind, back=False):
    if kind == 'pilotcap':
        if back: return
        cv.drawOval(skia.Rect(x - u * 1.05, y - u * 1.25, x + u * 1.05, y - u * 0.55), fillp(C('#1f2a4a'))); cv.drawOval(skia.Rect(x - u * 1.05, y - u * 1.25, x + u * 1.05, y - u * 0.55), strokep(INK, u * 0.07))
        cv.drawRoundRect(skia.Rect(x - u * 0.95, y - u * 0.7, x + u * 0.95, y - u * 0.5), u * 0.08, u * 0.08, fillp(C('#111827')))
        cv.drawLine(x - u * 0.35, y - u * 0.9, x + u * 0.35, y - u * 0.9, strokep(C('#f0c75e'), u * 0.1))
        return
    return _hair_old9(cv, x, y, u, kind, back)

def cockpit(cv, T, roll=0.0, pitch=0.0, dark=0.0, ap_on=True, warn=False):
    # sky seen through the windshield, rotated by roll
    cv.save(); cv.clipPath(poly([(60, 180), (1020, 180), (1080, 900), (0, 900)]), doAntiAlias=True)
    cv.save(); cv.translate(540, 560 + pitch * 6); cv.rotate(-roll)
    cv.drawRect(skia.Rect(-2000, -2000, 2000, 0), fillp(shader=lin((0, -800), (0, 0), [C('#050816'), C('#1a2550')])))
    cv.drawRect(skia.Rect(-2000, 0, 2000, 2000), fillp(shader=lin((0, 0), (0, 800), [C('#0a0d14'), C('#020305')])))
    rnd = random.Random(1)
    for i in range(70): cv.drawCircle(rnd.uniform(-1200, 1200), rnd.uniform(-900, -20), rnd.uniform(1, 2.6), fillp(C('#ffffff'), alpha=0.7))
    for i in range(12): cv.drawCircle(rnd.uniform(-1200, 1200), rnd.uniform(40, 300), 3, fillp(C('#ffd680'), alpha=0.6))
    cv.drawLine(-2000, 0, 2000, 0, strokep(C('#3a4a7a'), 3))
    cv.restore(); cv.restore()
    # frame + panel
    cv.drawPath(poly([(0, 0), (W, 0), (W, 180), (0, 180)]), fillp(C('#2a2e36')))
    cv.drawPath(poly([(0, 180), (60, 180), (0, 900)]), fillp(C('#2a2e36'))); cv.drawPath(poly([(W, 180), (1020, 180), (W, 900)]), fillp(C('#2a2e36')))
    cv.drawLine(540, 180, 540, 900, strokep(C('#2a2e36'), 40))
    cv.drawRect(skia.Rect(0, 880, W, H), fillp(shader=lin((0, 880), (0, H), [C('#3a3e47'), C('#1a1c22')])))
    cv.drawRect(skia.Rect(0, 880, W, 910), fillp(C('#1a1c22')))
    for i, x in enumerate((90, 330, 600, 840)):
        r = skia.Rect(x, 960, x + 160, 1120)
        cv.drawRoundRect(r, 10, 10, fillp(C('#0a0d14'))); cv.drawRoundRect(r, 10, 10, strokep(C('#5a5f6a'), 5))
        if i in (0, 2): attitude(cv, x + 80, 1040, 70, roll)
        else:
            for j in range(4): cv.drawLine(x + 20, 990 + j * 30, x + 140 - (j % 2) * 40, 990 + j * 30, strokep(C('#7cf29a'), 4, alpha=0.7))
    # autopilot lights
    cv.drawRoundRect(skia.Rect(380, 920, 700, 950), 8, 8, fillp(C('#111318')))
    for i, (lbl, on) in enumerate((('AP', True), ('ROLL', ap_on), ('PITCH', True))):
        x = 410 + i * 100
        cv.drawRoundRect(skia.Rect(x - 40, 922, x + 40, 948), 6, 6, fillp(C('#3fbf6b') if on else C('#2a2e36')))
        text(cv, lbl, x, 942, 18, C('#06110a') if on else C('#5a5f6a'))
    if warn and (T * 4) % 1 < 0.5:
        cv.drawRoundRect(skia.Rect(780, 900, 1000, 950), 8, 8, fillp(C('#e2483b'))); text(cv, 'STALL', 890, 937, 32, C('#ffffff'))
    if dark > 0: full_dark(cv, dark)

def full_dark(cv, a):
    cv.drawRect(skia.Rect(-3000, -3000, 5000, 5000), fillp(skia.Color(0, 0, 0, int(255 * a))))

def attitude(cv, x, y, r, roll):
    cv.save(); p = skia.Path(); p.addCircle(x, y, r); cv.clipPath(p, doAntiAlias=True)
    cv.translate(x, y); cv.rotate(-roll)
    cv.drawRect(skia.Rect(-r * 2, -r * 2, r * 2, 0), fillp(C('#3a8ad8'))); cv.drawRect(skia.Rect(-r * 2, 0, r * 2, r * 2), fillp(C('#8a5a2a')))
    cv.drawLine(-r * 2, 0, r * 2, 0, strokep(C('#ffffff'), 3))
    cv.restore()
    cv.drawLine(x - r * 0.6, y, x - r * 0.2, y, strokep(C('#ffd166'), 6)); cv.drawLine(x + r * 0.2, y, x + r * 0.6, y, strokep(C('#ffd166'), 6)); cv.drawCircle(x, y, 5, fillp(C('#ffd166')))
    cv.drawCircle(x, y, r, strokep(INK, 4))

def yoke(cv, x, y, s=1.0, push=0.0):
    cv.save(); cv.translate(x, y + push * 30); cv.scale(s, s)
    cv.drawRect(skia.Rect(-22, 0, 22, 500), fillp(C('#2a2e36')))
    p = skia.Path(); p.moveTo(-200, -40); p.lineTo(-200, 60); p.quadTo(-200, 110, -150, 110); p.lineTo(150, 110); p.quadTo(200, 110, 200, 60); p.lineTo(200, -40)
    cv.drawPath(p, strokep(C('#3a3e47'), 46)); cv.drawPath(p, strokep(INK, 4))
    cv.drawRoundRect(skia.Rect(-60, 40, 60, 110), 14, 14, fillp(C('#3a3e47')))
    cv.restore()

def a310(cv, x, y, s=1.0, rot=0, bank=0):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    far = poly([(-20, -20), (110, -20), (10, -140), (-50, -140)])
    cv.drawPath(far, fillp(C('#9aa0aa'))); cv.drawPath(far, strokep(INK, 5))
    body = skia.Path(); body.addRoundRect(skia.Rect(-360, -55, 360, 55), 55, 55)
    cv.drawPath(body, fillp(C('#f4f4f0'))); cv.drawPath(body, strokep(INK, 7))
    cv.drawRect(skia.Rect(-360, 0, 360, 18), fillp(C('#2a4aa0')))
    for i in range(14): cv.drawCircle(-260 + i * 38, -15, 8, fillp(C('#ffe7a0')))
    cv.drawPath(poly([(-300, -45), (-380, -190), (-320, -190), (-230, -45)]), fillp(C('#2a4aa0'))); cv.drawPath(poly([(-300, -45), (-380, -190), (-320, -190), (-230, -45)]), strokep(INK, 6))
    cv.drawPath(poly([(300, -30), (355, -20), (355, 5), (300, 5)]), fillp(C('#1a2244')))
    near = poly([(-40, 25), (130, 25), (-20, 230), (-110, 230)])
    cv.drawPath(near, fillp(C('#c9ced8'))); cv.drawPath(near, strokep(INK, 6))
    cv.drawRoundRect(skia.Rect(0, 80, 110, 125), 20, 20, fillp(C('#7a808c'))); cv.drawRoundRect(skia.Rect(0, 80, 110, 125), 20, 20, strokep(INK, 4))
    cv.drawCircle(-340, 0, 9, fillp(C('#ff3030'))); 
    cv.restore()

# ---- additions for the Rogozov story
CHARS.update({
    'rogo':    dict(adult=True, shirt=C('#3c6e8f'), stripe=None, hair='short_black', pants=C('#2a2f3d')),
    'rogo_op': dict(adult=True, shirt=C('#f4f4f0'), stripe=None, hair='surgcap', pants=C('#cfd6dc')),
    'rogo_pk': dict(adult=True, shirt=C('#d9482f'), stripe=None, hair='hood', pants=C('#2a2f3d')),
    'artem':   dict(adult=True, shirt=C('#f4f4f0'), stripe=None, hair='surgcap', glasses=True, pants=C('#cfd6dc')),
    'tepl':    dict(adult=True, shirt=C('#f4f4f0'), stripe=None, hair='surgcap', pants=C('#cfd6dc')),
    'artem_s': dict(adult=True, shirt=C('#7a8a5a'), stripe=None, hair='beanie', glasses=True, pants=C('#3a3a3a')),
    'tepl_s':  dict(adult=True, shirt=C('#8a5a3a'), stripe=C('#c98a52'), hair='short', pants=C('#2f3b55')),
    'crew1':   dict(adult=True, shirt=C('#e0a030'), stripe=None, hair='hood', pants=C('#2a2f3d')),
    'crew2':   dict(adult=True, shirt=C('#3a7a5a'), stripe=None, hair='hood', pants=C('#2a2f3d')),
    'crew3':   dict(adult=True, shirt=C('#5a5aa0'), stripe=None, hair='hood', pants=C('#2a2f3d')),
    'crewA':   dict(adult=True, shirt=C('#6a6f7a'), stripe=None, hair='spiky', pants=C('#2a2f3d')),
    'crewB':   dict(adult=True, shirt=C('#9a4a4a'), stripe=None, hair='slick', pants=C('#2a2f3d')),
    'crewC':   dict(adult=True, shirt=C('#4a6a9a'), stripe=C('#dfe6ea'), hair='curly', pants=C('#2a2f3d')),
})
_hair_old13 = hair
def hair(cv, x, y, u, kind, back=False):
    if kind == 'surgcap':
        if back: return
        p = skia.Path(); p.moveTo(x - u * 1.0, y - u * 0.35); p.quadTo(x - u * 1.05, y - u * 1.25, x, y - u * 1.18); p.quadTo(x + u * 1.05, y - u * 1.25, x + u * 1.0, y - u * 0.35)
        p.quadTo(x, y - u * 0.55, x - u * 1.0, y - u * 0.35); p.close()
        cv.drawPath(p, fillp(C('#bfe0dc'))); cv.drawPath(p, strokep(INK, u * 0.07))
        cv.drawLine(x - u * 0.9, y - u * 0.5, x + u * 0.9, y - u * 0.5, strokep(C('#9cc8c2'), u * 0.05))
        return
    if kind == 'hood':
        if back:
            cv.drawOval(skia.Rect(x - u * 1.35, y - u * 1.3, x + u * 1.35, y + u * 1.2), fillp(C('#e9e2d0')))
            cv.drawOval(skia.Rect(x - u * 1.35, y - u * 1.3, x + u * 1.35, y + u * 1.2), strokep(INK, u * 0.07))
            rnd = random.Random(int(x))
            for i in range(26):
                a = i / 26 * 2 * math.pi; cv.drawLine(x + math.cos(a) * u * 1.2, y + math.sin(a) * u * 1.15, x + math.cos(a) * u * 1.42, y + math.sin(a) * u * 1.35, strokep(C('#cfc6b0'), u * 0.08))
        return
    return _hair_old13(cv, x, y, u, kind, back)

def snowfall(cv, T, n=120, wind=300, seed=5, a=0.8, size=(2, 6), fall=180):
    rnd = random.Random(seed)
    for i in range(n):
        sp = rnd.uniform(0.6, 1.4)
        x = (rnd.uniform(0, W + 400) + T * wind * sp) % (W + 400) - 200
        y = (rnd.uniform(0, H) + T * fall * sp) % H
        r = rnd.uniform(*size)
        if wind > 600: cv.drawLine(x, y, x - wind * 0.04 * sp, y - fall * 0.02, strokep(C('#ffffff'), r * 0.8, alpha=a * rnd.uniform(0.4, 1)))
        else: cv.drawCircle(x, y, r, fillp(C('#ffffff'), alpha=a * rnd.uniform(0.4, 1)))

def polar_sky(cv, top=C('#0b1630'), bot=C('#3a5277'), stars=True, seed=2, h=1250):
    cv.drawRect(skia.Rect(-200, -200, W + 200, H + 200), fillp(shader=lin((0, 0), (0, h), [top, bot])))
    if stars:
        rnd = random.Random(seed)
        for i in range(80): cv.drawCircle(rnd.uniform(0, W), rnd.uniform(0, h * 0.7), rnd.uniform(1, 2.4), fillp(C('#ffffff'), alpha=rnd.uniform(0.3, 0.9)))

def aurora(cv, T, y=420, a=0.5):
    for k, col in enumerate((C('#5cf2b0'), C('#7ad7ff'), C('#a98bff'))):
        p = skia.Path(); p.moveTo(-100, y + k * 60)
        for i in range(13):
            x = -100 + i * 110; p.lineTo(x, y + k * 60 + math.sin(i * 0.7 + T * 0.8 + k) * 70)
        cv.drawPath(p, strokep(col, 70 - k * 15, blur=28, alpha=a * (1 - k * 0.25)))

def snow_ground(cv, y=1250, col=C('#e8f0f7'), shade_=C('#a9bdd1')):
    p = skia.Path(); p.moveTo(-200, y)
    for i in range(9): p.quadTo(-200 + i * 180 + 90, y - 30 + (i % 2) * 40, -200 + (i + 1) * 180, y + (i % 3) * 8)
    p.lineTo(W + 200, H + 200); p.lineTo(-200, H + 200); p.close()
    cv.drawPath(p, fillp(shader=lin((0, y), (0, H), [col, shade_])))
    cv.drawPath(p, strokep(C('#8aa0b8'), 4))

def hut(cv, x, y, s=1.0, lit=True, snow=True, door_=True, col=C('#8a6a4a')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    soft_shadow(cv, 0, 0, 230, 30, 0.35)
    cv.drawRect(skia.Rect(-200, -220, 200, 0), fillp(shader=lin((-200, 0), (200, 0), [shade(col, 1.1), shade(col, 0.8)])))
    for i in range(1, 6): cv.drawLine(-200, -220 + i * 37, 200, -220 + i * 37, strokep(shade(col, 0.7), 3))
    cv.drawRect(skia.Rect(-200, -220, 200, 0), strokep(INK, 7))
    roof = poly([(-235, -215), (235, -215), (190, -300), (-190, -300)])
    cv.drawPath(roof, fillp(C('#5a4a3e'))); cv.drawPath(roof, strokep(INK, 7))
    if snow:
        sn = skia.Path(); sn.moveTo(-245, -210); sn.quadTo(-200, -340, -150, -300); sn.lineTo(150, -305); sn.quadTo(220, -330, 245, -210); sn.quadTo(0, -250, -245, -210); sn.close()
        cv.drawPath(sn, fillp(C('#f4f8fc'))); cv.drawPath(sn, strokep(INK, 5))
    wcol = C('#ffd27a') if lit else C('#2a3448')
    cv.drawRect(skia.Rect(40, -170, 140, -80), fillp(wcol)); cv.drawRect(skia.Rect(40, -170, 140, -80), strokep(INK, 6))
    cv.drawLine(90, -170, 90, -80, strokep(INK, 4)); cv.drawLine(40, -125, 140, -125, strokep(INK, 4))
    if lit: cv.drawCircle(90, -125, 110, fillp(C('#ffcc66'), alpha=0.18, blur=40))
    if door_:
        cv.drawRect(skia.Rect(-150, -160, -70, 0), fillp(C('#4a3a2e'))); cv.drawRect(skia.Rect(-150, -160, -70, 0), strokep(INK, 6))
    cv.restore()

def red_flag(cv, x, y, h=260, T=0):
    cv.drawLine(x, y, x, y - h, strokep(C('#c7ccd4'), 8))
    p = skia.Path(); p.moveTo(x, y - h)
    for i in range(6): p.lineTo(x + i * 24, y - h + math.sin(T * 6 + i) * 6)
    p.lineTo(x + 120, y - h + 80 + math.sin(T * 6 + 5) * 6)
    for i in range(5, -1, -1): p.lineTo(x + i * 24, y - h + 80 + math.sin(T * 6 + i) * 6)
    p.close(); cv.drawPath(p, fillp(C('#d8312c'))); cv.drawPath(p, strokep(INK, 5))

def scalpel(cv, x, y, s=1.0, ang=0, glint=0.0):
    cv.save(); cv.translate(x, y); cv.rotate(ang); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-110, -12, 10, 12), 10, 10, fillp(C('#9aa3ad'))); cv.drawRoundRect(skia.Rect(-110, -12, 10, 12), 10, 10, strokep(INK, 5))
    for i in range(4): cv.drawLine(-95 + i * 22, -6, -95 + i * 22, 6, strokep(C('#6f7782'), 3))
    b = skia.Path(); b.moveTo(8, -8); b.lineTo(70, -10); b.quadTo(110, -2, 115, 10); b.lineTo(8, 8); b.close()
    cv.drawPath(b, fillp(shader=lin((0, -10), (0, 10), [C('#ffffff'), C('#c9d2dc')]))); cv.drawPath(b, strokep(INK, 4))
    if glint > 0:
        sparkle(cv, 85, -6, 40 * glint, a=glint)
    cv.restore()

def hand_mirror(cv, x, y, r=70, ang=0, reflect=True):
    cv.save(); cv.translate(x, y); cv.rotate(ang)
    cv.drawRoundRect(skia.Rect(-12, r * 0.9, 12, r * 2.1), 8, 8, fillp(C('#6a5a4a'))); cv.drawRoundRect(skia.Rect(-12, r * 0.9, 12, r * 2.1), 8, 8, strokep(INK, 5))
    cv.drawCircle(0, 0, r * 1.08, fillp(C('#8a7a5a'))); cv.drawCircle(0, 0, r * 1.08, strokep(INK, 6))
    cv.drawCircle(0, 0, r, fillp(shader=lin((-r, -r), (r, r), [C('#eaf6ff'), C('#9fc3dc')])))
    if reflect: cv.drawLine(-r * 0.5, -r * 0.2, -r * 0.1, -r * 0.6, strokep(C('#ffffff'), r * 0.12, alpha=0.8))
    cv.restore()

def op_lamp(cv, x, y, s=1.0, glow=1.0):
    cv.drawLine(x, -50, x, y - 60 * s, strokep(INK, 6))
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    sh = poly([(-110, 30), (-60, -60), (60, -60), (110, 30)])
    cv.drawPath(sh, fillp(C('#5a6a72'))); cv.drawPath(sh, strokep(INK, 6))
    cv.drawOval(skia.Rect(-80, 10, 80, 50), fillp(C('#fff6d6'))); cv.drawOval(skia.Rect(-80, 10, 80, 50), strokep(INK, 4))
    cv.restore()
    if glow > 0: cv.drawCircle(x, y + 30 * s, 160 * s, fillp(C('#fff2c0'), alpha=0.35 * glow, blur=50))

def tray(cv, x, y, s=1.0, jar=False):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-110, -18, 110, 18), 8, 8, fillp(C('#c9d2dc'))); cv.drawRoundRect(skia.Rect(-110, -18, 110, 18), 8, 8, strokep(INK, 5))
    for i, (dx, l) in enumerate(((-70, 60), (-25, 70), (20, 55))): cv.drawLine(dx - l / 2, -26, dx + l / 2, -30, strokep(C('#8a939e'), 7))
    if jar:
        cv.drawRoundRect(skia.Rect(45, -95, 100, -20), 10, 10, fillp(C('#a8d8c8'), alpha=0.85)); cv.drawRoundRect(skia.Rect(45, -95, 100, -20), 10, 10, strokep(INK, 4))
        cv.drawRect(skia.Rect(40, -108, 105, -92), fillp(C('#5a6a72')))
    cv.restore()

def thermometer(cv, x, y, s=1.0, level=0.5):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-28, -300, 28, 0), 28, 28, fillp(C('#ffffff'))); cv.drawRoundRect(skia.Rect(-28, -300, 28, 0), 28, 28, strokep(INK, 7))
    cv.drawCircle(0, 20, 50, fillp(C('#e2483b'))); cv.drawCircle(0, 20, 50, strokep(INK, 7))
    cv.drawRoundRect(skia.Rect(-12, -40 - 230 * level, 12, 10), 12, 12, fillp(C('#e2483b')))
    for i in range(6): cv.drawLine(14, -60 - i * 40, 26, -60 - i * 40, strokep(INK, 4))
    cv.restore()

def body_icon(cv, x, y, s=1.0, T=0, pain=1.0, fever=0, nausea=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    ol = strokep(C('#7ad7ff'), 8)
    cv.drawCircle(0, -330, 90, strokep(C('#7ad7ff'), 8))
    tor = skia.Path(); tor.moveTo(-150, -210); tor.quadTo(0, -250, 150, -210); tor.lineTo(130, 150); tor.quadTo(0, 190, -130, 150); tor.close()
    cv.drawPath(tor, fillp(C('#7ad7ff'), alpha=0.08)); cv.drawPath(tor, ol)
    for sx in (-1, 1):
        cv.drawLine(sx * 150, -200, sx * 230, 100, ol); cv.drawLine(sx * 70, 170, sx * 90, 480, ol)
    if fever > 0:
        k = fever; cv.drawCircle(0, -330, 120, fillp(C('#ff5a3a'), alpha=0.35 * k * (0.7 + 0.3 * math.sin(T * 8)), blur=30))
    if nausea > 0:
        for i in range(3):
            a = T * 3 + i * 2.1; cv.drawCircle(math.cos(a) * 40, -40 + math.sin(a) * 30, 18 * nausea, fillp(C('#8be07a'), alpha=0.7 * nausea))
    if pain > 0:
        pr = 50 + 18 * math.sin(T * 9)
        cv.drawCircle(-65, 90, pr * 1.6, fillp(C('#ff3b30'), alpha=0.35 * pain, blur=25))
        cv.drawCircle(-65, 90, 28 * pain, fillp(C('#ff3b30'))); cv.drawCircle(-65, 90, 28 * pain, strokep(INK, 4))
        for i in range(6):
            a = i / 6 * 2 * math.pi + T; r0 = 45 + 10 * math.sin(T * 9); cv.drawLine(-65 + math.cos(a) * r0, 90 + math.sin(a) * r0, -65 + math.cos(a) * (r0 + 30 * pain), 90 + math.sin(a) * (r0 + 30 * pain), strokep(C('#ff3b30'), 7))
    cv.restore()

def gut_icon(cv, x, y, s=1.0, T=0, bad=1.0, gone=False):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    p = skia.Path(); p.moveTo(-170, 120); p.lineTo(-170, -150); p.quadTo(-170, -190, -130, -190); p.lineTo(130, -190); p.quadTo(170, -190, 170, -150); p.lineTo(170, 160)
    cv.drawPath(p, strokep(C('#f2b5a0'), 70)); cv.drawPath(p, strokep(C('#c97a68'), 6))
    q = skia.Path(); q.moveTo(-100, -100)
    for i in range(6): q.quadTo(-80 + i * 40, -130 + (i % 2) * 170, -60 + i * 40, -40 + (i % 2) * 40)
    cv.drawPath(q, strokep(C('#f7c9b8'), 50)); cv.drawPath(q, strokep(C('#d89a88'), 5))
    if not gone:
        ap = skia.Path(); ap.moveTo(-170, 130); ap.quadTo(-200, 200, -150, 240)
        col = mix(C('#f2b5a0'), C('#e2483b'), bad)
        cv.drawPath(ap, strokep(col, 34)); cv.drawPath(ap, strokep(INK, 4, alpha=0.6))
        if bad > 0:
            cv.drawCircle(-170, 195, 70 + 10 * math.sin(T * 8), fillp(C('#ff3b30'), alpha=0.4 * bad, blur=28))
    cv.restore()

def calendar(cv, x, y, s=1.0, top='', big='', col=C('#2a4aa0'), k=1.0, rot=0):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s * k, s * k)
    cv.drawRoundRect(skia.Rect(-240, -220, 240, 220), 26, 26, fillp(C('#ffffff'))); cv.drawRoundRect(skia.Rect(-240, -220, 240, 220), 26, 26, strokep(INK, 8))
    cv.drawRect(skia.Rect(-236, -216, 236, -100), fillp(col)); cv.drawLine(-240, -100, 240, -100, strokep(INK, 6))
    for dx in (-120, 120): cv.drawRoundRect(skia.Rect(dx - 14, -250, dx + 14, -190), 10, 10, fillp(C('#5a5f6a')))
    text(cv, top, 0, -140, 58, C('#ffffff')); text(cv, big, 0, 110, 150 if len(big) <= 4 else 110, INK)
    cv.restore()

def hourglass(cv, x, y, s=1.0, frac=0.5, T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    for yy in (-230, 230): cv.drawRoundRect(skia.Rect(-170, yy - 20, 170, yy + 20), 12, 12, fillp(C('#8a5a33'))); 
    gl = skia.Path(); gl.moveTo(-130, -210); gl.lineTo(130, -210); gl.quadTo(130, -60, 15, 0); gl.quadTo(130, 60, 130, 210); gl.lineTo(-130, 210); gl.quadTo(-130, 60, -15, 0); gl.quadTo(-130, -60, -130, -210); gl.close()
    cv.drawPath(gl, fillp(C('#dff1ff'), alpha=0.5))
    cv.save(); cv.clipPath(gl, doAntiAlias=True)
    ht = 190 * (1 - frac); cv.drawRect(skia.Rect(-140, -10 - ht, 140, 0), fillp(C('#e9b44c')))
    hb = 190 * frac; cv.drawRect(skia.Rect(-140, 210 - hb, 140, 220), fillp(C('#e9b44c')))
    if 0 < frac < 1: cv.drawLine(0, 0, 0, 210 - hb, strokep(C('#e9b44c'), 6))
    cv.restore(); cv.drawPath(gl, strokep(INK, 7))
    for yy in (-230, 230): cv.drawRoundRect(skia.Rect(-170, yy - 20, 170, yy + 20), 12, 12, strokep(INK, 6))
    cv.restore()

def antarctica_map(cv, x, y, r, T=0, pin=1.0):
    cv.drawCircle(x, y, r, fillp(shader=rad((x - r * 0.3, y - r * 0.3), r * 1.4, [C('#3a86c8'), C('#123a6a')])))
    cv.drawCircle(x, y, r, strokep(INK, 8))
    rnd = random.Random(4); p = skia.Path()
    for i in range(40):
        a = i / 40 * 2 * math.pi; rr = r * (0.55 + 0.08 * math.sin(a * 3) + 0.05 * math.sin(a * 7) + rnd.uniform(-0.02, 0.02))
        if 3.6 < a < 4.2: rr = r * 0.72
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr
        p.moveTo(px, py) if i == 0 else p.lineTo(px, py)
    p.close(); cv.drawPath(p, fillp(C('#f4f8fc'))); cv.drawPath(p, strokep(C('#8aa0b8'), 6))
    return (x + r * 0.08, y - r * 0.56)

# ---- additions for the LaPlante story
CHARS.update({
    'tina':   dict(adult=False, shirt=C('#9a6ad0'), stripe=None, hair='long', pants=C('#3a3f5a')),
    'kathy':  dict(adult=False, shirt=C('#3aa39a'), stripe=None, hair='pony', pants=C('#3a3f5a')),
    'dad':    dict(adult=True, shirt=C('#8a6a4a'), stripe=C('#a8875f'), hair='short', pants=C('#3a3a44')),
    'daniel': dict(adult=False, shirt=C('#4a4f5a'), stripe=None, hair='spiky', pants=C('#2a2a30')),
    'friend': dict(adult=False, shirt=C('#e0a030'), stripe=None, hair='bob', pants=C('#3a3f5a')),
})
def face_paint(cv, head, u):
    hx, hy = head
    for (dx, dy, col) in ((-0.55, 0.15, C('#d8312c')), (0.55, 0.15, C('#d8312c')), (0, -0.55, C('#f4efd0')), (-0.45, -0.35, C('#f4efd0')), (0.45, -0.35, C('#f4efd0'))):
        cv.drawLine(hx + dx * u - 0.18 * u, hy + dy * u, hx + dx * u + 0.18 * u, hy + dy * u + 0.06 * u, strokep(col, u * 0.12, alpha=0.9))

def hatchet(cv, x, y, s=1.0, ang=0, col=C('#121318')):
    cv.save(); cv.translate(x, y); cv.rotate(ang); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-10, -160, 10, 40), 8, 8, fillp(C('#6a4a2a'))); cv.drawRoundRect(skia.Rect(-10, -160, 10, 40), 8, 8, strokep(INK, 4))
    cv.drawPath(poly([(-8, -160), (-90, -175), (-100, -110), (-8, -120)]), fillp(col)); cv.drawPath(poly([(-8, -160), (-90, -175), (-100, -110), (-8, -120)]), strokep(INK, 4))
    cv.restore()

def night_window(cv, x, y, w, h, T=0, moon=True, frame=C('#4a4050')):
    cv.drawRect(skia.Rect(x - 12, y - 12, x + w + 12, y + h + 12), fillp(shade(frame, 0.8)))
    cv.drawRect(skia.Rect(x, y, x + w, y + h), fillp(shader=lin((0, y), (0, y + h), [C('#070b1e'), C('#1c2648')])))
    rnd = random.Random(int(x))
    for i in range(10): cv.drawCircle(x + rnd.uniform(0, w), y + rnd.uniform(0, h * 0.7), 2, fillp(C('#ffffff'), alpha=0.7))
    if moon: cv.drawCircle(x + w * 0.7, y + h * 0.28, min(w, h) * 0.13, fillp(C('#eef1ff')))
    cv.drawRect(skia.Rect(x, y, x + w, y + h), strokep(frame, 10))
    cv.drawLine(x + w / 2, y, x + w / 2, y + h, strokep(frame, 8)); cv.drawLine(x, y + h / 2, x + w, y + h / 2, strokep(frame, 8))

def wallpaper(cv, r, col=C('#5a4a6a'), stripe=C('#4e3f5e'), floor=C('#3a2a22'), floor_y=1500):
    cv.drawRect(r, fillp(col))
    for x in range(int(r.left()), int(r.right()), 60): cv.drawRect(skia.Rect(x, r.top(), x + 22, min(r.bottom(), floor_y)), fillp(stripe))
    cv.drawRect(skia.Rect(r.left(), floor_y, r.right(), r.bottom()), fillp(floor))
    cv.drawRect(skia.Rect(r.left(), floor_y - 24, r.right(), floor_y), fillp(shade(floor, 1.5)))

def wall_cavity(cv, x0, x1, y0=0, y1=1500, T=0, lit=0.0):
    cv.drawRect(skia.Rect(x0, y0, x1, y1), fillp(C('#120e0c')))
    if lit > 0: cv.drawRect(skia.Rect(x0, y0, x1, y1), fillp(C('#3a2e26'), alpha=lit))
    for sx in (x0, x1 - 34): cv.drawRect(skia.Rect(sx, y0, sx + 34, y1), fillp(C('#7a5a3a'))); cv.drawRect(skia.Rect(sx, y0, sx + 34, y1), strokep(INK, 4))
    for yy in range(int(y0) + 300, int(y1), 420): cv.drawRect(skia.Rect(x0, yy, x1, yy + 26), fillp(C('#6a4a30')))
    cv.drawLine(x0 + 70, y0, x0 + 70, y1, strokep(C('#5a6068'), 16, alpha=0.8))
    rnd = random.Random(3)
    for i in range(30):
        px = rnd.uniform(x0, x1); py = (rnd.uniform(y0, y1) + T * 12) % (y1 - y0) + y0
        cv.drawCircle(px, py, 2, fillp(C('#c9b89a'), alpha=0.35))

def eyes_dark(cv, x, y, s=1.0, T=0, blink=True):
    b = blink and ((T * 0.7 + 1.0) % 3.1) < 0.12
    for dx in (-22, 22):
        if b: cv.drawLine(x + dx * s - 10 * s, y, x + dx * s + 10 * s, y, strokep(C('#f4efe2'), 4 * s))
        else:
            cv.drawOval(skia.Rect(x + dx * s - 12 * s, y - 8 * s, x + dx * s + 12 * s, y + 8 * s), fillp(C('#f4efe2')))
            cv.drawCircle(x + dx * s, y, 4.5 * s, fillp(INK))

def wall_phone(cv, x, y, s=1.0, T=0, ring=False):
    sh = math.sin(T * 60) * 5 if ring else 0
    cv.save(); cv.translate(x + sh, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-90, -150, 90, 150), 24, 24, fillp(C('#e8d9b0'))); cv.drawRoundRect(skia.Rect(-90, -150, 90, 150), 24, 24, strokep(INK, 7))
    cv.drawCircle(0, 40, 60, fillp(C('#d6c69c'))); cv.drawCircle(0, 40, 60, strokep(INK, 5))
    for i in range(10): a = i / 10 * 2 * math.pi - 1; cv.drawCircle(math.cos(a) * 40, 40 + math.sin(a) * 40, 9, fillp(C('#f4ecd4'))); cv.drawCircle(math.cos(a) * 40, 40 + math.sin(a) * 40, 9, strokep(INK, 3))
    hs = skia.Path(); hs.moveTo(-110, -170); hs.quadTo(0, -210, 110, -170); hs.lineTo(110, -120); hs.quadTo(0, -150, -110, -120); hs.close()
    cv.save(); cv.translate(0, -15 * abs(math.sin(T * 30)) if ring else 0)
    cv.drawPath(hs, fillp(C('#d6c69c'))); cv.drawPath(hs, strokep(INK, 7)); cv.restore()
    p = skia.Path(); p.moveTo(-60, 150)
    for i in range(10): p.quadTo(-80 + (i % 2) * 40, 175 + i * 22, -60, 190 + i * 22)
    cv.drawPath(p, strokep(C('#d6c69c'), 8))
    cv.restore()
    if ring:
        for k in range(3):
            r = 160 + ((T * 300 + k * 60) % 180)
            cv.drawArc(skia.Rect(x - r, y - 60 - r, x + r, y - 60 + r), -60, 40, False, strokep(C('#ffd166'), 8, alpha=1 - (r - 160) / 180))
            cv.drawArc(skia.Rect(x - r, y - 60 - r, x + r, y - 60 + r), -160, 40, False, strokep(C('#ffd166'), 8, alpha=1 - (r - 160) / 180))

def retro_tv(cv, x, y, s=1.0, ch=0, static=0.0, T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-260, -210, 260, 210), 30, 30, fillp(C('#7a5a3a'))); cv.drawRoundRect(skia.Rect(-260, -210, 260, 210), 30, 30, strokep(INK, 8))
    scr = skia.Rect(-220, -170, 120, 170)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(scr, 40, 40), doAntiAlias=True)
    cols = [[C('#e8e8e8'), C('#e8d23a'), C('#3ad2d2'), C('#3ad23a'), C('#d23ad2'), C('#d23a3a'), C('#3a3ad2')],
            [C('#2a6ab0'), C('#3a8ad8')], [C('#3a7a3a'), C('#8ad07a')], [C('#b04a3a'), C('#e8a050')]][ch % 4]
    w = scr.width() / len(cols)
    for i, c in enumerate(cols): cv.drawRect(skia.Rect(scr.left() + i * w, scr.top(), scr.left() + (i + 1) * w, scr.bottom()), fillp(c))
    if static > 0:
        rnd = random.Random(int(T * 30))
        for i in range(260): cv.drawRect(skia.Rect(rnd.uniform(-220, 120), rnd.uniform(-170, 170), 0, 0).makeOffset(0, 0) if False else skia.Rect.MakeXYWH(rnd.uniform(-220, 120), rnd.uniform(-170, 170), 8, 4), fillp(C('#ffffff') if rnd.random() < 0.5 else C('#222222'), alpha=static))
    cv.restore()
    cv.drawRoundRect(scr, 40, 40, strokep(INK, 8))
    for i in range(2): cv.drawCircle(190, -100 + i * 90, 26, fillp(C('#c9a56a'))); cv.drawCircle(190, -100 + i * 90, 26, strokep(INK, 5))
    text(cv, str(ch + 2), 190, 120, 50, C('#f4efe2'))
    cv.drawLine(-60, -210, -140, -330, strokep(INK, 6)); cv.drawLine(60, -210, 140, -330, strokep(INK, 6))
    cv.restore()

def spirit_board(cv, x, y, s=1.0, px=0.0, py=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-380, -240, 380, 240), 40, 40, fillp(C('#c9a06a'))); cv.drawRoundRect(skia.Rect(-380, -240, 380, 240), 40, 40, strokep(INK, 8))
    text(cv, 'YES', -280, -170, 50, C('#3a2a1a')); text(cv, 'NO', 290, -170, 50, C('#3a2a1a'))
    row1 = 'ABCDEFGHIJKLM'; row2 = 'NOPQRSTUVWXYZ'
    for r, row in enumerate((row1, row2)):
        for i, ch_ in enumerate(row):
            a = (i - 6) * 0.11; xx = math.sin(a) * 520; yy = -40 + r * 90 + (1 - math.cos(a)) * 380
            text(cv, ch_, xx, yy, 44, C('#3a2a1a'))
    text(cv, 'GOODBYE', 0, 210, 46, C('#3a2a1a'))
    cv.save(); cv.translate(px * 300, py * 160)
    pl = poly([(0, -80), (70, 40), (0, 70), (-70, 40)])
    cv.drawPath(pl, fillp(C('#f4efe2'), alpha=0.92)); cv.drawPath(pl, strokep(INK, 6)); cv.drawCircle(0, 10, 22, strokep(INK, 5))
    cv.restore(); cv.restore()

def candle(cv, x, y, h=120, T=0, seed=0, w=34):
    cv.drawRect(skia.Rect(x - w / 2, y - h, x + w / 2, y), fillp(C('#f4efe2'))); cv.drawRect(skia.Rect(x - w / 2, y - h, x + w / 2, y), strokep(INK, 4))
    f = 1 + 0.15 * math.sin(T * 9 + seed * 2)
    cv.drawOval(skia.Rect(x - 10, y - h - 42 * f, x + 10, y - h), fillp(C('#ffd166'))); cv.drawCircle(x, y - h - 18, 70, fillp(C('#ffb040'), alpha=0.22, blur=26))

def police_car(cv, x, y, s=1.0, T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    soft_shadow(cv, 0, 0, 300, 30, 0.4)
    body = skia.Path(); body.moveTo(-300, -40); body.lineTo(-280, -120); body.lineTo(-150, -130); body.lineTo(-90, -210); body.lineTo(130, -210); body.lineTo(200, -130); body.lineTo(300, -115); body.lineTo(310, -40); body.close()
    cv.drawPath(body, fillp(C('#f4f4f0'))); cv.drawPath(body, strokep(INK, 7))
    cv.drawRect(skia.Rect(-300, -110, 310, -70), fillp(C('#1f2a4a')))
    text(cv, 'POLICE', 0, -80, 44, C('#ffffff'))
    for gx in (-75, 40): cv.drawPath(poly([(gx, -195), (gx + 90, -195), (gx + 110 if gx > 0 else gx + 90, -140), (gx - 10 if gx < 0 else gx, -140)]), fillp(C('#9fc3dc')))
    on = (T * 4) % 1 < 0.5
    cv.drawRoundRect(skia.Rect(-60, -240, 0, -210), 6, 6, fillp(C('#e2483b') if on else C('#5a1a1a'))); cv.drawRoundRect(skia.Rect(0, -240, 60, -210), 6, 6, fillp(C('#3a6ae2') if not on else C('#1a1a5a')))
    cv.drawCircle(-30 if on else 30, -225, 160, fillp(C('#e2483b') if on else C('#3a6ae2'), alpha=0.25, blur=40))
    for wx in (-190, 190): cv.drawCircle(wx, -40, 55, fillp(C('#1b1b22'))); cv.drawCircle(wx, -40, 24, fillp(C('#8a939e')))
    cv.restore()

def ferris(cv, x, y, r, T):
    cv.drawLine(x, y, x - r * 0.7, y + r * 1.25, strokep(C('#3a3a50'), 14)); cv.drawLine(x, y, x + r * 0.7, y + r * 1.25, strokep(C('#3a3a50'), 14))
    cv.drawCircle(x, y, r, strokep(C('#5a5a7a'), 10))
    cols = [C('#ffd166'), C('#e2483b'), C('#7ad7ff'), C('#3fbf6b')]
    for i in range(10):
        a = i / 10 * 2 * math.pi + T * 0.3; px, py = x + math.cos(a) * r, y + math.sin(a) * r
        cv.drawLine(x, y, px, py, strokep(C('#5a5a7a'), 5))
        cv.drawCircle(px, py, 10, fillp(cols[i % 4])); cv.drawCircle(px, py, 26, fillp(cols[i % 4], alpha=0.3, blur=10))
        cv.drawRoundRect(skia.Rect(px - 26, py + 8, px + 26, py + 50), 8, 8, fillp(cols[(i + 1) % 4])); cv.drawRoundRect(skia.Rect(px - 26, py + 8, px + 26, py + 50), 8, 8, strokep(INK, 4))

def house_ext(cv, x, y, s=1.0, lit=(1, 1, 0, 1), col=C('#7a8aa0')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    soft_shadow(cv, 0, 0, 380, 30, 0.4)
    cv.drawRect(skia.Rect(-340, -420, 340, 0), fillp(shader=lin((-340, 0), (340, 0), [shade(col, 1.1), shade(col, 0.8)])))
    for i in range(1, 12): cv.drawLine(-340, -i * 36, 340, -i * 36, strokep(shade(col, 0.7), 3))
    cv.drawRect(skia.Rect(-340, -420, 340, 0), strokep(INK, 8))
    roof = poly([(-390, -410), (390, -410), (0, -680)])
    cv.drawPath(roof, fillp(C('#3a3240'))); cv.drawPath(roof, strokep(INK, 8))
    cv.drawRect(skia.Rect(160, -650, 230, -520), fillp(C('#6a4a3a'))); cv.drawRect(skia.Rect(160, -650, 230, -520), strokep(INK, 6))
    wins = [(-250, -360), (110, -360), (-250, -170), (110, -170)]
    for (wx, wy), on in zip(wins, lit):
        c = C('#ffd27a') if on else C('#1a2038')
        cv.drawRect(skia.Rect(wx, wy, wx + 140, wy + 110), fillp(c)); cv.drawRect(skia.Rect(wx, wy, wx + 140, wy + 110), strokep(INK, 6))
        cv.drawLine(wx + 70, wy, wx + 70, wy + 110, strokep(INK, 4)); cv.drawLine(wx, wy + 55, wx + 140, wy + 55, strokep(INK, 4))
        if on: cv.drawCircle(wx + 70, wy + 55, 120, fillp(C('#ffcc66'), alpha=0.15, blur=40))
    cv.drawRect(skia.Rect(-50, -200, 50, 0), fillp(C('#5a3a2a'))); cv.drawRect(skia.Rect(-50, -200, 50, 0), strokep(INK, 6))
    cv.restore()

def bars(cv, x0, x1, y0, y1, n=7, col=C('#5a5f6a')):
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n; cv.drawRect(skia.Rect(x - 12, y0, x + 12, y1), fillp(col)); cv.drawRect(skia.Rect(x - 12, y0, x + 12, y1), strokep(INK, 4))
    for yy in (y0 + 40, y1 - 40): cv.drawRect(skia.Rect(x0 - 20, yy - 16, x1 + 20, yy + 16), fillp(shade(col, 0.85))); cv.drawRect(skia.Rect(x0 - 20, yy - 16, x1 + 20, yy + 16), strokep(INK, 4))
_hair_old14 = hair
def hair(cv, x, y, u, kind, back=False):
    if kind == 'spiky_dark':
        if back: return
        p = skia.Path(); p.moveTo(x - u * 0.95, y - u * 0.2)
        for (a, b) in [(-1.0, -0.9), (-0.6, -0.95), (-0.5, -1.4), (-0.15, -1.0), (0.05, -1.5), (0.3, -1.0), (0.55, -1.4), (0.65, -0.9), (1.0, -0.95), (0.95, -0.2)]:
            p.lineTo(x + a * u, y + b * u)
        p.quadTo(x, y - u * 0.75, x - u * 0.95, y - u * 0.2); p.close()
        cv.drawPath(p, fillp(C('#2a1e18'))); cv.drawPath(p, strokep(INK, u * 0.08))
        return
    return _hair_old14(cv, x, y, u, kind, back)
CHARS['daniel']['hair'] = 'spiky_dark'

# ---- additions for the Chris Lemons story
CHARS.update({
    'chris_d': dict(adult=True, shirt=C('#26303c'), stripe=C('#e2483b'), hair='divehelm', pants=C('#26303c')),
    'dave_d':  dict(adult=True, shirt=C('#1f2f4a'), stripe=C('#7ad7ff'), hair='divehelm', pants=C('#1f2f4a')),
    'chris':   dict(adult=True, shirt=C('#26303c'), stripe=C('#e2483b'), hair='short', pants=C('#26303c')),
    'duncan':  dict(adult=True, shirt=C('#2a3a2a'), stripe=C('#f0c020'), hair='beanie', pants=C('#2a3a2a')),
    'crewm':   dict(adult=True, shirt=C('#e86a2a'), stripe=C('#f4f4f0'), hair='bcap', pants=C('#2a2f3d')),
    'crewm2':  dict(adult=True, shirt=C('#e86a2a'), stripe=C('#f4f4f0'), hair='short_black', pants=C('#2a2f3d')),
    'expert':  dict(adult=True, shirt=C('#f5f5f2'), coat=True, tie=None, inner=C('#5a7aa0'), hair='bald_grey', glasses=True, pants=C('#3a3f55')),
})
def sea_bg(cv, T, dark=0.0, rays=True, top=C('#0e4a6e'), bot=C('#020a14')):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [top, bot])))
    if rays:
        for i in range(5):
            x = 100 + i * 220 + math.sin(T * 0.5 + i) * 40
            cv.drawPath(poly([(x - 40, -50), (x + 40, -50), (x + 180, 1400), (x - 60, 1400)]), fillp(C('#8fd8ff'), alpha=0.05 * (1 - dark)))
    particles(cv, T, 80, 7, C('#bfe8e0'))
    if dark > 0: cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(skia.Color(0, 4, 10, int(255 * dark))))

def seabed(cv, y=1500, col=C('#2a3a3a')):
    p = skia.Path(); p.moveTo(-300, y)
    for i in range(10): p.quadTo(-300 + i * 180 + 90, y - 25 + (i % 2) * 30, -300 + (i + 1) * 180, y + (i % 3) * 6)
    p.lineTo(W + 300, H + 300); p.lineTo(-300, H + 300); p.close()
    cv.drawPath(p, fillp(shader=lin((0, y), (0, H), [col, shade(col, 0.5)]))); cv.drawPath(p, strokep(INK, 5))
    rnd = random.Random(2)
    for i in range(14): x = rnd.uniform(0, W); cv.drawOval(skia.Rect(x - 30, y + rnd.uniform(20, 300), x + 30, y + rnd.uniform(20, 300) + 16), fillp(shade(col, 0.8)))

def structure(cv, x, y, s=1.0, col=C('#d8a020')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    for (a, b, c, d) in ((-300, 0, -300, -300), (300, 0, 300, -300), (-300, -300, 300, -300), (-300, -150, 300, -150), (-300, 0, 300, -300), (300, 0, -300, -300)):
        cv.drawLine(a, b, c, d, strokep(INK, 40)); cv.drawLine(a, b, c, d, strokep(col, 28))
    cv.drawRect(skia.Rect(-340, -330, 340, -290), fillp(shade(col, 0.8))); cv.drawRect(skia.Rect(-340, -330, 340, -290), strokep(INK, 6))
    cv.drawRoundRect(skia.Rect(-420, -40, 420, 30), 30, 30, fillp(C('#5a6068'))); cv.drawRoundRect(skia.Rect(-420, -40, 420, 30), 30, 30, strokep(INK, 6))
    cv.restore()

def umbilical(cv, pts, col=C('#f0c020'), w=16, alpha=1.0):
    p = skia.Path(); p.moveTo(*pts[0])
    if len(pts) == 3: p.quadTo(*pts[1], *pts[2])
    else:
        for q in pts[1:]: p.lineTo(*q)
    cv.drawPath(p, strokep(INK, w + 8, alpha=alpha)); cv.drawPath(p, strokep(col, w, alpha=alpha))
    return p

def dsv(cv, x, y, s=1.0, rot=0, lights=True):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    hull = skia.Path(); hull.moveTo(-420, -40); hull.lineTo(420, -60); hull.quadTo(400, 80, 260, 120); hull.lineTo(-360, 120); hull.quadTo(-420, 60, -420, -40); hull.close()
    cv.drawPath(hull, fillp(C('#1f2a3a'))); cv.drawPath(hull, strokep(INK, 7))
    cv.drawRect(skia.Rect(-420, 10, 410, 50), fillp(C('#e86a2a')))
    cv.drawRect(skia.Rect(80, -230, 330, -50), fillp(C('#f4f1ea'))); cv.drawRect(skia.Rect(80, -230, 330, -50), strokep(INK, 6))
    for k in range(4): cv.drawRect(skia.Rect(100 + k * 55, -200, 135 + k * 55, -165), fillp(C('#ffd27a') if lights else C('#9fd0f0')))
    cv.drawRect(skia.Rect(260, -320, 330, -230), fillp(C('#f4f1ea'))); cv.drawRect(skia.Rect(260, -320, 330, -230), strokep(INK, 6))
    cv.drawLine(-200, -50, -280, -360, strokep(INK, 22)); cv.drawLine(-200, -50, -280, -360, strokep(C('#f0c020'), 14))
    cv.drawLine(-280, -360, -380, -60, strokep(INK, 4))
    cv.drawRect(skia.Rect(-120, -140, 20, -50), fillp(C('#c9ced8'))); cv.drawRect(skia.Rect(-120, -140, 20, -50), strokep(INK, 5))
    cv.restore()

def waves(cv, T, y=700, amp=40, col=C('#16324a'), k=0.012, speed=2.0, alpha=1.0):
    p = skia.Path(); p.moveTo(-300, H + 300); p.lineTo(-300, y)
    for xx in range(-300, W + 320, 20): p.lineTo(xx, y + math.sin(xx * k + T * speed) * amp + math.sin(xx * k * 2.3 - T * speed * 1.3) * amp * 0.4)
    p.lineTo(W + 300, H + 300); p.close()
    cv.drawPath(p, fillp(col, alpha=alpha)); cv.drawPath(p, strokep(C('#bfe8ff'), 5, alpha=0.6 * alpha))

def rain(cv, T, n=120, seed=4, a=0.5, slant=0.35):
    rnd = random.Random(seed)
    for i in range(n):
        x = (rnd.uniform(0, W + 300) - T * 300 * slant) % (W + 300) - 150; y = (rnd.uniform(0, H) + T * 1600) % H
        cv.drawLine(x, y, x - 40 * slant, y + 40, strokep(C('#cfe4f0'), 3, alpha=a))

def rov(cv, x, y, s=1.0, T=0, lights=True, beam_to=None):
    if lights and beam_to: beam(cv, x + 110 * s, y + 20 * s, beam_to[0], beam_to[1], 0.3, 150)
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-150, -100, 150, 90), 24, 24, fillp(C('#f0c020'))); cv.drawRoundRect(skia.Rect(-150, -100, 150, 90), 24, 24, strokep(INK, 7))
    cv.drawRect(skia.Rect(-150, -30, 150, 0), fillp(C('#2a2e38')))
    for tx in (-170, 170): cv.drawRoundRect(skia.Rect(tx - 25, -70, tx + 25, 50), 14, 14, fillp(C('#3a3e47'))); cv.drawRoundRect(skia.Rect(tx - 25, -70, tx + 25, 50), 14, 14, strokep(INK, 5))
    cv.drawCircle(110, 20, 22, fillp(C('#fff6c0') if lights else C('#5a5f6a'))); cv.drawCircle(110, 20, 22, strokep(INK, 5))
    cv.drawCircle(60, 40, 14, fillp(C('#1b1b22'))); cv.drawCircle(60, 40, 6, fillp(C('#e2483b')))
    cv.drawLine(0, -100, 0, -400, strokep(INK, 8))
    cv.restore()

def dive_bell(cv, x, y, s=1.0, lit=True, hatch=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawLine(0, -260, 0, -2000, strokep(INK, 10))
    b = skia.Path(); b.addRoundRect(skia.Rect(-200, -260, 200, 200), 160, 160)
    cv.drawPath(b, fillp(shader=lin((-200, 0), (200, 0), [C('#f0c020'), C('#b07a10')]))); cv.drawPath(b, strokep(INK, 8))
    for i in range(3): cv.drawCircle(-90 + i * 90, -110, 34, fillp(C('#ffd27a') if lit else C('#2a3a4a'))); cv.drawCircle(-90 + i * 90, -110, 34, strokep(INK, 6))
    if lit: cv.drawCircle(0, -110, 260, fillp(C('#ffd27a'), alpha=0.15, blur=60))
    cv.drawOval(skia.Rect(-110, 170, 110, 230), fillp(C('#ffd27a') if lit else C('#1a2a3a'))); cv.drawOval(skia.Rect(-110, 170, 110, 230), strokep(INK, 6))
    cv.restore()

def gauge(cv, x, y, r, frac, label='AIR', col=C('#3fbf6b')):
    cv.drawCircle(x, y, r, fillp(C('#f4efe2'))); cv.drawCircle(x, y, r, strokep(INK, r * 0.1))
    cv.drawArc(skia.Rect(x - r * 0.8, y - r * 0.8, x + r * 0.8, y + r * 0.8), 135, 270, False, strokep(C('#d0d4da'), r * 0.12))
    cv.drawArc(skia.Rect(x - r * 0.8, y - r * 0.8, x + r * 0.8, y + r * 0.8), 135, 270 * frac, False, strokep(col if frac > 0.25 else C('#e2483b'), r * 0.12))
    a = math.radians(135 + 270 * frac)
    cv.drawLine(x, y, x + math.cos(a) * r * 0.7, y + math.sin(a) * r * 0.7, strokep(INK, r * 0.06)); cv.drawCircle(x, y, r * 0.08, fillp(INK))
    text(cv, label, x, y + r * 0.55, r * 0.25, INK)

def icon_bulb(cv, x, y, s=1.0, on=True):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawCircle(0, -20, 70, fillp(C('#ffd166') if on else C('#5a5f6a'))); cv.drawCircle(0, -20, 70, strokep(INK, 7))
    cv.drawRect(skia.Rect(-32, 45, 32, 95), fillp(C('#9aa0aa'))); cv.drawRect(skia.Rect(-32, 45, 32, 95), strokep(INK, 6)); cv.restore()

def icon_flame(cv, x, y, s=1.0, col=C('#ff8a3a')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    p = skia.Path(); p.moveTo(0, -110); p.quadTo(90, -20, 60, 50); p.quadTo(30, 100, 0, 100); p.quadTo(-30, 100, -60, 50); p.quadTo(-90, -20, 0, -110); p.close()
    cv.drawPath(p, fillp(col)); cv.drawPath(p, strokep(INK, 7))
    q = skia.Path(); q.moveTo(0, -20); q.quadTo(40, 30, 25, 65); q.quadTo(0, 85, -25, 65); q.quadTo(-40, 30, 0, -20); q.close(); cv.drawPath(q, fillp(C('#ffd166')))
    cv.restore()

def icon_radio(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-60, -80, 60, 100), 18, 18, fillp(C('#3a3e47'))); cv.drawRoundRect(skia.Rect(-60, -80, 60, 100), 18, 18, strokep(INK, 7))
    cv.drawLine(30, -80, 30, -150, strokep(INK, 8)); cv.drawRect(skia.Rect(-40, -55, 40, 0), fillp(C('#7cf29a')))
    for i in range(3): cv.drawLine(-35, 25 + i * 22, 35, 25 + i * 22, strokep(C('#9aa0aa'), 6))
    cv.restore()

def icon_air(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    for (bx, by, r) in ((0, 0, 50), (-50, 70, 30), (40, 80, 24), (-10, -90, 22)): cv.drawCircle(bx, by, r, fillp(C('#bfe8ff'), alpha=0.7)); cv.drawCircle(bx, by, r, strokep(C('#ffffff'), 5))
    cv.restore()

def cross(cv, x, y, r=110, k=1.0, col=C('#e2483b')):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.scale(k, k)
    cv.drawLine(-r, -r, r, r, strokep(col, r * 0.22)); cv.drawLine(r, -r, -r, r, strokep(col, r * 0.22)); cv.restore()

def brain_icon(cv, x, y, s=1.0, col=C('#ff9fb0')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    for (bx, by, r) in ((-80, -30, 90), (40, -60, 100), (100, 30, 80), (-40, 50, 85), (0, -10, 90)):
        cv.drawCircle(bx, by, r, fillp(col))
    for (bx, by, r) in ((-80, -30, 90), (40, -60, 100), (100, 30, 80), (-40, 50, 85)):
        cv.drawArc(skia.Rect(bx - r * 0.6, by - r * 0.6, bx + r * 0.6, by + r * 0.6), 200, 140, False, strokep(shade(col, 0.75), 10))
    cv.drawLine(0, -140, 0, 130, strokep(shade(col, 0.7), 8))
    cv.restore()

def snowflake(cv, x, y, r, rot=0, col=C('#bfe8ff')):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    for i in range(6):
        cv.save(); cv.rotate(i * 60); cv.drawLine(0, 0, 0, -r, strokep(col, r * 0.12))
        for f in (0.5, 0.75): cv.drawLine(0, -r * f, r * 0.2, -r * (f + 0.15), strokep(col, r * 0.08)); cv.drawLine(0, -r * f, -r * 0.2, -r * (f + 0.15), strokep(col, r * 0.08))
        cv.restore()
    cv.restore()

def o2_icon(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    for dx in (-60, 60): cv.drawCircle(dx, 0, 75, fillp(C('#e2483b'))); cv.drawCircle(dx, 0, 75, strokep(INK, 7))
    text(cv, 'O', -60, 25, 70, C('#ffffff')); text(cv, 'O', 60, 25, 70, C('#ffffff'))
    cv.restore()

def northsea_map(cv, T, pin=1.0):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#1a4a72')))
    for i in range(0, W, 60): cv.drawLine(i, 0, i, H, strokep(C('#2a5a82'), 2))
    uk = poly([(80, 600), (220, 560), (300, 700), (330, 900), (420, 1080), (380, 1250), (260, 1400), (120, 1450), (60, 1300), (120, 1150), (40, 1000), (90, 820)])
    nor = poly([(820, 300), (1000, 250), (1120, 400), (1120, 1100), (980, 1000), (860, 900), (780, 760), (800, 560)])
    dk = poly([(820, 1200), (920, 1150), (960, 1300), (880, 1420), (800, 1350)])
    for p in (uk, nor, dk): cv.drawPath(p, fillp(C('#5fae6a'))); cv.drawPath(p, strokep(INK, 6))
    k = pin
    if k > 0:
        cv.save(); cv.translate(560, 860); cv.scale(k, k)
        cv.drawCircle(0, -40, 30, fillp(C('#e2483b'))); cv.drawPath(poly([(-26, -26), (26, -26), (0, 20)]), fillp(C('#e2483b'))); cv.drawCircle(0, -40, 30, strokep(INK, 5)); cv.drawCircle(0, -40, 11, fillp(C('#ffffff')))
        cv.restore()

# ---- additions for the Canuck story
CHARS.update({
    'boy':    dict(adult=False, shirt=C('#e85d3a'), stripe=C('#ffd27a'), hair='cowlick', pants=C('#3d5a9a')),
    'woman2': dict(adult=True, shirt=C('#58b3a0'), stripe=None, hair='bob', glasses=True, pants=C('#3b3550')),
    'camop':  dict(adult=True, shirt=C('#5a6a7a'), stripe=None, hair='bcap', pants=C('#2a2f3d')),
    'pass1':  dict(adult=True, shirt=C('#b56fc7'), stripe=None, hair='bun', pants=C('#3b3550')),
    'pass2':  dict(adult=True, shirt=C('#7d8f6e'), stripe=None, hair='short', pants=C('#5a4a3a')),
    'pass3':  dict(adult=True, shirt=C('#d9a441'), stripe=None, hair='curly', pants=C('#38465f')),
})
def knife(cv, x, y, s=1.0, ang=0, glint=0.0):
    cv.save(); cv.translate(x, y); cv.rotate(ang); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-110, -16, -10, 16), 10, 10, fillp(C('#2a2a30'))); cv.drawRoundRect(skia.Rect(-110, -16, -10, 16), 10, 10, strokep(INK, 5))
    for i in range(3): cv.drawCircle(-85 + i * 28, 0, 4, fillp(C('#9aa0aa')))
    b = skia.Path(); b.moveTo(-10, -14); b.lineTo(130, -10); b.quadTo(170, 0, 150, 14); b.lineTo(-10, 14); b.close()
    cv.drawPath(b, fillp(shader=lin((0, -14), (0, 14), [C('#ffffff'), C('#b9c2cc')]))); cv.drawPath(b, strokep(INK, 5))
    if glint > 0: sparkle(cv, 110, -8, 36 * glint, a=glint)
    cv.restore()

def crow(cv, x, y, s=1.0, T=0, flap=None, facing=1, beak=0.0, knife_=False, band=True, eye='open', tilt=0, perched=False, baby=False, look=(0, 0)):
    cv.save(); cv.translate(x, y); cv.rotate(tilt); cv.scale(s * facing, s)
    body_c = [C('#2a2f44'), C('#0c0e16')]
    if baby: body_c = [C('#4a4f60'), C('#2a2e3a')]
    # tail
    tail = poly([(-120, 10), (-250, -10 if not perched else 60), (-250, 40 if not perched else 110), (-110, 50)])
    cv.drawPath(tail, fillp(C('#10121c'))); cv.drawPath(tail, strokep(INK, 6))
    # legs
    if perched or not flap:
        for lx in (-20, 30):
            cv.drawLine(lx, 70, lx - 5, 150, strokep(C('#2a2a30'), 9))
            for d in (-25, 0, 25): cv.drawLine(lx - 5, 150, lx - 5 + d, 170, strokep(C('#2a2a30'), 7))
        if band: cv.drawRoundRect(skia.Rect(-35, 100, -5, 118), 5, 5, fillp(C('#e2312c'))); cv.drawRoundRect(skia.Rect(-35, 100, -5, 118), 5, 5, strokep(INK, 3))
    else:
        for lx in (-10, 30): cv.drawLine(lx, 60, lx - 40, 120, strokep(C('#2a2a30'), 9))
        if band: cv.drawRoundRect(skia.Rect(-40, 82, -10, 100), 5, 5, fillp(C('#e2312c')))
        if knife_ is True: knife(cv, -40, 135, 0.8, 8)
    if knife_ is True and (perched or not flap): knife(cv, 0, 175, 0.8, 0)
    # body
    body = skia.Path(); body.addOval(skia.Rect(-140, -80, 120, 90))
    cv.drawPath(body, fillp(shader=rad((-20, -50), 200, body_c))); cv.drawPath(body, strokep(INK, 7))
    if baby:
        for i in range(8): a = i * 0.8; cv.drawLine(math.cos(a) * 110, math.sin(a) * 70, math.cos(a) * 135, math.sin(a) * 90, strokep(C('#4a4f60'), 8))
    # head
    cv.drawCircle(110, -70, 75, fillp(shader=rad((90, -100), 110, body_c))); cv.drawCircle(110, -70, 75, strokep(INK, 7))
    # beak
    bo = beak * 18
    up = poly([(165, -95), (260, -70 + bo * 0.2), (170, -62)]); lo = poly([(168, -62), (245, -60 + bo), (165, -45)])
    cv.drawPath(lo, fillp(C('#4a4f5a'))); cv.drawPath(lo, strokep(INK, 5))
    cv.drawPath(up, fillp(C('#5a606c'))); cv.drawPath(up, strokep(INK, 5))
    if knife_ == 'beak': knife(cv, 240, -60, 0.7, 12)
    # eye
    ex, ey = 130 + look[0] * 6, -85 + look[1] * 6
    if eye == 'closed': cv.drawLine(ex - 18, ey, ex + 18, ey, strokep(C('#f4f4f0'), 6))
    else:
        cv.drawCircle(ex, ey, 22, fillp(C('#f4f4f0'))); cv.drawCircle(ex, ey, 22, strokep(INK, 4))
        cv.drawCircle(ex + 6 + look[0] * 5, ey + look[1] * 5, 11, fillp(INK)); cv.drawCircle(ex + 9, ey - 5, 4, fillp(C('#ffffff')))
        if eye == 'smug': cv.drawLine(ex - 24, ey - 14, ex + 22, ey - 4, strokep(INK, 7))
    # wing
    if flap is None:
        w = skia.Path(); w.moveTo(-90, -30); w.quadTo(20, -60, 60, 10); w.quadTo(-20, 60, -130, 30); w.close()
        cv.drawPath(w, fillp(C('#181b28'))); cv.drawPath(w, strokep(INK, 5))
    else:
        a = math.sin(flap) * 55
        cv.save(); cv.translate(0, -30); cv.rotate(-a - 20)
        w = skia.Path(); w.moveTo(-40, 0); w.lineTo(-60, -230); w.lineTo(-10, -260); w.lineTo(20, -230); w.lineTo(50, -250); w.lineTo(70, -200); w.lineTo(60, 0); w.close()
        cv.drawPath(w, fillp(C('#181b28'))); cv.drawPath(w, strokep(INK, 6))
        for fx in (-30, 0, 30): cv.drawLine(fx, -30, fx + 5, -200, strokep(C('#2a2f44'), 4))
        cv.restore()
    cv.restore()

def parking_lot(cv, T, sky=(C('#7ab8e8'), C('#d8ecf8')), y0=1050):
    cv.drawRect(skia.Rect(-300, -300, W + 300, y0), fillp(shader=lin((0, 0), (0, y0), list(sky))))
    for (mx, mh, mw) in ((150, 260, 300), (520, 330, 380), (900, 240, 300)):
        cv.drawPath(poly([(mx - mw, y0), (mx, y0 - mh), (mx + mw, y0)]), fillp(C('#8aa6c0'), alpha=0.7))
        cv.drawPath(poly([(mx - mw * 0.25, y0 - mh * 0.75), (mx, y0 - mh), (mx + mw * 0.25, y0 - mh * 0.75)]), fillp(C('#f4f8fc'), alpha=0.8))
    for i, (bx, bw, bh) in enumerate(((40, 110, 320), (170, 90, 420), (290, 120, 260), (760, 100, 380), (880, 130, 300))):
        cv.drawRect(skia.Rect(bx, y0 - bh, bx + bw, y0), fillp(C('#6a8098'))); cv.drawRect(skia.Rect(bx, y0 - bh, bx + bw, y0), strokep(C('#5a6e84'), 3))
        for wy in range(int(y0 - bh + 30), int(y0 - 20), 50):
            for wx in range(bx + 15, bx + bw - 15, 30): cv.drawRect(skia.Rect(wx, wy, wx + 14, wy + 22), fillp(C('#c9dcec')))
    cv.drawRect(skia.Rect(-300, y0, W + 300, H + 300), fillp(shader=lin((0, y0), (0, H), [C('#5a5e66'), C('#3a3e46')])))
    for i in range(6):
        x = -100 + i * 260; cv.drawPath(poly([(x, y0 + 80), (x + 30, y0 + 80), (x - 60, H), (x - 110, H)]), fillp(C('#e8e8e0'), alpha=0.7))

def police_tape(cv, y, x0=-50, x1=W + 50, sag=40, ang=0):
    p = skia.Path(); p.moveTo(x0, y); p.quadTo((x0 + x1) / 2, y + sag, x1, y + ang)
    cv.drawPath(p, strokep(INK, 40)); cv.drawPath(p, strokep(C('#f0d020'), 32))
    meas = skia.PathMeasure(p, False); L = meas.getLength()
    f = skia.Font(skia.Typeface('Poppins', skia.FontStyle.Bold()), 22)
    d = 60
    while d < L - 200:
        pos, tan = meas.getPosTan(d)
        cv.save(); cv.translate(pos.x(), pos.y()); cv.rotate(math.degrees(math.atan2(tan.y(), tan.x())))
        cv.drawString('POLICE LINE', -70, 8, f, fillp(INK)); cv.restore(); d += 220

def marker(cv, x, y, n='1', s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    p = poly([(-50, 0), (50, 0), (30, -90), (-30, -90)]); cv.drawPath(p, fillp(C('#f0c020'))); cv.drawPath(p, strokep(INK, 5))
    text(cv, n, 0, -22, 52, INK); cv.restore()

def flames(cv, x, y, s=1.0, T=0):
    for i in range(7):
        h = (120 + 60 * math.sin(T * 9 + i * 1.7)) * s; w = 60 * s
        fx = x + (i - 3) * 50 * s
        p = skia.Path(); p.moveTo(fx - w / 2, y); p.quadTo(fx - w / 2, y - h * 0.6, fx, y - h); p.quadTo(fx + w / 2, y - h * 0.6, fx + w / 2, y); p.close()
        cv.drawPath(p, fillp(C('#ff7a1a') if i % 2 else C('#ffb020'), alpha=0.9))
    cv.drawCircle(x, y - 80 * s, 260 * s, fillp(C('#ff8a3a'), alpha=0.25, blur=50))
    for i in range(5):
        sy = (T * 80 + i * 90) % 450; cv.drawCircle(x + math.sin(i + T) * 60 * s, y - 200 * s - sy * s, (40 + sy * 0.15) * s, fillp(C('#3a3a40'), alpha=0.5 * (1 - sy / 450)))

def plain_car(cv, x, y, s=1.0, col=C('#6a7a8a'), burnt=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    soft_shadow(cv, 0, 0, 280, 26, 0.4)
    c = mix(col, C('#2a2a2e'), burnt)
    body = skia.Path(); body.moveTo(-280, -40); body.lineTo(-260, -110); body.lineTo(-140, -120); body.lineTo(-80, -200); body.lineTo(120, -200); body.lineTo(190, -120); body.lineTo(280, -105); body.lineTo(290, -40); body.close()
    cv.drawPath(body, fillp(c)); cv.drawPath(body, strokep(INK, 7))
    for gx in (-65, 40): cv.drawPath(poly([(gx, -185), (gx + 80, -185), (gx + 95 if gx > 0 else gx + 80, -130), (gx - 10 if gx < 0 else gx, -130)]), fillp(C('#2a2a30') if burnt > 0.5 else C('#9fc3dc')))
    for wx in (-180, 180): cv.drawCircle(wx, -40, 52, fillp(C('#1b1b22'))); cv.drawCircle(wx, -40, 22, fillp(C('#8a939e')))
    cv.restore()

def nest(cv, x, y, s=1.0, babies=0, T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawOval(skia.Rect(-170, -50, 170, 70), fillp(C('#7a5a3a'))); cv.drawOval(skia.Rect(-170, -50, 170, 70), strokep(INK, 6))
    rnd = random.Random(5)
    for i in range(26):
        a = rnd.uniform(-0.3, 0.3); xx = rnd.uniform(-160, 120)
        cv.drawLine(xx, rnd.uniform(-30, 50), xx + 60, rnd.uniform(-30, 50) + a * 40, strokep(C('#5a3a22'), 6))
    cv.restore()

def coffee_cup(cv, x, y, s=1.0, tilt=0):
    cv.save(); cv.translate(x, y); cv.rotate(tilt); cv.scale(s, s)
    cup = poly([(-60, -160), (60, -160), (45, 0), (-45, 0)])
    cv.drawPath(cup, fillp(C('#f4efe2'))); cv.drawPath(cup, strokep(INK, 6))
    cv.drawRect(skia.Rect(-56, -110, 56, -60), fillp(C('#a86a3a')))
    cv.drawRoundRect(skia.Rect(-70, -185, 70, -155), 10, 10, fillp(C('#3a2a22'))); cv.drawRoundRect(skia.Rect(-70, -185, 70, -155), 10, 10, strokep(INK, 5))
    for i in range(3): cv.drawPath(poly([(-30 + i * 30, -200), (-20 + i * 30, -240), (-30 + i * 30, -280)], close=False), strokep(C('#ffffff'), 5, alpha=0.5))
    cv.restore()

def tv_camera(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    for a in (-25, 0, 25): cv.drawLine(0, 0, math.sin(math.radians(a)) * 260, 360, strokep(C('#3a3e47'), 12))
    cv.drawRoundRect(skia.Rect(-150, -120, 110, 20), 20, 20, fillp(C('#2a2e38'))); cv.drawRoundRect(skia.Rect(-150, -120, 110, 20), 20, 20, strokep(INK, 6))
    cv.drawRoundRect(skia.Rect(110, -95, 200, -10), 12, 12, fillp(C('#3a3e47'))); cv.drawRoundRect(skia.Rect(110, -95, 200, -10), 12, 12, strokep(INK, 5))
    cv.drawCircle(200, -52, 34, fillp(C('#7ad7ff'))); cv.drawCircle(200, -52, 34, strokep(INK, 5))
    text(cv, 'NEWS', -20, -35, 50, C('#e2483b'))
    cv.drawCircle(-120, -100, 10, fillp(C('#e2483b')))
    cv.restore()

def eyeglasses(cv, x, y, s=1.0, rot=0):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    for dx in (-45, 45): cv.drawCircle(dx, 0, 36, fillp(C('#bfe8ff'), alpha=0.5)); cv.drawCircle(dx, 0, 36, strokep(INK, 7))
    cv.drawLine(-9, -4, 9, -4, strokep(INK, 7)); cv.drawLine(-81, -8, -110, -20, strokep(INK, 6)); cv.drawLine(81, -8, 110, -20, strokep(INK, 6))
    cv.restore()

def skyline(cv, y=1250, col=C('#2a3a52')):
    for i, (bx, bw, bh) in enumerate(((0, 120, 380), (110, 90, 560), (200, 140, 300), (340, 80, 640), (420, 150, 420), (570, 100, 700), (670, 130, 380), (800, 110, 520), (910, 170, 330))):
        cv.drawRect(skia.Rect(bx, y - bh, bx + bw, y), fillp(col)); cv.drawRect(skia.Rect(bx, y - bh, bx + bw, y), strokep(INK, 4))
        rnd = random.Random(i)
        for wy in range(int(y - bh + 30), int(y - 20), 46):
            for wx in range(bx + 14, bx + bw - 14, 28):
                if rnd.random() < 0.55: cv.drawRect(skia.Rect(wx, wy, wx + 12, wy + 20), fillp(C('#ffd27a'), alpha=0.85))

# ---- additions for the Lake Nyos story
CHARS.update({
    'farmer':  dict(adult=True, shirt=C('#c96a2a'), stripe=C('#f0c040'), hair='short_black', pants=C('#4a3a2a')),
    'mama':    dict(adult=True, shirt=C('#2a8a6a'), stripe=C('#f0c040'), hair='bun', pants=C('#6a3a5a')),
    'kid1':    dict(adult=False, shirt=C('#e0a030'), stripe=None, hair='short_black', pants=C('#3a3f5a')),
    'kid2':    dict(adult=False, shirt=C('#b04a7a'), stripe=None, hair='pony', pants=C('#3a3f5a')),
    'survivor':dict(adult=True, shirt=C('#7a6a9a'), stripe=None, hair='short_black', pants=C('#3a3a44')),
})
def night_sky(cv, top=C('#050a1e'), bot=C('#1c2a4e'), h=1300, stars=True, moon=(820, 300), seed=1):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, h), [top, bot])))
    if stars:
        rnd = random.Random(seed)
        for i in range(90): cv.drawCircle(rnd.uniform(-100, W + 100), rnd.uniform(-100, h * 0.7), rnd.uniform(1, 2.6), fillp(C('#ffffff'), alpha=rnd.uniform(0.3, 0.9)))
    if moon: cv.drawCircle(*moon, 70, fillp(C('#f2f4ff'))); cv.drawCircle(*moon, 160, fillp(C('#c8d4ff'), alpha=0.15, blur=40))

def day_sky(cv, top=C('#5aa8e8'), bot=C('#dff0fa'), h=1300, sun=(840, 280)):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, h), [top, bot])))
    if sun: cv.drawCircle(*sun, 90, fillp(C('#fff3b0'))); cv.drawCircle(*sun, 220, fillp(C('#fff3b0'), alpha=0.25, blur=50))

def crater_lake(cv, T, night=True, red=0.0, y=900, wobble=0.0, lake_col=None):
    hill = night and C('#16281c') or C('#4a9a4a')
    far = night and C('#0e1c18') or C('#6ab06a')
    cv.drawPath(poly([(-300, y + 120), (100, y - 240), (380, y - 120), (700, y - 300), (1380, y + 120)]), fillp(far))
    p = skia.Path(); p.moveTo(-300, H + 300); p.lineTo(-300, y + 200); p.quadTo(120, y - 180, 300, y - 60); p.lineTo(780, y - 60); p.quadTo(960, y - 180, 1380, y + 200); p.lineTo(1380, H + 300); p.close()
    cv.drawPath(p, fillp(shader=lin((0, y - 180), (0, y + 900), [hill, shade(hill, 0.5)]))); cv.drawPath(p, strokep(INK, 6))
    blue = lake_col or (C('#1a3a6a') if night else C('#2a8ad8'))
    col = mix(blue, C('#9a3a1a') if not night else C('#5a1e10'), red)
    r = skia.Rect(250, y - 110, 830, y + 10)
    cv.drawOval(r, fillp(shader=lin((0, y - 110), (0, y + 10), [shade(col, 1.25), shade(col, 0.8)]))); cv.drawOval(r, strokep(INK, 6))
    for i in range(3):
        yy = y - 70 + i * 28 + math.sin(T * 1.5 + i) * 3 * (1 + wobble * 8)
        cv.drawLine(330 + i * 40, yy, 750 - i * 40, yy, strokep(C('#ffffff'), 3, alpha=0.18))
    if night: cv.drawOval(skia.Rect(500, y - 90, 640, y - 60), fillp(C('#f2f4ff'), alpha=0.35))

def round_hut(cv, x, y, s=1.0, lit=True, smoke=0.0, T=0, wall=C('#b98a5a')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    soft_shadow(cv, 0, 0, 170, 22, 0.35)
    cv.drawRect(skia.Rect(-130, -180, 130, 0), fillp(shader=lin((-130, 0), (130, 0), [shade(wall, 1.1), shade(wall, 0.75)]))); cv.drawRect(skia.Rect(-130, -180, 130, 0), strokep(INK, 6))
    roof = poly([(-175, -170), (175, -170), (0, -390)]); cv.drawPath(roof, fillp(C('#c9a050'))); cv.drawPath(roof, strokep(INK, 6))
    for i in range(1, 5): cv.drawLine(-175 + i * 18, -170 - i * 6, 0, -390, strokep(C('#a07a30'), 3))
    cv.drawRoundRect(skia.Rect(-35, -120, 35, 0), 30, 30, fillp(C('#ffd27a') if lit else C('#2a1e14'))); cv.drawRoundRect(skia.Rect(-35, -120, 35, 0), 30, 30, strokep(INK, 5))
    if lit: cv.drawCircle(0, -60, 110, fillp(C('#ffcc66'), alpha=0.2, blur=30))
    if smoke > 0:
        for i in range(4):
            sy = (T * 40 + i * 50) % 200; cv.drawCircle(30 + math.sin(T + i) * 15, -400 - sy, 20 + sy * 0.15, fillp(C('#cfcfcf'), alpha=0.4 * smoke * (1 - sy / 200)))
    cv.restore()

def co2_cloud(cv, pts, T, a=0.45, col=C('#cfe8d8'), outline=False):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close()
    cv.drawPath(p, fillp(col, alpha=a, blur=30))
    for i in range(10):
        q = pts[i * len(pts) // 10]; cv.drawCircle(q[0] + math.sin(T * 2 + i) * 10, q[1] + math.cos(T * 1.7 + i) * 8, 60, fillp(col, alpha=a * 0.6, blur=25))
    if outline:
        cv.drawPath(p, strokep(C('#ffffff'), 5, alpha=0.8, pe=skia.DashPathEffect.Make([24, 18], T * 40)) if False else strokep(C('#ffffff'), 5, alpha=0.7))

def lantern(cv, x, y, s=1.0, flame=1.0, T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawLine(0, -170, 0, -120, strokep(INK, 6)); cv.drawArc(skia.Rect(-30, -200, 30, -140), 180, 180, False, strokep(INK, 6))
    cv.drawRect(skia.Rect(-60, -120, 60, -100), fillp(C('#3a3a40'))); cv.drawRect(skia.Rect(-60, 60, 60, 80), fillp(C('#3a3a40')))
    cv.drawRoundRect(skia.Rect(-55, -100, 55, 60), 20, 20, fillp(C('#cfe4f0'), alpha=0.35)); cv.drawRoundRect(skia.Rect(-55, -100, 55, 60), 20, 20, strokep(INK, 6))
    if flame > 0:
        f = flame * (1 + 0.1 * math.sin(T * 12))
        cv.drawOval(skia.Rect(-14 * f, 20 - 70 * f, 14 * f, 30), fillp(C('#ffb020'))); cv.drawOval(skia.Rect(-7 * f, 25 - 40 * f, 7 * f, 28), fillp(C('#fff0a0')))
        cv.drawCircle(0, -10, 200 * flame, fillp(C('#ffb040'), alpha=0.25 * flame, blur=40))
    cv.restore()

def africa_map(cv, T, pin=1.0):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#1a4a72')))
    for i in range(0, W, 60): cv.drawLine(i, 0, i, H, strokep(C('#2a5a82'), 2))
    af = poly([(300, 380), (520, 330), (700, 400), (820, 560), (900, 720), (840, 800), (800, 960), (740, 1150), (640, 1380), (560, 1520), (470, 1500), (430, 1300), (400, 1100), (330, 980), (230, 900), (160, 760), (180, 560)])
    cv.drawPath(af, fillp(C('#c9a86a'))); cv.drawPath(af, strokep(INK, 7))
    cm = poly([(470, 820), (540, 790), (560, 860), (540, 960), (480, 980), (450, 900)])
    cv.drawPath(cm, fillp(C('#3fbf6b'))); cv.drawPath(cm, strokep(INK, 5))
    if pin > 0:
        cv.save(); cv.translate(505, 830); cv.scale(pin, pin)
        cv.drawCircle(0, -40, 30, fillp(C('#e2483b'))); cv.drawPath(poly([(-26, -26), (26, -26), (0, 20)]), fillp(C('#e2483b'))); cv.drawCircle(0, -40, 30, strokep(INK, 5)); cv.drawCircle(0, -40, 11, fillp(C('#ffffff')))
        cv.restore()

def lake_section(cv, T, gas=0.6, shake=0.0, magma=True, bubbles_on=True):
    cv.drawRect(skia.Rect(-300, -300, W + 300, 420), fillp(C('#0a1430')))
    cv.drawRect(skia.Rect(-300, 420, W + 300, H + 300), fillp(C('#3a2a1e')))
    basin = skia.Path(); basin.moveTo(60, 420); basin.quadTo(540, 1700, 1020, 420); basin.close()
    sh = math.sin(T * 40) * 6 * shake
    cv.save(); cv.translate(sh, 0); cv.clipPath(basin, doAntiAlias=True)
    cv.drawRect(skia.Rect(0, 420, W, H), fillp(shader=lin((0, 420), (0, 1300), [C('#2a6ab0'), C('#0e2a50')])))
    top = 1300 - 500 * gas
    cv.drawRect(skia.Rect(0, top, W, H), fillp(C('#7ad79a'), alpha=0.35))
    cv.drawLine(0, top, W, top, strokep(C('#bff0d0'), 4, alpha=0.6))
    if bubbles_on:
        rnd = random.Random(4)
        for i in range(60):
            bx = rnd.uniform(200, 880); by = top + ((rnd.uniform(0, 600) - T * 30 * (1 + shake * 4)) % 600)
            cv.drawCircle(bx, by, rnd.uniform(4, 10), strokep(C('#e0fff0'), 3, alpha=0.7))
    cv.restore()
    cv.drawPath(basin, strokep(INK, 10))
    if magma:
        cv.drawRect(skia.Rect(-300, 1650, W + 300, H + 300), fillp(shader=lin((0, 1650), (0, H), [C('#a02a10'), C('#ff7a1a')])))
        for i in range(6):
            x = 200 + i * 140; y = 1650 - ((T * 60 + i * 50) % 300)
            cv.drawCircle(x, y, 10, fillp(C('#bff0d0'), alpha=0.6))

def soda(cv, x, y, s=1.0, shake=0.0, T=0, cap=True, foam=0.0):
    sh = math.sin(T * 50) * 14 * shake
    cv.save(); cv.translate(x + sh, y); cv.rotate(math.sin(T * 50) * 6 * shake); cv.scale(s, s)
    b = skia.Path(); b.moveTo(-40, -420); b.lineTo(40, -420); b.lineTo(40, -330); b.quadTo(140, -250, 140, -120); b.lineTo(140, 300); b.quadTo(140, 340, 100, 340); b.lineTo(-100, 340); b.quadTo(-140, 340, -140, 300); b.lineTo(-140, -120); b.quadTo(-140, -250, -40, -330); b.close()
    cv.drawPath(b, fillp(C('#3a8a5a'), alpha=0.85)); cv.drawPath(b, strokep(INK, 8))
    cv.drawRect(skia.Rect(-140, -20, 140, 140), fillp(C('#f4efe2'))); cv.drawRect(skia.Rect(-140, -20, 140, 140), strokep(INK, 6))
    text(cv, 'FIZZ', 0, 85, 70, C('#3a8a5a'))
    rnd = random.Random(2)
    for i in range(20): cv.drawCircle(rnd.uniform(-110, 110), (rnd.uniform(-250, 300) - T * 200 * (0.3 + shake)) % 550 - 250, rnd.uniform(4, 9), strokep(C('#e0fff0'), 3, alpha=0.8))
    if cap: cv.drawRoundRect(skia.Rect(-52, -470, 52, -415), 10, 10, fillp(C('#e2483b'))); cv.drawRoundRect(skia.Rect(-52, -470, 52, -415), 10, 10, strokep(INK, 6))
    if foam > 0:
        for i in range(14):
            a = -math.pi / 2 + (i - 7) * 0.12; r = 600 * foam * (0.5 + (i % 3) * 0.25)
            cv.drawCircle(math.cos(a) * r * 0.5, -430 + math.sin(a) * r, 40 + 30 * foam, fillp(C('#f4f8f0'), alpha=0.9))
    cv.restore()

def cow(cv, x, y, s=1.0, lying=False, T=0, col=C('#8a5a3a')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    if not lying:
        for lx in (-90, -50, 60, 100): cv.drawRect(skia.Rect(lx - 12, -40, lx + 12, 60), fillp(shade(col, 0.7))); cv.drawRect(skia.Rect(lx - 12, -40, lx + 12, 60), strokep(INK, 4))
        by = -90
    else: by = -30
    cv.drawRoundRect(skia.Rect(-140, by - 60, 140, by + 60), 50, 50, fillp(col)); cv.drawRoundRect(skia.Rect(-140, by - 60, 140, by + 60), 50, 50, strokep(INK, 6))
    cv.drawOval(skia.Rect(-60, by - 40, 20, by + 10), fillp(C('#f4efe2'), alpha=0.8))
    hy = by - 40 if not lying else by + 10
    cv.drawRoundRect(skia.Rect(120, hy - 45, 220, hy + 45), 35, 35, fillp(shade(col, 1.1))); cv.drawRoundRect(skia.Rect(120, hy - 45, 220, hy + 45), 35, 35, strokep(INK, 6))
    cv.drawLine(150, hy - 40, 135, hy - 75, strokep(C('#e8e0c8'), 10)); cv.drawLine(190, hy - 40, 205, hy - 75, strokep(C('#e8e0c8'), 10))
    if not lying: cv.drawCircle(190, hy - 8, 7, fillp(INK))
    else: cv.drawLine(180, hy - 8, 200, hy - 8, strokep(INK, 5))
    cv.drawLine(-140, by, -175, by + 50, strokep(INK, 7))
    cv.restore()

def degas_raft(cv, x, y, s=1.0, T=0, jet=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRect(skia.Rect(-120, -20, 120, 20), fillp(C('#d0d4da'))); cv.drawRect(skia.Rect(-120, -20, 120, 20), strokep(INK, 6))
    cv.drawRect(skia.Rect(-14, -60, 14, 400), fillp(C('#8a939e'))); cv.drawRect(skia.Rect(-14, -60, 14, 400), strokep(INK, 5))
    if jet > 0:
        for i in range(22):
            k = ((T * 1.4 + i / 22) % 1)
            h = 520 * jet; px = math.sin(i * 2.3) * 70 * k; py = -60 - h * math.sin(k * math.pi * 0.5) + (k ** 2) * 150
            cv.drawCircle(px, py, 18 + 26 * k, fillp(C('#e8f4ff'), alpha=0.85 * (1 - k * 0.7)))
    cv.restore()

# ---- additions for Operation Mincemeat
_hair_old18 = hair
def hair(cv, x, y, u, kind, back=False):
    if kind in ('fedora', 'peaked', 'peaked_dark'):
        if back: return
        if kind == 'fedora':
            col = C('#5a4a3a')
            cv.drawOval(skia.Rect(x - u * 1.35, y - u * 0.75, x + u * 1.35, y - u * 0.45), fillp(shade(col, 0.85))); cv.drawOval(skia.Rect(x - u * 1.35, y - u * 0.75, x + u * 1.35, y - u * 0.45), strokep(INK, u * 0.07))
            p = skia.Path(); p.moveTo(x - u * 0.8, y - u * 0.6); p.quadTo(x - u * 0.85, y - u * 1.45, x, y - u * 1.35); p.quadTo(x + u * 0.85, y - u * 1.45, x + u * 0.8, y - u * 0.6); p.close()
            cv.drawPath(p, fillp(col)); cv.drawPath(p, strokep(INK, u * 0.07))
            cv.drawRect(skia.Rect(x - u * 0.8, y - u * 0.78, x + u * 0.8, y - u * 0.62), fillp(C('#2a2018')))
        else:
            col = C('#5a6a4a') if kind == 'peaked' else C('#3a3e46')
            cv.drawOval(skia.Rect(x - u * 1.1, y - u * 1.35, x + u * 1.1, y - u * 0.75), fillp(col)); cv.drawOval(skia.Rect(x - u * 1.1, y - u * 1.35, x + u * 1.1, y - u * 0.75), strokep(INK, u * 0.07))
            cv.drawRect(skia.Rect(x - u * 0.85, y - u * 1.0, x + u * 0.85, y - u * 0.7), fillp(shade(col, 0.7))); cv.drawRect(skia.Rect(x - u * 0.85, y - u * 1.0, x + u * 0.85, y - u * 0.7), strokep(INK, u * 0.06))
            cv.drawPath(poly([(x - u * 0.75, y - u * 0.7), (x + u * 0.75, y - u * 0.7), (x + u * 0.9, y - u * 0.5), (x - u * 0.9, y - u * 0.5)]), fillp(C('#1a1a1e')))
            cv.drawCircle(x, y - u * 0.88, u * 0.12, fillp(C('#d8b040')))
        return
    return _hair_old18(cv, x, y, u, kind, back)

CHARS.update({
    'martin':  dict(adult=True, shirt=C('#7a7048'), stripe=None, tie=C('#4a4030'), hair='peaked', pants=C('#6a6040')),
    'spy1':    dict(adult=True, shirt=C('#9a8060'), coat=True, tie=C('#3a2a20'), inner=C('#e8e0d0'), hair='fedora', pants=C('#4a3a2a')),
    'spy2':    dict(adult=True, shirt=C('#3a5070'), stripe=None, tie=C('#1a2030'), hair='slick', pants=C('#2a3a50')),
    'fisher':  dict(adult=True, shirt=C('#3a6a8a'), stripe=C('#e8e0d0'), hair='beanie', pants=C('#4a3a2a')),
    'german':  dict(adult=True, shirt=C('#4a4e56'), stripe=None, tie=None, hair='peaked_dark', pants=C('#3a3e46')),
    'sailor':  dict(adult=True, shirt=C('#1f2a44'), stripe=C('#f4f4f0'), hair='flatcap', pants=C('#1f2a44')),
    'soldier': dict(adult=True, shirt=C('#6a7048'), stripe=None, hair='helmet_army', pants=C('#5a6040')),
})

def paper_bg(cv, col=C('#e9dcc0')):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(col))
    rnd = random.Random(7)
    for i in range(120): cv.drawCircle(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(2, 8), fillp(C('#c9b890'), alpha=0.25))

def desk_bg(cv, lamp=True):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=rad((540, 700), 1200, [C('#5a4630'), C('#140e08')])))
    for i in range(-2, 30): cv.drawLine(-300, i * 70, W + 300, i * 70 + 30, strokep(C('#3a2a1a'), 3, alpha=0.5))
    if lamp: cv.drawCircle(540, 800, 700, fillp(C('#ffe0a0'), alpha=0.18, blur=100))

def stamp(cv, x, y, s_, size=70, col=C('#c8281e'), rot=-12, k=1.0):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(k, k)
    f = skia.Font(skia.Typeface('Poppins', skia.FontStyle.Bold()), size); w = f.measureText(s_)
    r = skia.Rect(-w / 2 - 24, -size * 0.85, w / 2 + 24, size * 0.4)
    cv.drawRoundRect(r, 10, 10, strokep(col, 8, alpha=0.85)); text(cv, s_, 0, 0, size, col)
    cv.restore()

def doc(cv, x, y, w=420, h=560, rot=0, lines=8, title=None, k=1.0, col=C('#f6f0dc'), seed=1):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(k, k)
    soft_shadow(cv, 10, h / 2 + 10, w * 0.55, 20, 0.3)
    r = skia.Rect(-w / 2, -h / 2, w / 2, h / 2); cv.drawRect(r, fillp(col)); cv.drawRect(r, strokep(INK, 5))
    rnd = random.Random(seed)
    y0 = -h / 2 + (110 if title else 60)
    if title: text(cv, title, 0, -h / 2 + 70, 40, INK)
    for i in range(lines):
        cv.drawLine(-w / 2 + 40, y0 + i * 46, -w / 2 + 40 + rnd.uniform(0.5, 0.95) * (w - 80), y0 + i * 46, strokep(C('#6a6050'), 6))
    cv.restore()

def envelope(cv, x, y, s=1.0, rot=0, heart=True, k=1.0):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s * k, s * k)
    r = skia.Rect(-180, -110, 180, 110); cv.drawRect(r, fillp(C('#f8e8e0'))); cv.drawRect(r, strokep(INK, 6))
    cv.drawPath(poly([(-180, -110), (0, 20), (180, -110)], close=False), strokep(INK, 5))
    if heart:
        p = skia.Path(); p.moveTo(0, 70); p.cubicTo(-70, 20, -40, -40, 0, -5); p.cubicTo(40, -40, 70, 20, 0, 70); cv.drawPath(p, fillp(C('#e2483b'))); 
    cv.restore()

def ticket(cv, x, y, s=1.0, rot=0, k=1.0, label='THEATRE'):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s * k, s * k)
    p = skia.Path(); p.addRect(skia.Rect(-170, -70, 170, 70))
    cv.drawPath(p, fillp(C('#e8c070'))); cv.drawPath(p, strokep(INK, 5))
    for yy in range(-60, 70, 20): cv.drawCircle(100, yy, 4, fillp(INK))
    text(cv, label, -30, 10, 40, C('#6a2a1a')); text(cv, 'ADMIT ONE', -30, 50, 24, C('#6a2a1a'))
    cv.restore()

def ring(cv, x, y, s=1.0, k=1.0):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.scale(s * k, s * k)
    cv.drawCircle(0, 30, 70, strokep(C('#e8b830'), 22)); cv.drawCircle(0, 30, 70, strokep(INK, 4))
    cv.drawPath(poly([(-30, -40), (30, -40), (45, -20), (0, 15), (-45, -20)]), fillp(C('#cfeaff'))); cv.drawPath(poly([(-30, -40), (30, -40), (45, -20), (0, 15), (-45, -20)]), strokep(INK, 5))
    sparkle(cv, 20, -40, 26, a=0.9)
    cv.restore()

def briefcase(cv, x, y, s=1.0, rot=0, chain_to=None, open_=0.0):
    if chain_to:
        p = skia.Path(); p.moveTo(x, y - 90 * s); p.quadTo((x + chain_to[0]) / 2, max(y, chain_to[1]) + 60, *chain_to)
        cv.drawPath(p, strokep(C('#9aa0aa'), 10, pe=None) if False else strokep(C('#9aa0aa'), 10))
        meas = skia.PathMeasure(p, False); L = meas.getLength(); d = 0
        while d < L:
            pos, _ = meas.getPosTan(d); cv.drawOval(skia.Rect(pos.x() - 10, pos.y() - 6, pos.x() + 10, pos.y() + 6), strokep(INK, 4)); d += 22
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-60, -110, 60, -70), 14, 14, strokep(C('#3a2a1a'), 14))
    cv.drawRoundRect(skia.Rect(-200, -80, 200, 150), 20, 20, fillp(C('#7a4a2a'))); cv.drawRoundRect(skia.Rect(-200, -80, 200, 150), 20, 20, strokep(INK, 7))
    cv.drawLine(-200, -10, 200, -10, strokep(C('#5a3218'), 6))
    for dx in (-120, 120): cv.drawRect(skia.Rect(dx - 18, -24, dx + 18, 6), fillp(C('#d8b040'))); cv.drawRect(skia.Rect(dx - 18, -24, dx + 18, 6), strokep(INK, 4))
    cv.restore()

def typewriter(cv, x, y, s=1.0, T=0, paper_text='', typed=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    pr = skia.Rect(-220, -620, 220, -120); cv.drawRect(pr, fillp(C('#f6f0dc'))); cv.drawRect(pr, strokep(INK, 5))
    n = int(len(paper_text) * typed)
    f = skia.Font(skia.Typeface('Courier New', skia.FontStyle.Bold()), 40)
    lines_ = paper_text[:n].split('\n')
    for i, ln in enumerate(lines_): cv.drawString(ln, -190, -540 + i * 56, f, fillp(INK))
    cv.drawRoundRect(skia.Rect(-300, -160, 300, -110), 20, 20, fillp(C('#2a2a30'))); cv.drawRoundRect(skia.Rect(-300, -160, 300, -110), 20, 20, strokep(INK, 5))
    body = poly([(-320, -110), (320, -110), (380, 120), (-380, 120)]); cv.drawPath(body, fillp(C('#2e3a34'))); cv.drawPath(body, strokep(INK, 7))
    for r in range(3):
        for i in range(9 - r):
            kx = -260 + r * 30 + i * 62; ky = -60 + r * 55
            press = 6 if (int(T * 12) + i + r) % 7 == 0 and typed < 1 else 0
            cv.drawCircle(kx, ky + press, 22, fillp(C('#e8e0d0'))); cv.drawCircle(kx, ky + press, 22, strokep(INK, 4))
    cv.restore()

def med_map(cv, T, sea=C('#3a6a8a'), land=C('#d8c49a')):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(sea))
    for i in range(0, W, 60): cv.drawLine(i, 0, i, H, strokep(shade(sea, 1.15), 2))
    for j in range(0, H, 60): cv.drawLine(0, j, W, j, strokep(shade(sea, 1.15), 2))
    shapes = {
        'europe': [(-100, -100), (1200, -100), (1200, 500), (1000, 560), (900, 700), (760, 640), (640, 520), (600, 600), (520, 760), (470, 700), (430, 560), (300, 520), (200, 640), (60, 700), (-100, 680)],
        'spain': [(-100, 680), (60, 700), (200, 640), (230, 760), (180, 900), (40, 960), (-100, 940)],
        'italy': [(470, 700), (520, 760), (600, 860), (660, 960), (640, 1000), (580, 930), (520, 860), (470, 780)],
        'sicily': [(540, 1030), (640, 1010), (620, 1080)],
        'sardinia': [(380, 820), (420, 820), (430, 930), (390, 950), (370, 880)],
        'greece': [(820, 760), (900, 780), (930, 900), (880, 1000), (830, 940), (800, 840)],
        'africa': [(-100, 1150), (300, 1120), (540, 1170), (800, 1220), (1200, 1180), (1200, 2100), (-100, 2100)],
    }
    for k, pts in shapes.items():
        p = poly(pts); cv.drawPath(p, fillp(land if k not in ('spain',) else shade(land, 0.92))); cv.drawPath(p, strokep(INK, 5))
    return {'sicily': (600, 1040), 'sardinia': (400, 880), 'greece': (870, 880), 'spain': (100, 820), 'africa': (540, 1300), 'germany': (700, 300), 'london': (300, 200)}

def map_arrow(cv, a, b, k=1.0, col=C('#e2483b'), w=18, bend=-120):
    if k <= 0: return
    p = skia.Path(); mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + bend
    p.moveTo(*a); p.quadTo(mx, my, *b)
    meas = skia.PathMeasure(p, False); L = meas.getLength(); seg = skia.Path(); meas.getSegment(0, L * k, seg, True)
    cv.drawPath(seg, strokep(INK, w + 8)); cv.drawPath(seg, strokep(col, w))
    pos, tan = meas.getPosTan(L * k * 0.999)
    ang = math.atan2(tan.y(), tan.x())
    cv.save(); cv.translate(pos.x(), pos.y()); cv.rotate(math.degrees(ang))
    cv.drawPath(poly([(30, 0), (-25, -28), (-25, 28)]), fillp(col)); cv.drawPath(poly([(30, 0), (-25, -28), (-25, 28)]), strokep(INK, 5)); cv.restore()

def submarine(cv, x, y, s=1.0, surfaced=False):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    b = skia.Path(); b.addRoundRect(skia.Rect(-420, -60, 420, 70), 65, 65)
    cv.drawPath(b, fillp(shader=lin((0, -60), (0, 70), [C('#5a6470'), C('#2a3038')]))); cv.drawPath(b, strokep(INK, 7))
    cv.drawRoundRect(skia.Rect(-60, -170, 90, -50), 20, 20, fillp(C('#4a5460'))); cv.drawRoundRect(skia.Rect(-60, -170, 90, -50), 20, 20, strokep(INK, 6))
    cv.drawLine(20, -170, 20, -260, strokep(INK, 8)); cv.drawLine(20, -260, 50, -260, strokep(INK, 8))
    for i in range(6): cv.drawCircle(-300 + i * 110, 5, 12, fillp(C('#ffd27a') if surfaced else C('#1a2028')))
    cv.drawPath(poly([(-420, 0), (-480, -60), (-480, 60)]), fillp(C('#3a4048'))); cv.drawPath(poly([(-420, 0), (-480, -60), (-480, 60)]), strokep(INK, 5))
    text(cv, 'SERAPH', 260, 20, 34, C('#e8e0d0'))
    cv.restore()

def tank_icon(cv, x, y, s=1.0, col=C('#4a4e56')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-80, -10, 80, 30), 20, 20, fillp(C('#2a2a30'))); cv.drawRect(skia.Rect(-70, -40, 70, -10), fillp(col)); cv.drawRect(skia.Rect(-70, -40, 70, -10), strokep(INK, 4))
    cv.drawRect(skia.Rect(-30, -65, 30, -40), fillp(col)); cv.drawRect(skia.Rect(-30, -65, 30, -40), strokep(INK, 4)); cv.drawLine(30, -55, 100, -60, strokep(INK, 8))
    cv.restore()

def ship_icon(cv, x, y, s=1.0, col=C('#4a4e56')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawPath(poly([(-90, -10), (90, -10), (65, 25), (-70, 25)]), fillp(col)); cv.drawPath(poly([(-90, -10), (90, -10), (65, 25), (-70, 25)]), strokep(INK, 4))
    cv.drawRect(skia.Rect(-30, -45, 30, -10), fillp(col)); cv.drawRect(skia.Rect(-30, -45, 30, -10), strokep(INK, 4))
    cv.restore()

def headstone(cv, x, y, s=1.0, lines_=('WILLIAM MARTIN',), k2=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    p = skia.Path(); p.moveTo(-200, 0); p.lineTo(-200, -380); p.quadTo(-200, -480, 0, -480); p.quadTo(200, -480, 200, -380); p.lineTo(200, 0); p.close()
    cv.drawPath(p, fillp(shader=lin((-200, 0), (200, 0), [C('#e8e4dc'), C('#b8b4ac')]))); cv.drawPath(p, strokep(INK, 7))
    cv.drawLine(0, -440, 0, -340, strokep(C('#8a8680'), 8)); cv.drawLine(-40, -400, 40, -400, strokep(C('#8a8680'), 8))
    for i, ln in enumerate(lines_):
        a = 1 if i == 0 else k2
        if a > 0: text(cv, ln, 0, -260 + i * 80, 40 if i else 46, C('#3a3a3a') if i == 0 else C('#2a4a2a'))
    cv.restore()

# ---- additions for Lascaux
CHARS.update({
    'marcel':  dict(adult=True, shirt=C('#8a5a3a'), stripe=None, hair='short', pants=C('#3a3a44')),
    'jacques': dict(adult=False, shirt=C('#3a6a8a'), stripe=None, hair='cowlick', pants=C('#3a3a44')),
    'georges': dict(adult=False, shirt=C('#6a7a3a'), stripe=None, hair='sidepart', pants=C('#3a3a44')),
    'simon':   dict(adult=False, shirt=C('#b04a3a'), stripe=C('#e8d8b0'), hair='curly', pants=C('#3a3a44')),
    'teacher': dict(adult=True, shirt=C('#5a5a6a'), stripe=None, tie=C('#7a3b2e'), hair='bald_grey', glasses=True, pants=C('#3a3a44')),
    'caveman': dict(adult=True, shirt=C('#8a6a4a'), stripe=C('#6a4a2a'), hair='long', pants=C('#6a4a2a')),
    'tourist1':dict(adult=True, shirt=C('#d07a3a'), stripe=None, hair='bob', pants=C('#3a3f5a')),
    'tourist2':dict(adult=True, shirt=C('#3a8a6a'), stripe=None, hair='short', pants=C('#3a3a44')),
})
OCHRE = C('#b8562a'); YELL = C('#d8a040'); BLK = C('#1e1612')
def rock_wall(cv, T, base=C('#c9a77a'), dark=C('#5a4030'), seed=3, light=None, lr=600):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [base, shade(base, 0.8)])))
    rnd = random.Random(seed)
    for i in range(40):
        x = rnd.uniform(-100, W + 100); y = rnd.uniform(-100, H + 100); r = rnd.uniform(60, 220)
        cv.drawCircle(x, y, r, fillp(shade(base, rnd.uniform(0.85, 1.12)), alpha=0.5, blur=30))
    for i in range(18):
        x = rnd.uniform(0, W); y = rnd.uniform(0, H)
        p = skia.Path(); p.moveTo(x, y)
        for j in range(4): p.lineTo(x + rnd.uniform(-120, 120), y + j * 40 + rnd.uniform(0, 40))
        cv.drawPath(p, strokep(shade(base, 0.7), 4, alpha=0.5))
    if light is not None:
        lx, ly = light
        m = skia.Paint(); m.setShader(skia.GradientShader.MakeRadial((lx, ly), lr, [skia.Color(0, 0, 0, 0), skia.Color(10, 6, 4, 245)], [0.25, 1.0]))
        cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), m)

def cave_animal(cv, kind, x, y, s=1.0, col=OCHRE, k=1.0, facing=1, outline=BLK):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.scale(s * facing, s)
    cv.saveLayer(None, (lambda p: (p.setAlphaf(k * 0.92), p)[1])(skia.Paint()))
    if kind in ('horse', 'deer'):
        b = skia.Path(); b.moveTo(-170, -10); b.cubicTo(-160, -90, 80, -110, 140, -70); b.lineTo(210, -160); b.quadTo(250, -170, 270, -130); b.lineTo(200, -30); b.cubicTo(160, 40, -60, 60, -170, 20); b.close()
        cv.drawPath(b, fillp(col, blur=2))
        cv.save(); cv.translate(275, -105); cv.rotate(50); cv.drawOval(skia.Rect(-70, -32, 70, 32), fillp(col)); cv.drawOval(skia.Rect(-70, -32, 70, 32), strokep(outline, 7)); cv.restore()
        for lx in (-130, -90, 90, 130): cv.drawLine(lx, 20, lx + (10 if lx > 0 else -10), 140, strokep(col, 18))
        cv.drawLine(-170, 0, -230, 90, strokep(col, 14))
        if kind == 'horse':
            for i in range(6): cv.drawLine(150 + i * 12, -90 - i * 12, 130 + i * 12, -120 - i * 12, strokep(BLK, 10))
        else:
            for sx in (-1, 1):
                cv.drawLine(250, -150, 250 + sx * 40, -270, strokep(BLK, 7)); cv.drawLine(250 + sx * 20, -210, 250 + sx * 70, -225, strokep(BLK, 6)); cv.drawLine(250 + sx * 30, -240, 250 + sx * 80, -280, strokep(BLK, 6))
        cv.drawPath(b, strokep(outline, 8))
    elif kind in ('bull', 'bison'):
        b = skia.Path()
        if kind == 'bull':
            b.moveTo(-220, -20); b.cubicTo(-200, -110, 100, -120, 170, -90); b.quadTo(240, -100, 260, -50); b.quadTo(250, 0, 200, 10); b.cubicTo(150, 60, -80, 70, -220, 30); b.close()
        else:
            b.moveTo(-200, 0); b.cubicTo(-190, -80, -20, -100, 40, -170); b.quadTo(160, -200, 210, -100); b.quadTo(260, -60, 230, 0); b.cubicTo(180, 70, -80, 70, -200, 40); b.close()
        cv.drawPath(b, fillp(col, blur=2))
        for lx in (-170, -120, 120, 170): cv.drawLine(lx, 30, lx, 150, strokep(col, 22))
        cv.drawLine(-220, 0, -270, 110, strokep(col, 12))
        cv.drawPath(b, strokep(outline, 9))
        hx = 240 if kind == 'bull' else 220
        cv.drawPath(poly([(hx - 30, -90), (hx - 10, -170), (hx + 20, -100)], close=False), strokep(BLK, 9))
        cv.drawPath(poly([(hx, -90), (hx + 40, -160), (hx + 50, -95)], close=False), strokep(BLK, 9))
        if kind == 'bison':
            for i in range(5): cv.drawLine(-20 + i * 40, -110 - i * 10, -10 + i * 40, -60, strokep(BLK, 7))
    cv.restore(); cv.restore()

def oil_lamp(cv, x, y, s=1.0, T=0, flame=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-60, -20, 60, 40), 20, 20, fillp(C('#6a6a70'))); cv.drawRoundRect(skia.Rect(-60, -20, 60, 40), 20, 20, strokep(INK, 5))
    cv.drawRect(skia.Rect(-10, -40, 10, -20), fillp(C('#3a3a40')))
    if flame > 0:
        f = flame * (1 + 0.12 * math.sin(T * 14) + 0.05 * math.sin(T * 31))
        cv.drawOval(skia.Rect(-16 * f, -40 - 80 * f, 16 * f, -32), fillp(C('#ffb020'))); cv.drawOval(skia.Rect(-8 * f, -40 - 45 * f, 8 * f, -34), fillp(C('#fff0a0')))
        cv.drawCircle(0, -70, 220, fillp(C('#ffb040'), alpha=0.25 * flame, blur=50))
    cv.restore()

def fallen_tree(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawOval(skia.Rect(-150, -40, 150, 60), fillp(C('#0a0604'))); cv.drawOval(skia.Rect(-150, -40, 150, 60), strokep(INK, 6))
    cv.save(); cv.rotate(-12)
    cv.drawRoundRect(skia.Rect(150, -100, 900, -10), 40, 40, fillp(C('#6a4a32'))); cv.drawRoundRect(skia.Rect(150, -100, 900, -10), 40, 40, strokep(INK, 7))
    for i in range(7):
        a = -80 + i * 28; cv.drawLine(160, -55, 160 + math.cos(math.radians(a)) * 220, -55 + math.sin(math.radians(a)) * 220, strokep(C('#5a3a22'), 14))
    cv.drawCircle(160, -55, 110, fillp(C('#6a4a32'), alpha=0.7)); cv.drawCircle(160, -55, 110, strokep(INK, 5))
    cv.restore()
    cv.restore()

def countryside(cv, T):
    day_sky(cv, C('#8ac8f0'), C('#f0f4e0'), h=1100, sun=(860, 260))
    cv.drawPath(poly([(-300, 1050), (200, 880), (600, 960), (1000, 860), (1380, 980), (1380, H + 300), (-300, H + 300)]), fillp(C('#6aa85a')))
    cv.drawPath(poly([(-300, 1250), (300, 1120), (800, 1200), (1380, 1100), (1380, H + 300), (-300, H + 300)]), fillp(C('#4a8a4a')))
    for (x, y, h) in ((120, 1130, 200), (260, 1100, 240), (820, 1150, 220), (960, 1110, 260)):
        cv.drawOval(skia.Rect(x - 40, y - h, x + 40, y), fillp(C('#2e6a3a'))); cv.drawOval(skia.Rect(x - 40, y - h, x + 40, y), strokep(INK, 4))

def woods(cv, T, off=0.0):
    day_sky(cv, C('#bfe0d0'), C('#f0f4e0'), h=1400, sun=None)
    for layer, (col, sc, sp) in enumerate(((C('#7aa86a'), 0.7, 0.3), (C('#4a7a4a'), 1.0, 0.6), (C('#2e5a34'), 1.3, 1.0))):
        for i in range(8):
            x = ((i * 220 - off * 300 * sp) % 1760) - 340
            cv.drawRect(skia.Rect(x - 18 * sc, 600 + layer * 200, x + 18 * sc, 1600), fillp(shade(col, 0.6)))
            cv.drawCircle(x, 600 + layer * 200, 150 * sc, fillp(col)); cv.drawCircle(x, 600 + layer * 200, 150 * sc, strokep(INK, 4))
    cv.drawRect(skia.Rect(-300, 1550, W + 300, H + 300), fillp(C('#6a5a3a')))
    rnd = random.Random(4)
    for i in range(40): cv.drawCircle(rnd.uniform(0, W), rnd.uniform(1560, H), rnd.uniform(6, 14), fillp([C('#c96a2a'), C('#d8a040'), C('#8a4a2a')][i % 3]))

# ---- additions for Mount Pelée
CHARS.update({
    'ludger':  dict(adult=True, shirt=C('#d8c8a8'), stripe=None, hair='short_black', pants=C('#5a4a3a')),
    'mayor':   dict(adult=True, shirt=C('#2a2a34'), stripe=None, tie=C('#e8e0d0'), hair='tophat', pants=C('#2a2a34')),
    'towns1':  dict(adult=True, shirt=C('#e8a040'), stripe=None, hair='bun', pants=C('#6a3a5a')),
    'towns2':  dict(adult=True, shirt=C('#4a8ac8'), stripe=C('#f4f4f0'), hair='short_black', pants=C('#3a3a44')),
    'towns3':  dict(adult=True, shirt=C('#c84a4a'), stripe=None, hair='curly', pants=C('#3a3a44')),
    'gendarme':dict(adult=True, shirt=C('#2a3a6a'), stripe=None, hair='cap', pants=C('#c83a3a')),
    'rescuer': dict(adult=True, shirt=C('#8a7a5a'), stripe=None, hair='flatcap', pants=C('#4a3a2a')),
})
def pelee(cv, x, y, s=1.0, T=0, erupt=0.0, smoke=0.3, col=C('#5a6a4a')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    m = poly([(-700, 0), (-200, -560), (-90, -600), (90, -610), (220, -540), (700, 0)])
    cv.drawPath(m, fillp(shader=lin((-400, 0), (400, -300), [shade(col, 1.15), shade(col, 0.6)]))); cv.drawPath(m, strokep(INK, 8))
    for i in range(5): cv.drawLine(-60 + i * 30, -600, -300 + i * 150, 0, strokep(shade(col, 0.75), 6, alpha=0.6))
    if smoke > 0:
        for i in range(7):
            k = ((T * 0.15 + i / 7) % 1)
            cv.drawCircle(math.sin(i * 1.7 + T * 0.5) * 60 * k, -620 - k * 500, (60 + 140 * k) * (0.6 + smoke), fillp(C('#6a6a6e'), alpha=0.6 * (1 - k) * min(1, smoke * 2)))
    if erupt > 0:
        cv.drawCircle(0, -620, 300 * erupt, fillp(C('#ff7a1a'), alpha=0.5 * erupt, blur=60))
        for i in range(10):
            a = -math.pi / 2 + (i - 5) * 0.22; r = 700 * erupt
            cv.drawCircle(math.cos(a) * r * 0.6, -620 + math.sin(a) * r, 120 * erupt, fillp(C('#4a4446'), alpha=0.85))
        for i in range(12):
            a = -math.pi / 2 + (i - 6) * 0.25; r = 500 * erupt * (0.6 + (i % 3) * 0.2)
            cv.drawCircle(math.cos(a) * r, -620 + math.sin(a) * r, 18, fillp(C('#ffb020')))
    cv.restore()

def town(cv, x0, y, T=0, n=11, ruined=0.0, scale=1.0, seed=2):
    rnd = random.Random(seed)
    cols = [C('#e8c070'), C('#e88a6a'), C('#8ac8d8'), C('#f0e0c0'), C('#c8d88a')]
    x = x0
    for i in range(n):
        w = rnd.uniform(70, 120) * scale; h = rnd.uniform(90, 180) * scale
        col = mix(cols[i % 5], C('#5a5456'), ruined)
        if ruined > 0.5:
            p = poly([(x, y), (x, y - h * 0.5), (x + w * 0.3, y - h * 0.65), (x + w * 0.6, y - h * 0.35), (x + w, y - h * 0.55), (x + w, y)])
            cv.drawPath(p, fillp(col)); cv.drawPath(p, strokep(INK, 4))
        else:
            cv.drawRect(skia.Rect(x, y - h, x + w, y), fillp(col)); cv.drawRect(skia.Rect(x, y - h, x + w, y), strokep(INK, 4))
            cv.drawPath(poly([(x - 6, y - h), (x + w + 6, y - h), (x + w / 2, y - h - 40 * scale)]), fillp(C('#b84a2a'))); cv.drawPath(poly([(x - 6, y - h), (x + w + 6, y - h), (x + w / 2, y - h - 40 * scale)]), strokep(INK, 4))
            for wy in range(int(y - h + 20 * scale), int(y - 20 * scale), int(40 * scale)): cv.drawRect(skia.Rect(x + w * 0.3, wy, x + w * 0.5, wy + 22 * scale), fillp(C('#3a4a5a')))
        x += w + 8 * scale
    if 0 < ruined:
        for i in range(8):
            k = ((T * 0.2 + i / 8) % 1); sx = x0 + (x - x0) * (i + 0.5) / 8
            cv.drawCircle(sx + math.sin(i) * 20, y - 100 - k * 400, 40 + 80 * k, fillp(C('#5a5458'), alpha=0.5 * ruined * (1 - k)))

def sea_strip(cv, y, T, col=C('#2a7ab0')):
    p = skia.Path(); p.moveTo(-300, H + 300); p.lineTo(-300, y)
    for xx in range(-300, W + 320, 30): p.lineTo(xx, y + math.sin(xx * 0.015 + T * 2) * 8)
    p.lineTo(W + 300, H + 300); p.close()
    cv.drawPath(p, fillp(shader=lin((0, y), (0, H), [col, shade(col, 0.6)])))

def pyro_cloud(cv, front_x, y_top, y_bot, T, col=C('#5a5050'), glow=True):
    rnd = random.Random(4)
    for i in range(26):
        fx = front_x - rnd.uniform(0, 900); fy = rnd.uniform(y_top, y_bot)
        r = rnd.uniform(90, 190) * (1 + 0.1 * math.sin(T * 3 + i))
        cv.drawCircle(fx, fy, r, fillp(shade(col, rnd.uniform(0.8, 1.2))))
        if glow and i % 3 == 0: cv.drawCircle(fx, fy + r * 0.4, r * 0.6, fillp(C('#ff6a1a'), alpha=0.35, blur=25))

def stone_cell(cv, T, x=540, y=1100, s=1.0, glow=0.0, inside=True, name='ludger', expr='worried', ground_y=None):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    outer = skia.Rect(-420, -420, 420, 420); inner = skia.Rect(-300, -300, 300, 330)
    cv.drawRect(outer, fillp(C('#7a7468'))); cv.drawRect(outer, strokep(INK, 8))
    rnd = random.Random(1)
    for r_ in range(-420, 420, 70):
        off = 0 if (r_ // 70) % 2 else 50
        for c_ in range(-420 + off, 420, 100): cv.drawRect(skia.Rect(c_, r_, c_ + 100, r_ + 70), strokep(C('#5a5448'), 4))
    cv.drawRect(inner, fillp(C('#2a2620'))); cv.drawRect(inner, strokep(INK, 6))
    cv.drawRect(skia.Rect(150, -260, 300, -220), fillp(mix(C('#9ac8e0'), C('#ff7a1a'), glow))); cv.drawRect(skia.Rect(150, -260, 300, -220), strokep(INK, 5))
    if glow > 0:
        cv.drawPath(poly([(150, -260), (300, -220), (-100, 330), (-300, 330)]), fillp(C('#ff7a1a'), alpha=0.25 * glow))
        cv.drawRect(inner, fillp(C('#ff5a1a'), alpha=0.18 * glow))
    if inside: character(cv, name, -60, 330, 95, t=T, expr=expr, look=(0.5, -0.4), blink_seed=3)
    cv.restore()

def circus_tent(cv, x, y, s=1.0, T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    for i in range(8):
        c = C('#d8312c') if i % 2 == 0 else C('#f4efe2')
        cv.drawPath(poly([(-400 + i * 100, 0), (-300 + i * 100, 0), (0, -600)]), fillp(c))
    cv.drawPath(poly([(-400, 0), (400, 0), (0, -600)]), strokep(INK, 8))
    cv.drawLine(0, -600, 0, -720, strokep(INK, 8))
    p = skia.Path(); p.moveTo(0, -720); p.lineTo(80, -700 + math.sin(T * 5) * 8); p.lineTo(0, -680); p.close(); cv.drawPath(p, fillp(C('#ffd166')))
    cv.drawPath(poly([(-80, 0), (80, 0), (0, -220)]), fillp(C('#1a1210')))
    cv.restore()

# ---- additions for the alien autopsy film
def full(cv, col): cv.drawRect(skia.Rect(-3000, -3000, 5000, 5000), fillp(col))
def zoom_at(cv, z, px, py, tx=540, ty=960):
    cv.translate(tx, ty); cv.scale(z, z); cv.translate(-px, -py)

_hair_old21 = hair
def hair(cv, x, y, u, kind, back=False):
    if kind == 'hazhood':
        if back:
            cv.drawOval(skia.Rect(x - u * 1.3, y - u * 1.35, x + u * 1.3, y + u * 1.25), fillp(C('#f4f4f0'))); cv.drawOval(skia.Rect(x - u * 1.3, y - u * 1.35, x + u * 1.3, y + u * 1.25), strokep(INK, u * 0.07))
            return
        cv.drawRoundRect(skia.Rect(x - u * 0.85, y - u * 0.6, x + u * 0.85, y + u * 0.55), u * 0.3, u * 0.3, strokep(C('#9aa0aa'), u * 0.09))
        return
    if kind == 'shades_spiky':
        if back: return
        _hair_old21(cv, x, y, u, 'spiky', back)
        return
    return _hair_old21(cv, x, y, u, kind, back)

CHARS.update({
    'ray':     dict(adult=True, shirt=C('#2a2a34'), stripe=None, tie=None, hair='slick', glasses=True, pants=C('#2a2a34')),
    'doc1':    dict(adult=True, shirt=C('#f4f4f0'), stripe=None, hair='hazhood', pants=C('#f4f4f0')),
    'sculptor':dict(adult=True, shirt=C('#6a8a9a'), stripe=None, hair='curly', pants=C('#3a3a44')),
    'viewer1': dict(adult=True, shirt=C('#d07a3a'), stripe=None, hair='bob', pants=C('#3a3f5a')),
    'viewer2': dict(adult=True, shirt=C('#3a8a6a'), stripe=None, hair='short', pants=C('#3a3a44')),
    'viewer3': dict(adult=False, shirt=C('#e0a030'), stripe=None, hair='pony', pants=C('#3a3f5a')),
    'ufofan':  dict(adult=True, shirt=C('#3a3a6a'), stripe=C('#7cf29a'), hair='beanie', pants=C('#2a2a34')),
    'pundit1': dict(adult=True, shirt=C('#2a4a7a'), stripe=None, tie=C('#c83a3a'), hair='slick', pants=C('#2a2a34')),
    'pundit2': dict(adult=True, shirt=C('#6a3a3a'), stripe=None, tie=C('#e8d040'), hair='bald_grey', glasses=True, pants=C('#2a2a34')),
})

def alien_body(cv, x, y, s=1.0, sheet=True, T=0, six=True):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    skin = C('#d8d4c8')
    body = skia.Path(); body.addRoundRect(skia.Rect(-60, -80, 360, 80), 70, 70)
    cv.drawPath(body, fillp(skin)); cv.drawPath(body, strokep(INK, 6))
    cv.drawOval(skia.Rect(-280, -120, -40, 110), fillp(skin)); cv.drawOval(skia.Rect(-280, -120, -40, 110), strokep(INK, 6))
    cv.drawOval(skia.Rect(-200, -70, -150, 0), fillp(C('#2a2a30'))); cv.drawOval(skia.Rect(-200, 10, -150, 70), fillp(C('#2a2a30')))
    if sheet:
        sh = skia.Path(); sh.moveTo(40, -100); sh.quadTo(220, -130, 400, -95); sh.lineTo(420, 100); sh.quadTo(220, 120, 30, 100); sh.close()
        cv.drawPath(sh, fillp(C('#f4f4f0'))); cv.drawPath(sh, strokep(INK, 6))
    if six:
        cv.drawCircle(60, 115, 26, fillp(skin)); cv.drawCircle(60, 115, 26, strokep(INK, 5))
        for i in range(6):
            a = math.radians(40 + i * 20); cv.drawLine(60 + math.cos(a) * 20, 115 + math.sin(a) * 20, 60 + math.cos(a) * 60, 115 + math.sin(a) * 60, strokep(skin, 10)); cv.drawLine(60 + math.cos(a) * 20, 115 + math.sin(a) * 20, 60 + math.cos(a) * 60, 115 + math.sin(a) * 60, strokep(INK, 3))
    cv.restore()

def op_table(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRect(skia.Rect(-400, 0, 400, 40), fillp(C('#b8bec6'))); cv.drawRect(skia.Rect(-400, 0, 400, 40), strokep(INK, 6))
    for lx in (-340, 340): cv.drawRect(skia.Rect(lx - 14, 40, lx + 14, 380), fillp(C('#8a9098')))
    cv.restore()

def autopsy_scene(cv, T, focus=0.0, close=False, bg=True):
    if bg:
        cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#c8c4b8')))
        cv.drawRect(skia.Rect(-300, 1350, W + 300, H + 300), fillp(C('#9a968a')))
        cv.drawRect(skia.Rect(100, 200, 980, 260), fillp(C('#8a867a')))
    else:
        cv.drawRect(skia.Rect(-60, 500, 1140, 1500), fillp(C('#e8e4dc'))); cv.drawRect(skia.Rect(-60, 500, 1140, 1500), strokep(INK, 6))
        for x in range(0, 1140, 120): cv.drawLine(x, 500, x + 20, 1500, strokep(C('#c8c4b8'), 5))
    if close:
        cv.save(); zoom_at(cv, 1.8, 480, 1330, 540, 960)
    for i, (x, ex) in enumerate(((210, 'o'), (870, 'neutral'))):
        character(cv, 'doc1', x, 1620, 110, t=T, expr=ex, pose={'hrA': (x + (200 if x < 540 else -200), 1320 + math.sin(T * 3 + i) * 10), 'hlA': (x + (130 if x < 540 else -130), 1350)}, look=(0.6 if x < 540 else -0.6, 0.8), blink_seed=i)
    op_table(cv, 540, 1420, 1.0)
    alien_body(cv, 520, 1340, 0.95, True, T)
    if close: cv.restore()

def bw_film(cv, T, draw_fn, blur=0.0, grain=1.0, timecode=True, tint=True):
    surf = skia.Surface(W, H); c2 = surf.getCanvas(); draw_fn(c2)
    img = surf.makeImageSnapshot()
    p = skia.Paint()
    mat = [0.33, 0.55, 0.12, 0, 0.02] * 3 + [0, 0, 0, 1, 0]
    p.setColorFilter(skia.ColorFilters.Matrix(mat))
    if blur > 0: p.setImageFilter(skia.ImageFilters.Blur(blur, blur))
    flick = 1 + 0.06 * math.sin(T * 37) + 0.04 * math.sin(T * 13)
    cv.drawImage(img, 0, 0, skia.SamplingOptions(), p)
    full(cv, skia.Color(0, 0, 0, int(max(0, min(120, (1 - flick) * 600 + 30)))))
    rnd = random.Random(int(T * 24))
    for i in range(int(260 * grain)):
        cv.drawCircle(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1, 3), fillp(C('#ffffff') if rnd.random() < 0.5 else C('#000000'), alpha=0.35))
    for i in range(3):
        if rnd.random() < 0.6: x = rnd.uniform(0, W); cv.drawLine(x, 0, x + rnd.uniform(-10, 10), H, strokep(C('#e8e8e8'), 2, alpha=0.4))
    vignette(cv, 0.8)
    if tint: full(cv, skia.Color(60, 40, 10, 25))
    if timecode:
        f = skia.Font(skia.Typeface('Courier New', skia.FontStyle.Bold()), 40)
        cv.drawString(f'00:{int(T) // 60:02d}:{int(T) % 60:02d}:{int(T * 24) % 24:02d}', 60, 1820, f, fillp(C('#f4f4f0'), alpha=0.8))

def crt_tv(cv, x, y, s, T, content=None):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-420, -330, 420, 330), 50, 50, fillp(C('#4a4440'))); cv.drawRoundRect(skia.Rect(-420, -330, 420, 330), 50, 50, strokep(INK, 10))
    scr = skia.Rect(-350, -270, 230, 270)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(scr, 60, 60), doAntiAlias=True)
    cv.drawRect(scr, fillp(C('#101010')))
    if content:
        cv.save(); cv.translate(-60, 0); cv.scale(580 / W, 540 / 1000); cv.translate(-540, -900); content(cv); cv.restore()
    for yy in range(-270, 270, 6): cv.drawLine(-350, yy, 230, yy, strokep(C('#000000'), 2, alpha=0.18))
    cv.drawCircle(-60, 0, 420, fillp(C('#9fd8ff'), alpha=0.08, blur=40))
    cv.restore()
    cv.drawRoundRect(scr, 60, 60, strokep(INK, 10))
    for i in range(2): cv.drawCircle(320, -120 + i * 110, 34, fillp(C('#8a7a6a'))); cv.drawCircle(320, -120 + i * 110, 34, strokep(INK, 5))
    for i in range(4): cv.drawLine(270, 120 + i * 30, 370, 120 + i * 30, strokep(INK, 5))
    cv.drawLine(-100, -330, -200, -470, strokep(INK, 7)); cv.drawLine(100, -330, 200, -470, strokep(INK, 7))
    cv.restore()
    cv.drawCircle(x, y, 600 * s, fillp(C('#9fd8ff'), alpha=0.08, blur=80))

def living_room(cv, T, lamp=True):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#5a4a6a')))
    for x in range(-300, W + 300, 70): cv.drawRect(skia.Rect(x, -300, x + 26, 1500), fillp(C('#524362')))
    cv.drawRect(skia.Rect(-300, 1500, W + 300, H + 300), fillp(C('#6a4a32')))
    cv.drawRect(skia.Rect(-300, 1480, W + 300, 1510), fillp(C('#4a3222')))
    if lamp: cv.drawCircle(540, 600, 700, fillp(C('#ffe0a0'), alpha=0.08, blur=80))

def couch(cv, x, y, s=1.0, col=C('#8a3a3a')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-420, -260, 420, -60), 50, 50, fillp(col)); cv.drawRoundRect(skia.Rect(-420, -260, 420, -60), 50, 50, strokep(INK, 7))
    cv.drawRoundRect(skia.Rect(-460, -130, 460, 40), 40, 40, fillp(shade(col, 1.1))); cv.drawRoundRect(skia.Rect(-460, -130, 460, 40), 40, 40, strokep(INK, 7))
    for sx in (-1, 1): cv.drawRoundRect(skia.Rect(sx * 460 - 60, -200, sx * 460 + 60, 40), 40, 40, fillp(shade(col, 0.9))); cv.drawRoundRect(skia.Rect(sx * 460 - 60, -200, sx * 460 + 60, 40), 40, 40, strokep(INK, 6))
    cv.restore()

def film_can(cv, x, y, s=1.0, rot=0, label='TOP SECRET'):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    cv.drawCircle(0, 0, 220, fillp(C('#8a9098'))); cv.drawCircle(0, 0, 220, strokep(INK, 8))
    cv.drawCircle(0, 0, 170, strokep(C('#6a7078'), 6)); cv.drawCircle(0, 0, 40, fillp(C('#5a6068')))
    for i in range(6): a = i * math.pi / 3; cv.drawCircle(math.cos(a) * 100, math.sin(a) * 100, 32, fillp(C('#6a7078')))
    cv.restore()
    if label: stamp(cv, x, y + 30, label, 56, k=1)

def film_strip(cv, x, y, w, h, T, n=4, frame_fn=None, off=0.0):
    cv.drawRect(skia.Rect(x, y, x + w, y + h), fillp(C('#1a1a1a')))
    for i in range(int(w / 40) + 2):
        hx = x + ((i * 40 - off) % (w + 40)) - 20
        cv.drawRoundRect(skia.Rect(hx, y + 10, hx + 22, y + 34), 5, 5, fillp(C('#e8e4d8'))); cv.drawRoundRect(skia.Rect(hx, y + h - 34, hx + 22, y + h - 10), 5, 5, fillp(C('#e8e4d8')))
    fw = (w - (n + 1) * 20) / n
    for i in range(n):
        r = skia.Rect(x + 20 + i * (fw + 20), y + 50, x + 20 + i * (fw + 20) + fw, y + h - 50)
        cv.drawRect(r, fillp(C('#9a968c')))
        if frame_fn: cv.save(); cv.clipRect(r); frame_fn(cv, r, i); cv.restore()

def saucer(cv, x, y, s=1.0, rot=0, T=0, crashed=False):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    cv.drawOval(skia.Rect(-260, -40, 260, 50), fillp(C('#9aa0aa'))); cv.drawOval(skia.Rect(-260, -40, 260, 50), strokep(INK, 7))
    cv.drawOval(skia.Rect(-120, -120, 120, 10), fillp(C('#bfe8ff'), alpha=0.85)); cv.drawOval(skia.Rect(-120, -120, 120, 10), strokep(INK, 6))
    for i in range(5): cv.drawCircle(-180 + i * 90, 10, 14, fillp(C('#7cf29a') if not crashed or (T * 3 + i) % 2 < 1 else C('#2a3a2a')))
    cv.restore()

# ---- additions for Flight 1282
CHARS.update({
    'pax1': dict(adult=True, shirt=C('#d07a3a'), stripe=None, hair='bob', pants=C('#3a3f5a')),
    'pax2': dict(adult=True, shirt=C('#3a8a6a'), stripe=None, hair='short', pants=C('#3a3a44')),
    'pax3': dict(adult=True, shirt=C('#7a5aa0'), stripe=None, hair='bun', pants=C('#3a3a44')),
    'pax4': dict(adult=True, shirt=C('#c84a4a'), stripe=None, hair='curly', pants=C('#3a3a44')),
    'teen': dict(adult=False, shirt=C('#3a6ab0'), stripe=C('#e8e8e8'), hair='cowlick', pants=C('#3a3a44')),
    'teen_bare': dict(adult=False, shirt=C('#f0d8c0'), stripe=None, hair='cowlick', pants=C('#3a3a44')),
    'cap1': dict(adult=True, shirt=C('#f4f4f0'), stripe=None, tie=C('#1f2a44'), hair='pilotcap', pants=C('#1f2a44')),
    'inv1': dict(adult=True, shirt=C('#2a3a5a'), stripe=C('#f0d020'), hair='bcap', pants=C('#2a2a34')),
    'teach': dict(adult=True, shirt=C('#8a6a4a'), stripe=None, hair='short', glasses=True, pants=C('#3a3a44')),
    'walker': dict(adult=True, shirt=C('#5a7a4a'), stripe=None, hair='beanie', pants=C('#3a3a44')),
})
def jet(cv, x, y, s=1.0, rot=0, hole=0.0, T=0, gear=False, livery=C('#1f3a6a')):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    # far wing
    cv.drawPath(poly([(-40, 20), (80, 20), (-20, -150), (-90, -150)]), fillp(C('#9aa2ae'))); cv.drawPath(poly([(-40, 20), (80, 20), (-20, -150), (-90, -150)]), strokep(INK, 5))
    # tail fin
    fin = poly([(-480, -20), (-380, -20), (-470, -260), (-540, -260)])
    cv.drawPath(fin, fillp(livery)); cv.drawPath(fin, strokep(INK, 6))
    cv.drawPath(poly([(-520, 0), (-400, 0), (-520, 40), (-600, 40)]), fillp(C('#c9ced8'))); cv.drawPath(poly([(-520, 0), (-400, 0), (-520, 40), (-600, 40)]), strokep(INK, 5))
    # fuselage
    f = skia.Path(); f.moveTo(-560, -30); f.lineTo(420, -70); f.quadTo(560, -60, 600, 10); f.quadTo(560, 70, 420, 70); f.lineTo(-500, 60); f.quadTo(-580, 40, -560, -30); f.close()
    cv.drawPath(f, fillp(shader=lin((0, -70), (0, 70), [C('#ffffff'), C('#c9ced8')]))); cv.drawPath(f, strokep(INK, 7))
    cv.drawLine(-540, 30, 560, 25, strokep(livery, 14))
    for i in range(26):
        wx = -420 + i * 32
        if not (hole > 0 and -260 < wx < -200): cv.drawRoundRect(skia.Rect(wx, -35, wx + 14, -15), 6, 6, fillp(C('#2a3a5a')))
    cv.drawPath(poly([(480, -50), (540, -45), (560, -20), (490, -20)]), fillp(C('#2a3a5a')))
    # door plug position (behind wing)
    pr = skia.Rect(-270, -55, -190, 30)
    if hole > 0:
        cv.drawRoundRect(pr, 14, 14, fillp(C('#0a0e18'))); cv.drawRoundRect(pr, 14, 14, strokep(INK, 5))
    else:
        cv.drawRoundRect(pr, 14, 14, strokep(C('#9aa2ae'), 3))
    # near wing + engine
    cv.drawPath(poly([(-60, 30), (140, 30), (-80, 260), (-170, 260)]), fillp(C('#c9ced8'))); cv.drawPath(poly([(-60, 30), (140, 30), (-80, 260), (-170, 260)]), strokep(INK, 6))
    cv.drawRoundRect(skia.Rect(-20, 70, 170, 150), 40, 40, fillp(C('#b8bec8'))); cv.drawRoundRect(skia.Rect(-20, 70, 170, 150), 40, 40, strokep(INK, 6))
    cv.drawOval(skia.Rect(140, 72, 190, 148), fillp(C('#3a3e47')))
    if gear:
        for gx in (60, -330): cv.drawLine(gx, 60, gx, 130, strokep(INK, 8)); cv.drawCircle(gx, 140, 22, fillp(C('#1b1b22')))
    cv.restore()
    a = math.radians(rot)
    hx = x + (-230 * math.cos(a) - (-12) * math.sin(a)) * s; hy = y + (-230 * math.sin(a) + (-12) * math.cos(a)) * s
    return hx, hy

def clouds_bg(cv, T, top=C('#3a5a8a'), bot=C('#e8b890'), speed=500, n=6):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [top, bot])))
    for i in range(n):
        x = ((i * 420 - T * speed) % 2200) - 500; y = 300 + (i * 260) % 1400
        for dx, dy, r in ((0, 0, 90), (80, -30, 110), (170, 0, 90), (90, 30, 80)): cv.drawCircle(x + dx, y + dy, r, fillp(C('#ffffff'), alpha=0.85))

def door_plug(cv, x, y, s=1.0, rot=0, bolts=4, bolt_x=False):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    r = skia.Rect(-150, -260, 150, 260)
    cv.drawRoundRect(r, 40, 40, fillp(shader=lin((-150, 0), (150, 0), [C('#e8ecf0'), C('#a8b0bc')]))); cv.drawRoundRect(r, 40, 40, strokep(INK, 8))
    cv.drawRoundRect(skia.Rect(-50, -110, 50, 20), 24, 24, fillp(C('#2a3a5a'))); cv.drawRoundRect(skia.Rect(-50, -110, 50, 20), 24, 24, strokep(INK, 5))
    for i, (bx, by) in enumerate(((-120, -230), (120, -230), (-120, 230), (120, 230))):
        cv.drawCircle(bx, by, 18, fillp(C('#5a6068') if i < bolts else C('#1a1a1e'))); cv.drawCircle(bx, by, 18, strokep(INK, 4))
        if bolt_x and i >= bolts: cross(cv, bx, by, 34, 1.0)
    cv.restore()

def cabin(cv, T, hole=True, wind=1.0, masks=0.0, pax=True, expr='shock', empty_hl=0.0, teen_shirt=1.0):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#5a6a8a')))
    cv.save(); cv.translate(0, 200)
    cv.drawRect(skia.Rect(-300, -600, W + 300, 260), fillp(C('#e8e4dc'))); cv.drawRect(skia.Rect(-300, 230, W + 300, 270), fillp(C('#b8b4ac')))
    wall = skia.Rect(-300, 270, W + 300, 1150); cv.drawRect(wall, fillp(C('#ece8e0')))
    for i in range(5):
        wx = 40 + i * 230
        if hole and i == 3: continue
        cv.drawRoundRect(skia.Rect(wx, 520, wx + 110, 700), 40, 40, fillp(C('#7ab0e0'))); cv.drawRoundRect(skia.Rect(wx, 520, wx + 110, 700), 40, 40, strokep(INK, 6))
    if hole:
        hr = skia.Rect(700, 380, 960, 1000)
        cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(hr, 50, 50), doAntiAlias=True)
        cv.drawRect(hr, fillp(shader=lin((0, 380), (0, 1000), [C('#2a3a6a'), C('#c88a6a')])))
        for i in range(4):
            yy = 380 + ((T * 900 + i * 180) % 700); cv.drawCircle(830 + math.sin(i) * 60, yy, 70, fillp(C('#ffffff'), alpha=0.8))
        cv.restore()
        cv.drawRoundRect(hr, 50, 50, strokep(INK, 10))
        for i in range(10): cv.drawLine(700 + (i % 2) * 260, 400 + i * 60, 700 + (i % 2) * 260 + (12 if i % 2 == 0 else -12), 420 + i * 60, strokep(C('#5a5e66'), 6))
    if masks > 0:
        for i in range(4):
            mx = 120 + i * 180; drop = 200 * ease(masks)
            cv.drawLine(mx, 260, mx + math.sin(T * 9 + i) * 15 * wind, 260 + drop, strokep(C('#f0f0f0'), 4))
            cv.drawOval(skia.Rect(mx - 30 + math.sin(T * 9 + i) * 15 * wind, 260 + drop, mx + 30 + math.sin(T * 9 + i) * 15 * wind, 320 + drop), fillp(C('#f0c020'))); cv.drawOval(skia.Rect(mx - 30 + math.sin(T * 9 + i) * 15 * wind, 260 + drop, mx + 30 + math.sin(T * 9 + i) * 15 * wind, 320 + drop), strokep(INK, 4))
    # seats + passengers
    names = ['pax1', 'pax2', 'teen', 'pax3', 'pax4']
    for i in range(5):
        sx = 60 + i * 200
        cv.drawRoundRect(skia.Rect(sx - 40, 1000, sx + 120, 1480), 40, 40, fillp(C('#2a3a6a'))); cv.drawRoundRect(skia.Rect(sx - 40, 1000, sx + 120, 1480), 40, 40, strokep(INK, 6))
        cv.drawRoundRect(skia.Rect(sx - 50, 1400, sx + 130, 1480), 20, 20, fillp(C('#3a4a7a'))); cv.drawRoundRect(skia.Rect(sx - 50, 1400, sx + 130, 1480), 20, 20, strokep(INK, 5))
    for i in range(5):
        sx = 60 + i * 200
        near_hole = hole and i == 4
        if pax and not near_hole:
            n = names[i % len(names)]
            if n == 'teen' and teen_shirt < 1: n = 'teen_bare'
            character(cv, n, sx + 40, 1520, 85 if 'teen' not in n else 78, t=T, expr=expr, pose={'sit': True, 'tilt': math.sin(T * 6 + i) * 6 * wind}, look=(1, 0), blink_seed=i)
        if near_hole and empty_hl > 0: cv.drawRoundRect(skia.Rect(sx - 60, 980, sx + 140, 1500), 40, 40, strokep(C('#3fbf6b'), 12, alpha=empty_hl))
    cv.drawRect(skia.Rect(-300, 1480, W + 300, H + 300), fillp(C('#5a6a8a')))
    cv.restore()
    if wind > 0:
        rnd = random.Random(int(T * 10) % 3)
        for i in range(24):
            k = ((T * 2.5 + i / 24) % 1); y0 = 400 + i * 50
            cv.drawLine(-100 + k * 900, y0, -100 + k * 900 + 160, y0 - 10, strokep(C('#ffffff'), 5, alpha=0.6 * wind * (1 - k)))

# ---- additions for Virginia Hall
_hair_old23 = hair
def hair(cv, x, y, u, kind, back=False):
    if kind == 'vhair':
        col = C('#6a4a32')
        if back:
            cv.drawOval(skia.Rect(x - u * 1.15, y - u * 1.1, x + u * 1.15, y + u * 0.75), fillp(col)); cv.drawOval(skia.Rect(x - u * 1.15, y - u * 1.1, x + u * 1.15, y + u * 0.75), strokep(INK, u * 0.07))
            return
        p = skia.Path(); p.moveTo(x - u * 1.0, y - u * 0.1); p.quadTo(x - u * 1.0, y - u * 1.15, x, y - u * 1.08); p.quadTo(x + u * 1.0, y - u * 1.15, x + u * 1.02, y - u * 0.15)
        p.quadTo(x + u * 0.5, y - u * 0.75, x - u * 0.2, y - u * 0.55); p.quadTo(x - u * 0.7, y - u * 0.5, x - u * 1.0, y - u * 0.1); p.close()
        cv.drawPath(p, fillp(col)); cv.drawPath(p, strokep(INK, u * 0.07))
        return
    if kind == 'scarf':
        col = C('#7a6a5a')
        if back:
            cv.drawOval(skia.Rect(x - u * 1.25, y - u * 1.2, x + u * 1.25, y + u * 1.1), fillp(col)); cv.drawOval(skia.Rect(x - u * 1.25, y - u * 1.2, x + u * 1.25, y + u * 1.1), strokep(INK, u * 0.07))
            return
        cv.drawPath(poly([(x - u * 1.05, y - u * 0.2), (x - u * 0.9, y - u * 1.0), (x, y - u * 1.2), (x + u * 0.9, y - u * 1.0), (x + u * 1.05, y - u * 0.2), (x + u * 0.6, y - u * 0.75), (x - u * 0.6, y - u * 0.75)]), fillp(col))
        cv.drawLine(x - u * 0.6, y - u * 0.72, x + u * 0.6, y - u * 0.72, strokep(C('#c8c0b0'), u * 0.12))
        cv.drawPath(poly([(x - u * 0.62, y - u * 0.75), (x + u * 0.62, y - u * 0.75), (x + u * 0.55, y - u * 0.55), (x - u * 0.55, y - u * 0.55)]), fillp(C('#d8d4cc')))
        return
    if kind == 'beret':
        if back: return
        cv.drawOval(skia.Rect(x - u * 1.0, y - u * 1.3, x + u * 0.9, y - u * 0.55), fillp(C('#2a2a30'))); cv.drawOval(skia.Rect(x - u * 1.0, y - u * 1.3, x + u * 0.9, y - u * 0.55), strokep(INK, u * 0.07))
        cv.drawLine(x, y - u * 1.3, x + u * 0.1, y - u * 1.45, strokep(INK, u * 0.08))
        return
    return _hair_old23(cv, x, y, u, kind, back)

CHARS.update({
    'vh':      dict(adult=True, shirt=C('#3a5a7a'), stripe=None, hair='vhair', pants=C('#2a3040')),
    'vh_coat': dict(adult=True, shirt=C('#8a6a4a'), coat=True, tie=None, inner=C('#d8c8b0'), hair='vhair', pants=C('#3a3028')),
    'vh_old':  dict(adult=True, shirt=C('#6a6a58'), stripe=C('#8a8470'), hair='scarf', pants=C('#4a4a3a')),
    'gest':    dict(adult=True, shirt=C('#2a2c30'), coat=True, tie=C('#1a1a1e'), inner=C('#4a4c50'), hair='peaked_dark', pants=C('#2a2c30')),
    'soe':     dict(adult=True, shirt=C('#3a3a44'), stripe=None, tie=C('#7a2a2a'), hair='slick', pants=C('#2a2a34')),
    'fighter1':dict(adult=True, shirt=C('#5a6a3a'), stripe=None, hair='beret', pants=C('#3a3a2a')),
    'fighter2':dict(adult=True, shirt=C('#7a5a3a'), stripe=None, hair='flatcap', pants=C('#3a3a2a')),
    'guide':   dict(adult=True, shirt=C('#4a3a2a'), stripe=None, hair='beret', pants=C('#3a3a2a')),
    'doctor':  dict(adult=True, shirt=C('#f5f5f2'), coat=True, tie=None, inner=C('#5a7aa0'), hair='bald_grey', glasses=True, pants=C('#3a3f55')),
    'official':dict(adult=True, shirt=C('#2a2a34'), stripe=None, tie=C('#3a5a8a'), hair='bald_grey', glasses=True, pants=C('#2a2a34')),
})

def cuthbert(cv, x, y, s=1.0, rot=0, tag_=False, bow=False):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-70, -420, 70, -300), 40, 40, fillp(C('#c8a070'))); cv.drawRoundRect(skia.Rect(-70, -420, 70, -300), 40, 40, strokep(INK, 6))
    for sx in (-1, 1): cv.drawLine(sx * 60, -400, sx * 80, -480, strokep(C('#6a4a2a'), 10))
    cv.drawLine(-90, -480, 90, -480, strokep(C('#6a4a2a'), 10))
    shin = poly([(-55, -300), (55, -300), (40, -40), (-40, -40)])
    cv.drawPath(shin, fillp(shader=lin((-55, 0), (55, 0), [C('#d8b080'), C('#a07a48')]))); cv.drawPath(shin, strokep(INK, 6))
    for yy in (-250, -170, -100): cv.drawLine(-48, yy, 48, yy + 6, strokep(C('#8a6a3a'), 3))
    cv.drawRect(skia.Rect(-30, -60, 30, -30), fillp(C('#9aa0aa'))); cv.drawRect(skia.Rect(-30, -60, 30, -30), strokep(INK, 4))
    shoe = skia.Path(); shoe.moveTo(-50, -30); shoe.lineTo(40, -30); shoe.quadTo(150, -20, 150, 20); shoe.lineTo(-60, 20); shoe.close()
    cv.drawPath(shoe, fillp(C('#3a2a20'))); cv.drawPath(shoe, strokep(INK, 6))
    if bow:
        cv.drawPath(poly([(-60, -330), (0, -305), (-60, -280)]), fillp(C('#c83a3a'))); cv.drawPath(poly([(60, -330), (0, -305), (60, -280)]), fillp(C('#c83a3a'))); cv.drawCircle(0, -305, 14, fillp(C('#a02a2a')))
    cv.restore()
    if tag_:
        cv.save(); cv.translate(x + 120 * s, y - 220 * s); cv.rotate(-8)
        cv.drawRoundRect(skia.Rect(0, -40, 260, 40), 14, 14, fillp(C('#f6f0dc'))); cv.drawRoundRect(skia.Rect(0, -40, 260, 40), 14, 14, strokep(INK, 5))
        cv.drawLine(-60 * s, 0, 0, 0, strokep(INK, 3)); text(cv, 'CUTHBERT', 130, 14, 38, INK); cv.restore()

def lyon_street(cv, T, night=True):
    if night: night_sky(cv, C('#070b1e'), C('#1c2442'), h=900, moon=(820, 220))
    else: day_sky(cv, C('#9ab0c0'), C('#e8e0d0'), h=900, sun=None)
    for i, (x, w, h, col) in enumerate(((-40, 260, 760, C('#4a4250')), (220, 240, 840, C('#3e3a48')), (460, 260, 720, C('#4a4458')), (720, 400, 800, C('#3a3644')))):
        cv.drawRect(skia.Rect(x, 1450 - h, x + w, 1450), fillp(col if night else shade(col, 1.9))); cv.drawRect(skia.Rect(x, 1450 - h, x + w, 1450), strokep(INK, 5))
        cv.drawPath(poly([(x - 10, 1450 - h), (x + w + 10, 1450 - h), (x + w - 20, 1450 - h - 50), (x + 20, 1450 - h - 50)]), fillp(C('#2a2630')))
        rnd = random.Random(i)
        for wy in range(int(1450 - h + 60), 1350, 130):
            for wx in range(x + 30, x + w - 50, 90):
                lit = night and rnd.random() < 0.35
                cv.drawRect(skia.Rect(wx, wy, wx + 46, wy + 76), fillp(C('#ffd27a') if lit else C('#1a2030'))); cv.drawRect(skia.Rect(wx, wy, wx + 46, wy + 76), strokep(INK, 3))
                cv.drawRect(skia.Rect(wx - 6, wy + 76, wx + 52, wy + 84), fillp(C('#5a5468')))
    cv.drawRect(skia.Rect(-300, 1450, W + 300, H + 300), fillp(shader=lin((0, 1450), (0, H), [C('#3a3a44'), C('#1a1a20')])))
    for r in range(8):
        for c in range(-1, 14):
            x = c * 90 + (r % 2) * 45; y = 1470 + r * 60
            cv.drawRoundRect(skia.Rect(x, y, x + 80, y + 50), 14, 14, strokep(C('#4a4a56'), 3))
    lx = 140; cv.drawLine(lx, 1450, lx, 1000, strokep(C('#1a1a1e'), 14)); cv.drawCircle(lx, 990, 34, fillp(C('#ffe0a0')))
    if night: cv.drawPath(poly([(lx - 30, 1000), (lx + 30, 1000), (lx + 220, 1700), (lx - 220, 1700)]), fillp(C('#ffe0a0'), alpha=0.12))

def wanted_poster(cv, x, y, s=1.0, rot=0, k=1.0):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s * k, s * k)
    cv.drawRect(skia.Rect(-200, -280, 200, 280), fillp(C('#efe2c0'))); cv.drawRect(skia.Rect(-200, -280, 200, 280), strokep(INK, 6))
    text(cv, 'WANTED', 0, -190, 72, C('#8a1a1a'))
    cv.drawRect(skia.Rect(-130, -150, 130, 110), fillp(C('#c8b890'))); cv.drawRect(skia.Rect(-130, -150, 130, 110), strokep(INK, 4))
    cv.save(); cv.clipRect(skia.Rect(-130, -150, 130, 110))
    def f(): character(cv, 'vh_coat', 0, 330, 90, t=0, expr='neutral')
    silhouette(cv, f); cv.restore()
    text(cv, '?', 0, 40, 130, C('#efe2c0'))
    text(cv, 'LA DAME QUI BOITE', 0, 175, 30, INK); text(cv, '"THE LIMPING LADY"', 0, 230, 28, C('#8a1a1a'))
    cv.restore()

def radio_set(cv, x, y, s=1.0, T=0, on=True):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-220, -150, 220, 150), 20, 20, fillp(C('#5a4a32'))); cv.drawRoundRect(skia.Rect(-220, -150, 220, 150), 20, 20, strokep(INK, 7))
    cv.drawRoundRect(skia.Rect(-190, -120, 190, 120), 14, 14, fillp(C('#3a3e34')))
    for i, dx in enumerate((-120, -40, 40, 120)):
        cv.drawCircle(dx, -40, 30, fillp(C('#2a2a26'))); cv.drawCircle(dx, -40, 30, strokep(C('#9a9a8a'), 4))
        a = T * 2 + i; cv.drawLine(dx, -40, dx + math.cos(a) * 22, -40 + math.sin(a) * 22, strokep(C('#e8e0c8'), 4))
    cv.drawRoundRect(skia.Rect(-150, 40, 150, 90), 10, 10, fillp(C('#ffb040') if on else C('#3a3020')))
    cv.drawLine(160, -150, 260, -380, strokep(INK, 6))
    cv.restore()
    if on:
        for kk in range(3):
            r = ((T * 1.2 + kk / 3) % 1); cv.drawArc(skia.Rect(x + 260 * s - 60 - r * 200, y - 380 * s - 60 - r * 200, x + 260 * s + 60 + r * 200, y - 380 * s + 60 + r * 200), 220, 100, False, strokep(C('#7cf29a'), 6, alpha=1 - r))

def telegram(cv, x, y, msg, T, t0, dur=1.8, w=860, h=520, rot=-2, head='MESSAGE'):
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    soft_shadow(cv, 10, h / 2, w * 0.5, 22, 0.35)
    cv.drawRect(skia.Rect(-w / 2, -h / 2, w / 2, h / 2), fillp(C('#f0e6c8'))); cv.drawRect(skia.Rect(-w / 2, -h / 2, w / 2, h / 2), strokep(INK, 6))
    cv.drawRect(skia.Rect(-w / 2, -h / 2, w / 2, -h / 2 + 90), fillp(C('#5a4a32'))); text(cv, head, 0, -h / 2 + 62, 48, C('#f4efe2'))
    n = int(len(msg) * clamp((T - t0) / dur))
    f = skia.Font(skia.Typeface('Courier New', skia.FontStyle.Bold()), 56)
    for i, ln in enumerate(msg[:n].split('\n')): cv.drawString(ln, -w / 2 + 50, -h / 2 + 180 + i * 80, f, fillp(INK))
    cv.restore()

def dsc_medal(cv, x, y, s=1.0, T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    rib = poly([(-90, -360), (90, -360), (90, -140), (-90, -140)])
    cv.drawPath(rib, fillp(C('#2a4a9a')))
    cv.drawRect(skia.Rect(-60, -360, 60, -140), fillp(C('#f4f4f0'))); cv.drawRect(skia.Rect(-25, -360, 25, -140), fillp(C('#b8282a')))
    cv.drawPath(rib, strokep(INK, 6))
    cross_ = poly([(-40, -150), (40, -150), (40, -60), (130, -60), (130, 20), (40, 20), (40, 170), (-40, 170), (-40, 20), (-130, 20), (-130, -60), (-40, -60)])
    cv.drawPath(cross_, fillp(shader=lin((-130, -150), (130, 170), [C('#f8d880'), C('#b88a20')]))); cv.drawPath(cross_, strokep(INK, 7))
    cv.drawCircle(0, -20, 50, fillp(C('#e8c060'))); cv.drawCircle(0, -20, 50, strokep(INK, 5))
    cv.restore()
    sparkle(cv, x + 110 * s, y - 120 * s, 40 * s, a=0.6 + 0.4 * math.sin(T * 5))

def mountains_snow(cv, T, dark=0.0):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, 1300), [mix(C('#6a7a9a'), C('#1a2238'), dark), mix(C('#d8e0ec'), C('#5a6680'), dark)])))
    for i, (x, h, col) in enumerate(((150, 900, C('#8a96b0')), (600, 1100, C('#7a88a4')), (1000, 850, C('#8a96b0')))):
        p = poly([(x - 600, 1500), (x, 1500 - h), (x + 600, 1500)]); cv.drawPath(p, fillp(mix(col, C('#2a3048'), dark))); cv.drawPath(p, strokep(INK, 6))
        cv.drawPath(poly([(x - 170, 1500 - h * 0.72), (x, 1500 - h), (x + 170, 1500 - h * 0.72), (x + 60, 1500 - h * 0.66), (x - 40, 1500 - h * 0.74)]), fillp(C('#f4f8fc')))
    cv.drawPath(poly([(-300, 1450), (500, 1250), (1380, 1420), (1380, H + 300), (-300, H + 300)]), fillp(C('#eef2f8'))); cv.drawPath(poly([(-300, 1450), (500, 1250), (1380, 1420), (1380, H + 300), (-300, H + 300)]), strokep(C('#9aa8c0'), 5))

# ---- additions for Kara Robinson
CHARS.update({
    'kara':  dict(adult=True, shirt=C('#4aa08a'), stripe=None, hair='pony', pants=C('#3a4a6a')),
    'evo':   dict(adult=True, shirt=C('#3a3a40'), stripe=None, hair='short_black', pants=C('#2a2a30')),
    'inv':   dict(adult=True, shirt=C('#2a3a5a'), coat=True, tie=C('#5a2a2a'), inner=C('#d8d8d0'), hair='short', pants=C('#2a2a34')),
    'inv2':  dict(adult=True, shirt=C('#4a4a50'), coat=True, tie=None, inner=C('#c8c8c0'), hair='bun', pants=C('#2a2a34')),
    'driver':dict(adult=True, shirt=C('#c86a3a'), stripe=None, hair='cap', pants=C('#3a3a4a')),
})

def apartment(cv, T, dark=0.0, bed=True, tv=True, lamp_on=True, door_open=0.0, empty=False):
    wall = mix(C('#8a7a6a'), C('#1a1c2a'), dark); flo = mix(C('#7a5a40'), C('#141018'), dark)
    cv.drawRect(skia.Rect(-300, -300, W + 300, 1450), fillp(shader=lin((0, 0), (0, 1450), [shade(wall, 1.1), shade(wall, 0.85)])))
    for i in range(-3, 16): cv.drawLine(i * 80, -300, i * 80, 1450, strokep(shade(wall, 0.92), 3))
    cv.drawRect(skia.Rect(-300, 1450, W + 300, H + 300), fillp(flo))
    for i in range(-4, 16): cv.drawLine(i * 110, 1450, i * 110 - 260, H + 60, strokep(shade(flo, 0.8), 4))
    cv.drawRect(skia.Rect(-300, 1430, W + 300, 1460), fillp(shade(wall, 0.6)))
    # window with blinds
    cv.drawRect(skia.Rect(600, 330, 960, 760), fillp(mix(C('#9ac8e8'), C('#0a1430'), dark))); cv.drawRect(skia.Rect(600, 330, 960, 760), strokep(INK, 8))
    for j in range(9): cv.drawRect(skia.Rect(600, 340 + j * 46, 960, 360 + j * 46), fillp(mix(C('#e8e0d0'), C('#3a3a48'), dark)))
    # door
    door(cv, 90, 760, 300, 690, openf=door_open, col=mix(C('#6a5040'), C('#2a2028'), dark))
    if tv:
        cv.drawRect(skia.Rect(640, 1160, 960, 1450), fillp(mix(C('#5a4030'), C('#1a1418'), dark))); cv.drawRect(skia.Rect(640, 1160, 960, 1450), strokep(INK, 6))
        cv.drawRoundRect(skia.Rect(660, 960, 940, 1160), 20, 20, fillp(C('#2a2a30'))); cv.drawRoundRect(skia.Rect(680, 980, 920, 1140), 14, 14, fillp(mix(C('#3a4a5a'), C('#5a7aa0'), 0.5 + 0.5 * math.sin(T * 7)) if not empty else C('#1a1a20')))
    if bed:
        cv.drawRoundRect(skia.Rect(-60, 1480, 520, 1640), 30, 30, fillp(mix(C('#5a6a9a'), C('#1a2030'), dark))); cv.drawRoundRect(skia.Rect(-60, 1480, 520, 1640), 30, 30, strokep(INK, 6))
        cv.drawRoundRect(skia.Rect(-60, 1400, 30, 1700), 16, 16, fillp(mix(C('#5a4030'), C('#1a1418'), dark)))
        cv.drawRoundRect(skia.Rect(0, 1440, 160, 1510), 30, 30, fillp(mix(C('#e8e8f0'), C('#3a3a48'), dark)))
    # lamp
    cv.drawLine(500, 1450, 500, 1060, strokep(C('#2a2a2a'), 10))
    cv.drawPath(poly([(440, 1060), (560, 1060), (530, 980), (470, 980)]), fillp(C('#e8d8a8') if lamp_on else C('#4a4a40'))); cv.drawPath(poly([(440, 1060), (560, 1060), (530, 980), (470, 980)]), strokep(INK, 5))
    if lamp_on: cv.drawCircle(500, 1080, 360, fillp(C('#ffe0a0'), alpha=0.16 * (1 - dark * 0.5), blur=90))
    if dark > 0: cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#05060e'), alpha=dark * 0.35))

def tub(cv, x, y, s=1.0, lid=1.0, col=C('#9ab0c4')):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    body = poly([(-230, -200), (230, -200), (200, 60), (-200, 60)])
    cv.drawPath(body, fillp(col, alpha=0.95)); cv.drawPath(body, strokep(INK, 7))
    for i in range(3): cv.drawLine(-190 + i * 4, -140 + i * 60, 190 - i * 4, -140 + i * 60, strokep(shade(col, 0.85), 5))
    ly = lerp(-420, -200, lid)
    cv.save(); cv.rotate(lerp(-20, 0, lid), -240, ly)
    cv.drawRoundRect(skia.Rect(-250, ly - 36, 250, ly + 6), 14, 14, fillp(shade(col, 0.8))); cv.drawRoundRect(skia.Rect(-250, ly - 36, 250, ly + 6), 14, 14, strokep(INK, 6))
    cv.restore(); cv.restore()

def handcuff(cv, x, y, s=1.0, open_=0.0, T=0, rot=0):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    met = C('#b8bcc8')
    for cx in (-140, 140):
        cv.drawCircle(cx, 0, 90, strokep(INK, 34)); cv.drawCircle(cx, 0, 90, strokep(met, 22))
    cv.save(); cv.translate(140, 0); cv.rotate(-60 * open_)
    cv.drawArc(skia.Rect(-90, -90, 90, 90), 200, 120, False, strokep(C('#2a2a30'), 36)); cv.drawArc(skia.Rect(-90, -90, 90, 90), 200, 120, False, strokep(C('#d8dce8'), 22)); cv.restore()
    for i in range(3): cv.drawCircle(-40 + i * 40, 0, 16, strokep(met, 8))
    cv.restore()

def fingerprint(cv, x, y, s=1.0, k=1.0, col=C('#3a3a48'), a=0.75, rot=0):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s * k, s * k)
    for i in range(7):
        r = 14 + i * 13
        cv.drawArc(skia.Rect(-r * 0.75, -r, r * 0.75, r), 200 + i * 7, 280 - i * 18, False, strokep(col, 5, alpha=a))
    cv.restore()

def watering_can(cv, x, y, s=1.0, tilt=0, T=0, flow=True):
    cv.save(); cv.translate(x, y); cv.rotate(tilt); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-80, -90, 80, 60), 20, 20, fillp(C('#3a9a6a'))); cv.drawRoundRect(skia.Rect(-80, -90, 80, 60), 20, 20, strokep(INK, 6))
    cv.drawLine(70, 20, 170, -60, strokep(INK, 22)); cv.drawLine(70, 20, 170, -60, strokep(C('#3a9a6a'), 12))
    cv.drawArc(skia.Rect(-110, -120, -10, 20), 90, 180, False, strokep(INK, 10))
    cv.restore()
    if flow:
        ang = math.radians(tilt)
        sx = x + (170 * math.cos(ang) + 60 * math.sin(ang)) * s; sy = y + (170 * math.sin(ang) - 60 * math.cos(ang)) * s
        for i in range(10):
            f = ((T * 2.5 + i / 10) % 1)
            cv.drawCircle(sx + f * 70 + (i % 3) * 8, sy + f * f * 380, 7, fillp(C('#7ad7ff'), alpha=1 - f * 0.6))

def flowers(cv, x0, x1, y, T=0, seed=3):
    rnd = random.Random(seed)
    for i in range(int((x1 - x0) / 55)):
        x = x0 + i * 55 + rnd.uniform(-10, 10); h = rnd.uniform(60, 120); sw = math.sin(T * 2 + i) * 4
        cv.drawLine(x, y, x + sw, y - h, strokep(C('#2a7a3a'), 6))
        col = rnd.choice([C('#ff6a8a'), C('#ffd14a'), C('#c86aff'), C('#ff8a3a')])
        for a in range(5): cv.drawCircle(x + sw + math.cos(a * 1.256) * 16, y - h + math.sin(a * 1.256) * 16, 12, fillp(col))
        cv.drawCircle(x + sw, y - h, 9, fillp(C('#fff2a0')))

def magazines(cv, x, y, s=1.0, rot=0):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    for i, col in enumerate((C('#e2483b'), C('#3a7ad8'), C('#f0c040'))):
        cv.save(); cv.rotate((i - 1) * 6)
        cv.drawRect(skia.Rect(-70, -95 - i * 10, 70, 95 - i * 10), fillp(col)); cv.drawRect(skia.Rect(-70, -95 - i * 10, 70, 95 - i * 10), strokep(INK, 5))
        cv.drawRect(skia.Rect(-55, -80 - i * 10, 55, -50 - i * 10), fillp(C('#ffffff')))
        cv.restore()
    cv.restore()

def apt_building(cv, x, y, s=1.0, lit=None, T=0, night=True):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    soft_shadow(cv, 0, 0, 460, 30, 0.4)
    cv.drawRect(skia.Rect(-420, -760, 420, 0), fillp(shader=lin((-420, 0), (420, 0), [C('#8a7a70') if not night else C('#4a4250'), C('#6a5a54') if not night else C('#2e2a36')])))
    cv.drawRect(skia.Rect(-420, -760, 420, 0), strokep(INK, 8))
    k = 0
    for r in range(3):
        for c in range(4):
            wx = -350 + c * 180; wy = -700 + r * 230
            on = lit[k] if lit else ((k * 7) % 3 == 0)
            cv.drawRect(skia.Rect(wx, wy, wx + 110, wy + 140), fillp(C('#ffd27a') if on and night else (C('#9ac8e8') if not night else C('#1a1e2e')))); cv.drawRect(skia.Rect(wx, wy, wx + 110, wy + 140), strokep(INK, 5)); k += 1
    for r in range(3): cv.drawLine(-430, -480 + r * 230, 430, -480 + r * 230, strokep(C('#2a2a30'), 10))
    cv.drawRect(skia.Rect(-60, -170, 60, 0), fillp(C('#3a2a22'))); cv.drawRect(skia.Rect(-60, -170, 60, 0), strokep(INK, 6))
    cv.restore()

def us_map(cv, T, land=C('#d8c49a'), sea=C('#2e5670')):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(sea))
    for i in range(-300, W + 300, 60): cv.drawLine(i, -300, i, H + 300, strokep(shade(sea, 1.12), 2))
    for j in range(-300, H + 300, 60): cv.drawLine(-300, j, W + 300, j, strokep(shade(sea, 1.12), 2))
    coast = [(-300, -300), (900, -300), (880, 200), (820, 420), (760, 560), (720, 700), (640, 860), (560, 980), (520, 1100), (560, 1300), (640, 1520), (660, 1700), (600, 1780), (520, 1650), (430, 1420), (360, 1330), (200, 1330), (-300, 1350)]
    cv.drawPath(poly(coast), fillp(land)); cv.drawPath(poly(coast), strokep(INK, 6))
    states = {'VA': [(260, 320), (780, 330), (820, 460), (740, 520), (260, 520)], 'SC': [(420, 860), (620, 840), (600, 960), (520, 1060), (420, 960)], 'FL': [(300, 1300), (520, 1290), (580, 1420), (650, 1690), (590, 1760), (500, 1600), (430, 1400), (300, 1360)]}
    pos = {}
    for k, pts in states.items():
        cv.drawPath(poly(pts), fillp(shade(land, 0.88))); cv.drawPath(poly(pts), strokep(INK, 4))
        cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts); pos[k] = (cx, cy)
    for k, n in (('VA', 'VIRGINIA'), ('SC', 'S. CAROLINA'), ('FL', 'FLORIDA')): text(cv, n, pos[k][0], pos[k][1] + 14, 38, shade(INK, 1.7))
    return pos

def map_pin(cv, x, y, k=1.0, col=C('#e2483b')):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.scale(k, k)
    cv.drawPath(poly([(0, 0), (-30, -60), (30, -60)]), fillp(col)); cv.drawCircle(0, -80, 36, fillp(col)); cv.drawCircle(0, -80, 36, strokep(INK, 5)); cv.drawCircle(0, -80, 12, fillp(C('#f4efe2'))); cv.restore()

def case_file(cv, x, y, s=1.0, rot=0, label='CASE FILE', k=1.0, frost=0.0):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s * k, s * k)
    soft_shadow(cv, 10, 230, 260, 20, 0.3)
    cv.drawRect(skia.Rect(-110, -260, 60, -220), fillp(C('#c8a868'))); cv.drawRect(skia.Rect(-110, -260, 60, -220), strokep(INK, 5))
    cv.drawRect(skia.Rect(-240, -230, 240, 230), fillp(C('#d8b878'))); cv.drawRect(skia.Rect(-240, -230, 240, 230), strokep(INK, 6))
    text(cv, label, 0, -150, 44, INK)
    for i in range(4): cv.drawLine(-180, -60 + i * 60, 180 - i * 30, -60 + i * 60, strokep(C('#8a6a3a'), 6))
    if frost > 0:
        cv.drawRect(skia.Rect(-240, -230, 240, 230), fillp(C('#cfe8ff'), alpha=0.45 * frost))
        rnd = random.Random(2)
        for i in range(12): snowflake(cv, rnd.uniform(-220, 220), rnd.uniform(-210, 210), rnd.uniform(14, 30) * frost, col=C('#ffffff'))
    cv.restore()

def road_night(cv, T, speed=1.0, y=1250):
    night_sky(cv, C('#04060e'), C('#1a2238'), h=y, moon=(820, 260))
    for i in range(10):
        x = ((i * 170 - T * 300 * speed * 0.3) % 1700) - 200
        cv.drawPath(poly([(x - 60, y), (x, y - 200 - (i % 3) * 60), (x + 60, y)]), fillp(C('#0e1a14')))
    cv.drawRect(skia.Rect(-300, y, W + 300, H + 300), fillp(C('#1e2026')))
    for i in range(12):
        x = ((i * 200 - T * 900 * speed) % 2400) - 300
        cv.drawRect(skia.Rect(x, y + 210, x + 110, y + 228), fillp(C('#e8d870')))

def siren_glow(cv, T, x=540, y=900, a=0.35):
    r = math.sin(T * 12) > 0
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#ff2a3a') if r else C('#2a5aff'), alpha=a * 0.35))

# ---- additions for James Howells
CHARS.update({
    'james': dict(adult=True, shirt=C('#3a4a6a'), stripe=None, hair='short_black', glasses=True, pants=C('#2a2f3d')),
    'gf':    dict(adult=True, shirt=C('#c86a8a'), stripe=None, hair='long', pants=C('#3a3a4a')),
    'clerk': dict(adult=True, shirt=C('#2a2a34'), stripe=None, tie=C('#8a2a2a'), hair='bald_grey', glasses=True, pants=C('#2a2a34')),
    'judge': dict(adult=True, shirt=C('#1a1a20'), stripe=None, hair='bald_grey', pants=C('#1a1a20')),
})
BTC_GOLD = C('#f2a93b')
def coin(cv, x, y, r=60, rot=0, spin=0.0, a=1.0):
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(max(0.15, abs(math.cos(spin))), 1)
    p = fillp(shader=lin((-r, -r), (r, r), [C('#ffd27a'), C('#d88a1a')])); 
    if a < 1: p.setAlphaf(a)
    cv.drawCircle(0, 0, r, p); cv.drawCircle(0, 0, r, strokep(INK, max(3, r * 0.08), alpha=a))
    cv.drawCircle(0, 0, r * 0.78, strokep(C('#fff0b0'), max(2, r * 0.05), alpha=a))
    f = skia.Font(skia.Typeface('Poppins', skia.FontStyle.Bold()), r * 1.15)
    tw = f.measureText('B'); cv.drawString('B', -tw / 2, r * 0.4, f, fillp(C('#ffffff'), alpha=a))
    for dx in (-0.12, 0.12): cv.drawLine(dx * r, -r * 0.62, dx * r, -r * 0.42, strokep(C('#ffffff'), r * 0.09, alpha=a)); cv.drawLine(dx * r, r * 0.42, dx * r, r * 0.62, strokep(C('#ffffff'), r * 0.09, alpha=a))
    cv.restore()

def hdd(cv, x, y, s=1.0, rot=0, glow=0.0, T=0):
    if glow > 0: cv.drawCircle(x, y, 260 * s, fillp(BTC_GOLD, alpha=0.45 * glow, blur=80 * s))
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-160, -110, 160, 110), 22, 22, fillp(shader=lin((0, -110), (0, 110), [C('#4a4e58'), C('#22252c')]))); cv.drawRoundRect(skia.Rect(-160, -110, 160, 110), 22, 22, strokep(INK, 8))
    cv.drawRoundRect(skia.Rect(-130, -80, 130, 80), 14, 14, fillp(C('#c8ccd4'))); cv.drawRoundRect(skia.Rect(-130, -80, 130, 80), 14, 14, strokep(INK, 4))
    cv.drawRect(skia.Rect(-110, -60, 40, -20), fillp(C('#ffffff'))); cv.drawLine(-100, -40, 20, -40, strokep(C('#8a8e98'), 4))
    cv.drawCircle(80, 20, 30, fillp(C('#8a8e98'))); cv.drawCircle(80, 20, 30, strokep(INK, 4))
    for i in range(5): cv.drawRect(skia.Rect(-120 + i * 26, 92, -104 + i * 26, 108), fillp(C('#d8b040')))
    cv.restore()

def laptop(cv, x, y, s=1.0, openf=1.0, screen_fn=None, T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawPath(poly([(-300, 0), (300, 0), (340, 40), (-340, 40)]), fillp(C('#9aa0aa'))); cv.drawPath(poly([(-300, 0), (300, 0), (340, 40), (-340, 40)]), strokep(INK, 6))
    h = 380 * openf
    if openf > 0.02:
        cv.drawRoundRect(skia.Rect(-280, -h, 280, 0), 16, 16, fillp(C('#3a3e46'))); cv.drawRoundRect(skia.Rect(-280, -h, 280, 0), 16, 16, strokep(INK, 6))
        if openf > 0.9:
            scr = skia.Rect(-250, -h + 26, 250, -26)
            cv.drawRect(scr, fillp(C('#0a1a14')))
            if screen_fn: cv.save(); cv.clipRect(scr); screen_fn(cv, scr); cv.restore()
    cv.restore()

def junk_bag(cv, x, y, s=1.0, T=0, tied=True):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    p = skia.Path(); p.moveTo(-150, 0); p.quadTo(-220, -200, -90, -300); p.lineTo(90, -300); p.quadTo(220, -200, 150, 0); p.close()
    cv.drawPath(p, fillp(shader=lin((-200, 0), (200, 0), [C('#3a3a40'), C('#141418')]))); cv.drawPath(p, strokep(INK, 7))
    for i in range(3): cv.drawLine(-100 + i * 80, -250, -120 + i * 90, -40, strokep(C('#4a4a52'), 5))
    if tied:
        cv.drawPath(poly([(-60, -300), (0, -360), (60, -300)]), fillp(C('#222226'))); cv.drawPath(poly([(-60, -300), (-10, -380), (-40, -400)]), fillp(C('#222226')))
    cv.restore()

def landfill(cv, T, night=False, closed=0.0, x0=0):
    if night: night_sky(cv, C('#04060e'), C('#1a2238'), h=1100, moon=(840, 260))
    else: day_sky(cv, C('#8aa8c0'), C('#e8e4d8'), h=1100, sun=None)
    rnd = random.Random(4)
    hill = [(-300, 1400), (-100, 900), (200, 760), (520, 700), (820, 780), (1100, 900), (1380, 1300), (1380, H + 300), (-300, H + 300)]
    cv.drawPath(poly(hill), fillp(mix(C('#7a6a5a'), C('#5a8a4a'), closed))); cv.drawPath(poly(hill), strokep(INK, 7))
    if closed < 1:
        for i in range(140):
            x = rnd.uniform(-100, 1180); y = rnd.uniform(760, 1500)
            col = rnd.choice([C('#3a3a40'), C('#8a5a3a'), C('#5a7aa0'), C('#c8b080'), C('#6a6a6a'), C('#a04a3a')])
            w = rnd.uniform(20, 60)
            cv.save(); cv.translate(x, y); cv.rotate(rnd.uniform(-40, 40)); cv.drawRect(skia.Rect(-w / 2, -w / 3, w / 2, w / 3), fillp(col, alpha=1 - closed)); cv.restore()
    for i in range(5):
        bx = ((i * 260 + T * 30) % 1500) - 200; by = 300 + math.sin(T * 2 + i) * 40 + (i % 2) * 80
        if closed < 0.5:
            cv.drawPath(poly([(bx - 26, by), (bx, by + 8), (bx + 26, by)], close=False), strokep(INK, 5))

def section(cv, T, depth_glow=1.0, cover=0.0, dark=0.0, drive_xy=(560, 1420), scan=0.0):
    sky = mix(C('#8aa8c0'), C('#06080e'), dark)
    cv.drawRect(skia.Rect(-300, -300, W + 300, 640), fillp(sky))
    layers = [C('#7a6a5a'), C('#6a5a4c'), C('#5a4a40'), C('#4a3c34'), C('#3a2e28'), C('#2a2020')]
    for i, col in enumerate(layers):
        y0 = 620 + i * 230
        cv.drawRect(skia.Rect(-300, y0, W + 300, y0 + 240), fillp(mix(col, C('#0a0808'), dark * 0.6)))
        cv.drawLine(-300, y0, W + 300, y0 + 10 * math.sin(i), strokep(shade(col, 0.7), 5))
        rnd = random.Random(i)
        for j in range(30):
            x = rnd.uniform(-100, 1180); y = rnd.uniform(y0 + 20, y0 + 220); w = rnd.uniform(18, 50)
            cv.save(); cv.translate(x, y); cv.rotate(rnd.uniform(-50, 50)); cv.drawRect(skia.Rect(-w / 2, -w / 4, w / 2, w / 4), fillp(shade(col, rnd.uniform(0.6, 1.4)))); cv.restore()
    if cover > 0:
        cv.drawRect(skia.Rect(-300, 560, W + 300, 560 + 90 * cover), fillp(C('#5a8a4a'))); cv.drawLine(-300, 560 + 90 * cover, W + 300, 560 + 90 * cover, strokep(INK, 5))
        for i in range(30): cv.drawLine(i * 40 - 20, 560, i * 40 - 10, 530, strokep(C('#3a7a3a'), 5, alpha=cover))
    hdd(cv, drive_xy[0], drive_xy[1], 0.45, rot=-20, glow=depth_glow * (0.75 + 0.25 * math.sin(T * 3)))
    if scan > 0:
        r = (T * 600) % 900
        cv.drawCircle(drive_xy[0], drive_xy[1], r, strokep(BTC_GOLD, 6, alpha=scan * (1 - r / 900)))

def council_bldg(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRect(skia.Rect(-420, -600, 420, 0), fillp(C('#c8c0b0'))); cv.drawRect(skia.Rect(-420, -600, 420, 0), strokep(INK, 8))
    cv.drawPath(poly([(-460, -600), (0, -800), (460, -600)]), fillp(C('#a8a090'))); cv.drawPath(poly([(-460, -600), (0, -800), (460, -600)]), strokep(INK, 8))
    for i in range(6): cv.drawRect(skia.Rect(-360 + i * 136, -520, -320 + i * 136, -40), fillp(C('#e8e0d0'))); cv.drawRect(skia.Rect(-360 + i * 136, -520, -320 + i * 136, -40), strokep(INK, 5))
    cv.drawRect(skia.Rect(-300, -580, 300, -530), fillp(C('#2a3a5a'))); text(cv, 'CITY COUNCIL', 0, -542, 40, C('#f4efe2'))
    cv.restore()

def robot_dog(cv, x, y, s=1.0, T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    for i, lx in enumerate((-110, -60, 60, 110)):
        a = math.sin(T * 6 + i * 1.6) * 0.3
        kx = lx + math.sin(a) * 40; cv.drawLine(lx, -150, kx + 20, -80, strokep(INK, 26)); cv.drawLine(lx, -150, kx + 20, -80, strokep(C('#e8c040'), 16))
        cv.drawLine(kx + 20, -80, lx, 0, strokep(INK, 22)); cv.drawLine(kx + 20, -80, lx, 0, strokep(C('#3a3a40'), 12))
    cv.drawRoundRect(skia.Rect(-160, -220, 160, -140), 30, 30, fillp(C('#e8c040'))); cv.drawRoundRect(skia.Rect(-160, -220, 160, -140), 30, 30, strokep(INK, 7))
    cv.drawRoundRect(skia.Rect(150, -230, 240, -170), 20, 20, fillp(C('#3a3a40'))); cv.drawCircle(220, -200, 10, fillp(C('#7cf29a')))
    cv.restore()

def drone(cv, x, y, s=1.0, T=0, beam_to=None):
    if beam_to: cv.drawPath(poly([(x - 20, y + 20), (x + 20, y + 20), (beam_to[0] + 160, beam_to[1]), (beam_to[0] - 160, beam_to[1])]), fillp(C('#7cf29a'), alpha=0.18))
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    for sx in (-1, 1):
        cv.drawLine(0, 0, sx * 130, -20, strokep(INK, 12))
        cv.drawOval(skia.Rect(sx * 130 - 70 * abs(math.sin(T * 30)) - 8, -34, sx * 130 + 70 * abs(math.sin(T * 30)) + 8, -22), fillp(C('#c8ccd4'), alpha=0.7))
    cv.drawRoundRect(skia.Rect(-60, -30, 60, 30), 14, 14, fillp(C('#ececf0'))); cv.drawRoundRect(skia.Rect(-60, -30, 60, 30), 14, 14, strokep(INK, 6))
    cv.drawCircle(0, 30, 16, fillp(C('#2a2a30')))
    cv.restore()

def excavator(cv, x, y, s=1.0, T=0, arm=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-220, -70, 220, 0), 35, 35, fillp(C('#2a2a30'))); cv.drawRoundRect(skia.Rect(-220, -70, 220, 0), 35, 35, strokep(INK, 6))
    for i in range(6): cv.drawCircle(-170 + i * 68, -35, 18, fillp(C('#5a5a62')))
    cv.drawRoundRect(skia.Rect(-170, -240, 120, -70), 16, 16, fillp(C('#f0b020'))); cv.drawRoundRect(skia.Rect(-170, -240, 120, -70), 16, 16, strokep(INK, 6))
    cv.drawRect(skia.Rect(-140, -220, -30, -140), fillp(C('#9ac8e8'))); cv.drawRect(skia.Rect(-140, -220, -30, -140), strokep(INK, 4))
    a = -30 + arm * 40
    cv.save(); cv.translate(100, -180); cv.rotate(a)
    cv.drawLine(0, 0, 260, 0, strokep(INK, 40)); cv.drawLine(0, 0, 260, 0, strokep(C('#f0b020'), 28))
    cv.translate(260, 0); cv.rotate(70 - arm * 30)
    cv.drawLine(0, 0, 200, 0, strokep(INK, 32)); cv.drawLine(0, 0, 200, 0, strokep(C('#f0b020'), 20))
    cv.drawPath(poly([(190, -40), (270, -10), (230, 60), (180, 30)]), fillp(C('#5a5a62'))); cv.drawPath(poly([(190, -40), (270, -10), (230, 60), (180, 30)]), strokep(INK, 5))
    cv.restore(); cv.restore()

def price_chart(cv, x0, y0, w, h, T, t0, dur=1.2, col=C('#3fbf6b'), seed=3, up=True):
    f = clamp((T - t0) / dur); rnd = random.Random(seed); pts = []
    n = 40
    for i in range(n):
        u = i / (n - 1); v = (u ** 3.2 if up else u) + rnd.uniform(-0.03, 0.03)
        pts.append((x0 + u * w, y0 + h - clamp(v, 0, 1) * h))
    m = max(2, int(n * f))
    cv.drawRect(skia.Rect(x0, y0, x0 + w, y0 + h), fillp(C('#0e1418'), alpha=0.85)); cv.drawRect(skia.Rect(x0, y0, x0 + w, y0 + h), strokep(C('#2a3a44'), 4))
    for i in range(1, 5): cv.drawLine(x0, y0 + h * i / 5, x0 + w, y0 + h * i / 5, strokep(C('#1a2a34'), 2))
    fillpath = skia.Path(); fillpath.moveTo(pts[0][0], y0 + h)
    for p in pts[:m]: fillpath.lineTo(*p)
    fillpath.lineTo(pts[m - 1][0], y0 + h); fillpath.close()
    cv.drawPath(fillpath, fillp(col, alpha=0.2))
    line = poly(pts[:m], close=False); cv.drawPath(line, strokep(col, 10))
    cv.drawCircle(*pts[m - 1], 14, fillp(col)); return pts[m - 1]

def gavel(cv, x, y, s=1.0, ang=0):
    cv.save(); cv.translate(x, y); cv.rotate(ang); cv.scale(s, s)
    cv.drawLine(0, 0, 0, 300, strokep(INK, 34)); cv.drawLine(0, 0, 0, 300, strokep(C('#8a5a3a'), 22))
    cv.drawRoundRect(skia.Rect(-120, -60, 120, 40), 30, 30, fillp(C('#7a4a2a'))); cv.drawRoundRect(skia.Rect(-120, -60, 120, 40), 30, 30, strokep(INK, 7))
    cv.drawRect(skia.Rect(-90, -60, -70, 40), fillp(C('#e8c060'))); cv.drawRect(skia.Rect(70, -60, 90, 40), fillp(C('#e8c060')))
    cv.restore()

def uk_map(cv, T):
    sea = C('#2e5670'); land = C('#d8c49a')
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(sea))
    for i in range(-300, W + 300, 60): cv.drawLine(i, -300, i, H + 300, strokep(shade(sea, 1.12), 2))
    for j in range(-300, H + 300, 60): cv.drawLine(-300, j, W + 300, j, strokep(shade(sea, 1.12), 2))
    gb = [(520, 200), (640, 260), (600, 420), (700, 560), (760, 760), (820, 980), (880, 1180), (820, 1360), (640, 1400), (420, 1420), (300, 1460), (360, 1360), (480, 1300), (420, 1220), (380, 1080), (450, 1000), (420, 860), (480, 720), (420, 560), (460, 400), (420, 300)]
    cv.drawPath(poly(gb), fillp(land)); cv.drawPath(poly(gb), strokep(INK, 6))
    wales = [(380, 1080), (450, 1000), (560, 1040), (580, 1240), (480, 1300), (420, 1220)]
    cv.drawPath(poly(wales), fillp(C('#c89a6a'))); cv.drawPath(poly(wales), strokep(INK, 5))
    ir = [(80, 700), (300, 640), (330, 900), (240, 1060), (60, 1000)]
    cv.drawPath(poly(ir), fillp(shade(land, 0.92))); cv.drawPath(poly(ir), strokep(INK, 5))
    text(cv, 'WALES', 480, 1150, 40, INK)
    return (560, 1250)

# ---- additions for Charles Ingram
CHARS.update({
    'charles': dict(adult=True, shirt=C('#3a4a6a'), coat=True, tie=C('#8a2a2a'), inner=C('#e8e8f0'), hair='sidepart', pants=C('#2a2f3d')),
    'diana':   dict(adult=True, shirt=C('#8a3a5a'), stripe=None, hair='bob', pants=C('#2a2a34')),
    'whit':    dict(adult=True, shirt=C('#5a5a4a'), coat=True, tie=C('#3a5a3a'), inner=C('#d8d8c8'), hair='bald_grey', glasses=True, pants=C('#3a3a34')),
    'host':    dict(adult=True, shirt=C('#2a2a34'), coat=True, tie=C('#1a1a20'), inner=C('#c8c8d0'), hair='short', pants=C('#2a2a34')),
    'tech':    dict(adult=True, shirt=C('#4a5a4a'), stripe=None, hair='cap', pants=C('#2a2a30')),
})
QBLUE = C('#1a2a7a'); QGOLD = C('#f0c040'); QORANGE = C('#f08a20'); QGREEN = C('#3fbf6b')
def studio(cv, T, lights=1.0, dark=0.0):
    cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(shader=lin((0, 0), (0, H), [mix(C('#0a0a2a'), C('#020208'), dark), mix(C('#12124a'), C('#04040e'), dark)])))
    for i in range(7):
        a = math.sin(T * 0.8 + i * 1.1) * 0.35
        x0 = 80 + i * 155
        cv.save(); cv.rotate(math.degrees(a) * 0.4, x0, -100)
        cv.drawPath(poly([(x0 - 14, -100), (x0 + 14, -100), (x0 + 160, 1500), (x0 - 160, 1500)]), fillp(C('#7a5aff') if i % 2 else C('#3aa0ff'), alpha=0.09 * lights, blur=14)); cv.restore()
    cv.drawOval(skia.Rect(-200, 1250, W + 200, 2100), fillp(shader=rad((540, 1650), 800, [C('#2a3a9a'), C('#0a0a2a')])))
    for r in (300, 450, 600):
        cv.drawOval(skia.Rect(540 - r * 1.3, 1650 - r * 0.42, 540 + r * 1.3, 1650 + r * 0.42), strokep(C('#6a8aff'), 4, alpha=0.5 * lights))
    if dark > 0: cv.drawRect(skia.Rect(-300, -300, W + 300, H + 300), fillp(C('#000000'), alpha=dark * 0.4))

def hot_chair(cv, x, y, s=1.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawLine(0, 0, 0, -220, strokep(C('#9aa0aa'), 16)); cv.drawLine(-80, 0, 80, 0, strokep(C('#9aa0aa'), 14))
    cv.drawRoundRect(skia.Rect(-90, -260, 90, -220), 14, 14, fillp(C('#2a2a40'))); cv.drawRoundRect(skia.Rect(-90, -260, 90, -220), 14, 14, strokep(INK, 5))
    cv.restore()

def qpanel(cv, x, y, w, q, answers, T, hi=None, hicol=QORANGE, correct=None, qscale=1.0):
    # question bar + 4 rounded answer bars (generic quiz layout)
    cv.save(); cv.translate(x, y)
    cv.drawRoundRect(skia.Rect(-w / 2, -150, w / 2, 0), 40, 40, fillp(shader=lin((0, -150), (0, 0), [C('#1a2a8a'), C('#0a1040')]))); cv.drawRoundRect(skia.Rect(-w / 2, -150, w / 2, 0), 40, 40, strokep(C('#c8d0ff'), 5))
    lines = q.split('\n')
    for i, ln in enumerate(lines): text(cv, ln, 0, -95 + i * 52 - (len(lines) - 1) * 18, 44 * qscale, C('#ffffff'))
    bw = (w - 30) / 2
    for i, a in enumerate(answers):
        cx = -w / 2 + (i % 2) * (bw + 30); cy = 40 + (i // 2) * 120
        col = C('#0a1040')
        if correct == i: col = QGREEN
        elif hi == i: col = hicol
        cv.drawRoundRect(skia.Rect(cx, cy, cx + bw, cy + 96), 30, 30, fillp(col)); cv.drawRoundRect(skia.Rect(cx, cy, cx + bw, cy + 96), 30, 30, strokep(C('#c8d0ff'), 5))
        f = skia.Font(skia.Typeface('Poppins', skia.FontStyle.Bold()), 40)
        cv.drawString('ABCD'[i] + ':', cx + 24, cy + 62, f, fillp(QGOLD if hi != i and correct != i else C('#ffffff')))
        cv.drawString(a, cx + 90, cy + 62, f, fillp(C('#ffffff')))
    cv.restore()

def money_ladder(cv, x, y, level, T, values=None, w=420):
    values = values or ['£100', '£200', '£300', '£500', '£1,000', '£2,000', '£4,000', '£8,000', '£16,000', '£32,000', '£64,000', '£125,000', '£250,000', '£500,000', '£1 MILLION']
    n = len(values); h = 74
    cv.drawRoundRect(skia.Rect(x - w / 2 - 20, y - n * h - 20, x + w / 2 + 20, y + 20), 30, 30, fillp(C('#08082a'), alpha=0.9)); cv.drawRoundRect(skia.Rect(x - w / 2 - 20, y - n * h - 20, x + w / 2 + 20, y + 20), 30, 30, strokep(C('#6a7aff'), 5))
    for i, v in enumerate(values):
        yy = y - (i + 1) * h
        cur = abs(i - level) < 0.5
        if cur: cv.drawRoundRect(skia.Rect(x - w / 2, yy + 6, x + w / 2, yy + h - 6), 24, 24, fillp(QORANGE))
        col = C('#ffffff') if (i in (4, 9) or i == n - 1) else QGOLD
        if i < level - 0.5: col = shade(col, 0.6)
        f = skia.Font(skia.Typeface('Poppins', skia.FontStyle.Bold()), 40)
        cv.drawString(str(i + 1), x - w / 2 + 20, yy + 50, f, fillp(C('#8a8aff') if not cur else C('#ffffff')))
        tw = f.measureText(v); cv.drawString(v, x + w / 2 - 20 - tw, yy + 50, f, fillp(col if not cur else C('#ffffff')))

def lifeline(cv, x, y, kind, s=1.0, crossed=0.0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    cv.drawOval(skia.Rect(-110, -70, 110, 70), fillp(C('#0a1040'))); cv.drawOval(skia.Rect(-110, -70, 110, 70), strokep(C('#c8d0ff'), 6))
    if kind == 0: text(cv, '50:50', 0, 16, 50, C('#ffffff'))
    elif kind == 1:
        cv.drawRoundRect(skia.Rect(-26, -40, 26, 40), 12, 12, strokep(C('#ffffff'), 8)); cv.drawLine(-10, 30, 10, 30, strokep(C('#ffffff'), 6))
    else:
        for i in range(3): character_head = None; cv.drawCircle(-50 + i * 50, -14, 18, fillp(C('#ffffff'))); cv.drawArc(skia.Rect(-80 + i * 50, 4, -20 + i * 50, 60), 180, 180, True, fillp(C('#ffffff')))
    if crossed > 0:
        cv.drawLine(-110 * crossed, -70 * crossed, 110 * crossed, 70 * crossed, strokep(C('#e2483b'), 18)); cv.drawLine(-110 * crossed, 70 * crossed, 110 * crossed, -70 * crossed, strokep(C('#e2483b'), 18))
    cv.restore()

def cough_burst(cv, x, y, k, s=1.0, col=C('#ffffff'), word='*COUGH*', rot=-8):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.scale(k * s, k * s); cv.rotate(rot)
    star = [(math.cos(a / 18 * math.tau) * (250 if a % 2 == 0 else 170), math.sin(a / 18 * math.tau) * (130 if a % 2 == 0 else 90)) for a in range(18)]
    cv.drawPath(poly(star), fillp(C('#e2483b'))); cv.drawPath(poly(star), strokep(INK, 7))
    text(cv, word, 0, 24, 70, col); cv.restore()

def waveform(cv, x0, y0, w, h, T, spikes=(), t0=0, prog=1.0, col=C('#7cf29a'), hicol=C('#e2483b'), hi=()):
    rnd = random.Random(4); n = 120
    for i in range(int(n * prog)):
        x = x0 + i * w / n
        a = rnd.uniform(0.05, 0.25) * h
        sp = i in spikes
        if sp: a = h * 0.95
        c = hicol if (sp and i in hi) else (QGOLD if sp else col)
        cv.drawLine(x, y0 - a / 2, x, y0 + a / 2, strokep(c, 5 if not sp else 7))

def cheque(cv, x, y, s=1.0, rot=0, amount='£1,000,000', frost=0.0, void=False, k=1.0):
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.rotate(rot); cv.scale(s * k, s * k)
    soft_shadow(cv, 0, 230, 460, 26, 0.35)
    cv.drawRect(skia.Rect(-460, -220, 460, 220), fillp(shader=lin((-460, 0), (460, 0), [C('#e8f0e0'), C('#d0e0f0')]))); cv.drawRect(skia.Rect(-460, -220, 460, 220), strokep(INK, 7))
    text(cv, 'PAY: MAJOR C. INGRAM', -120, -130, 38, INK)
    cv.drawRoundRect(skia.Rect(40, -60, 420, 40), 10, 10, fillp(C('#ffffff'))); cv.drawRoundRect(skia.Rect(40, -60, 420, 40), 10, 10, strokep(INK, 4))
    text(cv, amount, 230, 4, 52, INK)
    cv.drawLine(-420, 20, -20, 20, strokep(C('#8a8a9a'), 3)); text(cv, 'ONE MILLION POUNDS', -220, 4, 30, C('#3a3a4a'))
    cv.drawLine(160, 160, 420, 160, strokep(C('#8a8a9a'), 3))
    if frost > 0:
        cv.drawRect(skia.Rect(-460, -220, 460, 220), fillp(C('#cfe8ff'), alpha=0.55 * frost))
        rnd = random.Random(2)
        for i in range(18): snowflake(cv, rnd.uniform(-430, 430), rnd.uniform(-200, 200), rnd.uniform(16, 36) * frost, col=C('#ffffff'))
    cv.restore()

def audience(cv, T, y0=1100, rows=4, hi_seat=None, hi=0.0, dark=0.6):
    for r in range(rows):
        y = y0 + r * 170
        cv.drawRect(skia.Rect(-300, y + 20, W + 300, y + 90), fillp(shade(C('#1a1a3a'), 1 - r * 0.1)))
        for c in range(-1, 9):
            x = c * 140 + (r % 2) * 70 + 20
            is_hi = hi_seat == (r, c)
            def f(x=x, y=y, r=r, c=c): character(cv, 'host', x, y + 60, 34 + r * 4, t=T, blink_seed=r * 10 + c)
            if is_hi and hi > 0:
                cv.drawCircle(x, y - 80, 140, fillp(C('#ffe0a0'), alpha=0.35 * hi, blur=30))
                character(cv, 'whit', x, y + 60, 34 + r * 4, t=T, expr='neutral')
            else: silhouette(cv, f)

# ---- additions for Joe Simpson / Siula Grande (Touching the Void story)
_hair_old24 = hair
def hair(cv, x, y, u, kind, back=False):
    if kind in ('helmet_red', 'helmet_blue'):      # climbing helmet: dome + rim + a small headlamp
        if back: return
        col = C('#d8402e') if kind == 'helmet_red' else C('#2f6fc0')
        p = skia.Path(); p.addArc(skia.Rect(x - u * 1.08, y - u * 1.22, x + u * 1.08, y + u * 0.5), 180, 180); p.close()
        cv.drawPath(p, fillp(shader=lin((x - u, y - u * 1.2), (x + u, y), [shade(col, 1.2), shade(col, 0.85)]))); cv.drawPath(p, strokep(INK, u * 0.08))
        cv.drawRoundRect(skia.Rect(x - u * 1.12, y - u * 0.42, x + u * 1.12, y - u * 0.28), u * 0.07, u * 0.07, fillp(shade(col, 0.7)))
        cv.drawRoundRect(skia.Rect(x - u * 1.12, y - u * 0.42, x + u * 1.12, y - u * 0.28), u * 0.07, u * 0.07, strokep(INK, u * 0.05))
        cv.drawRoundRect(skia.Rect(x - u * 0.2, y - u * 0.62, x + u * 0.2, y - u * 0.4), u * 0.06, u * 0.06, fillp(C('#f4f0d8')))
        cv.drawRoundRect(skia.Rect(x - u * 0.2, y - u * 0.62, x + u * 0.2, y - u * 0.4), u * 0.06, u * 0.06, strokep(INK, u * 0.04))
        return
    return _hair_old24(cv, x, y, u, kind, back)

CHARS.update({
    'joe':   dict(adult=True, shirt=C('#d8743a'), stripe=C('#b85a28'), hair='helmet_red', pants=C('#2a3550')),
    'simon': dict(adult=True, shirt=C('#3a8a7a'), stripe=C('#2c6e62'), hair='helmet_blue', pants=C('#3a3a44')),
    'joe_bare': dict(adult=True, shirt=C('#d8743a'), stripe=C('#b85a28'), hair='short', pants=C('#2a3550')),
    'simon_bare': dict(adult=True, shirt=C('#3a8a7a'), stripe=C('#2c6e62'), hair='short_black', pants=C('#3a3a44')),
})

ICE = C('#cfe6f5'); ICE_D = C('#7fb0d4'); ICE_DD = C('#2a5a84')
def andes_sky(cv, dark=0.0, dusk=0.0):
    top = mix(mix(C('#3a7ac8'), C('#e88a5a'), dusk * 0.4), C('#0a1024'), dark)
    bot = mix(mix(C('#cfe6f8'), C('#f8c890'), dusk), C('#2a3656'), dark)
    cv.drawRect(skia.Rect(-400, -400, W + 400, H + 400), fillp(shader=lin((0, 0), (0, 1300), [top, bot])))

def peak(cv, x, y, s=1.0, dark=0.0, flutes=True, col=C('#a8b4c8')):
    """Siula Grande-like summit: a steep pyramid with a fluted west face of snow. x,y = foot centre, s=1 is 1000 px tall."""
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    rock = mix(col, C('#1e2436'), dark)
    body = [(-620, 0), (-260, -560), (-120, -800), (0, -1000), (90, -860), (230, -640), (640, 0)]
    cv.drawPath(poly(body), fillp(shader=lin((-600, -1000), (600, 0), [shade(rock, 1.15), shade(rock, 0.75)]))); cv.drawPath(poly(body), strokep(INK, 7))
    snow = mix(C('#f6faff'), C('#7a86a4'), dark)
    sn = [(-120, -800), (0, -1000), (90, -860), (170, -700), (60, -560), (-40, -620), (-150, -500), (-260, -560)]
    cv.drawPath(poly(sn), fillp(snow)); cv.drawPath(poly(sn), strokep(INK, 5))
    if flutes:
        for i in range(9):
            fx = -230 + i * 50
            cv.drawLine(fx + 80, -560 - 330 * math.exp(-((i - 4) / 3.5) ** 2), fx - 10, -60 - (i % 3) * 30, strokep(shade(snow, 0.88), 9, alpha=0.8))
    cv.restore()

def range_bg(cv, T, dark=0.0, y=1250, far=True):
    if far:
        for i, (px, h) in enumerate(((-80, 380), (260, 470), (620, 340), (980, 450), (1250, 300))):
            pts = [(px - 380, y), (px, y - h), (px + 380, y)]
            cv.drawPath(poly(pts), fillp(mix(C('#b8c6dc'), C('#28324a'), dark), alpha=0.9))
            cv.drawPath(poly([(px - 90, y - h * 0.76), (px, y - h), (px + 90, y - h * 0.76), (px + 30, y - h * 0.7)]), fillp(mix(C('#f4f8fc'), C('#6a7690'), dark)))

def rope(cv, pts, col=C('#e8c040'), w=10, alpha=1.0, slack=0.0):
    """rope through pts (list of (x,y)); slack bends each segment downwards."""
    p = skia.Path(); p.moveTo(*pts[0])
    for a, b in zip(pts, pts[1:]):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + slack * math.dist(a, b) * 0.25
        p.quadTo(mx, my, b[0], b[1])
    cv.drawPath(p, strokep(INK, w + 6, alpha=alpha)); cv.drawPath(p, strokep(col, w, alpha=alpha))
    dash = strokep(shade(col, 0.7), w * 0.45, alpha=alpha); dash.setPathEffect(skia.DashPathEffect.Make([w * 0.9, w * 1.1], 0))
    cv.drawPath(p, dash)

def ice_wall(cv, x0, y0, x1, y1, T=0, seed=3, over=0.0):
    """blue ice face from (x0,y0) top-left to (x1,y1) bottom-right; over = overhang of the top edge (px)."""
    pts = [(x0 - over, y0), (x1 + over, y0), (x1, y1), (x0, y1)]
    cv.drawPath(poly(pts), fillp(shader=lin((0, y0), (0, y1), [ICE, ICE_D]))); cv.drawPath(poly(pts), strokep(INK, 6))
    rnd = random.Random(seed)
    for i in range(10):
        xx = rnd.uniform(x0, x1); cv.drawLine(xx, y0 + 20, xx + rnd.uniform(-30, 30), y1 - rnd.uniform(20, 200), strokep(C('#ffffff'), rnd.uniform(4, 10), alpha=0.35))
    for i in range(int((x1 - x0) / 46)):     # icicles under the lip
        ix = x0 - over + 20 + i * 46 + rnd.uniform(-8, 8); L = rnd.uniform(30, 90)
        cv.drawPath(poly([(ix - 12, y0), (ix + 12, y0), (ix, y0 + L)]), fillp(C('#eaf6ff'))); cv.drawPath(poly([(ix - 12, y0), (ix + 12, y0), (ix, y0 + L)]), strokep(INK, 3))
    cv.drawRect(skia.Rect(x0 - over - 10, y0 - 40, x1 + over + 10, y0), fillp(C('#f6faff'))); cv.drawLine(x0 - over - 10, y0, x1 + over + 10, y0, strokep(INK, 5))

def crevasse_bg(cv, T, light=0.5, depth=1.0):
    """inside a crevasse: two blue ice walls, a sliver of sky at the top, darkness below."""
    cv.drawRect(skia.Rect(-400, -400, W + 400, H + 400), fillp(shader=lin((0, 0), (0, H), [C('#0e2a48'), C('#020610')])))
    cv.drawPath(poly([(380, -400), (700, -400), (640, 200), (450, 220)]), fillp(C('#dff2ff'), alpha=0.55 * light + 0.2))
    for side in (-1, 1):
        x_edge = 540 + side * 170
        pts = [(540 + side * 1000, -400), (x_edge + side * 10, -400), (x_edge - side * 40, 500), (x_edge + side * 60, 1100), (x_edge - side * 20, 1700), (540 + side * 140, 2400), (540 + side * 1000, 2400)]
        cv.drawPath(poly(pts), fillp(shader=lin((x_edge, 0), (540 + side * 700, 0), [C('#5a9ac8'), C('#0e2a48')])))
        cv.drawPath(poly(pts), strokep(INK, 6))
        rnd = random.Random(side + 7)
        for i in range(12):
            yy = rnd.uniform(-200, 1900); cv.drawLine(x_edge + side * 30, yy, x_edge + side * rnd.uniform(200, 500), yy + rnd.uniform(-60, 60), strokep(C('#9ad0f0'), rnd.uniform(3, 7), alpha=0.35))
    cv.drawPath(poly([(380, -400), (700, -400), (600, 1200), (480, 1200)]), fillp(C('#cfefff'), alpha=0.12 * light, blur=30))

def ice_ledge(cv, x, y, w=420, s=1.0):
    p = poly([(x - w / 2, y), (x + w / 2, y - 6), (x + w / 2 - 40, y + 60), (x + 30, y + 110), (x - w / 2 + 50, y + 70)])
    cv.drawPath(p, fillp(shader=lin((0, y), (0, y + 110), [C('#e8f6ff'), C('#6aa0c8')]))); cv.drawPath(p, strokep(INK, 6))

def tent(cv, x, y, s=1.0, lit=False, col=C('#e8a030'), T=0):
    cv.save(); cv.translate(x, y); cv.scale(s, s)
    if lit: cv.drawCircle(0, -80, 260, fillp(C('#ffd890'), alpha=0.35, blur=60))
    body = poly([(-200, 0), (0, -190), (200, 0)])
    cv.drawPath(body, fillp(shade(col, 1.25) if lit else col)); cv.drawPath(body, strokep(INK, 7))
    cv.drawPath(poly([(-40, 0), (0, -110), (40, 0)]), fillp(C('#3a2a1a') if not lit else C('#fff0b8'))); cv.drawPath(poly([(-40, 0), (0, -110), (40, 0)]), strokep(INK, 5))
    cv.drawLine(0, -190, 0, -230, strokep(INK, 6)); cv.drawLine(-200, 0, -260, 10, strokep(INK, 3)); cv.drawLine(200, 0, 260, 10, strokep(INK, 3))
    cv.restore()

def ice_axe(cv, x, y, s=1.0, ang=0):
    cv.save(); cv.translate(x, y); cv.rotate(ang); cv.scale(s, s)
    cv.drawRoundRect(skia.Rect(-8, -10, 8, 160), 6, 6, fillp(C('#3a3a44'))); cv.drawRoundRect(skia.Rect(-8, -10, 8, 160), 6, 6, strokep(INK, 4))
    hp = poly([(-70, -10), (60, -22), (80, -6), (10, 4), (-70, 6)])
    cv.drawPath(hp, fillp(C('#c8ccd4'))); cv.drawPath(hp, strokep(INK, 4)); cv.restore()

def bone_icon(cv, x, y, s=1.0, crack=0.0, k=1.0):
    """simple cartoon leg bone (x-ray card style); crack 0..1 draws the break as a red zigzag. Non-graphic."""
    if k <= 0: return
    cv.save(); cv.translate(x, y); cv.scale(s * k, s * k)
    cv.drawRoundRect(skia.Rect(-220, -300, 220, 300), 30, 30, fillp(C('#0e1a2a'))); cv.drawRoundRect(skia.Rect(-220, -300, 220, 300), 30, 30, strokep(INK, 8))
    for dy in (-1, 1):
        cv.drawRoundRect(skia.Rect(-28, dy * 30 - (220 if dy < 0 else 0), 28, dy * 30 + (220 if dy > 0 else 0)), 20, 20, fillp(C('#eef4ff')))
        for sx in (-1, 1): cv.drawCircle(sx * 34, dy * 230, 40, fillp(C('#eef4ff')))
    cv.drawRoundRect(skia.Rect(-60, -40, 60, 40), 30, 30, fillp(C('#eef4ff')))
    if crack > 0:
        zz = [(-70, -6), (-40, 14), (-10, -14), (20, 12), (50, -10), (80, 8)]
        n = max(2, int(len(zz) * crack + 0.999)); cv.drawPath(poly(zz[:n], close=False), strokep(C('#e2483b'), 12))
    cv.restore()

def peru_map(cv, T, pin=1.0, sea=C('#2e5670'), land=C('#d8c49a')):
    cv.drawRect(skia.Rect(-400, -400, W + 400, H + 400), fillp(sea))
    for i in range(-400, W + 400, 60): cv.drawLine(i, -400, i, H + 400, strokep(shade(sea, 1.12), 2))
    for j in range(-400, H + 400, 60): cv.drawLine(-400, j, W + 400, j, strokep(shade(sea, 1.12), 2))
    sa = [(300, 240), (520, 160), (760, 260), (980, 420), (1040, 640), (980, 860), (860, 1080), (760, 1300), (640, 1520), (560, 1760), (520, 1900), (470, 1880),
          (470, 1600), (420, 1300), (360, 1060), (300, 860), (220, 700), (200, 520), (240, 360)]
    cv.drawPath(poly(sa), fillp(shade(land, 0.92))); cv.drawPath(poly(sa), strokep(INK, 6))
    pe = [(240, 360), (330, 420), (380, 560), (470, 640), (480, 820), (430, 960), (360, 1000), (300, 860), (220, 700), (200, 520)]
    cv.drawPath(poly(pe), fillp(C('#d8a070'))); cv.drawPath(poly(pe), strokep(INK, 6))
    text(cv, 'PERU', 330, 600, 48, INK)
    text(cv, 'SOUTH AMERICA', 720, 1000, 34, shade(INK, 1.6))
    k = back(clamp(pin))
    if k > 0:
        cv.save(); cv.translate(390, 760); cv.scale(k, k)
        cv.drawPath(poly([(0, 0), (-28, -56), (28, -56)]), fillp(C('#e2483b'))); cv.drawCircle(0, -76, 34, fillp(C('#e2483b'))); cv.drawCircle(0, -76, 34, strokep(INK, 5))
        cv.drawCircle(0, -76, 11, fillp(C('#f4efe2'))); cv.restore()

def moraine(cv, T, y=1150, seed=4, dark=0.0):
    """glacier moraine: grey rubble field under a pale sky."""
    cv.drawRect(skia.Rect(-400, y - 40, W + 400, H + 400), fillp(shader=lin((0, y), (0, H), [mix(C('#9a958a'), C('#2a2a30'), dark), mix(C('#6a655c'), C('#14141a'), dark)])))
    rnd = random.Random(seed)
    for i in range(70):
        rx = rnd.uniform(-200, W + 200); ry = rnd.uniform(y, H + 100); r = rnd.uniform(14, 46) * (0.6 + (ry - y) / 900)
        cv.drawOval(skia.Rect(rx - r, ry - r * 0.6, rx + r, ry + r * 0.5), fillp(mix(C('#b0aaa0'), C('#3a3a40'), dark * 0.8 + rnd.uniform(0, 0.25))))
        cv.drawOval(skia.Rect(rx - r, ry - r * 0.6, rx + r, ry + r * 0.5), strokep(INK, 3))

def crawler(cv, name, x, y, u, T, speed=3.0, expr='strain', look=(1, 0.2)):
    """a stick figure dragging himself along on his elbows, facing right; the stiff (broken) leg trails straight."""
    ph = T * speed
    cv.save(); cv.translate(x, y)
    lw = u * 0.085; lp = strokep(INK, lw)
    hip = (-u * 1.2, -u * 0.25); sh = (u * 0.35, -u * 0.55 + math.sin(ph) * u * 0.05)
    cv.drawLine(*hip, -u * 3.0, -u * 0.08, lp)                                 # stiff leg, straight out behind
    cv.drawLine(*hip, -u * 2.3, -u * 0.3 + math.sin(ph) * u * 0.08, lp); cv.drawLine(-u * 2.3, -u * 0.3 + math.sin(ph) * u * 0.08, -u * 2.9, -u * 0.05, lp)
    body = skia.Path(); body.moveTo(*hip); body.lineTo(*sh)
    cv.drawPath(body, strokep(INK, u * 1.0)); cv.drawPath(body, strokep(CHARS[name]['shirt'], u * 0.84))
    for s_ in (0, math.pi):
        ex = sh[0] + u * 0.6 + math.cos(ph + s_) * u * 0.35; cv.drawLine(*sh, ex, -u * 0.15, lp); cv.drawLine(ex, -u * 0.15, ex + u * 0.4, -u * 0.02, lp)
    hx, hy = sh[0] + u * 1.15, sh[1] - u * 0.45
    hair(cv, hx, hy, u, CHARS[name]['hair'], back=True)
    hr_ = skia.Rect(hx - u, hy - u * 0.95, hx + u, hy + u * 0.92)
    cv.drawOval(hr_, fillp(shader=rad((hx - u * 0.35, hy - u * 0.4), u * 1.6, [C('#ffffff'), HEAD, C('#d9d6cf')], [0, 0.55, 1]))); cv.drawOval(hr_, strokep(INK, lw))
    hair(cv, hx, hy, u, CHARS[name]['hair']); face(cv, hx, hy, u, expr, ((T % 3.1) < 0.12), look)
    cv.restore()
