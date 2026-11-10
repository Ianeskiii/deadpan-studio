"""Tube Town - When the barista still gets your name wrong.  usage: python3 build12.py SHOT OUTDIR [opts]"""
import os, sys, random, json
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
exec(open(os.path.join(HERE, 'set12.py')).read())
from mathutils import Matrix
doug['mouth'].location.y = -0.326          # mouth sits on the face surface (v6 fix)
BEAT = 15
def V(*a): return Vector(a)
exec(open(os.path.join(HERE, 'rig.py')).read())
doug_r = Rig(doug, 'doug', M['doug'], M['doug'], lift=0.17)
bari_r = Rig(bari, 'bari', C_['bari'], C_['bari'], lift=0.15)
dr, br = doug['root'], bari['root']
doug_r.setup_bend(['doug_body'], (doug['zc'] + 0.15) - 0.25)
D_EZ = doug_r.ez; B_EZ = bari_r.ez
LEGS = dict(
    stand=lambda: {'N': ((-0.15, 0.0, 0), (0, -1, 0.2)), 'P': ((0.15, 0.0, 0), (0, -1, 0.2))},
    relaxed=lambda: {'N': ((-0.15, 0.0, 0), (0, -1, 0.2)), 'P': ((0.2, 0.04, 0), (0.3, -1, 0.5))},
    relaxed2=lambda: {'N': ((-0.2, 0.04, 0), (-0.3, -1, 0.5)), 'P': ((0.15, 0.0, 0), (0, -1, 0.2))},
)
exec(open(os.path.join(HERE, '..', 'ep11', 'helpers_e.py')).read())
DDBZ = [bp.location.z for bp in doug['brows']]; BBZ = [bp.location.z for bp in bari['brows']]
T = json.load(open(os.path.join(HERE, 'vo', 'timing.json')))
VO = os.path.join(HERE, 'vo')
N = T['N']

def bump(f, c, w):                      # smooth 0..1..0 pulse centred on c, half-width w
    x = abs(f - c) / w
    return 0.0 if x >= 1 else 0.5 * (1 + math.cos(math.pi * x))
def ramp(f, a, b):
    return 0.0 if f <= a else 1.0 if f >= b else smooth((f - a) / (b - a))
def idle(rig, seed=0.0, amp=1.0):        # breathing + tiny weight drift so nobody is ever frozen
    def L(f):
        b = math.sin((f + seed) / 26 * 2 * math.pi / 3.2)
        return V(0.004 * math.sin((f + seed) / 47), 0, 0.006 * b * amp), V(0.8 * b * amp, 0.9 * math.sin((f + seed) / 53) * amp, 0), (0, 0)
    return L
def add_layers(*Ls):
    def L(f):
        u, r_, bx, by = V(0, 0, 0), V(0, 0, 0), 0.0, 0.0
        for l in Ls:
            a_, b_, (x_, y_) = l(f); u += a_; r_ += b_; bx += x_; by += y_
        return u, r_, (bx, by)
    return L
def world_to_local(rig, f, p):
    scene.frame_set(f); return tuple(rig.upper.matrix_world.inverted() @ Vector(p))

# ============================================================ BLOCKING
DPOS, DHEAD = (-0.8, 0.05), 55          # Doug at the counter, cheated toward camera
WAITP, WAITH = (-1.05, -0.55), 15        # where Doug waits
BPOS, BHEAD = (0.76, 0.05), -55          # barista behind the counter
CUP_COUNTER = V(0.02, 0.0, CT + 0.072)
# key frames from the dialogue
F_AWE = T['b1']['fs']; F_Q = 57; F_DOUG = T['d1']['fs']; F_B2 = T['b2']['fs']
LET = [187, 203, 224, 245]; F_PERF = T['b3']['fs']; F_B3E = T['b3']['fe']
F_CALL = T['b4']['fs']; F_DOG = 363; F_B4E = T['b4']['fe']
F_SIGH = T['d3']['f']; F_D3 = T['d3']['fs']; F_D3E = T['d3']['fe']
F_YEAH = T['b5']['fs']; F_B5E = T['b5']['fe']; F_BYE = T['b6']['fs']; F_BYEDOG = 553; F_B6E = T['b6']['fe']
F_ASIDE0, F_ASIDE1 = F_B3E + 6, F_B3E + 28
F_TURN0, F_TURN1 = F_B4E + 4, F_B4E + 24
F_BACK0, F_BACK1 = F_TURN1 + 3, F_SIGH
F_TAKE = F_B5E + 16
F_GO0 = F_TAKE + 10; F_STOP = F_BYEDOG + 9; F_GO1 = F_STOP + 18

