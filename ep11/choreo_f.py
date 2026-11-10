# ============================================================ CHOREOGRAPHY v6 (body only; the face is animated per-frame in face_f.py)
DX, DY = 0.3, 3.4
RX0 = -0.95
exec(open(os.path.join(HERE, 'helpers_e.py')).read())
hp2 = arms(N='hp', P='hp')
VO = os.path.join(HERE, 'vo6')
# dialogue placement (global frame where each wav starts)
LINES = {'g1': 64, 'g2': 258, 'g3': 288, 'g4': 357, 'd1': 438}
GRAB, SLOW0, SLOW1, SPIN, RELEASE = 151, 181, 255, 331, 340
REACT0, REACT1 = 428, 465

# ---------------------------------------------------------------- DOUG: carefree the whole time
doug_r.walk(1, 60, (DX, 4.8), (DX, DY), 0, steps=4, arms=hp2, lean=6, bob=0.045, sway=4,
            bendfun=lambda ph: (0, 34 * math.sin(ph) * doug_r.SIDE))
doug_r.place(61, (DX, DY), 0)
K1 = kembot(doug_r, 61, amp=34, twist=10, shift=0.05)
run(doug_r, 61, SLOW0 - 1, [ST(doug_r, 61, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide'), ST(doug_r, SLOW0 - 1, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide')], K1)
whip1 = ((0.5, -0.05, D_EZ + 0.55), ('auto', (1, 0, 0))); whip2 = ((0.25, -0.15, D_EZ + 0.78), ('auto', (1, 0, 0)))
G1 = giling(doug_r, SLOW0, period=60, amp=38, shift=0.06)
run(doug_r, SLOW0, SLOW1, [ST(doug_r, SLOW0, (0, 0, -0.06), (-6, 0, 0), 1.0, arms(N='hp', P='behind'), 'wide'),
                           ST(doug_r, SLOW0 + 48, (0, 0, -0.08), (-8, 0, 0), 1.0, arms(N='hp', P='behind'), 'wide'),
                           ST(doug_r, SLOW0 + 58, (0, 0, -0.04), (-4, 0, 0), 1.0, arms(N='hp', P=whip1), 'wide'),
                           ST(doug_r, SLOW0 + 68, (0, 0, 0.0), (-2, 4, 0), 1.03, arms(N='hp', P=whip2), 'wide'),
                           ST(doug_r, SLOW1, (0, 0, -0.02), (2, 0, 0), 1.0, arms(N='hp', P=whip2), 'wide')], G1)
