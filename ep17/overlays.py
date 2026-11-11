"""Captions in the house style (DejaVu Sans Bold, white, black outline; title at y=260, line step int(66*1.27)):
  title.png    WHEN YOU FINISH WORK AT 4:59 PM   (the opening, 0-3.3 s)
  unmamba.png  UNMAMBA.                          (small, from UNMAMBA to the cut to black)"""
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920; FP = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def draw_lines(img, lines, size, y, stroke):
    d = ImageDraw.Draw(img); f = ImageFont.truetype(FP, size); step = int(size * 1.27)
    for ln in lines:
        w = d.textlength(ln, font=f); d.text(((W - w) / 2, y), ln, font=f, fill='white', stroke_width=stroke, stroke_fill='black'); y += step
t = Image.new('RGBA', (W, H), (0, 0, 0, 0)); draw_lines(t, ['WHEN YOU FINISH WORK', 'AT 4:59 PM'], 66, 260, 7); t.save('title.png')
u = Image.new('RGBA', (W, H), (0, 0, 0, 0)); draw_lines(u, ['UNMAMBA.'], 54, 300, 6); u.save('unmamba.png')
print('captions ok')
