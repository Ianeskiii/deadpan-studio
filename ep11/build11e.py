"""Tube Town - robbed but the music's still playing (v2: rubber-hose rig + source choreography).
Global timeline 480 frames @30fps, 120 BPM (beat = 15 frames).  usage: python3 build11b.py SHOT OUTDIR [opts]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
exec(open(os.path.join(HERE, 'set11.py')).read())
ricky['mouth'] = sphere('ricky_mouth', 0.03, M['mouth'], (0, -0.262, ricky['ez'] - 0.19), (1.3, 0.5, 0.5), parent=ricky['root'])
MASK = mat('mask_black', hexc('#111114'), 0.6, 0.3)
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.276, depth=0.1, location=(0, 0, ricky['ez'] + 0.005))
mk = bpy.context.active_object; mk.name = 'ricky_mask'; finish(mk, MASK, ricky['root'])
for sx in (-1, 1):
    box('mask_tail', (0.03, 0.02, 0.13), (sx * 0.05, 0.285, ricky['ez'] - 0.05), MASK, 0.008, ricky['root']).rotation_euler = (0, sx * D(25), 0)
se = empty('rsmile_e', (0, -0.266, ricky['ez'] - 0.19), ricky['root'])
ricky_smile = noodle('ricky_smile', [(-0.06, 0, 0.012), (0.0, -0.004, -0.016), (0.07, 0, 0.03)], 0.012, M['mouth'], se)
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
wave_hand = lambda dx: {'P': ((-0.5, -0.66 - dx, 1.02), ('auto', (1, 0, -0.2))), 'N': ((-0.33, 0.05, 0.25), (-0.42, 0.05, 0.42))}
for k, f in enumerate(range(138, 166, 4)):
    ricky_r.pose(f, up=(0, 0, 0.04), rot=(6, 0, 0), arms=wave_hand(0.14 if k % 2 else -0.1), legs=LEGS['stand']())
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
scratch = lambda dx: {'N': ((-0.1 + dx, -0.05, R_EZ + 0.32), ('auto', (-1, -0.3, 0))), 'P': ((0.38, -0.2, 0.05), ('auto', (1, 0.3, 0)))}
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
up_hist = []; U = doug_r.upper
for f in range(1, 481):
    scene.frame_set(f)
    Mu = U.matrix_world
    rh = (wp(ricky_r.hand['N']) + wp(ricky_r.hand['P'])) / 2
    bx_ = doug_r.bmods[0][0].angle; by_ = doug_r.bmods[0][1].angle
    hip = Mu @ (V(-0.37, -0.02, 0.37) + doug_r.disp(math.degrees(bx_), math.degrees(by_)))
    shoulder = Mu @ V(0.22, -0.08, doug_r.sh_z + 0.2); chest = Mu @ V(-0.05, -0.335, doug_r.sh_z - 0.02)
    if GRAB + 4 <= f < RELEASE:          # Ricky pulls the bag; strap stays hooked on Doug's shoulder
        bp = rh + V(0, 0, -0.06); a, c = shoulder, bp + V(0, 0, 0.13); mid = (a + c) / 2 + V(0, 0, -0.02)
        brot = (0, 0, D(90))
    else:
        bp, a, mid, c = hip, shoulder, chest, hip + V(0, 0, 0.13); brot = (0, 0, Mu.to_euler().z)
    bag.location = bp; bag.rotation_euler = brot
    bag.keyframe_insert('location', frame=f); bag.keyframe_insert('rotation_euler', frame=f)
    for i, pt in enumerate(sp_.points):
        t = i / (NS - 1); v = (1 - t) ** 2 * a + 2 * (1 - t) * t * mid + t ** 2 * c
        pt.co = (v.x, v.y, v.z, 1.0); pt.keyframe_insert('co', frame=f)
    up_hist.append(U.rotation_euler.copy())
for f in range(1, 481):
    cur = up_hist[f - 1]; old = up_hist[max(0, f - 4)]
    for o in hat_objs:
        r0 = hat_rest[o]; o.rotation_euler = (r0.x + 0.6 * (old.x - cur.x), r0.y + 0.6 * (old.y - cur.y), r0.z)
        o.keyframe_insert('rotation_euler', frame=f)
scene.frame_set(1)

# ============================================================ CAMERAS v5 - all from the front side (Ricky screen-left, Doug screen-right)
SHOTS = {'E1': (1, 90), 'E2': (91, 135), 'E3': (136, 165), 'E4': (166, 195), 'E5': (196, 285), 'E6': (286, 300),
         'E7': (301, 360), 'E8': (361, 420), 'E9': (421, 450), 'E10': (451, 480)}
f0, f1 = SHOTS[SHOT]
def shake(f, amp):
    return V(amp * (math.sin(f * 0.37) + 0.5 * math.sin(f * 0.91 + 1.3)), amp * 0.6 * math.sin(f * 0.53 + 2.1),
             amp * (math.sin(f * 0.29 + 0.5) + 0.4 * math.sin(f * 1.13)))
def shoot(p0, p1, tgt, lens, fstop, amp=0.012, focus_fn=None):
    cam_data.lens = lens; cam_data.dof.aperture_fstop = fstop
    for f in range(f0, f1 + 1, 2):
        t = (f - f0) / max(1, f1 - f0)
        key(cam, 'location', f, p0.lerp(p1, smooth(t)) + shake(f, amp))
        scene.frame_set(f)
        tp = tgt(f) if callable(tgt) else tgt
        key(target, 'location', f, tp + shake(f + 40, amp * 0.6))
        key(focus, 'location', f, focus_fn(f) if focus_fn else tp)
def dpos(z=0.95): return lambda f: wp(dr) + V(0, 0, z)
def rface(): return lambda f: ricky_r.upper.matrix_world @ V(0, -0.2, R_EZ - 0.05)
def dface(): return lambda f: doug_r.upper.matrix_world @ V(0, -0.2, D_EZ - 0.08)
MID = V((RX0 + DX) / 2, DY, 0.85)
if SHOT == 'E1':      # front, tracking the groove-walk
    shoot(V(DX + 0.1, 2.2, 0.98), V(DX - 0.15, 1.75, 0.98), dpos(0.95), 28, 3.2, focus_fn=lambda f: wp(dr) + V(0, -0.3, 0.9))
elif SHOT == 'E2':    # two-shot: Ricky demands the bag, Doug keeps dancing
    shoot(V(-0.25, 1.45, 1.0), V(-0.25, 1.6, 1.0), V(-0.25, DY, 0.92), 24, 3.5)
elif SHOT == 'E3':    # Doug's face: eyes shut, singing, Ricky's hand waving in front of him
    scene.frame_set(150); fp = dface()(150)
    shoot(fp + V(-0.1, -1.05, -0.04), fp + V(-0.1, -0.95, -0.04), dface(), 30, 2.6, amp=0.008)
elif SHOT == 'E4':    # wide: the grab
    shoot(V(-0.25, 1.0, 1.0), V(-0.25, 1.1, 0.98), V(-0.25, DY, 0.85), 21, 4.0)
elif SHOT == 'E5':    # SLOW-MO low wide: Doug's giling swings Ricky around on the strap
    shoot(V(-0.2, 1.3, 0.42), V(-0.15, 1.5, 0.45), V(-0.25, DY, 0.95), 19, 3.5, amp=0.006, focus_fn=lambda f: wp(dr) + V(0, 0, 0.9))
elif SHOT == 'E6':    # reaction: Ricky straining, frustrated
    scene.frame_set(293); rp = rface()(293)
    shoot(rp + V(0.42, -1.25, 0.0), rp + V(0.4, -1.15, 0.0), rface(), 30, 2.6, amp=0.012)
elif SHOT == 'E7':    # WIDE: Ricky pulls with everything, Doug vogues + kembots + fist-pumps
    shoot(V(-0.3, 0.75, 1.05), V(-0.3, 0.9, 1.02), V(-0.3, DY, 0.82), 19, 4.5)
elif SHOT == 'E8':    # medium-wide: fist pumps, the spin, Ricky flung onto his butt
    shoot(V(-0.4, 0.65, 0.95), V(-0.5, 0.7, 0.92), V(-0.55, DY, 0.75), 18, 4.5, amp=0.014)
elif SHOT == 'E9':    # reaction: Ricky on the ground, confused, scratching his head
    scene.frame_set(435); rp = rface()(435)
    shoot(rp + V(0.35, -1.3, 0.12), rp + V(0.32, -1.2, 0.1), rface() if False else (lambda f: rface()(f) + V(0, 0, -0.12)), 30, 2.6, amp=0.01)
elif SHOT == 'E10':   # wide: Ricky gives up, Doug grooves off screen-right
    shoot(V(-0.85, 1.0, 0.95), V(-0.8, 1.05, 0.95), V(-0.75, DY - 0.15, 0.6), 18, 4.5)
scene.frame_set(f0)
FR = FR or f'{f0}-{f1}'
render(480)
