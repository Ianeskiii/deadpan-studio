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
    def setup_bend(self, mesh_names, origin_z):
        self.bend_org = empty(self.name + '_bendorg', (0, 0, origin_z), self.upper)
        self.bmods = []
        for nm in mesh_names:
            ob = bpy.data.objects[nm]; me = ob.data
            bm = bmesh.new(); bm.from_mesh(me)
            bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.25], cuts=12, use_grid_fill=True)
            bm.to_mesh(me); bm.free()
            mods = []
            for ax in ('X', 'Y'):
                m = ob.modifiers.new('bend' + ax, 'SIMPLE_DEFORM'); m.deform_method = 'BEND'; m.deform_axis = ax
                m.origin = self.bend_org; m.limits = (0.0, 0.5); mods.append(m)
            self.bmods.append(mods)
        ob = bpy.data.objects[mesh_names[0]]
        def bottom(ax, ay):
            for mx, my in self.bmods: mx.angle = D(ax); my.angle = D(ay)
            bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get(); ev = ob.evaluated_get(dg); m = ev.to_mesh()
            zmin = min(v.co.z for v in m.vertices)
            pts = [v.co.copy() for v in m.vertices if v.co.z < zmin + 0.05]
            c = sum(pts, Vector()) / len(pts); ev.to_mesh_clear(); return c
        c0 = bottom(0, 0); self.dX = bottom(35, 0) - c0; self.dY = bottom(0, 35) - c0; bottom(0, 0)
        self.dX.z = 0; self.dY.z = 0
        self.FWD = 1 if self.dX.y < 0 else -1
        self.SIDE = 1 if self.dY.x > 0 else -1
        print('BEND', self.name, tuple(round(v, 3) for v in self.dX), tuple(round(v, 3) for v in self.dY))
    def disp(self, ax, ay):
        if not hasattr(self, 'bmods'): return V(0, 0, 0)
        g = lambda t: (1 - math.cos(t)) / t if abs(t) > 1e-5 else t / 2
        k = g(D(35)); return self.dX * (g(D(ax)) / k) + self.dY * (g(D(ay)) / k)
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
    def pose(self, f, up=(0, 0, 0), rot=(0, 0, 0), sq=1.0, arms=None, legs=None, bend=(0, 0)):
        """up: offset of the upper pivot from standing base; rot (deg) of upper body; arms/legs: {side: (hand|foot, bend|joint)}"""
        loc = V(0, 0, self.base) + V(*up)
        self.upper.location = loc; self.upper.keyframe_insert('location', frame=f)
        e = Euler((D(rot[0]), D(rot[1]), D(rot[2])))
        self.upper.rotation_euler = e; self.upper.keyframe_insert('rotation_euler', frame=f)
        self.upper.scale = (1 / math.sqrt(sq), 1 / math.sqrt(sq), sq); self.upper.keyframe_insert('scale', frame=f)
        for mods in getattr(self, 'bmods', []):
            for m_, a_ in zip(mods, bend):
                m_.angle = D(a_); m_.keyframe_insert('angle', frame=f)
        hd = self.disp(*bend)
        for side, spec in (arms or {}).items():
            hand, el = spec
            sh = self.shoulder(side); hand = Vector(hand)
            if isinstance(el, tuple) and len(el) == 2 and el[0] == 'auto':
                elbow = self.joint(sh, hand, self.arm_len, el[1])
            else:
                elbow = Vector(el)
            self.key_points(self.arm[side], f, (sh, elbow, hand))
            self.hand[side].location = hand; self.hand[side].keyframe_insert('location', frame=f)
        Me = e.to_matrix()
        for side, spec in (legs or {}).items():
            foot, bend = spec
            hip = loc + Me @ (self.hip_off[side] + hd)
            foot = V(*foot)
            knee = self.joint(hip, foot, self.leg_len, bend)
            self.key_points(self.leg[side], f, (hip, knee, foot))
            self.foot[side].location = foot + V(0, -0.035, 0.03); self.foot[side].keyframe_insert('location', frame=f)
    def place(self, f, xy, heading, z=0.0):
        self.root.location = (xy[0], xy[1], z); self.root.keyframe_insert('location', frame=f)
        self.root.rotation_euler = (0, 0, D(heading)); self.root.keyframe_insert('rotation_euler', frame=f)
    def walk(self, f0, f1, p0, p1, heading, steps, arms, crouch=0.0, lean=4, bob=0.035, lift=0.07, sway=5, arm_pump=None, hfun=None, bendfun=None):
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
            bd = bendfun(ph) if bendfun else (0, 0)
            self.pose(f, up=(0, 0, dip), rot=(lean + 4 * abs(math.cos(ph)), sway * math.sin(ph), 0), arms=arms_f, legs=legs, bend=bd)