V1 = {'P': ((-0.04, -0.5, D_EZ + 0.18), (0.42, -0.25, D_EZ - 0.1)), 'N': ((0.06, -0.45, D_EZ - 0.15), (-0.45, -0.2, 0.55))}
V2 = {'N': ((0.04, -0.5, D_EZ + 0.18), (-0.42, -0.25, D_EZ - 0.1)), 'P': ((-0.06, -0.45, D_EZ - 0.15), (0.45, -0.2, 0.55))}
V3 = {'P': ((0.3, -0.42, D_EZ + 0.35), (0.5, -0.15, D_EZ)), 'N': ((-0.3, -0.42, D_EZ + 0.35), (-0.5, -0.15, D_EZ))}
FP1 = {'P': ((0.1, -0.9, 0.72), ('auto', (1, 0, -0.3))), 'N': ((-0.28, -0.12, 0.72), (-0.5, 0.15, 0.55))}
FP2 = {'N': ((-0.1, -0.9, 0.72), ('auto', (-1, 0, -0.3))), 'P': ((0.28, -0.12, 0.72), (0.5, 0.15, 0.55))}
K2 = kembot(doug_r, SLOW1 + 1, amp=36, twist=10, shift=0.05)
run(doug_r, SLOW1 + 1, 293, [ST(doug_r, f, (0, 0, -0.02), (3, 0, 0), 1.0, (V1, V3, V2, V3)[k % 4], 'wide') for k, f in enumerate(range(SLOW1 + 1, 294, 7))], K2)
G3 = giling(doug_r, 294, period=30, amp=32, shift=0.05)
run(doug_r, 294, SPIN - 1, [ST(doug_r, f, (0, 0, -0.03), (8, 0, 8 * (1 if k % 2 == 0 else -1)), 1.0, FP1 if k % 2 == 0 else FP2, 'wide') for k, f in enumerate(range(294, SPIN, 7))], G3)
T_ARMS = {'N': ((-0.85, -0.05, 0.62), ('auto', (-1, 0, 0.3))), 'P': ((0.85, -0.05, 0.62), ('auto', (1, 0, 0.3)))}
run(doug_r, SPIN, 345, [ST(doug_r, SPIN, (0, 0, 0.03), (0, 0, 0), 1.0, T_ARMS, 'stand'), ST(doug_r, 345, (0, 0, 0.0), (0, 0, 0), 1.0, T_ARMS, 'stand')])
doug_r.place(SPIN, (DX, DY), 0); doug_r.place(345, (DX, DY), 360)
K3 = kembot(doug_r, 346, amp=34, twist=10, shift=0.05)
run(doug_r, 346, REACT0 - 1, [ST(doug_r, 346, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide'), ST(doug_r, REACT0 - 1, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide')], K3)
# the deadpan reaction: stops, lifts one headphone, glances over ("...You good?"), puts it back
lift_cup = ((-0.5, -0.02, D_EZ + 0.04), (-0.6, 0.05, D_EZ - 0.2))
relaxed = {'N': ((-0.15, -0.0, 0), (0, -1, 0.2)), 'P': ((0.2, 0.04, 0), (0.3, -1, 0.5))}   # weight on one leg
REACT = [ST(doug_r, REACT0, (0, 0, -0.02), (2, 0, 0), 1.0, hp2, 'wide'),
         ST(doug_r, REACT0 + 6, (0.02, 0, -0.03), (0, 3, -10), 1.0, arms(N=lift_cup, P='hp'), relaxed),
         ST(doug_r, REACT1 - 6, (0.02, 0, -0.03), (0, 3, -12), 1.0, arms(N=lift_cup, P='hp'), relaxed),
         ST(doug_r, REACT1, (0, 0, -0.02), (3, 0, 0), 1.0, hp2, 'wide')]
