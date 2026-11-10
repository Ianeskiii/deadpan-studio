from PIL import Image, ImageDraw, ImageFont
B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; Rg = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def F(p, s): return ImageFont.truetype(p, s)
def wrap(d, text, font, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines
# back label
W, H = 520, 1150
im = Image.new('RGB', (W, H), (246, 251, 253)); d = ImageDraw.Draw(im)
d.rectangle((0, 0, W, 110), fill=(38, 166, 201)); d.text((W//2, 55), 'SUDZ', font=F(B, 70), fill='white', anchor='mm')
y = 140
def block(title, body, size=30, gap=12):
    global y
    d.text((30, y), title, font=F(B, 34), fill=(20, 40, 60)); y += 48
    for ln in wrap(d, body, F(Rg, size), W - 60):
        d.text((30, y), ln, font=F(Rg, size), fill=(40, 50, 60)); y += size + 8
    y += gap + 14
block('INGREDIENTS:', 'Aqua (Water), Sodium Laureth Sulfate, Cocamidopropyl Betaine, Glycerin, Sodium Chloride, Citric Acid, Fragrance (Parfum), Very Small Bubbles.', 28)
block('WARNING:', 'For external use only. Avoid contact with eyes. Do not drink. We mean it.', 28)
d.text((30, y), 'DIRECTIONS:', font=F(B, 34), fill=(20, 40, 60)); y += 50
d.text((30, y), 'Apply to wet hair.', font=F(Rg, 30), fill=(40, 50, 60)); y += 50
d.rounded_rectangle((20, y - 6, W - 20, y + 66), 14, fill=(255, 236, 140))
d.text((W//2, y + 30), 'Lather. Rinse. Repeat.', font=F(B, 38), fill=(20, 30, 40), anchor='mm'); y += 100
d.text((30, y), '12 FL OZ (355 mL)', font=F(B, 26), fill=(40, 50, 60)); y += 38
d.text((30, y), 'Made in Tube Town', font=F(Rg, 24), fill=(90, 100, 110)); y += 50
for i in range(46):
    if i % 3 != 1: d.rectangle((40 + i * 9, y, 40 + i * 9 + (5 if i % 4 else 3), y + 70), fill='black')
im.save('tex/label_back.png'); print('back text ends at y', y + 70)
# front label
W2, H2 = 520, 900
im = Image.new('RGB', (W2, H2), (38, 166, 201)); d = ImageDraw.Draw(im)
for cx, cy, r in ((90, 120, 40), (420, 160, 55), (130, 700, 60), (400, 760, 35), (300, 90, 25), (70, 420, 30), (460, 480, 28)):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline='white', width=6)
d.text((W2//2, 360), 'SUDZ', font=F(B, 150), fill='white', anchor='mm', stroke_width=6, stroke_fill=(20, 90, 130))
d.text((W2//2, 500), 'SHAMPOO', font=F(B, 56), fill=(255, 236, 140), anchor='mm')
d.text((W2//2, 570), 'Extra Bubbly', font=F(Rg, 40), fill='white', anchor='mm')
im.save('tex/label_front.png'); print('ok')
