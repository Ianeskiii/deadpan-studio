from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 64)
for name, txt in (('sub_demand', 'Hey! Gimme the bag!'), ('sub_giveup', 'Ugh... forget it.')):
    img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    w = d.textlength(txt, font=f); d.text(((1080 - w) / 2, 1250), txt, font=f, fill='white', stroke_width=7, stroke_fill='black')
    img.save(name + '.png')
print('ok')