doug_r = Rig(doug, 'doug', M['doug'], M['doug'], lift=0.17)
ricky_r = Rig(ricky, 'ricky', P['ricky'], P['track'], lift=0.15)
dr, rr = doug['root'], ricky['root']
doug_r.setup_bend(['doug_body'], (doug['zc'] + 0.15) - 0.25)
ricky_r.setup_bend(['ricky_body', 'jacket'], (ricky['zc'] + 0.1) - 0.25)
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
    bx_ = doug_r.bmods[0][0].angle; by_ = doug_r.bmods[0][1].angle
    hip = Mu @ (V(-0.37, -0.02, 0.37) + doug_r.disp(math.degrees(bx_), math.degrees(by_))); shoulder = Mu @ V(0.22, -0.08, doug_r.sh_z + 0.2); chest = Mu @ V(-0.05, -0.335, doug_r.sh_z - 0.02)
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

# ============================================================ CAMERAS (v3: 14 angles, handheld feel)
SHOTS = {
    'C1': (1, 45), 'C2': (46, 75), 'C3': (76, 90), 'C4': (91, 102), 'C5': (103, 150), 'C6': (151, 189),
    'C7': (190, 231), 'C8': (232, 273), 'C9': (274, 306), 'C10': (307, 339), 'C11': (340, 363),
    'C12': (364, 405), 'C13': (406, 450), 'C14': (451, 480)}
f0, f1 = SHOTS[SHOT]
def shake(f, amp):
    return V(amp * (math.sin(f * 0.37) + 0.5 * math.sin(f * 0.91 + 1.3)),
             amp * 0.6 * math.sin(f * 0.53 + 2.1),
             amp * (math.sin(f * 0.29 + 0.5) + 0.4 * math.sin(f * 1.13)))
def shoot(p0, p1, tgt, lens, fstop, amp=0.012, focus_fn=None):
    """camera moves p0->p1 with handheld shake; tgt: Vector or callable(f)->Vector"""
    cam_data.lens = lens; cam_data.dof.aperture_fstop = fstop
    for f in range(f0, f1 + 1, 2):
        t = (f - f0) / max(1, f1 - f0)
        key(cam, 'location', f, p0.lerp(p1, smooth(t)) + shake(f, amp))
        scene.frame_set(f)
        tp = tgt(f) if callable(tgt) else tgt
        key(target, 'location', f, tp + shake(f + 40, amp * 0.6))
        key(focus, 'location', f, focus_fn(f) if focus_fn else tp)
def dpos(z=0.95): return lambda f: wp(dr) + V(0, 0, z)
def dup_(z=0.95): return lambda f: wp(doug_r.upper) + V(0, 0, z)
if SHOT == 'C1':      # front, tracking the sassy walk
    shoot(V(DX + 0.25, 2.25, 0.95), V(DX + 0.22, 2.0, 0.95), dpos(0.95), 30, 3.2, focus_fn=lambda f: wp(dr) + V(0, -0.3, 0.9))
elif SHOT == 'C2':    # ground-level wide: Ricky sprints in and grabs
    shoot(V(-1.0, 1.55, 0.22), V(-0.85, 1.7, 0.24), V(-0.35, DY + 0.2, 0.75), 20, 4.0, amp=0.015)
