from PIL import Image, ImageDraw, ImageFont
B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def card(lines, y, size, name, fill='white', step=None):
    f = ImageFont.truetype(B, size); img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for ln in lines:
        w = d.textlength(ln, font=f); d.text(((1080 - w) / 2, y), ln, font=f, fill=fill, stroke_width=max(6, size // 9), stroke_fill='black'); y += step or int(size * 1.27)
    img.save(name + '.png')
card(['That one friend who’s', '“five minutes away”'], 300, 64, 'caption')
card(['Almost there, babe.'], 1200, 62, 'sub_tina')
card(['3 hours later...'], 860, 96, 'card_3h', fill=(255, 214, 64))
print('ok')
