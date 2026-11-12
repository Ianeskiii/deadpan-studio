"""Tube Town ep20 - "Me while watching Jeolee before going to sleep".
One continuous shot, 300 frames (10.0 s @ 30 fps). Doug lies on his side in bed at 2 AM, no hat,
watching his phone; sleepy -> interested -> small smile -> kilig -> big happy smile.
usage: cd ep20 && python3 build.py S OUTDIR [--still F] [--samples N] [--pct P] [--engine cycles] [--step K]
Beats are in BEATS below (frames)."""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
from mathutils import Matrix
V = Vector
N = 300
BEATS = json.load(open(os.path.join(HERE, 'beats.json')))
B = BEATS['frames']

# ============================================================ BEDROOM AT 2 AM (set from ep10, relit for night)
R_ = dict(
    floor=brick_mat('planks', hexc('#8a5a3c'), hexc('#7c5034'), hexc('#4f3322'), 1.2, 0.9, 0.12, 0.5, 0.55),
    wall=mat('bwall', hexc('#55658a'), 0.85),
    wood=mat('bedwood', hexc('#a8714a'), 0.45, 0.2),
    sheet=mat('sheet', hexc('#f2f1ee'), 0.8),
    pillow=mat('pillow', hexc('#fbfbfb'), 0.85, 0, sheen=0.5),
    blinds=mat('blinds', hexc('#e9e4da'), 0.6),
    night=mat('nightglass', (0, 0, 0), 0.5, 0, hexc('#5f7fc4'), 0.35),
    clock=mat('clockbody', hexc('#1b1b1f'), 0.25, 0.6),
    seg=mat('redseg', (0, 0, 0), 0.4, 0, hexc('#ff3b2f'), 6),
    segoff=mat('redsegoff', hexc('#0c0303'), 0.95),
    frame=mat('frame', hexc('#e8e2d6'), 0.6),
    art=mat('art2', hexc('#f2a65a'), 0.7),
    lampshade=mat('shade', hexc('#f3e3c3'), 0.8),
    screen=mat('pscreen', (0, 0, 0), 0.3, 0, hexc('#fff1dc'), 2.2),
)
def quilt_mat():
    m = bpy.data.materials.new('quilt'); m.use_nodes = True
    n = m.node_tree.nodes; l = m.node_tree.links; b = n['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.9; b.inputs['Sheen Weight'].default_value = 0.6
    tc = n.new('ShaderNodeTexCoord'); ck = n.new('ShaderNodeTexChecker'); ck.inputs['Scale'].default_value = 7
    ck.inputs['Color1'].default_value = (*hexc('#3d7fb8'), 1); ck.inputs['Color2'].default_value = (*hexc('#2f6a9c'), 1)
    l.new(tc.outputs['Generated'], ck.inputs['Vector']); l.new(ck.outputs['Color'], b.inputs['Base Color'])
    return m
QUILT = quilt_mat()

box('floor', (8, 8, 0.1), (0, 1.0, -0.05), R_['floor'])
box('backwall', (8, 0.1, 4), (0, 2.25, 2), R_['wall'])
box('sidewall', (0.1, 8, 4), (-2.0, 1.0, 2), R_['wall'])
box('bedframe', (1.36, 2.2, 0.3), (0, 1.05, 0.2), R_['wood'], 0.03)
box('mattress', (1.24, 2.05, 0.22), (0, 1.05, 0.44), R_['sheet'], 0.06)
box('headboard', (1.4, 0.08, 1.05), (0, 2.18, 0.6), R_['wood'], 0.03)
pillow = sphere('pillow', 1.0, R_['pillow'], (0.0, 1.86, 0.66), (0.5, 0.3, 0.13))
MATT = 0.55
# nightstand + clock (2:07)
NX, NY = 0.98, 1.72
box('nightstand', (0.5, 0.42, 0.56), (NX, NY, 0.28), R_['wood'], 0.02)
box('drawer_line', (0.44, 0.005, 0.01), (NX, NY - 0.212, 0.36), R_['clock'])
CX, CY, CZ = NX - 0.06, NY - 0.06, 0.56
clock = empty('clock', (CX, CY, CZ)); clock.rotation_euler = (0, 0, D(-35))
box('clock_body', (0.27, 0.11, 0.13), (0, 0, 0.065), R_['clock'], 0.02, clock)
box('clock_face', (0.235, 0.004, 0.09), (0, -0.056, 0.07), mat('cface', hexc('#0b0606'), 0.2, 0.8), 0, clock)
SEG = {'a': (0, 1), 'b': (1, .5), 'c': (1, -.5), 'd': (0, -1), 'e': (-1, -.5), 'f': (-1, .5), 'g': (0, 0)}
DIG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc',
       '8': 'abcdefg', '9': 'abcdfg'}
