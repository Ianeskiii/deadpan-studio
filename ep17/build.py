"""Tube Town - When you finish work at 4:59 PM ("Mamba out").
usage: cd ep17 && python3 build.py SHOT OUTDIR [opts]
  SHOT = A S C D E   (film shots)  |  QA (prints hand/prop positions)  |  SIDE (QA side view)
Pipeline: vo17.py -> screen.py -> build.py QA -> render.sh -> overlays.py -> audio.py -> assemble.py
Beats live in beats.py. Seated legs are the ep14/ep16 set-up; the face (curve mouth, lids, brows) is the ep16 one.
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
from beats import *
from mathutils import Matrix, Quaternion, Euler
import soundfile as _sf
def V(*a): return Vector(a)
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def win(f, w): return smooth((f - w[0]) / max(1, w[1] - w[0]))
def ease_tab(keys, f):
    if f <= keys[0][0]: return keys[0][1]
    for (fa, a), (fb, b) in zip(keys, keys[1:]):
        if fa <= f <= fb:
            t = smooth((f - fa) / max(1, fb - fa))
            if isinstance(a, (int, float)): return a + (b - a) * t
            if isinstance(a, Vector): return a.lerp(b, t)
            return tuple(x + (y - x) * t for x, y in zip(a, b))
    return keys[-1][1]
def mlerp(ma, mb, t):
    la, ra, _ = ma.decompose(); lb, rb, _ = mb.decompose()
    m = ra.slerp(rb, t).to_matrix().to_4x4(); m.translation = la.lerp(lb, t); return m

# ============================================================ HOME OFFICE (warm late afternoon)
tina['root'].location = (-80, 0, 0)
for o in list(bpy.data.objects):
    if o.name.startswith(('phone', 'screen')) and o.parent and o.parent.name.startswith('tina'): o.hide_render = True
R_ = dict(
    floor=brick_mat('planks17', hexc('#7a5638'), hexc('#6c4b31'), hexc('#4a3220'), 1.2, 1.6, 0.18, 0.37, 0.55),
    wall=mat('of_wall', hexc('#c8b597'), 0.9), wall2=mat('of_wall2', hexc('#b9a586'), 0.9), ceil=mat('of_ceil', hexc('#d8cdb8'), 0.9),
    desk=mat('of_desk', hexc('#a07a52'), 0.45, 0.1), deskleg=mat('of_deskleg', hexc('#2b2d31'), 0.4, 0.5),
    dark=mat('of_dark', hexc('#1c1e22'), 0.35, 0.3), grey=mat('of_grey', hexc('#3a3d44'), 0.45, 0.2), chair=mat('of_chair', hexc('#2e3442'), 0.7, 0.0, sheen=0.4),
    metal=mat('of_metal', hexc('#9aa0a8'), 0.3, 0.8), rug=mat('of_rug', hexc('#4f6273'), 0.95), plant=mat('of_leaf', hexc('#3f6e45'), 0.6),
    pot=mat('of_pot', hexc('#d9d2c4'), 0.5), book1=mat('of_b1', hexc('#a2423a'), 0.7), book2=mat('of_b2', hexc('#3e5f8a'), 0.7), book3=mat('of_b3', hexc('#d2a64a'), 0.7),
    frame=mat('of_frame', hexc('#2b2b2b'), 0.5), art=mat('of_art', hexc('#e2a46b'), 0.8), mug=mat('of_mug', hexc('#e9e4da'), 0.3, 0.2),
    sky=mat('of_sky', (0, 0, 0), 0.5, 0, hexc('#ffc38a'), 2.2), blind=mat('of_blind', hexc('#efe6d6'), 0.8),
)
box('of_floor', (8, 8, 0.1), (0, 0, -0.05), R_['floor'])
box('of_rear', (8, 0.2, 3.0), (0, 1.65, 1.5), R_['wall'])
box('of_front', (8, 0.2, 3.0), (0, -1.95, 1.5), R_['wall2'])
box('of_right', (0.2, 8, 3.0), (2.5, 0, 1.5), R_['wall2'])
box('of_ceil', (8, 8, 0.1), (0, 0, 3.0), R_['ceil'])
WX = -1.95                                    # window wall (Doug's right, screen-left in the A shot): an opening the sun comes through
box('win_w_lo', (0.2, 8, 0.95), (WX, 0, 0.475), R_['wall2']); box('win_w_hi', (0.2, 8, 0.8), (WX, 0, 2.6), R_['wall2'])
box('win_w_a', (0.2, 3.0, 1.25), (WX, -2.5, 1.575), R_['wall2']); box('win_w_b', (0.2, 3.0, 1.25), (WX, 2.4, 1.575), R_['wall2'])
for z in (0.95, 2.2): box('win_sill', (0.26, 3.0, 0.05), (WX, -0.05, z), R_['ceil'])
for y in (-1.0, 0.9): box('win_jamb', (0.26, 0.05, 1.25), (WX, y, 1.575), R_['ceil'])
for i in range(7): box('blind', (0.02, 1.9, 0.035), (WX + 0.12, -0.05, 2.12 - i * 0.06), R_['blind'])        # half-raised blinds
box('of_skyplane', (0.05, 9, 5), (-3.4, 0, 1.5), R_['sky'])
box('of_rug', (2.2, 1.8, 0.012), (0, -0.25, 0.006), R_['rug'], 0.004)
# shelf + books + art on the rear wall (behind Doug)
box('shelf', (1.1, 0.24, 0.03), (0.95, 1.45, 1.55), R_['desk'])
x = 0.48
for i, (w_, h_, m_) in enumerate(((0.05, 0.24, 'book1'), (0.04, 0.27, 'book2'), (0.06, 0.22, 'book3'), (0.045, 0.26, 'book1'), (0.05, 0.23, 'book2'))):
    box('book', (w_, 0.17, h_), (x, 1.45, 1.565 + h_ / 2), R_[m_]); x += w_ + 0.008
cyl('shelf_pot', 0.06, 0.1, (1.3, 1.45, 1.615), R_['pot'])
for i in range(5): sphere('shelf_leaf', 0.05, R_['plant'], (1.3 + 0.04 * math.cos(i * 1.3), 1.45 + 0.04 * math.sin(i * 1.3), 1.7), (1, 0.6, 1.5))
box('art_f', (0.62, 0.03, 0.46), (-0.75, 1.54, 1.75), R_['frame'], 0.005); box('art', (0.56, 0.02, 0.40), (-0.75, 1.52, 1.75), R_['art'])
cyl('floor_pot', 0.17, 0.36, (1.7, 1.15, 0.18), R_['pot'])
for i in range(8):
    a_ = i * 2.3; sphere('fleaf', 0.14, R_['plant'], (1.7 + 0.11 * math.cos(a_), 1.15 + 0.11 * math.sin(a_), 0.55 + 0.07 * (i % 3)), (1, 0.5, 1.8), rot=(D(22) * math.cos(a_), D(22) * math.sin(a_), a_))

# ---- desk, monitor, keyboard, mouse, lamp, mug
SEAT = 0.42; DESK = 0.78
box('desk_top', (2.0, 0.74, 0.04), (0.0, -0.75, DESK - 0.02), R_['desk'], 0.008)
for sx in (-0.97, 0.97): box('desk_leg', (0.04, 0.66, DESK - 0.04), (sx, -0.75, (DESK - 0.04) / 2), R_['deskleg'])
box('desk_back', (1.8, 0.02, 0.32), (0.05, -1.08, DESK - 0.2), R_['deskleg'])
MON = V(0.0, -0.98, 1.17); SCW, SCH = 0.64, 0.36; MON_YAW = float(os.environ.get('MON_YAW', '-15'))   # turned a little toward the A camera
MON_M = Matrix.Translation(MON) @ Matrix.Rotation(D(MON_YAW), 4, 'Z')
mon = empty('monitor', tuple(MON)); mon.rotation_euler = (0, 0, D(MON_YAW))
box('mon_bezel', (SCW + 0.025, 0.024, SCH + 0.025), (0, -0.013, 0), R_['dark'], 0.006, mon)
box('mon_back', (0.3, 0.05, 0.2), (0, -0.045, 0), R_['grey'], 0.02, mon)
box('mon_neck', (0.05, 0.03, 0.34), (0, -0.07, DESK + 0.17 - MON.z), R_['grey'], 0.008, mon)
box('mon_foot', (0.26, 0.18, 0.014), (0, -0.04, DESK + 0.007 - MON.z), R_['grey'], 0.005, mon)
box('webcam', (0.07, 0.03, 0.025), (0, -0.006, SCH / 2 + 0.03), R_['dark'], 0.006, mon)
cyl('webcam_lens', 0.007, 0.004, (0, 0.010, SCH / 2 + 0.03), mat('lens', hexc('#0a0d1a'), 0.1, 0.5), rot=(D(90), 0, 0), verts=16, parent=mon)
WEBCAM = MON_M @ V(0, 0.006, SCH / 2 + 0.03)
scr_m = bpy.data.materials.new('mon_screen'); scr_m.use_nodes = True; nt = scr_m.node_tree; nt.nodes.clear()
em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.35
o_ = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs['Emission'], o_.inputs['Surface'])
SDIR = os.path.join(HERE, 'screen'); NSC = len([f for f in os.listdir(SDIR) if f.endswith('.png')]) if os.path.isdir(SDIR) else 0
if NSC:
    img = bpy.data.images.load(os.path.join(SDIR, 's_0001.png')); img.source = 'SEQUENCE'
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.image_user.frame_duration = NSC; tex.image_user.frame_start = 1
    tex.image_user.frame_offset = 0; tex.image_user.use_auto_refresh = True; tex.extension = 'CLIP'
    nt.links.new(tex.outputs['Color'], em.inputs['Color'])
else: em.inputs['Color'].default_value = (0.8, 0.8, 0.85, 1)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
scr = bpy.context.active_object; scr.name = 'mon_screen'; scr.scale = (SCW, SCH, 1); scr.rotation_euler = (D(-90), D(180), 0)
scr.data.materials.append(scr_m); scr.parent = mon; scr.location = (0, 0.0005, 0)
sl = bpy.data.lights.new('screen_glow', 'AREA'); sl.shape = 'RECTANGLE'; sl.size = SCW; sl.size_y = SCH; sl.energy = 18; sl.color = (0.85, 0.9, 1.0)
slo = link(bpy.data.objects.new('screen_glow', sl)); slo.parent = mon; slo.location = (0, 0.03, 0); slo.rotation_euler = (D(-90), 0, 0); slo.visible_camera = False
def scr_px(px, py):            # screen pixel (1920x1080) -> world point on the monitor (the screen faces Doug)
    return MON_M @ V(-(px / 1920 - 0.5) * SCW, 0.002, (0.5 - py / 1080) * SCH)
ACC_W = scr_px(1120, 822); CLOCK_W = scr_px(960, 150); DOC_W = scr_px(700, 700); CARD_W = scr_px(960, 560)
KB = V(0.02, -0.60, DESK)
box('kb', (0.42, 0.14, 0.018), (KB.x, KB.y, DESK + 0.009), R_['dark'], 0.004)
for r in range(4):
    for c in range(14):
        box('key', (0.024, 0.024, 0.008), (KB.x - 0.185 + c * 0.0285, KB.y - 0.045 + r * 0.03, DESK + 0.021), R_['grey'], 0.002)
box('mousepad', (0.24, 0.2, 0.004), (0.42, -0.62, DESK + 0.002), R_['grey'], 0.003)
mouse = empty('mouse'); box('mouse_body', (0.062, 0.1, 0.026), (0, 0, 0.017), R_['dark'], 0.022, mouse)
MOUSE0 = V(0.42, -0.62, DESK + 0.004)
cyl('lamp_base', 0.07, 0.02, (-0.88, -1.04, DESK + 0.01), R_['dark'])
cyl('lamp_arm', 0.01, 0.42, (-0.88, -1.04, DESK + 0.22), R_['dark'])
sphere('lamp_head', 0.07, mat('lamp_shade', hexc('#e9a35a'), 0.4, 0.0, hexc('#ffcf8a'), 1.2), (-0.85, -0.98, DESK + 0.44), (1, 1, 0.7))
cyl('mug', 0.04, 0.1, (-0.22, -1.02, DESK + 0.05), R_['mug'])
cyl('mug_coffee', 0.035, 0.002, (-0.22, -1.02, DESK + 0.095), mat('coffee', hexc('#3b2416'), 0.2))

# ---- office chair (seat top at SEAT like the couch so the ep14 seated legs fit)
box('ch_seat', (0.66, 0.58, 0.08), (0, 0.10, SEAT - 0.04), R_['chair'], 0.03)
box('ch_back', (0.6, 0.07, 0.6), (0, 0.42, SEAT + 0.36), R_['chair'], 0.03)
box('ch_spine', (0.06, 0.04, 0.3), (0, 0.47, SEAT + 0.04), R_['dark'], 0.01)
cyl('ch_column', 0.028, SEAT - 0.16, (0, 0.10, (SEAT - 0.08) / 2 + 0.04), R_['metal'])
for i in range(5):
    a_ = D(90 + 72 * i); bx = box('ch_leg', (0.30, 0.04, 0.03), (0.15 * math.cos(a_), 0.10 + 0.15 * math.sin(a_), 0.07), R_['dark'], 0.01)
    bx.rotation_euler = (0, 0, a_); sphere('ch_wheel', 0.03, R_['dark'], (0.29 * math.cos(a_), 0.10 + 0.29 * math.sin(a_), 0.03))

# ---- light: low sun through the window, warm room, the screen
world(hexc('#3a3226'), 0.35)
sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.2; sun.color = hexc('#ffb36b'); sun.angle = D(2.5)
sn_ = link(bpy.data.objects.new('sun', sun)); sn_.rotation_euler = Euler((D(72), 0, D(-75)))       # low, from the window side
def aimed_area(name, loc, tgt, power, color, size):
    q = (V(*tgt) - V(*loc)).to_track_quat('-Z', 'Y'); return area(name, loc, q.to_euler(), power, color, size)
aimed_area('key', (1.2, -1.3, 2.3), (0, -0.2, 1.2), 110, hexc('#ffe2c0'), (1.2, 1.2))
aimed_area('fill', (-1.2, -1.2, 1.6), (0, 0, 1.2), 35, hexc('#ffd2a0'), (1.0, 1.0))
aimed_area('rim', (-0.9, 1.3, 2.2), (0, 0, 1.3), 60, hexc('#ffb878'), (1.0, 1.0))

# ============================================================ PROPS THAT MOVE: headset, pen
hsm = mat('hs_shell', hexc('#2a2d33'), 0.35, 0.3); hsp = mat('hs_pad', hexc('#141518'), 0.8); hsa = mat('hs_accent', hexc('#e07a3a'), 0.4, 0.2)
hs = empty('headset'); hs.rotation_mode = 'QUATERNION'
CUP_X = 0.352
for sx in (-1, 1):
    cyl('hs_cup', 0.072, 0.045, (sx * (CUP_X + 0.018), 0, 0), hsm, rot=(0, D(90), 0), parent=hs)
    cyl('hs_pad', 0.076, 0.024, (sx * (CUP_X - 0.012), 0, 0), hsp, rot=(0, D(90), 0), parent=hs)
    cyl('hs_ring', 0.074, 0.006, (sx * (CUP_X + 0.042), 0, 0), hsa, rot=(0, D(90), 0), parent=hs)
bc = bpy.data.curves.new('hs_band', 'CURVE'); bc.dimensions = '3D'; bc.bevel_depth = 0.016; bc.bevel_resolution = 4; bc.use_fill_caps = True
sp_ = bc.splines.new('POLY'); K_ = 24; sp_.points.add(K_)
for i, p in enumerate(sp_.points):          # behind the head, below the hat brim: neckband style, never touches the cap
    th = math.pi * i / K_; p.co = (-math.cos(th) * (CUP_X + 0.03), math.sin(th) * 0.375, 0.035 * math.sin(th) - 0.01, 1)
band = link(bpy.data.objects.new('hs_band', bc)); band.data.materials.append(hsm); band.parent = hs
mc = bpy.data.curves.new('hs_boom', 'CURVE'); mc.dimensions = '3D'; mc.bevel_depth = 0.006; mc.bevel_resolution = 3; mc.use_fill_caps = True
sp_ = mc.splines.new('NURBS'); pts = [(-0.39, -0.02, -0.02), (-0.41, -0.12, -0.07), (-0.38, -0.24, -0.10), (-0.31, -0.32, -0.115)]
sp_.points.add(len(pts) - 1)
for p, c in zip(sp_.points, pts): p.co = c + (1,)
sp_.use_endpoint_u = True; sp_.order_u = 3
boom = link(bpy.data.objects.new('hs_boom', mc)); boom.data.materials.append(hsm); boom.parent = hs
sphere('hs_mic', 0.02, hsp, (-0.30, -0.33, -0.115), (1.2, 1, 1), parent=hs)
HS_LOCAL = Matrix.Translation(V(0, 0.0, 0.98))                                      # worn: in Doug's upper-body space
# on the desk to his right, set down on its side (right cup nearest him), tipped so the cups and the mic both rest on the desk
HS_DESK = Matrix.Translation(V(-0.62, -0.73, DESK + 0.072)) @ Matrix.Rotation(D(-90), 4, 'Z') @ Matrix.Rotation(D(-12), 4, 'X')

pen = empty('pen'); pen.rotation_mode = 'QUATERNION'
cyl('pen_body', 0.012, 0.17, (0, 0, 0), mat('pen_blue', hexc('#2f6fe0'), 0.3, 0.3), verts=20, parent=pen)
cyl('pen_cap', 0.0125, 0.04, (0, 0, 0.066), mat('pen_cap', hexc('#f1f3f6'), 0.25, 0.4), verts=20, parent=pen)
cyl('pen_tip', 0.006, 0.016, (0, 0, -0.093), R_['metal'], verts=12, parent=pen)
box('pen_clip', (0.005, 0.006, 0.045), (0, 0.013, 0.062), R_['metal'], 0, pen)
PEN_R = 0.0125
def pen_lying(xy, yaw): return Matrix.Translation(V(xy[0], xy[1], DESK + PEN_R)) @ Matrix.Rotation(D(yaw), 4, 'Z') @ Matrix.Rotation(D(90), 4, 'X')
PEN_HOME = pen_lying((0.27, -0.47), 75)            # where it lives
PEN_LANDED = pen_lying((0.19, -0.45), -70)         # where the mic drop leaves it

# ============================================================ DOUG
exec(open(os.path.join(HERE, '..', 'ep12', 'rig.py')).read())
doug['mouth'].location.y = -0.326
doug_r = Rig(doug, 'doug', M['doug'], M['doug'], lift=0.17)
BASE = doug_r.base
KNEE_L = {'N': V(-0.17, -0.50, SEAT + 0.075), 'P': V(0.17, -0.50, SEAT + 0.075)}
FOOT_L = {'N': V(-0.19, -0.51, 0.03), 'P': V(0.19, -0.51, 0.03)}
SEATED = V(0, 0.05, 0)

ROLL_HS = float(os.environ.get('ROLL_HS', '5'))
POST = [(1, (6, 0, 0.0)), (TYPE[1], (6, 0, 0.0)), (RELAX[1], (0, 0, -0.012)),                      # typing ... shoulders let go
        (HS_OFF[0], (0, 0, -0.012)), (HS_OFF[0] + 12, (3, 0, -0.005)), (HS_OFF[1] - 4, (12, ROLL_HS, -0.01)), (HS_OFF[1] + 2, (5, 0, -0.01)),
        (PEN_PICK[1], (3, 0, -0.005)), (M_F + 15, (-2, 0, 0.004)), (PEN_DROP + 4, (-2.5, 0, 0.004)),      # sits back, pleased
        (CALL, (-2.5, 0, 0.004)), (DRAIN[1], (0, 0, -0.006)), (REACH[0], (0, 0, -0.008)), (REACH[1], (8, 0, -0.012)),
        (PEN_UP[1], (4, 0, -0.012)), (PEN_BACK[1], (7, 0, -0.012)), (HS_GRAB[1], (12, ROLL_HS, -0.012)), (HS_ON[0] + 6, (6, 0, -0.01)),
        (HS_ON[1], (2, 0, -0.01)), (SINK[0], (2, 0, -0.01)), (SINK[1], (5, 0, -0.04)), (MOUSE[1], (6, 0, -0.04)), (N, (6, 0, -0.04))]
def posture(f): return ease_tab(POST, f)
def breath(f): return 0.003 * math.sin(2 * math.pi * f / 96)
def upper_matrix(f):
    lean, roll, lift = posture(f); up = V(0, 0, BASE + lift + breath(f) * 0.4)
    return Matrix.Translation(SEATED) @ Matrix.Translation(up) @ Euler((D(lean), D(roll), 0)).to_matrix().to_4x4()
def to_local(w, f): return upper_matrix(f).inverted() @ V(*w)

# ---- headset world matrix
def HS(f):
    worn = lambda f_: upper_matrix(f_) @ HS_LOCAL
    lifted = lambda f_: upper_matrix(f_) @ Matrix.Translation(V(0, -0.10, 1.07))
    if f < HS_OFF[0] + 7: return worn(f)
    if f < HS_OFF[0] + 13: return mlerp(worn(f), lifted(f), win(f, (HS_OFF[0] + 7, HS_OFF[0] + 13)))
    if f < HS_OFF[1] - 2: return mlerp(lifted(f), HS_DESK, win(f, (HS_OFF[0] + 13, HS_OFF[1] - 2)))
    if f < HS_ON[0]: return HS_DESK
    if f < HS_ON[0] + 10: return mlerp(HS_DESK, lifted(f), win(f, (HS_ON[0], HS_ON[0] + 10)))
    if f < HS_ON[1] - 4: return mlerp(lifted(f), worn(f), win(f, (HS_ON[0] + 10, HS_ON[1] - 4)))
    return worn(f)
def cup_grip(f, side):         # a hand on the outside of a cup
    sx = -1 if side == 'N' else 1
    return HS(f) @ V(sx * (CUP_X + 0.075), 0.0, 0.0)

# ---- pen world matrix (grip: the pen sits through the fist)
def HAND_PEN(hand_w, upright):
    if upright: return Matrix.Translation(hand_w + V(0, 0, -0.012))                               # held up like a mic: vertical
    return Matrix.Translation(hand_w + V(0, 0, -0.045)) @ Matrix.Rotation(D(75), 4, 'Z') @ Matrix.Rotation(D(80), 4, 'X')
PEN_FALL_FROM = None
def pen_matrix(f, hw):
    """hw: right (N) hand world position this frame"""
    if f < PEN_PICK[0] + 5: return PEN_HOME
    if f < PEN_DROP:
        m_hold = HAND_PEN(hw, True); m_low = HAND_PEN(hw, False)
        return mlerp(PEN_HOME, m_hold, win(f, (PEN_PICK[0] + 5, PEN_PICK[1]))) if f < PEN_PICK[1] else m_hold
    if f < REACH[1]:            # dropped: falls under gravity, tips over, one small bounce, lies still
        t = (f - PEN_DROP) / FPS; z0 = MIC_TOP.z - 0.012; zl = DESK + PEN_R; T_ = math.sqrt(2 * (z0 - zl) / 9.81)
        lp, lq, _ = PEN_LANDED.decompose()
        if t < T_:
            z = z0 - 0.5 * 9.81 * t * t; a = t / T_
            q = Quaternion().slerp(lq, a ** 1.5)
            m = q.to_matrix().to_4x4(); m.translation = V(MIC_TOP.x, MIC_TOP.y, 0).lerp(V(lp.x, lp.y, 0), a) + V(0, 0, z); return m
        tb = t - T_; hop = 0.012 * max(0.0, math.sin(math.pi * tb / 0.1)) if tb < 0.1 else 0.0
        m = PEN_LANDED.copy(); m.translation = lp + V(0, 0, hop); return m
    if f < PEN_BACK[1] - 2:
        held = HAND_PEN(hw, False)
        if f < PEN_UP[0] + 3: return mlerp(PEN_LANDED, held, win(f, (REACH[1] - 1, PEN_UP[0] + 3)))
        if f < PEN_BACK[0] + 8: return held
        return mlerp(held, PEN_HOME, win(f, (PEN_BACK[0] + 8, PEN_BACK[1] - 2)))
    return PEN_HOME

# ---- hands (world targets)
REST = {'N': V(-0.24, -0.46, DESK + 0.06), 'P': V(0.24, -0.46, DESK + 0.06)}
def typing(side, f):
    sx = -1 if side == 'N' else 1; ph = f * 1.9 + (0 if side == 'N' else 1.6)
    return KB + V(sx * 0.10 + 0.02 * math.sin(f * 0.37 + sx), 0.015, 0.06 + 0.014 * max(0.0, math.sin(ph)))
MIC_TOP = V(0.24, -0.47, 1.17)                                      # beside his face                                     # the pen held up, mic-style
def pen_grab_pt(m): return m.translation + V(0, 0, 0.05)
def mouse_pos(f):
    return MOUSE0 + V(0.032, 0.016, 0) * win(f, CURSOR) + V(0.006 * math.sin(f * 0.11), 0, 0) * (f < TYPE[1])
def hand_P(f):
    if f < TYPE[1]: return typing('P', f)
    if f < HS_OFF[0]: return typing('P', TYPE[1]).lerp(REST['P'], win(f, (TYPE[1], RELAX[1])))
    if f < HS_OFF[0] + 7: return REST['P'].lerp(cup_grip(f, 'P'), win(f, (HS_OFF[0], HS_OFF[0] + 7)))
    if f < HS_OFF[0] + 13: return cup_grip(f, 'P')                                                  # both hands lift it off
    if f < PEN_PICK[0]: return cup_grip(HS_OFF[0] + 13, 'P').lerp(REST['P'], win(f, (HS_OFF[0] + 13, PEN_PICK[0])))   # lets go; the right hand sets it down
    if f < PEN_PICK[0] + 5: return REST['P'].lerp(pen_grab_pt(PEN_HOME), win(f, (PEN_PICK[0], PEN_PICK[0] + 5)))
    if f < PEN_PICK[1]: return pen_grab_pt(PEN_HOME).lerp(MIC_TOP, win(f, (PEN_PICK[0] + 5, PEN_PICK[1])))
    if f < PEN_DROP + 3: return MIC_TOP + V(0, 0, 0.004 * math.sin((f - PEN_PICK[1]) * 0.5))
    if f < REACH[0]: return (MIC_TOP + V(0, 0, 0.01)).lerp(REST['P'], win(f, (PEN_DROP + 3, PEN_DROP + 18)))
    lp = pen_grab_pt(PEN_LANDED)
    if f < REACH[1]: return REST['P'].lerp(lp, win(f, REACH))                                        # slow, reluctant
    held_hi = V(0.2, -0.47, DESK + 0.17)
    if f < PEN_UP[1]: return lp.lerp(held_hi, win(f, PEN_UP))
    if f < PEN_BACK[1]: return held_hi.lerp(pen_grab_pt(PEN_HOME), win(f, (PEN_BACK[0], PEN_BACK[1] - 2)))
    if f < HS_ON[0] + 4: return pen_grab_pt(PEN_HOME).lerp(REST['P'], win(f, (PEN_BACK[1], HS_GRAB[1])))
    if f < HS_ON[0] + 11: return REST['P'].lerp(cup_grip(f, 'P'), win(f, (HS_ON[0] + 4, HS_ON[0] + 11)))   # the left hand joins mid-air
    if f < HS_ON[1]: return cup_grip(f, 'P')
    if f < MOUSE[0]: return cup_grip(HS_ON[1], 'P').lerp(REST['P'] + V(0, 0, -0.01), win(f, HANDS_DOWN))
    on_mouse = lambda f_: mouse_pos(f_) + V(0, 0.012, 0.06)
    if f < MOUSE[1]: return (REST['P'] + V(0, 0, -0.01)).lerp(on_mouse(f), win(f, MOUSE))
    return on_mouse(f)
def hand_N(f):
    if f < TYPE[1]: return typing('N', f)
    if f < HS_OFF[0]: return typing('N', TYPE[1]).lerp(REST['N'], win(f, (TYPE[1], RELAX[1])))
    if f < HS_OFF[0] + 7: return REST['N'].lerp(cup_grip(f, 'N'), win(f, (HS_OFF[0], HS_OFF[0] + 7)))
    if f < HS_OFF[1]: return cup_grip(f, 'N')                                                       # carries it down, sets it on the desk
    if f < HS_GRAB[0]: return cup_grip(HS_OFF[1], 'N').lerp(REST['N'], win(f, (HS_OFF[1], HS_OFF[1] + 10)))
    if f < HS_GRAB[1]: return REST['N'].lerp(cup_grip(HS_ON[0], 'N'), win(f, HS_GRAB))
    if f < HS_ON[1]: return cup_grip(f, 'N')
    return cup_grip(HS_ON[1], 'N').lerp(REST['N'] + V(0.02, 0.02, -0.01), win(f, HANDS_DOWN))
HANDW = {'N': hand_N, 'P': hand_P}

for f in range(1, N + 1):
    doug_r.place(f, (SEATED.x, SEATED.y), 0.0)
    lean, roll, lift = posture(f); br = breath(f)
    arms = {s_: (tuple(to_local(HANDW[s_](f), f)), ('auto', ((-1 if s_ == 'N' else 1), 0.25, -0.5))) for s_ in ('N', 'P')}
    doug_r.pose(f, up=(0, 0, lift + br * 0.4), rot=(lean, roll, 0), sq=1 + br, arms=arms,
                legs={'N': ((-0.15, 0.0, 0), (0, -1, 0.2)), 'P': ((0.15, 0.0, 0), (0, -1, 0.2))})
    for s_ in ('N', 'P'):        # ep14 seated legs under the desk
        foot = SEATED + FOOT_L[s_] - SEATED; hip = V(0, 0, BASE + lift) + doug_r.hip_off[s_]
        doug_r.key_points(doug_r.leg[s_], f, (hip, KNEE_L[s_] - SEATED, foot))
        doug_r.foot[s_].location = foot + V(0, -0.035, 0.03); doug_r.foot[s_].keyframe_insert('location', frame=f)
    m = HS(f); hs.location = m.translation; hs.rotation_quaternion = m.to_quaternion()
    hs.keyframe_insert('location', frame=f); hs.keyframe_insert('rotation_quaternion', frame=f)
    m = pen_matrix(f, hand_P(f)); pen.location = m.translation; pen.rotation_quaternion = m.to_quaternion()
    pen.keyframe_insert('location', frame=f); pen.keyframe_insert('rotation_quaternion', frame=f)
    mouse.location = mouse_pos(f); mouse.keyframe_insert('location', frame=f)

# ============================================================ FACE: eyes, lids, brows, curve mouth (smile), lip-sync
D_LIDS = [o for o in bpy.data.objects if o.name.startswith('doug_lid')]
BZ = [b.location.z for b in doug['brows']]
mouth0 = doug['mouth']; mouth0.hide_render = True; mouth0.hide_viewport = True
mcu = bpy.data.curves.new('doug_mouth_c', 'CURVE'); mcu.dimensions = '3D'; mcu.bevel_depth = 0.016; mcu.bevel_resolution = 6; mcu.use_fill_caps = True
msp = mcu.splines.new('POLY'); msp.points.add(6)
mouth = link(bpy.data.objects.new('doug_mouth_c', mcu)); mouth.data.materials.append(M['mouth'])
mouth.parent = mouth0; mouth.matrix_parent_inverse = Matrix.Identity(4)
MX = [-0.036 + 0.012 * i for i in range(7)]
def mouth_shape(f, sm):
    for p, x in zip(msp.points, MX):
        u = x / 0.036; z = 0.02 * sm * (u * u - 0.35)
        p.co = (-z, 0.32 - math.sqrt(0.32 ** 2 - x * x), x, 1.0); p.keyframe_insert('co', frame=f)
# lids: focused -> tired -> relieved -> pleased -> (frozen) -> drained -> resigned -> blank
LID = [(1, 16), (TYPE[1], 16), (CLOCK_LOOK[1], 14), (RELAX[1], 24), (HS_OFF[1], 22), (M_F, 14), (M_F + 14, 10), (PEN_DROP + 6, 12),
       (CALL, 12), (CALL + 3, 4), (SH['C'][0], 4), (DRAIN[1], 18), (G_PEN[1], 22), (REACH[1], 26), (PEN_BACK[1], 26),
       (SINK[1], 28), (A_F, 28), (A_F + 20, 30), (MOUSE[1], 26), (LOOK_UP[0], 24), (N, 24)]
BLINKS = [(12, 2), (RELAX[0] + 3, 3), (M_F + 2, 3), (G_PEN[0] - 2, 3), (HS_ON[1] + 2, 4), (A_F + 4, 4)]   # none in the final stare
BROW = [(1, (-0.004, -2)), (TYPE[1], (-0.004, -2)), (RELAX[1], (0.008, 2)), (M_F + 10, (0.016, 4)), (PEN_DROP + 6, (0.014, 3)),
        (CALL, (0.014, 3)), (CALL + 3, (0.026, 6)), (SH['C'][0], (0.024, 5)), (DRAIN[1], (0.0, -2)), (SINK[1], (-0.008, -5)),
        (LOOK_UP[0], (-0.006, -4)), (N, (-0.006, -4))]
SMILE = [(1, 0.0), (RELAX[0], 0.0), (RELAX[1] + 4, 0.55), (M_F, 0.7), (M_F + 10, 1.0), (CALL, 1.0), (SH['C'][0] + 4, 1.0),
         (DRAIN[1], -0.05), (SINK[1], -0.35), (A_F + 30, -0.3), (LOOK_UP[0], 0.0), (N, 0.0)]
MOUTH_O = {}
def add_take(path, f0, breaths):
    a, sr = _sf.read(os.path.join(HERE, path)); hop = sr // 30
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)]); rms /= rms.max(); prev = 0.0
    for i, r_ in enumerate(rms):
        fr = f0 + i; t = i / 30; o = max(0.0, min(1.0, (r_ - 0.07) / 0.5)); o = o if o > prev else prev * 0.5 + o * 0.5; prev = o
        for (b0, b1, amp) in breaths:
            if b0 <= t <= b1: o = max(o, amp * math.sin(math.pi * (t - b0) / (b1 - b0)))
        MOUTH_O[fr] = max(MOUTH_O.get(fr, 0.0), o)
add_take('vo/m1.wav', M_F, [(0.0, 0.22, 0.10), (0.24, 0.42, 0.22)])      # breath in, a small pleased breath out
add_take('vo/a2.wav', A_F, [(0.0, 0.30, 0.10)])
def blink_amt(f):
    for b_, dur in BLINKS:
        if abs(f - b_) <= dur: return 1 - abs(f - b_) / (dur + 1)
    return 0.0
CAM_E = WEBCAM + (MON_M.to_3x3() @ V(0, 0.03, 0.0))
def pen_pt(f): return pen.matrix_world.translation.copy()
GAZE = [(1, DOC_W), (CLOCK_LOOK[0], DOC_W), (CLOCK_LOOK[0] + 5, CLOCK_W), (RELAX[1], CLOCK_W), (HS_OFF[0] + 4, V(0, -1.4, 1.35)),
        (HS_OFF[1] - 4, HS_DESK.translation), (PEN_PICK[0] + 2, PEN_HOME.translation), (PEN_PICK[1], V(-0.1, -1.6, 1.3)),
        (CALL - 1, V(-0.1, -1.6, 1.3)), (G_SCREEN[0], V(-0.1, -1.6, 1.3)), (G_SCREEN[1], CARD_W), (G_PEN[0], CARD_W),
        (G_PEN[1], PEN_LANDED.translation), (G_BACK[0], PEN_LANDED.translation), (G_BACK[1], CARD_W), (REACH[0] + 6, CARD_W),
        (REACH[1] - 4, PEN_LANDED.translation), (PEN_BACK[1], PEN_HOME.translation), (HS_GRAB[0] + 2, HS_DESK.translation),
        (HS_ON[0] + 6, V(0, -1.4, 1.2)), (HANDS_DOWN[0], CARD_W), (MOUSE[1], CARD_W), (CURSOR[1], ACC_W), (LOOK_UP[0], ACC_W),
        (LOOK_UP[1], CAM_E), (N, CAM_E)]
for f in range(1, N + 1):
    scene.frame_set(f)
    T_ = ease_tab(GAZE, f)
    for pv in doug['eyes']:
        P = pv.matrix_world.translation; Rp = pv.parent.matrix_world.to_3x3().normalized()
        d = Rp.inverted() @ (T_ - P)
        yaw = math.degrees(math.atan2(d.x, -d.y)); pt = -math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
        pv.rotation_euler = (D(max(-36, min(48, pt))), 0, D(max(-40, min(40, yaw)))); pv.keyframe_insert('rotation_euler', frame=f)
    lv = ease_tab(LID, f); lv = lv + (95 - lv) * blink_amt(f)
    for o in D_LIDS: o.rotation_euler = (D(min(98, lv)), 0, 0); o.keyframe_insert('rotation_euler', frame=f)
    dz, tl_ = ease_tab(BROW, f)
    for i, bp in enumerate(doug['brows']):
        sx = -1 if i == 0 else 1
        bp.location.z = BZ[i] + dz; bp.keyframe_insert('location', frame=f)
        bp.rotation_euler = (0, sx * D(-6 + tl_), 0); bp.keyframe_insert('rotation_euler', frame=f)
    sm = ease_tab(SMILE, f); mouth_shape(f, sm)
    o = MOUTH_O.get(f, 0.0)
    mouth.scale = (1 + 2.3 * o, 1, (1 - 0.08 * abs(sm)) * (1 + 0.12 * o)); mouth.keyframe_insert('scale', frame=f)

# ============================================================ CAMERAS
EYE = lambda f: upper_matrix(f) @ V(0, -0.2, doug_r.ez - 0.05)
def envcam(name, d):
    if os.environ.get(name):
        v = [float(x) for x in os.environ[name].split(',')]; return V(*v[:3]), V(*v[3:6]), v[6]
    return d
def cam_for(f):
    """-> (location, target, lens, fstop, focus)"""
    if f <= SH['A'][1] or SH['B'][0] <= f <= SH['B'][1]:     # medium, front-left 3/4: his face, hands, headset, pen (monitor from the side)
        p, t, l = envcam('CAM_A', (V(0.80, -1.32, 1.50), V(0.05, -0.32, 1.20), 22))
        k = smooth((f - 1) / 104); return p.lerp(p + V(-0.02, 0.03, -0.01), k), t, l, 5.6, EYE(f)
    if f <= SH['S'][1]:        # the screen (the clock insert I, and S)
        p, t, l = envcam('CAM_S', (MON_M @ V(0.0, 0.56, 0.07), MON_M @ V(0, 0, -0.005), 30))
        return p, t, l, 11.0, V(MON.x, MON.y, MON.z)
    if f <= SH['C'][1]:        # medium close-up, front-right (from between him and the monitor)
        p, t, l = envcam('CAM_C', (V(0.64, -1.02, 1.46), V(0.02, -0.16, 1.26), 22))
        k = smooth((f - SH['C'][0]) / 89); return p.lerp(p + V(0.01, 0.025, 0), k), t, l, 4.0, EYE(f)
    if f <= SH['D'][1]:        # medium, from his right: Doug, headset, the screen (cursor)
        p, t, l = envcam('CAM_D', (V(1.28, -0.70, 1.72), V(-0.10, -0.40, 1.12), 18))
        return p, t, l, 5.6, EYE(f)
    p, t, l = envcam('CAM_E', (CAM_E, V(0, 0.05, 1.54), 20))   # the webcam's view: tight on his face
    return p, t, l, 4.0, EYE(f)
def cam_setup(name):
    a_, b_ = SH[name]
    for f in range(a_, b_ + 1):
        p, tgt, lens, fs, fp = cam_for(f)
        key(cam, 'location', f, p); key(target, 'location', f, tgt); key(focus, 'location', f, fp)
        key(cam_data, 'lens', f, lens); key(cam_data.dof, 'aperture_fstop', f, fs)

if SHOT == 'QA':
    for f in (10, 48, 60, 75, 90, 104, 110, 230, 250, 270, 290, 300, 330, 370):
        scene.frame_set(f)
        sh = {s: (upper_matrix(f) @ doug_r.shoulder(s)) for s in ('N', 'P')}
        hw = {s: doug_r.hand[s].matrix_world.translation for s in ('N', 'P')}
        print(f, 'reach N %.2f P %.2f' % ((hw['N'] - sh['N']).length, (hw['P'] - sh['P']).length),
              'pen', tuple(round(x, 3) for x in pen.matrix_world.translation), 'hs', tuple(round(x, 3) for x in hs.matrix_world.translation))
    sys.exit(0)
if SHOT == 'SIDE':
    SH['SIDE'] = (1, N)
    for f in range(1, N + 1):
        key(cam, 'location', f, V(2.2, -0.45, 1.1)); key(target, 'location', f, V(0.0, -0.45, 1.0)); key(focus, 'location', f, V(0, -0.4, 1.0))
        key(cam_data, 'lens', f, 24); key(cam_data.dof, 'aperture_fstop', f, 16.0)
else:
    cam_setup(SHOT)
f0, f1 = SH[SHOT]; scene.frame_set(f0)
cam_data.clip_start = 0.01
FR = FR or f'{f0}-{f1}'
render(N)
