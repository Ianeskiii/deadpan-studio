from PIL import Image, ImageDraw, ImageFont
B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; Rg = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def F(p, s): return ImageFont.truetype(p, s)
W, H = 600, 1100
def chat(msgs, name):
    im = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((40, 30), '9:41', font=F(B, 30), fill='white')
    d.rectangle((0, 90, W, 230), fill=(22, 22, 24))
    d.ellipse((W//2-40, 100, W//2+40, 180), fill=(43, 181, 168))
    d.text((W//2, 135), 'T', font=F(B, 44), fill='white', anchor='mm')
    d.text((W//2, 205), 'Tina ♥', font=F(B, 28), fill='white', anchor='mm')
    y = 260
    for who, text, stamp in msgs:
        if stamp:
            d.text((W//2, y), stamp, font=F(Rg, 22), fill=(140, 140, 146), anchor='mm'); y += 36
        f = F(Rg, 33) if who != 'big' else F(B, 40)
        tw = d.textlength(text, font=f); bw, bh = tw + 46, 64
        if who == 'me':
            x1 = W - 30; d.rounded_rectangle((x1 - bw, y, x1, y + bh), 34, fill=(10, 132, 255))
            d.text((x1 - bw + 25, y + bh/2), text, font=f, fill='white', anchor='lm')
        else:
            x0 = 30; d.rounded_rectangle((x0, y, x0 + bw, y + bh), 34, fill=(58, 58, 60))
            d.text((x0 + 25, y + bh/2), text, font=f, fill='white', anchor='lm')
        y += bh + 12
    d.rounded_rectangle((30, H - 110, W - 30, H - 40), 35, outline=(70, 70, 74), width=3)
    d.text((60, H - 75), 'Message', font=F(Rg, 28), fill=(110, 110, 116), anchor='lm')
    im.save(f'tex/{name}.png')
A = [('me', 'here! where r u?', 'Today 4:00 PM')]
chat(A, 'chat_a')
chat(A + [('them', 'omw!! 5 min', None)], 'chat_b')
C = A + [('them', 'omw!! 5 min', None), ('them', 'Almost there, babe', '4:03 PM'), ('me', '??', '6:30 PM'), ('me', 'the movie started', '7:05 PM')]
chat(C, 'chat_c')
chat(C + [('them', 'ok leaving now!!', '7:12 PM')], 'chat_d')
def poster(title, sub, c1, c2, name):
    im = Image.new('RGB', (400, 600), c1); d = ImageDraw.Draw(im)
    for i in range(0, 600, 1): d.line((0, i, 400, i), fill=tuple(int(a + (b - a) * i / 600) for a, b in zip(c1, c2)))
    d.ellipse((90, 140, 310, 360), fill=(255, 220, 120))
    d.rectangle((140, 260, 260, 520), fill=(240, 120, 80)); d.ellipse((140, 200, 260, 320), fill=(240, 120, 80))
    for k, ln in enumerate(title): d.text((200, 50 + k * 50), ln, font=F(B, 44), fill='white', anchor='mm', stroke_width=3, stroke_fill='black')
    d.text((200, 560), sub, font=F(B, 22), fill='white', anchor='mm')
    im.save(f'tex/{name}.png')
poster(['ATTACK OF', 'THE NOODLES'], 'NOW SHOWING', (30, 20, 70), (200, 60, 90), 'poster1')
poster(['LOVE IN', 'TUBE TOWN'], 'COMING SOON', (240, 130, 160), (90, 40, 120), 'poster2')
print('ok')
