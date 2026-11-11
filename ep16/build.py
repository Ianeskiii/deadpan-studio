"""Tube Town - When you finally have free time to play games.   v2 (11.5 s cut; v1 = 21.7 s version, see git history)
usage: cd ep16 && python3 build.py SHOT OUTDIR [opts]
  SHOT = A C E G   (film shots)  |  QA (print beats, write beats.json)
Pipeline: vo16.py -> build.py QA -> tv.py -> render.sh -> overlays.py -> audio.py -> assemble.py
Room, couch, lighting and Doug's seated legs are the ep14 (Front Camera v2) set-up.
"""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
from mathutils import Matrix, Quaternion, Euler
def V(*a): return Vector(a)
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def ease_tab(keys, f):
    """keys [(frame, number | tuple | Vector)] -> smoothstep between keys"""
    if f <= keys[0][0]: return keys[0][1]
    for (fa, a), (fb, b) in zip(keys, keys[1:]):
        if fa <= f <= fb:
            t = smooth((f - fa) / max(1, fb - fa))
            if isinstance(a, (int, float)): return a + (b - a) * t
            if isinstance(a, Vector): return a.lerp(b, t)
            return tuple(x + (y - x) * t for x, y in zip(a, b))
    return keys[-1][1]
FPS = 30

# ============================================================ BEATS (frames, 30 fps)
SH = dict(
    A=(1, 66),        # 0.0-2.2  medium close-up, already seated, controller in hand, menu on: happy inhale, "hah", "FINALLY!", leans in
    C=(67, 96),       # 2.2-3.2  over the shoulder: LANTERN HOLLOW menu; he re-grips, thumb moves toward the buttons (never presses)
    #  97-114           3.2-3.8  hard-cut black card "3 MINUTES LATER..." (assemble.py)
    E=(115, 204),     # 3.8-6.8  medium close-up: heavy lids, slow blink, droop, catches himself, looks at the TV, eyes close, tilt, relax
    G=(205, 345),     # 6.8-11.5 WIDE reveal: asleep, controller in his hands, NEW GAME on the TV. Vine boom on the cut, snoring from 8.2
)
N = 345
VO_F = 10                                   # vo/c.wav starts here (inhale 0.30 s, "hah" exhale, "Finally!")
INHALE = (10, 19); HAH = (20, 30); FIN = (33, 54)
REGRIP = (68, 80); THUMB = (80, 92); LEAN = (70, 92)
CARD = (97, 114)
HEAVY = (115, 128); SLOWBLINK = 131; DROOP = (138, 158); CATCH = (160, 167); LOOK = (167, 178); CLOSE = (178, 194)
TILT = (182, 204); RELAX = (188, 204); ASLEEP = 198
REVEAL = 205; SNORE0 = 247                  # first snore inhale at 8.2 s (the boom has decayed by ~7.97 s)
BOOT = (-60, -40); MENU_ON = -30; PRESS = -20   # v2: the console and the menu are already on at frame 1

# ============================================================ LIVING ROOM (ep14: evening, lamp-lit)
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

# ============================================================ TV SCREEN (image sequence from tv.py) + its light on the room
TV_DIR = os.path.join(HERE, 'tv')
NTV = len([f for f in os.listdir(TV_DIR) if f.endswith('.png')]) if os.path.isdir(TV_DIR) else 0
tv_m = bpy.data.materials.new('tv_screen'); tv_m.use_nodes = True; nt = tv_m.node_tree; nt.nodes.clear()
em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.5
o_ = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs['Emission'], o_.inputs['Surface'])
if NTV:
    img = bpy.data.images.load(os.path.join(TV_DIR, 'tv_0001.png')); img.source = 'SEQUENCE'
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.image_user.frame_duration = NTV; tex.image_user.frame_start = 1
    tex.image_user.frame_offset = 0; tex.image_user.use_auto_refresh = True; tex.extension = 'CLIP'
    nt.links.new(tex.outputs['Color'], em.inputs['Color'])
else:
    em.inputs['Color'].default_value = (0.02, 0.02, 0.03, 1)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, TVY + 0.0315, TVZ))
