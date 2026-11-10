import json, subprocess
exec(open('timing13.py').read().split('ORDER =')[0])
# same takes; the ending gets room for Doug's look (cup -> barista) before he speaks
ORDER = [('b1', 1.85), ('d1', 0.6), ('b2', 0.8), ('d2', 0.85), ('b3', 0.5), ('b4', 3.6)]
T = {}; end = 0
for name, gap in ORDER:
    sg = spans(f'vo3/{name}.wav'); s, e = sg[0][0], sg[-1][1]
    st = gap if name == 'b1' else end + gap; ft = st - s
    T[name] = dict(file_t=round(ft, 3), s=round(st, 3), e=round(ft + e, 3), f=int(round(ft * 30)) + 1,
                   fs=int(round(st * 30)) + 1, fe=int(round((ft + e) * 30)) + 1, words=[int(round((ft + a) * 30)) + 1 for a, b in sg])
    end = ft + e
T['N'] = T['b4']['fe'] + 266; T['END'] = round(T['N'] / 30, 3)
json.dump(T, open('vo3/timing16.json', 'w'), indent=1)
for k in ('b3', 'b4', 'N', 'END'): print(k, T[k])