# ============================================================ DOUG
Ad = dict(
    down=lambda s: ((s * 0.37, -0.03, 0.06), ('auto', (s, 0.3, 0))),
    down2=lambda s: ((s * 0.36, 0.0, 0.03), ('auto', (s, 0.4, 0))),
)
def darms(**kw):
    return {side: (Ad[nm](-1 if side == 'N' else 1) if isinstance(nm, str) else nm) for side, nm in kw.items()}
dn = darms(N='down', P='down'); dn2 = darms(N='down2', P='down2')
swing_d = lambda f, ph: {'N': ((-0.37, 0.12 * math.sin(ph), 0.07), ('auto', (-1, 0.3, 0))), 'P': ((0.37, -0.12 * math.sin(ph), 0.07), ('auto', (1, 0.3, 0)))}
# walk in
doug_r.walk(1, 30, (-2.25, -0.3), DPOS, 78, steps=3.2, arms=swing_d, lean=4, bob=0.035, sway=4)
for f in range(30, 39):
    doug_r.place(f, DPOS, 78 + (DHEAD - 78) * smooth((f - 30) / 8))
nods = lambda f: sum(6 * bump(f, c + 5, 7) for c in LET) + 7 * bump(f, F_B3E + 1, 7) + 3 * bump(f, F_DOUG + 3, 6)
nod_layer = lambda f: (V(0, 0, 0), V(nods(f), 0, 0), (0, 0))
# standing at the counter until he steps aside
S1 = [ST(doug_r, 31, (0, 0, -0.01), (2, 0, 0), 1.0, dn, 'stand'),
      ST(doug_r, 40, (0, 0, 0.0), (0, 0, 0), 1.0, dn, 'relaxed'),
      ST(doug_r, F_DOUG + 14, (0.01, 0, 0.0), (0, 2, 0), 1.0, dn, 'relaxed'),
      ST(doug_r, T['b2']['fe'] + 4, (0.01, 0, 0.0), (1, 3, 0), 1.0, dn, 'relaxed'),     # holds the look for a beat
      ST(doug_r, LET[0] - 4, (0, 0, -0.01), (3, 0, 0), 1.0, dn, 'stand'),               # leans in to spell it out
      ST(doug_r, LET[3] + 12, (0, 0, -0.01), (3, 0, 0), 1.0, dn, 'stand'),
      ST(doug_r, F_ASIDE0, (0, 0, 0.0), (0, 0, 0), 1.0, dn, 'stand')]
run(doug_r, 39, F_ASIDE0, S1, add_layers(idle(doug_r, 0), nod_layer))
# steps aside to wait
doug_r.walk(F_ASIDE0, F_ASIDE1, DPOS, WAITP, DHEAD, steps=2.2, arms=swing_d, lean=3, bob=0.03, sway=3,
            hfun=lambda t: DHEAD + (WAITH - DHEAD) * smooth(min(1, t * 1.4)))
# waits; on "DOG!" freezes, then slowly turns his head toward the counter
look_rot = 40
S2 = [ST(doug_r, F_ASIDE1, (0, 0, 0), (0, 0, 0), 1.0, dn2, 'relaxed2'),
      ST(doug_r, F_DOG - 2, (0.01, 0, 0), (0, -2, -6), 1.0, dn2, 'relaxed2'),
      ST(doug_r, F_TURN0, (0.0, 0, 0.0), (0, 0, -6), 1.0, dn2, 'stand'),
      ST(doug_r, F_TURN1, (0.0, 0, 0.0), (2, 0, look_rot), 1.0, dn2, 'stand')]
run(doug_r, F_ASIDE1, F_TURN1, S2, idle(doug_r, 40, 0.8))
doug_r.place(F_ASIDE1, WAITP, WAITH); doug_r.place(F_TURN1, WAITP, WAITH)
# walks back to the counter (root takes over the head turn)
doug_r.walk(F_BACK0, F_BACK1, WAITP, DPOS, WAITH + look_rot, steps=2.2, arms=swing_d, lean=5, bob=0.03, sway=3,
            hfun=lambda t: WAITH + look_rot + (DHEAD - WAITH - look_rot) * smooth(t))
