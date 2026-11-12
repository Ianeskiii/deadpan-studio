"""Encode ep20: frames/S/*.png -> 1080x1920 30 fps with the caption, plus audio.
usage: python3 assemble.py [--step K] [--audio supplied.(mp3|wav|m4a|mp4)] [--offset SECONDS] [--out NAME.mp4]
Audio: the owner's Jeolee/PBB clip is used exactly as supplied (no pitch/speed change, no added music or dialogue).
--offset shifts where in the clip the video starts (default 0). Without --audio the video gets a silent track."""
import subprocess, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
a = sys.argv[1:]
def opt(k, d): return type(d)(a[a.index(k) + 1]) if k in a else d
STEP = opt('--step', 1); AUDIO = opt('--audio', ''); OFF = opt('--offset', 0.0)
OUT = opt('--out', 'TubeTown_Jeolee_Bedtime_v1.mp4')
DUR = 10.0
v = ['-framerate', str(30 // STEP), '-pattern_type', 'glob', '-i', 'frames/S/*.png', '-i', 'caption.png']
vf = '[0]scale=1080:1920:flags=lanczos,fps=30[v];[v][1]overlay,format=yuv420p[vo]'
if AUDIO:
    aud = ['-ss', str(OFF), '-t', str(DUR), '-i', AUDIO]
    af = ';[2:a]aresample=48000,apad,atrim=0:%.3f[ao]' % DUR
else:
    aud = ['-f', 'lavfi', '-t', str(DUR), '-i', 'anullsrc=r=48000:cl=stereo']; af = ';[2:a]atrim=0:%.3f[ao]' % DUR
cmd = ['ffmpeg', '-v', 'error', '-y', *v, *aud, '-filter_complex', vf + af, '-map', '[vo]', '-map', '[ao]',
       '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30', '-t', str(DUR),
       '-c:a', 'aac', '-b:a', '192k', OUT]
subprocess.run(cmd, check=True)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,r_frame_rate,nb_frames',
                      '-of', 'compact', OUT], capture_output=True, text=True).stdout)
