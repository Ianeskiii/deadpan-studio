"""Place each line on the timeline (speech onset frame) and derive every beat/shot from the real take lengths.
Writes vo/timing.json and beats.json.  30 fps."""
import json, numpy as np, soundfile as sf
def spans(p, thr=0.1):
    a, sr = sf.read(p); h = sr // 100
    r = np.array([np.sqrt(np.mean(a[i:i + h] ** 2)) for i in range(0, len(a), h)]); on = r > thr * r.max()
    segs, s = [], None
    for i, v in enumerate(on):
        if v and s is None: s = i
        if not v and s is not None:
            if i - s > 4: segs.append((s / 100, i / 100))
            s = None
    if s is not None: segs.append((s / 100, len(on) / 100))
    return segs
T = {}
def place(name, onset_frame):
    sg = spans(f'vo/{name}.wav'); s, e = sg[0][0], sg[-1][1]
    st = (onset_frame - 1) / 30; ft = st - s
    T[name] = dict(file_t=round(ft, 3), s=round(st, 3), e=round(ft + e, 3), f=int(round(ft * 30)) + 1,
                   fs=onset_frame, fe=int(round((ft + e) * 30)) + 1, words=[int(round((ft + a) * 30)) + 1 for a, b in sg])
    return T[name]['fe']
B = {}
# ---- A  wide two-shot: Doug walks in and stops; Green, mid-bite, notices and freezes; the question; the first lie
B['WALK'] = (1, 26)                 # Doug walks in from screen-left and stops
B['G_BITE'] = (1, 14)               # Green: fork to mouth, a bite, chewing
B['G_RELOAD'] = (16, 30)            # Green loads the fork again, starts raising it
B['G_NOTICE'] = 30                  # Green's eyes catch Doug
B['G_FREEZE'] = 34                  # fork stops dead half way to his mouth
d1e = place('d1', 46)               # Doug: "Did you eat my cake?"
B['G_HES1'] = d1e + 4               # the split-second freeze, then the lie
g1e = place('g1', d1e + 12)         # Green: "What? No."
A_END = g1e + 8
# ---- B  Doug close-up: his eyes drop to the cake on the fork, hold
B['B'] = (A_END + 1, A_END + 34); B['D_TO_FORK'] = A_END + 6
# ---- C  Green medium: he notices the stare, slowly lowers the fork, second lie
C0 = B['B'][1] + 1
B['G_SEE_STARE'] = C0 + 4; B['G_LOWER'] = (C0 + 10, C0 + 34)
B['G_HES2'] = C0 + 36
g2e = place('g2', C0 + 42)          # Green: "I haven't even seen your cake."
B['C'] = (C0, g2e + 8)
# ---- D  Doug close-up: eyes to the box hidden behind Green's hip ... back to Green ... down to the frosting on his mouth
D0 = B['C'][1] + 1
B['D_TO_BOX'] = D0 + 8; B['D_BACK'] = D0 + 24; B['D_TO_MOUTH'] = D0 + 36; B['D_TO_FACE'] = D0 + 52
B['D'] = (D0, D0 + 64)
# ---- E  Green close-up: the frosting; third line
E0 = B['D'][1] + 1
g3e = place('g3', E0 + 8)           # Green: "Why are you looking at me like that?"
B['E'] = (E0, g3e + 10)
# ---- F  silence, MEDIUM on Green (mouth to lap in frame): a piece of cake slips out of his mouth, hangs, drops onto his shirt
F0 = B['E'][1] + 1
B['CRUMB_SLIP'] = (F0 + 12, F0 + 22)  # pushes out over his lower lip
B['CRUMB'] = (F0 + 34, F0 + 44)     # lets go -> falls -> lands on the jacket
B['G_GLANCE'] = F0 + 54              # Green, frozen, glances down at it
B['F'] = (F0, F0 + 64)
# ---- G  wide: both look down at it.  Awkward silence.
G0 = B['F'][1] + 1
B['G_LOOKDOWN'] = B['G_GLANCE']; B['D_LOOKDOWN'] = G0 + 3
B['G'] = (G0, G0 + 40)
# ---- H  Green close-up: slowly looks back up at Doug; completely serious
H0 = B['G'][1] + 1
B['G_LOOKUP'] = (H0 + 2, H0 + 20)
g4e = place('g4', H0 + 28)          # Green: "...That's not mine."
B['H'] = (H0, g4e + 6)
# ---- I  Doug close-up: the long, unimpressed stare.  Then black.
I0 = B['H'][1] + 1
B['D_SLOWBLINK'] = I0 + 22            # hold the stare, one slow blink, then ~0.85 s more of stare
B['I'] = (I0, I0 + 55)
B['BLACK'] = (I0 + 56, I0 + 63)
N = B['BLACK'][1]
B['A'] = (1, A_END)
B['SHOTS'] = {k: B[k] for k in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I')}
B['N'] = N; T['N'] = N; T['END'] = round(N / 30, 3)
json.dump(T, open('vo/timing.json', 'w'), indent=1)
json.dump(B, open('beats.json', 'w'), indent=1)
for k, v in B['SHOTS'].items(): print(k, v, round((v[1] - v[0] + 1) / 30, 2), 's')
print({k: (v['fs'], v['fe']) for k, v in T.items() if isinstance(v, dict)})
print('N', N, round(N / 30, 2), 's')
