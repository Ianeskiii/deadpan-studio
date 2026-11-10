"""Deadpan Studio, local mode: the studio website and the production queue on your own PC. No GitHub needed.

  python3 tools/local_studio.py            # normally started by local/start.sh
  open http://localhost:8080

What it does
- Serves the studio website (index.html + studio.js) and the videos from this folder.
- Saves what you do on the site straight into this folder: new shorts, revisions, library requests, narration MP3s.
- Runs Claude Code (`claude -p`, signed in with your own Claude account) whenever there is work, one run at a time.
  It also checks every 30 minutes to resume anything left half-done (e.g. after a usage limit).
- Logs of every Claude run go to .local/runs/.

Settings (environment variables): STUDIO_PORT (8080), STUDIO_HOST (127.0.0.1), STUDIO_MODEL (claude-opus-5-5),
STUDIO_CHECK_MIN (30), STUDIO_AUTORUN (1; set 0 to only run when you press "Run the queue now" on the site),
CLAUDE_BIN (path to claude if it isn't on PATH).
Standard library only.
"""
import glob, json, mimetypes, os, re, shutil, subprocess, threading, time, urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PORT = int(os.environ.get('STUDIO_PORT', '8080'))
HOST = os.environ.get('STUDIO_HOST', '127.0.0.1')
MODEL = os.environ.get('STUDIO_MODEL', 'claude-opus-5-5')
CHECK_MIN = float(os.environ.get('STUDIO_CHECK_MIN', '30'))
AUTORUN = os.environ.get('STUDIO_AUTORUN', '1') != '0'
RUNS = os.path.join(ROOT, '.local', 'runs')
TOOLS = 'Bash,Read,Write,Edit,MultiEdit,Glob,Grep,TodoWrite,WebSearch,WebFetch'
PROMPT = """Run the queue. Follow CLAUDE.md exactly, in LOCAL MODE (see "Local mode" in CLAUDE.md):
you are running on the owner's own PC, started by tools/local_studio.py. STUDIO_LOCAL=1 is set, so tools/studio.py
saves and commits locally and never pulls or pushes. Don't use GitHub at all (no git pull, git push or gh).
The pipeline is set up already (local/start.sh ran setup.sh in .venv). Nobody is watching and nobody can answer
questions, so make reasonable choices and note them in the short's notes. Use tools/studio.py for every status
change so progress shows on the website."""

WRITE_OK = [re.compile(p) for p in (r'^shorts/[a-z0-9][a-z0-9-]{0,80}/short\.json$',
                                     r'^shorts/[a-z0-9][a-z0-9-]{0,80}/revision-\d{10,16}\.json$',
                                     r'^library/requests/[a-z0-9][a-z0-9-]{0,100}\.json$')]
HIDDEN = re.compile(r'(^|/)(\.git|\.venv|\.local|\.cache|__pycache__|node_modules)(/|$)|(^|/)\.')


def now_ms(): return int(time.time() * 1000)


def work_waiting():
    """Same rule as the old GitHub workflow: anything queued, in revision or half-done, or a sticky short whose MP3 arrived."""
    for p in glob.glob('shorts/*/short.json'):
        try: d = json.load(open(p, encoding='utf-8'))
        except Exception: continue
        folder = os.path.dirname(p)
        has_mp3 = any(f.lower().endswith('.mp3') for f in os.listdir(folder))
        if d.get('channel') == 'sticky' and d.get('status') == 'needs-audio':
            if has_mp3: return True
            continue
        if d.get('status') in ('queued', 'revision', 'working'): return True
    return bool(glob.glob('shorts/*/revision-*.json') or glob.glob('library/requests/*.json'))


def claude_bin():
    c = os.environ.get('CLAUDE_BIN') or shutil.which('claude')
    if not c and os.path.exists(os.path.expanduser('~/.local/bin/claude')): c = os.path.expanduser('~/.local/bin/claude')
    return c


