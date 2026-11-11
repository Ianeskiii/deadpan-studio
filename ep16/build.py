"""Tube Town - When you finally have free time to play games.
usage: cd ep16 && python3 build.py SHOT OUTDIR [opts]
  SHOT = A B C E F G   (film shots)  |  QA (print beats, write beats.json)
Pipeline: build.py QA -> tv.py -> render.sh -> overlays.py -> audio.py -> assemble.py
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
    A=(1, 112),       # medium-wide: drags himself in, drops the bag by the couch, sees the console -> perks up (small smile)
    B=(113, 205),     # medium: crosses to the couch, plops down, grabs the controller, presses the power button (TV/console wake)
    C=(206, 258),     # over the shoulder: boot logo -> the menu (NEW GAME), he leans in, thumbs ready
    #  259-290          black card "15 MINUTES LATER..." (assemble.py)
    E=(291, 420),     # medium close-up: fighting sleep - heavy lids, slow blinks, head droops, catches himself, thumb hovers
    F=(421, 510),     # closer, other side: one last try, eyes close, head tilts, grip relaxes. Silence before the cut.
    G=(511, 640),     # WIDE reveal: asleep, controller in his hands, NEW GAME on the TV. FAHHH on the cut, pause, snoring
)
N = 650               # 641-650 black
WALK1 = (1, 46); DROP = 50; BAG_LAND = 58; NOTICE = 64; PERK = (70, 82)
WALK2 = (113, 134); TURN = (134, 142); SIT = (142, 154)
REACH = (158, 168); LIFT = (168, 180); NJOIN = (172, 180); PRESS = 188; BOOT = (188, 213); MENU_ON = 214; LEAN = (222, 238)
CARD = (259, 290)
DROOP = (322, 356); CATCH = 360; HOVER = (382, 402)
TRY = (424, 438); CLOSE = (440, 478); TILT = (452, 492); RELAX = (476, 500); ASLEEP = 496; SILENCE = (497, 510)
REVEAL = 511
G_BLACK = 641

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
doug_r.walk(WALK1[0], WALK1[1], (D_START.x, D_START.y), (D_STOP.x, D_STOP.y), H1, steps=3.4, arms=swing_tired, lean=9, bob=0.025, lift=0.05, sway=3, crouch=0.015)
doug_r.walk(WALK2[0], WALK2[1], (D_STOP.x, D_STOP.y), (D_FRONT.x, D_FRONT.y), H2, steps=3.0, arms=swing_brisk, lean=3, bob=0.035, sway=4)
WALKING = set(range(WALK1[0], WALK1[1] + 1)) | set(range(WALK2[0], WALK2[1] + 1))

def root_of(f):
    """(position, heading) for the frames walk() doesn't drive"""
    if f <= SH['A'][1]:
        return D_STOP, ease_tab([(WALK1[1], H1), (NOTICE + 2, H1), (NOTICE + 10, H_NOTICE)], f)
    if f < TURN[0]: return D_FRONT, H2
    if f < SIT[0]: return D_FRONT, ease_tab([(TURN[0], H2), (TURN[1], 0.0)], f)
    s = smooth((f - SIT[0]) / (SIT[1] - SIT[0]))
    return D_FRONT.lerp(SEATED, s), 0.0
def sit_amt(f): return 0.0 if f < SIT[0] else smooth((f - SIT[0]) / (SIT[1] - SIT[0]))

ROLL = float(os.environ.get('ROLL', '9'))      # head tilt asleep (- = to his left)
# posture: (lean fwd deg, roll deg, lift) - seated keys; A uses its own
POST = [(SIT[1], (0, 0, 0.0)), (LEAN[0], (0, 0, 0.0)), (LEAN[1], (4, 0, 0.0)), (CARD[0], (4, 0, 0.0)),
        (SH['E'][0], (1, 0, -0.015)), (DROOP[0], (1.5, 0, -0.018)), (DROOP[1], (11, 2.5, -0.03)), (CATCH, (11, 2.5, -0.03)),
        (CATCH + 4, (-2, 0, -0.008)), (CATCH + 16, (0.5, 0, -0.014)), (SH['E'][1], (2, 0.5, -0.018)), (TRY[1], (3, 0.5, -0.016)),
        (TILT[0], (3.5, 0.5, -0.02)), (TILT[1], (13, ROLL, -0.035)), (N, (13, ROLL, -0.035))]
def posture(f):
    if f <= SH['A'][1]:
        lean = ease_tab([(WALK1[1], 9), (PERK[0], 9), (PERK[1], 0)], f); lift = ease_tab([(WALK1[1], -0.015), (PERK[0], -0.015), (PERK[1], 0.02)], f)
        return lean, 0.0, lift
    if f < SIT[0]: return 2.0, 0.0, 0.0
    if f <= SIT[1]:
        s = (f - SIT[0]) / (SIT[1] - SIT[0])
        return -5 * math.sin(math.pi * s), 0.0, -0.06 * math.sin(math.pi * min(1, s * 1.15))       # plops back onto the cushion
    return ease_tab(POST, f)
