"""Tube Town - robbed but the music's still playing (v2: rubber-hose rig + source choreography).
Global timeline 480 frames @30fps, 120 BPM (beat = 15 frames).  usage: python3 build11b.py SHOT OUTDIR [opts]"""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
exec(open(os.path.join(HERE, 'set11.py')).read())
ricky['mouth'] = sphere('ricky_mouth', 0.03, M['mouth'], (0, -0.276, ricky['ez'] - 0.19), (1.3, 0.5, 0.5), parent=ricky['root'])
# FIX: Ricky's mouth sat inside the jacket shell and the zip ran over his chin -> lower the collar line
_j = bpy.data.objects['jacket']; bpy.data.objects.remove(_j, do_unlink=True)
capsule('jacket', 0.283, 0.3, P['track'], (0, 0, ricky['zc'] - 0.2), parent=ricky['root'])
for _o in bpy.data.objects:
    if _o.name.startswith('jstripe') or _o.name == 'zip':
        _o.scale.z = 0.4 / _o.dimensions.z if _o.dimensions.z else 1; _o.location.z = ricky['zc'] - 0.25
# FIX: Doug's mouth only protruded 9 mm from the body -> sits on the surface now (same size/shape)
doug['mouth'].location.y = -0.326
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
         ST(doug_r, REACT0 + 6, (0.02, 0, -0.03), (0, 3, -40), 1.0, arms(N=lift_cup, P='hp'), relaxed),
         ST(doug_r, REACT1 - 6, (0.02, 0, -0.03), (0, 3, -42), 1.0, arms(N=lift_cup, P='hp'), relaxed),
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
ricky_r.place(g + 66, (-0.45, DY - 0.08), 90); ricky_r.place(g + 72, (-0.6, DY - 0.08), 90)
ricky_r.pose(g + 72, up=(0, 0, 0.0), rot=(7, 0, 12), arms=palm_out, legs=LEGS['stand']())      # leans in, peering: "...hello?"
ricky_r.pose(GRAB - 4, up=(0, 0, -0.02), rot=(8, 0, 14), arms=palm_out, legs=LEGS['stand']())
ricky_r.place(GRAB - 2, (-0.6, DY - 0.08), 90); ricky_r.place(GRAB + 4, (-0.6, DY), 90)
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


# ---------------------------------------------------------------- bag + strap + hat lag + FACE (baked per frame)
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
exec(open(os.path.join(HERE, 'face_f.py')).read())
BAGP = V(0, 0, 0)
def bag_pt(): return BAGP.copy()
up_hist = []; U = doug_r.upper
for f in range(1, 481):
    scene.frame_set(f)
    Mu = U.matrix_world
    rh = (wp(ricky_r.hand['N']) + wp(ricky_r.hand['P'])) / 2
    bx_ = doug_r.bmods[0][0].angle; by_ = doug_r.bmods[0][1].angle
    hip = Mu @ (V(-0.37, -0.02, 0.37) + doug_r.disp(math.degrees(bx_), math.degrees(by_)))
    shoulder = Mu @ V(0.22, -0.08, doug_r.sh_z + 0.2); chest = Mu @ V(-0.05, -0.335, doug_r.sh_z - 0.02)
    if GRAB + 4 <= f < RELEASE:
        bp = rh + V(0, 0, -0.06); a, c = shoulder, bp + V(0, 0, 0.13); mid = (a + c) / 2 + V(0, 0, -0.02); brot = (0, 0, D(90))
    else:
        bp, a, mid, c = hip, shoulder, chest, hip + V(0, 0, 0.13); brot = (0, 0, Mu.to_euler().z)
    bag.location = bp; bag.rotation_euler = brot; BAGP = bp
    bag.keyframe_insert('location', frame=f); bag.keyframe_insert('rotation_euler', frame=f)
    for i, pt in enumerate(sp_.points):
        t = i / (NS - 1); v = (1 - t) ** 2 * a + 2 * (1 - t) * t * mid + t ** 2 * c
        pt.co = (v.x, v.y, v.z, 1.0); pt.keyframe_insert('co', frame=f)
    face_pass(f)
    up_hist.append(U.rotation_euler.copy())
