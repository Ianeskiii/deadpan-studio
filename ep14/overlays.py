"""Burned-in title caption (Permanent Marker, ../ep12/marker.ttf)."""
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920
f = ImageFont.truetype('../ep12/marker.ttf', 70)
img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); y = 230
for ln in ['When you accidentally', 'open the front camera']:
    w = d.textlength(ln, font=f); d.text(((W - w) / 2, y), ln, font=f, fill='white', stroke_width=7, stroke_fill='black'); y += 92
img.save('caption.png'); print('caption ok')
