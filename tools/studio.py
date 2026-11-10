"""Queue helper for Claude. Run from the repo root.

  python3 tools/studio.py queue                      # shorts waiting (queued / revision), oldest first, plus library requests
  python3 tools/studio.py stage <id> <stageIndex> [etaMinutes] [note]   # mark progress, then commit + push
  python3 tools/studio.py version <id> <video.mp4> <poster.jpg> <seconds> "<notes>"   # add a finished version, mark ready
  python3 tools/studio.py fail <id> "<reason>"
  python3 tools/studio.py index                      # rebuild shorts/index.json (the site's offline fallback)
  python3 tools/studio.py narration <id> <file.txt> ["<notes>"]   # sticky Stage 1 done: save narration, status -> needs-audio

Channels: a short's "channel" is "deadpan-doug" (the default when the field is missing) or "sticky".
Sticky shorts run in two stages (channels/sticky/PLAYBOOK.md): narration, then video once the owner has
committed an .mp3 into shorts/<id>/. A sticky short in "needs-audio" without an .mp3 is skipped.
Set STUDIO_NO_PUSH=1 to work locally without committing or pushing (tests).

Revision requests arrive as shorts/<id>/revision-<ms>.json files. `queue` folds them into short.json
(status -> revision) and deletes the files. `version` marks every open revision done in the new version.
Every write command commits and pushes, so the website and other accounts see it.
"""
import json, os, shutil, subprocess, sys, time, glob