tvs = bpy.context.active_object; tvs.name = 'tv_screen'; tvs.scale = (TVW, TVH, 1); tvs.rotation_euler = (D(-90), D(180), 0)
tvs.data.materials.append(tv_m)
tl = bpy.data.lights.new('tv_glow', 'AREA'); tl.shape = 'RECTANGLE'; tl.size = TVW; tl.size_y = TVH
tlo = link(bpy.data.objects.new('tv_glow', tl)); tlo.location = (0, TVY + 0.06, TVZ); tlo.rotation_euler = (D(-90), 0, 0)
tlo.visible_camera = False
def tv_state(f):     # 0 off, (0,1) boot, 1 menu
    if f < BOOT[0]: return 0.0
    if f < MENU_ON: return 0.5 * smooth((f - BOOT[0]) / 6)
    return 1.0
for f in range(1, N + 1):
    s = tv_state(f)
    tl.energy = 0 if s == 0 else (55 if s < 1 else 70); tl.color = (0.55, 0.65, 1.0) if s < 1 else (0.75, 0.62, 0.95)
    tl.keyframe_insert('energy', frame=f); tl.keyframe_insert('color', frame=f)

# ============================================================ PROPS: console, controller, work bag (all original designs)
TV_YAW, TV_FWD = 22.0, 0.34           # ep16: the TV unit is angled a little toward the room's left (for the final wide)
white = mat('cons_white', hexc('#eef0f2'), 0.35, 0.3); blk = mat('cons_black', hexc('#141518'), 0.35, 0.4)
led = bpy.data.materials.new('cons_led'); led.use_nodes = True; lb = led.node_tree.nodes['Principled BSDF']
lb.inputs['Base Color'].default_value = (0.02, 0.02, 0.03, 1); lb.inputs['Emission Color'].default_value = (0.25, 0.55, 1.0, 1)
lb.inputs['Emission Strength'].default_value = 0.0
CONS = V(0.78, -1.86, 0.5)
cons = empty('console', tuple(CONS))
box('cons_core', (0.07, 0.24, 0.36), (0, 0, 0.18), blk, 0.012, cons)
for sx in (-1, 1):            # two curved white shells (a slim tower; not a copy of any real console)
    sh_ = box('cons_shell', (0.025, 0.27, 0.40), (sx * 0.048, 0, 0.2), white, 0.02, cons)
    sh_.rotation_euler = (0, sx * D(-4), 0)
box('cons_led', (0.012, 0.004, 0.30), (0, -0.122, 0.2), led, 0, cons)
box('cons_base', (0.16, 0.12, 0.012), (0, 0, 0.006), blk, 0.004, cons)
TVR = Matrix.Translation(V(0, TVY + TV_FWD, 0)) @ Matrix.Rotation(D(TV_YAW), 4, 'Z') @ Matrix.Translation(V(0, -TVY, 0))
bpy.context.view_layer.update()
for o in [bpy.data.objects[n] for n in ('cabinet', 'tv_body', 'tv_foot', 'tv_screen', 'tv_glow')] + [cons]:
    o.matrix_world = TVR @ o.matrix_world
bpy.context.view_layer.update()
def tvw(p): return TVR @ V(*p)        # an original-room point on the TV unit -> its world position now
CONS = tvw(CONS)
for f in (1, PRESS - 1, PRESS + 6, N):
    lb.inputs['Emission Strength'].default_value = 0.0 if f < PRESS else 6.0; lb.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)

ctrl = empty('controller'); ctrl.rotation_mode = 'QUATERNION'
box('ctl_body', (0.16, 0.085, 0.04), (0, 0, 0), white, 0.018, ctrl)
for sx in (-1, 1):
    g_ = capsule('ctl_grip', 0.03, 0.06, white, (sx * 0.075, 0.045, -0.012), rot=(D(70), sx * D(-18), 0), parent=ctrl)
    cyl('ctl_stick', 0.012, 0.018, (sx * 0.03, 0.012, 0.025), blk, verts=20, parent=ctrl)
box('ctl_pad', (0.07, 0.04, 0.006), (0, -0.012, 0.021), blk, 0.004, ctrl)
for (bx, by) in ((0.058, -0.015), (0.072, -0.002), (0.044, -0.002), (0.058, 0.011)):
    cyl('ctl_btn', 0.006, 0.008, (bx, by, 0.022), blk, verts=16, parent=ctrl)
box('ctl_led', (0.05, 0.005, 0.004), (0, -0.043, 0.012), led, 0, ctrl)
CTL_BTN = V(0.0, 0.016, 0.026)       # the middle "home" button he presses (controller-local)
cyl('ctl_home', 0.007, 0.008, tuple(CTL_BTN - V(0, 0, 0.004)), blk, verts=16, parent=ctrl)

