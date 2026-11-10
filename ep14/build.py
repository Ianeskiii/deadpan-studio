"""Tube Town - When you accidentally open the front camera.
usage: cd ep14 && python3 build.py SHOT OUTDIR [opts]
  SHOT = A B C D E F   (film shots)
       | SEL           (the phone's front camera: what the screen shows; render before screen.py)
       | SIM           (bake the blanket cloth to blanket.pc2; run once before the film shots)
       | QA            (print beats, write beats.json)
Pipeline: build.py QA -> build.py SIM -> render SEL -> screen.py -> render A..F -> audio.py -> assemble.py
"""
import os, sys, json, struct
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
from mathutils import Matrix, Quaternion
def V(*a): return Vector(a)
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
FPS = 30

# ============================================================ BEATS (frames, 30 fps)
B = dict(
    A=(1, 40),          # medium: scrolling on the couch
    B=(41, 110),        # POV close-up of the phone: feed -> accidental tap on the camera icon -> front camera (he keeps swiping, unaware)
    C=(111, 180),       # reaction close-up: eyes slowly widen, drift off, one blink, back to the screen
    D=(181, 216),       # v2 final: three-quarter medium - he physically raises the phone from chest to eye level
    DP=(217, 300),      # v2 final: his POV - the normal angle, then a slow lower (phone sinks in frame), the bad angle returns, pause
    E=(301, 335),       # close-up: silent disappointment
    F=(336, 465),       # wide: screen off, phone face down, stillness, blanket over the head, hold
)
N = 474                 # 466-474 black
SWIPES = [8, 22, 50]
TAP_CAM = 66            # accidental tap: his thumb comes down for the next swipe and lands on the camera icon
CAM_ON = 69             # camera app opens (activation sound)
SWIPE_CAM = 80          # one more lazy swipe on the camera view: nothing scrolls (he hasn't noticed yet)
TAP_OFF = 342           # screen off
SCREEN_OFF = 343
PUT_DOWN = 370          # phone lands face down on the cushion
GRAB = 408              # hands take the blanket off the couch back
COVERED = 434           # blanket is over his head
F_BLACK = 466

# ============================================================ LIVING ROOM (evening, lamp-lit; TV off)
tina['root'].location = (-80, 0, 0)
for o in list(bpy.data.objects):
    if o.name.startswith(('phone', 'screen')) and o.parent and o.parent.name.startswith('tina'): o.hide_render = True