elif SHOT == 'C3':    # punch-in close-up: arm fling, singing face
    shoot(V(0.95, 2.45, 0.95), V(0.88, 2.55, 0.97), V(0.28, DY, 1.42), 26, 2.8, amp=0.018)
elif SHOT == 'C4':    # over Ricky's shoulder: Doug turns, grabs the strap
    shoot(V(-1.75, 2.55, 1.15), V(-1.7, 2.65, 1.12), V(0.25, DY, 0.95), 24, 3.5)
elif SHOT == 'C5':    # SLOW-MO low angle behind Ricky, focus on Doug (Ricky soft in the foreground)
    shoot(V(TR[0] - 0.42, DY - 0.78, 0.3), V(TR[0] - 0.22, DY - 1.0, 0.33), V(TD[0] - 0.12, DY, 1.05), 22, 2.4, amp=0.006,
          focus_fn=lambda f: V(TD[0], DY, 1.0))
elif SHOT == 'C6':    # SLOW-MO waist-level close on the giling + arm whip
    shoot(V(TD[0] - 1.3, DY - 1.25, 0.8), V(TD[0] - 1.15, DY - 1.35, 0.85), dup_(0.6), 24, 2.6, amp=0.006)
elif SHOT == 'C7':    # 3/4 front of Doug: vogue hands + kembot, Ricky at the edge
    shoot(V(-0.85, 1.85, 1.1), V(-0.75, 1.95, 1.08), V(0.05, DY, 0.85), 22, 3.2, focus_fn=lambda f: wp(dr) + V(0, 0, 0.9))
elif SHOT == 'C8':    # Ricky's POV: fist pumps + giling straight at us
    shoot(V(TR[0] - 0.55, DY - 0.5, 1.38), V(TR[0] - 0.45, DY - 0.45, 1.35), V(TD[0] - 0.25, DY, 0.85), 24, 3.0, amp=0.014,
          focus_fn=lambda f: V(TD[0] - 0.2, DY, 0.9))
elif SHOT == 'C9':    # side-on wide: synchronized tug + hip thrusts
    shoot(V(-0.1, 0.75, 0.85), V(-0.1, 0.9, 0.85), V(-0.1, DY, 0.72), 17, 4.5)
elif SHOT == 'C10':   # reverse, low behind Doug looking at Ricky
    shoot(V(TD[0] + 1.0, DY + 0.85, 0.5), V(TD[0] + 0.9, DY + 0.75, 0.52), V(TR[0] + 0.1, DY, 0.75), 20, 3.5, amp=0.014)
elif SHOT == 'C11':   # low, close: the huge pull
    shoot(V(TD[0] + 1.25, DY - 1.55, 0.32), V(TD[0] + 1.15, DY - 1.45, 0.32), V(TD[0] - 0.5, DY, 0.8), 18, 4.0, amp=0.02)
elif SHOT == 'C12':   # high angle: Ricky falls, Doug lunges and yanks
    shoot(V(SITX + 0.75, DY - 1.35, 2.35), V(SITX + 0.7, DY - 1.2, 2.25), V(SITX + 0.65, DY, 0.35), 22, 4.0)
elif SHOT == 'C13':   # close-up: Ricky cringing
    fc = V(SITX, DY, 0.0) + V(0, 0, ricky_r.base - 0.38 + R_EZ)
    shoot(fc + V(1.0, -0.38, 0.14), fc + V(0.9, -0.34, 0.12), fc + V(0, 0.02, -0.06), 28, 2.8, amp=0.01, focus_fn=lambda f: fc + V(0.2, 0, 0))
elif SHOT == 'C14':   # front, tracking: grooves toward us again (loop)
    shoot(V(DX + 0.25, 3.05, 0.95), V(DX + 0.25, 2.25, 0.95), dpos(0.95), 30, 3.2, focus_fn=lambda f: wp(dr) + V(0, -0.3, 0.9))
scene.frame_set(f0)
FR = FR or f'{f0}-{f1}'
render(480)
