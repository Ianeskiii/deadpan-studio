"""Title (house typography: Barista ep12/overlays13.py + Bathroom ep9 - DejaVu Sans Bold 66, white, 7 px black outline,
y=260, line step int(66*1.27)) and the time-skip card text."""
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920; SIZE = 66; STEP = int(SIZE * 1.27); MAXW = 940
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', SIZE)
def wrap(text, font, maxw):
    d = ImageDraw.Draw(Image.new('RGB', (1, 1))); lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
def draw_lines(img, lines, font, y, step, stroke):
    d = ImageDraw.Draw(img)
    for ln in lines:
        w = d.textlength(ln, font=font); d.text(((W - w) / 2, y), ln, font=font, fill='white', stroke_width=stroke, stroke_fill='black'); y += step
TITLE = wrap('When you finally have free time to play games', F, MAXW)
cap = Image.new('RGBA', (W, H), (0, 0, 0, 0)); draw_lines(cap, TITLE, F, 260, STEP, 7); cap.save('caption.png')
# time skip: same family/weight/outline, a bit bigger, centred on the black card
F2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 74)
card = Image.new('RGBA', (W, H), (0, 0, 0, 0)); draw_lines(card, ['15 MINUTES LATER...'], F2, H // 2 - 50, 100, 8); card.save('later.png')
print('title lines:', TITLE)
