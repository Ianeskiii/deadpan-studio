"""Encode each shot (frames + caption + subtitles), concat with -c copy, mux audio."""
import json, subprocess, os
T = json.load(open('vo/timing.json')); N = T['N']
SH = {'A': (1, 178), 'B': (179, 262), 'C': (263, 401), 'D': (402, 424), 'E': (425, 531), 'F': (532, N)}
STEP = {k: (1 if k == 'D' else 2) for k in SH}
fr = lambda f: (f - 1) / 30
os.makedirs('parts', exist_ok=True); lst = []
for s, (a, b) in SH.items():
    t0, t1 = fr(a), fr(b + 1); dur = t1 - t0
    ins = ['-framerate', str(30 // STEP[s]), '-pattern_type', 'glob', '-i', f'frames/{s}/*.png', '-i', 'caption.png']
    fc = '[0]scale=1080:1920:flags=lanczos,fps=30[v0];[v0][1]overlay[v1]'; last = 'v1'; k = 2
    for name, v in T.items():
        if not isinstance(v, dict): continue
        on, off = max(v['s'] - 0.08, t0), min(v['e'] + 0.35, t1)
        if off <= on: continue
        ins += ['-i', f's_{name}.png']
        fc += f";[{last}][{k}]overlay=enable='between(t,{on - t0:.3f},{off - t0:.3f})'[v{k}]"; last = f'v{k}'; k += 1
    fc += f';[{last}]format=yuv420p[out]'
    tmp = f'parts/tmp_{s}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[out]', '-t', f'{dur:.4f}',
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30', tmp], check=True)
    os.replace(tmp, f'parts/{s}.mp4'); lst.append(f"file '{s}.mp4'")
open('parts/list.txt', 'w').write('\n'.join(lst) + '\n')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'parts/list.txt', '-c', 'copy', 'parts/video.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'parts/video.mp4', '-i', 'ep12_audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k', '-shortest', 'TubeTown_Barista_Name.mp4'], check=True)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name', '-of', 'compact', 'TubeTown_Barista_Name.mp4'], capture_output=True, text=True).stdout)
