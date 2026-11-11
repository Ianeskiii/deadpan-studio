"""Shots -> one mp4 per part (title burned in), the black "15 MINUTES LATER..." card, fades into/out of the card,
concat (-c copy), mux audio.wav."""
import json, subprocess, os
B = json.load(open('beats.json')); N = B['N']; SH = B['SH']
PARTS = [('A', 1), ('B', 1), ('C', 2), ('CARD', 0), ('E', 2), ('F', 2), ('G', 2), ('BLACK', 0)]
os.makedirs('parts', exist_ok=True); lst = []
FADE = 6 / 30
def run(a): subprocess.run(['ffmpeg', '-v', 'error', '-y'] + a, check=True)
ENC = ['-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30']
for name, step in PARTS:
    out = f'parts/{name}.mp4'
    if name == 'CARD':
        a, b = B['CARD']; dur = (b - a + 1) / 30
        run(['-f', 'lavfi', '-i', f'color=c=black:s=1080x1920:r=30', '-loop', '1', '-i', 'caption.png', '-loop', '1', '-i', 'later.png', '-filter_complex',
             f"[0][1]overlay[v];[2]format=rgba,fade=t=in:st=0.1:d=0.25:alpha=1,fade=t=out:st={dur - 0.3:.3f}:d=0.25:alpha=1[l];[v][l]overlay=shortest=1,format=yuv420p[o]",
             '-map', '[o]', '-t', f'{dur:.4f}'] + ENC + [out])
    elif name == 'BLACK':
        dur = (N - B['G_BLACK'] + 1) / 30
        run(['-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:r=30', '-t', f'{dur:.4f}'] + ENC + [out])
    else:
        a, b = SH[name]; dur = (b - a + 1) / 30
        fx = ''
        if name == 'C': fx = f',fade=t=out:st={dur - FADE:.3f}:d={FADE:.3f}'
        if name == 'E': fx = f',fade=t=in:st=0:d={FADE:.3f}'
        run(['-framerate', str(30 // step), '-pattern_type', 'glob', '-i', f'frames/{name}/*.png', '-i', 'caption.png', '-filter_complex',
             f'[0]scale=1080:1920:flags=lanczos,fps=30{fx}[v];[v][1]overlay,format=yuv420p[o]', '-map', '[o]', '-t', f'{dur:.4f}'] + ENC + [out])
    lst.append(f"file '{name}.mp4'")
open('parts/list.txt', 'w').write('\n'.join(lst) + '\n')
run(['-f', 'concat', '-safe', '0', '-i', 'parts/list.txt', '-c', 'copy', 'parts/video.mp4'])
run(['-i', 'parts/video.mp4', '-i', 'audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
     '-movflags', '+faststart', 'TubeTown_Free_Time_Games.mp4'])
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name', '-of', 'compact',
                      'TubeTown_Free_Time_Games.mp4'], capture_output=True, text=True).stdout)