for f in range(1, 481):
    cur = up_hist[f - 1]; old = up_hist[max(0, f - 4)]
    for o in hat_objs:
        r0 = hat_rest[o]; o.rotation_euler = (r0.x + 0.6 * (old.x - cur.x), r0.y + 0.6 * (old.y - cur.y), r0.z)
        o.keyframe_insert('rotation_euler', frame=f)
scene.frame_set(1)

# ============================================================ CAMERAS v6: 5 shots, one side of the action, wide on the struggle
SHOTS = {'A': (1, 60), 'B': (61, 180), 'C': (181, 350), 'D': (351, 427), 'E': (428, 480)}
def shake(f, amp):
    return V(amp * (math.sin(f * 0.37) + 0.5 * math.sin(f * 0.91 + 1.3)), amp * 0.6 * math.sin(f * 0.53 + 2.1),
             amp * (math.sin(f * 0.29 + 0.5) + 0.4 * math.sin(f * 1.13)))
def shoot(fa, fb, p0, p1, tgt, lens, fstop, amp=0.007, focus_fn=None):
    for f in range(fa, fb + 1, 2 if fb - fa > 2 else 1):
        t = (f - fa) / max(1, fb - fa)
        key(cam, 'location', f, p0.lerp(p1, smooth(t)) + shake(f, amp))
        scene.frame_set(f)
        tp = tgt(f) if callable(tgt) else tgt
        key(target, 'location', f, tp + shake(f + 40, amp * 0.6))
        key(focus, 'location', f, focus_fn(f) if focus_fn else tp)
        key(cam_data, 'lens', f, lens); key(cam_data.dof, 'aperture_fstop', f, fstop)
def cam_setup(name):
    fa, fb = SHOTS[name]
    if name == 'A':   # front, tracking the groove-walk; Green enters screen-left
        shoot(fa, fb, V(DX - 0.05, 2.0, 0.98), V(DX - 0.25, 1.75, 0.98), lambda f: wp(dr) + V(-0.12, 0, 0.92), 26, 3.5,
              focus_fn=lambda f: wp(dr) + V(0, -0.3, 0.9))
    elif name == 'B': # wide two-shot: demand, hand-wave, grab
        shoot(fa, fb, V(-0.22, 1.2, 1.0), V(-0.22, 1.45, 0.98), V(-0.22, DY, 0.9), 22, 4.0)
    elif name == 'C': # wide, a little low: slow-mo, struggle, spin, fling (one continuous take)
        shoot(fa, fb, V(-0.4, 0.8, 0.8), V(-0.45, 0.95, 0.82), V(-0.45, DY, 0.82), 19, 4.5)
    elif name == 'D': # medium two-shot favouring Green on the ground; Doug still dancing screen-right
        shoot(fa, fb, V(-0.82, 0.85, 0.92), V(-0.8, 1.0, 0.9), V(-0.75, DY - 0.1, 0.68), 18, 4.5)
    elif name == 'E': # Doug's deadpan check-in, Green in frame screen-left
        shoot(fa, fb, V(-0.6, 0.9, 1.02), V(-0.56, 1.1, 1.0), V(-0.55, DY - 0.05, 0.85), 18, 4.0)
if SHOT == 'QA':
    for nm in SHOTS: cam_setup(nm)
    f0, f1 = 1, 480
    exec(open(os.path.join(HERE, 'qa_full.py')).read())
elif SHOT.startswith('QA_'):
    nm = SHOT[3:]; cam_setup(nm); f0, f1 = SHOTS[nm]; SHOT = nm
    exec(open(os.path.join(HERE, 'qa_mouth.py')).read())
else:
    cam_setup(SHOT); f0, f1 = SHOTS[SHOT]
    scene.frame_set(f0)
    FR = FR or f'{f0}-{f1}'
    render(480)
