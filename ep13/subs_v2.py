"""V2: big English subtitles at the bottom of the video (house style: DejaVu Sans Bold, white, 7 px black outline),
burned over the v1 picture, with the shouted V2 voices (anime_audio_v2.wav).
usage: python3 subs_v2.py <v1.mp4> <out.mp4>"""
import json, os, sys, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920; SIZE = 60; Y_BOTTOM = 1700          # last text line ends here: clear of the Shorts UI at the very bottom
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', SIZE)
T = json.load(open('vo/timing.json')); L = T['lines']
os.makedirs('ov2', exist_ok=True)
src, out = sys.argv[1], sys.argv[2]
inputs, chain, last = [], [], '0:v'
for i, l in enumerate(L):
    rows = textwrap.wrap(l['sub'], 20)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    y = Y_BOTTOM - len(rows) * int(SIZE * 1.27)
    for r in rows:
        w = d.textlength(r, font=F); d.text(((W - w) / 2, y), r, font=F, fill='white', stroke_width=7, stroke_fill='black'); y += int(SIZE * 1.27)
    p = f'ov2/s{i:02d}.png'; img.save(p)
    t0 = l['t']
    t1 = min(L[i + 1]['t'], l['t'] + l['d'] + 0.6) if i + 1 < len(L) else l['t'] + l['d'] + 0.35   # gone before the dead silence
    inputs += ['-i', p]
    chain.append(f"[{last}][{i + 2}:v]overlay=0:0:enable='between(t,{t0:.3f},{t1 - 0.001:.3f})'[v{i}]"); last = f'v{i}'
    print(f'{t0:6.2f}-{t1:6.2f}  {" / ".join(rows)}')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', 'anime_audio_v2.wav', *inputs, '-filter_complex', ';'.join(chain),
                '-map', f'[{last}]', '-map', '1:a', '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], check=True)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
