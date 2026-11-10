"""Tube Town - barista episode v2 (natural timing, waiting montage, understated ending).  usage: python3 build13.py SHOT OUTDIR [opts]"""
import os, sys, random, json
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
exec(open(os.path.join(HERE, 'set13.py')).read())
from mathutils import Matrix
doug['mouth'].location.y = -0.326
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
VO = os.path.join(HERE, 'vo2')
T = json.load(open(os.path.join(VO, 'timing14.json'))); N = T['N']
def bump(f, c, w):
    x = abs(f - c) / w
    return 0.0 if x >= 1 else 0.5 * (1 + math.cos(math.pi * x))
def ramp(f, a, b): return 0.0 if f <= a else 1.0 if f >= b else smooth((f - a) / (b - a))
def idle(seed=0.0, amp=1.0):
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
def rot_layer(fn): return lambda f: (V(0, 0, 0), V(*fn(f)), (0, 0))
def world_to_local(rig, f, p):
    scene.frame_set(f); return tuple(rig.upper.matrix_world.inverted() @ Vector(p))
def wp(o): return o.matrix_world.translation.copy()

# ============================================================ BLOCKING + BEATS (all from the dialogue timing)
DPOS, DHEAD = (-0.8, 0.05), 55            # order spot
PICKP = (-0.8, PICK_Y)                    # pickup spot (same counter, nearer the door)
BPOS, BHEAD = (0.76, 0.05), -55
PICKB = (0.74, PICK_Y)
MACH = (1.18, 0.33)
CUP_PICK = V(0.03, PICK_Y, CT + 0.072)
CUP_TRAY = V(1.70, 0.18, CT + 0.072)
F_B1, F_B1E = T['b1']['fs'], T['b1']['fe']
F_D1, F_D1E = T['d1']['fs'], T['d1']['fe']
F_B2, F_B2E = T['b2']['fs'], T['b2']['fe']
LET = T['d2']['words']; F_D2E = T['d2']['fe']
F_B3, F_B3E = T['b3']['fs'], T['b3']['fe']
F_CALL, F_DOG, F_B4E = T['b4']['fs'], T['b4']['words'][3], T['b4']['fe']
F_SIGH, F_D3, F_D3E = T['d3']['f'], T['d3']['fs'], T['d3']['fe']
F_YEAH, F_B5E = T['b5']['fs'], T['b5']['fe']
# montage
F_WRITE0, F_WRITE1 = F_B3E - 6, F_B3E + 22          # writes the name right after "Got it!"
F_STEP0, F_STEP1 = F_B3E + 6, F_B3E + 34            # Doug walks to the pickup spot
F_TOMACH0, F_TOMACH1 = F_WRITE1, F_WRITE1 + 16      # barista to the machine
SH_D = (F_TOMACH1 + 1, F_TOMACH1 + 33)               # machine insert
F_POUR0, F_POUR1 = SH_D[0] + 2, SH_D[0] + 20
F_LID = SH_D[0] + 24
F_TOPICK0, F_TOPICK1 = SH_D[1] + 1, F_CALL - 6      # barista brings the cup over
# ending (v3): cup -> barista -> line -> "Yeah?" -> silent stare -> back to the cup -> gives up -> exit
F_NOTICE0, F_NOTICE1 = F_DOG + 2, F_DOG + 14        # Doug turns toward her, eyes go straight to the cup
F_LOWER0, F_LOWER1 = F_DOG + 12, F_DOG + 22         # she brings the raised cup down and out toward him
SH_G = (F_B4E + 10, F_B4E + 31)                      # over-the-shoulder: what Doug is looking at
F_EYES0 = SH_G[1] + 7; F_EYES1 = F_EYES0 + 14       # eyes drift cup -> barista
F_HEAD0, F_HEAD1 = F_EYES0 + 4, F_EYES1 + 4         # head follows
F_SET = F_B5E                                        # she sets it down as she says "Yeah?"
F_STARE1 = F_B5E + 30                                # ~1 s stare
F_BACKCUP0, F_BACKCUP1 = F_STARE1, F_STARE1 + 10    # looks back at the cup
F_DISAPP1 = F_BACKCUP1 + 18                          # disappointment settles
F_GIVEUP = F_BACKCUP1 + 4
F_TAKE = F_DISAPP1 + 10
F_TURN0, F_TURN1 = F_TAKE + 8, F_TAKE + 18
F_GO0 = F_TURN1