doug_r.pose(F_TURN1 + 1, rot=(2, 0, 0), arms=dn2, legs=LEGS['stand']())
# at the counter: sigh, the line, the stare, takes the cup
gest = darms(N=((-0.16, -0.42, 0.5), ('auto', (-1, 0.1, -0.2))), P='down')
F_REACH = F_TAKE - 6
S3 = [ST(doug_r, F_BACK1, (0, 0, 0), (2, 0, 0), 1.0, dn, 'stand'),
      ST(doug_r, F_BACK1 + 8, (0, 0, -0.025), (5, 0, 0), 0.97, dn, 'stand'),            # the sigh: shoulders drop
      ST(doug_r, F_D3 - 2, (0, 0, -0.015), (3, 0, 0), 0.985, dn, 'stand'),
      ST(doug_r, F_D3 + 8, (0, 0, -0.01), (2, 0, 0), 1.0, gest, 'stand'),                # small hand toward the cup
      ST(doug_r, F_D3E - 2, (0, 0, -0.01), (2, 0, 0), 1.0, gest, 'stand'),
      ST(doug_r, F_D3E + 8, (0, 0, -0.015), (2, 0, 0), 0.99, dn, 'stand'),
      ST(doug_r, F_REACH, (0, 0, -0.015), (2, 0, 0), 0.99, dn, 'stand')]
run(doug_r, F_BACK1, F_REACH, S3, idle(doug_r, 80, 0.7))
for f in range(F_BACK1, F_GO0 - 9): doug_r.place(f, DPOS, DHEAD)
reach_loc = world_to_local(doug_r, F_TAKE, CUP_COUNTER + V(0.0, -0.05, -0.02))
hold_d = ((-0.3, -0.3, 0.42), ('auto', (-1, 0.2, -0.3)))
S4 = [ST(doug_r, F_REACH, (0, 0, -0.015), (2, 0, 0), 0.99, dn, 'stand'),
      ST(doug_r, F_TAKE, (0, 0, -0.03), (8, 0, 0), 1.0, darms(N=(reach_loc, ('auto', (-1, 0.2, -0.3))), P='down'), 'stand'),
      ST(doug_r, F_TAKE + 8, (0, 0, -0.01), (2, 0, 0), 1.0, darms(N=hold_d, P='down'), 'stand')]
run(doug_r, F_REACH, F_TAKE + 8, S4)
# turns and heads for the door, cup in hand
EXITH = -45; P1 = (DPOS[0] - 0.72, DPOS[1] - 0.72); P2 = (P1[0] - 0.42, P1[1] - 0.42)
for f in range(F_GO0 - 9, F_GO0 + 1):
    t = smooth((f - (F_GO0 - 9)) / 9); doug_r.place(f, DPOS, DHEAD + (EXITH - DHEAD) * t)
    doug_r.pose(f, up=(0, 0, -0.01), rot=(2, 0, 0), arms=darms(N=hold_d, P='down'), legs=LEGS['stand']())
swing_c = lambda f, ph: {'N': hold_d, 'P': ((0.37, -0.12 * math.sin(ph), 0.07), ('auto', (1, 0.3, 0)))}
doug_r.walk(F_GO0, F_STOP, DPOS, P1, EXITH, steps=3.0, arms=swing_c, lean=4, bob=0.035, sway=3)
# "Have a nice day, Dog!" - stops, eyes shut in silent disappointment, carries on without turning around
S5 = [ST(doug_r, F_STOP, (0, 0, -0.005), (3, 0, 0), 1.0, darms(N=hold_d, P='down'), 'stand'),
      ST(doug_r, F_STOP + 6, (0, 0, -0.03), (6, 0, 0), 0.965, darms(N=hold_d, P='down'), 'stand'),
      ST(doug_r, F_GO1 - 3, (0, 0, -0.025), (5, 0, 0), 0.975, darms(N=hold_d, P='down'), 'stand'),
      ST(doug_r, F_GO1, (0, 0, -0.01), (3, 0, 0), 1.0, darms(N=hold_d, P='down'), 'stand')]
run(doug_r, F_STOP, F_GO1, S5)
for f in range(F_STOP, F_GO1 + 1): doug_r.place(f, P1, EXITH)
doug_r.walk(F_GO1, N + 2, P1, P2, EXITH, steps=2.0, arms=swing_c, lean=4, bob=0.035, sway=3)

