from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
for name, lines in (('s_g1', ['Hey. Hey! Gimme the bag.']), ('s_g2', ['Come ON—']), ('s_g3', ['Let... GO!']),
                    ('s_g4', ['Ugh— you know what?', 'Forget it.']), ('s_d1', ['...You good?'])):
    img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(img); y = 1300
    for ln in lines:
        w = d.textlength(ln, font=f); d.text(((1080 - w) / 2, y), ln, font=f, fill='white', stroke_width=7, stroke_fill='black'); y += 76
    img.save(name + '.png')
print('ok')