STAGES = ["Queued", "Script & timing", "Voices", "Set & cast", "Animation", "Test frames", "Rendering", "Sound & edit", "Final check", "Ready"]
STICKY_STAGES = ["Queued", "Writing narration", "Needs audio", "Timing", "Scenes", "Test frames", "Rendering", "Sound & edit", "Final check", "Ready"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
now = lambda: int(time.time() * 1000)


def load(i):
    return json.load(open(f'shorts/{i}/short.json'))


def save(i, d):
    d['updatedAt'] = now()
    json.dump(d, open(f'shorts/{i}/short.json', 'w'), indent=2, ensure_ascii=False)
    open(f'shorts/{i}/short.json', 'a').write('\n')


def channel(d):
    return d.get('channel') or 'deadpan-doug'


def stages_for(d):
    return STICKY_STAGES if channel(d) == 'sticky' else STAGES


def mp3s(i):
    return sorted(f for f in glob.glob(f'shorts/{i}/*') if f.lower().endswith('.mp3'))


def sticky_next(d):
    """Which sticky stage a short needs now: 'narration', 'video', 'wait' (needs-audio, no mp3) or None (nothing)."""
    i, st = d['id'], d.get('status')
    open_revs = [r for r in d.get('revisions', []) if not r.get('done')]
    has_narr = os.path.exists(f'shorts/{i}/narration.txt')
    if any(r.get('kind') == 'narration' for r in open_revs) or (st in ('queued', 'revision', 'working') and not has_narr):
        return 'narration'
    if st == 'working' and (d.get('stageIndex') or 0) <= 1:
        return 'narration'
    if st in ('needs-audio', 'revision', 'working', 'queued'):
        return 'video' if mp3s(i) else 'wait'
    return None


def git(*a, check=True):
    return subprocess.run(['git', *a], check=check, capture_output=True, text=True)


def push(msg):
    index()
    if os.environ.get('STUDIO_NO_PUSH'):
        print('(STUDIO_NO_PUSH: not committing)', msg); return
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
    paths = sorted(p for p in glob.glob('shorts/*/*.json') + glob.glob('library/requests/*.json') + glob.glob('shorts/*/narration.txt')
                   + [m for m in glob.glob('shorts/*/*') if m.lower().endswith('.mp3')] if not p.endswith('index.json'))
    json.dump({'paths': paths, 'at': now()}, open('shorts/index.json', 'w'), indent=1)


def queue():
    git('pull', '-q', '--rebase', 'origin', 'main', check=False)
    changed = False
    for f in sorted(glob.glob('shorts/*/revision-*.json')):
        i = f.split('/')[1]
        d, r = load(i), json.load(open(f))
        rev = {'text': r.get('text', ''), 'at': r.get('at', now()), 'done': False}
        if r.get('kind'): rev['kind'] = r['kind']  # sticky: "narration" (Stage 1) or "video" (Stage 2)
        d.setdefault('revisions', []).append(rev)
        d.update(status='revision', stage='Queued', stageIndex=0, progress=0, etaMinutes=None)
        save(i, d); os.remove(f); changed = True
    if changed:
        push('Queue: fold in revision requests')
    rows = [load(p.split('/')[1]) for p in glob.glob('shorts/*/short.json')]
    for r in rows: r.setdefault('id', r.get('id'))
    def waiting(r):
        if channel(r) == 'sticky': return sticky_next(r) in ('narration', 'video')
        return r.get('status') in ('queued', 'revision', 'working')
    wait = sorted((r for r in rows if waiting(r)), key=lambda r: r.get('createdAt') or 0)
    for r in wait:
        open_revs = [x['text'] for x in r.get('revisions', []) if not x.get('done')]
        if channel(r) == 'sticky':
            nxt = sticky_next(r)
            what = ('STAGE 1 narration' if nxt == 'narration' else f"STAGE 2 video from {mp3s(r['id'])[-1]}")
            print(f"- {r['id']}  [sticky, {r['status']}]  {r.get('title')}  -> {what}  (follow channels/sticky/PLAYBOOK.md)"
                  + (f"\n    notes: {r.get('description')}" if r.get('description') else '')
                  + (f"\n    open revisions: {[(x.get('kind') or 'video', x['text']) for x in r.get('revisions', []) if not x.get('done')]}" if open_revs else ''))
            continue
        print(f"- {r['id']}  [{r['status']}]  {r.get('title')}  ({r.get('durationMin')}-{r.get('durationMax')} s)"
              f"  chars={r.get('characters') or ['doug']} new={r.get('newCharacters') or '-'} scene={r.get('scene') or r.get('newScene') or '-'}"
              + (f"\n    open revisions: {open_revs}" if open_revs else ''))
    for r in rows:
        if channel(r) == 'sticky' and sticky_next(r) == 'wait':
            print(f"  (waiting for the owner's narration audio, skipped: {r['id']})")
    for f in sorted(glob.glob('library/requests/*.json')):
        print('- library request:', f, json.load(open(f)))
    if not wait and not glob.glob('library/requests/*.json'):
        print('Queue is empty.')


def stage(i, idx, eta=None, note=''):
    d = load(i); idx = int(idx)
    d.update(status='working', stage=stages_for(d)[idx], stageIndex=idx, progress=round(idx / 9 * 100),
             etaMinutes=None if eta in (None, '') else float(eta), note=note)
    save(i, d); push(f'{i}: {stages_for(d)[idx]}')


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


def narration(i, path, notes=''):
    """Sticky Stage 1 done: save the narration, drop audio made for an older narration, wait for the owner's MP3."""
    d = load(i)
    text = '\n'.join(l.strip() for l in open(path, encoding='utf-8') if l.strip()) + '\n'
    open(f'shorts/{i}/narration.txt', 'w', encoding='utf-8').write(text)
    for m in mp3s(i):
        os.remove(m)
    for r in d.get('revisions', []):
        if not r.get('done') and r.get('kind') == 'narration':
            r.update(done=True, doneIn='narration')
    d.update(channel='sticky', status='needs-audio', stage='Needs audio', stageIndex=2, progress=round(2 / 9 * 100), etaMinutes=None,
             note=notes, narrationAt=now())
    save(i, d); push(f'{i}: narration ready, waiting for audio')
    print(f'{i}: narration saved ({len(text.split())} words); status needs-audio')


def fail(i, reason):
    d = load(i); d.update(status='failed', note=reason, etaMinutes=None); save(i, d); push(f'{i}: failed')


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    {'queue': queue, 'stage': stage, 'version': version, 'fail': fail, 'index': index, 'narration': narration}[cmd](*args)