dw, dh, th = 0.016, 0.026, 0.0065
for x0_, ch in zip((-0.068, -0.002, 0.052), '207'):
    for sname, (sx, sz) in SEG.items():
        horiz = sname in 'adg'
        dims = (dw * 2 - th, 0.003, th) if horiz else (th, 0.003, dh - th)
        loc = (x0_ + sx * dw, -0.0595, 0.078 + sz * dh)
        box('seg' if sname in DIG[ch] else 'segoff', dims, loc, R_['seg'] if sname in DIG[ch] else R_['segoff'], 0, clock)
for z in (0.066, 0.09): box('colon', (th, 0.003, th), (-0.035, -0.0595, z), R_['seg'], 0, clock)
box('artframe', (0.62, 0.04, 0.46), (1.3, 2.19, 1.75), R_['frame'], 0.01)
box('art', (0.54, 0.02, 0.38), (1.3, 2.17, 1.75), R_['art'])
WX = -0.95
box('win_frame', (0.95, 0.06, 1.05), (WX, 2.2, 1.75), R_['frame'], 0.01)
box('win_glow', (0.85, 0.02, 0.95), (WX, 2.24, 1.75), R_['night'])
for k in range(14):
    b_ = box('slat', (0.86, 0.012, 0.052), (WX, 2.15, 1.3 + k * 0.066), R_['blinds'], 0.002); b_.rotation_euler = (D(12), 0, 0)
# night light: cool moon through the blinds, dim blue fill, faint cool rim; the phone is the key on Doug's face
area('moon', (WX + 0.2, 2.7, 2.2), (D(-50), D(-10), D(10)), 55, hexc('#7f9fe0'), (0.9, 0.9))
area('fill', (1.8, 0.4, 2.4), (D(50), 0, D(70)), 22, hexc('#6f86c8'), (2, 2))
area('rim', (-1.4, 0.9, 2.0), (D(35), D(-55), 0), 7, hexc('#8fa8ff'), (1, 1))
world(hexc('#18223a'), 0.9)
hf = area('hand_fill', (1.25, 1.15, 1.25), (0, 0, 0), 5, hexc('#ffcf9a'), (0.4, 0.4))
hf.rotation_euler = (V((0.6, 1.5, 0.88)) - hf.location).to_track_quat('-Z', 'Y').to_euler()

# ============================================================ DOUG: no hat, on his right side, facing the camera (+X)
for o in bpy.data.objects:
    if o.name.startswith('hat_'): o.hide_render = True; o.hide_viewport = True      # bedtime: no bucket hat
tina['root'].location = (-50, 0, 0)
dr = doug['root']
TILT = D(6.5)                                    # head end raised onto the pillow
BASE = Matrix(((0, -1, 0), (0, 0, 1), (-1, 0, 0)))   # columns: local x->-Z, local y->-X, local z->+Y
ROOT0 = V((-0.06, 0.34, 0.885))
ROLL0 = D(-16)                                   # rolled back a little so the face opens up toward the camera
def root_mat(roll=0.0, pitch=0.0, yaw=0.0):
    """roll: about the body axis (+ turns the face down into the pillow); pitch: head up; yaw: curl."""
    Rt = Matrix.Rotation(TILT + pitch, 3, 'X') @ Matrix.Rotation(yaw, 3, 'Z') @ BASE @ Matrix.Rotation(ROLL0 + roll, 3, 'Z')
    return Rt
