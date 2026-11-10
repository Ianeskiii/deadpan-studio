"""Sticky Animation helper. Run from the repo root.

  python3 channels/sticky/sticky.py prep <id>              # newest shorts/<id>/*.mp3 + narration.txt -> episodes/<id>/timeline.json (+ template scenes.py/audio.py if missing)
  python3 channels/sticky/sticky.py stills <id> [t ...]    # full-size test frames (default: one per shot) + contact sheets stills/sheet*.jpg
  python3 channels/sticky/sticky.py render <id> [--jobs N] [--only i,j]   # scene files, audio mix, concat, mux, loop check -> episodes/<id>/final.mp4 + poster.jpg
  python3 channels/sticky/sticky.py audio <id>             # just re-run audio.py (mix.wav) and re-mux final.mp4

The episode folder (channels/sticky/episodes/<id>/) holds scenes.py, audio.py, lines.txt and timeline.json (committed)
plus render outputs (ignored by git).
"""
import glob, json, os, shutil, subprocess, sys

CH = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(CH))
PY = sys.executable

def ep_dir(i): return os.path.join(CH, 'episodes', i)
def run(cmd, cwd=None, **kw):
    print('+', ' '.join(cmd) if isinstance(cmd, list) else cmd, flush=True)
    return subprocess.run(cmd, cwd=cwd, check=True, **kw)

def newest_mp3(i):
    files = [f for f in glob.glob(os.path.join(ROOT, 'shorts', i, '*')) if f.lower().endswith('.mp3')]
    if not files: sys.exit(f'No .mp3 in shorts/{i}/ yet.')
    def committed(f):  # newest by git commit time, falling back to mtime
        r = subprocess.run(['git', 'log', '-1', '--format=%ct', '--', f], cwd=ROOT, capture_output=True, text=True)
        return int(r.stdout.strip() or 0) or os.path.getmtime(f)
    return max(files, key=committed)

def prep(i):
    d = ep_dir(i); os.makedirs(d, exist_ok=True)
    narr = os.path.join(ROOT, 'shorts', i, 'narration.txt')
    if not os.path.exists(narr): sys.exit(f'shorts/{i}/narration.txt is missing.')
    mp3 = newest_mp3(i)
    print('audio:', os.path.relpath(mp3, ROOT))
    run([PY, os.path.join(CH, 'timeline.py'), d, narr, mp3])
    for f in ('scenes.py', 'audio.py'):
        if not os.path.exists(os.path.join(d, f)):
            shutil.copy(os.path.join(CH, 'template', f), os.path.join(d, f)); print('template ->', f)
    json.dump({'audio': os.path.relpath(mp3, ROOT)}, open(os.path.join(d, 'source.json'), 'w'), indent=1)

def shots(d):
    out = subprocess.run([PY, '-c', 'import sys,os,json;sys.path[:0]=[os.getcwd(),sys.argv[1]];import scenes;'
                          'print(json.dumps([[s[0],s[1],s[2].__name__,(s[4] if len(s)>4 else "fade")] for s in scenes.scenes()]))', CH],
                         cwd=d, capture_output=True, text=True, check=True).stdout
    return json.loads(out.strip().splitlines()[-1])

def sheets(d, files):
    from PIL import Image
    per = 14
    for f in glob.glob(os.path.join(d, 'stills', 'sheet*.jpg')): os.remove(f)
    for p in range(0, len(files), per):
        sub = files[p:p + per]; cols = 7
        m = Image.new('RGB', (cols * 300, ((len(sub) + cols - 1) // cols) * 533), 'black')
        for k, f in enumerate(sub): m.paste(Image.open(f).resize((300, 533)), ((k % cols) * 300, (k // cols) * 533))
        m.save(os.path.join(d, 'stills', f'sheet{p // per}.jpg'), quality=85)
    print('contact sheets:', sorted(glob.glob(os.path.join(d, 'stills', 'sheet*.jpg'))))

def stills(i, *ts):
    d = ep_dir(i); sc = shots(d)
    ts = list(ts) or [f'{a * 0.3 + b * 0.7:.2f}' for a, b, _, _ in sc]
    shutil.rmtree(os.path.join(d, 'stills'), ignore_errors=True)
    run([PY, os.path.join(CH, 'render.py'), 'still', *ts], cwd=d)
    sheets(d, [os.path.join(d, 'stills', f'still_{t}.jpg') for t in ts])

def audio(i):
    d = ep_dir(i)
    run([PY, 'audio.py'], cwd=d)
    mux(d)

def mux(d):
    tl = json.load(open(os.path.join(d, 'timeline.json')))
    run(['ffmpeg', '-v', 'error', '-y', '-i', 'v.mp4', '-i', 'mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', 'final.mp4'], cwd=d)
    run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.0', '-i', 'final.mp4', '-vframes', '1', '-q:v', '3', 'poster.jpg'], cwd=d)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'final.mp4'], cwd=d, capture_output=True, text=True).stdout)
    run(['ffmpeg', '-v', 'error', '-y', '-i', 'final.mp4', '-vf', r'select=eq(n\,0)', '-vframes', '1', 'loop_first.png'], cwd=d)
    run(['ffmpeg', '-v', 'error', '-y', '-sseof', '-0.05', '-i', 'final.mp4', '-update', '1', 'loop_last.png'], cwd=d)
    import numpy as np; from PIL import Image
    a = np.asarray(Image.open(os.path.join(d, 'loop_first.png')), float); b = np.asarray(Image.open(os.path.join(d, 'loop_last.png')), float)
    diff = abs(a - b).mean()
    print(f'final.mp4: {dur:.2f}s (timeline {tl["total"]}s); loop diff first/last frame = {diff:.2f} (under ~5 is seamless)')
    json.dump({'seconds': round(dur, 2), 'loopDiff': round(diff, 2)}, open(os.path.join(d, 'result.json'), 'w'))

def render(i, *args):
    d = ep_dir(i); sc = shots(d)
    jobs = os.cpu_count() or 2; only = None
    a = list(args)
    while a:
        x = a.pop(0)
        if x == '--jobs': jobs = int(a.pop(0))
        elif x == '--only': only = [int(v) for v in a.pop(0).split(',')]
    idx = only if only is not None else list(range(len(sc)))
    if only is None:
        for f in glob.glob(os.path.join(d, 'sc[0-9][0-9].mp4')): os.remove(f)
    # longest scenes first, spread over the workers
    idx.sort(key=lambda k: -(sc[k][1] - sc[k][0]))
    groups = [idx[w::jobs] for w in range(jobs)]
    procs = [subprocess.Popen([PY, os.path.join(CH, 'render.py'), 'video', *map(str, g)], cwd=d) for g in groups if g]
    bad = [p.wait() for p in procs]
    missing = [k for k in range(len(sc)) if not os.path.exists(os.path.join(d, f'sc{k:02d}.mp4'))]
    if any(bad) or missing: sys.exit(f'render failed; missing scenes {missing}')
    open(os.path.join(d, 'list.txt'), 'w').write(''.join(f"file 'sc{k:02d}.mp4'\n" for k in range(len(sc))))
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', 'v.mp4'], cwd=d)
    run([PY, 'audio.py'], cwd=d)
    mux(d)

if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    {'prep': prep, 'stills': stills, 'render': render, 'audio': audio}[cmd](*args)
