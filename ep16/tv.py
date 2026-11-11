"""TV picture tv/tv_NNNN.png (one per film frame): off -> fictional console boot logo -> an original game's title menu
(LANTERN HOLLOW: NEW GAME / CONTINUE / SETTINGS) that never changes - nobody ever presses start."""
import os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
B = json.load(open('beats.json')); N = B['N']
W, H = 960, 540
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FS = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
os.makedirs('tv', exist_ok=True)
def sm(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
rng = np.random.default_rng(16)

# ---- static menu art: dusk sky, layered hills, a lit lantern tower on a hill, title, menu
yy = np.linspace(0, 1, H)[:, None]
sky = (np.array([18, 22, 58]) * (1 - yy) + np.array([120, 70, 110]) * yy ** 1.6).astype(np.float32)
art = np.repeat(sky[:, None, :].reshape(H, 1, 3), W, 1)
im0 = Image.fromarray(np.clip(art, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im0)
d.ellipse((640, 70, 760, 190), fill=(255, 226, 170))                                    # big moon
for k, (base, amp, col) in enumerate(((330, 50, (48, 40, 82)), (380, 40, (34, 30, 62)), (430, 30, (22, 20, 42)))):
    pts = [(0, H)] + [(x, base - amp * math.sin(x / (140 + 40 * k) + k) - 18 * math.sin(x / 47.0 + 2 * k)) for x in range(0, W + 10, 10)] + [(W, H)]
    d.polygon(pts, fill=col)
tx, ty = 720, 300                                                                       # lantern tower
d.rectangle((tx - 14, ty - 120, tx + 14, ty + 40), fill=(16, 14, 30)); d.polygon([(tx - 26, ty - 120), (tx + 26, ty - 120), (tx, ty - 165)], fill=(16, 14, 30))
glow = Image.new('L', (W, H), 0); ImageDraw.Draw(glow).ellipse((tx - 60, ty - 140, tx + 60, ty - 30), fill=200)
glow = glow.filter(ImageFilter.GaussianBlur(28))
im0 = Image.composite(Image.new('RGB', (W, H), (255, 190, 90)), im0, glow.point(lambda v: int(v * 0.7)))
d = ImageDraw.Draw(im0); d.rectangle((tx - 7, ty - 98, tx + 7, ty - 80), fill=(255, 220, 140))
STARS = [(rng.integers(0, W), rng.integers(0, 230), rng.random() * 6.28) for _ in range(60)]
FT = ImageFont.truetype(FS, 66); FT2 = ImageFont.truetype(FS, 24); FM = ImageFont.truetype(FB, 38); FH = ImageFont.truetype(FB, 16)
def title(d):
    for dx, dy in ((3, 3),): d.text((70 + dx, 60 + dy), 'LANTERN', font=FT, fill=(20, 10, 30))
    d.text((70, 60), 'LANTERN', font=FT, fill=(255, 214, 140)); d.text((74, 128), 'H O L L O W', font=FT2, fill=(250, 236, 210))
ITEMS = ['NEW GAME', 'CONTINUE', 'SETTINGS']
def menu(f):
    im = im0.copy(); d = ImageDraw.Draw(im)
    for (x, y, ph) in STARS:
        a = 0.5 + 0.5 * math.sin(ph + f * 0.12); c = int(150 + 105 * a); d.point((int(x), int(y)), fill=(c, c, c))
        if a > 0.85: d.point((int(x) + 1, int(y)), fill=(c, c, c))
    title(d)
    pulse = 0.5 + 0.5 * math.sin(f * 0.16)
    y0 = 270
    for i, t in enumerate(ITEMS):
        y = y0 + i * 62
        if i == 0:      # selected: highlight bar + arrow, gently pulsing (waiting for a press that never comes)
            bar = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(bar).rounded_rectangle((52, y - 8, 360, y + 46), 10, fill=(255, 210, 120, int(70 + 50 * pulse)))
            im = Image.alpha_composite(im.convert('RGBA'), bar).convert('RGB'); d = ImageDraw.Draw(im)
            d.polygon([(64, y + 8), (64, y + 32), (82, y + 20)], fill=(255, 240, 200))
            d.text((96, y), t, font=FM, fill=(255, 255, 255))
        else:
            d.text((96, y), t, font=FM, fill=(190, 184, 210))
    d.text((W - 250, H - 34), 'v1.0   ©2026 Hollow Lamp Games', font=FH, fill=(170, 160, 190))
    return im
def boot(f):
    a = sm((f - B['BOOT'][0]) / 8) * (1 - sm((f - (B['MENU_ON'] - 6)) / 6))
    im = Image.new('RGB', (W, H), (4, 6, 14)); d = ImageDraw.Draw(im)
    c = tuple(int(v * a) for v in (235, 240, 255))
    f_ = ImageFont.truetype(FB, 64); tw = d.textlength('NOVA', font=f_)
    d.text(((W - tw) / 2, H / 2 - 50), 'NOVA', font=f_, fill=c)
    r = 26 + 4 * a; d.ellipse((W / 2 - r, H / 2 + 40 - r * 0.2, W / 2 + r, H / 2 + 40 + r * 0.2), outline=tuple(int(v * a) for v in (90, 150, 255)), width=3)
    return im
for f in range(1, N + 1):
    if f < B['BOOT'][0]: im = Image.new('RGB', (W, H), (0, 0, 0))
    elif f < B['MENU_ON']: im = boot(f)
    else:
        im = menu(f)
        if f < B['MENU_ON'] + 8: im = Image.blend(Image.new('RGB', (W, H)), im, sm((f - B['MENU_ON']) / 8))
    im.save(f'tv/tv_{f:04d}.png')
Image.open(f'tv/tv_{max(1, B["MENU_ON"] + 30):04d}.png').save('tv_menu.jpg')
print('tv frames', N)
