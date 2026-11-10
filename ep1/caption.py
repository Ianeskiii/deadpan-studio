from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920
img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 66)
lines = ['When the microwave', 'says 2 minutes']
y = 300
for ln in lines:
    w = d.textlength(ln, font=f)
    d.text(((W - w) / 2, y), ln, font=f, fill='white', stroke_width=7, stroke_fill='black')
    y += 84
img.save('caption.png'); print('caption ok')