R_ = dict(
    floor=brick_mat('planks2', hexc('#6b4a33'), hexc('#5f412c'), hexc('#3f2a1c'), 1.2, 1.6, 0.18, 0.37, 0.55),
    wall=mat('lr_wall', hexc('#55687c'), 0.9), wall2=mat('lr_wall2', hexc('#465668'), 0.9),
    couch=mat('couch', hexc('#5a6e5a'), 0.85, 0.0, sheen=0.5), cushion=mat('cushion', hexc('#667d66'), 0.85, 0.0, sheen=0.5),
    wood=mat('lr_wood', hexc('#4a3426'), 0.5, 0.2), black=mat('tvblack', hexc('#111214'), 0.3, 0.4),
    rug=mat('rug', hexc('#7a4d4a'), 0.95), can=mat('can', hexc('#c0392b'), 0.25, 0.7), night=mat('night', (0, 0, 0), 0.5, 0, hexc('#2b3f78'), 0.6),
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
COUCH = [box('couch_base', (2.0, 0.85, SEAT - 0.12), (0, 0.15, (SEAT - 0.12) / 2), R_['couch'], 0.04)]
for cx in (-0.48, 0.48): COUCH.append(box('seat_cushion', (0.94, 0.8, 0.13), (cx, 0.12, SEAT - 0.065), R_['cushion'], 0.05))
COUCH.append(box('couch_back', (2.0, 0.24, 0.62), (0, 0.5, SEAT + 0.22), R_['couch'], 0.08))
for cx in (-0.98, 0.98): COUCH.append(box('arm_rest', (0.24, 0.9, 0.55), (cx, 0.15, 0.36), R_['couch'], 0.08))
TVW, TVH, TVZ, TVY = 1.72, 0.97, 1.12, -1.95
box('cabinet', (2.1, 0.45, 0.5), (0, TVY + 0.02, 0.25), R_['wood'], 0.02)
box('tv_body', (TVW + 0.06, 0.06, TVH + 0.06), (0, TVY, TVZ), R_['black'], 0.01)
box('tv_foot', (0.5, 0.25, 0.04), (0, TVY + 0.02, 0.52), R_['black'])
box('coffee_table', (0.9, 0.5, 0.05), (0.15, -0.95, 0.38), R_['wood'], 0.01)
for lx in (-0.25, 0.55):
    for ly in (-1.15, -0.75): box('ct_leg', (0.04, 0.04, 0.36), (lx, ly, 0.18), R_['wood'])
cyl('soda', 0.033, 0.12, (0.45, -0.9, 0.465), R_['can'])
box('remote', (0.05, 0.17, 0.02), (-0.1, -0.88, 0.415), R_['black'], 0.006).rotation_euler = (0, 0, D(20))
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
aimed_area('key', (1.1, -1.4, 2.5), (0, 0, 1.2), 140, hexc('#ffe0b8'), (1.2, 1.2))
aimed_area('fill', (-1.6, -1.2, 1.5), (0, 0, 1.1), 35, hexc('#b8c8ff'), (1.0, 1.0))
aimed_area('rim', (-1.2, 1.2, 2.2), (0, 0, 1.3), 70, hexc('#8fa6ff'), (1.0, 1.0))

# ============================================================ DOUG on the couch
exec(open(os.path.join(HERE, '..', 'ep12', 'rig.py')).read())
doug['mouth'].location.y = -0.326
doug_r = Rig(doug, 'doug', M['doug'], M['doug'], lift=0.17)
SIT_LEGS = {'N': ((-0.17, -0.42, 0.0), (0, -1, 0.9)), 'P': ((0.17, -0.42, 0.0), (0, -1, 0.9))}
# v2: real sitting legs. Thigh lies on the seat cushion (above its top at z=SEAT), knee just past the cushion's front edge,
# shin hangs straight down in front of the couch base, foot flat on the rug. (root-local coords; root is at ROOT)
# v2 final: the knee sits 0.50 in front of the hip (v2 WIP had 0.40, so the whole thigh was inside his belly and the shins
# looked like they hung from his stomach). Now the thigh runs visibly along the cushion top, the knee clears the cushion's
# front edge (y=-0.28 world) by 0.17, the shin drops plumb in front of the couch base with 0.12 clearance, feet flat on the rug.
KNEE_L = {'N': V(-0.17, -0.50, SEAT + 0.075), 'P': V(0.17, -0.50, SEAT + 0.075)}
FOOT_L = {'N': V(-0.19, -0.51, 0.03), 'P': V(0.19, -0.51, 0.03)}
ROOT = V(0, 0.05, 0)
doug_r.place(1, (ROOT.x, ROOT.y), 0)
UP0 = V(0, 0, doug_r.base)
def to_local(w, up=V(0, 0, 0)): return V(*w) - ROOT - UP0 - up       # upper body never rotates in this short
def to_world(l, up=V(0, 0, 0)): return V(*l) + ROOT + UP0 + up
LAP = {'N': V(-0.19, -0.42, 0.19), 'P': V(0.19, -0.42, 0.19)}       # hands resting on top of the (now visible) thighs
scene.frame_set(1)
EYE_C = sum((e.matrix_world.translation for e in doug['eyes']), Vector()) / 2

# ============================================================ PHONE (unparented; world pose keyed every frame)
def aim_quat(p, tgt):
    ly = -(V(*tgt) - V(*p)).normalized()               # phone back (+Y local) points away from the face
    up = V(0, 0, 1); lz = (up - ly * up.dot(ly)).normalized(); lx = ly.cross(lz)
    return Matrix((lx, ly, lz)).transposed().to_quaternion()
LOW = (V(0.05, -0.56, 0.96), None)
HIGH = (V(0.12, -0.80, 1.48), None)      # v2 final: true eye level (eyes at z 1.456), a little to his right so it clears his face
LOW = (LOW[0], aim_quat(LOW[0], EYE_C)); HIGH = (HIGH[0], aim_quat(HIGH[0], EYE_C))
MIDP = V(0.46, -0.38, 0.72)
SEATP = V(0.62, -0.06, SEAT + 0.007)
SEATQ = Matrix(((-1, 0, 0), (0, 0, 1), (0, 1, 0))).transposed().to_quaternion()   # columns lx=-X, ly=+Z (back up), lz=+Y
MIDQ = LOW[1].slerp(SEATQ, 0.6)
RAISE, LOWER = (190, 212), (238, 268)     # v2 final: one clear comparison (v1 did it twice): raise, hold, slow lower, pause
PH_KEYS = [(1, LOW), (RAISE[0], LOW), (RAISE[1], HIGH), (LOWER[0], HIGH), (LOWER[1], LOW),
           (346, LOW), (362, (MIDP, MIDQ)), (PUT_DOWN, (SEATP, SEATQ)), (N, (SEATP, SEATQ))]
def phone_pose(f):
    for (fa, (pa, qa)), (fb, (pb, qb)) in zip(PH_KEYS, PH_KEYS[1:]):
        if fa <= f <= fb:
            t = smooth((f - fa) / max(1, fb - fa))
            p = pa.lerp(pb, t); q = qa.slerp(qb, t)
            if f < RAISE[0]:      # small idle drift while scrolling / staring
                p = p + V(0.004 * math.sin(f * 0.07), 0, 0.005 * math.sin(f * 0.05 + 1))
            return p, q
    return PH_KEYS[-1][1]
def PM(f):
    p, q = phone_pose(f); m = q.to_matrix().to_4x4(); m.translation = p; return m
PHW, PHT, PHH = 0.12, 0.014, 0.24
phone = box('phone_body', (PHW, PHT, PHH), (0, 0, 0), M['phone'], 0.008)
phone.rotation_mode = 'QUATERNION'
cam_bump = cyl('phone_lens', 0.009, 0.004, (0.035, PHT / 2 + 0.001, 0.095), mat('lens', hexc('#08080a'), 0.1, 0.8), rot=(D(90), 0, 0), verts=24, parent=phone)
SCR_DIR = os.path.join(HERE, 'screen')
NSCR = len([f for f in os.listdir(SCR_DIR) if f.endswith('.png')]) if os.path.isdir(SCR_DIR) else 0
scr_m = bpy.data.materials.new('phone_screen'); scr_m.use_nodes = True; nt = scr_m.node_tree; nt.nodes.clear()
em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.6
out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
if NSCR and SHOT not in ('SEL', 'SIM'):
    img = bpy.data.images.load(os.path.join(SCR_DIR, 'sc_0001.png')); img.source = 'SEQUENCE'
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.image_user.frame_duration = NSCR; tex.image_user.frame_start = 1
    tex.image_user.frame_offset = 0; tex.image_user.use_auto_refresh = True; tex.extension = 'CLIP'
    nt.links.new(tex.outputs['Color'], em.inputs['Color'])
else:
    em.inputs['Color'].default_value = (0.7, 0.8, 0.9, 1)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -PHT / 2 - 0.0008, 0.0))
