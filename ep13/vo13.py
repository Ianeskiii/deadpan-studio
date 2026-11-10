"""Original anime dialogue (JP) + matching English subtitles. Timeline escalates; then a sudden stop."""
import sys, json, numpy as np, soundfile as sf
sys.path.insert(0, '.'); from jtts import jp
SR = 24000; H, R = 'jm_kumo', 'jf_alpha'
# (speaker, japanese, subtitle, speed, gap-before-in-seconds)
LINES = [
 # scene 1 - watching normally
 (H, 'お前には負けない！', "I won't lose to you!", 1.0, 0.8),
 # scene 2 - the eye movement
 (R, 'まだ終わっていない！', "This isn't over yet!", 1.05, 0.9),
 (H, 'なぜ戦うんだ！', 'Why do you fight?!', 1.15, 0.5),
 (R, '答える必要はない！', "I don't need to answer that!", 1.2, 0.35),
 # scene 3 - escalation: arguing, faster
 (H, '約束したからだ！', 'Because I made a promise!', 1.3, 0.15),
 (R, 'くだらない！', 'Pathetic!', 1.35, 0.06),
 (H, '大事なんだ！', 'It matters to me!', 1.35, 0.05),
 (R, '黙れ！', 'Shut up!', 1.35, 0.04),
 (H, '嫌だ！', 'No!', 1.35, 0.03),
 (R, '行くぞ！', 'Here I come!', 1.4, 0.03),
 # scene 4 - even faster, back-to-back
 (H, '今だ！', 'Now!', 1.35, 0.02),
 (R, 'させるか！', 'Not so fast!', 1.35, 0.0),
 (H, 'そこだ！', 'There!', 1.35, 0.0),
 (R, 'まだだ！', 'Not yet!', 1.5, 0.0),
 (H, '終わりだ！', "It's over!", 1.5, 0.0),
 (R, '負けない！', "I won't lose!", 1.35, 0.0),
 (H, 'なにっ！', 'What?!', 1.35, 0.0),
]
out = []; t = 0.0
for i, (spk, jtxt, sub, sp, gap) in enumerate(LINES):
    a, ps = jp(jtxt, spk, sp)
    a = a / (np.abs(a).max() + 1e-9) * 0.9
    sf.write(f'vo/l{i:02d}.wav', a, SR)
    t += gap; d = len(a) / SR
    out.append(dict(i=i, spk=spk, jp=jtxt, sub=sub, t=round(t, 3), d=round(d, 3), ph=ps))
    t += d
END_TALK = t
SIL = 1.0                 # the awkward silence
T = dict(lines=out, end_talk=round(END_TALK, 3), black=round(END_TALK + SIL, 3), end=round(END_TALK + SIL + 0.5, 3))
json.dump(T, open('vo/timing.json', 'w'), indent=1, ensure_ascii=False)
for l in out: print(f"{l['t']:6.2f} +{l['d']:.2f}  {l['spk']:8s} {l['jp']}  /  {l['sub']}")
print('talk ends', T['end_talk'], 'black at', T['black'], 'end', T['end'])
