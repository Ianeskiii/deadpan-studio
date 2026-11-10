import json, subprocess, os
B = json.load(open('beats.json')); N = B['N']; FB = B['F_BLACK']
PARTS = [('A', 1, 50, 2), ('B', 51, 110, 2), ('C', 111, 180, 2), ('D', 181, 300, 1), ('E', 301, 335, 2), ('F1', 336, 397, 2), ('F2', 398, 440, 1), ('F3', 441, FB - 1, 2)]
os.makedirs('parts', exist_ok=True); lst = []
for name, a, b, step in PARTS:
    dur = (b - a + 1) / 30
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(30 // step), '-pattern_type', 'glob', '-i', f'frames/{name}/*.png', '-i', 'caption.png',
                    '-filter_complex', '[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay,format=yuv420p[o]', '-map', '[o]', '-t', f'{dur:.4f}',
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-r', '30', f'parts/tmp_{name}.mp4'], check=True)
    os.replace(f'parts/tmp_{name}.mp4', f'parts/{name}.mp4'); lst.append(f"file '{name}.mp4'")
blk = (N - FB + 1) / 30
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:r=30', '-t', f'{blk:.4f}', '-c:v', 'libx264', '-crf', '18',
                '-preset', 'veryfast', '-pix_fmt', 'yuv420p', 'parts/tmp_black.mp4'], check=True)
os.replace('parts/tmp_black.mp4', 'parts/black.mp4'); lst.append("file 'black.mp4'")
open('parts/list.txt', 'w').write('\n'.join(lst) + '\n')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'parts/list.txt', '-c', 'copy', 'parts/video.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'parts/video.mp4', '-i', 'audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                '-shortest', 'TubeTown_Front_Camera.mp4'], check=True)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name', '-of', 'compact', 'TubeTown_Front_Camera.mp4'], capture_output=True, text=True).stdout)
