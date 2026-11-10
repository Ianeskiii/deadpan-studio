"""Queue helper for Claude. Run from the repo root.

  python3 tools/studio.py queue                      # shorts waiting (queued / revision), oldest first, plus library requests
  python3 tools/studio.py stage <id> <stageIndex> [etaMinutes] [note]   # mark progress, then commit + push
  python3 tools/studio.py version <id> <video.mp4> <poster.jpg> <seconds> "<notes>"   # add a finished version, mark ready
  python3 tools/studio.py fail <id> "<reason>"
  python3 tools/studio.py index                      # rebuild shorts/index.json (the site's offline fallback)

Revision requests arrive as shorts/<id>/revision-<ms>.json files. `queue` folds them into short.json
(status -> revision) and deletes the files. `version` marks every open revision done in the new version.
Every write command commits and pushes, so the website and other accounts see it.
"""
import json, os, shutil, subprocess, sys, time, glob

STAGES = ["Queued", "Script & timing", "Voices", "Set & cast", "Animation", "Test frames", "Rendering", "Sound & edit", "Final check", "Ready"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
now = lambda: int(time.time() * 1000)


def load(i):
    return json.load(open(f'shorts/{i}/short.json'))


def save(i, d):
    d['updatedAt'] = now()
    json.dump(d, open(f'shorts/{i}/short.json', 'w'), indent=2, ensure_ascii=False)
    open(f'shorts/{i}/short.json', 'a').write('\n')


def git(*a, check=True):
    return subprocess.run(['git', *a], check=check, capture_output=True, text=True)


def push(msg):
    index()
    git('add', '-A', 'shorts', 'library')
    if git('diff', '--cached', '--quiet', check=False).returncode == 0:
        return
    git('-c', 'user.name=Deadpan Studio', '-c', 'user.email=noreply@anthropic.com', 'commit', '-q', '-m', msg)
    for _ in range(3):  # another account may have pushed meanwhile
        if git('push', '-q', 'origin', 'HEAD:main', check=False).returncode == 0:
            return
        git('pull', '-q', '--rebase', 'origin', 'main', check=False)
    print('WARNING: push failed; run git push manually')


def index():
    paths = sorted(p for p in glob.glob('shorts/*/*.json') + glob.glob('library/requests/*.json') if not p.endswith('index.json'))
    json.dump({'paths': paths, 'at': now()}, open('shorts/index.json', 'w'), indent=1)


def queue():
    git('pull', '-q', '--rebase', 'origin', 'main', check=False)
    changed = False
    for f in sorted(glob.glob('shorts/*/revision-*.json')):
        i = f.split('/')[1]
        d, r = load(i), json.load(open(f))
        d.setdefault('revisions', []).append({'text': r.get('text', ''), 'at': r.get('at', now()), 'done': False})
        d.update(status='revision', stage='Queued', stageIndex=0, progress=0, etaMinutes=None)
        save(i, d); os.remove(f); changed = True
    if changed:
        push('Queue: fold in revision requests')
    rows = [load(p.split('/')[1]) for p in glob.glob('shorts/*/short.json')]
    wait = sorted((r for r in rows if r.get('status') in ('queued', 'revision', 'working')), key=lambda r: r.get('createdAt') or 0)
    for r in wait:
        open_revs = [x['text'] for x in r.get('revisions', []) if not x.get('done')]
        print(f"- {r['id']}  [{r['status']}]  {r.get('title')}  ({r.get('durationMin')}-{r.get('durationMax')} s)"
              f"  chars={r.get('characters') or ['doug']} new={r.get('newCharacters') or '-'} scene={r.get('scene') or r.get('newScene') or '-'}"
              + (f"\n    open revisions: {open_revs}" if open_revs else ''))
    for f in sorted(glob.glob('library/requests/*.json')):
        print('- library request:', f, json.load(open(f)))
    if not wait and not glob.glob('library/requests/*.json'):
        print('Queue is empty.')


def stage(i, idx, eta=None, note=''):
    d = load(i); idx = int(idx)
    d.update(status='working', stage=STAGES[idx], stageIndex=idx, progress=round(idx / 9 * 100),
             etaMinutes=None if eta in (None, '') else float(eta), note=note)
    save(i, d); push(f'{i}: {STAGES[idx]}')


def version(i, video, poster, seconds, notes):
    d = load(i)
    v = max([x['v'] for x in d.get('versions', [])] or [0]) + 1
    shutil.copy(video, f'shorts/{i}/v{v}.mp4'); shutil.copy(poster, f'shorts/{i}/v{v}.jpg')
    d.setdefault('versions', []).append({'v': v, 'video': f'v{v}.mp4', 'poster': f'v{v}.jpg', 'seconds': round(float(seconds), 1), 'notes': notes})
    for r in d.get('revisions', []):
        if not r.get('done'):
            r.update(done=True, doneIn=v)
    d.update(status='ready', stage='Ready', stageIndex=9, progress=100, etaMinutes=None, note='')
    save(i, d); push(f'{i}: v{v} ready')
    print(f'{i}: v{v} published')


def fail(i, reason):
    d = load(i); d.update(status='failed', note=reason, etaMinutes=None); save(i, d); push(f'{i}: failed')


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    {'queue': queue, 'stage': stage, 'version': version, 'fail': fail, 'index': index}[cmd](*args)
