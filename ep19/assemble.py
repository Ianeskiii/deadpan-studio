"""Shots -> one mp4 per part with the caption burned in over every shot, black tail, concat (-c copy), mux audio.wav
-> deadpan_doug_mama_fake_news.mp4"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from beats import *
PARTS = ['A', 'B', 'C', 'O', 'D', 'E', 'F', 'BLACK']
OUT = 'deadpan_doug_mama_fake_news.mp4'
os.makedirs('parts', exist_ok=True); lst = []
def run(a): subprocess.run(['ffmpeg', '-v', 'error', '-y'] + a, check=True)
ENC = ['-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30']
for name in PARTS:
    out = f'parts/{name}.mp4'
    if name == 'BLACK':
        run(['-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:r=30', '-t', f'{(N - BLACK + 1) / 30:.4f}'] + ENC + [out])
    else:
        a, b = SH[name]; dur = (b - a + 1) / 30; step = STEP[name]
        inputs = ['-framerate', str(30 // step), '-pattern_type', 'glob', '-i', f'frames/{name}/*.png', '-loop', '1', '-i', 'title.png']
        fc = '[0]scale=1080:1920:flags=lanczos,fps=30[v0];[v0][1]overlay[v1];[v1]format=yuv420p[o]'
        run(inputs + ['-filter_complex', fc, '-map', '[o]', '-t', f'{dur:.4f}'] + ENC + [out])
    lst.append(f"file '{name}.mp4'")
open('parts/list.txt', 'w').write('\n'.join(lst) + '\n')
run(['-f', 'concat', '-safe', '0', '-i', 'parts/list.txt', '-c', 'copy', 'parts/video.mp4'])
run(['-i', 'parts/video.mp4', '-i', 'audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
     '-movflags', '+faststart', OUT])
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name', '-of', 'compact', OUT],
                     capture_output=True, text=True).stdout)