bagm = mat('bag', hexc('#3b4a5c'), 0.7, 0.0); bagd = mat('bag_dark', hexc('#26303c'), 0.7)
bag = empty('bag'); bag.rotation_mode = 'XYZ'
box('bag_body', (0.38, 0.11, 0.28), (0, 0, 0), bagm, 0.03, bag)
box('bag_flap', (0.385, 0.03, 0.17), (0, -0.05, 0.05), bagd, 0.02, bag)
box('bag_clasp', (0.05, 0.012, 0.035), (0, -0.068, -0.02), mat('clasp', hexc('#b8a06a'), 0.3, 0.8), 0.004, bag)
for sx in (-1, 1): box('bag_handle', (0.02, 0.02, 0.09), (sx * 0.06, 0, 0.18), bagd, 0.008, bag)
box('bag_handle_top', (0.14, 0.02, 0.02), (0, 0, 0.225), bagd, 0.008, bag)
BAG_HANDLE = V(0, 0, 0.225)

# ============================================================ DOUG
exec(open(os.path.join(HERE, '..', 'ep12', 'rig.py')).read())
doug['mouth'].location.y = -0.326
doug_r = Rig(doug, 'doug', M['doug'], M['doug'], lift=0.17)
BASE = doug_r.base
KNEE_L = {'N': V(-0.17, -0.50, SEAT + 0.075), 'P': V(0.17, -0.50, SEAT + 0.075)}      # ep14 v2 seated legs
FOOT_L = {'N': V(-0.19, -0.51, 0.03), 'P': V(0.19, -0.51, 0.03)}
SEATED = V(0, 0.05, 0)
STAND_KNEE = {'N': V(-0.145, -0.015, 0.23), 'P': V(0.145, -0.015, 0.23)}
STAND_FOOT = {'N': V(-0.15, 0.0, 0.0), 'P': V(0.15, 0.0, 0.0)}
STAND = {'N': ((-0.15, 0.0, 0), (0, -1, 0.2)), 'P': ((0.15, 0.0, 0), (0, -1, 0.2))}
DOWN = {'N': ((-0.37, -0.03, 0.06), ('auto', (-1, 0.3, 0))), 'P': ((0.37, -0.03, 0.06), ('auto', (1, 0.3, 0)))}
CARRY_P = ((0.38, 0.0, 0.10), ('auto', (1, 0.2, 0.2)))
D_START, D_STOP, D_FRONT = V(-2.2, -0.85, 0), V(-1.28, -0.64, 0), V(0.0, -0.40, 0)
def heading(p0, p1): return math.degrees(math.atan2(p1.x - p0.x, -(p1.y - p0.y)))
H1 = heading(D_START, D_STOP); H2 = heading(D_STOP, D_FRONT)
H_NOTICE = heading(D_STOP, CONS + V(0, 0, 0)) + 8          # body turns most of the way to the console/TV
swing_tired = lambda f, ph: {'N': ((-0.36, 0.07 * math.sin(ph), 0.05), ('auto', (-1, 0.3, 0))), 'P': CARRY_P}
swing_brisk = lambda f, ph: {'N': ((-0.37, 0.11 * math.sin(ph), 0.07), ('auto', (-1, 0.3, 0))), 'P': ((0.37, -0.11 * math.sin(ph), 0.07), ('auto', (1, 0.3, 0)))}
WALKING = set()

def root_of(f): return SEATED, 0.0          # v2: seated on the couch the whole time
def sit_amt(f): return 1.0

ROLL = float(os.environ.get('ROLL', '9'))      # head tilt asleep (- = to his left)
# posture: (lean fwd deg, roll deg, lift)
POST = [(1, (1, 0, 0.0)), (INHALE[0], (1, 0, 0.0)), (INHALE[1], (-1.5, 0, 0.014)), (HAH[1], (0, 0, 0.006)),     # inhale: chest up; "hah": settles
        (FIN[0], (0.5, 0, 0.006)), (FIN[0] + 12, (6, 0, 0.012)), (SH['A'][1], (6.5, 0, 0.012)),                  # FINALLY: leans in
        (LEAN[0], (6.5, 0, 0.012)), (LEAN[1], (9, 0, 0.012)), (CARD[0], (9, 0, 0.012)),                           # OTS: further in, ready
        (SH['E'][0], (2, 0, -0.016)), (HEAVY[1], (3, 0, -0.018)), (DROOP[0], (3, 0, -0.018)),                    # 3 min later: sagging
        (DROOP[1], (11, 2.5, -0.03)), (CATCH[0], (11.5, 2.5, -0.03)), (CATCH[1], (1, 0, -0.012)),                 # droops ... catches himself
        (LOOK[1], (2, 0.5, -0.016)), (TILT[0], (3, 0.5, -0.02)), (TILT[1], (13, ROLL, -0.035)), (N, (13, ROLL, -0.035))]