run(doug_r, REACT0, REACT1, REACT)
K4 = kembot(doug_r, REACT1 + 1, amp=34, twist=10, shift=0.05, env=lambda f: min(1.0, (f - REACT1) / 6))
run(doug_r, REACT1 + 1, 480, [ST(doug_r, REACT1 + 1, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide'), ST(doug_r, 480, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'wide')], K4)
CUP_N = [o for o in bpy.data.objects if (o.name.startswith('hp_cup') or o.name.startswith('hp_pad')) and o.location.x < 0]
for o in CUP_N:
    base = o.location.copy()
    key(o, 'location', REACT0 + 2, base); key(o, 'location', REACT0 + 7, base + V(-0.09, 0.0, 0.04))
    key(o, 'location', REACT1 - 6, base + V(-0.09, 0.0, 0.04)); key(o, 'location', REACT1 - 1, base)

def hip_side(f):
    L = K1 if f < SLOW0 else G1 if f <= SLOW1 else K2 if f <= 293 else G3
    return L(f)[2][1] / 36.0 * doug_r.SIDE

# ---------------------------------------------------------------- RICKY (Green): confident -> confused -> straining -> annoyed -> defeated
ricky_r.place(1, (-6, 6), 90); ricky_r.place(35, (-6, 6), 90)
swing = lambda f, ph: {'N': ((-0.33, 0.14 * math.sin(ph), 0.08), ('auto', (-1, 0.3, 0))), 'P': ((0.33, -0.14 * math.sin(ph), 0.08), ('auto', (1, 0.3, 0)))}
ricky_r.walk(36, 60, (-2.55, 3.22), (-0.82, DY - 0.02), 90, steps=3.5, arms=swing, lean=3, bob=0.04, sway=7)
casual = {'N': ((-0.33, 0.04, 0.22), (-0.42, 0.06, 0.42)), 'P': ((0.36, -0.02, 0.08), ('auto', (1, 0.3, 0)))}   # hand on hip
hey_wave = {'P': ((0.2, -0.4, R_EZ + 0.35), ('auto', (1, 0, -0.2))), 'N': casual['N']}
point_bag = {'N': ((-0.05, -0.62, 0.3), ('auto', (-1, 0, 0.2))), 'P': ((0.36, -0.02, 0.08), ('auto', (1, 0.3, 0)))}
palm_out = {'P': ((0.1, -0.66, 0.72), ('auto', (1, 0, -0.4))), 'N': casual['N']}
wave_face = lambda dx: {'P': ((-0.5, -0.66 - dx, 1.0), ('auto', (1, 0, -0.2))), 'N': casual['N']}
g = LINES['g1']
ricky_r.place(61, (-0.82, DY - 0.02), 90)
ricky_r.pose(61, up=(0, 0, 0.0), rot=(-3, 0, 0), arms=casual, legs=LEGS['stand']())
ricky_r.pose(g + 6, up=(0.02, 0, 0.0), rot=(-5, 3, 0), arms=casual, legs=relaxed)              # weight shift, sizing him up
ricky_r.pose(g + 9, up=(0, 0, 0.03), rot=(-8, 0, 0), arms=hey_wave, legs=relaxed)               # "Hey."
ricky_r.pose(g + 20, up=(0, 0, 0.0), rot=(-2, 0, 4), arms=casual, legs=relaxed)
ricky_r.place(g + 26, (-0.82, DY - 0.02), 90); ricky_r.place(g + 32, (-0.45, DY - 0.08), 90)    # steps in
for k, f in enumerate(range(g + 32, g + 48, 4)):                                                # "Hey!" waving in his face
    ricky_r.pose(f, up=(0, 0, 0.04), rot=(8, 0, 0), arms=wave_face(0.14 if k % 2 else -0.1), legs=LEGS['stand']())
ricky_r.pose(g + 50, up=(0, 0, 0.0), rot=(10, 0, 0), arms=point_bag, legs=LEGS['brace']())      # "Gimme the bag." - points at it
ricky_r.pose(g + 61, up=(0, 0, 0.02), rot=(2, 0, 0), arms=palm_out, legs=LEGS['brace']())       # palm out
ricky_r.pose(g + 72, up=(0, 0, 0.0), rot=(12, 0, 12), arms=palm_out, legs=LEGS['stand']())      # leans in, peering: "...hello?"
ricky_r.pose(GRAB - 4, up=(0, 0, -0.02), rot=(14, 0, 14), arms=palm_out, legs=LEGS['stand']())
ricky_r.place(GRAB - 2, (-0.45, DY - 0.08), 90); ricky_r.place(GRAB + 4, (-0.6, DY), 90)
grab = {'N': ((-0.08, -0.6, 0.38), ('auto', (-1, 0, -0.3))), 'P': ((0.08, -0.6, 0.38), ('auto', (1, 0, -0.3)))}
ricky_r.pose(GRAB + 2, up=(0, 0, -0.08), rot=(16, 0, 0), arms=grab, legs=LEGS['brace']())
pullA = arms(N='pull', P='pull')
STOMP = LINES['g2'] + 5; YANK = LINES['g3'] + 23
for f in range(GRAB + 8, SPIN, 2):                           # yanked around by Doug's hips; effort escalates
    h = hip_side(f)
    effort = 0.6 if f < SLOW0 else 0.8 if f < SLOW1 else 1.0
    shake = 0.012 * math.sin(f * 1.7) * effort
    extra_lean = -16 * max(0, 1 - abs(f - YANK) / 6)           # the all-in "GO!" yank
    lift = 0.12 * max(0, 1 - abs(f - STOMP) / 4)               # foot stomp on "Come ON"
    ricky_r.place(f, (RX0 + 0.32 * h + shake, DY + 0.04 * math.sin(f * 0.3)), 90 - 10 * h)
    ricky_r.pose(f, up=(0, 0, -0.1 - 0.03 * effort), rot=(-24 + 18 * h + extra_lean, 4 * math.sin(f * 0.9) * effort, 8 * h), arms=pullA,
                 legs={'N': ((-0.18, -0.5 + 0.15 * h, lift), (0, -1, 0.4)), 'P': ((0.2, 0.32 + 0.1 * h, 0), (0, -1, 0.2))})
for f in range(SPIN, RELEASE + 1):                           # whipped around by the spin, flung
    th = D(360 * (f - SPIN) / (345 - SPIN))
    pos = V(DX, DY, 0) + Matrix.Rotation(th, 3, 'Z') @ V(-1.2, 0, 0)
    ricky_r.place(f, (pos.x, pos.y), 90 + math.degrees(th), z=0.05 * math.sin(math.pi * (f - SPIN) / (RELEASE - SPIN)))
    ricky_r.pose(f, up=(0, 0, -0.05), rot=(-30, 0, 0), arms=pullA, legs={'N': ((-0.15, -0.4, 0.15), (0, -1, 0.4)), 'P': ((0.15, 0.3, 0.1), (0, -1, 0.2))})
SITP = (-1.55, 3.25)
down = {'N': ((-0.38, -0.2, 0.05), ('auto', (-1, 0.3, 0))), 'P': ((0.38, -0.2, 0.05), ('auto', (1, 0.3, 0)))}
ricky_r.place(RELEASE + 5, (-1.25, 3.1), 70, z=0.35); ricky_r.place(RELEASE + 10, SITP, 80)
ricky_r.pose(RELEASE + 5, up=(0, 0, -0.1), rot=(-40, 0, 20), arms={'N': ((-0.45, 0.1, 0.9), ('auto', (-1, 0, 0))), 'P': ((0.45, 0.1, 0.9), ('auto', (1, 0, 0)))}, legs=LEGS['sit']())
ricky_r.pose(RELEASE + 10, up=(0, 0, -0.4), rot=(-12, 0, 0), sq=0.9, arms=down, legs=LEGS['sit']())
ricky_r.pose(RELEASE + 14, up=(0, 0, -0.34), rot=(-14, 0, 0), sq=1.04, arms=down, legs=LEGS['sit']())
for k, f in enumerate(range(RELEASE + 16, LINES['g4'], 3)):    # dazed head shake
    ricky_r.pose(f, up=(0, 0, -0.37), rot=(-12, 0, (8, -8)[k % 2]), arms=down, legs=LEGS['sit']())
g = LINES['g4']
facepalm = {'N': ((-0.04, -0.34, R_EZ + 0.04), ('auto', (-1, -0.2, -0.5))), 'P': down['P']}
you_know = {'P': ((0.36, -0.36, R_EZ + 0.08), ('auto', (1, 0, -0.5))), 'N': down['N']}
dismiss = {'P': ((0.5, -0.25, 0.2), ('auto', (1, 0, 0))), 'N': down['N']}
ricky_r.pose(g, up=(0, 0, -0.37), rot=(-10, 0, 0), arms=down, legs=LEGS['sit']())
ricky_r.pose(g + 6, up=(0, 0, -0.39), rot=(16, 0, 0), arms=facepalm, legs=LEGS['sit']())          # "Ugh."
ricky_r.pose(g + 18, up=(0, 0, -0.38), rot=(10, 0, 0), arms=facepalm, legs=LEGS['sit']())
ricky_r.pose(g + 26, up=(0, 0, -0.36), rot=(-6, 0, 8), arms=you_know, legs=LEGS['sit']())         # "you know what?"
ricky_r.pose(g + 40, up=(0, 0, -0.36), rot=(-8, 0, 10), arms=you_know, legs=LEGS['sit']())
ricky_r.pose(g + 56, up=(0, 0, -0.38), rot=(4, 0, 0), arms=dismiss, legs=LEGS['sit']())            # "Forget it." - waves it off
ricky_r.pose(g + 66, up=(0, 0, -0.42), rot=(16, 0, -4), sq=0.95, arms=down, legs=LEGS['sit']())    # slumps
ricky_r.pose(REACT0 + 14, up=(0, 0, -0.42), rot=(12, 0, -10), sq=0.95, arms=down, legs=LEGS['sit']())  # turns to Doug
for k, f in enumerate(range(452, 471, 5)):                                                       # slow "no" head shake
    ricky_r.pose(f, up=(0, 0, -0.42), rot=(12, 0, (-14, -4)[k % 2]), sq=0.95, arms=down, legs=LEGS['sit']())
ricky_r.pose(480, up=(0, 0, -0.43), rot=(18, 0, -6), sq=0.95, arms=down, legs=LEGS['sit']())

