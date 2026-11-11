"""Shots -> one mp4 per part with captions burned in (title over A/I/B; UNMAMBA. from its beat to the cut), black tail,
concat (-c copy), mux audio.wav -> deadpan_doug_459pm_mamba_out.mp4"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from beats import *
PARTS = [('A', 1), ('I', 2), ('B', 1), ('S', 2), ('C', 2), ('D', 2), ('E', 2), ('BLACK', 0)]
OUT = 'deadpan_doug_459pm_mamba_out.mp4'
os.makedirs('parts', exist_ok=True); lst = []
def run(a): subprocess.run(['ffmpeg', '-v', 'error', '-y'] + a, check=True)
ENC = ['-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30']
TITLE_END = 99                       # title off just after "Mamba out." (3.27 s)
for name, step in PARTS:
    out = f'parts/{name}.mp4'
    if name == 'BLACK':
        run(['-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:r=30', '-t', f'{(N - BLACK + 1) / 30:.4f}'] + ENC + [out])
    else:
        a, b = SH[name]; dur = (b - a + 1) / 30
        ov = []
        if a < TITLE_END: ov.append(('title.png', 0, (min(b, TITLE_END - 1) - a + 1) / 30))
        if b >= UNMAMBA: ov.append(('unmamba.png', max(0, UNMAMBA - a) / 30, dur))
        inputs = ['-framerate', str(30 // step), '-pattern_type', 'glob', '-i', f'frames/{name}/*.png']
        fc = '[0]scale=1080:1920:flags=lanczos,fps=30[v0]'; last = 'v0'
        for i, (png, t0, t1) in enumerate(ov):
            inputs += ['-loop', '1', '-i', png]
            fc += f";[{last}][{i + 1}]overlay=enable='between(t,{t0:.3f},{t1 - 0.001:.3f})'[v{i + 1}]"; last = f'v{i + 1}'
        fc += f';[{last}]format=yuv420p[o]'
        run(inputs + ['-filter_complex', fc, '-map', '[o]', '-t', f'{dur:.4f}'] + ENC + [out])
    lst.append(f"file '{name}.mp4'")
open('parts/list.txt', 'w').write('\n'.join(lst) + '\n')
run(['-f', 'concat', '-safe', '0', '-i', 'parts/list.txt', '-c', 'copy', 'parts/video.mp4'])
run(['-i', 'parts/video.mp4', '-i', 'audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
     '-movflags', '+faststart', OUT])
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name', '-of', 'compact', OUT],
                     capture_output=True, text=True).stdout)
