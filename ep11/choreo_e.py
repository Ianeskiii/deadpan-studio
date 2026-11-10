# ============================================================ CHOREOGRAPHY v5 - robbery vs. carefree dancing
# Doug faces the camera the whole time, eyes closed, never reacts. Ricky (screen-left) does all the struggling.
DX, DY = 0.3, 3.4
RX0 = -0.95
lids(doug, 1, 40); lids(ricky, 1, 26)
exec(open(os.path.join(HERE, 'helpers_e.py')).read())
hp2 = arms(N='hp', P='hp')
def sing(f0, f1, step=7):
    for k, f in enumerate(range(f0, f1 + 1, step)): mouth_open(doug, f, (0.7, 0.2, 0.9, 0.35)[k % 4])
def eyes_r(f, x, z):
    for e in ricky['eyes']: key(e, 'rotation_euler', f, Euler((D(x), 0, D(z))))
def rsay(wav, f0):
    with wave.open(wav) as w_:
        sr = w_.getframerate(); a = np.frombuffer(w_.readframes(w_.getnframes()), '<i2').astype(float)
    hop = sr // 30; rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)]); rms /= rms.max() + 1e-9
    for i, v in enumerate(list(rms) + [0, 0]):
        mouth_open(ricky, f0 + i, min(1.0, max(0.0, (v - 0.08) / 0.55)))
ricky_smile.hide_render = True; ricky_smile.keyframe_insert('hide_render', frame=1)

# ---------------------------------------------------------------- DOUG: one continuous dance (global frames)
GRAB, SLOW0, SLOW1, SPIN, RELEASE = 166, 196, 285, 391, 400
doug_r.walk(1, 90, (DX, 5.2), (DX, DY), 0, steps=6, arms=hp2, lean=6, bob=0.045, sway=4,
            bendfun=lambda ph: (0, 34 * math.sin(ph) * doug_r.SIDE))