scr = bpy.context.active_object; scr.name = 'phone_screen'; scr.scale = (0.108, 0.222, 1); scr.rotation_euler = (D(90), 0, 0)
scr.data.materials.append(scr_m); scr.parent = phone
# the screen lights his face: area light on the screen, facing out of it
gl = bpy.data.lights.new('phone_glow', 'AREA'); gl.shape = 'RECTANGLE'; gl.size = 0.108; gl.size_y = 0.222
glo = link(bpy.data.objects.new('phone_glow', gl)); glo.parent = phone; glo.location = (0, -0.02, 0); glo.rotation_euler = (D(-90), 0, 0)
glo.visible_camera = False
for f in range(1, N + 1):
    m_ = PM(f); phone.location = m_.translation; phone.rotation_quaternion = m_.to_quaternion()
    phone.keyframe_insert('location', frame=f); phone.keyframe_insert('rotation_quaternion', frame=f)
    if f < CAM_ON: col, en = (0.92, 0.95, 1.0), 2.2           # bright white feed
    elif f < SCREEN_OFF: col, en = (1.0, 0.93, 0.8), 1.6      # camera view (mostly his own yellow face)
    else: col, en = (1, 1, 1), 0.0
    gl.color = col; gl.energy = en; gl.keyframe_insert('color', frame=f); gl.keyframe_insert('energy', frame=f)

