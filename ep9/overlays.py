from PIL import Image, ImageDraw, ImageFont
B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def card(lines, y, size, name, fill='white'):
    f = ImageFont.truetype(B, size); img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for ln in lines:
        w = d.textlength(ln, font=f); d.text(((1080 - w) / 2, y), ln, font=f, fill=fill, stroke_width=max(6, size // 9), stroke_fill='black'); y += int(size * 1.27)
    img.save(name + '.png')
card(['When you go to the bathroom', 'and forget your phone'], 300, 60, 'caption')
card(['Lather... rinse... repeat.'], 1250, 62, 'sub1')
card(['...How many times?'], 1250, 66, 'sub2')
print('ok')