def posture(f): return ease_tab(POST, f)
def breath(f):
    if f >= ASLEEP: return 0.006 * math.sin(2 * math.pi * (f - SNORE0) / 66 - math.pi / 2)      # slow sleep breathing; inhales start at SNORE0 + 66k
    return 0.0025 * math.sin(2 * math.pi * f / 105)

# controller world pose
def cq(pitch, yaw=0.0, roll=0.0): return Euler((D(pitch), D(roll), D(yaw)), 'ZXY').to_quaternion() if False else (Quaternion(V(0, 0, 1), D(yaw)) @ Quaternion(V(1, 0, 0), D(pitch)) @ Quaternion(V(0, 1, 0), D(roll)))
C_CUSH = (V(0.6, -0.04, SEAT + 0.035), cq(0, 25))
C_HOLD = (V(0.0, -0.50, 0.80), cq(-42))
C_FWD = (V(0.0, -0.53, 0.82), cq(-45))
C_LOW = (V(0.0, -0.49, 0.75), cq(-36))
C_DROOP = (V(0.02, -0.48, 0.70), cq(-28, 0, -6))
C_JERK = (V(0.0, -0.50, 0.79), cq(-44))
C_LAP = (V(0.05, -0.45, 0.645), cq(-14, -6, 10))
C_EXC = (V(0.0, -0.52, 0.82), cq(-44))                       # FINALLY: up a touch with the lean
C_REG = (V(0.01, -0.51, 0.835), cq(-50, 4, -5))               # re-grip: a little lift and wiggle
C_KEYS = [(1, C_HOLD), (FIN[0], C_HOLD), (FIN[0] + 12, C_EXC), (REGRIP[0], C_EXC), (REGRIP[0] + 5, C_REG), (REGRIP[1], C_FWD), (CARD[0], C_FWD),
          (SH['E'][0], C_LOW), (DROOP[0], C_LOW), (DROOP[1], C_DROOP), (CATCH[0], C_DROOP), (CATCH[1], C_JERK), (LOOK[1], C_LOW),
          (RELAX[0], C_LOW), (RELAX[1], C_LAP), (N, C_LAP)]
def ctrl_pose(f):
    for (fa, (pa, qa)), (fb, (pb, qb)) in zip(C_KEYS, C_KEYS[1:]):
        if fa <= f <= fb:
            t = smooth((f - fa) / max(1, fb - fa)); return pa.lerp(pb, t), qa.slerp(qb, t)
    return C_KEYS[-1][1]
def CM(f):
    p, q = ctrl_pose(f)
    if f >= ASLEEP: p = p + V(0, 0, 0.6 * breath(f))
    m = q.to_matrix().to_4x4(); m.translation = p; return m
GRIP = {'N': V(-0.08, 0.06, -0.035), 'P': V(0.08, 0.06, -0.035)}
for f in range(1, N + 1):
    m_ = CM(f); ctrl.location = m_.translation; ctrl.rotation_quaternion = m_.to_quaternion()
    ctrl.keyframe_insert('location', frame=f); ctrl.keyframe_insert('rotation_quaternion', frame=f)
    lb_on = f >= PRESS
for f in (1, PRESS - 1, PRESS + 4, N): pass

def mix(a, b, t): return a.lerp(b, smooth(t))
def root_matrix(f):
    p, h = root_of(f); return Matrix.Translation(p) @ Matrix.Rotation(D(h), 4, 'Z')
def upper_matrix(f):
    lean, roll, lift = posture(f); up = V(0, 0, BASE + lift + breath(f) * 0.4)
    return root_matrix(f) @ Matrix.Translation(up) @ Euler((D(lean), D(roll), 0)).to_matrix().to_4x4()
