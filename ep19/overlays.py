"""Caption in the house style used since ep13 (DejaVu Sans Bold, white, black outline, top centre, two lines):
  title.png   "Mama mong mahilig / maniwala sa fake news"   (the whole skit, off on the hard cut to black)"""
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920; FP = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def draw_lines(img, lines, size, y, stroke):
    d = ImageDraw.Draw(img); f = ImageFont.truetype(FP, size); step = int(size * 1.27)
    for ln in lines:
        w = d.textlength(ln, font=f); d.text(((W - w) / 2, y), ln, font=f, fill='white', stroke_width=stroke, stroke_fill='black'); y += step
t = Image.new('RGBA', (W, H), (0, 0, 0, 0)); draw_lines(t, ['Mama mong mahilig', 'maniwala sa fake news'], 66, 250, 7); t.save('title.png')
print('captions ok')
