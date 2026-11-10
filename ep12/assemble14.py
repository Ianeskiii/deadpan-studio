"""v2: encode each shot (frames + caption + subtitles), concat -c copy, mux audio."""
import json, subprocess, os
T = json.load(open('vo2/timing14.json')); N = T['N']
SH = {k: tuple(v) for k, v in json.load(open('beats14.json'))['SHOTS'].items()}
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
os.makedirs('parts3', exist_ok=True); lst = []
for s, (a, b) in SH.items():
    t0, t1 = fr(a), fr(b + 1); dur = t1 - t0
    ins = ['-framerate', str(30 // STEP[s]), '-pattern_type', 'glob', '-i', f'frames3/{s}/*.png', '-i', 'ov2/caption.png']
    fc = '[0]scale=1080:1920:flags=lanczos,fps=30[v0];[v0][1]overlay[v1]'; last = 'v1'; k = 2
    for png, on, off in subs:
        on, off = max(on, t0), min(off, t1)
        if off <= on: continue
        ins += ['-i', png]; fc += f";[{last}][{k}]overlay=enable='between(t,{on - t0:.3f},{off - t0:.3f})'[v{k}]"; last = f'v{k}'; k += 1
    fc += f';[{last}]format=yuv420p[out]'
    tmp = f'parts3/tmp_{s}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[out]', '-t', f'{dur:.4f}',
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30', tmp], check=True)
    os.replace(tmp, f'parts3/{s}.mp4'); lst.append(f"file '{s}.mp4'")
open('parts3/list.txt', 'w').write('\n'.join(lst) + '\n')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'parts3/list.txt', '-c', 'copy', 'parts3/video.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'parts3/video.mp4', '-i', 'ep12_audio_v3.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k', '-shortest', 'TubeTown_Barista_Name_v3.mp4'], check=True)
print(SH)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name,r_frame_rate', '-of', 'compact', 'TubeTown_Barista_Name_v3.mp4'], capture_output=True, text=True).stdout)