def to_local(w, f): return upper_matrix(f).inverted() @ V(*w)
def down_world(side, f): return upper_matrix(f) @ V(*DOWN[side][0])
def grip_w(side, f): return CM(f) @ GRIP[side]
def hand_world(side, f):
    g = grip_w(side, f)
    if side == 'P' and THUMB[0] <= f <= CARD[0] + 2:     # thumb moves over toward the buttons ... and stays there, ready. Never presses.
        a = smooth((f - THUMB[0]) / 8)
        hov = CM(f) @ (CTL_BTN + V(0.035, 0.03, 0.06 + 0.004 * math.sin(f * 0.6)))
        return g.lerp(hov, a)
    if side == 'N' and REGRIP[0] <= f <= REGRIP[1]:      # left hand slides along the grip as he re-seats it
        return g + (CM(f).to_3x3() @ V(0.0, -0.025, 0.0)) * math.sin(math.pi * (f - REGRIP[0]) / (REGRIP[1] - REGRIP[0]))
    return g

for f in range(1, N + 1):
    p, h = root_of(f)
    doug_r.place(f, (p.x, p.y), h)
    lean, roll, lift = posture(f); br = breath(f)
    arms = {}
    for s_ in ('N', 'P'):
        arms[s_] = (tuple(to_local(hand_world(s_, f), f)), ('auto', ((-1 if s_ == 'N' else 1), 0.15, -0.5)))
    sq = 1 + br * (2.0 if f >= ASLEEP else 1.0)
    doug_r.pose(f, up=(0, 0, lift + br * 0.4), rot=(lean, roll, 0), sq=sq, arms=arms, legs=STAND)
    s = sit_amt(f)
    if s > 0:     # legs: standing -> seated (ep14 v2 pose); the feet stay planted, the body slides back onto the cushion
        rp = root_of(f)[0]
        for s_ in ('N', 'P'):
            foot_w = (D_FRONT + STAND_FOOT[s_]).lerp(SEATED + FOOT_L[s_], s)
            foot = foot_w - rp
            hip = V(0, 0, BASE) + V(0, 0, lift) + doug_r.hip_off[s_]
            knee = (STAND_KNEE[s_] + (D_FRONT - rp)).lerp(KNEE_L[s_], s)
            knee = knee.lerp(KNEE_L[s_], 0)                      # (knee path: straight blend)
            if s < 1: knee.z = max(knee.z, (hip.z + foot.z) / 2 + 0.06 * math.sin(math.pi * s))
            doug_r.key_points(doug_r.leg[s_], f, (hip, knee, foot))
            doug_r.foot[s_].location = foot + V(0, -0.035, 0.03); doug_r.foot[s_].keyframe_insert('location', frame=f)

# the work bag: already dropped by the couch's arm (where it landed in v1) - just set dressing now
bag.location = V(-1.349, -0.266, 0.12); bag.rotation_euler = (D(-14), 0, D(H1 - 90))

# ============================================================ FACE: eyes, lids, brows, smile, sleepy mouth
D_LIDS = [o for o in bpy.data.objects if o.name.startswith('doug_lid')]
BZ = [b.location.z for b in doug['brows']]
mouth0 = doug['mouth']; mouth0.hide_render = True; mouth0.hide_viewport = True
mcu = bpy.data.curves.new('doug_mouth_c', 'CURVE'); mcu.dimensions = '3D'; mcu.bevel_depth = 0.016; mcu.bevel_resolution = 6; mcu.use_fill_caps = True
msp = mcu.splines.new('POLY'); msp.points.add(6)
mouth = link(bpy.data.objects.new('doug_mouth_c', mcu)); mouth.data.materials.append(M['mouth'])
mouth.parent = mouth0; mouth.matrix_parent_inverse = Matrix.Identity(4)      # rides on the hidden capsule (its local z = along the mouth, -x = up)
MX = [-0.036 + 0.012 * i for i in range(7)]
def mouth_shape(f, sm):
    for p, x in zip(msp.points, MX):
        u = x / 0.036; z = 0.02 * sm * (u * u - 0.35)          # corners up, middle down a touch
        p.co = (-z, 0.32 - math.sqrt(0.32 ** 2 - x * x), x, 1.0); p.keyframe_insert('co', frame=f)
