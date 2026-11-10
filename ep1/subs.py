from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 62)
for name, lines in (('sub_tina', ['Why not just', 'let it beep?']), ('sub_doug', ['Because it doesn’t', 'get to win.'])):
    img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(img); y = 1180
    for ln in lines:
        w = d.textlength(ln, font=f); d.text(((1080 - w) / 2, y), ln, font=f, fill='white', stroke_width=7, stroke_fill='black'); y += 78
    img.save(name + '.png')
print('subs ok')