dr.rotation_mode = 'XYZ'
dr.location = ROOT0; dr.rotation_euler = root_mat().to_euler()
doug['mouth'].hide_render = True
LIDS = [o for o in bpy.data.objects if o.name.startswith('doug_lid')]
EZ = doug['ez']; R = doug['r']
BROW_Z0 = [bp.location.z for bp in doug['brows']]
# mouth: one bezier tube that morphs from the neutral bean into a smile (keyed control points)
MP = V((0, -0.313, EZ - 0.17))
mouth_e = empty('mouth_e', MP, dr)
mouth = noodle('mouth_curve', [(-0.03, 0, 0), (0, 0, 0), (0.03, 0, 0)], 0.016, M['mouth'], mouth_e)
SH_NEU = [(-0.03, 0.000, 0.000), (0, 0.000, 0.000), (0.03, 0.000, 0.000)]
SH_SM = [(-0.05, 0.003, 0.012), (0, -0.002, -0.007), (0.05, 0.003, 0.012)]
SH_BIG = [(-0.072, 0.007, 0.03), (0, -0.003, -0.02), (0.072, 0.007, 0.03)]
def mouth_shape(s):
    a, b, t = (SH_NEU, SH_SM, s / 0.5) if s <= 0.5 else (SH_SM, SH_BIG, (s - 0.5) / 0.5)
    return [V(p) * (1 - t) + V(q) * t for p, q in zip(a, b)]

# ============================================================ PHONE in the right (lower) hand, resting low in front of his face
bpy.context.view_layer.update()
def eye_mid(): return (doug['eyes'][0].matrix_world.translation + doug['eyes'][1].matrix_world.translation) / 2
EYE0 = eye_mid()
PH0 = V((0.64, 1.53, 0.93))                       # phone centre: in front of his face, low over the mattress
phone = empty('phone_e', PH0)
def phone_rot(P):
    n = (eye_mid() - P).normalized()               # screen normal (local -y) points at his eyes
    up = V((0, 1, 0.25)).normalized()
    yv = -n; zv = (up - yv * up.dot(yv)).normalized(); xv = yv.cross(zv)
    return Matrix((xv, yv, zv)).transposed().to_euler()
phone.rotation_euler = phone_rot(PH0)
# iPhone-style phone (generic, no logo): rounded-corner slab, titanium frame, frosted back glass,
# square camera bump with three lenses + flash in the top corner, black display with a pill-shaped island.
PW, PT, PH, PR = 0.13, 0.016, 0.262, 0.024          # width, thickness, height, corner radius (phone space: x, y, z)
PM = dict(
    frame=mat('ph_frame', hexc('#b9b1a3'), 0.28, 0.0),
    back=mat('ph_back', hexc('#cfc6b6'), 0.55, 0.3),
    bump=mat('ph_bump', hexc('#c4bba9'), 0.3, 0.6),
    ring=mat('ph_ring', hexc('#8f877a'), 0.2, 0.0),
    glass=mat('ph_lens', hexc('#050608'), 0.05, 1.0),
    flash=mat('ph_flash', hexc('#f3ead2'), 0.3, 0.5),
    bezel=mat('ph_bezel', hexc('#020203'), 0.15, 1.0),
)
for k in ('frame', 'ring'):
    PM[k].node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 1.0
