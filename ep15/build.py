"""Tube Town - When Someone Is Lying Straight to Your Face.  Doug + Green (Ricky's model) + the cake.
usage: cd ep15 && python3 build.py SHOT OUTDIR [--still F] [--samples N] [--pct P] [--engine cycles] [--step S]
  SHOT = A..I  (film shots, ranges in beats.json)  |  TEST (the approved style frame)  |  QA (print checks)
Pipeline: vo.py -> timing.py -> build.py QA -> render.sh -> audio.py -> overlays.py -> assemble.py
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
from mathutils import Matrix
def V(*a): return Vector(a)
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
BT = json.load(open(os.path.join(HERE, 'beats.json'))); N = BT['N']
TM = json.load(open(os.path.join(HERE, 'vo', 'timing.json')))
VO = os.path.join(HERE, 'vo')
tina['root'].location = (-80, 0, 0)
for o in list(bpy.data.objects):
    if o.name.startswith(('phone', 'screen')) and o.parent and o.parent.name.startswith('tina'): o.hide_render = True

# ============================================================ LIVING ROOM (ep14 set, evening, lamp-lit)
R_ = dict(
    floor=brick_mat('planks2', hexc('#6b4a33'), hexc('#5f412c'), hexc('#3f2a1c'), 1.2, 1.6, 0.18, 0.37, 0.55),
    wall=mat('lr_wall', hexc('#55687c'), 0.9), wall2=mat('lr_wall2', hexc('#465668'), 0.9),
    couch=mat('couch', hexc('#5a6e5a'), 0.85, 0.0, sheen=0.5), cushion=mat('cushion', hexc('#667d66'), 0.85, 0.0, sheen=0.5),
    wood=mat('lr_wood', hexc('#4a3426'), 0.5, 0.2), black=mat('tvblack', hexc('#111214'), 0.3, 0.4),
    rug=mat('rug', hexc('#7a4d4a'), 0.95), night=mat('night', (0, 0, 0), 0.5, 0, hexc('#2b3f78'), 0.6),
    plant=mat('leaf2', hexc('#2f5e3a'), 0.6), pot=mat('pot2', hexc('#8a5a3c'), 0.6), frame=mat('pframe', hexc('#c9a26a'), 0.4, 0.4),
    art=mat('art', hexc('#a35a6a'), 0.8), lamp=mat('lamp2', (0, 0, 0), 0.4, 0, hexc('#ffcf8a'), 3.0),
)
box('lr_floor', (10, 10, 0.1), (0, 0, -0.05), R_['floor'])
box('lr_back', (10, 0.2, 3.2), (0, -2.15, 1.6), R_['wall'])
box('lr_rear', (10, 0.2, 3.2), (0, 1.55, 1.6), R_['wall2'])
box('lr_left', (0.2, 8, 3.2), (-2.6, 0, 1.6), R_['wall2'])
box('lr_right', (0.2, 8, 3.2), (2.6, 0, 1.6), R_['wall'])
box('lr_ceiling', (10, 10, 0.1), (0, 0, 3.2), R_['wall2'])
box('rug', (2.6, 2.0, 0.012), (0, -0.85, 0.006), R_['rug'], 0.004)
box('window', (0.05, 1.2, 1.1), (2.47, 0.2, 1.6), R_['night'])
for wy in (-0.4, 0.2, 0.8): box('win_mull', (0.06, 0.05, 1.15), (2.45, wy, 1.6), R_['wood'])
SEAT = 0.42
box('couch_base', (2.0, 0.85, SEAT - 0.12), (0, 0.15, (SEAT - 0.12) / 2), R_['couch'], 0.04)
for cx in (-0.48, 0.48): box('seat_cushion', (0.94, 0.8, 0.13), (cx, 0.12, SEAT - 0.065), R_['cushion'], 0.05)
box('couch_back', (2.0, 0.24, 0.62), (0, 0.5, SEAT + 0.22), R_['couch'], 0.08)
for cx in (-0.98, 0.98): box('arm_rest', (0.24, 0.9, 0.55), (cx, 0.15, 0.36), R_['couch'], 0.08)
TVW, TVH, TVZ, TVY = 1.72, 0.97, 1.12, -1.95
box('cabinet', (2.1, 0.45, 0.5), (0, TVY + 0.02, 0.25), R_['wood'], 0.02)
box('tv_body', (TVW + 0.06, 0.06, TVH + 0.06), (0, TVY, TVZ), R_['black'], 0.01)
box('tv_foot', (0.5, 0.25, 0.04), (0, TVY + 0.02, 0.52), R_['black'])
TABLE = V(0.15, -0.95, 0.405)                                   # coffee-table top centre
box('coffee_table', (0.9, 0.5, 0.05), (TABLE.x, TABLE.y, 0.38), R_['wood'], 0.01)
for lx in (-0.25, 0.55):
    for ly in (-1.15, -0.75): box('ct_leg', (0.04, 0.04, 0.36), (lx, ly, 0.18), R_['wood'])
cyl('pot', 0.16, 0.32, (-1.9, -1.7, 0.16), R_['pot'])
for i in range(7):
    a_ = i * 2.3; sphere('leaf', 0.13, R_['plant'], (-1.9 + 0.1 * math.cos(a_), -1.7 + 0.1 * math.sin(a_), 0.5 + 0.06 * (i % 3)), (1, 0.5, 1.7), rot=(D(20) * math.cos(a_), D(20) * math.sin(a_), a_))
box('art_frame', (0.7, 0.04, 0.5), (1.4, -2.03, 1.75), R_['frame'], 0.01); box('art', (0.62, 0.02, 0.42), (1.4, -2.0, 1.75), R_['art'])
box('art_frame2', (0.6, 0.04, 0.45), (-0.9, 1.43, 1.65), R_['frame'], 0.01); box('art2', (0.52, 0.02, 0.37), (-0.9, 1.40, 1.65), mat('art2', hexc('#5f8fb0'), 0.8))
cyl('lamp_pole', 0.015, 1.4, (2.2, 1.25, 0.7), R_['black']); sphere('lamp_shade', 0.14, R_['lamp'], (2.2, 1.25, 1.45), (1, 1, 0.8))
pl = bpy.data.lights.new('corner', 'POINT'); pl.energy = 60; pl.color = hexc('#ffc27a'); pl.shadow_soft_size = 0.2
link(bpy.data.objects.new('corner', pl)).location = (2.2, 1.25, 1.42)
world(hexc('#232a38'), 0.35)
def aimed_area(name, loc, tgt, power, color, size):
    q = (V(*tgt) - V(*loc)).to_track_quat('-Z', 'Y')
    return area(name, loc, q.to_euler(), power, color, size)
aimed_area('key', (1.3, -1.6, 2.5), (-0.2, -0.5, 1.0), 190, hexc('#ffe0b8'), (1.4, 1.4))
aimed_area('fill', (-1.8, -1.6, 1.6), (-0.3, -0.4, 1.0), 45, hexc('#b8c8ff'), (1.0, 1.0))
aimed_area('rim', (-1.2, 1.2, 2.2), (0, 0, 1.3), 70, hexc('#8fa6ff'), (1.0, 1.0))
aimed_area('rim_d', (-2.2, -0.2, 2.0), (-1.0, -1.2, 1.2), 50, hexc('#8fa6ff'), (0.8, 0.8))

# ============================================================ GREEN (Ricky's model from ep11, no robber mask / headphones)
G_ = dict(
    beanie=mat('beanie', hexc('#7d7a4a'), 0.95, 0, sheen=0.6),
    track=mat('track', hexc('#1f6f78'), 0.55, 0.1),
    stripe=mat('stripe', hexc('#e9e4d0'), 0.6),
    ricky=mat('ricky', hexc('#8fbf6a'), 0.38, 0.6),
    iris_r=mat('iris_r', hexc('#3b2a1a'), 0.3, 0.8),
)
green = character('ricky', G_['ricky'], 0.27, 0.55, G_['iris_r'], 0.095, 0.11, lids=True)
gr = green['root']; gtop = green['top']
sphere('beanie', 0.285, G_['beanie'], (0, 0, gtop - 0.1), (1, 1, 0.85), parent=gr, half=True)
bpy.ops.mesh.primitive_torus_add(major_radius=0.27, minor_radius=0.045, location=(0, 0, gtop - 0.1))
finish(bpy.context.active_object, G_['beanie'], gr)
capsule('mustache', 0.022, 0.1, M['brow'], (0, -0.272, green['ez'] - 0.13), rot=(0, D(90), 0), parent=gr)
capsule('jacket', 0.283, 0.3, G_['track'], (0, 0, green['zc'] - 0.2), parent=gr)          # ep11 v2 collar line
for sx in (-1, 1):
    box('jstripe', (0.03, 0.02, 0.4), (sx * 0.12, -0.278, green['zc'] - 0.25), G_['stripe'], 0.008, gr)
box('zip', (0.012, 0.012, 0.4), (0, -0.284, green['zc'] - 0.25), G_['stripe'], 0, gr)
G_MOUTH_Z = green['ez'] - 0.19
green['mouth'] = sphere('ricky_mouth', 0.03, M['mouth'], (0, -0.276, G_MOUTH_Z), (1.3, 0.5, 0.5), parent=gr)
# the evidence: chocolate frosting smeared around his mouth (thin flattened blobs on the body surface)
CHOC = mat('choc', hexc('#3d2216'), 0.35, 0.3)
FROST = mat('frosting', hexc('#4a2a1b'), 0.25, 0.5)
SPONGE = mat('sponge', hexc('#5b3423'), 0.85)
CREAM = mat('cream', hexc('#f1e6d4'), 0.5)
SMEAR = mat('smear', hexc('#5e3119'), 0.18, 0.8)            # glossy milk-chocolate: reads apart from his dark mustache
def smear_blob(x, z, s, sx=1.6, sz=0.9, tilt=0):
    y = -math.sqrt(max(0.2715 ** 2 - x * x, 0))
    sphere('smear', s, SMEAR, (x, y, G_MOUTH_Z + z), (sx, 0.18, sz), parent=gr, rot=(0, D(tilt), math.atan2(x, -y)))
for i in range(22):           # a messy ring of frosting round the mouth, heavier at the corners and on the chin
    a = 2 * math.pi * i / 22
    x = 0.068 * math.cos(a); z = -0.004 + 0.034 * math.sin(a)
    corner = abs(math.cos(a)) ** 3
    smear_blob(x, z, 0.016 + 0.01 * corner, 1.5, 1.0, math.degrees(a))
for (x, z, s, t) in ((0.105, 0.012, 0.022, -25), (0.125, 0.026, 0.014, -35), (-0.1, -0.012, 0.02, 30), (0.0, -0.048, 0.022, 0), (0.03, -0.055, 0.016, 15)):
    smear_blob(x, z, s, 1.8, 0.8, t)          # streak toward his cheek, a dab on the chin
D_EZ0 = doug['ez']
doug['mouth'].location.y = -0.326

# ============================================================ RIGS
exec(open(os.path.join(HERE, '..', 'ep12', 'rig.py')).read())
doug_r = Rig(doug, 'doug', M['doug'], M['doug'], lift=0.17)
green_r = Rig(green, 'ricky', G_['ricky'], G_['track'], lift=0.17)
doug_r.setup_bend(['doug_body'], (doug['zc'] + 0.15) - 0.25)
G_ROOT = V(0.12, 0.05, 0); G_HEAD = -22           # on the couch, turned a little toward Doug (box hidden at his right hip)
D_POS = V(-0.88, -1.30, 0)
D_START = V(-2.05, -1.62, 0)                      # walks in from screen-left
G_FACE0 = G_ROOT + V(0, 0, green_r.base + green_r.ez) + V(-0.08, -0.25, 0)
D_HEAD = math.degrees(math.atan2((G_FACE0 - D_POS).x, -(G_FACE0 - D_POS).y))
D_EZ, G_EZ = doug_r.ez, green_r.ez
G_MOUTH_L = V(0, -0.285, G_MOUTH_Z - 0.25)        # Green's mouth in his upper-body space
STAND = {'N': ((-0.15, 0.0, 0), (0, -1, 0.2)), 'P': ((0.15, 0.0, 0), (0, -1, 0.2))}
DOWN = {'N': ((-0.37, -0.03, 0.06), ('auto', (-1, 0.3, 0))), 'P': ((0.37, -0.03, 0.06), ('auto', (1, 0.3, 0)))}
swing_d = lambda f, ph: {'N': ((-0.37, 0.12 * math.sin(ph), 0.07), ('auto', (-1, 0.3, 0))), 'P': ((0.37, -0.12 * math.sin(ph), 0.07), ('auto', (1, 0.3, 0)))}
G_PLATE_H = V(-0.06, -0.40, 0.16)                 # Green's left hand under the plate (upper-local)
PLATE_L = V(-0.04, -0.455, 0.19)                  # plate centre (upper-local)
SLICE_TOP = PLATE_L + V(0.02, 0.0, 0.08)
KNEE_L = {'N': V(-0.13, -0.40, SEAT + 0.07), 'P': V(0.13, -0.40, SEAT + 0.07)}
FOOT_L = {'N': V(-0.15, -0.44, 0.02), 'P': V(0.15, -0.44, 0.02)}
def ease_tab(keys, f):
    """keys [(frame, value or tuple)], smoothstep between keys"""
    if f <= keys[0][0]: return keys[0][1]
    if f >= keys[-1][0]: return keys[-1][1]
    for (fa, va), (fb, vb) in zip(keys, keys[1:]):
        if fa <= f <= fb:
            t = smooth((f - fa) / max(1, fb - fa))
            if isinstance(va, (tuple, list, Vector)): return tuple(a + (b - a) * t for a, b in zip(va, vb))
            return va + (vb - va) * t

# ============================================================ PROPS: plate + slice, fork + bite, the cake box
def prism(name, pts2d, z0, z1, m, parent=None, bevel=0.003):
    """vertical prism from a 2D outline (x, y) between heights z0..z1"""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in pts2d]; hi = [bm.verts.new((x, y, z1)) for x, y in pts2d]
    bm.faces.new(lo[::-1]); bm.faces.new(hi)
    n = len(pts2d)
    for i in range(n): bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me)); o.data.materials.append(m)
    if bevel:
        b = o.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = 2
    if parent: o.parent = parent
    return o
def wedge_pts(r, ang, n=10):
    pts = [(0.0, 0.0)]
    for i in range(n + 1):
        a = -ang / 2 + ang * i / n; pts.append((r * math.sin(a), r * math.cos(a)))
    return pts
def cake_slice(name, r, ang, parent):
    """chocolate layer cake slice: sponge / cream / sponge / frosting top; tip at origin, crust toward +Y"""
    p = wedge_pts(r, ang)
    prism(name + '_s1', p, 0.0, 0.026, SPONGE, parent)
    prism(name + '_cr', [(x * 0.99, y * 0.99) for x, y in p], 0.026, 0.034, CREAM, parent)
    prism(name + '_s2', p, 0.034, 0.06, SPONGE, parent)
    prism(name + '_fr', [(x * 1.02, y * 1.02) for x, y in p], 0.06, 0.071, FROST, parent, 0.004)
    prism(name + '_bk', [(x * 1.02, y * 1.02 + 0.004) for x, y in wedge_pts(r, ang)[1:]] + [(0, r * 0.93)], 0.0, 0.071, FROST, parent, 0.0)
PLATE_M = mat('plate', hexc('#f2efe8'), 0.2, 0.6)
STEEL = mat('steel', hexc('#dfe2e6'), 0.15, 0.3)
plate = empty('plate_e', tuple(PLATE_L), green_r.upper)
cyl('plate', 0.12, 0.012, (0, 0, 0), PLATE_M, parent=plate, verts=64)
cyl('plate_rim', 0.125, 0.006, (0, 0, 0.006), PLATE_M, parent=plate, verts=64).scale = (1, 1, 1)
sl = empty('slice', (0.03, 0.05, 0.007), plate); sl.rotation_euler = (0, 0, D(200))
cake_slice('slice', 0.10, D(42), sl)
# fork in the right fist (posed per frame below), with a bite on the tines
fork = empty('fork', (0, 0, 0), green_r.upper)
fork.rotation_mode = 'QUATERNION'
fork.scale = (1.5, 1.5, 1.5)
cyl('fork_handle', 0.007, 0.17, (0, 0, 0.05), STEEL, parent=fork, verts=16)
box('fork_neck', (0.024, 0.004, 0.03), (0, 0, 0.15), STEEL, 0.001, fork)
for tx in (-0.009, 0.0, 0.009): box('fork_tine', (0.0035, 0.0035, 0.045), (tx, 0, 0.185), STEEL, 0.001, fork)
bite = empty('bite', (0, -0.012, 0.178), fork); bite.rotation_euler = (D(-90), 0, D(15))
cake_slice('bite', 0.045, D(50), bite)
# the box: white bakery box, lid shut, DOUG in marker on the front. Green has shoved it behind his right hip on the couch:
# hidden from Doug's side, but the label pokes out toward the camera, so the audience can see he is lying.
BOX_W = mat('cakebox', hexc('#f4f1ea'), 0.8)
BOX_IN = mat('cakebox_in', hexc('#e7dfd0'), 0.85)
INK = mat('marker', hexc('#1b1f3a'), 0.6)
cb = empty('cakebox', (0.43, 0.2, SEAT + 0.012)); cb.rotation_euler = (D(-10), D(4), D(34))
BW_, BD_, BH_ = 0.34, 0.30, 0.11
box('cb_bottom', (BW_, BD_, 0.006), (0, 0, 0.003), BOX_IN, 0, cb)
box('cb_front', (BW_, 0.006, BH_), (0, -BD_ / 2, BH_ / 2), BOX_W, 0, cb)
box('cb_back', (BW_, 0.006, BH_), (0, BD_ / 2, BH_ / 2), BOX_W, 0, cb)
for sx in (-1, 1): box('cb_side', (0.006, BD_, BH_), (sx * BW_ / 2, 0, BH_ / 2), BOX_W, 0, cb)
hinge = empty('cb_hinge', (0, BD_ / 2, BH_), cb); hinge.rotation_euler = (D(-7), 0, 0)      # lid slammed shut in a hurry, not quite closed
box('cb_lid', (BW_ + 0.01, BD_ + 0.01, 0.006), (0, BD_ / 2, 0), BOX_W, 0, hinge)
mk = bpy.data.fonts.load(os.path.join(HERE, '..', 'ep12', 'marker.ttf'))
name_t = text('DOUG', 0.105, (0, -BD_ / 2 - 0.004, BH_ / 2 + 0.002), INK, rot=(D(90), 0, 0), extrude=0.0005, parent=cb)
name_t.data.font = mk; name_t.rotation_euler = (D(90), D(-3), 0)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -BD_ / 2 - 0.0042, BH_ / 2 - 0.045))
ul = bpy.context.active_object; ul.name = 'underline'; ul.scale = (0.2, 0.005, 1); ul.rotation_euler = (D(90), 0, D(0)); ul.data.materials.append(INK); ul.parent = cb
lf = empty('leftover', (-0.08, 0.04, 0.006), cb); lf.rotation_euler = (0, 0, D(130))
cake_slice('leftover', 0.075, D(14), lf)
import random as _rnd; _rnd.seed(4)
for i in range(9):          # crumbs + frosting streaks where the cake used to be
    x, y = _rnd.uniform(-0.13, 0.12), _rnd.uniform(-0.11, 0.11)
    sphere('crumb', _rnd.uniform(0.006, 0.011), SPONGE if i % 2 else FROST, (x, y, 0.01), (1, 1, 0.6), parent=cb)
sphere('streak', 0.04, FROST, (0.05, -0.02, 0.006), (1.6, 0.6, 0.06), parent=cb)
sphere('lid_smudge', 0.03, SMEAR, (0.1, -BD_ / 2 - 0.004, BH_ - 0.012), (1.4, 0.12, 0.5), parent=cb)   # frosting thumbprint on the box
for i in range(8):          # crumb trail on the coffee table, where the box used to be
    x, y = _rnd.uniform(-0.25, 0.25), _rnd.uniform(-0.12, 0.15)
    sphere('tcrumb', _rnd.uniform(0.007, 0.012), SPONGE if i % 2 else FROST, (TABLE.x + x, TABLE.y + y, TABLE.z + 0.004), (1, 1, 0.6))
sphere('ring', 0.13, SMEAR, (TABLE.x - 0.1, TABLE.y + 0.02, TABLE.z + 0.001), (0.9, 0.6, 0.012))   # frosting mark left by the box

# ============================================================ BEATS
SH = {k: tuple(v) for k, v in BT['SHOTS'].items()}
WALK0, WALK1 = BT['WALK']
F_NOTICE, F_FREEZE = BT['G_NOTICE'], BT['G_FREEZE']
F_HES1, F_HES2 = BT['G_HES1'], BT['G_HES2']
F_TO_FORK = BT['D_TO_FORK']; F_SEE = BT['G_SEE_STARE']; LOW0, LOW1 = BT['G_LOWER']
F_TO_BOX, F_BACK, F_TO_MOUTH = BT['D_TO_BOX'], BT['D_BACK'], BT['D_TO_MOUTH']
CR0, CR1 = BT['CRUMB']; F_GDOWN, F_DDOWN = BT['G_LOOKDOWN'], BT['D_LOOKDOWN']; UP0, UP1 = BT['G_LOOKUP']
L = {k: v for k, v in TM.items() if isinstance(v, dict)}

# ============================================================ DOUG: walks in, stops, then stands perfectly still (breathing only)
doug_r.walk(WALK0, WALK1, (D_START.x, D_START.y), (D_POS.x, D_POS.y), math.degrees(math.atan2(D_POS.x - D_START.x, -(D_POS.y - D_START.y))),
            steps=3.0, arms=swing_d, lean=4, bob=0.03, sway=4)
WALK_HEAD = math.degrees(math.atan2(D_POS.x - D_START.x, -(D_POS.y - D_START.y)))
D_ROT = [(WALK1, (2, 0, 0)), (WALK1 + 6, (0, 0, 0)), (F_DDOWN - 2, (0, 0, 0)), (F_DDOWN + 6, (9, 0, 0)), (SH['H'][0] + 4, (9, 0, 0)),
         (SH['H'][0] + 14, (1, 0, 0)), (N, (1, 0, 0))]
for f in range(WALK1, N + 1):
    doug_r.place(f, (D_POS.x, D_POS.y), WALK_HEAD + (D_HEAD - WALK_HEAD) * smooth((f - WALK1) / 7))
    br = 0.004 * math.sin(2 * math.pi * f / 105)
    rot = ease_tab(D_ROT, f)
    doug_r.pose(f, up=(0, 0, -0.008 + br * 0.4), rot=rot, sq=1 + br, arms=DOWN, legs=STAND)

# ============================================================ GREEN: eating -> frozen -> lies with his whole chest
# fork states: (tip point, direction from hand to tip), upper-local
def nrm(*a): return V(*a).normalized()
FORK_LEN = 0.305
ST = dict(
    MOUTH=(G_MOUTH_L + V(0.0, -0.035, 0.0), nrm(-0.35, 0.5, 0.55)),
    PLATE=(SLICE_TOP + V(0, 0, 0.0), nrm(-0.25, 0.15, -0.9)),
    MID=(G_MOUTH_L + V(0.05, -0.2, -0.16), nrm(-0.3, 0.35, 0.85)),
    LOW=(V(0.12, -0.55, 0.36), nrm(0.05, -0.25, 1.0)),
)
FORK_KEYS = [(1, 'PLATE', 0.45), (6, 'MOUTH', 1), (13, 'PLATE', 1), (19, 'PLATE', 1), (F_NOTICE, 'MID', 0.75), (F_FREEZE, 'MID', 1),
             (LOW0, 'MID', 1), (LOW1, 'LOW', 1), (N, 'LOW', 1)]
def state_at(name, amt, prev):
    tp, dr = ST[name]
    if amt >= 1 or prev is None: return tp, dr
    pt, pd = prev; return pt.lerp(tp, amt), pd.slerp(dr, amt) if hasattr(pd, 'slerp') else (pd.lerp(dr, amt)).normalized()
_fk = []; prev = None
for fr_, nm, amt in FORK_KEYS:
    st = state_at(nm, amt, ST['PLATE'] if prev is None else prev); _fk.append((fr_, st)); prev = st
def fork_state(f):
    if f <= _fk[0][0]: return _fk[0][1]
    for (fa, (ta, da)), (fb, (tb, db)) in zip(_fk, _fk[1:]):
        if fa <= f <= fb:
            t = (f - fa) / max(1, fb - fa)
            if fb == F_NOTICE: t = t ** 0.8                               # rising normally ...
            elif fb == F_FREEZE: t = 1 - (1 - t) ** 3                     # ... and stopping dead
            else: t = smooth(t)
            return ta.lerp(tb, t), da.lerp(db, t).normalized()
    return _fk[-1][1]
def fork_hand(f):
    tip, d = fork_state(f); return tip - d * FORK_LEN, d
def fork_tip_local(f): return fork_state(f)[0]
G_ROT = [(1, (-3, 0, 0)), (F_NOTICE, (-3, 0, 0)), (F_FREEZE, (-4, 0, 0)),            # freeze: stiffens up
         (F_HES1, (-4, 0, 0)), (F_HES1 + 4, (-1, -2, 0)), (L['g1']['fs'] + 2, (-7, 2, 0)), (L['g1']['fe'] + 6, (-6, 1, 0)),   # hitch, then chin up: "What? No."
         (F_SEE, (-5, 0, 0)), (F_SEE + 8, (1, 0, 0)), (LOW1, (0, 0, 0)),          # looks down at his fork, lowers it
         (F_HES2, (1, -2, 0)), (L['g2']['fs'] + 2, (-6, 3, 0)), (L['g2']['fe'] + 8, (-5, 2, 0)),
         (L['g3']['fs'] - 2, (-5, 2, 0)), (L['g3']['fs'] + 8, (-6, -4, 0)), (L['g3']['fe'], (-6, -4, 0)),   # head tilt: "like that?"
         (CR0, (-5, -2, 0)), (F_GDOWN, (-4, 0, 0)), (F_GDOWN + 8, (12, 0, 0)), (UP0, (12, 0, 0)),          # looks down at it
         (UP1, (-3, 0, 0)), (N, (-3, 0, 0))]
G_UP = [(1, 0.0), (F_NOTICE, 0.0), (F_FREEZE, 0.012), (F_HES1, 0.012), (L['g1']['fe'] + 10, 0.004), (N, 0.004)]
for f in range(1, N + 1):
    green_r.place(f, (G_ROOT.x, G_ROOT.y), G_HEAD)
    br = 0.004 * math.sin(2 * math.pi * f / 95 + 1.3)
    hand, d = fork_hand(f)
    arms = {'N': (tuple(G_PLATE_H + V(0, 0, 0.004 * math.sin(f / 13))), ('auto', (-1, 0.2, -0.6))), 'P': (tuple(hand), ('auto', (1, 0.3, -0.7)))}
    green_r.pose(f, up=(0, 0, ease_tab(G_UP, f) + br * 0.4), rot=ease_tab(G_ROT, f), sq=1 + br, arms=arms,
                 legs={'N': (tuple(FOOT_L['N']), (0, -1, 0.9)), 'P': (tuple(FOOT_L['P']), (0, -1, 0.9))})
    for s_ in ('N', 'P'):                          # seated hip -> knee -> foot (ep14 v2)
        hip = V(0, 0, green_r.base) + green_r.hip_off[s_]
        green_r.key_points(green_r.leg[s_], f, (hip, KNEE_L[s_], FOOT_L[s_]))
        green_r.foot[s_].location = FOOT_L[s_] + V(0, -0.035, 0.03); green_r.foot[s_].keyframe_insert('location', frame=f)
    fork.location = hand; fork.rotation_quaternion = d.to_track_quat('Z', 'Y')
    fork.keyframe_insert('location', frame=f); fork.keyframe_insert('rotation_quaternion', frame=f)
# the bite: eaten at the first mouth contact, a new one stabbed off the slice (which gets a little smaller)
for f, vis in ((1, True), (6, False), (17, True)):
    for o in bite.children_recursive if hasattr(bite, 'children_recursive') else bite.children:
        o.hide_render = not vis; o.keyframe_insert('hide_render', frame=f)
sl.scale = (1, 1, 1); sl.keyframe_insert('scale', frame=1); sl.keyframe_insert('scale', frame=16)
sl.scale = (0.86, 0.86, 1); sl.keyframe_insert('scale', frame=18)

# ============================================================ THE CRUMB (falls out of his mouth onto his jacket)
crumb_e = empty('crumb_e', tuple(G_MOUTH_L + V(0, -0.012, -0.012)), green_r.upper)
cake_slice('crumb', 0.028, D(60), crumb_e)
crumb_e.rotation_euler = (D(70), D(20), 0)
LAND = V(0.025, -0.3, 0.40)                       # on the jacket front, chest height (sticks: it's frosting)
for f in range(1, N + 1):
    if f < CR0: p, s, r = G_MOUTH_L + V(0, -0.006, -0.014), 0.001, (D(70), D(20), 0)       # still in his mouth
    elif f <= CR1:
        t = (f - CR0) / (CR1 - CR0)
        p = (G_MOUTH_L + V(0, -0.02, -0.02)).lerp(LAND, t * t) + V(0, -0.03 * math.sin(math.pi * t), 0); s = 1.0
        r = (D(70 + 140 * t), D(20 + 60 * t), D(30 * t))
    else:
        k = f - CR1; p = LAND + V(0, 0, 0.012 * math.exp(-k / 2) * abs(math.sin(k * 1.6))); s = 1.0; r = (D(210), D(80), D(30))
    crumb_e.location = p; crumb_e.scale = (s, s, s); crumb_e.rotation_euler = r
    for pth in ('location', 'scale', 'rotation_euler'): crumb_e.keyframe_insert(pth, frame=f)

# ============================================================ FACES: gaze, saccades, blinks, lids, brows, mouths
import soundfile as _sf
_rng = random.Random(15) if 'random' in dir() else None
import random as _random; _rng = _random.Random(15)
def _mouth_tracks():
    tr = {'doug': {}, 'green': {}}
    for name, v in L.items():
        a, sr = _sf.read(os.path.join(VO, name + '.wav')); hop = sr // 30
        who = 'doug' if name.startswith('d') else 'green'
        rms, cen = [], []
        for i in range(0, len(a) - hop, hop):
            seg = a[i:i + 2 * hop] * np.hanning(len(a[i:i + 2 * hop]))
            S = np.abs(np.fft.rfft(seg)); fr_ = np.fft.rfftfreq(len(seg), 1 / sr)
            rms.append(np.sqrt(np.mean(a[i:i + hop] ** 2))); band = (fr_ > 300) & (fr_ < 4000)
            cen.append(float((S[band] * fr_[band]).sum() / (S[band].sum() + 1e-9)))
        rms = np.array(rms) / (max(rms) + 1e-9); o_prev = 0.0
        for i, (r_, c_) in enumerate(zip(rms, cen)):
            o = max(0.0, min(1.0, (r_ - 0.06) / 0.5))
            o = o if o > o_prev else o_prev * 0.55 + o * 0.45; o_prev = o
            w = max(0.0, min(1.0, (c_ - 1100) / 1300)) if o > 0.08 else 0.5
            tr[who][v['f'] + i] = (o, w)
    return tr
MTR = _mouth_tracks()
def mtrack(who, f): return MTR[who].get(f, (0.0, 0.5))
def chew(f):                       # Green chewing the first bite until he notices Doug
    if 7 <= f < F_NOTICE: return 0.28 * abs(math.sin(math.pi * (f - 7) / 6))
    return 0.0
D_LIDS = [o for o in bpy.data.objects if o.name.startswith('doug_lid')]
G_LIDS = [o for o in bpy.data.objects if o.name.startswith('ricky_lid')]
def lids_set(objs, f, deg):
    for o in objs: o.rotation_euler = (D(deg), 0, 0); o.keyframe_insert('rotation_euler', frame=f)
G_BZ = [b.location.z for b in green['brows']]
def g_brows(f, dz, tilt):
    for i, bp in enumerate(green['brows']):
        sx = -1 if i == 0 else 1
        bp.location = (bp.location.x, bp.location.y, G_BZ[i] + dz); bp.keyframe_insert('location', frame=f)
        bp.rotation_euler = (0, sx * D(-6 + tilt), 0); bp.keyframe_insert('rotation_euler', frame=f)
def blink_amt(f, blinks):
    for b_, dur in blinks:
        if abs(f - b_) <= dur: return 1 - abs(f - b_) / (dur + 1)
    return 0.0
# Doug: deadpan lids the whole time, a touch heavier once he has seen the frosting; one slow blink in the final stare
D_LID = [(1, 23), (F_TO_MOUTH, 23), (F_TO_MOUTH + 8, 27), (SH['I'][0], 27), (SH['I'][0] + 10, 29), (N, 29)]
D_BLINKS = [(WALK1 + 4, 3), (F_BACK - 3, 2), (SH['E'][0] + 30, 3), (F_DDOWN - 6, 2), (SH['I'][0] + 24, 5)]
# Green: relaxed while eating (30), caught (-34), confident between lies (8), hitch before each lie (-28)
G_LID = [(1, 30), (F_NOTICE, 30), (F_NOTICE + 3, -34), (F_HES1, -30), (F_HES1 + 3, -28), (L['g1']['fs'] + 2, 6), (L['g1']['fe'] + 8, 8),
         (F_SEE, 8), (F_SEE + 4, -18), (LOW1, -10), (F_HES2, -24), (L['g2']['fs'] + 3, 6), (L['g2']['fe'] + 10, 8),
         (L['g3']['fs'], 4), (L['g3']['fe'], 4), (CR0 + 2, 6), (CR0 + 6, -30), (UP0, -26), (UP1, 14), (N, 14)]
G_BLINKS = [(F_HES1 + 2, 2), (L['g1']['fe'] + 2, 2), (F_HES2 + 2, 2), (L['g2']['fe'] + 6, 2), (L['g3']['fe'] + 4, 2), (UP1 + 4, 3)]
G_BROW = [(1, (0, 0)), (F_NOTICE, (0, 0)), (F_NOTICE + 3, (0.03, -6)), (L['g1']['fs'], (0.02, 4)), (L['g1']['fe'] + 6, (0.01, 0)),
          (L['g2']['fs'], (0.025, 6)), (L['g2']['fe'] + 6, (0.01, 0)), (L['g3']['fs'], (-0.005, 10)), (L['g3']['fe'], (-0.005, 10)),
          (CR0 + 4, (0.03, -4)), (UP1, (0.0, 2)), (N, (0.0, 2))]
SAC = {}
def saccade(who, f, amp=1.0):
    k = (who, f // 11)
    if k not in SAC: SAC[k] = V(_rng.uniform(-0.03, 0.03), 0, _rng.uniform(-0.02, 0.02))
    return SAC[k] * amp
def aim(pivot, Tp, clamp_yaw=40, clamp_pitch=48):
    P = pivot.matrix_world.translation; Rp = pivot.parent.matrix_world.to_3x3().normalized()
    d = Rp.inverted() @ (Tp - P)
    yaw = math.degrees(math.atan2(d.x, -d.y)); pitch_ = -math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    yaw = max(-clamp_yaw, min(clamp_yaw, yaw)); pitch_ = max(-clamp_pitch, min(clamp_pitch, pitch_))
    pivot.rotation_euler = (D(pitch_), 0, D(yaw)); pivot.keyframe_insert('rotation_euler', frame=scene.frame_current)
def g_up(): return green_r.upper.matrix_world
def d_face(): return doug_r.upper.matrix_world @ V(0, -0.25, D_EZ - 0.04)
def g_face(): return g_up() @ V(0, -0.24, G_EZ - 0.03)
def g_mouth(): return g_up() @ (G_MOUTH_L + V(0, -0.02, 0))
def g_fork(): return fork.matrix_world @ V(0, -0.012, 0.18)
def box_pt(): return cb.matrix_world @ V(0, -BD_ / 2, BH_ / 2)
def crumb_pt(): return crumb_e.matrix_world.translation.copy()
def blend(keys, f):
    """keys [(frame, fn)] -> point; 4-frame eye moves between targets (eyes jump, they don't drift)"""
    cur = keys[0][1]()
    for i, (fk, fn) in enumerate(keys):
        if f >= fk:
            prev = keys[i - 1][1]() if i else fn(); t = smooth((f - fk) / 4.0); cur = prev.lerp(fn(), t)
    return cur
def ahead_d(): return doug_r.upper.matrix_world @ V(0, -2.0, D_EZ - 0.15)
D_GAZE = [(1, ahead_d), (WALK1 - 6, g_face), (F_TO_FORK, g_fork), (LOW1 + 4, g_face), (F_TO_BOX, box_pt), (F_BACK, g_face), (F_TO_MOUTH, g_mouth),
          (CR0 + 2, crumb_pt), (SH['H'][0] + 10, g_face), (N, g_face)]
G_GAZE = [(1, g_fork), (F_NOTICE, d_face), (F_HES1, lambda: d_face() + V(0.25, 0.1, -0.35)), (F_HES1 + 6, d_face),
          (F_SEE, g_fork), (LOW1 - 6, d_face), (F_HES2, lambda: d_face() + V(-0.3, 0.2, -0.3)), (F_HES2 + 6, d_face),
          (F_GDOWN, crumb_pt), (UP0 + 6, d_face), (N, d_face)]
for f in range(1, N + 1):
    scene.frame_set(f)
    # Doug
    lv = ease_tab(D_LID, f); lids_set(D_LIDS, f, lv + (95 - lv) * blink_amt(f, D_BLINKS))
    still = SH['I'][0] <= f or SH['D'][0] <= f < SH['E'][0]
    tgt = blend(D_GAZE, f) + saccade('d', f, 0.15 if still else 0.5)
    for pv in doug['eyes']: aim(pv, tgt)
    o, w = mtrack('doug', f); m = doug['mouth']
    m.scale = (1 + 2.3 * o, 1, (1 + 0.15 * o) * (0.82 + 0.36 * w)); m.keyframe_insert('scale', frame=f)
    # Green
    lv = ease_tab(G_LID, f); o, w = mtrack('green', f)
    lids_set(G_LIDS, f, lv + (95 - lv) * blink_amt(f, G_BLINKS) - 6 * o)
    dz, tl = ease_tab(G_BROW, f); g_brows(f, dz + 0.008 * o, tl)
    tgt = blend(G_GAZE, f) + saccade('g', f, 0.6)
    for pv in green['eyes']: aim(pv, tgt)
    o = max(o, chew(f)); m = green['mouth']
    m.scale = (1.3 * (1 + 0.2 * o) * (0.8 + 0.45 * w), 0.5, 0.5 * (1 + 2.3 * o) * (1.1 - 0.3 * w)); m.keyframe_insert('scale', frame=f)

# ============================================================ CAMERAS
scene.frame_set(SH['B'][0]); bpy.context.view_layer.update()
DF = d_face(); GF = g_face(); GM = g_mouth()
def rotz(v, deg):
    c, s = math.cos(D(deg)), math.sin(D(deg)); return V(v.x * c - v.y * s, v.x * s + v.y * c, v.z)
dDG = (GF - DF); dDG.z = 0; dDG.normalize()
WIDE = (V(2.15, -2.02, 1.12), V(-0.4, -0.5, 0.9), 22, 8.0, V(-0.3, -0.6, 0.9))
def d_cu(dist, lens):          # on Doug, from just beside Green's eyeline (screen-right of it)
    return (DF + rotz(dDG, 24) * dist + V(0, 0, -0.07), DF + V(0, 0, -0.03), lens, 4.0, DF)
def g_cu(dist, lens, dz=0.0):  # on Green, from just beside Doug's eyeline
    return (GF + rotz(-dDG, -22) * dist + V(0, 0, 0.04 + dz), GF + V(0, 0, -0.06 + dz), lens, 4.0, GF)
def cam_for(f):
    """-> (location, target, lens, fstop, focus)"""
    if f <= SH['A'][1]:
        t = (f - 1) / (SH['A'][1] - 1); p, tg, ln, fs, fp = WIDE
        return p + V(-0.04, 0.05, 0) * smooth(t), tg, ln + 0.6 * smooth(t), fs, fp
    if f <= SH['B'][1]:
        t = (f - SH['B'][0]) / (SH['B'][1] - SH['B'][0]); a = d_cu(1.35, 26); return a[0] + rotz(dDG, 24) * (-0.04 * t), *a[1:]
    if f <= SH['C'][1]:        # Green medium: face, fork, plate and the box at his hip all in frame
        t = smooth((f - SH['C'][0]) / (SH['C'][1] - SH['C'][0]))
        p = GF + rotz(-dDG, 28) * 1.6 + V(0, 0, -0.1); tg = GF + V(0.16, 0.05, -0.33)
        return p + rotz(-dDG, 28) * (-0.08 * t), tg, 30, 5.6, GF + V(0, 0, -0.2)
    if f <= SH['D'][1]: return d_cu(1.3, 27)
    if f <= SH['E'][1]: return g_cu(1.2, 27, -0.06)
    if f <= SH['F'][1]:        # slow push-in on his face (mouth + chest stay in frame for the crumb)
        t = smooth((f - SH['F'][0]) / (SH['F'][1] - SH['F'][0]))
        a = g_cu(1.2, 27, -0.06); b = g_cu(0.95, 27, -0.12)
        return a[0].lerp(b[0], t), a[1].lerp(b[1], t), 27, 4.0, GM
    if f <= SH['G'][1]: return WIDE[0] + V(-0.04, 0.05, 0), WIDE[1], WIDE[2] + 0.6, WIDE[3], WIDE[4]
    if f <= SH['H'][1]: return g_cu(1.15, 27, -0.06)
    t = (f - SH['I'][0]) / max(1, SH['I'][1] - SH['I'][0]); a = d_cu(1.3, 28)
    return a[0] + rotz(dDG, 24) * (-0.05 * t), *a[1:]
def cam_setup(name):
    a_, b_ = SH[name]
    for f in range(a_, b_ + 1):
        p, tgt, lens, fs, fp = cam_for(f)
        key(cam, 'location', f, p); key(target, 'location', f, tgt); key(focus, 'location', f, fp)
        key(cam_data, 'lens', f, lens); key(cam_data.dof, 'aperture_fstop', f, fs)
cam_data.clip_start = 0.02
if SHOT == 'QA':
    print('D_HEAD', round(D_HEAD, 1), 'DF', tuple(round(x, 3) for x in DF), 'GF', tuple(round(x, 3) for x in GF))
    for f in (1, 6, F_NOTICE, F_FREEZE, LOW1, CR0, CR1, N):
        scene.frame_set(f); print('f', f, 'fork tip', tuple(round(x, 3) for x in g_fork()), 'crumb', tuple(round(x, 3) for x in crumb_pt()))
    sys.exit(0)
if SHOT == 'TEST':
    p, tgt, lens, fs, fp = WIDE; key(cam, 'location', 1, p); key(target, 'location', 1, tgt); key(focus, 'location', 1, fp)
    key(cam_data, 'lens', 1, lens); key(cam_data.dof, 'aperture_fstop', 1, fs)
    render(N)
else:
    cam_setup(SHOT); f0, f1 = SH[SHOT]; scene.frame_set(f0)
    FR = FR or f'{f0}-{f1}'
    render(N)
