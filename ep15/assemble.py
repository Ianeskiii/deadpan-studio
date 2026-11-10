"""Encode each shot (frames + title + subtitles), add the black tail, concat -c copy, mux the audio."""
import json, subprocess, os
T = json.load(open('vo/timing.json')); B = json.load(open('beats.json')); N = B['N']
SH = {k: tuple(v) for k, v in B['SHOTS'].items()}
STEP = {k: (1 if k in ('A', 'F') else 2) for k in SH}
OUT = 'TubeTown_Lying_To_Your_Face.mp4'
fr = lambda f: (f - 1) / 30
subs = [(f'ov/s_{k}.png', v['s'] - 0.08, v['e'] + 0.35) for k, v in T.items() if isinstance(v, dict)]
os.makedirs('parts', exist_ok=True); lst = []
for s, (a, b) in SH.items():
    t0, t1 = fr(a), fr(b + 1); dur = t1 - t0
    ins = ['-framerate', str(30 // STEP[s]), '-pattern_type', 'glob', '-i', f'frames/{s}/*.png', '-i', 'ov/caption.png']
    fc = '[0]scale=1080:1920:flags=lanczos,fps=30[v0];[v0][1]overlay[v1]'; last = 'v1'; k = 2
    for png, on, off in subs:
        on, off = max(on, t0), min(off, t1)
        if off <= on: continue
        ins += ['-i', png]; fc += f";[{last}][{k}]overlay=enable='between(t,{on - t0:.3f},{off - t0:.3f})'[v{k}]"; last = f'v{k}'; k += 1
    fc += f';[{last}]format=yuv420p[out]'
    tmp = f'parts/tmp_{s}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[out]', '-t', f'{dur:.4f}',
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30', tmp], check=True)
    os.replace(tmp, f'parts/{s}.mp4'); lst.append(f"file '{s}.mp4'")
blk = (B['BLACK'][1] - B['BLACK'][0] + 1) / 30
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1080x1920:r=30', '-t', f'{blk:.4f}', '-c:v', 'libx264', '-crf', '18',
                '-preset', 'veryfast', '-pix_fmt', 'yuv420p', 'parts/tmp_black.mp4'], check=True)
os.replace('parts/tmp_black.mp4', 'parts/black.mp4'); lst.append("file 'black.mp4'")
open('parts/list.txt', 'w').write('\n'.join(lst) + '\n')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'parts/list.txt', '-c', 'copy', 'parts/video.mp4'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'parts/video.mp4', '-i', 'audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k', '-shortest', OUT], check=True)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,codec_name,r_frame_rate', '-of', 'compact', OUT],
                     capture_output=True, text=True).stdout)
