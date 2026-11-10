"""Make timeline.json for a sticky episode from its narration text and the owner's MP3.

  python3 timeline.py <episode_dir> <narration.txt> <audio.mp3> [whisper_model_dir] [--force]

Writes into <episode_dir>: lines.txt (one narration line per row), voice.wav (the voice, trailing silence trimmed),
timeline.json ({lines:[{i,text,t0,t1,words:[{w,t0,t1,est?}],chunks:[[t0,t1],...]}], total, sync}), asr.json and sync.json.

Word times come from faster-whisper word timestamps on the repo's whisper_small model, aligned to the exact
narration words (so captions always show the script's spelling). Two passes are made: the whole file, then
short windows cut at the pauses (whisper often drops or skips stretches of a long file; short windows can't drift).
The pass that matches more script words wins. Words neither pass matched are placed inside the real speech
between their matched neighbours (pauses found by ffmpeg silencedetect), never spread blindly over silence.

SYNC CHECK: the timeline is then checked against the audio (see check_sync). If the captions would not follow
the voice, the files are still written for inspection but the script exits with code 2 and prints SYNC FAIL.
Do not render a video from a failed timeline. --force skips the exit (only after checking by hand).
"""
import difflib, json, os, re, subprocess, sys

PAUSE_END = re.compile(r"(…|\.\.\.|[.,!?;:—–-])[\"'”’)]*$")

# Sync thresholds (see check_sync)
MIN_COVERAGE = 0.75       # share of script words whisper actually matched
MAX_EST_RUN_S = 3.0       # longest stretch of estimated (unmatched) words, in seconds
MAX_WORDS_IN_SILENCE = 2  # words whose time is mostly inside a pause
MAX_LATE_EARLY_LINES = 0.2  # share of lines that don't start where the speech resumes after a pause


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower().replace("’", "'"))


def silences(wav):
    out = subprocess.run(['ffmpeg', '-i', wav, '-af', 'silencedetect=noise=-35dB:d=0.18', '-f', 'null', '-'], capture_output=True, text=True).stderr
    v = [float(x) for x in re.findall(r'silence_(?:start|end): ([0-9.]+)', out)]
    return [(v[i], v[i + 1]) for i in range(0, len(v) - 1, 2)]


def speech_in(g0, g1, sil):
    """Speech segments inside [g0, g1]: the interval minus the pauses."""
    segs, x = [], g0
    for s0, s1 in sil:
        if s1 <= x or s0 >= g1: continue
        if s0 > x: segs.append((x, min(s0, g1)))
        x = max(x, s1)
    if x < g1: segs.append((x, g1))
    return [(a, b) for a, b in segs if b - a > 0.04]


def spread(idx, words, segs, g0, g1):
    """Place words idx over the speech segments, weighted by word length. Returns {k: [t0, t1]}."""
    wts = [len(norm(words[k])) + 1.5 for k in idx]
    if not segs: segs = [(g0, g1)]
    total_sp = sum(b - a for a, b in segs)
    out, acc, tot = {}, 0.0, sum(wts)

    def at(u):  # position u (seconds of speech) -> real time
        for a, b in segs:
            if u <= b - a + 1e-9: return a + u
            u -= b - a
        return segs[-1][1]
    for k, wgt in zip(idx, wts):
        u0 = total_sp * acc / tot; acc += wgt; u1 = total_sp * acc / tot
        out[k] = [round(at(u0 + 1e-6), 3), round(at(u1), 3)]
    return out


def transcribe(wm, pcm, sr=16000, offset=0.0):
    segs, _ = wm.transcribe(pcm, language='en', word_timestamps=True, beam_size=5, vad_filter=False,
                            condition_on_previous_text=False)
    return [dict(w=w.word.strip(), t0=round(w.start + offset, 3), t1=round(w.end + offset, 3)) for s in segs for w in (s.words or [])]


def windows(sil, total, maxlen=10.0):
    """Cut the audio into windows of at most ~maxlen seconds, cutting in the middle of pauses."""
    mids = [(a + b) / 2 for a, b in sil]
    cuts = [0.0]
    for i, m in enumerate(mids):
        nxt = mids[i + 1] if i + 1 < len(mids) else total
        if nxt - cuts[-1] > maxlen and m - cuts[-1] >= 1.0: cuts.append(m)
    cuts.append(total)
    return [(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1) if cuts[i + 1] - cuts[i] > 0.2]


def match(script_words, asr):
    a = [norm(w) for w in script_words]; b = [norm(x['w']) for x in asr]
    times = [None] * len(a)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            x = asr[blk.b + k]; times[blk.a + k] = [x['t0'], x['t1']]
    # drop matches that go backwards in time (a stray match far from its neighbours)
    last = -1.0
    for k, t in enumerate(times):
        if t is None: continue
        if t[0] < last - 0.3: times[k] = None
        else: last = t[0]
    return times


