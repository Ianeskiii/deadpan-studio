"""Phone screen frames screen/sc_0001.png ... (one per film frame).
Feed app while scrolling -> accidental tap on the camera shortcut -> front camera (frames/SEL, mirrored, with camera UI) -> off.
The selfie frames are real renders from the phone's position (build.py SEL), so the face is the same Doug model; only the
angle changes. The low-angle grade adds the cheap-front-camera look (harsh contrast, green cast, noise, a little barrel)."""
import os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
B = json.load(open('beats.json')); N = B['N']
W, H = 432, 888
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f_s, f_b, f_t = ImageFont.truetype(FR, 17), ImageFont.truetype(FB, 19), ImageFont.truetype(FB, 15)
os.makedirs('screen', exist_ok=True)
def sm(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

# ------------------------------------------------------------------ feed (one long canvas)
rng = np.random.default_rng(14)
FEED_H = 3400
feed = Image.new('RGB', (W, FEED_H), (246, 246, 248)); d = ImageDraw.Draw(feed)
PAL = [((255, 166, 92), (255, 94, 98)), ((120, 200, 255), (60, 110, 220)), ((150, 230, 160), (40, 150, 110)), ((255, 220, 120), (240, 150, 60)),
       ((210, 160, 255), (120, 80, 200))]
names = ['pizza_rat_fan', 'sunset.daily', 'mountain_mike', 'cat_facts_99', 'nature.pics', 'daily.donut', 'lake_life']
y = 80
for i in range(9):
    c0, c1 = PAL[i % len(PAL)]
    d.ellipse((18, y, 58, y + 40), fill=c1); d.text((70, y + 9), names[i % len(names)], font=f_b, fill=(30, 30, 34))
    d.text((W - 40, y + 4), '...', font=f_b, fill=(120, 120, 120))
    y += 54; ih = 330
    for k in range(ih):    # gradient picture
        t = k / ih; col = tuple(int(c0[j] * (1 - t) + c1[j] * t) for j in range(3)); d.line((0, y + k, W, y + k), fill=col)
    kind = i % 3
    if kind == 0: d.ellipse((W / 2 - 60, y + 90, W / 2 + 60, y + 210), fill=(255, 240, 200))
    elif kind == 1: d.polygon([(0, y + ih), (140, y + 120), (260, y + ih)], fill=(70, 80, 110)); d.polygon([(150, y + ih), (300, y + 80), (W, y + ih)], fill=(50, 60, 90))
    else: d.ellipse((W / 2 - 110, y + 70, W / 2 + 110, y + 290), fill=(232, 180, 90)); d.ellipse((W / 2 - 90, y + 90, W / 2 + 90, y + 270), fill=(250, 214, 120))
    y += ih + 14
    for k, ic in enumerate(('♡', '◯', '➤')): d.text((20 + k * 46, y), ic, font=f_b, fill=(40, 40, 44))
    d.rounded_rectangle((20, y + 36, 20 + rng.integers(180, 360), y + 50), 6, fill=(205, 205, 212))
    d.rounded_rectangle((20, y + 60, 20 + rng.integers(120, 300), y + 74), 6, fill=(220, 220, 226))
    y += 100
def feed_frame(f, tap=0.0):
    off = 0.0
    for s in B['SWIPES']: off += 330 * sm((f - s) / 12)
    off += 6 * f / 30                     # a little inertia drift
    im = feed.crop((0, int(off), W, int(off) + H)).copy(); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 64), fill=(255, 255, 255)); d.text((18, 20), 'feed', font=ImageFont.truetype(FB, 26), fill=(20, 20, 24))
    d.text((W - 70, 22), '9:41', font=f_t, fill=(20, 20, 24))
    d.rectangle((0, H - 78, W, H), fill=(255, 255, 255)); d.line((0, H - 78, W, H - 78), fill=(220, 220, 225), width=2)
    # bottom bar: camera shortcut at the far left (the one he hits), home, search, profile
    cx, cy = 44, H - 38
    # v2: the camera shortcut is a filled blue button so it reads at a glance; it lights up when his thumb lands on it
    d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(40, 120, 255) if tap <= 0 else (20, 80, 200))
    d.rounded_rectangle((cx - 17, cy - 10, cx + 17, cy + 14), 5, fill=(255, 255, 255)); d.ellipse((cx - 8, cy - 6, cx + 8, cy + 10), fill=(40, 120, 255))
    d.ellipse((cx - 4, cy - 2, cx + 4, cy + 6), fill=(255, 255, 255)); d.rectangle((cx - 7, cy - 15, cx + 5, cy - 10), fill=(255, 255, 255))
    for k, x in enumerate((150, 250, 360)):
        if k == 0: d.polygon([(x - 18, cy + 14), (x - 18, cy - 4), (x, cy - 18), (x + 18, cy - 4), (x + 18, cy + 14)], outline=(20, 20, 24), width=3)
        if k == 1: d.ellipse((x - 13, cy - 15, x + 9, cy + 7), outline=(20, 20, 24), width=3); d.line((x + 6, cy + 4, x + 16, cy + 14), fill=(20, 20, 24), width=4)
        if k == 2: d.ellipse((x - 15, cy - 15, x + 15, cy + 15), fill=(255, 120, 90))
    if tap > 0:
        r = 30 + 34 * tap; a = int(170 * (1 - tap))
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse((cx - r, cy - r, cx + r, cy + r), fill=(120, 120, 130, a))
        im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')
    return im

