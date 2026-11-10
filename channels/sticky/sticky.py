"""Sticky Animation helper. Run from the repo root.

  python3 channels/sticky/sticky.py prep <id>              # newest shorts/<id>/*.mp3 + narration.txt -> episodes/<id>/timeline.json (+ template scenes.py/audio.py if missing)
  python3 channels/sticky/sticky.py stills <id> [t ...]    # full-size test frames (default: one per shot) + contact sheets stills/sheet*.jpg
  python3 channels/sticky/sticky.py render <id> [--jobs N] [--only i,j]   # scene files, audio mix, concat, mux, loop check -> episodes/<id>/final.mp4 + poster.jpg
  python3 channels/sticky/sticky.py audio <id>             # just re-run audio.py (mix.wav) and re-mux final.mp4
  python3 channels/sticky/sticky.py check <id>             # sync check of final.mp4: captions vs voice, voice offset, length (render runs it too)

prep stops with SYNC FAIL when the word timing doesn't follow the voice, and render refuses a timeline that didn't pass.

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
    def committed(f):  # newest by git commit time; a file not committed yet (local mode upload) is newer than any committed one
        r = subprocess.run(['git', 'log', '-1', '--format=%ct', '--', f], cwd=ROOT, capture_output=True, text=True)
        ct = int(r.stdout.strip() or 0) if r.returncode == 0 else 0
        return (1, os.path.getmtime(f)) if ct == 0 else (0, ct)
    return max(files, key=committed)

def prep(i, *args):
    d = ep_dir(i); os.makedirs(d, exist_ok=True)
    narr = os.path.join(ROOT, 'shorts', i, 'narration.txt')
    if not os.path.exists(narr): sys.exit(f'shorts/{i}/narration.txt is missing.')
    mp3 = newest_mp3(i)
    print('audio:', os.path.relpath(mp3, ROOT))
    cmd = [PY, os.path.join(CH, 'timeline.py'), d, narr, mp3] + (['--force'] if '--force' in args else [])
    print('+', ' '.join(cmd), flush=True)
    rc = subprocess.run(cmd).returncode
    if rc == 2:
        sys.exit(f'\nprep: SYNC FAIL for {i}. The word timing does not follow the voice, so the captions and shots would be off.\n'
                 f'Don\'t build or render from this timeline. Read episodes/{i}/sync.json and the word list above:\n'
                 f'- if the MP3 says different words from narration.txt (edited in ElevenLabs), make narration.txt match the audio and re-run prep;\n'
                 f'- otherwise fail the short with the problems listed, so the owner can re-export the audio.')
    if rc: sys.exit(f'prep failed (timeline.py exit {rc})')
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
    check(i)

def mux(d):
    tl = json.load(open(os.path.join(d, 'timeline.json')))
    run(['ffmpeg', '-v', 'error', '-y', '-i', 'v.mp4', '-i', 'mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', 'final.mp4'], cwd=d)
    run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.0', '-i', 'final.mp4', '-vframes', '1', '-q:v', '3', 'poster.jpg'], cwd=d)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'final.mp4'], cwd=d, capture_output=True, text=True).stdout)
    run(['ffmpeg', '-v', 'error', '-y', '-i', 'final.mp4', '-vf', r'select=eq(n\,0)', '-vframes', '1', 'loop_first.png'], cwd=d)
    run(['ffmpeg', '-v', 'error', '-y', '-sseof', '-0.3', '-i', 'final.mp4', '-update', '1', 'loop_last.png'], cwd=d)
    import numpy as np; from PIL import Image
    a = np.asarray(Image.open(os.path.join(d, 'loop_first.png')), float); b = np.asarray(Image.open(os.path.join(d, 'loop_last.png')), float)
    diff = abs(a - b).mean()
    print(f'final.mp4: {dur:.2f}s (timeline {tl["total"]}s); loop diff first/last frame = {diff:.2f} (under ~5 is seamless)')
    json.dump({'seconds': round(dur, 2), 'loopDiff': round(diff, 2)}, open(os.path.join(d, 'result.json'), 'w'))

def render(i, *args):
    d = ep_dir(i)
    sync = json.load(open(os.path.join(d, 'timeline.json'))).get('sync') or {}
    if not sync.get('ok') and '--force' not in args:
        sys.exit(f'render: timeline.json has no passing sync check ({"; ".join(sync.get("problems", [])) or "made before the check existed"}).\n'
                 f'Run `python3 channels/sticky/sticky.py prep {i}` first; only render once it prints SYNC OK.')
    sc = shots(d)
    jobs = os.cpu_count() or 2; only = None
    a = [x for x in args if x != '--force']
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
    check(i)

def envelope(path, t=None, rate=100):
    """Loudness envelope (rate per second) of an audio or video file's sound."""
    import numpy as np
    cmd = ['ffmpeg', '-v', 'error', '-i', path] + (['-t', str(t)] if t else []) + ['-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-']
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32)
    n = 16000 // rate
    x = x[: len(x) // n * n].reshape(-1, n)
    return np.sqrt((x ** 2).mean(1) + 1e-9)

def voice_offset(voice, video, span=40.0, max_shift=1.5):
    """How far the voice sits from its place in the video's mix (s; + means the video's voice is late), and the match score."""
    import numpy as np
    a = np.log(envelope(voice, span)); b = np.log(envelope(video, span + max_shift))
    a = (a - a.mean()) / (a.std() + 1e-9); b = (b - b.mean()) / (b.std() + 1e-9)
    best = (-9.0, 0)
    for s in range(-int(max_shift * 100), int(max_shift * 100) + 1):
        if s >= 0: x, y = a[: len(b) - s], b[s: s + len(a)]
        else: x, y = a[-s:], b[: len(a) + s]
        m = min(len(x), len(y))
        if m < 200: continue
        c = float((x[:m] * y[:m]).mean())
        if c > best[0]: best = (c, s)
    return best[1] / 100, best[0]

def check(i, *args):
    """Final sync check: captions follow the voice, and the voice in final.mp4 sits exactly where the timeline says."""
    sys.path.insert(0, CH); import timeline as TLM
    d = ep_dir(i); tl = json.load(open(os.path.join(d, 'timeline.json')))
    problems = []
    sil = TLM.silences(os.path.join(d, 'voice.wav'))
    ok, rep = TLM.check_sync(tl['lines'], sil, tl['total'])
    problems += [f'captions: {p}' for p in rep['problems']]
    final = os.path.join(d, 'final.mp4')
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', final], capture_output=True, text=True).stdout)
    if abs(dur - tl['total']) > 0.3: problems.append(f'length: final.mp4 is {dur:.2f}s but the voice is {tl["total"]}s')
    off, score = voice_offset(os.path.join(d, 'voice.wav'), final)
    if abs(off) > 0.08: problems.append(f'audio: the voice in final.mp4 is {off:+.2f}s off its timeline position')
    if score < 0.35: problems.append(f'audio: final.mp4 sound barely matches voice.wav (score {score:.2f}); wrong or missing voice track?')
    res = {}
    rp = os.path.join(d, 'result.json')
    if os.path.exists(rp): res = json.load(open(rp))
    res['sync'] = dict(ok=not problems, problems=problems, voiceOffsetS=off, voiceMatch=round(score, 3), coverage=rep.get('coverage'))
    json.dump(res, open(rp, 'w'), indent=1)
    if problems:
        sys.exit('SYNC CHECK FAILED for final.mp4 (do not publish):\n  - ' + '\n  - '.join(problems))
    print(f'SYNC CHECK OK: captions follow the voice; voice offset {off:+.2f}s (match {score:.2f}); length {dur:.2f}s')

if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    {'prep': prep, 'stills': stills, 'render': render, 'audio': audio, 'check': check}[cmd](*args)