# ============================================================ BARISTA
def barms(**kw): return kw
on_ctr = {'N': ((-0.2, -0.38, 0.5), ('auto', (-1, 0.2, -0.3))), 'P': ((0.2, -0.38, 0.5), ('auto', (1, 0.2, -0.3)))}
bari_r.place(1, BPOS, BHEAD)
reach_stack = world_to_local(bari_r, 1, (0.2, 0.6, CT + 0.06))
cup_chest = ((0.22, -0.33, 0.44), ('auto', (1, 0.2, -0.4)))
mk_ready = ((-0.06, -0.4, 0.6), ('auto', (-1, 0.1, -0.4)))
mk_write = ((0.02, -0.42, 0.56), ('auto', (-1, 0.1, -0.4)))
cup_write = ((0.08, -0.4, 0.5), ('auto', (1, 0.2, -0.4)))
bari_r.place(1, BPOS, BHEAD)
S = [ST(bari_r, 1, (0, 0, 0), (4, 0, 0), 1.0, on_ctr, 'stand'),
     ST(bari_r, F_AWE - 2, (0, 0, 0), (4, 0, 0), 1.0, on_ctr, 'stand'),
     ST(bari_r, F_AWE + 6, (0, 0, 0.0), (6, 0, 8), 1.0, {'N': on_ctr['N'], 'P': (reach_stack, ('auto', (1, 0.2, -0.2)))}, 'stand'),
     ST(bari_r, F_AWE + 14, (0, 0, 0.01), (0, 0, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'relaxed'),
     ST(bari_r, F_Q + 10, (0, 0, 0.0), (5, 7, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'relaxed'),       # head tilt on the question
     ST(bari_r, F_DOUG + 14, (0, 0, 0.0), (2, 2, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'relaxed'),
     ST(bari_r, F_B2 - 4, (0, 0, -0.005), (-2, -8, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'relaxed'),  # pause... confused tilt
     ST(bari_r, F_B2 + 12, (0, 0, -0.01), (7, -4, 0), 1.0, {'N': mk_write, 'P': cup_write}, 'stand'),     # leans in, marker ready
     ST(bari_r, LET[0], (0, 0, -0.02), (12, 0, 0), 1.0, {'N': mk_write, 'P': cup_write}, 'stand'),
     ST(bari_r, LET[3] + 14, (0, 0, -0.02), (12, 0, 0), 1.0, {'N': mk_write, 'P': cup_write}, 'stand'),
     ST(bari_r, F_PERF + 6, (0, 0, 0.015), (-4, 3, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'relaxed'),   # "Perfect. Got it!"
     ST(bari_r, F_B3E, (0, 0, 0.01), (-2, 0, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'relaxed')]
def write_layer(f):
    # little marker strokes while each letter is written
    v = sum(bump(f, c + 12, 10) for c in LET)
    return V(0, 0, 0), V(1.5 * v * math.sin(f * 1.3), 0, 2 * v * math.sin(f * 0.9)), (0, 0)
run(bari_r, 1, F_B3E, S, add_layers(idle(bari_r, 13, 1.1), write_layer, lambda f: (V(0, 0, 0), V(-5 * bump(f, F_PERF + 20, 6), 0, 0), (0, 0))))
for f in range(1, F_B3E + 1): bari_r.place(f, BPOS, BHEAD)
# hand strokes (marker) layered directly onto the N hand
for f in range(LET[0], LET[3] + 26):
    v = sum(bump(f, c + 12, 10) for c in LET)
    if v <= 0: continue
    h = Vector(mk_write[0]) + V(0.012 * math.sin(f * 2.1) * v, 0, 0.014 * math.sin(f * 2.9 + 1) * v)
    bari_r.pose(f, up=tuple(interp(S, f)['up']), rot=tuple(interp(S, f)['rot']), arms={'N': (h, ('auto', (-1, 0.1, -0.4)))})
# makes the drink: turns to the machine and back
MACH = (1.18, 0.33); F_M0, F_M1, F_M2, F_M3 = F_B3E + 2, F_B3E + 12, F_B3E + 22, F_CALL - 2
CALLP, CALLH = (0.74, 0.0), -32
for f in range(F_M0, F_M3 + 1):
    if f <= F_M1:
        t = smooth((f - F_M0) / (F_M1 - F_M0)); p = Vector(BPOS).lerp(Vector(MACH), t); h = BHEAD + (90 - BHEAD) * t
    elif f <= F_M2:
        p, h = Vector(MACH), 90
    else:
        t = smooth((f - F_M2) / (F_M3 - F_M2)); p = Vector(MACH).lerp(Vector(CALLP), t); h = 90 + (CALLH - 90) * t
    bari_r.place(f, tuple(p), h)
    walking = f < F_M1 or f > F_M2
    ph = (f - F_M0) * 0.55
    legs = LEGS['stand']() if not walking else {'N': ((-0.15, 0.08 * math.sin(ph), 0.05 * max(0, math.sin(ph))), (0, -1, 0.3)), 'P': ((0.15, -0.08 * math.sin(ph), 0.05 * max(0, -math.sin(ph))), (0, -1, 0.3))}
    arm_ = {'N': ((-0.18, -0.42, 0.62), ('auto', (-1, 0.1, -0.3))), 'P': ((0.1, -0.45, 0.45), ('auto', (1, 0.2, -0.3)))} if F_M1 - 2 <= f <= F_M2 + 2 else \
           {'N': ((-0.33, -0.05, 0.12), ('auto', (-1, 0.3, 0))), 'P': cup_chest}
    bari_r.pose(f, up=(0, 0, -0.01 if walking else 0), rot=(5 if not walking else 2, 0, 0), arms=arm_, legs=legs)
# "Coffee for..." (hand by her mouth, calling out)  "...DOG!" (cup raised up high, proud)
call_hand = ((-0.12, -0.3, B_EZ - 0.08), ('auto', (-1, 0, -0.3)))
cup_up = ((0.27, -0.3, B_EZ + 0.12), ('auto', (1, 0.2, -0.2)))
cup_show = ((0.34, -0.3, B_EZ - 0.02), ('auto', (1, 0.2, -0.3)))
cup_offer = ((0.16, -0.42, 0.47), ('auto', (1, 0.2, -0.4)))
S6 = [ST(bari_r, F_M3, (0, 0, 0), (2, 0, 0), 1.0, {'N': ((-0.33, -0.05, 0.12), ('auto', (-1, 0.3, 0))), 'P': cup_chest}, 'stand'),
      ST(bari_r, F_CALL + 6, (0, 0, 0.01), (-5, 0, 0), 1.0, {'N': call_hand, 'P': cup_chest}, 'stand'),
      ST(bari_r, F_DOG - 4, (0, 0, 0.0), (-4, 0, 0), 1.0, {'N': call_hand, 'P': cup_chest}, 'stand'),
      ST(bari_r, F_DOG + 4, (0, 0, 0.03), (-8, 3, 0), 1.0, {'N': on_ctr['N'], 'P': cup_up}, 'relaxed'),
      ST(bari_r, F_TURN1 + 6, (0, 0, 0.02), (-5, 4, 0), 1.0, {'N': on_ctr['N'], 'P': cup_up}, 'relaxed'),
      ST(bari_r, F_BACK1 - 6, (0, 0, 0.0), (0, 2, 0), 1.0, {'N': on_ctr['N'], 'P': cup_show}, 'relaxed'),
      ST(bari_r, F_D3, (0, 0, 0.0), (2, 0, 0), 1.0, {'N': on_ctr['N'], 'P': cup_offer}, 'relaxed'),
      ST(bari_r, F_YEAH - 4, (0, 0, 0.0), (6, -3, 0), 1.0, {'N': on_ctr['N'], 'P': cup_offer}, 'relaxed'),   # glances down at the cup
      ST(bari_r, F_YEAH + 10, (0, 0, 0.01), (0, 5, 0), 1.0, {'N': on_ctr['N'], 'P': cup_offer}, 'relaxed')]  # "Yeah?" - looks up, beaming
run(bari_r, F_M3, F_YEAH + 10, S6, idle(bari_r, 29, 1.0))
for f in range(F_M3, F_YEAH + 30): bari_r.place(f, CALLP, CALLH + (BHEAD + 5 - CALLH) * ramp(f, F_TURN1, F_BACK1))
# sets the cup down on the counter, Doug takes it, she waves him off
F_SET = F_TAKE - 4
set_loc = world_to_local(bari_r, F_SET, CUP_COUNTER + V(0.03, 0.02, -0.02))
wave = lambda k: {'N': on_ctr['N'], 'P': ((0.3 + 0.06 * k, -0.32, B_EZ + 0.14), ('auto', (1, 0, -0.2)))}
S7 = [ST(bari_r, F_YEAH + 10, (0, 0, 0.01), (0, 5, 0), 1.0, {'N': on_ctr['N'], 'P': cup_offer}, 'relaxed'),
      ST(bari_r, F_SET, (0, 0, -0.01), (10, 0, 6), 1.0, {'N': on_ctr['N'], 'P': (set_loc, ('auto', (1, 0.2, -0.3)))}, 'relaxed'),
      ST(bari_r, F_SET + 10, (0, 0, 0.0), (3, 0, 0), 1.0, on_ctr, 'relaxed'),
      ST(bari_r, F_BYE - 4, (0, 0, 0.0), (2, 0, 0), 1.0, on_ctr, 'relaxed')]
for k, f in enumerate(range(F_BYE + 2, F_B6E + 8, 5)):
    S7.append(ST(bari_r, f, (0, 0, 0.02), (-4, 4, 0), 1.0, wave(1 if k % 2 else -1), 'relaxed'))
S7.append(ST(bari_r, F_B6E + 16, (0, 0, 0.0), (2, 2, 0), 1.0, on_ctr, 'relaxed'))
S7.append(ST(bari_r, N, (0, 0, 0.0), (2, 2, 0), 1.0, on_ctr, 'relaxed'))
run(bari_r, F_YEAH + 10, N, S7, idle(bari_r, 61, 1.0))
for f in range(F_YEAH + 30, N + 1): bari_r.place(f, CALLP, BHEAD + 5 + (-25 - BHEAD - 5) * ramp(f, F_GO0, F_STOP))

# ============================================================ PROPS + FACES + HAT (baked per frame)
def wp(o): return o.matrix_world.translation.copy()
exec(open(os.path.join(HERE, 'face12.py')).read())
exec(open(os.path.join(HERE, 'cams12.py')).read())
hat_objs = [o for o in bpy.data.objects if o.name.startswith('hat_')]
hat_rest = {o: o.rotation_euler.copy() for o in hat_objs}
MARKER_REST = V(0.12, -0.32, CT + 0.012)
def cup_owner(f):
    if f < F_AWE + 6: return 'stack'
    if f < F_SET + 1: return 'bari'
    if f < F_TAKE + 1: return 'counter'
    return 'doug'
def cup_pos(owner):
    if owner == 'stack': return V(0.18, 0.62, CT + 0.07 + 6 * 0.028 + 0.02)
    if owner == 'counter': return CUP_COUNTER.copy()
    rig = bari_r if owner == 'bari' else doug_r
    h = wp(rig.hand['P' if owner == 'bari' else 'N']); R = rig.root.matrix_world.to_3x3().normalized()
    return h + R @ V(0.0, -0.055, 0.0) + V(0, 0, 0.01)
prev_owner, blend_from, blend_f = None, None, -99
up_hist = []
TEXT_ON = F_PERF - 2
for f in range(1, N + 1):
    scene.frame_set(f)
    ow = cup_owner(f)
    p = cup_pos(ow)
    if ow != prev_owner:
        if prev_owner is not None: blend_from, blend_f = cup.location.copy(), f
        prev_owner = ow
    if f - blend_f < 5: p = blend_from.lerp(p, smooth((f - blend_f) / 5))
    cup.location = p
    cp = cam_pos(f); d = cp - p
    cup.rotation_euler = (0, 0, math.atan2(d.x, -d.y) + (D(8) if ow == 'bari' else 0))
    cup.keyframe_insert('location', frame=f); cup.keyframe_insert('rotation_euler', frame=f)
    dog_txt.hide_render = f < TEXT_ON; dog_txt.keyframe_insert('hide_render', frame=f)
    if F_AWE + 12 <= f < F_M0:
        h = wp(bari_r.hand['N']); marker.location = h + V(0.0, 0.0, 0.03)
        marker.rotation_euler = (D(25), D(-30), bari_r.root.rotation_euler.z)
    else:
        marker.location = MARKER_REST; marker.rotation_euler = (0, D(90), D(20))
    marker.keyframe_insert('location', frame=f); marker.keyframe_insert('rotation_euler', frame=f)
    face_pass(f)
    up_hist.append(doug_r.upper.rotation_euler.copy())
for f in range(1, N + 1):
    cur = up_hist[f - 1]; old = up_hist[max(0, f - 4)]
    for o in hat_objs:
        r0 = hat_rest[o]; o.rotation_euler = (r0.x + 0.6 * (old.x - cur.x), r0.y + 0.6 * (old.y - cur.y), r0.z)
        o.keyframe_insert('rotation_euler', frame=f)
scene.frame_set(1)

if SHOT == 'QA':
    for nm in SHOTS: cam_setup(nm)
    f0, f1 = 1, N
    exec(open(os.path.join(HERE, 'qa12.py')).read())
else:
    cam_setup(SHOT); f0, f1 = SHOTS[SHOT]
    scene.frame_set(f0)
    FR = FR or f'{f0}-{f1}'
    render(N)