# ============================================================ BODY + HANDS
def hold_P(f): return PM(f) @ V(0.03, 0.02, -0.182)          # right fist under the bottom edge (v2: lower, so the screen's bottom bar shows)
def cradle_N(f): return PM(f) @ V(-0.05, 0.025, -0.186)       # left hand also under the bottom edge
ICON = V(-0.043, 0, -0.101)                                   # camera shortcut on the screen (screen.py: x=44, y=H-38)
def tap_N(f, depth): return PM(f) @ (ICON + V(-0.004, -0.062 - 0.05 * depth, -0.012))
def swipe_N(f, f0):
    t = (f - f0) / 6.0; return PM(f) @ V(-0.03, -0.062, -0.05 + 0.06 * smooth(t))
def mix(a, b, t): t = smooth(t); return a.lerp(b, t)
GRAB_W = {'N': V(-0.30, 0.43, 1.0), 'P': V(0.30, 0.43, 1.0)}
def blanket_hand(side, f):
    sx = -1 if side == 'N' else 1
    path = [(398, to_world(LAP[side])), (403, V(sx * 0.36, 0.12, 1.2)), (GRAB, GRAB_W[side]), (416, V(sx * 0.3, 0.6, 1.95)), (421, V(sx * 0.28, 0.0, 2.15)),
            (426, V(sx * 0.26, -0.52, 1.75)), (COVERED, V(sx * 0.22, -0.48, 1.15))]
    if f <= path[0][0]: return path[0][1]
    for (fa, pa), (fb, pb) in zip(path, path[1:]):
        if fa <= f <= fb: return mix(pa, pb, (f - fa) / max(1, fb - fa))
    return path[-1][1]
def hand_world(side, f):
    if side == 'P':
        if f < PUT_DOWN + 2: return hold_P(f)
        if f < 398:
            a = hold_P(PUT_DOWN + 2); b = to_world(LAP['P']); t = (f - PUT_DOWN - 2) / 12
            return mix(a, b, t) + V(0, 0, 0.08 * math.sin(math.pi * min(1, max(0, t))))
        return blanket_hand('P', f)
    # left hand
    if f < 181:
        for s in SWIPES + [SWIPE_CAM]:
            if s - 4 <= f < s: return mix(cradle_N(f), tap_N(f, 0.5), (f - s + 4) / 4)
            if s <= f < s + 6: return swipe_N(f, s)
            if s + 6 <= f < s + 11: return mix(swipe_N(f, s + 6 - 6), cradle_N(f), (f - s - 6) / 5)
        if TAP_CAM - 6 <= f <= TAP_CAM: return mix(cradle_N(f), tap_N(f, 0.0), (f - TAP_CAM + 6) / 6)
        if TAP_CAM < f <= TAP_CAM + 2: return tap_N(f, 0.0)
        if TAP_CAM + 2 < f <= TAP_CAM + 8: return mix(tap_N(f, 0.0), cradle_N(f), (f - TAP_CAM - 2) / 6)
        return cradle_N(f)
    if f < 190: return mix(cradle_N(f), to_world(LAP['N']), (f - 181) / 9)
    if f < TAP_OFF - 5: return to_world(LAP['N'])
    if f <= TAP_OFF: return mix(to_world(LAP['N']), tap_N(f, 0.0), (f - TAP_OFF + 5) / 5)
    if f < 398: return mix(tap_N(f, 0.0), to_world(LAP['N']), (f - TAP_OFF) / 8)
    return blanket_hand('N', f)
def up_of(f):
    if 301 <= f: return V(0, 0, -0.015 * smooth((f - 303) / 20))     # a small sink with the disappointment
    return V(0, 0, 0)
def bend_of(side, f):
    sx = -1 if side == 'N' else 1
    if f >= 398: return ('auto', (sx * 1, 0.2, -0.6))
    return ('auto', (sx * 1, 0.1, -0.5))