def breath(f):
    if f >= ASLEEP: return 0.006 * math.sin(2 * math.pi * (f - ASLEEP) / 66)      # slow sleep breathing
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
C_KEYS = [(1, C_CUSH), (LIFT[0], C_CUSH), (LIFT[1], C_HOLD), (LEAN[0], C_HOLD), (LEAN[1], C_FWD), (CARD[0], C_FWD),
          (SH['E'][0], C_LOW), (DROOP[0], C_LOW), (DROOP[1], C_DROOP), (CATCH, C_DROOP), (CATCH + 4, C_JERK), (CATCH + 18, C_LOW),
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
    if f < REACH[0]: return down_world(side, f)
    if side == 'P':
        if f < REACH[1]: return mix(down_world('P', f), grip_w('P', f), (f - REACH[0]) / (REACH[1] - REACH[0]))
        g = grip_w('P', f)
        if PRESS - 4 <= f <= PRESS + 4:            # thumb goes to the home button: the fist dips onto the middle of the pad
            a = 1 - abs(f - PRESS) / 4.0; return g.lerp(CM(f) @ (CTL_BTN + V(0.03, 0.03, 0.02)), smooth(a))
        if HOVER[0] <= f <= HOVER[1] + 8 or TRY[0] <= f <= CLOSE[0] + 20:     # hovering over START, never pressing it
            if f <= HOVER[1] + 8: a = smooth((f - HOVER[0]) / 6) * (1 - smooth((f - HOVER[1]) / 8))
            else: a = smooth((f - TRY[0]) / 8) * (1 - smooth((f - CLOSE[0] - 8) / 12))
            hov = CM(f) @ (CTL_BTN + V(0.035, 0.035, 0.065 + 0.006 * math.sin(f * 0.5)))
            return g.lerp(hov, a)
        return g
    if f < NJOIN[0]: return down_world('N', f)
    if f < NJOIN[1]: return mix(down_world('N', f), grip_w('N', f), (f - NJOIN[0]) / (NJOIN[1] - NJOIN[0]))
    return grip_w('N', f)

for f in range(1, N + 1):
    if f in WALKING:
        if f <= WALK1[1] or f >= WALK2[0]:   # walk() already posed these; legs stay walk legs
            continue
    p, h = root_of(f)
    doug_r.place(f, (p.x, p.y), h)
    lean, roll, lift = posture(f); br = breath(f)
    arms = {}
    for s_ in ('N', 'P'):
        if f <= SH['A'][1]:
            arms[s_] = CARRY_P if (s_ == 'P' and f < DROP) else DOWN[s_]
        else:
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

# the bag: in his right hand, dropped by the couch's arm, lands, tips a little
scene.frame_set(1)
BAG_FLOOR = None
def hand_P_world(f):
    scene.frame_set(f); return doug_r.hand['P'].matrix_world.translation.copy()
drop_from = None
for f in range(1, N + 1):
    if f < DROP:
        hp = hand_P_world(f); _, hd = root_of(f) if f > WALK1[1] else (None, H1)
        bag.location = hp - BAG_HANDLE - V(0, 0, 0.03); bag.rotation_euler = (0, 0, D(hd - 90 + 8 * math.sin(f * 0.35)))
        drop_from = (bag.location.copy(), hd)
    else:
        p0, hd = drop_from
        land = V(p0.x, p0.y, 0.14)
        t = min(1.0, (f - DROP) / (BAG_LAND - DROP))
        z = p0.z + (land.z - p0.z) * t * t
        tip = 0 if f < BAG_LAND else 14 * smooth((f - BAG_LAND) / 6) - 3 * math.sin(min(1, (f - BAG_LAND) / 8) * math.pi)
        bag.location = V(p0.x, p0.y, z); bag.rotation_euler = (D(-tip), 0, D(hd - 90))
        if f >= BAG_LAND: bag.location.z = 0.14 - 0.02 * smooth((f - BAG_LAND) / 6)
    bag.keyframe_insert('location', frame=f); bag.keyframe_insert('rotation_euler', frame=f)

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
LID = [(1, 34), (NOTICE, 34), (NOTICE + 4, 26), (PERK[0], 28), (PERK[1], 8), (SH['A'][1], 10), (SIT[1], 12), (MENU_ON, 6), (CARD[0], 8),
       (SH['E'][0], 40), (DROOP[0] - 6, 48), (DROOP[1], 80), (CATCH, 82), (CATCH + 3, 14), (CATCH + 14, 22), (SH['E'][1], 50),
       (TRY[1], 52), (CLOSE[0], 56), (CLOSE[0] + 14, 78), (CLOSE[0] + 20, 66), (CLOSE[1], 95), (N, 95)]
BLINKS = [(24, 4), (109, 2), (MENU_ON + 12, 3), (300, 9), (334, 10), (412, 10)]      # tired = slow blinks
BROW = [(1, (-0.012, -6)), (PERK[0], (-0.012, -6)), (PERK[1], (0.02, 4)), (SH['A'][1], (0.015, 3)), (SIT[1], (0.01, 2)), (MENU_ON, (0.02, 4)),
        (CARD[0], (0.012, 2)), (SH['E'][0], (-0.004, -3)), (DROOP[1], (-0.012, -6)), (CATCH, (-0.012, -6)), (CATCH + 3, (0.025, 5)),
        (CATCH + 20, (0.005, 0)), (CLOSE[1], (-0.012, -5)), (N, (-0.012, -5))]
SMILE = [(1, 0.0), (PERK[0] + 2, 0.0), (PERK[1] + 4, 1.0), (SH['A'][1], 1.0), (SIT[1], 0.6), (MENU_ON, 0.6), (MENU_ON + 8, 1.0),
         (CARD[0], 1.0), (SH['E'][0], 0.0), (N, 0.0)]
def blink_amt(f):
    for b_, dur in BLINKS:
        if abs(f - b_) <= dur: return 1 - abs(f - b_) / (dur + 1)
    return 0.0
TVC = tvw(V(0, TVY, TVZ - 0.05))
def gaze(f):
    if f < NOTICE: return root_matrix(f) @ V(0, -2.0, 1.2)
    if f <= SH['A'][1]: return CONS + V(0, 0, 0.25) if f < NOTICE + 20 else TVC.lerp(CONS + V(0, 0, 0.25), 0.4)
    if f < TURN[0]: return root_matrix(f) @ V(0, -2.0, 1.2)
    if REACH[0] - 4 <= f < LIFT[1] - 2: return CM(f).translation
    if HOVER[0] <= f <= HOVER[1]: return CM(f) @ CTL_BTN if f < HOVER[0] + 12 else TVC
    if f >= DROOP[0] and f < CATCH: return TVC.lerp(CM(f).translation, smooth((f - DROOP[0]) / (DROOP[1] - DROOP[0])) * 0.7)
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
    if f >= ASLEEP: op = 0.18 + 0.1 * max(0.0, math.sin(2 * math.pi * (f - ASLEEP) / 66))        # mouth hangs a little open, asleep
    mouth.scale = (1 + 1.6 * op, 1, 1 - 0.08 * sm); mouth.keyframe_insert('scale', frame=f)

# ============================================================ CAMERAS
EYE = lambda f: upper_matrix(f) @ V(0, -0.2, doug_r.ez - 0.05)
def cam_for(f):
    """-> (location, target, lens, fstop, focus point)"""
    if os.environ.get('CAMO'):     # QA: any framing "x,y,z,tx,ty,tz,lens"
        v = [float(x) for x in os.environ['CAMO'].split(',')]; return V(*v[:3]), V(*v[3:6]), v[6], 8.0, V(*v[3:6])
    if f <= SH['A'][1]:        # medium-wide from the TV side: he comes in from the left, the console is just behind camera
        t = smooth((f - 1) / 111)
        return V(0.5, -1.22, 1.34).lerp(V(0.42, -1.16, 1.32), t), V(-1.4, -0.55, 0.98).lerp(V(-1.2, -0.6, 1.02), t), 20, 5.6, EYE(f)
    if f <= SH['B'][1]:        # medium from the front-right: the cross to the couch, the plop, the controller
        return V(0.55, -1.13, 1.25), V(-0.12, -0.2, 0.95), 19, 5.6, EYE(f)
    if f <= SH['C'][1]:        # over his right shoulder at the TV
        t = smooth((f - SH['C'][0]) / 52)
        return V(0.86, 0.82, 1.66).lerp(V(0.82, 0.72, 1.62), t), V(-0.2, -1.95, 1.0), 26, 8.0, V(0, -1.9, 1.1)
    if f <= SH['E'][1]:        # medium close-up: face down to the controller
        t = smooth((f - SH['E'][0]) / 129)
        return V(0.2, -1.3, 1.34).lerp(V(0.17, -1.22, 1.32), t), V(0.0, -0.2, 1.24), 22, 4.0, EYE(f)
    if f <= SH['F'][1]:        # closer, from his left
        t = smooth((f - SH['F'][0]) / 89)
        return V(-0.5, -1.5, 1.34).lerp(V(-0.46, -1.42, 1.32), t), V(0.0, -0.2, 1.2), 25, 4.0, EYE(f)
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
    json.dump({'SH': SH, 'N': N, 'WALK1': WALK1, 'DROP': DROP, 'BAG_LAND': BAG_LAND, 'NOTICE': NOTICE, 'PERK': PERK, 'WALK2': WALK2,
               'TURN': TURN, 'SIT': SIT, 'REACH': REACH, 'LIFT': LIFT, 'PRESS': PRESS, 'BOOT': BOOT, 'MENU_ON': MENU_ON, 'LEAN': LEAN,
               'CARD': CARD, 'DROOP': DROOP, 'CATCH': CATCH, 'HOVER': HOVER, 'TRY': TRY, 'CLOSE': CLOSE, 'TILT': TILT, 'RELAX': RELAX,
               'ASLEEP': ASLEEP, 'SILENCE': SILENCE, 'REVEAL': REVEAL, 'G_BLACK': G_BLACK}, open(os.path.join(HERE, 'beats.json'), 'w'), indent=1)
    for f in (20, 112, 154, 200, 300, 500, 600):
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