# ------------------------------------------------------------------ front camera
def lowness(f):
    """1 = phone low (the horrifying angle), 0 = raised (normal)"""
    (r0, r1), (l0, l1) = B['RAISE'][0], B['LOWER'][0]       # v2 final: one comparison, keyed from build.py's phone moves
    K = [(1, 1.0), (r0, 1.0), (r1, 0.0), (l0, 0.0), (l1, 1.0), (N, 1.0)]
    for (fa, a), (fb, b) in zip(K, K[1:]):
        if fa <= f <= fb: return a + (b - a) * sm((f - fa) / max(1, fb - fa))
    return 1.0
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
def barrel(a, k):
    if k <= 1e-3: return a
    h = a.shape[0]; X, Y = xx[:h], yy[:h]
    cx, cy = W / 2, h * 0.5; nx, ny = (X - cx) / (W / 2), (Y - cy) / (W / 2); r2 = nx * nx + ny * ny
    s = 1 / (1 + k * r2); sx = np.clip(cx + nx * s * (W / 2), 0, W - 1).astype(np.int32); sy = np.clip(cy + ny * s * (W / 2), 0, h - 1).astype(np.int32)
    return a[sy, sx]
def selfie(f):
    p = f'frames/SEL/SEL_{f:04d}.png'
    if not os.path.exists(p):    # holds were rendered with a step; use the nearest earlier frame
        g = f
        while g > 0 and not os.path.exists(f'frames/SEL/SEL_{g:04d}.png'): g -= 1
        p = f'frames/SEL/SEL_{g:04d}.png'
    im = Image.open(p).convert('RGB').transpose(Image.FLIP_LEFT_RIGHT)       # front cameras show a mirror image
    vh = H - 64 - 170; sc = max(W / im.width, vh / im.height); im = im.resize((int(im.width * sc + 0.5), int(im.height * sc + 0.5)), Image.LANCZOS)
    x0 = (im.width - W) // 2; y0 = (im.height - vh) // 2; im = im.crop((x0, y0, x0 + W, y0 + vh))
    L = lowness(f); a = np.asarray(im).astype(np.float32) / 255
    # cheap-front-camera grade, scaled by how low the phone is
    lum = a @ np.array([0.3, 0.59, 0.11], np.float32)
    a = a + (lum[..., None] - a) * 0.25 * L                                  # washed-out colour
    a = (a - 0.5) * (1 + 0.35 * L) + 0.5 + 0.05 * L                          # harsh contrast, blown highlights
    a = a * (1 - L * np.array([0.08, -0.03, 0.06], np.float32))              # sickly green cast
    a = a * (1 + 0.04 * (1 - L) * np.array([1.0, 0.4, -0.6], np.float32))    # raised: a touch warmer
    a = barrel(a, 0.22 * L)
    rr = np.random.default_rng(f); a = a + rr.normal(0, 0.035 * L, a.shape[:2])[..., None]
    vg = 1 - 0.35 * L * np.clip(((xx[:vh] - W / 2) ** 2 / (W / 2) ** 2 + (yy[:vh] - vh / 2) ** 2 / (vh / 2) ** 2) - 0.3, 0, 1)
    a = np.clip(a * vg[..., None], 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))