for f in range(1, N + 1):
    up = up_of(f)
    arms = {s: (tuple(to_local(hand_world(s, f), up)), bend_of(s, f)) for s in ('N', 'P')}
    doug_r.pose(f, up=tuple(up), rot=(0, 0, 0), arms=arms, legs=SIT_LEGS)
    for s_ in ('N', 'P'):      # v2: override the rig's straight leg with the seated hip -> knee -> foot
        hip = V(0, 0, doug_r.base) + up + doug_r.hip_off[s_]
        doug_r.key_points(doug_r.leg[s_], f, (hip, KNEE_L[s_], FOOT_L[s_]))
        doug_r.foot[s_].location = FOOT_L[s_] + V(0, -0.035, 0.03); doug_r.foot[s_].keyframe_insert('location', frame=f)

# ============================================================ EYES + LIDS
D_LIDS = [o for o in bpy.data.objects if o.name.startswith('doug_lid')]
AWAY = V(0.0, -2.0, 1.75)
SACC = [(1, (0.0, 0.03)), (14, (-0.02, -0.01)), (27, (0.015, 0.035)), (44, (-0.01, 0.0)), (56, (0.02, 0.03)), (72, (-0.015, -0.03)),
        (90, (0.0, 0.01)), (122, (0.015, 0.03)), (131, (-0.015, 0.025)), (140, (0.0, 0.0)), (176, (0.0, 0.0)),
        (305, (0.0, 0.0)), (313, (0.012, 0.0)), (322, (-0.008, -0.01)), (N, (-0.008, -0.01))]
def sacc(f):      # small eye movements over the phone (reading the feed, then checking the image), 3-frame moves
    prev = SACC[0][1]
    for (fa, a), (fb, b) in zip(SACC, SACC[1:]):
        if fa <= f < fb:
            t = smooth((f - fa) / 3.0); return V(prev[0] + (a[0] - prev[0]) * t, 0, prev[1] + (a[1] - prev[1]) * t)
        prev = a
    return V(0, 0, 0)
def look_target(f):
    sc = PM(f) @ (V(0, -0.007, 0) + sacc(f))
    if 150 <= f < 170:
        return sc.lerp(AWAY, smooth((f - 150) / 6)) if f < 160 else AWAY.lerp(sc, smooth((f - 165) / 5))
    if f >= 374: return sc.lerp(V(0.0, -2.0, 1.45), smooth((f - 374) / 6))
    return sc
BLINKS = [(30, 3), (160, 3), (226, 3)]          # one content blink while the angle is good
def blink_amt(f):
    for b_, dur in BLINKS:
        if abs(f - b_) <= dur: return 1 - abs(f - b_) / (dur + 1)
    return 0.0
LID_KEYS = [(1, 23), (114, 23), (124, 30), (132, 30), (150, -26), (192, -26), (212, 6), (238, 8), (258, -4), (268, -16), (282, -12),
            (300, -8), (305, -8), (322, 32), (N, 32)]      # v2 final: wide (low) -> relaxed (eye level) -> wide again as it sinks -> settles
def lid_of(f):
    for (fa, a), (fb, b) in zip(LID_KEYS, LID_KEYS[1:]):
        if fa <= f <= fb: return a + (b - a) * smooth((f - fa) / max(1, fb - fa))
    return LID_KEYS[-1][1]
EYE_LOG = {}
for f in range(1, N + 1):
    scene.frame_set(f)
    T_ = look_target(f)
    for pv in doug['eyes']:
        P = pv.matrix_world.translation; Rp = pv.parent.matrix_world.to_3x3().normalized()
        d = Rp.inverted() @ (T_ - P)
        yaw = math.degrees(math.atan2(d.x, -d.y)); pitch_ = -math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
        yaw = max(-40, min(40, yaw)); pitch_ = max(-36, min(52, pitch_))
        pv.rotation_euler = (D(pitch_), 0, D(yaw)); pv.keyframe_insert('rotation_euler', frame=f)
    EYE_LOG[f] = round(pitch_, 1)
    lv = lid_of(f); lv = lv + (95 - lv) * blink_amt(f)
    for o in D_LIDS: o.rotation_euler = (D(lv), 0, 0); o.keyframe_insert('rotation_euler', frame=f)