# ============================================================ DOUG
Ad = dict(down=lambda s: ((s * 0.37, -0.03, 0.06), ('auto', (s, 0.3, 0))),
          down2=lambda s: ((s * 0.36, 0.0, 0.03), ('auto', (s, 0.4, 0))))
def darms(**kw): return {side: (Ad[nm](-1 if side == 'N' else 1) if isinstance(nm, str) else nm) for side, nm in kw.items()}
dn = darms(N='down', P='down'); dn2 = darms(N='down2', P='down2')
swing_d = lambda f, ph: {'N': ((-0.37, 0.12 * math.sin(ph), 0.07), ('auto', (-1, 0.3, 0))), 'P': ((0.37, -0.12 * math.sin(ph), 0.07), ('auto', (1, 0.3, 0)))}
doug_r.walk(1, 30, (-2.25, -0.3), DPOS, 78, steps=3.2, arms=swing_d, lean=4, bob=0.035, sway=4)
for f in range(30, 39): doug_r.place(f, DPOS, 78 + (DHEAD - 78) * smooth((f - 30) / 8))
# listening nods: small one after the question, one per letter, one acknowledging "Got it"
nods = lambda f: (4 * bump(f, F_B1E + 8, 7) + sum(5 * bump(f, c + 4, 6) for c in LET) + 6 * bump(f, F_B3E + 3, 7))
S1 = [ST(doug_r, 31, (0, 0, -0.01), (2, 0, 0), 1.0, dn, 'stand'),
      ST(doug_r, 42, (0, 0, 0.0), (0, 0, 0), 1.0, dn, 'relaxed'),
      ST(doug_r, F_D1E + 10, (0.01, 0, 0.0), (0, 2, 0), 1.0, dn, 'relaxed'),
      ST(doug_r, F_B2E + 6, (0.01, 0, 0.0), (1, 3, 0), 1.0, dn, 'relaxed'),          # takes the question in
      ST(doug_r, LET[0] - 6, (0, 0, -0.01), (3, 0, 0), 1.0, dn, 'stand'),             # leans in slightly to spell
      ST(doug_r, F_D2E + 6, (0, 0, -0.01), (3, 0, 0), 1.0, dn, 'stand'),
      ST(doug_r, F_STEP0, (0, 0, 0.0), (0, 0, 0), 1.0, dn, 'stand')]
run(doug_r, 39, F_STEP0, S1, add_layers(idle(0), rot_layer(lambda f: (nods(f), 0, 0))))
for f in range(39, F_STEP0 + 1): doug_r.place(f, DPOS, DHEAD)
# walks along the counter to the pickup spot (turns toward it, walks, turns back to face the counter)
doug_r.walk(F_STEP0, F_STEP1, DPOS, PICKP, DHEAD, steps=2.6, arms=swing_d, lean=3, bob=0.03, sway=3,
            hfun=lambda t: DHEAD + (8 - DHEAD) * smooth(min(1, t / 0.3)) + (DHEAD - 8) * smooth(max(0, (t - 0.72) / 0.28)))
