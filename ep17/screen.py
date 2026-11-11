"""Monitor picture screen/s_NNNN.png (1920x1080, one per film frame).
A generic work document + a big desktop clock widget (4:59 PM; seconds once we're on the screen close-up) + taskbar;
at CALL an original "work chat" incoming-call card: BOSS / Incoming call / Decline - Accept (no real app's logo or artwork).
The cursor glides toward Accept and stops just short of it."""
import os, sys, math
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from beats import *
W, H = 1920, 1080
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def F(p, s): return ImageFont.truetype(p, s)
os.makedirs('screen', exist_ok=True)
def sm(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
TYPED = "Q4 numbers attached. That's everything for today."
def base(f):
    im = Image.new('RGB', (W, H), (226, 229, 236)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 64), fill=(52, 58, 74)); d.text((28, 16), 'Q4 Report - Final', font=F(FB, 30), fill=(235, 238, 245))
    for i, t in enumerate(('File', 'Edit', 'View', 'Share')): d.text((520 + 120 * i, 18), t, font=F(FR, 26), fill=(190, 196, 210))
    d.rectangle((360, 290, 1560, 1020), fill=(255, 255, 255), outline=(205, 208, 216))         # the document page
    y = 330
    for i, w_ in enumerate((900, 1040, 760, 980, 600, 1010)):
        d.rounded_rectangle((420, y, 420 + w_, y + 18), 6, fill=(205, 210, 220)); y += 46
    n = int(len(TYPED) * sm((f - TYPE[0]) / (TYPE[1] - TYPE[0] - 2))) if f >= TYPE[0] else 0
    d.text((420, y + 14), TYPED[:n], font=F(FR, 38), fill=(40, 44, 56))
    if n < len(TYPED) or (f // 15) % 2 == 0:                                                   # caret
        cx = 420 + d.textlength(TYPED[:n], font=F(FR, 38)) + 4; d.rectangle((cx, y + 12, cx + 3, y + 58), fill=(40, 44, 56))
    d.rectangle((0, H - 58, W, H), fill=(32, 36, 48))                                           # taskbar
    for i in range(6): d.rounded_rectangle((40 + 70 * i, H - 46, 84 + 70 * i, H - 12), 8, fill=(80, 90, 112))
    d.text((W - 190, H - 46), '4:59 PM', font=F(FB, 28), fill=(225, 230, 240))
    return im
def clock(im, f):
    d = ImageDraw.Draw(im)
    t = '4:59 PM' if f < SH['S'][0] else ('4:59:58 PM' if f < CLK_59 else '4:59:59 PM')
    fn = F(FB, 150); tw = d.textlength(t, font=fn)
    x0 = (W - tw) / 2 - 50
    d.rounded_rectangle((x0, 70, x0 + tw + 100, 258), 44, fill=(24, 28, 40))
    d.text(((W - tw) / 2, 82), t, font=fn, fill=(255, 255, 255))
    if f >= CLK_59 and f < CLK_59 + 6:                                                        # the tick: a quick flash on the last digit
        a = 1 - (f - CLK_59) / 6; d.rounded_rectangle((x0 - 6, 64, x0 + tw + 106, 264), 48, outline=(255, 214, 120), width=int(2 + 6 * a))
def handset(d, cx, cy, s, down=False):
    """a simple phone-handset glyph (two ear/mouth pads joined by an arc) - drawn, not copied"""
    rot = math.radians(135 if down else -45)
    pts = []
    for k in range(25):
        a = math.pi * k / 24; x = math.cos(a) * s * 0.55; y = -math.sin(a) * s * 0.30 + s * 0.12
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    d.line(pts, fill=(255, 255, 255), width=int(s * 0.2), joint='curve')
    for e in (pts[0], pts[-1]): d.ellipse((e[0] - s * 0.17, e[1] - s * 0.17, e[0] + s * 0.17, e[1] + s * 0.17), fill=(255, 255, 255))
ACC = (1120, 822); DEC = (800, 822); BR = 64
def call(im, f):
    a = sm((f - CALL) / 5);
    if a <= 0: return im
    dim = Image.new('RGBA', (W, H), (10, 12, 20, int(110 * a))); im = Image.alpha_composite(im.convert('RGBA'), dim)
    card = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((500, 290, 1420, 990), 30, fill=(36, 36, 58, 255), outline=(98, 100, 190, 255), width=3)
    d.text((540, 296), 'Work Chat  ·  Call', font=F(FR, 30), fill=(170, 172, 210))
    ring = ((f - CALL) % 30) / 30                                                              # pulsing rings round the avatar
    for k in (0, 0.5):
        r_ = 86 + 70 * ((ring + k) % 1); al = int(150 * (1 - (ring + k) % 1))
        d.ellipse((960 - r_, 450 - r_, 960 + r_, 450 + r_), outline=(120, 124, 230, al), width=4)
    d.ellipse((960 - 86, 450 - 86, 960 + 86, 450 + 86), fill=(98, 100, 190, 255))
    fn = F(FB, 92); tw = d.textlength('B', font=fn); d.text((960 - tw / 2, 450 - 56), 'B', font=fn, fill=(255, 255, 255))
    fn = F(FB, 96); tw = d.textlength('BOSS', font=fn); d.text((960 - tw / 2, 560), 'BOSS', font=fn, fill=(255, 255, 255))
    fn = F(FR, 50); tw = d.textlength('Incoming call', font=fn); d.text((960 - tw / 2, 672), 'Incoming call', font=fn, fill=(200, 202, 225))
    for (cx, cy), col, lab, dn in ((DEC, (214, 54, 64), 'Decline', True), (ACC, (34, 170, 84), 'Accept', False)):
        d.ellipse((cx - BR, cy - BR, cx + BR, cy + BR), fill=col + (255,)); handset(d, cx, cy, 58, dn)
        fn = F(FB, 36); tw = d.textlength(lab, font=fn); d.text((cx - tw / 2, cy + BR + 12), lab, font=fn, fill=(235, 236, 245))
    s = 0.92 + 0.08 * a                                                                        # a small pop-in
    card = card.resize((int(W * s), int(H * s)), Image.LANCZOS); c2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    c2.paste(card, ((W - card.width) // 2, (H - card.height) // 2)); c2.putalpha(Image.eval(c2.getchannel('A'), lambda v: int(v * a)))
    return Image.alpha_composite(im, c2).convert('RGB')
C0, C1 = (1560, 640), (ACC[0] + 50, ACC[1] - 92)           # comes in from the right, stops just above-right of Accept
def cursor_pos(f):
    if f < TYPE[1]: return (420 + 30 * math.sin(f * 0.2), 680)
    if f < CURSOR[0]: return C0
    return tuple(a + (b - a) * sm((f - CURSOR[0]) / (CURSOR[1] - CURSOR[0])) for a, b in zip(C0, C1))
def cursor(im, f):
    x, y = cursor_pos(f); d = ImageDraw.Draw(im); s = 1.6
    p = [(0, 0), (0, 34), (9, 26), (15, 40), (21, 37), (15, 24), (27, 24)]
    d.polygon([(x + a * s, y + b * s) for a, b in p], fill=(20, 20, 24), outline=(255, 255, 255), width=3)
for f in range(1, N + 1):
    im = base(f); im = call(im, f); clock(im, f); cursor(im, f)
    im.save(f'screen/s_{f:04d}.png')
Image.open(f'screen/s_{CALL + 20:04d}.png').save('screen_call.jpg', quality=88); Image.open('screen/s_0030.png').save('screen_work.jpg', quality=88)
print('screen frames', N)