# ============================================================ BLANKET (draped over the couch back; cloth baked to blanket.pc2)
BW, BL = 1.4, 2.2
NX, NY = 36, 56
bpy.ops.mesh.primitive_grid_add(x_subdivisions=NX, y_subdivisions=NY, size=1, location=(0, 0, 0))
blanket = bpy.context.active_object; blanket.name = 'blanket'
TOP_Y0, TOP_Y1, TOP_Z, REAR_Y = 0.40, 0.645, 0.965, 0.648
def drape(u, v):           # u in [-0.5,0.5] across, v in [0,1] from the front edge
    x = u * BW; s = v * BL
    if s <= TOP_Y1 - TOP_Y0: return V(x, TOP_Y0 + s, TOP_Z)
    s -= TOP_Y1 - TOP_Y0
    if s <= TOP_Z - 0.006: return V(x, REAR_Y, TOP_Z - s)
    s -= TOP_Z - 0.006
    return V(x, REAR_Y + s, 0.006)
_co = np.zeros(len(blanket.data.vertices) * 3, dtype=np.float32); blanket.data.vertices.foreach_get('co', _co); _co = _co.reshape(-1, 3)
REST = [tuple(drape(c[0], c[1] + 0.5)) for c in _co]
blanket.data.vertices.foreach_set('co', np.array(REST, dtype=np.float32).ravel()); blanket.data.update()
pin = blanket.vertex_groups.new(name='pin')
PIN = {s: [i for i, c in enumerate(REST) if (V(*c) - (GRAB_W[s] - V(0, 0.03, 0.035))).length < 0.075 and c[1] < 0.46] for s in ('N', 'P')}
for s in PIN: pin.add(PIN[s], 1.0, 'REPLACE')
bmat = bpy.data.materials.new('blanket'); bmat.use_nodes = True; bn = bmat.node_tree.nodes; bl_ = bmat.node_tree.links
bsdf = bn['Principled BSDF']; bsdf.inputs['Roughness'].default_value = 0.95; bsdf.inputs['Sheen Weight'].default_value = 0.8
ck = bn.new('ShaderNodeTexChecker'); ck.inputs['Scale'].default_value = 7
ck.inputs['Color1'].default_value = (*hexc('#4f7cac'), 1); ck.inputs['Color2'].default_value = (*hexc('#a9c1d9'), 1)
uvn = bn.new('ShaderNodeTexCoord'); bl_.new(uvn.outputs['UV'], ck.inputs['Vector']); bl_.new(ck.outputs['Color'], bsdf.inputs['Base Color'])
blanket.data.materials.append(bmat)
for p in blanket.data.polygons: p.use_smooth = True
PC2 = os.path.join(HERE, 'blanket.pc2')
def hand_track(side, f):
    if f < GRAB: return GRAB_W[side] - V(0, 0.03, 0.035)
    sx = -1 if side == 'N' else 1
    return hand_world(side, f) + V(sx * 0.02, 0.0, -0.01)
