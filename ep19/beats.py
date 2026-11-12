"""ep19 timeline, 30 fps.  Every line is the owner's MP3 as-is; FILE[k] = film frame where sample 0 of that file plays.
Shots (brief order): A Mom MCU (discovery) | B Doug MCU (calm correction) | C Mom medium (shows the post) |
OTS over Doug's shoulder onto the phone (2016) | D Doug CU ("Ma... 2016 pa 'tong post.") | E Mom MCU (punchline) |
F Doug tight CU: turns to the lens, ~2 s silent stare | hard cut to black."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
MS = json.load(open(os.path.join(HERE, 'vo', 'measure.json')))
LINES = ['mom_dialogue_1', 'doug_dialogue_1', 'mom_dialogue_2', 'doug_dialogue_2', 'mom_dialogue_3']
def frames(k): return int(round(MS[k]['dur'] * 30))           # file length in frames
FILE = {}
FILE['mom_dialogue_1'] = 4                                       # "NAK!" lands at ~0.2 s: the hook is immediate
A_END = FILE['mom_dialogue_1'] + frames('mom_dialogue_1') + 3    # cut to Doug just after her last syllable
FILE['doug_dialogue_1'] = A_END + 10                             # he looks up first, then answers (~0.4 s turn gap)
B_END = FILE['doug_dialogue_1'] + frames('doug_dialogue_1') - 1
FILE['mom_dialogue_2'] = B_END + 7
C_END = FILE['mom_dialogue_2'] + frames('mom_dialogue_2') + 3
O_END = C_END + 34                                               # the over-the-shoulder insert: ~1.1 s, no dialogue
FILE['doug_dialogue_2'] = O_END + 5                              # a brief pause on his face before "Ma..."
D_END = FILE['doug_dialogue_2'] + frames('doug_dialogue_2') - 2
FILE['mom_dialogue_3'] = D_END + 6
E_END = FILE['mom_dialogue_3'] + frames('mom_dialogue_3') + 1
SPEECH_END = FILE['mom_dialogue_3'] + int(round(MS['mom_dialogue_3']['e'] * 30))
F0 = E_END + 1
TURN = (F0 + 3, F0 + 15)                                         # Doug turns his head to the lens
BLACK = SPEECH_END + 66                                          # ~2.2 s of silence after her last syllable, then hard cut
N = BLACK + 7                                                    # ~0.25 s of black
SH = dict(A=(1, A_END), B=(A_END + 1, B_END), C=(B_END + 1, C_END), O=(C_END + 1, O_END), D=(O_END + 1, D_END),
          E=(D_END + 1, E_END), F=(F0, BLACK - 1))
STEP = dict(A=1, B=2, C=2, O=2, D=2, E=2, F=2)
# acting beats
A_LEAN = (6, 14)                 # Mom: eyes pop, leans in to the phone
A_TURN = (16, 26)                # ... turns to Doug, phone comes up
B_LOOKUP = SH['B'][0] + 3        # Doug's eyes come up off his phone
C_RAISE = (SH['C'][0] + 2, FILE['mom_dialogue_2'] + 34)   # Mom pushes the phone out toward Doug ("Nasa Facebook oh!")
C_TAP = FILE['mom_dialogue_2'] + 50                      # she taps the screen on "oh!"
D_LEAN = (SH['C'][1] - 6, SH['O'][0] + 14)               # Doug leans in to read (seen in the OTS, carried into D)
D_READ = SH['O'][0] + 8          # eyes on the date
E_BACK = FILE['mom_dialogue_3'] + 4      # Mom: slight backward move on "AY GANUN?"
E_NOD = (FILE['mom_dialogue_3'] + 70, FILE['mom_dialogue_3'] + 86)
if __name__ == '__main__':
    for k, v in SH.items(): print(k, v, round((v[1] - v[0] + 1) / 30, 2), 's')
    print('FILE', FILE); print('speech end', SPEECH_END, 'BLACK', BLACK, 'N', N, round(N / 30, 2), 's')
    print('silence', round((BLACK - SPEECH_END) / 30, 2), 's')