LID = [(1, 8), (INHALE[0], 8), (INHALE[1], 0), (HAH[1], 4), (FIN[0], 2), (FIN[0] + 8, -10), (SH['A'][1], -8),      # eyes brighten on FINALLY
       (LEAN[0], -6), (CARD[0], 0),
       (SH['E'][0], 22), (HEAVY[1], 29), (DROOP[0], 30), (DROOP[1], 80), (CATCH[0], 82), (CATCH[1], 12), (LOOK[0] + 4, 18),     # heavy ... droop ... caught
       (LOOK[1], 26), (CLOSE[0] + 6, 52), (CLOSE[0] + 9, 44), (CLOSE[1], 95), (N, 95)]                                      # tries to look; eyes close
BLINKS = [(62, 2), (SLOWBLINK, 8)]                # one quick blink after FINALLY; one slow heavy blink 3 min later
BROW = [(1, (0.012, 2)), (INHALE[0], (0.012, 2)), (INHALE[1], (0.026, 6)), (HAH[1], (0.02, 4)), (FIN[0] + 8, (0.03, 7)), (SH['A'][1], (0.024, 5)),
        (CARD[0], (0.018, 4)), (SH['E'][0], (-0.006, -3)), (DROOP[1], (-0.012, -6)), (CATCH[0], (-0.012, -6)), (CATCH[1], (0.022, 5)),
        (LOOK[1], (0.004, 0)), (CLOSE[1], (-0.012, -5)), (N, (-0.012, -5))]
SMILE = [(1, 0.55), (INHALE[0], 0.55), (HAH[0], 0.9), (FIN[0], 1.0), (SH['A'][1], 1.0), (CARD[0], 0.85), (SH['E'][0], 0.0), (N, 0.0)]
# lip-sync from the take (vo/c.wav, placed at VO_F): breath spans drawn by hand, "Finally!" from its loudness
import soundfile as _sf
_a, _sr = _sf.read(os.path.join(HERE, 'vo', 'c.wav')); _hop = _sr // 30
_rms = np.array([np.sqrt(np.mean(_a[i:i + _hop] ** 2)) for i in range(0, len(_a) - _hop, _hop)]); _rms /= _rms.max()
MOUTH_O = {}; _prev = 0.0
for i, r_ in enumerate(_rms):
    f_ = VO_F + i; o = max(0.0, min(1.0, (r_ - 0.06) / 0.5)); o = o if o > _prev else _prev * 0.5 + o * 0.5; _prev = o
    if INHALE[0] <= f_ <= INHALE[1]: o = max(o, 0.14 * math.sin(math.pi * (f_ - INHALE[0]) / (INHALE[1] - INHALE[0])))     # breath in, lips parted
    if HAH[0] <= f_ <= HAH[1]: o = max(o, 0.42 * math.sin(math.pi * (f_ - HAH[0]) / (HAH[1] - HAH[0])) ** 0.7)              # "hah": open, smiling
    MOUTH_O[f_] = o
def blink_amt(f):
    for b_, dur in BLINKS:
        if abs(f - b_) <= dur: return 1 - abs(f - b_) / (dur + 1)
    return 0.0
TVC = tvw(V(0, TVY, TVZ - 0.05))
def gaze(f):
    if REGRIP[0] <= f < REGRIP[0] + 9: return CM(f).translation            # a glance down at his hands while re-gripping
    if f >= DROOP[0] and f < CATCH[1]: return TVC.lerp(CM(f).translation, smooth((f - DROOP[0]) / (DROOP[1] - DROOP[0])) * 0.7)
    return TVC
for f in range(1, N + 1):
    scene.frame_set(f)
    T_ = gaze(f)
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
    sm = ease_tab(SMILE, f)
    mouth_shape(f, sm)
    op = 0.0
    if f >= ASLEEP: op = 0.18 + 0.1 * max(0.0, math.sin(2 * math.pi * (f - SNORE0) / 66))        # mouth hangs a little open, asleep
    o = MOUTH_O.get(f, 0.0)                                                                       # talking: the mouth opens taller
    mouth.scale = (1 + 1.6 * op + 2.3 * o, 1, (1 - 0.08 * sm) * (1 + 0.12 * o)); mouth.keyframe_insert('scale', frame=f)