if SHOT == 'SIM':
    HOOKS = {}
    for s in ('N', 'P'):
        e = empty('hook_' + s, tuple(hand_track(s, 1)))
        for f in range(1, N + 1): key(e, 'location', f, tuple(hand_track(s, f)))
        hk = blanket.modifiers.new('hook_' + s, 'HOOK'); hk.object = e; hk.vertex_indices_set(PIN[s])
        scene.frame_set(1); hk.matrix_inverse = e.matrix_world.inverted(); HOOKS[s] = e
    cl = blanket.modifiers.new('cloth', 'CLOTH'); cs = cl.settings
    cs.quality = 8; cs.mass = 0.25; cs.tension_stiffness = 12; cs.compression_stiffness = 12; cs.shear_stiffness = 6
    cs.bending_stiffness = 0.4; cs.air_damping = 1.5; cs.vertex_group_mass = 'pin'; cs.pin_stiffness = 1.0
    cl.collision_settings.distance_min = 0.012; cl.collision_settings.collision_quality = 4
    cl.collision_settings.use_self_collision = False
    cl.point_cache.frame_start = 1; cl.point_cache.frame_end = N
    def collider(o, outer=0.01):
        c = o.modifiers.new('col', 'COLLISION'); o.collision.thickness_outer = outer; o.collision.cloth_friction = 25
    for o in COUCH: collider(o)
    collider(bpy.data.objects['lr_floor'])
    # Doug proxies (not rendered): body with eyes, hat crown, hat brim
    up_ = doug_r.upper
    prox = [capsule('px_body', 0.355, 0.62, M['doug'], (0, 0, doug['zc'] - 0.25), parent=up_, seg=32)]
    prox.append(cyl('px_crown', 0.36, 0.3, (0, 0, doug['top'] - 0.25 - 0.1 + 0.12), M['hat'], verts=32, parent=up_))
    prox.append(cyl('px_brim', 0.49, 0.05, (0, 0, doug['top'] - 0.25 - 0.1 - 0.05), M['hat'], verts=48, parent=up_))
    for o in prox: collider(o, 0.015); o.hide_render = True
    frames = []
    for f in range(1, N + 1):
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get(); ev = blanket.evaluated_get(dg); me = ev.to_mesh()
        frames.append(np.array([tuple(v.co) for v in me.vertices], dtype=np.float32)); ev.to_mesh_clear()
        if f % 50 == 0: print('sim', f, flush=True)
    SETTLE = 60
    for f in range(SETTLE - 1): frames[f] = frames[SETTLE - 1]
    with open(PC2, 'wb') as fh:
        fh.write(struct.pack('<12siiffi', b'POINTCACHE2\0', 1, len(REST), 1.0, 1.0, N))
        for a in frames: fh.write(a.astype('<f4').tobytes())
    print('SIM written', PC2, len(REST), 'verts', N, 'frames; pins', {k: len(v) for k, v in PIN.items()})
    sys.exit(0)
if os.path.exists(PC2):
    mc = blanket.modifiers.new('cache', 'MESH_CACHE'); mc.cache_format = 'PC2'; mc.filepath = PC2
    mc.play_mode = 'SCENE'; mc.frame_start = 0.0; mc.frame_scale = 1.0
sub = blanket.modifiers.new('sub', 'SUBSURF'); sub.levels = 1; sub.render_levels = 1
sol = blanket.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = 0.014; sol.offset = 1.0

# ============================================================ SELFIE CAMERA (the phone's front camera)
def selfie_cam(f):
    m_ = PM(f); R = m_.to_3x3()
    lx, ly, lz = R.col[0], R.col[1], R.col[2]
    loc = m_ @ V(0.0, -0.01, 0.1)
    rot = Matrix((-lx, lz, ly)).transposed().to_euler()
    return loc, rot

# ============================================================ CAMERAS
SC = lambda f: PM(f) @ V(0, -0.007, 0)
D_CAM = (V(-0.7, -1.65, 1.3), V(0.07, -0.4, 1.22), 27, 5.6, EYE_C + V(0, 0, -0.06))   # from his left: face, mouth and the whole arm move stay clear
FACE = EYE_C + V(0, 0, -0.06)
def cam_for(f):
    """-> (location, target, lens, fstop, focus point)"""
    if SHOT == 'S': return V(2.3, -0.30, 0.78), V(0.0, -0.22, 0.62), 38, 16.0, V(0, -0.2, 0.6)
    if f <= B['A'][1]:
        t = (f - 1) / 40
        return V(0.3, -1.75, 1.42).lerp(V(0.27, -1.62, 1.4), t), V(0.03, -0.25, 1.17), 30, 4.0, FACE
    if f <= B['B'][1]:      # his point of view
        t = smooth((f - 41) / 69)      # v2: a little wider and lower in frame, so the whole screen (bottom bar too) clears the title
        s = SC(f); return V(0.0, -0.335, 1.43), s + V(0, 0, 0.03 - 0.008 * t), 54 + 4 * t, 5.6, s
    if f <= B['C'][1]:      # reaction, from just past the phone
        t = smooth((f - 111) / 69)
        return V(0.24, -1.15, 1.2).lerp(V(0.2, -1.05, 1.22), t), FACE + V(0, 0, 0.1), 38, 4.0, FACE
    if f <= B['D'][1]:      # v2 final: fixed three-quarter medium, the raise is a visible arm move (v1 hid it in a POV that followed the phone)
        if os.environ.get('DCAM'):                                    # QA: try framings
            v = [float(x) for x in os.environ['DCAM'].split(',')]; return V(*v[:3]), V(*v[3:6]), v[6], 5.6, FACE
        return D_CAM
    if f <= B['DP'][1]:     # his POV; the camera follows the phone only 80%, so as he lowers it the phone sinks in frame
        s = SC(f); return V(0.0, -0.335, 1.43), s.lerp(SC(RAISE[1] + 6), 0.2), 40, 5.6, s
    if f <= B['E'][1]:
        t = smooth((f - 301) / 34)
        return V(0.2, -1.1, 1.22).lerp(V(0.16, -1.0, 1.25), t), FACE + V(0, 0, 0.1), 36, 4.0, FACE
    t = smooth((f - 336) / 129)
    return V(0.55, -1.78, 1.25).lerp(V(0.5, -1.7, 1.24), t), V(0.12, 0.0, 1.0), 24, 6.0, V(0.1, -0.1, 1.1)