class Runner:
    def __init__(self):
        self.ev = threading.Event(); self.lock = threading.Lock()
        self.s = dict(running=False, startedAt=None, lastEnd=None, lastExit=None, lastLog=None, reason=None,
                      error=None, pauseUntil=None, autorun=AUTORUN, nextCheck=None)
        self.proc = None
        threading.Thread(target=self.loop, daemon=True).start()

    def kick(self, reason, manual=False):
        with self.lock:
            self.s['reason'] = reason
            if manual: self.s['pauseUntil'] = None
        if AUTORUN or manual: self.ev.set()

    def state(self):
        with self.lock: d = dict(self.s)
        d['waiting'] = work_waiting(); d['claude'] = bool(claude_bin()); d['model'] = MODEL
        if d['lastLog'] and os.path.exists(d['lastLog']):
            try: d['logTail'] = open(d['lastLog'], encoding='utf-8', errors='replace').read()[-1500:]
            except Exception: pass
        return d

    def loop(self):
        streak = 0
        while True:
            with self.lock: self.s['nextCheck'] = now_ms() + int(CHECK_MIN * 60000) if AUTORUN else None
            self.ev.wait(timeout=CHECK_MIN * 60 if AUTORUN else None); self.ev.clear()
            with self.lock: pause = self.s['pauseUntil']
            if pause and now_ms() < pause: continue
            while work_waiting():
                code = self.run_once()
                if code is None: break                       # claude missing
                if code != 0:                                 # usage limit or crash: wait before trying again
                    with self.lock: self.s['pauseUntil'] = now_ms() + int(CHECK_MIN * 60000)
                    break
                streak += 1
                if streak >= 2: streak = 0; break             # a short that keeps coming back waits for the next check (saves usage)
            streak = 0

    def run_once(self):
        c = claude_bin()
        if not c:
            with self.lock: self.s['error'] = 'Claude Code (claude) was not found inside WSL. Install it there and sign in: see LOCAL.md.'
            return None
        os.makedirs(RUNS, exist_ok=True)
        log = os.path.join(RUNS, time.strftime('run-%Y%m%d-%H%M%S.log'))
        env = dict(os.environ, STUDIO_LOCAL='1')
        cmd = [c, '-p', PROMPT, '--model', MODEL, '--max-turns', '600', '--allowedTools', TOOLS]
        with self.lock: self.s.update(running=True, startedAt=now_ms(), lastLog=log, error=None)
        print(f'[studio] Claude started ({self.s["reason"] or "queue"}), log: {os.path.relpath(log, ROOT)}', flush=True)
        try:
            with open(log, 'w', encoding='utf-8') as f:
                f.write(f'$ claude -p "<run the queue>" --model {MODEL}\n\n'); f.flush()
                self.proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
                code = self.proc.wait()
        except Exception as e:
            code = 1; open(log, 'a').write(f'\n[studio] could not run claude: {e}\n')
        with self.lock: self.s.update(running=False, lastEnd=now_ms(), lastExit=code)
        print(f'[studio] Claude finished with exit code {code}', flush=True)
        return code


RUNNER = None