# waits: weight shifts, glances around, blank stare
F_WAIT0 = F_STEP1 + 1
S2 = [ST(doug_r, F_WAIT0, (0, 0, 0), (1, 0, 0), 1.0, dn2, 'relaxed2'),
      ST(doug_r, SH_D[1] + 8, (0.012, 0, 0), (0, -2, -10), 1.0, dn2, 'relaxed2'),       # glances off toward the room
      ST(doug_r, F_TOPICK1 - 4, (-0.008, 0, 0), (1, 2, 4), 1.0, dn2, 'relaxed'),       # weight shift, blank stare
      ST(doug_r, F_NOTICE0, (0, 0, 0), (1, 1, 2), 1.0, dn2, 'relaxed'),
      ST(doug_r, F_NOTICE1, (0, 0, -0.005), (6, 0, 8), 1.0, dn2, 'stand'),             # turns to her, looking at the cup
      ST(doug_r, SH_G[1], (0, 0, -0.008), (8, 3, 8), 1.0, dn2, 'stand'),                # ...processing (tiny head tilt)
      ST(doug_r, F_HEAD0, (0, 0, -0.008), (8, 3, 8), 1.0, dn2, 'stand'),
      ST(doug_r, F_HEAD1, (0, 0, -0.008), (2, 1, 8), 1.0, dn2, 'stand'),                # head follows his eyes up to her
      ST(doug_r, F_SIGH + 10, (0, 0, -0.018), (3, 0, 8), 0.985, dn2, 'stand'),          # small breath out before speaking
      ST(doug_r, F_D3 + 6, (0, 0, -0.012), (2, 0, 8), 1.0, darms(N=((-0.17, -0.42, 0.48), ('auto', (-1, 0.1, -0.2))), P='down2'), 'stand'),
      ST(doug_r, F_D3E - 2, (0, 0, -0.012), (2, 0, 8), 1.0, darms(N=((-0.15, -0.43, 0.5), ('auto', (-1, 0.1, -0.2))), P='down2'), 'stand'),
      ST(doug_r, F_D3E + 10, (0, 0, -0.012), (2, 0, 8), 1.0, dn2, 'stand'),
      ST(doug_r, F_STARE1, (0, 0, -0.012), (2, 0, 8), 1.0, dn2, 'stand'),               # the stare: dead still
      ST(doug_r, F_BACKCUP1, (0, 0, -0.014), (9, 0, 6), 1.0, dn2, 'stand'),             # looks back down at the cup
      ST(doug_r, F_DISAPP1, (0, 0, -0.03), (10, 0, 6), 0.97, dn2, 'stand'),             # shoulders sink
      ST(doug_r, F_TAKE - 8, (0, 0, -0.025), (9, 0, 6), 0.975, dn2, 'stand')]
run(doug_r, F_WAIT0, F_TAKE - 8, S2, idle(40, 0.6))
for f in range(F_WAIT0, F_TURN0 + 1): doug_r.place(f, PICKP, DHEAD)
reach_loc = world_to_local(doug_r, F_TAKE, CUP_PICK + V(-0.01, -0.05, -0.02))
hold_d = ((-0.3, -0.3, 0.42), ('auto', (-1, 0.2, -0.3)))
S3 = [ST(doug_r, F_TAKE - 8, (0, 0, -0.025), (9, 0, 6), 0.975, dn2, 'stand'),
      ST(doug_r, F_TAKE, (0, 0, -0.03), (10, 0, 4), 1.0, darms(N=(reach_loc, ('auto', (-1, 0.2, -0.3))), P='down2'), 'stand'),
      ST(doug_r, F_TAKE + 8, (0, 0, -0.01), (2, 0, 0), 1.0, darms(N=hold_d, P='down'), 'stand')]
run(doug_r, F_TAKE - 8, F_TAKE + 8, S3)
EXITH = -50; P1 = (PICKP[0] - 0.95, PICKP[1] - 0.8)
for f in range(F_TURN0, F_TURN1 + 1):
    doug_r.place(f, PICKP, DHEAD + (EXITH - DHEAD) * smooth((f - F_TURN0) / (F_TURN1 - F_TURN0)))
    doug_r.pose(f, up=(0, 0, -0.01), rot=(2, 0, 0), arms=darms(N=hold_d, P='down'), legs=LEGS['stand']())
