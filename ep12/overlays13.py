from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def card(name, lines, y, size):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img); f = ImageFont.truetype(F, size)
    for ln in lines:
        w = d.textlength(ln, font=f); d.text(((W - w) / 2, y), ln, font=f, fill='white', stroke_width=7, stroke_fill='black'); y += int(size * 1.27)
    img.save('ov2/' + name + '.png')
card('caption', ['When the barista still', 'gets your name wrong'], 260, 66)
SUBS = {'b1': 'Name for the order?', 'd1': 'Doug.', 'b2': 'How do you spell that?', 'b3': 'Perfect. Got it!',
        'b4': 'Coffee for... DOG!', 'd3': 'I literally spelled it.', 'b5': 'Yeah?'}
for k, v in SUBS.items(): card('s_' + k, [v], 1330, 60)
for i, t in enumerate(['D...', 'D... O...', 'D... O... U...', 'D... O... U... G.']): card(f's_d2_{i}', [t], 1330, 64)
print('ok')
