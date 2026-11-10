"""Burned-in title + dialogue subtitles, in the house style of the approved episodes (ep12, ep14):
DejaVu Sans Bold, white with a 7 px black outline, centred.  Writes ov/caption.png and ov/s_<line>.png (1080x1920)."""
import os
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
os.makedirs('ov', exist_ok=True)
def card(name, lines, y, size):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); f = ImageFont.truetype(F, size)
    for ln in lines:
        w = d.textlength(ln, font=f); d.text(((W - w) / 2, y), ln, font=f, fill='white', stroke_width=7, stroke_fill='black'); y += int(size * 1.27)
    img.save(os.path.join('ov', name + '.png'))
card('caption', ['When someone is lying', 'straight to your face'], 260, 66)
SUBS = {'d1': ['Did you eat my cake?'], 'g1': ['What? No.'], 'g2': ["I haven't even", 'seen your cake.'],
        'g3': ['Why are you looking', 'at me like that?'], 'g4': ["...That's not mine."]}
for k, v in SUBS.items(): card('s_' + k, v, 1390, 60)
print('overlays ok')
