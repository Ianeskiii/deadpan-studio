"""Tube Town - When Someone Is Lying Straight to Your Face.  Doug + Green (Ricky's model) + the cake.
usage: cd ep15 && python3 build.py SHOT OUTDIR [--still F] [--samples N] [--pct P] [--engine cycles]
  SHOT = TEST  (style test frame: wide establishing two-shot, Green frozen mid-bite, cake box on the table)
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
from mathutils import Matrix
def V(*a): return Vector(a)
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
N = 30
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
SMEAR = mat('smear', hexc('#4f2c1c'), 0.45, 0.2)
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

# ============================================================ RIGS + POSES
exec(open(os.path.join(HERE, '..', 'ep12', 'rig.py')).read())
doug_r = Rig(doug, 'doug', M['doug'], M['doug'], lift=0.17)
green_r = Rig(green, 'ricky', G_['ricky'], G_['track'], lift=0.17)
doug_r.setup_bend(['doug_body'], (doug['zc'] + 0.15) - 0.25)
G_ROOT = V(0.12, 0.05, 0); G_HEAD = -22           # on the couch, turned a little toward Doug (box hidden at his right hip)
D_POS = V(-0.88, -1.30, 0)
G_FACE = G_ROOT + V(0, 0, green_r.base + green_r.ez) + V(-0.08, -0.25, 0)
D_HEAD = math.degrees(math.atan2((G_FACE - D_POS).x, -(G_FACE - D_POS).y))
doug_r.place(1, (D_POS.x, D_POS.y), D_HEAD)
green_r.place(1, (G_ROOT.x, G_ROOT.y), G_HEAD)
STAND = {'N': ((-0.15, 0.0, 0), (0, -1, 0.2)), 'P': ((0.15, 0.0, 0), (0, -1, 0.2))}
DOWN = {'N': ((-0.37, -0.03, 0.06), ('auto', (-1, 0.3, 0))), 'P': ((0.37, -0.03, 0.06), ('auto', (1, 0.3, 0)))}
# Green: plate on his lap in the left hand, fork frozen half way to his mouth in the right
G_PLATE_H = V(-0.06, -0.40, 0.16)                  # upper-local hand positions
G_FORK_H = V(0.2, -0.46, 0.34)
G_ARMS = {'N': (tuple(G_PLATE_H), ('auto', (-1, 0.2, -0.6))), 'P': (tuple(G_FORK_H), ('auto', (1, 0.3, -0.7)))}
KNEE_L = {'N': V(-0.13, -0.40, SEAT + 0.07), 'P': V(0.13, -0.40, SEAT + 0.07)}
FOOT_L = {'N': V(-0.15, -0.44, 0.02), 'P': V(0.15, -0.44, 0.02)}
for f in (1, N):
    doug_r.pose(f, up=(0, 0, -0.008), rot=(2, 0, 0), arms=DOWN, legs=STAND)
    green_r.pose(f, up=(0, 0, 0), rot=(-3, 0, 0), arms=G_ARMS, legs={'N': (tuple(FOOT_L['N']), (0, -1, 0.9)), 'P': (tuple(FOOT_L['P']), (0, -1, 0.9))})
    for s_ in ('N', 'P'):                          # seated hip -> knee -> foot (ep14 v2)
        hip = V(0, 0, green_r.base) + green_r.hip_off[s_]
        green_r.key_points(green_r.leg[s_], f, (hip, KNEE_L[s_], FOOT_L[s_]))
        green_r.foot[s_].location = FOOT_L[s_] + V(0, -0.035, 0.03); green_r.foot[s_].keyframe_insert('location', frame=f)
scene.frame_set(1); bpy.context.view_layer.update()

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
hp = green_r.hand['N'].matrix_world.translation.copy()
plate = empty('plate_e', hp + V(0.02, -0.06, 0.035))
plate.rotation_euler = (0, 0, D(G_HEAD))
cyl('plate', 0.12, 0.012, (0, 0, 0), PLATE_M, parent=plate, verts=64)
cyl('plate_rim', 0.125, 0.006, (0, 0, 0.006), PLATE_M, parent=plate, verts=64).scale = (1, 1, 1)
sl = empty('slice', (0.03, 0.05, 0.007), plate); sl.rotation_euler = (0, 0, D(200))
cake_slice('slice', 0.10, D(42), sl)
# fork in the right fist, tines up toward his mouth, with the bite he has not eaten (yet)
fh = green_r.hand['P'].matrix_world.translation.copy()
mouth_w = green['mouth'].matrix_world.translation.copy()
fork = empty('fork', fh)
fork.rotation_mode = 'QUATERNION'
fdir = (mouth_w + V(0.12, -0.3, 0.05) - fh).normalized()
fork.rotation_quaternion = fdir.to_track_quat('Z', 'Y')
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

# ============================================================ EYES + LIDS
def aim_eyes(C, T_, f):
    for pv in C['eyes']:
        P = pv.matrix_world.translation; Rp = pv.parent.matrix_world.to_3x3().normalized()
        d = Rp.inverted() @ (V(*T_) - P)
        yaw = math.degrees(math.atan2(d.x, -d.y)); pitch_ = -math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
        yaw = max(-40, min(40, yaw)); pitch_ = max(-36, min(52, pitch_))
        pv.rotation_euler = (D(pitch_), 0, D(yaw)); pv.keyframe_insert('rotation_euler', frame=f)
def lids(prefix, deg, f):
    for o in bpy.data.objects:
        if o.name.startswith(prefix): o.rotation_euler = (D(deg), 0, 0); o.keyframe_insert('rotation_euler', frame=f)
scene.frame_set(1); bpy.context.view_layer.update()
DEYE = sum((e.matrix_world.translation for e in doug['eyes']), Vector()) / 2
GEYE = sum((e.matrix_world.translation for e in green['eyes']), Vector()) / 2
for f in (1, N):
    aim_eyes(doug, GEYE + V(0, 0, -0.03), f)      # Doug: on Green
    aim_eyes(green, DEYE, f)                      # Green: frozen, eyes on Doug
    lids('doug_lid', 23, f)                       # Doug's deadpan
    lids('ricky_lid', -32, f)                     # Green: caught mid-bite, eyes open wide (his usual is 30)

# ============================================================ CAMERA
SHOTS = dict(
    TEST=(V(2.1, -2.0, 1.12), V(-0.24, -0.45, 0.9), 24, 8.0, V(-0.2, -0.6, 0.9)),   # wide two-shot: both, the hidden box beside Green
)
if SHOT == 'QA':
    print('D_HEAD', round(D_HEAD, 1), 'DEYE', tuple(round(x, 3) for x in DEYE), 'GEYE', tuple(round(x, 3) for x in GEYE))
    sys.exit(0)
p, tgt, lens, fs, fp = SHOTS[SHOT]
cam.location = p; target.location = tgt; focus.location = fp; cam_data.lens = lens; cam_data.dof.aperture_fstop = fs
cam_data.clip_start = 0.02
render(N)
