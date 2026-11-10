"""Make timeline.json for a sticky episode from its narration text and the owner's MP3.

  python3 timeline.py <episode_dir> <narration.txt> <audio.mp3> [whisper_model_dir]

Writes into <episode_dir>: lines.txt (one narration line per row), voice.wav (the voice, trailing silence trimmed),
timeline.json ({lines:[{i,text,t0,t1,words:[{w,t0,t1}],chunks:[[t0,t1],...]}], total}) and asr.json.
Word times come from faster-whisper word timestamps on the repo's whisper_small model, aligned to the exact
narration words (so captions always show the script's spelling). Chunks are the pauses found by ffmpeg silencedetect.
"""
import difflib, json, os, re, subprocess, sys

def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower().replace("’", "'"))

def silences(wav):
    out = subprocess.run(['ffmpeg', '-i', wav, '-af', 'silencedetect=noise=-35dB:d=0.18', '-f', 'null', '-'], capture_output=True, text=True).stderr
    v = [float(x) for x in re.findall(r'silence_(?:start|end): ([0-9.]+)', out)]
    return [(v[i], v[i + 1]) for i in range(0, len(v) - 1, 2)]

def main(ep, narr, audio, model=None):
    os.makedirs(ep, exist_ok=True)
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model = model or os.path.join(root, 'whisper_small')
    lines = [l.strip() for l in open(narr, encoding='utf-8') if l.strip()]
    open(os.path.join(ep, 'lines.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    narr_wav = os.path.join(ep, 'narr.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', audio, '-ac', '1', '-ar', '44100', narr_wav], check=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', narr_wav], capture_output=True, text=True).stdout)
    sil = silences(narr_wav)
    # leading/trailing silence
    end = dur
    if sil and sil[-1][1] >= dur - 0.05: end = sil[-1][0]; sil = sil[:-1]
    total = round(min(dur, end + 0.05), 2)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', narr_wav, '-t', str(total), os.path.join(ep, 'voice.wav')], check=True)

    from faster_whisper import WhisperModel
    wm = WhisperModel(model, device='cpu', compute_type='int8')
    segs, _ = wm.transcribe(narr_wav, language='en', word_timestamps=True, beam_size=5, vad_filter=False,
                            initial_prompt=' '.join(lines)[:800])
    asr = [dict(w=w.word.strip(), t0=round(w.start, 3), t1=round(w.end, 3)) for s in segs for w in s.words]
    json.dump(asr, open(os.path.join(ep, 'asr.json'), 'w'), indent=0)

    script = [(li, w) for li, l in enumerate(lines) for w in l.split()]
    a = [norm(w) for _, w in script]; b = [norm(x['w']) for x in asr]
    times = [None] * len(script)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            x = asr[blk.b + k]; times[blk.a + k] = [x['t0'], x['t1']]
    # fill unmatched runs by spreading them over the gap, weighted by word length
    i = 0
    while i < len(script):
        if times[i] is not None: i += 1; continue
        j = i
        while j < len(script) and times[j] is None: j += 1
        g0 = times[i - 1][1] if i > 0 else 0.0
        g1 = times[j][0] if j < len(script) else total
        if g1 - g0 < 0.12 * (j - i):  # no room: borrow from the neighbours
            g0 = times[i - 1][0] if i > 0 else 0.0
        wts = [len(norm(script[k][1])) + 1.5 for k in range(i, j)]; tot = sum(wts); x = g0
        for k, wgt in zip(range(i, j), wts):
            d = (g1 - g0) * wgt / tot; times[k] = [round(x, 3), round(x + d, 3)]; x += d
        i = j
    for k in range(len(times) - 1):  # keep words in order and non-overlapping
        times[k + 1][0] = max(times[k + 1][0], times[k][0] + 0.05)
        times[k][1] = max(min(times[k][1], times[k + 1][0]), times[k][0] + 0.05)
    bounds = [0.0] + [x for s in sil for x in s] + [total]
    chunks = [(bounds[i], bounds[i + 1]) for i in range(0, len(bounds) - 1, 2)]
    out = []
    for li, text in enumerate(lines):
        ws = [dict(w=w, t0=times[k][0], t1=times[k][1]) for k, (l2, w) in enumerate(script) if l2 == li]
        t0, t1 = ws[0]['t0'], ws[-1]['t1']
        ch = [[round(c0, 2), round(c1, 2)] for c0, c1 in chunks if c1 > t0 + 0.05 and c0 < t1 - 0.05] or [[t0, t1]]
        out.append(dict(i=li, text=text, t0=round(t0, 3), t1=round(t1, 3), words=ws, chunks=ch))
    json.dump(dict(lines=out, total=total), open(os.path.join(ep, 'timeline.json'), 'w'), indent=1)
    matched = sum(t is not None for t in times)
    print(f'timeline.json: {len(lines)} lines, {len(script)} words, total {total}s')
    for o in out: print(o['i'], f"{o['t0']:.2f}-{o['t1']:.2f}", ' '.join(f"{w['w']}@{w['t0']:.2f}" for w in o['words']))

if __name__ == '__main__':
    main(*sys.argv[1:])