swing_c = lambda f, ph: {'N': hold_d, 'P': ((0.37, -0.12 * math.sin(ph), 0.07), ('auto', (1, 0.3, 0)))}
doug_r.walk(F_GO0, N + 4, PICKP, P1, EXITH, steps=4.0, arms=swing_c, lean=4, bob=0.035, sway=3)

# ============================================================ BARISTA
on_ctr = {'N': ((-0.2, -0.38, 0.5), ('auto', (-1, 0.2, -0.3))), 'P': ((0.2, -0.38, 0.5), ('auto', (1, 0.2, -0.3)))}
bari_r.place(1, BPOS, BHEAD)
reach_stack = world_to_local(bari_r, 1, (0.2, 0.6, CT + 0.06))
reach_mk = world_to_local(bari_r, 1, (0.12, -0.3, CT + 0.03))
cup_chest = ((0.22, -0.33, 0.44), ('auto', (1, 0.2, -0.4)))
mk_ready = ((-0.08, -0.38, 0.52), ('auto', (-1, 0.1, -0.4)))
mk_write = ((0.04, -0.43, 0.54), ('auto', (-1, 0.1, -0.4)))
cup_write = ((0.1, -0.41, 0.48), ('auto', (1, 0.2, -0.4)))
F_GRAB = 40
bnods = lambda f: (5 * bump(f, 34, 6) + sum(3 * bump(f, c + 7, 6) for c in LET) + 6 * bump(f, F_D2E + 8, 7) + 4 * bump(f, F_B3 + 16, 6))
S = [ST(bari_r, 1, (0, 0, 0), (4, 0, 0), 1.0, on_ctr, 'stand'),
     ST(bari_r, F_GRAB - 4, (0, 0, 0), (4, 0, 0), 1.0, on_ctr, 'stand'),
     ST(bari_r, F_GRAB + 4, (0, 0, 0.0), (6, 0, 8), 1.0, {'N': (reach_mk, ('auto', (-1, 0.2, -0.3))), 'P': (reach_stack, ('auto', (1, 0.2, -0.2)))}, 'stand'),
     ST(bari_r, F_GRAB + 14, (0, 0, 0.01), (1, 0, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'relaxed'),
     ST(bari_r, F_B1 + 12, (0, 0, 0.0), (3, 4, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'relaxed'),          # casual tilt on the question
     ST(bari_r, F_D1E + 4, (0, 0, 0.0), (2, 2, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'relaxed'),
     ST(bari_r, F_B2 - 6, (0, 0, -0.005), (0, -5, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'relaxed'),        # small "hm?" tilt
     ST(bari_r, F_B2 + 14, (0, 0, -0.008), (4, -2, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'stand'),
     ST(bari_r, LET[0], (0, 0, -0.01), (5, 0, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'stand'),             # listens, eye contact
     ST(bari_r, F_D2E + 4, (0, 0, -0.01), (4, 0, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'stand'),
     ST(bari_r, F_B3 + 6, (0, 0, 0.012), (-3, 2, 0), 1.0, {'N': mk_ready, 'P': cup_chest}, 'relaxed'),        # "Perfect."
     ST(bari_r, F_WRITE0, (0, 0, -0.01), (10, 0, 0), 1.0, {'N': mk_write, 'P': cup_write}, 'stand'),          # writes it down
     ST(bari_r, F_WRITE1, (0, 0, -0.01), (10, 0, 0), 1.0, {'N': mk_write, 'P': cup_write}, 'stand')]
run(bari_r, 1, F_WRITE1, S, add_layers(idle(13, 1.0), rot_layer(lambda f: (bnods(f), 0, 0))))
for f in range(1, F_WRITE1 + 1): bari_r.place(f, BPOS, BHEAD)
for f in range(F_WRITE0 + 2, F_WRITE1 - 1):        # marker strokes: three letters
    v = 1.0
    h = Vector(mk_write[0]) + V(0.014 * math.sin(f * 1.9), 0, 0.012 * math.sin(f * 2.7 + 1) - 0.004 * ((f - F_WRITE0) / 10))
    st = interp(S, f); bari_r.pose(f, up=tuple(st['up']), rot=tuple(st['rot']), arms={'N': (h, ('auto', (-1, 0.1, -0.4)))})
# to the machine
def bari_move(fa, fb, pa, pb, ha, hb, arms_fn, turn_frac=0.35):
    for f in range(fa, fb + 1):
        t = (f - fa) / max(1, fb - fa)
        p = Vector(pa).lerp(Vector(pb), smooth(t)); h = ha + (hb - ha) * smooth(min(1, t / turn_frac))
        bari_r.place(f, tuple(p), h)
        ph = t * math.pi * 3
        legs = {'N': ((-0.15, 0.08 * math.sin(ph), 0.05 * max(0, math.sin(ph))), (0, -1, 0.3)), 'P': ((0.15, -0.08 * math.sin(ph), 0.05 * max(0, -math.sin(ph))), (0, -1, 0.3))}
        bari_r.pose(f, up=(0, 0, -0.012 * abs(math.sin(ph))), rot=(3, 2 * math.sin(ph), 0), arms=arms_fn(f, ph), legs=legs)
carry = lambda f, ph: {'N': ((-0.34, 0.08 * math.sin(ph), 0.1), ('auto', (-1, 0.3, 0))), 'P': cup_chest}
bari_move(F_TOMACH0, F_TOMACH1, BPOS, MACH, BHEAD, 90, carry, 0.55)
# at the machine: cup on the tray, pour, lid on (N hand = camera side)
bari_r.place(SH_D[0], MACH, 90)
tray_loc = world_to_local(bari_r, SH_D[0], CUP_TRAY + V(0, -0.06, 0.0))
lever_loc = world_to_local(bari_r, SH_D[0], (1.74, 0.42, CT + 0.32))
lid_hi = world_to_local(bari_r, SH_D[0], CUP_TRAY + V(0, -0.01, 0.16))
lid_on = world_to_local(bari_r, SH_D[0], CUP_TRAY + V(0, -0.01, 0.1))
lid_hi = world_to_local(bari_r, SH_D[0], CUP_TRAY + V(0, 0.05, 0.16))
lid_on = world_to_local(bari_r, SH_D[0], CUP_TRAY + V(0, 0.04, 0.1))
side_N = ((-0.34, -0.1, 0.16), ('auto', (-1, 0.3, 0)))          # near arm stays down, out of the insert
S4 = [ST(bari_r, SH_D[0], (0, 0, -0.01), (8, 0, 0), 1.0, {'N': side_N, 'P': (lever_loc, ('auto', (1, 0.2, -0.3)))}, 'stand'),
      ST(bari_r, F_POUR1 - 4, (0, 0, -0.01), (8, 0, 0), 1.0, {'N': side_N, 'P': (lever_loc, ('auto', (1, 0.2, -0.3)))}, 'stand'),
      ST(bari_r, F_POUR1 + 2, (0, 0, -0.01), (8, 0, 0), 1.0, {'N': side_N, 'P': (lid_hi, ('auto', (1, 0.2, -0.3)))}, 'stand'),
      ST(bari_r, F_LID, (0, 0, -0.015), (10, 0, 0), 1.0, {'N': side_N, 'P': (lid_on, ('auto', (1, 0.2, -0.3)))}, 'stand'),
      ST(bari_r, SH_D[1], (0, 0, -0.01), (6, 0, 0), 1.0, {'N': side_N, 'P': (lid_on, ('auto', (1, 0.2, -0.3)))}, 'stand')]
run(bari_r, SH_D[0], SH_D[1], S4)
for f in range(SH_D[0], SH_D[1] + 1): bari_r.place(f, MACH, 90)
# brings it to the pickup end (cup now in the N hand while walking, swaps to P on arrival)
carryN = lambda f, ph: {'N': ((-0.22, -0.33, 0.44), ('auto', (-1, 0.2, -0.4))), 'P': ((0.34, -0.08 * math.sin(ph), 0.1), ('auto', (1, 0.3, 0)))}
bari_move(F_TOPICK0, F_TOPICK1, MACH, PICKB, 90, BHEAD, carryN, 0.45)
CUP_HAND_SWAP = F_TOPICK1 - 2
call_hand = ((-0.12, -0.3, B_EZ - 0.1), ('auto', (-1, 0, -0.3)))
cup_up = ((0.34, 0.08, B_EZ - 0.06), ('auto', (1, 0.3, -0.2)))       # holds it up beside her head
cup_offer = ((0.14, -0.42, 0.48), ('auto', (1, 0.2, -0.4)))
set_loc = world_to_local(bari_r, F_SET, CUP_PICK + V(0.03, 0.02, -0.02))
S5 = [ST(bari_r, F_TOPICK1, (0, 0, 0), (2, 0, 0), 1.0, {'N': on_ctr['N'], 'P': cup_chest}, 'stand'),
      ST(bari_r, F_CALL + 4, (0, 0, 0.01), (-4, 0, -8), 1.0, {'N': call_hand, 'P': cup_chest}, 'stand'),     # calls out to the room
      ST(bari_r, F_DOG - 6, (0, 0, 0.01), (-4, 0, -8), 1.0, {'N': call_hand, 'P': cup_chest}, 'stand'),
      ST(bari_r, F_DOG + 2, (0, 0, 0.03), (-6, 2, -2), 1.0, {'N': on_ctr['N'], 'P': cup_up}, 'relaxed'),     # holds it up: "DOG!"
      ST(bari_r, F_LOWER0, (0, 0, 0.025), (-4, 2, 0), 1.0, {'N': on_ctr['N'], 'P': cup_up}, 'relaxed'),
      ST(bari_r, F_LOWER1, (0, 0, 0.0), (1, 0, 0), 1.0, {'N': on_ctr['N'], 'P': cup_offer}, 'relaxed'),     # holds it out to him
      ST(bari_r, F_D3E + 2, (0, 0, 0.005), (1, 2, 0), 1.0, {'N': on_ctr['N'], 'P': cup_offer}, 'relaxed'),
      ST(bari_r, F_YEAH - 2, (0, 0, 0.01), (-2, 3, 0), 1.0, {'N': on_ctr['N'], 'P': cup_offer}, 'relaxed'),
      ST(bari_r, F_SET, (0, 0, -0.005), (7, 4, 4), 1.0, {'N': on_ctr['N'], 'P': (set_loc, ('auto', (1, 0.2, -0.3)))}, 'relaxed'),  # "Yeah?" + sets it down, sure of herself
      ST(bari_r, F_SET + 12, (0, 0, 0.005), (1, 4, 0), 1.0, on_ctr, 'relaxed'),
      ST(bari_r, F_GO0 + 10, (0, 0, 0.005), (1, 3, 0), 1.0, on_ctr, 'relaxed'),
      ST(bari_r, N, (0, 0, 0.0), (2, 1, -6), 1.0, on_ctr, 'relaxed')]
run(bari_r, F_TOPICK1, N, S5, idle(29, 1.0))
for f in range(F_TOPICK1, N + 1): bari_r.place(f, PICKB, BHEAD + (-25 - BHEAD) * ramp(f, F_GO0 + 4, N))

# ============================================================ PROPS + FACES + HAT (baked per frame)
exec(open(os.path.join(HERE, 'face14.py')).read())
exec(open(os.path.join(HERE, 'cams14_test.py')).read())
hat_objs = [o for o in bpy.data.objects if o.name.startswith('hat_')]
hat_rest = {o: o.rotation_euler.copy() for o in hat_objs}
MARKER_REST = V(0.12, -0.3, CT + 0.012)
def cup_owner(f):
    if f < F_GRAB + 4: return 'stack'
    if f < SH_D[0]: return 'bariP'
    if f <= SH_D[1] - 1: return 'tray'
    if f < CUP_HAND_SWAP: return 'bariN'
    if f < F_SET + 1: return 'bariP'
    if f < F_TAKE + 1: return 'pick'
    return 'doug'
def cup_pos(ow):
    if ow == 'stack': return V(0.18, 0.62, CT + 0.07 + 6 * 0.028 + 0.02)
    if ow == 'tray': return CUP_TRAY.copy()
    if ow == 'pick': return CUP_PICK.copy()
    rig, side = {'bariP': (bari_r, 'P'), 'bariN': (bari_r, 'N'), 'doug': (doug_r, 'N')}[ow]
    h = wp(rig.hand[side]); R = rig.root.matrix_world.to_3x3().normalized()
    return h + R @ V(0.0, -0.055, 0.0) + V(0, 0, 0.01)
TEXT_ON = F_WRITE1 - 4
prev_owner, blend_from, blend_f = None, None, -99
up_hist = []
for f in range(1, N + 1):
    scene.frame_set(f)
    ow = cup_owner(f); p = cup_pos(ow)
    if ow != prev_owner:
        if prev_owner is not None: blend_from, blend_f = cup.location.copy(), f
        prev_owner = ow
    if f - blend_f < 4 and f != SH_D[0]: p = blend_from.lerp(p, smooth((f - blend_f) / 4))
    cup.location = p
    # where the lettering faces: toward her while writing, away from camera at the machine, toward camera from the call on
    if f < SH_D[0]:   tgt = wp(bari_r.upper) + V(0, 0, 0.8)
    elif f < F_CALL - 4: tgt = p + V(1, 0.3, 0)
    else:             tgt = cam_pos(f)
    d = tgt - p; cup.rotation_euler = (0, 0, math.atan2(d.x, -d.y))
    cup.keyframe_insert('location', frame=f); cup.keyframe_insert('rotation_euler', frame=f)
    dog_txt.hide_render = f < TEXT_ON; dog_txt.keyframe_insert('hide_render', frame=f)
    # lid goes on at the machine
    lid_off = 1.0 if f < F_LID - 6 else max(0.0, 1 - (f - (F_LID - 6)) / 6)
    for o, z0 in zip(cup_lids, LID_Z):
        o.hide_render = f < F_POUR1; o.location.z = z0 + 0.07 * lid_off
        o.keyframe_insert('hide_render', frame=f); o.keyframe_insert('location', frame=f)
    crema.hide_render = not (F_POUR0 + 6 <= f < F_LID); crema.keyframe_insert('hide_render', frame=f)
    stream.hide_render = not (F_POUR0 <= f <= F_POUR1); stream.keyframe_insert('hide_render', frame=f)
    if F_GRAB + 4 <= f < F_TOMACH0 + 4:
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
F_STOP = F_GO1 = -10
if SHOT == 'QA':
    for nm in SHOTS: cam_setup(nm)
    f0, f1 = 1, N
    exec(open(os.path.join(HERE, 'qa12.py')).read())
    json.dump({'SHOTS': SHOTS, 'F_SET': F_SET, 'F_TAKE': F_TAKE, 'F_GO0': F_GO0, 'F_GIVEUP': F_GIVEUP, 'F_STARE1': F_STARE1, 'F_DISAPP1': F_DISAPP1, 'N': N}, open(os.path.join(HERE, 'beats14.json'), 'w'))
else:
    cam_setup(SHOT); f0, f1 = SHOTS[SHOT]
    scene.frame_set(f0)
    FR = FR or f'{f0}-{f1}'
    render(N)