def fill(times, words, sil, total):
    """Place unmatched words inside the real speech between their matched neighbours.
    If the run's punctuation breaks match the pauses one to one, each phrase gets its own speech segment."""
    est = [t is None for t in times]
    i = 0
    while i < len(words):
        if times[i] is not None: i += 1; continue
        j = i
        while j < len(words) and times[j] is None: j += 1
        g0 = times[i - 1][1] if i > 0 else 0.0
        g1 = times[j][0] if j < len(words) else total
        if g1 - g0 < 0.12 * (j - i):  # no room: borrow from the neighbours
            g0 = times[i - 1][0] if i > 0 else 0.0
        segs = speech_in(g0, g1, sil)
        idx = list(range(i, j))
        groups, cur = [], []
        for k in idx:
            cur.append(k)
            if PAUSE_END.search(words[k]): groups.append(cur); cur = []
        if cur: groups.append(cur)
        if len(groups) == len(segs) and len(segs) > 1:
            for grp, (a, b) in zip(groups, segs):
                for k, t in spread(grp, words, [(a, b)], a, b).items(): times[k] = t
        else:
            for k, t in spread(idx, words, segs, g0, g1).items(): times[k] = t
        i = j
    return est


def tidy(times, sil):
    # a word starting inside a pause (whisper often starts a word early) begins when the speech resumes
    for a, c in sil:
        if c - a < 0.25: continue
        for k, t in enumerate(times):
            if a + 0.02 < t[0] < c and (k == 0 or times[k - 1][1] <= a + 0.15):
                t[0] = round(c, 3); t[1] = max(t[1], round(c + 0.12, 3))
    # whisper word starts can lag a little after a pause: snap the first word after each pause to where the speech resumes
    for _, c in sil:
        k = next((k for k, t in enumerate(times) if t[0] >= c - 0.05), None)
        if k is not None and times[k][0] - c < 0.5 and (k == 0 or times[k - 1][1] <= c + 0.1):
            times[k][0] = round(c, 3)
    if times: times[0][0] = min(times[0][0], 0.0 if times[0][0] < 0.5 else times[0][0])
    for k in range(len(times) - 1):  # keep words in order and non-overlapping
        times[k + 1][0] = max(times[k + 1][0], times[k][0] + 0.05)
        times[k][1] = max(min(times[k][1], times[k + 1][0]), times[k][0] + 0.05)


def check_sync(lines, sil, total):
    """Does the timeline follow the voice? Returns (ok, report dict). Works on any timeline.json + the voice's pauses."""
    words = [w for l in lines for w in l['words']]
    n = len(words)
    est = [bool(w.get('est')) for w in words]
    known = 'est' in (words[0] if words else {})
    coverage = 1 - sum(est) / max(1, n) if known else None
    # longest run of estimated words, in seconds
    run, k = 0.0, 0
    while k < n:
        if not est[k]: k += 1; continue
        j = k
        while j < n and est[j]: j += 1
        run = max(run, words[j - 1]['t1'] - words[k]['t0']); k = j
    # words that sit mostly inside a real pause (>= 0.25 s): the caption would show while nothing is said
    long_sil = [(a, b) for a, b in sil if b - a >= 0.25]
    in_sil = []
    for w in words:
        d = max(0.05, w['t1'] - w['t0'])
        ov = sum(max(0.0, min(w['t1'], b) - max(w['t0'], a)) for a, b in long_sil)
        if ov / d > 0.6 and ov > 0.15: in_sil.append(f"{w['w']}@{w['t0']:.2f}")
    # each line after a pause should start where the speech resumes (a pause end), not before or long after it
    onsets = [b for a, b in sil if b - a >= 0.25]
    off = []
    for l in lines[1:]:
        t0 = l['t0']
        near = min((abs(t0 - o) for o in onsets), default=9.9)
        inside = any(a + 0.1 < t0 < b - 0.25 for a, b in long_sil)
        prev_pause = any(abs(o - t0) < 1.5 for o in onsets)
        if inside or (prev_pause and near > 0.4): off.append(f"line {l['i']} @{t0:.2f}")
    fails = []
    if coverage is not None and coverage < MIN_COVERAGE: fails.append(f'only {coverage:.0%} of words matched the audio')
    if run > MAX_EST_RUN_S: fails.append(f'{run:.1f}s of words in a row were guessed, not heard')
    if len(in_sil) > MAX_WORDS_IN_SILENCE: fails.append(f'{len(in_sil)} words are timed inside pauses: {", ".join(in_sil[:8])}')
    if len(off) > MAX_LATE_EARLY_LINES * max(1, len(lines) - 1): fails.append(f'{len(off)} lines don\'t start where the voice does: {", ".join(off[:8])}')
    rep = dict(ok=not fails, coverage=None if coverage is None else round(coverage, 3), longestGuessS=round(run, 2),
               wordsInPauses=in_sil, linesOff=off, problems=fails, total=total)
    return not fails, rep


