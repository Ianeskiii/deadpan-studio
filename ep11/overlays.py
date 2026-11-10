from PIL import Image, ImageDraw, ImageFont
B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
f = ImageFont.truetype(B, 58); img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(img); y = 300
for ln in ('Getting robbed but your', 'favorite music is still playing'):
    w = d.textlength(ln, font=f); d.text(((1080 - w) / 2, y), ln, font=f, fill='white', stroke_width=7, stroke_fill='black'); y += 74
img.save('caption.png'); print('ok')
