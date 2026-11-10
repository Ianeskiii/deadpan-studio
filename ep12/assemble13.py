"""v2: encode each shot (frames + caption + subtitles), concat -c copy, mux audio."""
import json, subprocess, os
T = json.load(open('vo2/timing.json')); N = T['N']
B3E, B4E = T['b3']['fe'], T['b4']['fe']
TOMACH1 = B3E + 22 + 16; SHD = (TOMACH1 + 1, TOMACH1 + 33)
SH = {'A': (1, 180), 'B': (181, 300), 'C': (301, TOMACH1), 'D': SHD, 'E': (SHD[1] + 1, T['b4']['fs'] - 1),
      'F': (T['b4']['fs'], B4E), 'G': (B4E + 1, B4E + 28), 'H': (B4E + 29, N)}
STEP = {k: (1 if k in ('D', 'G') else 2) for k in SH}
fr = lambda f: (f - 1) / 30
subs = []
for name, v in T.items():
    if not isinstance(v, dict): continue
    if name == 'd2':
        w = v['words']
        for i in range(4):
            on = fr(w[i]) - 0.05; off = fr(w[i + 1]) - 0.05 if i < 3 else v['e'] + 0.4
            subs.append((f'ov2/s_d2_{i}.png', on, off))
    else:
        off = v['e'] + (0.0 if name == 'b4' else 0.35)
        subs.append((f'ov2/s_{name}.png', v['s'] - 0.08, off))
os.makedirs('parts2', exist_ok=True); lst = []
for s, (a, b) in SH.items():
    t0, t1 = fr(a), fr(b + 1); dur = t1 - t0
    ins = ['-framerate', str(30 // STEP[s]), '-pattern_type', 'glob', '-i', f'frames2/{s}/*.png', '-i', 'ov2/caption.png']
    fc = '[0]scale=1080:1920:flags=lanczos,fps=30[v0];[v0][1]overlay[v1]'; last = 'v1'; k = 2
    for png, on, off in subs:
        on, off = max(on, t0), min(off, t1)
        if off <= on: continue
        ins += ['-i', png]; fc += f";[{last}][{k}]overlay=enable='between(t,{on - t0:.3f},{off - t0:.3f})'[v{k}]"; last = f'v{k}'; k += 1
    fc += f';[{last}]format=yuv420p[out]'
    tmp = f'parts2/tmp_{s}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[out]', '-t', f'{dur:.4f}',
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30', tmp], check=True)
    os.replace(tmp, f'parts2/{s}.mp4'); lst.append(f"file '{s}.mp4'")
open('parts2/list.txt', 'w').write('\n'.join(lst) + '\n')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'parts2/list.txt', '-c', 'copy', 'parts2/video.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'parts2/video.mp4', '-i', 'ep12_audio_v2.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k', '-shortest', 'TubeTown_Barista_Name_v2.mp4'], check=True)
print(SH)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name,r_frame_rate', '-of', 'compact', 'TubeTown_Barista_Name_v2.mp4'], capture_output=True, text=True).stdout)
