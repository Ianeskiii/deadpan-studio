"""Burned-in title caption: the house style of the approved episodes (ep12 barista, ep9-ep11):
DejaVu Sans Bold, white with a 7 px black outline, centred, two lines (v2; v1 used Permanent Marker)."""
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 66)
img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); y = 260
for ln in ['When you accidentally', 'open the front camera']:
    w = d.textlength(ln, font=f); d.text(((W - w) / 2, y), ln, font=f, fill='white', stroke_width=7, stroke_fill='black'); y += int(66 * 1.27)   # 83, exactly as ep12/overlays13.py (barista)
img.save('caption.png'); print('caption ok')
