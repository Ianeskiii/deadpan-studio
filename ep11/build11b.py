"""Tube Town - robbed but the music's still playing (v2: rubber-hose rig + source choreography).
Global timeline 480 frames @30fps, 120 BPM (beat = 15 frames).  usage: python3 build11b.py SHOT OUTDIR [opts]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
exec(open(os.path.join(HERE, 'set11.py')).read())
ricky['mouth'] = sphere('ricky_mouth', 0.03, M['mouth'], (0, -0.262, ricky['ez'] - 0.19), (1.3, 0.5, 0.5), parent=ricky['root'])
from mathutils import Matrix
BEAT = 15
def bf(b): return 1 + BEAT * (b - 1)
def V(*a): return Vector(a)

# ============================================================ RUBBER-HOSE RIG
JOINTS = {}
class Rig:
    def __init__(self, C, name, body_m, arm_m, lift, leg_r=0.055, arm_r=0.042):
        self.C = C; self.root = C['root']; self.name = name
        self.base = 0.25 + lift                       # upper-body pivot height (bottom of the tube)
        self.upper = empty(name + '_upper', (0, 0, 0.25), self.root)
        bpy.context.view_layer.update()
        hips = C['legs']
        for o in list(self.root.children):
            if o in hips or o is self.upper: continue
            mw = o.matrix_world.copy(); o.parent = self.upper; o.matrix_world = mw
        for h in hips:
            for o in h.children: o.hide_render = True
        for side in ('L', 'R'):
            for o in C['arms'][side].children: o.hide_render = True
        self.upper.location = (0, 0, self.base)
        r = C['r']; self.sh_z = (C['zc'] - 0.035) - 0.25; self.sh_x = r - 0.02
        self.ez = C['ez'] - 0.25; self.top = C['top'] - 0.25
        self.hip_off = {'N': V(-r * 0.42, 0, 0.04), 'P': V(r * 0.42, 0, 0.04)}
        self.arm, self.hand, self.leg, self.foot = {}, {}, {}, {}
        for side, sx in (('N', -1), ('P', 1)):
            self.arm[side] = self._hose(name + '_arm' + side, self.upper, arm_r, arm_m)
            self.hand[side] = sphere(name + '_hh' + side, 0.066, body_m, (0, 0, 0), (1, 0.9, 1.05), parent=self.upper)
            self.leg[side] = self._hose(name + '_leg' + side, self.root, leg_r, body_m)
            self.foot[side] = sphere(name + '_ft' + side, 0.078, body_m, (0, 0, 0), (0.95, 1.45, 0.55), parent=self.root)
        self.leg_len = self.base + 0.03
        self.arm_len = 0.6
    def _hose(self, nm, parent, rad, m):
        cu = bpy.data.curves.new(nm, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = rad
        cu.bevel_resolution = 6; cu.use_fill_caps = True
        sp = cu.splines.new('POLY'); sp.points.add(2)
        o = link(bpy.data.objects.new(nm, cu)); o.data.materials.append(m); o.parent = parent
        JOINTS[o.name] = sphere(nm + '_jt', rad * 1.04, m, (0, 0, 0), parent=parent)
        return o
    def shoulder(self, side): return V(self.sh_x * (-1 if side == 'N' else 1), 0, self.sh_z)
    @staticmethod
    def joint(a, b, length, bend):
        mid = (a + b) / 2; d = (b - a).length
        h = math.sqrt(max(0.0, (length / 2) ** 2 - (d / 2) ** 2))
        bend = Vector(bend); ab = (b - a).normalized() if d > 1e-6 else V(0, 0, 1)
        bend = (bend - ab * bend.dot(ab)); bend = bend.normalized() if bend.length > 1e-6 else V(0, -1, 0)
        return mid + bend * max(h, 0.02)
    def key_points(self, crv, f, pts):
        for p, v in zip(crv.data.splines[0].points, pts):
            p.co = (v.x, v.y, v.z, 1.0); p.keyframe_insert('co', frame=f)
        j = JOINTS[crv.name]; j.location = pts[1]; j.keyframe_insert('location', frame=f)
    def pose(self, f, up=(0, 0, 0), rot=(0, 0, 0), sq=1.0, arms=None, legs=None):
        """up: offset of the upper pivot from standing base; rot (deg) of upper body; arms/legs: {side: (hand|foot, bend|joint)}"""
        loc = V(0, 0, self.base) + V(*up)
        self.upper.location = loc; self.upper.keyframe_insert('location', frame=f)
        e = Euler((D(rot[0]), D(rot[1]), D(rot[2])))
        self.upper.rotation_euler = e; self.upper.keyframe_insert('rotation_euler', frame=f)
        self.upper.scale = (1 / math.sqrt(sq), 1 / math.sqrt(sq), sq); self.upper.keyframe_insert('scale', frame=f)
        for side, spec in (arms or {}).items():
            hand, el = spec
            sh = self.shoulder(side); hand = V(*hand)
            elbow = V(*el) if len(el) == 3 and isinstance(el, tuple) and el[0] != 'auto' else None
            if elbow is None:
                elbow = self.joint(sh, hand, self.arm_len, el[1])
            self.key_points(self.arm[side], f, (sh, elbow, hand))
            self.hand[side].location = hand; self.hand[side].keyframe_insert('location', frame=f)
        Me = e.to_matrix()
        for side, spec in (legs or {}).items():
            foot, bend = spec
            hip = loc + Me @ (self.hip_off[side])
            foot = V(*foot)
            knee = self.joint(hip, foot, self.leg_len, bend)
            self.key_points(self.leg[side], f, (hip, knee, foot))
            self.foot[side].location = foot + V(0, -0.035, 0.03); self.foot[side].keyframe_insert('location', frame=f)
    def place(self, f, xy, heading, z=0.0):
        self.root.location = (xy[0], xy[1], z); self.root.keyframe_insert('location', frame=f)
        self.root.rotation_euler = (0, 0, D(heading)); self.root.keyframe_insert('rotation_euler', frame=f)
    def walk(self, f0, f1, p0, p1, heading, steps, arms, crouch=0.0, lean=4, bob=0.035, lift=0.07, sway=5, arm_pump=None, hfun=None):
        dist = math.dist(p0, p1); sl = dist / max(steps, 1e-6)
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(1, f1 - f0)
            x = p0[0] + (p1[0] - p0[0]) * t; y = p0[1] + (p1[1] - p0[1]) * t
            self.place(f, (x, y), heading if hfun is None else hfun(t))
            ph = math.pi * steps * t
            legs = {}
            for i, side in enumerate(('N', 'P')):
                u = ((ph + i * math.pi) / (2 * math.pi)) % 1.0
                sx = -0.15 if side == 'N' else 0.15
                if u < 0.5:
                    fy = -sl / 2 + (u / 0.5) * sl; fz = 0.0
                else:
                    v = (u - 0.5) / 0.5; fy = sl / 2 - v * sl; fz = lift * math.sin(math.pi * v)
                legs[side] = ((sx, fy, fz), (0, -1, 0.3))
            dip = -bob * (1 - abs(math.sin(ph))) - crouch
            arms_f = arms(f, ph) if callable(arms) else arms
            self.pose(f, up=(0, 0, dip), rot=(lean + 4 * abs(math.cos(ph)), sway * math.sin(ph), 0), arms=arms_f, legs=legs)

doug_r = Rig(doug, 'doug', M['doug'], M['doug'], lift=0.17)
ricky_r = Rig(ricky, 'ricky', P['ricky'], P['track'], lift=0.15)
dr, rr = doug['root'], ricky['root']
D_EZ = doug_r.ez; R_EZ = ricky_r.ez

# ---------------------------------------------------------------- arm poses (upper-local; character faces local -y)
def mir(v): return (-v[0], v[1], v[2])
A = dict(
    hp=lambda s: ((s * 0.39, -0.03, D_EZ), (s * 0.58, 0.04, D_EZ - 0.22)),
    down=lambda s: ((s * 0.37, -0.02, 0.05), ('auto', (s, 0.3, 0))),
    up=lambda s: ((s * 0.42, 0.05, D_EZ + 0.7), ('auto', (s, 0, 0))),
    behind=lambda s: ((s * 0.1, 0.3, D_EZ + 0.12), (s * 0.58, 0.12, D_EZ + 0.2)),
    pull=lambda s: ((s * 0.07, -0.78, 0.5), ('auto', (s, 0, -0.4))),
    pull_hi=lambda s: ((s * 0.06, -0.8, 0.62), ('auto', (s, 0, -0.4))),
)
def arms(**kw):
    out = {}
    for side, name in kw.items():
        s = -1 if side == 'N' else 1
        out[side] = A[name](s) if isinstance(name, str) else name
    return out
LEGS = dict(
    stand=lambda: {'N': ((-0.15, 0.0, 0), (0, -1, 0.2)), 'P': ((0.15, 0.0, 0), (0, -1, 0.2))},
    wide=lambda: {'N': ((-0.42, 0.02, 0), (-1, -0.6, 0.5)), 'P': ((0.42, 0.02, 0), (1, -0.6, 0.5))},
    brace=lambda: {'N': ((-0.18, -0.5, 0), (0, -1, 0.4)), 'P': ((0.2, 0.32, 0), (0, -1, 0.2))},   # front foot forward
    brace_w=lambda: {'N': ((-0.3, -0.55, 0), (-0.4, -1, 0.4)), 'P': ((0.3, 0.35, 0), (0.4, -1, 0.2))},
    sit=lambda: {'N': ((-0.2, -0.6, 0.0), (0, -0.2, 1)), 'P': ((0.22, -0.55, 0.0), (0, -0.2, 1))},
)
def mouth_open(C, f, amt):
    m = C['mouth']; key(m, 'scale', f, V(1 + 0.6 * amt, 1, 1 + 1.4 * amt) if C is doug else V(1 + 0.8 * amt, 1, 1 + 1.5 * amt))
def lids(C, f, deg):
    for o in bpy.data.objects:
        if o.name.startswith(C['root'].name + '_lid'): key(o, 'rotation_euler', f, Euler((D(deg), 0, 0)))
def brows(C, f, dz, tilt, z0):
    for i, bp in enumerate(C['brows']):
        sx = -1 if i == 0 else 1
        key(bp, 'location', f, V(bp.location.x, bp.location.y, z0[i] + dz)); key(bp, 'rotation_euler', f, Euler((0, sx * D(tilt), 0)))
DBZ = [bp.location.z for bp in doug['brows']]; RBZ = [bp.location.z for bp in ricky['brows']]

# ============================================================ CHOREOGRAPHY
DX, DY = 0.3, 3.4          # Doug's spot
TD, TR = (0.55, DY), (-1.05, DY)    # tug positions (Doug faces -x, Ricky faces +x)
lids(doug, 1, 40)
lids(ricky, 1, 26)
# ---- S1 (1-70): Doug grooves toward camera, hands on headphones; one step per beat
doug_r.walk(1, 70, (DX, 5.0), (DX, DY), 0, steps=70 / BEAT, arms=arms(N='hp', P='hp'), lean=6, bob=0.045, sway=6)
for b in range(5):
    mouth_open(doug, bf(b + 1), 0.35 if b % 2 else 0.0); mouth_open(doug, bf(b + 1) + 7, 0.0)
# ---- Ricky sprints in crouched (40-68) and grabs (70)
rr.location = (-6, 6, 0)
ricky_r.place(1, (-6, 6), 65)
pump = lambda f, ph: {'N': ((-0.3, -0.25 * math.sin(ph), 0.25), ('auto', (-1, 0.2, 0))), 'P': ((0.3, 0.25 * math.sin(ph), 0.25), ('auto', (1, 0.2, 0)))}
ricky_r.walk(40, 66, (-2.9, 4.7), (-0.82, DY + 0.05), 65, steps=7, arms=pump, crouch=0.1, lean=24, bob=0.03, lift=0.09, sway=3)
ricky_r.place(39, (-6, 6), 65)
GRAB = 70
ricky_r.place(GRAB, (-0.78, DY), 90)
ricky_r.pose(GRAB, up=(0, 0, -0.06), rot=(12, 0, 0), arms={'N': ((-0.08, -0.58, 0.42), ('auto', (-1, 0, -0.3))), 'P': ((0.08, -0.58, 0.42), ('auto', (1, 0, -0.3)))}, legs=LEGS['brace']())
brows(ricky, GRAB, -0.02, 18, RBZ)
# ---- S3 (71-102): Doug flings an arm up on the beat (mouthing the lyrics), then turns and grabs the strap
F = bf(5) + 15   # 76 beat hit
doug_r.place(72, (DX, DY), 0)
doug_r.pose(72, up=(0, 0, -0.03), rot=(5, 0, 0), arms=arms(N='hp', P='hp'), legs=LEGS['stand']())
doug_r.pose(F, up=(0, 0, 0.04), rot=(-4, 8, 4), sq=1.05, arms=arms(N='hp', P='up'), legs=LEGS['wide']())
mouth_open(doug, F - 2, 0.0); mouth_open(doug, F, 1.0); mouth_open(doug, F + 10, 0.6); mouth_open(doug, F + 18, 0.0)
lids(doug, F - 2, 40); lids(doug, F, 8); lids(doug, F + 14, 40)
ricky_r.place(F + 6, (-0.78, DY), 90); ricky_r.place(F + 12, (-1.0, DY), 90)
ricky_r.pose(F + 12, up=(0, 0, -0.08), rot=(-22, 0, 0), arms={'N': ((-0.08, -0.62, 0.45), ('auto', (-1, 0, -0.3))), 'P': ((0.08, -0.62, 0.45), ('auto', (1, 0, -0.3)))}, legs=LEGS['brace']())
doug_r.place(F + 8, (DX, DY), 0)
doug_r.pose(F + 10, up=(0, 0, -0.06), rot=(4, -14, 0), arms=arms(N=((-0.75, -0.2, 0.45), ('auto', (-1, 0, -0.3))), P='up'), legs=LEGS['wide']())
doug_r.place(F + 20, TD, -90)
doug_r.pose(F + 22, up=(0, 0, -0.1), rot=(-12, 0, 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace']())
ricky_r.place(F + 22, TR, 90)
ricky_r.pose(F + 22, up=(0, 0, -0.08), rot=(-18, 0, 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace']())
# ---- S4 SLOW-MO (103-189): Doug leans way back, hand behind head, slow hip sway, arm whip, both hands
S4 = 103
seq = [  # (frame, up, rot, arms, legs)
    (S4, (0, 0, -0.12), (-22, 6, 0), arms(N='pull', P='behind'), 'brace_w'),
    (S4 + 20, (0.05, 0, -0.15), (-26, -8, -4), arms(N='pull', P='behind'), 'brace_w'),
    (S4 + 40, (-0.05, 0, -0.13), (-24, 9, 4), arms(N='pull', P='behind'), 'brace_w'),
    (S4 + 52, (0, 0, -0.1), (-20, 0, 0), arms(N='pull', P=((0.5, -0.05, D_EZ + 0.55), ('auto', (1, 0, 0)))), 'brace_w'),
    (S4 + 62, (0, 0, -0.08), (-18, 4, 0), arms(N='pull', P=((0.2, -0.2, D_EZ + 0.78), ('auto', (1, 0, 0)))), 'brace_w'),
    (S4 + 74, (0, 0, -0.14), (-28, 0, 0), arms(N='pull_hi', P='pull_hi'), 'brace_w'),
    (S4 + 86, (0, 0, -0.15), (-30, -4, 0), arms(N='pull_hi', P='pull_hi'), 'brace_w'),
]
for f, up, rot, a_, lg in seq: doug_r.pose(f, up=up, rot=rot, arms=a_, legs=LEGS[lg]())
mouth_open(doug, S4 + 50, 0.0); mouth_open(doug, S4 + 60, 0.8); mouth_open(doug, S4 + 72, 0.0)
for k, f in enumerate(range(S4, S4 + 87, 12)):   # Ricky straining, small jerks
    ricky_r.pose(f, up=(0, 0, -0.1 - 0.02 * (k % 2)), rot=(-20 - 4 * (k % 2), 3 * (1 if k % 2 else -1), 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace']())
brows(ricky, S4, -0.025, 22, RBZ)
# ---- S5 POV (190-273): Ricky holds the bag; Doug dances with his arms: vogue hand-waves, then fist pumps
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
k = 0
for f in range(S5, 232, 7):
    a_ = (V1, V3, V2, V3)[k % 4]
    doug_r.pose(f, up=(0, 0, -0.035 if k % 2 == 0 else 0.01), rot=(4, 5 * (1 if k % 2 else -1), 6 * (1 if (k // 2) % 2 else -1)), arms=a_, legs=LEGS['wide']()); k += 1
k = 0
for f in range(232, 274, 7):
    a_ = FP1 if k % 2 == 0 else FP2
    doug_r.pose(f, up=(0, 0, -0.05 if k % 2 == 0 else 0.0), rot=(10, 0, 10 * (1 if k % 2 == 0 else -1)), arms=a_, legs=LEGS['wide']()); k += 1
    mouth_open(doug, f, 0.6 if k % 2 else 0.1)
# ---- S6 side (274-339): synchronized tug, both lean back hard, pumping on every beat
S6 = 274
doug_r.place(S6, TD, -90); ricky_r.place(S6, TR, 90)
for k, f in enumerate(range(S6, 340, 15)):
    m = f + 7
    doug_r.pose(f, up=(0, 0, -0.16), rot=(-34, 0, 0), sq=0.96, arms=arms(N='pull_hi', P='pull_hi'), legs=LEGS['brace_w']())
    doug_r.pose(m, up=(0, 0, -0.1), rot=(-26, 0, 4 * (1 if k % 2 else -1)), sq=1.03, arms=arms(N='pull', P='pull'), legs=LEGS['brace_w']())
    ricky_r.pose(f, up=(0, 0, -0.14), rot=(-26, 0, 0), sq=0.96, arms=arms(N='pull_hi', P='pull_hi'), legs=LEGS['brace']())
    ricky_r.pose(m, up=(0, 0, -0.08), rot=(-18, 0, 0), sq=1.03, arms=arms(N='pull', P='pull'), legs=LEGS['brace']())
    doug_r.place(f, (TD[0] + 0.04, DY), -90); doug_r.place(m, (TD[0] - 0.02, DY), -90)
    ricky_r.place(f, (TR[0] - 0.04, DY), 90); ricky_r.place(m, (TR[0] + 0.02, DY), 90)
# ---- S7 (340-363): one huge lean-back pull; Ricky yanked off balance
S7 = 340
doug_r.pose(S7, up=(0, 0, -0.12), rot=(-28, 0, 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace_w']())
doug_r.pose(S7 + 9, up=(0, 0, -0.24), rot=(-50, 0, 0), sq=0.94, arms=arms(N='pull_hi', P='pull_hi'), legs=LEGS['brace_w']())
doug_r.pose(S7 + 22, up=(0, 0, -0.2), rot=(-42, 0, 0), arms=arms(N='pull_hi', P='pull_hi'), legs=LEGS['brace_w']())
doug_r.place(S7 + 9, (TD[0] + 0.12, DY), -90)
ricky_r.pose(S7 + 4, up=(0, 0, -0.08), rot=(-20, 0, 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace']())
ricky_r.pose(S7 + 12, up=(0, 0, 0.02), rot=(30, 0, 0), arms=arms(N='pull_hi', P='pull_hi'), legs={'N': ((-0.15, -0.45, 0.08), (0, -1, 0.4)), 'P': ((0.15, 0.4, 0), (0, -1, 0.2))})
ricky_r.place(S7 + 4, TR, 90); ricky_r.place(S7 + 14, (TR[0] + 0.35, DY), 90)
# falls on his butt
FALL = S7 + 20
SITX = TR[0] + 0.45
ricky_r.place(FALL, (SITX, DY), 90)
ricky_r.pose(FALL, up=(0, 0, -0.4), rot=(-10, 0, 0), sq=0.9, arms=hold_bag, legs=LEGS['sit']())
ricky_r.pose(FALL + 4, up=(0, 0, -0.33), rot=(-14, 0, 0), sq=1.04, arms=hold_bag, legs=LEGS['sit']())
ricky_r.pose(FALL + 8, up=(0, 0, -0.38), rot=(-10, 0, 0), sq=1.0, arms=hold_bag, legs=LEGS['sit']())
lids(ricky, FALL, 26); lids(ricky, FALL + 2, 60)
# ---- S8 (364-405): Doug lunges, grabs the bag, yanks it free
S8 = 364
doug_r.place(S8, (TD[0] + 0.1, DY), -90)
doug_r.pose(S8, up=(0, 0, -0.18), rot=(-30, 0, 0), arms=arms(N='pull', P='pull'), legs=LEGS['brace_w']())
doug_r.place(S8 + 12, (SITX + 1.12, DY), -90)
doug_r.pose(S8 + 12, up=(0, 0, -0.2), rot=(28, 0, 0), arms={'N': ((-0.07, -0.7, 0.1), ('auto', (-1, 0, 0.3))), 'P': ((0.07, -0.7, 0.1), ('auto', (1, 0, 0.3)))}, legs=LEGS['brace_w']())
YANK = S8 + 24
doug_r.pose(YANK, up=(0, 0, -0.08), rot=(-22, 0, 0), arms=arms(N=((-0.1, -0.45, 0.62), ('auto', (-1, 0, -0.4))), P=((0.1, -0.45, 0.62), ('auto', (1, 0, -0.4)))), legs=LEGS['brace']())
doug_r.place(YANK, (SITX + 1.3, DY), -90)
doug_r.pose(YANK + 14, up=(0, 0, 0.0), rot=(0, 6, 0), arms=arms(N=((-0.37, -0.05, 0.1), ('auto', (-1, 0.3, 0))), P='hp'), legs=LEGS['stand']())
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
# ---- S10 (451-480): back to grooving toward camera, hands on headphones (loops into S1)
ricky_r.place(450, (SITX, DY), 90); ricky_r.place(451, (-6, 6), 65)
doug_r.walk(451, 480, (DX, 5.8), (DX, 5.0 + (5.0 - DY) / 70 * 0.0), 0, steps=2.0, arms=arms(N='hp', P='hp'), lean=6, bob=0.045, sway=6)
lids(doug, 451, 40)

# ---------------------------------------------------------------- bag + strap + hat lag (baked per frame)
bag = empty('bag')
box('bag_body', (0.1, 0.32, 0.26), (0, 0, 0), P['bag'], 0.03, bag)
box('bag_flap', (0.105, 0.33, 0.12), (0, 0, 0.07), mat('flap', hexc('#3a3e43'), 0.7), 0.02, bag)
strap_cu = bpy.data.curves.new('strap', 'CURVE'); strap_cu.dimensions = '3D'; strap_cu.bevel_depth = 0.018
strap_cu.bevel_resolution = 3; strap_cu.use_fill_caps = True
NS = 12
sp_ = strap_cu.splines.new('POLY'); sp_.points.add(NS - 1)
strap = link(bpy.data.objects.new('strap', strap_cu)); strap.data.materials.append(P['bag'])
hat_objs = [o for o in bpy.data.objects if o.name.startswith('hat_')]
hat_rest = {o: o.rotation_euler.copy() for o in hat_objs}
def wp(o): return o.matrix_world.translation.copy()
up_hist = []
U = doug_r.upper
for f in range(1, 481):
    scene.frame_set(f)
    Mu = U.matrix_world
    rh = (wp(ricky_r.hand['N']) + wp(ricky_r.hand['P'])) / 2
    dh = (wp(doug_r.hand['N']) + wp(doug_r.hand['P'])) / 2
    hip = Mu @ V(-0.37, -0.02, 0.37); shoulder = Mu @ V(0.22, -0.08, doug_r.sh_z + 0.2); chest = Mu @ V(-0.05, -0.335, doug_r.sh_z - 0.02)
    if f < GRAB:
        bp, a, mid, c = hip, shoulder, chest, hip + V(0, 0, 0.13)
    elif f < F + 20:                     # Ricky has it; strap still over Doug's shoulder
        bp = rh + V(0, 0, -0.06); a, c = shoulder, bp + V(0, 0, 0.13); mid = (a + c) / 2
    elif f < S5 or (S6 <= f < YANK):     # both pulling: strap from Doug's hands to the bag in Ricky's hands
        bp = rh + V(0, 0, -0.06); a = wp(doug_r.hand['N']) if f < S4 + 74 else dh; c = bp + V(0, 0, 0.13); mid = (a + c) / 2 + V(0, 0, -0.02)
    elif f < S6:                          # POV section: Ricky clutches it, strap to Doug's shoulder
        bp = rh + V(0, 0, -0.06); a, c = shoulder, bp + V(0, 0, 0.13); mid = (a + c) / 2 + V(0, 0, -0.08)
    elif f < YANK + 14:                   # Doug holds it after the yank
        bp = dh + V(0, 0, -0.1); a, c = shoulder, bp + V(0, 0, 0.13); mid = (a + c) / 2
    else:
        bp, a, mid, c = hip, shoulder, chest, hip + V(0, 0, 0.13)
    bag.location = bp; bag.rotation_euler = (0, 0, Mu.to_euler().z)
    bag.keyframe_insert('location', frame=f); bag.keyframe_insert('rotation_euler', frame=f)
    for i, pt in enumerate(sp_.points):
        t = i / (NS - 1)
        v = (1 - t) ** 2 * a + 2 * (1 - t) * t * mid + t ** 2 * c
        pt.co = (v.x, v.y, v.z, 1.0); pt.keyframe_insert('co', frame=f)
    up_hist.append(U.rotation_euler.copy())
for f in range(1, 481):          # hat lags behind the body (overlapping action)
    cur = up_hist[f - 1]; old = up_hist[max(0, f - 4)]
    for o in hat_objs:
        r0 = hat_rest[o]
        o.rotation_euler = (r0.x + 0.6 * (old.x - cur.x), r0.y + 0.6 * (old.y - cur.y), r0.z)
        o.keyframe_insert('rotation_euler', frame=f)
scene.frame_set(1)

# ============================================================ CAMERAS
SHOTS = {'S1': (1, 75), 'S3': (76, 102), 'S4': (103, 189), 'S5': (190, 273), 'S6': (274, 339),
         'S7': (340, 363), 'S8': (364, 405), 'S9': (406, 450), 'S10': (451, 480)}
f0, f1 = SHOTS[SHOT]
cam_data.dof.aperture_fstop = 4.0
def track_doug(fa, fb, off=V(0, 0, 1.05)):
    for f in range(fa, fb + 1, 5):
        scene.frame_set(f); key(target, 'location', f, wp(dr) + off); key(focus, 'location', f, wp(dr) + V(0, -0.3, 1.0))
if SHOT in ('S1', 'S10'):
    key(cam, 'location', f0, V(DX + 0.32, 1.25, 1.02)); key(cam, 'location', f1, V(DX + 0.3, 1.35, 1.02))
    track_doug(f0, f1); cam_data.lens = 26
elif SHOT == 'S3':
    key(cam, 'location', f0, V(0.35, 1.05, 1.1)); key(cam, 'location', f1, V(0.25, 1.2, 1.05))
    target.location = (-0.15, DY, 1.0); focus.location = (0.1, DY, 1.0); cam_data.lens = 24
elif SHOT == 'S4':   # low behind Ricky (slow-mo)
    key(cam, 'location', f0, V(TR[0] - 0.55, DY - 0.62, 0.34)); key(cam, 'location', f1, V(TR[0] - 0.42, DY - 0.52, 0.36))
    target.location = (TD[0] - 0.15, DY, 1.12); focus.location = (TD[0], DY, 1.05); cam_data.lens = 22; cam_data.dof.aperture_fstop = 3.5
elif SHOT == 'S5':   # over Doug's shoulder, looking at Ricky
    key(cam, 'location', f0, V(TD[0] + 1.35, DY + 1.05, 1.78)); key(cam, 'location', f1, V(TD[0] + 1.25, DY + 0.95, 1.74))
    target.location = (TR[0] + 0.2, DY, 0.75); focus.location = (TR[0] + 0.15, DY, 0.9); cam_data.lens = 24; cam_data.dof.aperture_fstop = 3.2
elif SHOT == 'S6':   # side-on wide
    key(cam, 'location', f0, V(-0.1, 0.7, 0.85)); key(cam, 'location', f1, V(-0.1, 0.85, 0.85))
    target.location = (-0.1, DY, 0.72); focus.location = (-0.1, DY, 0.8); cam_data.lens = 17
elif SHOT == 'S7':   # low, close on the big pull
    key(cam, 'location', f0, V(TD[0] + 1.25, DY - 1.55, 0.32)); key(cam, 'location', f1, V(TD[0] + 1.15, DY - 1.45, 0.32))
    target.location = (TD[0] - 0.5, DY, 0.8); focus.location = (TD[0], DY, 0.8); cam_data.lens = 18
elif SHOT == 'S8':
    key(cam, 'location', f0, V(0.9, 1.55, 1.25)); key(cam, 'location', f1, V(0.8, 1.7, 1.2))
    target.location = (SITX + 0.35, DY, 0.45); focus.location = (SITX + 0.4, DY, 0.5); cam_data.lens = 22
elif SHOT == 'S9':   # Ricky's face, cringing
    fc = V(SITX, DY, 0.0) + V(0, 0, ricky_r.base - 0.38 + R_EZ)
    key(cam, 'location', f0, fc + V(1.0, -0.38, 0.14)); key(cam, 'location', f1, fc + V(0.9, -0.34, 0.12))
    target.location = fc + V(0, 0.02, -0.06); focus.location = fc + V(0.2, 0, 0); cam_data.lens = 28; cam_data.dof.aperture_fstop = 2.8
scene.frame_set(f0)
FR = FR or f'{f0}-{f1}'
render(480)