def main(ep, narr, audio, model=None, force=False):
    os.makedirs(ep, exist_ok=True)
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model = model or os.path.join(root, 'whisper_small')
    lines = [l.strip() for l in open(narr, encoding='utf-8') if l.strip()]
    open(os.path.join(ep, 'lines.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    narr_wav = os.path.join(ep, 'narr.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', audio, '-ac', '1', '-ar', '44100', narr_wav], check=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', narr_wav], capture_output=True, text=True).stdout)
    sil = silences(narr_wav)
    end = dur
    if sil and sil[-1][1] >= dur - 0.05: end = sil[-1][0]; sil = sil[:-1]
    total = round(min(dur, end + 0.05), 2)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', narr_wav, '-t', str(total), os.path.join(ep, 'voice.wav')], check=True)

    from faster_whisper import WhisperModel
    wm = WhisperModel(model, device='cpu', compute_type='int8')
    import soundfile as sf  # decode ourselves (faster-whisper's PyAV path breaks with some av versions)
    w16 = os.path.join(ep, 'n16.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', narr_wav, '-ac', '1', '-ar', '16000', w16], check=True)
    pcm, _ = sf.read(w16, dtype='float32')

    script = [(li, w) for li, l in enumerate(lines) for w in l.split()]
    words = [w for _, w in script]
    # pass 1: the whole file (no script prompt: a long prompt makes whisper skip or invent stretches)
    asr_full = transcribe(wm, pcm)
    # pass 2: short windows cut at pauses, each transcribed on its own
    asr_win = []
    for a, b in windows(sil, total):
        s0, s1 = max(0, int((a - 0.1) * 16000)), min(len(pcm), int((b + 0.1) * 16000))
        asr_win += [x for x in transcribe(wm, pcm[s0:s1], offset=s0 / 16000) if a - 0.15 <= (x['t0'] + x['t1']) / 2 <= b + 0.15]
    passes = {'full': (asr_full, match(words, asr_full)), 'windows': (asr_win, match(words, asr_win))}
    for name, (_, t) in passes.items(): print(f'whisper pass {name}: {sum(x is not None for x in t)}/{len(words)} script words matched')
    best = max(passes, key=lambda p: sum(x is not None for x in passes[p][1]))
    asr, times = passes[best]
    # fill gaps in the best pass from the other one where that keeps the order
    other = passes['full' if best == 'windows' else 'windows'][1]
    for k in range(len(times)):
        if times[k] is None and other[k] is not None:
            prev = next((times[j][1] for j in range(k - 1, -1, -1) if times[j] is not None), 0.0)
            nxt = next((times[j][0] for j in range(k + 1, len(times)) if times[j] is not None), total)
            if prev - 0.1 <= other[k][0] and other[k][1] <= nxt + 0.1: times[k] = list(other[k])
    json.dump(dict(full=asr_full, windows=asr_win, used=best), open(os.path.join(ep, 'asr.json'), 'w'), indent=0)

    est = fill(times, words, sil, total)
    tidy(times, sil)
    bounds = [0.0] + [x for s in sil for x in s] + [total]
    chunks = [(bounds[i], bounds[i + 1]) for i in range(0, len(bounds) - 1, 2)]
    out = []
    for li, text in enumerate(lines):
        ws = []
        for k, (l2, w) in enumerate(script):
            if l2 != li: continue
            d = dict(w=w, t0=times[k][0], t1=times[k][1])
            if est[k]: d['est'] = True
            ws.append(d)
        t0, t1 = ws[0]['t0'], ws[-1]['t1']
        ch = [[round(c0, 2), round(c1, 2)] for c0, c1 in chunks if c1 > t0 + 0.05 and c0 < t1 - 0.05] or [[t0, t1]]
        out.append(dict(i=li, text=text, t0=round(t0, 3), t1=round(t1, 3), words=ws, chunks=ch))
    for l in out:  # mark every word so the check knows they were tested
        for w in l['words']: w.setdefault('est', False)
    ok, rep = check_sync(out, sil, total)
    json.dump(dict(lines=out, total=total, sync=rep), open(os.path.join(ep, 'timeline.json'), 'w'), indent=1)
    json.dump(dict(rep, silences=sil), open(os.path.join(ep, 'sync.json'), 'w'), indent=1)
    print(f'timeline.json: {len(lines)} lines, {len(script)} words, total {total}s (word times from the {best} pass)')
    for o in out: print(o['i'], f"{o['t0']:.2f}-{o['t1']:.2f}", ' '.join(f"{w['w']}@{w['t0']:.2f}{'?' if w['est'] else ''}" for w in o['words']))
    print('(? = word not heard by whisper, placed in the speech between its neighbours)')
    if ok:
        print(f"SYNC OK: {rep['coverage']:.0%} of words heard, longest guessed stretch {rep['longestGuessS']}s")
    else:
        print('SYNC FAIL: the captions would not follow the voice.\n  - ' + '\n  - '.join(rep['problems']))
        if not force: sys.exit(2)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--force']
    main(*args, force='--force' in sys.argv)
