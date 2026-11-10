# ============================================================ CHOREOGRAPHY (v3: giling + kembot hip layers)
DX, DY = 0.3, 3.4
TD, TR = (0.55, DY), (-1.05, DY)
lids(doug, 1, 40)
lids(ricky, 1, 26)

# ---- state interpolation + hip layers --------------------------------------
def conc_arms(rig, a):
    out = {}
    for side, (hand, el) in a.items():
        sh = rig.shoulder(side); hand = Vector(hand)
        if isinstance(el, tuple) and len(el) == 2 and el[0] == 'auto':
            elbow = rig.joint(sh, hand, rig.arm_len, el[1])
        else:
            elbow = Vector(el)
        out[side] = (hand, elbow)
    return out
def conc_legs(spec): return {k: (Vector(f_), Vector(b_)) for k, (f_, b_) in spec.items()}
def ST(rig, f, up=(0, 0, 0), rot=(0, 0, 0), sq=1.0, arms=None, legs='stand'):
    return dict(f=f, up=Vector(up), rot=Vector(rot), sq=sq, arms=conc_arms(rig, arms),
                legs=conc_legs(LEGS[legs]() if isinstance(legs, str) else legs))
def smooth(t): return t * t * (3 - 2 * t)
def interp(states, f):
    if f <= states[0]['f']: return states[0]
    if f >= states[-1]['f']: return states[-1]
    for a_, b_ in zip(states, states[1:]):
        if a_['f'] <= f <= b_['f']:
            t = smooth((f - a_['f']) / max(1, b_['f'] - a_['f'])); L = lambda x, y: x.lerp(y, t)
            return dict(up=L(a_['up'], b_['up']), rot=L(a_['rot'], b_['rot']), sq=a_['sq'] + (b_['sq'] - a_['sq']) * t,
                        arms={k: (L(a_['arms'][k][0], b_['arms'][k][0]), L(a_['arms'][k][1], b_['arms'][k][1])) for k in a_['arms']},
                        legs={k: (L(a_['legs'][k][0], b_['legs'][k][0]), L(a_['legs'][k][1], b_['legs'][k][1])) for k in a_['legs']})
def run(rig, f0, f1, states, layer=None):
    for f in range(f0, f1 + 1):
        s_ = interp(states, f)
        dup, drot, bd = layer(f) if layer else (V(0, 0, 0), V(0, 0, 0), (0, 0))
        rig.pose(f, up=tuple(s_['up'] + dup), rot=tuple(s_['rot'] + drot), sq=s_['sq'], arms=s_['arms'], legs=s_['legs'], bend=bd)
def kembot(rig, f0, amp=30, beat=BEAT, twist=8, shift=0.04, env=lambda f: 1.0):
    """side-to-side hip sway, snapping to each beat"""
    def L(f):
        ph = math.pi * (f - f0) / beat; v = math.copysign(abs(math.sin(ph)) ** 0.55, math.sin(ph)) * env(f)
        return V(-shift * v * rig.SIDE, 0, -0.025 * abs(v)), V(0, -3 * v, twist * v), (0, amp * v)
    return L
def giling(rig, f0, period=2 * BEAT, amp=30, shift=0.045, env=lambda f: 1.0):
    """circular hip roll"""
    def L(f):
        a_ = 2 * math.pi * (f - f0) / period; e = env(f)
        bx, by = amp * math.sin(a_) * e, amp * math.cos(a_) * e
        return V(-shift * math.cos(a_) * e * rig.SIDE, shift * math.sin(a_) * e * rig.FWD, -0.02 * e), V(5 * math.sin(a_) * e, -5 * math.cos(a_) * e, 6 * math.sin(a_) * e), (bx, by)
    return L
def thrust(rig, f0, amp=26, beat=BEAT):
    """hip pump forward on every beat"""
    def L(f):
        v = max(0.0, math.cos(2 * math.pi * (f - f0) / beat)) ** 3
        return V(0, -0.03 * v, -0.03 * v), V(-4 * v, 0, 0), (rig.FWD * amp * v, 0)
    return L