class H(BaseHTTPRequestHandler):
    server_version = 'DeadpanStudio/1'

    def log_message(self, *a): pass

    def send_json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(b)))
        self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(b)

    def err(self, code, msg): self.send_json({'error': msg}, code)

    def body(self, limit):
        n = int(self.headers.get('Content-Length') or 0)
        if n > limit: raise ValueError(f'too large ({n} bytes)')
        return self.rfile.read(n)

    # ---------- reading ----------
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); path = urllib.parse.unquote(u.path)
        if path == '/api/files':
            paths = []
            for top in ('shorts', 'library'):
                for dp, dn, fn in os.walk(top):
                    dn[:] = [d for d in dn if not d.startswith('.')]
                    paths += [os.path.join(dp, f).replace(os.sep, '/') for f in fn if not f.startswith('.')]
            return self.send_json({'paths': sorted(paths), 'at': now_ms()})
        if path == '/api/status': return self.send_json(RUNNER.state())
        rel = path.lstrip('/') or 'index.html'
        if rel.endswith('/'): rel += 'index.html'
        full = os.path.realpath(os.path.join(ROOT, rel))
        if HIDDEN.search(rel) or not full.startswith(ROOT + os.sep) or not os.path.isfile(full):
            return self.err(404, 'not found')
        self.send_file(full)

    def send_file(self, full):
        size = os.path.getsize(full)
        ctype = {'.mp4': 'video/mp4', '.mp3': 'audio/mpeg', '.js': 'text/javascript', '.json': 'application/json'}.get(
            os.path.splitext(full)[1].lower()) or mimetypes.guess_type(full)[0] or 'application/octet-stream'
        if ctype.startswith('text/') or ctype in ('application/json', 'text/javascript'): ctype += '; charset=utf-8'
        start, end, code = 0, size - 1, 200
        m = re.match(r'bytes=(\d*)-(\d*)', self.headers.get('Range') or '')
        if m and size:
            if m.group(1): start = int(m.group(1)); end = int(m.group(2)) if m.group(2) else size - 1
            else: start = max(0, size - int(m.group(2) or 0))
            end = min(end, size - 1)
            if start > end: self.send_response(416); self.send_header('Content-Range', f'bytes */{size}'); self.end_headers(); return
            code = 206
        self.send_response(code); self.send_header('Content-Type', ctype); self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(end - start + 1)); self.send_header('Cache-Control', 'no-cache')
        if code == 206: self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.end_headers()
        with open(full, 'rb') as f:
            f.seek(start); left = end - start + 1
            try:
                while left > 0:
                    chunk = f.read(min(1 << 20, left))
                    if not chunk: break
                    self.wfile.write(chunk); left -= len(chunk)
            except (BrokenPipeError, ConnectionResetError): pass

    # ---------- writing ----------
    def do_POST(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        try:
            if u.path == '/api/run':
                RUNNER.kick('started by hand', manual=True); return self.send_json({'ok': True})
            if u.path == '/api/file':
                d = json.loads(self.body(512 * 1024) or b'{}')
                rel, content = d.get('path', ''), d.get('content', '')
                if not any(p.match(rel) for p in WRITE_OK): return self.err(400, 'That file path is not allowed.')
                obj = json.loads(content)  # must be valid JSON
                full = os.path.join(ROOT, rel)
                if rel.endswith('short.json') and os.path.exists(full): return self.err(409, 'A short with this id already exists. Change the title a little.')
                if rel.startswith('shorts/') and not rel.endswith('short.json') and not os.path.exists(os.path.join(os.path.dirname(full), 'short.json')):
                    return self.err(404, 'That short does not exist.')
                os.makedirs(os.path.dirname(full), exist_ok=True)
                tmp = full + '.part'
                with open(tmp, 'w', encoding='utf-8') as f: json.dump(obj, f, indent=2, ensure_ascii=False); f.write('\n')
                os.replace(tmp, full)
                print(f'[studio] saved {rel}', flush=True)
                RUNNER.kick(f'new {os.path.basename(rel)}')
                return self.send_json({'ok': True, 'path': rel})
            if u.path == '/api/upload':
                sid, name = (q.get('id') or [''])[0], (q.get('name') or ['narration.mp3'])[0]
                if not re.match(r'^[a-z0-9][a-z0-9-]{0,80}$', sid) or not os.path.exists(f'shorts/{sid}/short.json'):
                    return self.err(404, 'That short does not exist.')
                base = re.sub(r'[^A-Za-z0-9._-]+', '-', os.path.basename(name)).strip('.-') or 'narration.mp3'
                if not base.lower().endswith('.mp3'): return self.err(400, 'Only .mp3 files can be uploaded here.')
                data = self.body(300 * 1024 * 1024)
                if len(data) < 1000: return self.err(400, 'That file is empty.')
                full = os.path.join(ROOT, 'shorts', sid, base)
                with open(full + '.part', 'wb') as f: f.write(data)
                os.replace(full + '.part', full)
                os.utime(full, None)
                print(f'[studio] narration audio saved: shorts/{sid}/{base}', flush=True)
                RUNNER.kick('narration audio uploaded')
                return self.send_json({'ok': True, 'path': f'shorts/{sid}/{base}'})
            return self.err(404, 'not found')
        except ValueError as e:
            return self.err(400, str(e))


def main():
    global RUNNER
    RUNNER = Runner()
    srv = ThreadingHTTPServer((HOST, PORT), H)
    print(f'\n  Deadpan Studio (local) is running: open http://localhost:{PORT} in your browser.\n'
          f'  Claude Code: {"found" if claude_bin() else "NOT FOUND (see LOCAL.md)"} · model {MODEL} · '
          f'{"runs automatically" if AUTORUN else "runs only when you press Run on the site"} · Ctrl+C to stop.\n', flush=True)
    if AUTORUN and work_waiting(): RUNNER.kick('work waiting at start')
    try: srv.serve_forever()
    except KeyboardInterrupt:
        print('\n[studio] stopping.')
        if RUNNER.proc and RUNNER.proc.poll() is None:
            print('[studio] a Claude run is still going; it was stopped. The next start resumes from where it left off.')
            RUNNER.proc.terminate()


if __name__ == '__main__':
    main()