if SHOT == 'S': B['S'] = (1, N)     # QA only: profile view of the seated pose
def cam_setup(name):
    a_, b_ = B[name]
    for f in range(a_, b_ + 1):
        p, tgt, lens, fs, fp = cam_for(f)
        key(cam, 'location', f, p); key(target, 'location', f, tgt); key(focus, 'location', f, fp)
        key(cam_data, 'lens', f, lens); key(cam_data.dof, 'aperture_fstop', f, fs)

if SHOT == 'QA':
    print('EYE_C', tuple(round(x, 3) for x in EYE_C), 'pins', {k: len(v) for k, v in PIN.items()})
    print('eye pitch LOW', EYE_LOG[100], 'HIGH', EYE_LOG[225])
    for f in (20, 200, 225, 290, 380, 440):   # leg/couch clearances (world): shin back vs couch front, foot bottom vs rug, knee vs cushion edge
        sh = to_world(FOOT_L['N']) - ROOT - UP0
        kn = KNEE_L['N'] + ROOT; ft = FOOT_L['N'] + ROOT
        print(f, 'knee y', round(kn.y, 3), 'z', round(kn.z, 3), '| shin back y', round(max(kn.y, ft.y) + 0.055, 3), 'vs couch front', -0.275,
              '| foot bottom z', round(ft.z + 0.03 - 0.078 * 0.55, 3), 'vs rug', 0.012)
    json.dump({'SHOTS': B, 'N': N, 'CAM_ON': CAM_ON, 'SWIPES': SWIPES, 'SWIPE_CAM': SWIPE_CAM, 'TAP_CAM': TAP_CAM, 'TAP_OFF': TAP_OFF, 'SCREEN_OFF': SCREEN_OFF,
               'PUT_DOWN': PUT_DOWN, 'GRAB': GRAB, 'COVERED': COVERED, 'F_BLACK': F_BLACK,
               'RAISE': [list(RAISE)], 'LOWER': [list(LOWER)]},
              open(os.path.join(HERE, 'beats.json'), 'w'), indent=1)
    sys.exit(0)
if SHOT == 'SEL':
    for o in (phone, scr, cam_bump, doug_r.hand['P'], doug_r.arm['P'], JOINTS[doug_r.arm['P'].name]): o.hide_render = True
    glo.hide_render = False
    tc.mute = True; cam.constraints.remove(tc)
    cam_data.dof.use_dof = False; cam_data.lens = 15; cam_data.clip_start = 0.01
    for f in range(1, N + 1):
        loc, rot = selfie_cam(f); key(cam, 'location', f, loc); key(cam, 'rotation_euler', f, rot)
    FR = FR or f'{CAM_ON}-{SCREEN_OFF}'
    render(N)
else:
    cam_setup(SHOT); f0, f1 = B[SHOT]; scene.frame_set(f0)
    cam_data.clip_start = 0.02
    FR = FR or f'{f0}-{f1}'
    render(N)