hp2 = arms(N='hp', P='hp')
# ---- S1 (1-70): sassy groove-walk toward camera, hips swinging with every step
doug_r.walk(1, 70, (DX, 5.0), (DX, DY), 0, steps=70 / BEAT, arms=hp2, lean=6, bob=0.045, sway=4,
            bendfun=lambda ph: (0, 26 * math.sin(ph) * doug_r.SIDE))
for b in range(5):
    mouth_open(doug, bf(b + 1), 0.35 if b % 2 else 0.0); mouth_open(doug, bf(b + 1) + 7, 0.0)
# ---- Ricky sprints in crouched (40-68) and grabs (70)
ricky_r.place(1, (-6, 6), 65)
pump = lambda f, ph: {'N': ((-0.3, -0.25 * math.sin(ph), 0.25), ('auto', (-1, 0.2, 0))), 'P': ((0.3, 0.25 * math.sin(ph), 0.25), ('auto', (1, 0.2, 0)))}
ricky_r.walk(40, 66, (-2.9, 4.7), (-0.82, DY + 0.05), 65, steps=7, arms=pump, crouch=0.1, lean=24, bob=0.03, lift=0.09, sway=3)
ricky_r.place(39, (-6, 6), 65)
GRAB = 70
ricky_r.place(GRAB, (-0.78, DY), 90)
grab_arms = {'N': ((-0.08, -0.58, 0.42), ('auto', (-1, 0, -0.3))), 'P': ((0.08, -0.58, 0.42), ('auto', (1, 0, -0.3)))}
ricky_r.pose(GRAB, up=(0, 0, -0.06), rot=(12, 0, 0), arms=grab_arms, legs=LEGS['brace']())
brows(ricky, GRAB, -0.02, 18, RBZ)
# ---- S3 (71-102): arm fling on the beat with a hip pop, then turns and grabs the strap
F = 76
doug_r.place(71, (DX, DY), 0); doug_r.place(F + 8, (DX, DY), 0); doug_r.place(F + 20, TD, -90)
reachN = ((-0.75, -0.2, 0.45), ('auto', (-1, 0, -0.3)))
S3s = [ST(doug_r, 71, (0, 0, -0.03), (5, 0, 0), 1.0, hp2, 'stand'),
       ST(doug_r, F, (0, 0, 0.04), (-4, 8, 4), 1.05, arms(N='hp', P='up'), 'wide'),
       ST(doug_r, F + 10, (0, 0, -0.06), (4, -14, 0), 1.0, arms(N=reachN, P='up'), 'wide'),
       ST(doug_r, F + 22, (0, 0, -0.1), (-12, 0, 0), 1.0, arms(N='pull', P='pull'), 'brace')]