def camera_frame(f, fade=1.0):
    im = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    if fade > 0:
        s = selfie(f)
        if fade < 1: s = Image.blend(Image.new('RGB', s.size), s, fade)
        im.paste(s, (0, 64))
    d.rectangle((0, 0, W, 64), fill=(0, 0, 0))
    d.polygon([(40, 18), (28, 36), (38, 36), (32, 50), (48, 30), (38, 30), (44, 18)], fill=(255, 255, 255))      # flash
    d.ellipse((W / 2 - 4, 28, W / 2 + 4, 36), fill=(255, 210, 60))
    d.rectangle((0, H - 170, W, H), fill=(0, 0, 0))
    for k, (t, c) in enumerate((('VIDEO', (200, 200, 200)), ('PHOTO', (255, 210, 60)), ('PORTRAIT', (200, 200, 200)))):
        tw = d.textlength(t, font=f_t); d.text((W / 2 + (k - 1) * 120 - tw / 2, H - 160), t, font=f_t, fill=c)
    cx, cy = W / 2, H - 82
    d.ellipse((cx - 38, cy - 38, cx + 38, cy + 38), outline=(255, 255, 255), width=5); d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(255, 255, 255))
    d.rounded_rectangle((40, cy - 22, 84, cy + 22), 8, fill=(90, 90, 90))                                          # last-photo thumbnail
    x = W - 62; d.ellipse((x - 22, cy - 22, x + 22, cy + 22), fill=(60, 60, 60)); d.arc((x - 12, cy - 12, x + 12, cy + 12), 200, 340, fill='white', width=3)
    d.arc((x - 12, cy - 12, x + 12, cy + 12), 20, 160, fill='white', width=3)                                        # flip camera (already on front)
    return im
CAM_ON, OFF, TAP = B['CAM_ON'], B['SCREEN_OFF'], B['TAP_CAM']
OPEN = 5          # v2: the camera app zooms open out of the icon he hit, so the switch is obvious
for f in range(1, N + 1):
    if f < CAM_ON: im = feed_frame(f, sm((f - TAP) / (CAM_ON - TAP)) if TAP <= f < CAM_ON else 0.0)
    elif f < CAM_ON + OPEN:
        k = sm((f - CAM_ON + 1) / OPEN); bg = feed_frame(CAM_ON - 1, 1.0)
        cf = camera_frame(f, min(1.0, 0.2 + k)); w_, h_ = max(2, int(W * k)), max(2, int(H * k))
        x_ = int(44 * (1 - k)); y_ = int((H - 38) * (1 - k) - 0 * k)
        bg.paste(cf.resize((w_, h_), Image.LANCZOS), (x_ - int(w_ * 0.0), y_ - int(h_ * (1 - k) * 0)))
        im = bg
    elif f < OFF: im = camera_frame(f)
    else: im = Image.new('RGB', (W, H), (0, 0, 0))
    im.save(f'screen/sc_{f:04d}.png')
sheet = Image.new('RGB', (W * 5 // 2, H // 2))
for i, f in enumerate((50, 66, 71, 100, 250)): sheet.paste(Image.open(f'screen/sc_{f:04d}.png').resize((W // 2, H // 2)), (i * W // 2, 0))
sheet.save('screen_sheet.jpg'); print('screen frames', N)