def rrect_slab(name, w, h, r, depth, y, m, parent, bevel=0.0, seg=10):
    """Rounded rectangle in the x-z plane, extruded along y (centred on y)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    pts = []
    for cx, cz, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(seg + 1):
            a = D(a0 + 90 * k / seg); pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    front = [bm.verts.new((x, -depth / 2, z)) for x, z in pts]
    back = [bm.verts.new((x, depth / 2, z)) for x, z in pts]
    bm.faces.new(front[::-1]); bm.faces.new(back)
    n = len(pts)
    for i in range(n):
        bm.faces.new((front[i], front[(i + 1) % n], back[(i + 1) % n], back[i]))
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me)); o.location = (0, y, 0)
    if bevel:
        b = o.modifiers.new('b', 'BEVEL'); b.width = bevel; b.segments = 4; b.limit_method = 'ANGLE'; b.angle_limit = D(50)
    o.data.materials.append(m); o.parent = parent
    for pg in o.data.polygons: pg.use_smooth = True
    o.data.shade_auto_smooth() if hasattr(o.data, 'shade_auto_smooth') else None
    return o
rrect_slab('phone_frame', PW, PH, PR, PT, 0, PM['frame'], phone, bevel=0.004)
rrect_slab('phone_back', PW - 0.006, PH - 0.006, PR - 0.003, 0.001, PT / 2 + 0.0002, PM['back'], phone)
rrect_slab('phone_bezel', PW - 0.004, PH - 0.004, PR - 0.002, 0.001, -PT / 2 - 0.0002, PM['bezel'], phone)
rrect_slab('phone_screen', PW - 0.016, PH - 0.016, PR - 0.008, 0.001, -PT / 2 - 0.0008, R_['screen'], phone)
rrect_slab('phone_island', 0.034, 0.010, 0.005, 0.001, -PT / 2 - 0.0014, PM['bezel'], phone).location.z = PH / 2 - 0.018
# camera bump in the back top corner (viewer's left when looking at the back = +x)
BX, BZ, BS = PW / 2 - 0.036, PH / 2 - 0.036, 0.058
bump = rrect_slab('phone_bump', BS, BS, 0.014, 0.003, PT / 2 + 0.0015, PM['bump'], phone, bevel=0.0012)
bump.location.x, bump.location.z = BX, BZ
for i, (dx, dz) in enumerate(((-0.013, 0.013), (-0.013, -0.013), (0.013, 0.0))):      # three lenses, triangle layout
    ring = cyl('phone_lensring', 0.0115, 0.004, (BX + dx, PT / 2 + 0.004, BZ + dz), PM['ring'], rot=(D(90), 0, 0), parent=None)
    ring.parent = phone
    glass = cyl('phone_lens', 0.0085, 0.0012, (BX + dx, PT / 2 + 0.0062, BZ + dz), PM['glass'], rot=(D(90), 0, 0)); glass.parent = phone
fl = cyl('phone_flash', 0.0038, 0.001, (BX + 0.014, PT / 2 + 0.0035, BZ + 0.016), PM['flash'], rot=(D(90), 0, 0)); fl.parent = phone
cyl('phone_mic', 0.0022, 0.001, (BX + 0.014, PT / 2 + 0.0035, BZ - 0.016), PM['glass'], rot=(D(90), 0, 0)).parent = phone
# side buttons (power on +x, volume on -x)
box('phone_btn', (0.003, 0.006, 0.03), (PW / 2 + 0.0008, 0, 0.04), PM['frame'], 0.001, phone)
for z in (0.06, 0.025): box('phone_btn', (0.003, 0.006, 0.022), (-PW / 2 - 0.0008, 0, z), PM['frame'], 0.001, phone)
pl = bpy.data.lights.new('phone_light', 'AREA'); pl.energy = 5.5; pl.color = hexc('#ffe7cf'); pl.shape = 'RECTANGLE'
pl.size, pl.size_y = 0.11, 0.22
plo = link(bpy.data.objects.new('phone_light', pl)); plo.parent = phone; plo.location = (0, -0.02, 0)
plo.rotation_euler = (D(-90), 0, 0)              # light -Z -> phone -y (toward his face)
plo.visible_camera = False; plo.visible_glossy = False
bounce = bpy.data.lights.new('phone_bounce', 'POINT'); bounce.energy = 6; bounce.color = hexc('#ffd9b0'); bounce.shadow_soft_size = 0.15
bo = link(bpy.data.objects.new('phone_bounce', bounce)); bo.parent = phone; bo.location = (0, -0.12, -0.05)
# grip: mitten hand behind the lower half, thumb over the side edge
GRIP = V((0.0, 0.055, -0.06))                   # in phone space (behind the phone)
thumb = sphere('thumb', 0.034, M['doug'], (0.07, -0.006, -0.03), (0.75, 0.8, 1.3), parent=phone)

def reach(side, target_world, f):
    """Point an arm (shoulder empty) so its hand lands on target_world; keyed at frame f."""
    sh = doug['arms'][side]; sx = -1 if side == 'L' else 1
    scene.frame_set(f); bpy.context.view_layer.update()
    s_w = sh.matrix_world.translation.copy()
    inv = dr.matrix_world.to_3x3().normalized().inverted()
    d_local = inv @ (target_world - s_w)
    h = V((sx * 0.06, 0, -0.59))
    q = h.normalized().rotation_difference(d_local.normalized())
    sh.rotation_mode = 'QUATERNION'
    sh.rotation_quaternion = q; sh.keyframe_insert('rotation_quaternion', frame=f)
    sh.scale = V((1, 1, d_local.length / h.length)); sh.keyframe_insert('scale', frame=f)

# ============================================================ BLANKET (heightfield draped over the body, shape-keyed)
def body_axis_z(y): return ROOT0.z + max(0.0, y - ROOT0.y) * math.tan(TILT)
def blanket_z(x, y, pull=0.0, breath=0.0, foot=0.0, curl=0.0):
    zc = body_axis_z(y) + 0.02 + breath * 0.012
    xc = -0.06 + curl * 0.02
    hgt = zc + 0.36 - MATT
    w = 0.44
    u = abs(x - xc) / w
    z = MATT + (hgt * (1 - u ** 2.3) ** (1 / 2.3) if u < 1 else 0.0)
    if abs(x) > 0.6: z = min(z, MATT - (abs(x) - 0.6) * 2.4)
    z = max(z, MATT + 0.02 if abs(x) <= 0.6 else z)
    z += 0.010 * math.sin(x * 23) * math.sin(y * 17)
    if foot: z += foot * 0.05 * math.exp(-((x - 0.02) ** 2 / 0.02 + (y - 0.42) ** 2 / 0.01))
    return z
def blanket_top(x, pull):
    front = max(0.0, min(1.0, (x + 0.05) / 0.35))
    return 1.30 + 0.05 * front + pull * 0.07 * front
NX_, NY_ = 56, 40
def blanket_pts(pull=0.0, breath=0.0, foot=0.0, curl=0.0):
    pts = []
    for j in range(NY_ + 1):
        for i in range(NX_ + 1):
            x = -0.68 + 1.36 * i / NX_
            y = -0.02 + (blanket_top(x, pull) + 0.02 * (1 - abs(x) / 0.68) - (-0.02)) * j / NY_
            z = blanket_z(x, y, pull, breath, foot, curl)
            # the top edge folds over a little toward the camera so it reads as a quilt edge
            if j >= NY_ - 1 and x > -0.1: z += 0.012
            pts.append(V((x, y, z)))
    return pts
me = bpy.data.meshes.new('blanket'); bm = bmesh.new()
vv = [bm.verts.new(p) for p in blanket_pts()]
for j in range(NY_):
    for i in range(NX_):
        a = j * (NX_ + 1) + i
        bm.faces.new((vv[a], vv[a + 1], vv[a + NX_ + 2], vv[a + NX_ + 1]))
bm.to_mesh(me); bm.free()
blanket = link(bpy.data.objects.new('blanket', me))
s_ = blanket.modifiers.new('sol', 'SOLIDIFY'); s_.thickness = 0.045; s_.offset = 1
blanket.modifiers.new('sub', 'SUBSURF').levels = 1
finish(blanket, QUILT)
blanket.shape_key_add(name='Basis')
for nm, kw in (('pull', dict(pull=1)), ('breath', dict(breath=1)), ('foot', dict(foot=1)), ('curl', dict(curl=1))):
    sk = blanket.shape_key_add(name=nm, from_mix=False)
    for k, p in enumerate(blanket_pts(**kw)): sk.data[k].co = p
SK = blanket.data.shape_keys.key_blocks

# ============================================================ CAMERA: elevated three-quarter from the front-foot side
cam_data.lens = 34; cam_data.dof.aperture_fstop = 2.8
CAM0 = V((1.62, 1.40, 1.80)); CAM1 = V((1.52, 1.43, 1.74))
target.location = V((0.30, 1.58, 0.96))
focus.location = EYE0

# ============================================================ PERFORMANCE (per-frame tables, eased)
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def ease_tab(keys, f):
    if f <= keys[0][0]: return keys[0][1]
    if f >= keys[-1][0]: return keys[-1][1]
    for (fa, va), (fb, vb) in zip(keys, keys[1:]):
        if fa <= f <= fb:
            t = smooth((f - fa) / max(1, fb - fa))
            return tuple(x + (y - x) * t for x, y in zip(va, vb))
F_INT, F_SM0, F_SM1, F_KIL, F_PULL0, F_PULL1, F_PEAK0, F_PEAK1, F_SETTLE, F_WIG = (B[k] for k in (
    'interested', 'smile_start', 'smile_small', 'kilig', 'pull_start', 'pull_end', 'peak_start', 'peak_end', 'settle', 'shy_wiggle'))
#            (lid, low_lid, smile, browdz, browtilt, pull, roll, curl, sh_rise)
EMO = [(1,        (20, 0.0, 0.00, -0.01, 6, 0.0, 0.0, 0.0, 0.0)),        # sleepy, should have slept already
       (F_INT,    (20, 0.0, 0.00, -0.01, 6, 0.0, 0.0, 0.0, 0.0)),
       (F_INT + 10, (-6, 0.0, 0.00, 0.012, -2, 0.0, 0.0, 0.0, 0.0)),     # interested: lids lift, brows up a touch
       (F_SM0,    (-6, 0.0, 0.02, 0.012, -2, 0.0, 0.0, 0.0, 0.0)),
       (F_SM1,    (2, 0.25, 0.38, 0.010, -6, 0.0, 0.0, 0.0, 0.0)),      # small involuntary smile, eyes soften
       (F_KIL,    (4, 0.30, 0.45, 0.012, -8, 0.0, 0.0, 0.0, 0.0)),
       (F_PULL1,  (12, 0.55, 0.68, 0.020, -14, 1.0, D(4), 0.4, 1.0)),     # kilig: blanket pulled up, shoulders up, shy brows
       (F_PEAK0,  (14, 0.60, 0.74, 0.022, -16, 1.0, D(3), 0.5, 0.8)),
       (F_PEAK0 + 14, (28, 0.85, 1.00, 0.028, -18, 1.0, D(14), 1.0, 1.0)),  # peak: big smile, snuggles into the pillow
       (F_PEAK1 - 10, (28, 0.85, 1.00, 0.028, -18, 1.0, D(12), 1.0, 1.0)),
       (F_PEAK1,  (12, 0.65, 0.92, 0.020, -14, 1.0, D(3), 0.6, 0.5)),     # settles back, still watching
       (N,        (11, 0.62, 0.90, 0.020, -13, 1.0, D(2), 0.6, 0.4))]
BLINKS = BEATS['blinks']       # frame of full closure; slow when sleepy, quick and happy later
def blink(f):
    for b in BLINKS:
        dur = 4 if b < F_INT else 3
        if abs(f - b) <= dur: return 1 - abs(f - b) / (dur + 1)
    return 0.0
rng = random.Random(19)
SAC = {}
def saccade(f):
    k = f // (14 if f < F_INT else 10)
    if k not in SAC: SAC[k] = V((0, rng.uniform(-0.012, 0.012), rng.uniform(-0.008, 0.008)))
    return SAC[k]
def read_scan(f):   # tiny left-right reading of the clip across the screen (along the phone's width)
    return math.sin(f * 0.21) * 0.010 if f < F_INT else math.sin(f * 0.13) * 0.005

def aim(pivot, Tp, clamp_yaw=40, clamp_pitch=30):
    P = pivot.matrix_world.translation; Rp = pivot.parent.matrix_world.to_3x3().normalized()
    d = Rp.inverted() @ (Tp - P)
    yaw = math.degrees(math.atan2(d.x, -d.y)); pitch_ = -math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    yaw = max(-clamp_yaw, min(clamp_yaw, yaw)); pitch_ = max(-clamp_pitch, min(clamp_pitch, pitch_))
    return (D(pitch_), 0, D(yaw))

LSH = doug['arms']['L']; RSH = doug['arms']['R']
LSH0 = LSH.location.copy(); RSH0 = RSH.location.copy()
for f in range(1, N + 1):
    lid, low, sm, bdz, btilt, pull, roll, curl, rise = ease_tab(EMO, f)
    if os.environ.get('FORCE'): lid, low, sm = map(float, os.environ['FORCE'].split(','))
    # breathing (slower, deeper when sleepy) + the little shy wiggle at the end
    br = 0.5 + 0.5 * math.sin(f * (2 * math.pi / (110 if f < F_INT else 80)))
    wig = 0.0
    if F_WIG <= f <= F_WIG + 16: wig = math.sin((f - F_WIG) / 16 * 2 * math.pi) * (1 - (f - F_WIG) / 16)
    # peak foot wiggle under the blanket (seen as the far bump moving)
    foot = 0.0
    if F_PEAK0 + 6 <= f <= F_PEAK1 - 6: foot = 0.5 + 0.5 * math.sin((f - F_PEAK0) * 0.75)
    # root: roll into the pillow, slight curl (yaw), breathing lift, shy wiggle
    Rm = root_mat(roll=roll + D(2.5) * wig, pitch=D(1.2) * rise, yaw=D(3) * curl)
    dr.rotation_euler = Rm.to_euler(); dr.keyframe_insert('rotation_euler', frame=f)
    dr.location = ROOT0 + V((0, 0.02 * curl, 0.004 * br)); dr.keyframe_insert('location', frame=f)
    # shoulders rise (toward the head, local +z)
    LSH.location = LSH0 + V((0, 0, 0.035 * rise + 0.01 * wig)); LSH.keyframe_insert('location', frame=f)
    RSH.location = RSH0 + V((0, 0, 0.035 * rise)); RSH.keyframe_insert('location', frame=f)
    # blanket follows breath / pull / curl / feet
    for nm, v in (('pull', pull), ('breath', br), ('foot', foot), ('curl', curl)):
        SK[nm].value = v; SK[nm].keyframe_insert('value', frame=f)
    # lids (blink adds to the upper lid), lower lids (smile cheeks)
    bl = blink(f)
    for o in LIDS: o.rotation_euler = (D(lid + (100 - lid) * bl), 0, 0); o.keyframe_insert('rotation_euler', frame=f)
    for i, bp in enumerate(doug['brows']):
        sx = -1 if i == 0 else 1
        bp.location = (bp.location.x, bp.location.y, BROW_Z0[i] + bdz); bp.keyframe_insert('location', frame=f)
        bp.rotation_euler = (0, sx * D(btilt), 0); bp.keyframe_insert('rotation_euler', frame=f)
    # mouth morph
    for bpt, p in zip(mouth.data.splines[0].bezier_points, mouth_shape(sm)):
        bpt.handle_left_type = bpt.handle_right_type = 'AUTO'
        bpt.co = p; mouth.data.update_tag()
        bpt.keyframe_insert('co', frame=f)
    mouth.data.splines[0].calc_length()
    for bpt in mouth.data.splines[0].bezier_points:
        bpt.keyframe_insert('handle_left', frame=f); bpt.keyframe_insert('handle_right', frame=f)
    mouth.data.bevel_depth = 0.016 - 0.001 * sm; mouth.data.keyframe_insert('bevel_depth', frame=f)
    # camera: still, with a very slow push-in during the reaction
    t = smooth((f - F_SM0) / (N - F_SM0))
    cam.location = CAM0.lerp(CAM1, t); cam.keyframe_insert('location', frame=f)
    cam_data.lens = 34 + 3.5 * t; cam_data.keyframe_insert('lens', frame=f)

# phone follows the hand pose: keep it in front of his face; tiny hand tremor; the hand grips it
for f in range(1, N + 1):
    scene.frame_set(f); bpy.context.view_layer.update()
    lid, low, sm, bdz, btilt, pull, roll, curl, rise = ease_tab(EMO, f)
    P = PH0 + V((0, 0.025 * curl, -0.03 * curl + 0.012 * rise)) + V((0, 0.002 * math.sin(f * 0.37), 0.0015 * math.sin(f * 0.29)))
    phone.location = P; phone.keyframe_insert('location', frame=f)
    phone.rotation_euler = phone_rot(P); phone.keyframe_insert('rotation_euler', frame=f)
for f in range(1, N + 1, 2):
    scene.frame_set(f); bpy.context.view_layer.update()
    reach('R', phone.matrix_world @ GRIP, f)
    lid, low, sm, bdz, btilt, pull, roll, curl, rise = ease_tab(EMO, f)
    # free (left, upper) hand holds the blanket edge over his chest and pulls it up
    ex = 0.34; ey = blanket_top(ex, pull) - 0.035
    reach('L', V((ex + 0.03, ey, blanket_z(ex, ey, pull) + 0.03)), f)
# eyes on the screen (with reading scan + saccades); keyed after everything else moves
for f in range(1, N + 1):
    scene.frame_set(f); bpy.context.view_layer.update()
    Mw = phone.matrix_world
    T = Mw @ V((read_scan(f), -0.01, 0.0)) + saccade(f)
    for e in doug['eyes']:
        e.rotation_euler = aim(e, T); e.keyframe_insert('rotation_euler', frame=f)
    focus.location = eye_mid(); focus.keyframe_insert('location', frame=f)

scene.frame_set(1); bpy.context.view_layer.update()
print('DBG eye_mid', eye_mid(), 'phone', phone.matrix_world.translation, 'Lsh', LSH.matrix_world.translation, 'Lscale', LSH.scale, 'Rsh', RSH.matrix_world.translation, 'Rscale', RSH.scale)
print('DBG head top', dr.matrix_world @ V((0,0,doug['top'])), 'root', dr.matrix_world.translation)
if os.environ.get('DBGCAM'):
    cx, cy, cz, tx, ty, tz, ln = map(float, os.environ['DBGCAM'].split(','))
    cam.animation_data_clear(); cam_data.animation_data_clear(); cam.location = (cx, cy, cz); target.location = (tx, ty, tz); cam_data.lens = ln
    cam_data.dof.use_dof = False
render(N)