run(doug_r, 71, 102, S3s, kembot(doug_r, 71, amp=32, env=lambda f: 1.0 if f < F + 14 else max(0, 1 - (f - F - 14) / 8)))
mouth_open(doug, F - 2, 0.0); mouth_open(doug, F, 1.0); mouth_open(doug, F + 10, 0.6); mouth_open(doug, F + 18, 0.0)
lids(doug, F - 2, 40); lids(doug, F, 8); lids(doug, F + 14, 40)
ricky_r.place(F + 6, (-0.78, DY), 90); ricky_r.place(F + 12, (-1.0, DY), 90)
ricky_r.pose(F + 12, up=(0, 0, -0.08), rot=(-22, 0, 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace']())
ricky_r.place(F + 22, TR, 90)
ricky_r.pose(F + 22, up=(0, 0, -0.08), rot=(-18, 0, 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace']())
# ---- S4 SLOW-MO (103-189): leans back, hand behind head, BIG slow giling, arm whip, both hands
S4 = 103
whip1 = ((0.5, -0.05, D_EZ + 0.55), ('auto', (1, 0, 0))); whip2 = ((0.2, -0.2, D_EZ + 0.78), ('auto', (1, 0, 0)))
S4s = [ST(doug_r, S4, (0, 0, -0.1), (-18, 0, 0), 1.0, arms(N='pull', P='behind'), 'brace_w'),
       ST(doug_r, S4 + 46, (0, 0, -0.12), (-20, 0, 0), 1.0, arms(N='pull', P='behind'), 'brace_w'),
       ST(doug_r, S4 + 56, (0, 0, -0.09), (-16, 0, 0), 1.0, arms(N='pull', P=whip1), 'brace_w'),
       ST(doug_r, S4 + 66, (0, 0, -0.07), (-14, 4, 0), 1.0, arms(N='pull', P=whip2), 'brace_w'),
       ST(doug_r, S4 + 78, (0, 0, -0.13), (-26, 0, 0), 1.0, arms(N='pull_hi', P='pull_hi'), 'brace_w'),
       ST(doug_r, S4 + 86, (0, 0, -0.14), (-28, 0, 0), 1.0, arms(N='pull_hi', P='pull_hi'), 'brace_w')]
run(doug_r, S4, 189, S4s, giling(doug_r, S4, period=40, amp=36, shift=0.06, env=lambda f: 1.0 if f < S4 + 74 else max(0.35, 1 - (f - S4 - 74) / 12)))
mouth_open(doug, S4 + 50, 0.0); mouth_open(doug, S4 + 60, 0.8); mouth_open(doug, S4 + 72, 0.0)
lids(doug, S4, 40); lids(doug, S4 + 4, 55)
for k, f in enumerate(range(S4, S4 + 87, 12)):
    ricky_r.pose(f, up=(0, 0, -0.1 - 0.02 * (k % 2)), rot=(-20 - 4 * (k % 2), 3 * (1 if k % 2 else -1), 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace']())
brows(ricky, S4, -0.025, 22, RBZ)
# ---- S5 (190-273): Ricky clutches the bag; Doug: vogue hands + KEMBOT, then fist pumps + GILING
S5 = 190
hold_bag = {'N': ((-0.11, -0.36, 0.42), ('auto', (-1, 0, -0.5))), 'P': ((0.11, -0.36, 0.42), ('auto', (1, 0, -0.5)))}
ricky_r.place(S5, (TR[0] + 0.15, DY), 90)
for k, f in enumerate(range(S5, 274, 15)):
    ricky_r.pose(f, up=(0, 0, -0.03), rot=(-8, 2 * (1 if k % 2 else -1), 0), arms=hold_bag, legs=LEGS['stand']())
    for e in ricky['eyes']: key(e, 'rotation_euler', f, Euler((0, 0, D(10 if k % 2 else -10))))
brows(ricky, S5, 0.0, 0, RBZ)
for i, bp in enumerate(ricky['brows']):
    key(bp, 'location', S5 + 1, V(bp.location.x, bp.location.y, RBZ[i] + (0.04 if i == 1 else -0.01)))
doug_r.place(S5, (TD[0] - 0.2, DY), -90)
V1 = {'P': ((-0.04, -0.5, D_EZ + 0.18), (0.42, -0.25, D_EZ - 0.1)), 'N': ((0.06, -0.45, D_EZ - 0.15), (-0.45, -0.2, 0.55))}
V2 = {'N': ((0.04, -0.5, D_EZ + 0.18), (-0.42, -0.25, D_EZ - 0.1)), 'P': ((-0.06, -0.45, D_EZ - 0.15), (0.45, -0.2, 0.55))}
V3 = {'P': ((0.3, -0.42, D_EZ + 0.35), (0.5, -0.15, D_EZ)), 'N': ((-0.3, -0.42, D_EZ + 0.35), (-0.5, -0.15, D_EZ))}
FP1 = {'P': ((0.1, -0.9, 0.72), ('auto', (1, 0, -0.3))), 'N': ((-0.28, -0.12, 0.72), (-0.5, 0.15, 0.55))}
FP2 = {'N': ((-0.1, -0.9, 0.72), ('auto', (-1, 0, -0.3))), 'P': ((0.28, -0.12, 0.72), (0.5, 0.15, 0.55))}
S5s = [ST(doug_r, f, (0, 0, -0.02), (3, 0, 0), 1.0, (V1, V3, V2, V3)[k % 4], 'wide') for k, f in enumerate(range(S5, 232, 7))]
run(doug_r, S5, 231, S5s, kembot(doug_r, S5, amp=34, twist=10, shift=0.05))
S5bs = [ST(doug_r, f, (0, 0, -0.03), (9, 0, 9 * (1 if k % 2 == 0 else -1)), 1.0, FP1 if k % 2 == 0 else FP2, 'wide') for k, f in enumerate(range(232, 274, 7))]
run(doug_r, 232, 273, S5bs, giling(doug_r, 232, period=30, amp=30, shift=0.05))
for k, f in enumerate(range(232, 274, 7)): mouth_open(doug, f, 0.6 if k % 2 else 0.1)
# ---- S6 (274-339): synchronized tug with hip THRUSTS on every beat
S6 = 274
doug_r.place(S6, TD, -90); ricky_r.place(S6, TR, 90)
dS6, rS6 = [], []
for k, f in enumerate(range(S6, 340, 15)):
    m = f + 7
    dS6 += [ST(doug_r, f, (0, 0, -0.16), (-34, 0, 0), 0.96, arms(N='pull_hi', P='pull_hi'), 'brace_w'),
            ST(doug_r, m, (0, 0, -0.1), (-26, 0, 4 * (1 if k % 2 else -1)), 1.03, arms(N='pull', P='pull'), 'brace_w')]
    rS6 += [ST(ricky_r, f, (0, 0, -0.14), (-26, 0, 0), 0.96, arms(N='pull_hi', P='pull_hi'), 'brace'),
            ST(ricky_r, m, (0, 0, -0.08), (-18, 0, 0), 1.03, arms(N='pull', P='pull'), 'brace')]
    doug_r.place(f, (TD[0] + 0.04, DY), -90); doug_r.place(m, (TD[0] - 0.02, DY), -90)
    ricky_r.place(f, (TR[0] - 0.04, DY), 90); ricky_r.place(m, (TR[0] + 0.02, DY), 90)
run(doug_r, S6, 339, dS6, thrust(doug_r, S6, amp=30))
run(ricky_r, S6, 339, rS6, thrust(ricky_r, S6, amp=16))
# ---- S7 (340-363): one huge lean-back pull; Ricky yanked off balance
S7 = 340
doug_r.pose(S7, up=(0, 0, -0.12), rot=(-28, 0, 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace_w']())
doug_r.pose(S7 + 9, up=(0, 0, -0.24), rot=(-50, 0, 0), sq=0.94, arms=arms(N='pull_hi', P='pull_hi'), legs=LEGS['brace_w'](), bend=(-doug_r.FWD * 25, 0))
doug_r.pose(S7 + 22, up=(0, 0, -0.2), rot=(-42, 0, 0), arms=arms(N='pull_hi', P='pull_hi'), legs=LEGS['brace_w']())
doug_r.place(S7 + 9, (TD[0] + 0.12, DY), -90)
ricky_r.pose(S7 + 4, up=(0, 0, -0.08), rot=(-20, 0, 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace']())
ricky_r.pose(S7 + 12, up=(0, 0, 0.02), rot=(30, 0, 0), arms=arms(N='pull_hi', P='pull_hi'), legs={'N': ((-0.15, -0.45, 0.08), (0, -1, 0.4)), 'P': ((0.15, 0.4, 0), (0, -1, 0.2))})
ricky_r.place(S7 + 4, TR, 90); ricky_r.place(S7 + 14, (TR[0] + 0.35, DY), 90)
FALL = S7 + 20
SITX = TR[0] + 0.45
ricky_r.place(FALL, (SITX, DY), 90)
ricky_r.pose(FALL, up=(0, 0, -0.4), rot=(-10, 0, 0), sq=0.9, arms=hold_bag, legs=LEGS['sit']())
ricky_r.pose(FALL + 4, up=(0, 0, -0.33), rot=(-14, 0, 0), sq=1.04, arms=hold_bag, legs=LEGS['sit']())
ricky_r.pose(FALL + 8, up=(0, 0, -0.38), rot=(-10, 0, 0), sq=1.0, arms=hold_bag, legs=LEGS['sit']())
lids(ricky, FALL, 26); lids(ricky, FALL + 2, 60)
# ---- S8 (364-405): Doug lunges, grabs the bag, yanks it free (with a little hip pop)
S8 = 364
doug_r.place(S8, (TD[0] + 0.1, DY), -90)
doug_r.pose(S8, up=(0, 0, -0.18), rot=(-30, 0, 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace_w']())
doug_r.place(S8 + 12, (SITX + 1.12, DY), -90)
doug_r.pose(S8 + 12, up=(0, 0, -0.2), rot=(28, 0, 0), arms={'N': ((-0.07, -0.7, 0.1), ('auto', (-1, 0, 0.3))), 'P': ((0.07, -0.7, 0.1), ('auto', (1, 0, 0.3)))}, legs=LEGS['brace_w']())
YANK = S8 + 24
doug_r.pose(YANK, up=(0, 0, -0.08), rot=(-22, 0, 0), arms=arms(N=((-0.1, -0.45, 0.62), ('auto', (-1, 0, -0.4))), P=((0.1, -0.45, 0.62), ('auto', (1, 0, -0.4)))), legs=LEGS['brace']())
doug_r.place(YANK, (SITX + 1.3, DY), -90)
doug_r.pose(YANK + 8, up=(0, 0, 0.0), rot=(0, 6, 8), arms=arms(N=((-0.37, -0.05, 0.1), ('auto', (-1, 0.3, 0))), P='hp'), legs=LEGS['stand'](), bend=(0, 30 * doug_r.SIDE))
doug_r.pose(YANK + 14, up=(0, 0, 0.0), rot=(0, -4, -8), arms=arms(N=((-0.37, -0.05, 0.1), ('auto', (-1, 0.3, 0))), P='hp'), legs=LEGS['stand'](), bend=(0, -30 * doug_r.SIDE))
ricky_r.pose(YANK - 2, up=(0, 0, -0.38), rot=(-10, 0, 0), arms=hold_bag, legs=LEGS['sit']())
ricky_r.pose(YANK + 2, up=(0, 0, -0.36), rot=(18, 0, 0), arms={'N': ((-0.1, -0.62, 0.42), ('auto', (-1, 0, -0.3))), 'P': ((0.1, -0.62, 0.42), ('auto', (1, 0, -0.3)))}, legs=LEGS['sit']())
lids(ricky, YANK, 60); lids(ricky, YANK + 2, 0)
# ---- S9 (406-450): Ricky cringes, hands up shielding his face
S9 = 406
shield = {'N': ((-0.07, -0.42, R_EZ + 0.02), ('auto', (-1, -0.2, -0.6))), 'P': ((0.09, -0.4, R_EZ - 0.04), ('auto', (1, -0.2, -0.6)))}
ricky_r.pose(S9, up=(0, 0, -0.37), rot=(-6, 0, 0), arms=shield, legs=LEGS['sit']())
for k, f in enumerate(range(S9 + 8, 451, 8)):
    ricky_r.pose(f, up=(0, 0, -0.38 - 0.015 * (k % 2)), rot=(-10 - 4 * (k % 2), 0, -18 + 6 * (k % 2)), arms=shield, legs=LEGS['sit']())
lids(ricky, S9, 95); brows(ricky, S9, -0.03, -20, RBZ)
mouth_open(ricky, S9, 0.0); mouth_open(ricky, S9 + 3, 0.9)
# ---- S10 (451-480): grooves toward camera again, hips swinging (loops into S1)
ricky_r.place(450, (SITX, DY), 90); ricky_r.place(451, (-6, 6), 65)
doug_r.walk(451, 480, (DX, 5.8), (DX, 5.0), 0, steps=2.0, arms=hp2, lean=6, bob=0.045, sway=4,
            bendfun=lambda ph: (0, 26 * math.sin(ph) * doug_r.SIDE))
lids(doug, 451, 40)

