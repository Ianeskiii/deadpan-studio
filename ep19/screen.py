"""Phone screens (static images, 1000x2060 portrait):
  screen/mom_post.png   Mom's phone: an obviously sensational, unreliable feed post (all caps, "RAW?!" = "allegedly",
                        "SHARE BAGO MA-DELETE!!!"), posted by a gossip page, dated Marso 14, 2016 (big and readable for the OTS insert).
                        No real app logo, no real person's photo: a generic blue feed bar and a drawn candle + question marks.
  screen/doug_feed.png  Doug's phone: a plain dark-mode feed (grey blocks), so nothing on it competes with the joke."""
import os
from PIL import Image, ImageDraw, ImageFont
W, H = 1000, 2060
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def F(p, s): return ImageFont.truetype(p, s)
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screen'), exist_ok=True)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screen')

def wrap(d, text, font, width):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out

# ---------------------------------------------------------------- Mom's post
im = Image.new('RGB', (W, H), (240, 242, 245)); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 70), fill=(255, 255, 255)); d.text((40, 16), '9:41', font=F(FB, 36), fill=(20, 20, 20))
d.rounded_rectangle((W - 120, 24, W - 50, 50), 6, outline=(20, 20, 20), width=4); d.rectangle((W - 116, 28, W - 70, 46), fill=(20, 20, 20))
d.rectangle((0, 70, W, 190), fill=(59, 89, 152))                                   # generic blue app bar, no wordmark
d.rounded_rectangle((40, 100, 640, 160), 30, fill=(86, 116, 178)); d.text((80, 110), 'Maghanap...', font=F(FR, 36), fill=(205, 215, 235))
for i in range(3): d.ellipse((700 + 95 * i, 100, 760 + 95 * i, 160), fill=(86, 116, 178))
y = 215
d.rectangle((0, y, W, H - 120), fill=(255, 255, 255))
# post header: page avatar, page name, DATE (big), public globe
d.ellipse((40, y + 30, 170, y + 160), fill=(214, 40, 40)); d.text((83, y + 45), '!', font=F(FB, 96), fill=(255, 230, 0))
d.text((195, y + 30), 'SHOWBIZ CHIKA', font=F(FB, 50), fill=(20, 20, 20))
d.text((195, y + 88), 'UPDATES 24/7', font=F(FB, 40), fill=(20, 20, 20))
d.text((40, y + 185), 'Marso 14, 2016', font=F(FB, 72), fill=(70, 74, 82))
gx = 40 + int(d.textlength('Marso 14, 2016', font=F(FB, 72))) + 30
d.text((gx, y + 196), '·', font=F(FB, 60), fill=(70, 74, 82)); gx += 50
d.ellipse((gx, y + 205, gx + 56, y + 261), outline=(70, 74, 82), width=6); d.line((gx + 28, y + 205, gx + 28, y + 261), fill=(70, 74, 82), width=5)
d.line((gx, y + 233, gx + 56, y + 233), fill=(70, 74, 82), width=5)
d.text((W - 110, y + 20), '...', font=F(FB, 60), fill=(100, 100, 100))
# the sensational text
y += 300
f1 = F(FB, 64)
for ln in wrap(d, 'BREAKING NEWS: JACKIE CHAN PATAY NA RAW?!', f1, W - 80):
    d.text((40, y), ln, font=f1, fill=(15, 15, 15)); y += 78
y += 10
f2 = F(FB, 46)
for ln in wrap(d, 'SHARE MO NA BAGO MA-DELETE!!! 100% TOTOO!!!', f2, W - 80):
    d.text((40, y), ln, font=f2, fill=(200, 30, 30)); y += 58
y += 24
# the picture: a drawn candle on black, BREAKING banner, big question marks (no photo of anyone)
ih = 640
d.rectangle((0, y, W, y + ih), fill=(18, 18, 22))
d.rectangle((0, y + 30, W, y + 130), fill=(220, 20, 20)); d.text((40, y + 42), 'BREAKING!!!', font=F(FB, 70), fill=(255, 255, 255))
cx = W // 2; base_y = y + ih - 60
d.rectangle((cx - 45, base_y - 260, cx + 45, base_y), fill=(240, 236, 220))
d.ellipse((cx - 28, base_y - 360, cx + 28, base_y - 262), fill=(255, 190, 40)); d.ellipse((cx - 14, base_y - 330, cx + 14, base_y - 275), fill=(255, 245, 190))
d.line((cx, base_y - 262, cx, base_y - 250), fill=(30, 30, 30), width=5)
for qx in (150, W - 240): d.text((qx, y + 230), '?!', font=F(FB, 200), fill=(255, 210, 0))
y += ih + 20
for i, c in enumerate(((240, 180, 0), (60, 120, 230), (230, 60, 60))):
    d.ellipse((40 + 40 * i, y, 92 + 40 * i, y + 52), fill=c, outline=(255, 255, 255), width=4)
d.text((180, y + 4), '25K', font=F(FR, 40), fill=(90, 90, 90)); d.text((470, y + 4), '96K shares', font=F(FR, 40), fill=(90, 90, 90))
y += 80; d.line((40, y, W - 40, y), fill=(220, 222, 226), width=3); y += 20
for i, t in enumerate(('Like', 'Comment', 'Share')): d.text((70 + 320 * i, y), t, font=F(FB, 40), fill=(100, 104, 112))
d.rectangle((0, H - 120, W, H), fill=(255, 255, 255))
for i in range(5): d.rounded_rectangle((70 + 190 * i, H - 90, 130 + 190 * i, H - 40), 10, fill=(150, 156, 166) if i else (59, 89, 152))
im.save(os.path.join(OUT, 'mom_post.png'))

# ---------------------------------------------------------------- Doug's feed (dark mode, nothing readable)
im = Image.new('RGB', (W, H), (24, 25, 28)); d = ImageDraw.Draw(im)
d.text((40, 16), '9:41', font=F(FB, 36), fill=(230, 230, 230))
y = 110
for k in range(4):
    d.ellipse((40, y, 130, y + 90), fill=(70, 74, 82)); d.rounded_rectangle((150, y + 10, 520, y + 40), 12, fill=(70, 74, 82))
    d.rounded_rectangle((150, y + 55, 380, y + 78), 10, fill=(52, 55, 62))
    y += 120
    for w_ in (900, 760): d.rounded_rectangle((40, y, 40 + w_, y + 30), 12, fill=(60, 63, 70)); y += 50
    d.rectangle((0, y, W, y + 220), fill=((60, 90, 120), (110, 80, 60), (70, 110, 80), (100, 70, 110))[k]); y += 260
im.save(os.path.join(OUT, 'doug_feed.png'))
print('screens ok')