# ============================================================ CAMERAS
EYE = lambda f: upper_matrix(f) @ V(0, -0.2, doug_r.ez - 0.05)
def cam_for(f):
    """-> (location, target, lens, fstop, focus point)"""
    if os.environ.get('CAMO'):     # QA: any framing "x,y,z,tx,ty,tz,lens"
        v = [float(x) for x in os.environ['CAMO'].split(',')]; return V(*v[:3]), V(*v[3:6]), v[6], 8.0, V(*v[3:6])
    if f <= SH['A'][1]:        # medium close-up from his left-front: face (lip-sync) and the controller, a slow push in
        if os.environ.get('ACAM'):
            v = [float(x) for x in os.environ['ACAM'].split(',')]; return V(*v[:3]), V(*v[3:6]), v[6], 4.0, EYE(f)
        t = smooth((f - 1) / 65)
        return V(-0.5, -1.5, 1.34).lerp(V(-0.46, -1.43, 1.33), t), V(0.0, -0.2, 1.16), 24, 4.0, EYE(f)
    if f <= SH['C'][1]:        # over his right shoulder at the TV
        t = smooth((f - SH['C'][0]) / 29)
        return V(0.86, 0.82, 1.66).lerp(V(0.83, 0.75, 1.63), t), V(-0.2, -1.95, 1.0), 26, 8.0, V(0, -1.9, 1.1)
    if f <= SH['E'][1]:        # medium close-up: face down to the controller (v1 shot E framing), slow creep in
        t = smooth((f - SH['E'][0]) / 89)
        return V(0.2, -1.3, 1.34).lerp(V(0.17, -1.22, 1.32), t), V(0.0, -0.2, 1.22), 22, 4.0, EYE(f)
    # WIDE reveal: high, behind-right of the couch - Doug asleep in the foreground, NEW GAME on the TV beyond him
    if os.environ.get('GCAM'):
        v = [float(x) for x in os.environ['GCAM'].split(',')]; return V(*v[:3]), V(*v[3:6]), v[6], 8.0, V(0, -0.3, 1.0)
    return V(-2.3, -1.0, 1.55), V(-0.05, -0.8, 1.0), 18, 8.0, V(0, -0.3, 1.0)
def cam_setup(name):
    a_, b_ = SH[name]
    for f in range(a_, b_ + 1):
        p, tgt, lens, fs, fp = cam_for(f)
        key(cam, 'location', f, p); key(target, 'location', f, tgt); key(focus, 'location', f, fp)
        key(cam_data, 'lens', f, lens); key(cam_data.dof, 'aperture_fstop', f, fs)

if SHOT == "QA":
    json.dump({'SH': SH, 'N': N, 'VO_F': VO_F, 'INHALE': INHALE, 'HAH': HAH, 'FIN': FIN, 'REGRIP': REGRIP, 'THUMB': THUMB, 'LEAN': LEAN,
               'CARD': CARD, 'HEAVY': HEAVY, 'DROOP': DROOP, 'CATCH': CATCH, 'LOOK': LOOK, 'CLOSE': CLOSE, 'TILT': TILT, 'RELAX': RELAX,
               'ASLEEP': ASLEEP, 'SNORE0': SNORE0, 'REVEAL': REVEAL, 'BOOT': BOOT, 'MENU_ON': MENU_ON, 'PRESS': PRESS},
              open(os.path.join(HERE, 'beats.json'), 'w'), indent=1)
    for f in (1, 45, 85, 120, 150, 165, 204, 300):
        scene.frame_set(f)
        print(f, 'feet', [tuple(round(x, 3) for x in doug_r.foot[s].matrix_world.translation) for s in ('N', 'P')],
              'hands', [tuple(round(x, 3) for x in doug_r.hand[s].matrix_world.translation) for s in ('N', 'P')],
              'ctrl', tuple(round(x, 3) for x in ctrl.matrix_world.translation), 'bag', tuple(round(x, 3) for x in bag.matrix_world.translation))
    sys.exit(0)
if SHOT == 'S':        # QA side view of the seated pose
    SH['S'] = (1, N)
    for f in range(1, N + 1):
        key(cam, 'location', f, V(2.3, -0.30, 0.78)); key(target, 'location', f, V(0.0, -0.22, 0.62)); key(focus, 'location', f, V(0, -0.2, 0.6))
        key(cam_data, 'lens', f, 38); key(cam_data.dof, 'aperture_fstop', f, 16.0)
else:
    cam_setup(SHOT)
f0, f1 = SH[SHOT]; scene.frame_set(f0)
cam_data.clip_start = 0.02
FR = FR or f'{f0}-{f1}'
render(N)
