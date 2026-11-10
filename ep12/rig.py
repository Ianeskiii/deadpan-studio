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