doug_r.place(91, (DX, DY), 0)
fling = arms(N='hp', P='up')
dA = [ST(doug_r, 91, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide'),
      ST(doug_r, 118, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide'),
      ST(doug_r, 121, (0, 0, 0.04), (-4, 6, 4), 1.04, fling, 'wide'),
      ST(doug_r, 132, (0, 0, 0.0), (0, 0, 0), 1.0, fling, 'wide'),
      ST(doug_r, 140, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide'),
      ST(doug_r, SLOW0 - 1, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide')]
K1 = kembot(doug_r, 91, amp=36, twist=10, shift=0.05)
run(doug_r, 91, SLOW0 - 1, dA, K1)
# slow-mo: big slow giling, hand behind head, arm whip up (half-speed timing)
whip1 = ((0.5, -0.05, D_EZ + 0.55), ('auto', (1, 0, 0))); whip2 = ((0.25, -0.15, D_EZ + 0.78), ('auto', (1, 0, 0)))
dB = [ST(doug_r, SLOW0, (0, 0, -0.06), (-6, 0, 0), 1.0, arms(N='hp', P='behind'), 'wide'),
      ST(doug_r, SLOW0 + 50, (0, 0, -0.08), (-8, 0, 0), 1.0, arms(N='hp', P='behind'), 'wide'),
      ST(doug_r, SLOW0 + 62, (0, 0, -0.04), (-4, 0, 0), 1.0, arms(N='hp', P=whip1), 'wide'),
      ST(doug_r, SLOW0 + 74, (0, 0, 0.0), (-2, 4, 0), 1.03, arms(N='hp', P=whip2), 'wide'),
      ST(doug_r, SLOW1, (0, 0, -0.02), (2, 0, 0), 1.0, arms(N='hp', P=whip2), 'wide')]
G1 = giling(doug_r, SLOW0, period=60, amp=38, shift=0.06)
run(doug_r, SLOW0, SLOW1, dB, G1)
G2 = giling(doug_r, SLOW1 + 1, period=30, amp=32, shift=0.05)
run(doug_r, SLOW1 + 1, 300, [ST(doug_r, SLOW1 + 1, (0, 0, -0.02), (3, 0, 0), 1.0, hp2, 'wide'), ST(doug_r, 300, (0, 0, -0.02), (3, 0, 0), 1.0, hp2, 'wide')], G2)
# vogue + kembot, then fist pumps (toward camera) + giling
V1 = {'P': ((-0.04, -0.5, D_EZ + 0.18), (0.42, -0.25, D_EZ - 0.1)), 'N': ((0.06, -0.45, D_EZ - 0.15), (-0.45, -0.2, 0.55))}
V2 = {'N': ((0.04, -0.5, D_EZ + 0.18), (-0.42, -0.25, D_EZ - 0.1)), 'P': ((-0.06, -0.45, D_EZ - 0.15), (0.45, -0.2, 0.55))}
V3 = {'P': ((0.3, -0.42, D_EZ + 0.35), (0.5, -0.15, D_EZ)), 'N': ((-0.3, -0.42, D_EZ + 0.35), (-0.5, -0.15, D_EZ))}
FP1 = {'P': ((0.1, -0.9, 0.72), ('auto', (1, 0, -0.3))), 'N': ((-0.28, -0.12, 0.72), (-0.5, 0.15, 0.55))}
FP2 = {'N': ((-0.1, -0.9, 0.72), ('auto', (-1, 0, -0.3))), 'P': ((0.28, -0.12, 0.72), (0.5, 0.15, 0.55))}
K2 = kembot(doug_r, 301, amp=36, twist=10, shift=0.05)
run(doug_r, 301, 345, [ST(doug_r, f, (0, 0, -0.02), (3, 0, 0), 1.0, (V1, V3, V2, V3)[k % 4], 'wide') for k, f in enumerate(range(301, 346, 7))], K2)
G3 = giling(doug_r, 346, period=30, amp=32, shift=0.05)
run(doug_r, 346, SPIN - 1, [ST(doug_r, f, (0, 0, -0.03), (8, 0, 8 * (1 if k % 2 == 0 else -1)), 1.0, FP1 if k % 2 == 0 else FP2, 'wide') for k, f in enumerate(range(346, SPIN, 7))], G3)
# the spin (arms out) - unaware he just whipped Ricky around
T_ARMS = {'N': ((-0.85, -0.05, 0.62), ('auto', (-1, 0, 0.3))), 'P': ((0.85, -0.05, 0.62), ('auto', (1, 0, 0.3)))}
run(doug_r, SPIN, 405, [ST(doug_r, SPIN, (0, 0, 0.03), (0, 0, 0), 1.0, T_ARMS, 'stand'), ST(doug_r, 405, (0, 0, 0.0), (0, 0, 0), 1.0, T_ARMS, 'stand')])
doug_r.place(SPIN, (DX, DY), 0); doug_r.place(405, (DX, DY), 360)
K3 = kembot(doug_r, 406, amp=36, twist=10, shift=0.05)
run(doug_r, 406, 450, [ST(doug_r, 406, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide'), ST(doug_r, 450, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide')], K3)
doug_r.place(450, (DX, DY), 360)
doug_r.walk(451, 480, (DX, DY), (1.55, 2.85), 360 + 62, steps=2, arms=hp2, lean=6, bob=0.045, sway=4,
            bendfun=lambda ph: (0, 34 * math.sin(ph) * doug_r.SIDE))
sing(91, 480)
lids(doug, 136, 40); lids(doug, 138, 80); lids(doug, 166, 40)          # blissfully shut while Ricky waves at him

# Doug's hip side (-1..1, + = toward screen-right / away from Ricky) from the same layers
def hip_side(f):
    L = K1 if f < SLOW0 else G1 if f <= SLOW1 else G2 if f <= 300 else K2 if f <= 345 else G3
    return L(f)[2][1] / 36.0 * doug_r.SIDE

# ---------------------------------------------------------------- RICKY
ricky_r.place(1, (-6, 6), 90); ricky_r.place(74, (-6, 6), 90)
ricky_r.walk(75, 98, (-2.7, 3.25), (RX0 + 0.25, DY - 0.05), 90, steps=4, arms={'N': ((-0.36, -0.05, 0.05), ('auto', (-1, 0.3, 0))), 'P': ((0.36, -0.05, 0.05), ('auto', (1, 0.3, 0)))}, lean=4, bob=0.04, sway=5)
RD = RX0 + 0.25
demand = {'P': ((0.12, -0.68, 0.78), ('auto', (1, 0, -0.4))), 'N': ((-0.33, 0.05, 0.25), (-0.42, 0.05, 0.42))}
ricky_r.place(99, (RD, DY), 90)
ricky_r.pose(99, up=(0, 0, 0), rot=(-4, 0, 0), arms=demand, legs=LEGS['stand']())
ricky_r.pose(112, up=(0, 0, 0.02), rot=(-8, 0, 0), arms=demand, legs=LEGS['stand']())
ricky_r.pose(126, up=(0, 0, 0), rot=(-4, 0, 6), arms=demand, legs=LEGS['stand']())
brows(ricky, 99, -0.03, 24, RBZ); eyes_r(99, 0, 0)
rsay(os.path.join(HERE, 'vo_demand.wav'), 101)
# steps in and waves a hand in front of Doug's face (136-165)
ricky_r.place(134, (RD, DY), 90); ricky_r.place(138, (-0.42, DY - 0.08), 90)
wave_hand = lambda dx: {'P': ((-0.38 + dx, -0.62, 1.02), ('auto', (1, 0, -0.2))), 'N': ((-0.33, 0.05, 0.25), (-0.42, 0.05, 0.42))}
for k, f in enumerate(range(138, 166, 4)):
    ricky_r.pose(f, up=(0, 0, 0.04), rot=(6, 0, 0), arms=wave_hand(0.16 if k % 2 else -0.06), legs=LEGS['stand']())
# grabs the bag on the beat and pulls
ricky_r.place(GRAB - 2, (-0.42, DY - 0.08), 90); ricky_r.place(GRAB + 4, (-0.6, DY), 90)
grab = {'N': ((-0.08, -0.6, 0.38), ('auto', (-1, 0, -0.3))), 'P': ((0.08, -0.6, 0.38), ('auto', (1, 0, -0.3)))}
ricky_r.pose(GRAB + 4, up=(0, 0, -0.08), rot=(16, 0, 0), arms=grab, legs=LEGS['brace']())
pullA = arms(N='pull', P='pull')
# struggle: Ricky gets yanked around by Doug's hips (strap still on Doug's shoulder)
for f in range(GRAB + 10, SPIN, 2):
    h = hip_side(f)
    effort = 1.0 if f > 300 else 0.7
    shake = 0.012 * math.sin(f * 1.7) * effort
    ricky_r.place(f, (RX0 + 0.32 * h + shake, DY + 0.04 * math.sin(f * 0.3)), 90 - 10 * h)
    ricky_r.pose(f, up=(0, 0, -0.1 - 0.03 * effort), rot=(-24 + 18 * h, 4 * math.sin(f * 0.9) * effort, 8 * h), arms=pullA,
                 legs={'N': ((-0.18, -0.5 + 0.15 * h, 0), (0, -1, 0.4)), 'P': ((0.2, 0.32 + 0.1 * h, 0), (0, -1, 0.2))})
brows(ricky, GRAB, -0.03, 24, RBZ); lids(ricky, GRAB, 40)
mouth_open(ricky, GRAB + 10, 0.6); mouth_open(ricky, 300, 0.8)
# whipped around by the spin, flung, lands on his butt (screen-left)
for f in range(SPIN, RELEASE + 1):
    th = D(360 * (f - SPIN) / (405 - SPIN))
    pos = V(DX, DY, 0) + Matrix.Rotation(th, 3, 'Z') @ V(-1.2, 0, 0)
    ricky_r.place(f, (pos.x, pos.y), 90 + math.degrees(th), z=0.05 * math.sin(math.pi * (f - SPIN) / (RELEASE - SPIN)))
    ricky_r.pose(f, up=(0, 0, -0.05), rot=(-30, 0, 0), arms=pullA, legs={'N': ((-0.15, -0.4, 0.15), (0, -1, 0.4)), 'P': ((0.15, 0.3, 0.1), (0, -1, 0.2))})
SITP = (-1.55, 3.25)
ricky_r.place(RELEASE + 5, (-1.25, 3.1), 70, z=0.35); ricky_r.place(RELEASE + 10, SITP, 80)
ricky_r.pose(RELEASE + 5, up=(0, 0, -0.1), rot=(-40, 0, 20), arms={'N': ((-0.45, 0.1, 0.9), ('auto', (-1, 0, 0))), 'P': ((0.45, 0.1, 0.9), ('auto', (1, 0, 0)))}, legs=LEGS['sit']())
ricky_r.pose(RELEASE + 10, up=(0, 0, -0.4), rot=(-12, 0, 0), sq=0.9, arms={'N': ((-0.38, -0.2, 0.05), ('auto', (-1, 0.3, 0))), 'P': ((0.38, -0.2, 0.05), ('auto', (1, 0.3, 0)))}, legs=LEGS['sit']())
ricky_r.pose(RELEASE + 14, up=(0, 0, -0.34), rot=(-14, 0, 0), sq=1.04, arms={'N': ((-0.38, -0.2, 0.05), ('auto', (-1, 0.3, 0))), 'P': ((0.38, -0.2, 0.05), ('auto', (1, 0.3, 0)))}, legs=LEGS['sit']())
lids(ricky, RELEASE + 9, 40); lids(ricky, RELEASE + 10, 0)
mouth_open(ricky, RELEASE + 9, 0.0); mouth_open(ricky, RELEASE + 10, 1.0); mouth_open(ricky, RELEASE + 18, 0.2)
# confused, scratches his head: "Ugh... forget it."
scratch = lambda dx: {'P': ((0.1 + dx, -0.05, R_EZ + 0.32), ('auto', (1, -0.3, 0))), 'N': ((-0.38, -0.2, 0.05), ('auto', (-1, 0.3, 0)))}
for k, f in enumerate(range(421, 451, 5)):
    ricky_r.pose(f, up=(0, 0, -0.37), rot=(-10, 0, 10 if k % 2 else 4), arms=scratch(0.05 if k % 2 else -0.03), legs=LEGS['sit']())
eyes_r(421, -8, 18); eyes_r(432, -8, -14); eyes_r(442, -4, 10)
for i, bp in enumerate(ricky['brows']):
    key(bp, 'location', 421, V(bp.location.x, bp.location.y, RBZ[i] + (0.05 if i == 1 else 0.0)))
    key(bp, 'rotation_euler', 421, Euler((0, (-1 if i == 0 else 1) * D(-12 if i == 1 else 6), 0)))
lids(ricky, 421, 30)
rsay(os.path.join(HERE, 'vo_giveup.wav'), 424)
# throws his hands up, flops back - gives up
ricky_r.pose(453, up=(0, 0, -0.36), rot=(-14, 0, 0), arms={'N': ((-0.45, -0.1, R_EZ + 0.45), ('auto', (-1, 0, 0))), 'P': ((0.45, -0.1, R_EZ + 0.45), ('auto', (1, 0, 0)))}, legs=LEGS['sit']())
ricky_r.pose(466, up=(0, 0, -0.4), rot=(-30, 0, 0), arms={'N': ((-0.42, 0.1, 0.05), ('auto', (-1, 0.3, 0))), 'P': ((0.42, 0.1, 0.05), ('auto', (1, 0.3, 0)))}, legs=LEGS['sit']())
ricky_r.pose(480, up=(0, 0, -0.4), rot=(-32, 0, 0), arms={'N': ((-0.42, 0.1, 0.05), ('auto', (-1, 0.3, 0))), 'P': ((0.42, 0.1, 0.05), ('auto', (1, 0.3, 0)))}, legs=LEGS['sit']())
lids(ricky, 453, 30); lids(ricky, 466, 60)

