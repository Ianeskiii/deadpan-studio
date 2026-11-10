"""Tube Town - "Getting robbed but your favorite music is still playing".
One continuous 480-frame (16 s @30fps, 120 BPM => beat every 15 frames) choreography, cut between cameras.
usage: python3 build11.py SHOT OUTDIR [--still F] [--samples N] [--pct P] [--step S]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
from mathutils import Matrix
BEATF = 15
def bf(b): return 1 + BEATF * (b - 1)          # first frame of beat b (1-based)

# ============================================================ PARKING LOT (night)
P = dict(
    ground=brick_mat('slab', hexc('#8d8a85'), hexc('#86837e'), hexc('#77746f'), 0.7, 0.5, 0.5, 0.0, 0.85),
    wall=brick_mat('panel', hexc('#5d6672'), hexc('#58616c'), hexc('#3e454e'), 0.35, 1.0, 1.0, 0.0, 0.7, vertical=True),
    door=brick_mat('rollup', hexc('#aeb4bb'), hexc('#a5abb2'), hexc('#7f858c'), 3.0, 4.0, 0.08, 0.0, 0.5, vertical=True),
    yellow=mat('paint_y', hexc('#e6b422'), 0.6),
    white=mat('paint_w', hexc('#e9e9e4'), 0.6),
    car1=mat('car1', hexc('#e8e8e6'), 0.25, 0.8), car2=mat('car2', hexc('#7b8189'), 0.25, 0.8),
    glass=mat('cglass', hexc('#1a1f26'), 0.1, 0.8),
    tire=mat('tire', hexc('#161616'), 0.8),
    lamp=mat('wlamp', (0, 0, 0), 0.5, 0, hexc('#fff1d6'), 12),
    red=mat('redlamp', (0, 0, 0), 0.5, 0, hexc('#ff3a3a'), 10),
    beanie=mat('beanie', hexc('#7d7a4a'), 0.95, 0, sheen=0.6),
    track=mat('track', hexc('#1f6f78'), 0.55, 0.1),
    stripe=mat('stripe', hexc('#e9e4d0'), 0.6),
    ricky=mat('ricky', hexc('#8fbf6a'), 0.38, 0.6),
    iris_r=mat('iris_r', hexc('#3b2a1a'), 0.3, 0.8),
    hp=mat('headphones', hexc('#17171a'), 0.3, 0.6),
    hpcup=mat('hpcup', hexc('#e2453a'), 0.3, 0.6),
    bag=mat('bag', hexc('#2e3135'), 0.7, 0.1),
    star=mat('star', hexc('#ffd84a'), 0.4, 0, hexc('#ffc21a'), 2.0),
)
box('ground', (40, 30, 0.1), (0, 3, -0.05), P['ground'])
box('warehouse', (34, 0.3, 7), (0, 9.5, 3.5), P['wall'])
for dx in (-6, 0.5, 7):
    box('rollup', (3.2, 0.06, 3.6), (dx, 9.33, 1.8), P['door'])
box('warehouse_l', (0.3, 14, 7), (-11, 3, 3.5), P['wall'])
box('warehouse_r', (0.3, 14, 7), (11, 3, 3.5), P['wall'])
for ry in (1.0, 5.0):
    box('rollup_r', (0.06, 3.0, 3.4), (10.83, ry, 1.7), P['door'])
text('3', 1.4, (3.4, 9.32, 2.6), P['yellow'], extrude=0.01)
for i in range(-5, 6):
    box('pline', (0.08, 2.6, 0.005), (i * 2.3, 7.4, 0.003), P['white'])
for x, y in ((-4, 4.2), (4.6, 3.6)):
    box('yline', (2.0, 0.1, 0.005), (x, y, 0.003), P['yellow'])
def car(x, m, ang=0):
    e = empty('car', (x, 7.4, 0)); e.rotation_euler = (0, 0, D(90 + ang))
    box('cbody', (2.2, 1.05, 0.55), (0, 0, 0.5), m, 0.12, e)
    box('ccab', (1.25, 0.98, 0.45), (-0.15, 0, 0.98), m, 0.12, e)
    box('cwin', (1.27, 1.0, 0.3), (-0.15, 0, 1.0), P['glass'], 0.08, e)
    for wx in (-0.72, 0.72):
        for wy in (-0.5, 0.5):
            cyl('wheel', 0.24, 0.16, (wx, wy, 0.24), P['tire'], rot=(D(90), 0, 0), parent=e)
car(-6.9, P['car1']); car(-4.6, P['car2'], 4); car(-2.3, P['car1'], -3); car(5.9, P['car2'])
for lx in (-6, 0.5, 7):
    box('wall_lamp', (0.5, 0.12, 0.16), (lx, 9.3, 4.2), P['lamp'], 0.02)
    sp = bpy.data.lights.new('wl', 'SPOT'); sp.energy = 600; sp.spot_size = D(95); sp.spot_blend = 0.6
    sp.color = hexc('#ffe7c4'); sp.shadow_soft_size = 0.3
    so = link(bpy.data.objects.new('wl', sp)); so.location = (lx, 9.0, 4.1); so.rotation_euler = (D(35), 0, 0)
box('red_lamp', (0.14, 0.14, 0.14), (-10.8, 4, 3.0), P['red'])
rl = bpy.data.lights.new('red_l', 'POINT'); rl.energy = 160; rl.color = hexc('#ff3a3a')
link(bpy.data.objects.new('red_l', rl)).location = (-10.5, 4, 3.0)
flood = bpy.data.lights.new('flood', 'SPOT'); flood.energy = 2600; flood.spot_size = D(70); flood.spot_blend = 0.4
flood.color = hexc('#f4f1ff'); flood.shadow_soft_size = 0.25
fo = link(bpy.data.objects.new('flood', flood)); fo.location = (3.5, -3.5, 6.5)
ft = empty('flood_t', (-0.5, 3.0, 0)); c_ = fo.constraints.new('TRACK_TO'); c_.target = ft; c_.track_axis = 'TRACK_NEGATIVE_Z'; c_.up_axis = 'UP_Y'
area('sky_fill', (0, 0, 6), (0, 0, 0), 120, hexc('#7f8fc4'), (12, 12))
world(hexc('#0d1424'), 0.6)

# ============================================================ CHARACTERS
tina['root'].location = (-80, 0, 0)
dr = doug['root']
ricky = character('ricky', P['ricky'], 0.27, 0.55, P['iris_r'], 0.095, 0.11, lids=True)
rr = ricky['root']
# Ricky: beanie, mustache, tracksuit jacket, teal sleeves
rtop = ricky['top']
sphere('beanie', 0.285, P['beanie'], (0, 0, rtop - 0.1), (1, 1, 0.85), parent=rr, half=True)
bpy.ops.mesh.primitive_torus_add(major_radius=0.27, minor_radius=0.045, location=(0, 0, rtop - 0.1))
finish(bpy.context.active_object, P['beanie'], rr)
capsule('mustache', 0.022, 0.1, M['brow'], (0, -0.272, ricky['ez'] - 0.13), rot=(0, D(90), 0), parent=rr)
capsule('jacket', 0.283, 0.42, P['track'], (0, 0, ricky['zc'] - 0.13), parent=rr)
for sx in (-1, 1):
    box('jstripe', (0.03, 0.02, 0.55), (sx * 0.12, -0.278, ricky['zc'] - 0.15), P['stripe'], 0.008, rr)
box('zip', (0.012, 0.012, 0.6), (0, -0.284, ricky['zc'] - 0.15), P['stripe'], 0, rr)
for side in ('L', 'R'):
    for o in ricky['arms'][side].children:
        if o.type == 'CURVE': o.data.materials[0] = P['track']
for o in bpy.data.objects:
    if o.name.startswith('ricky_lid'): o.rotation_euler = (D(30), 0, 0)
# Doug: headphones over the hat
ez = doug['ez']
bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.025, location=(0, 0, ez + 0.03), rotation=(D(90), 0, 0))
band = bpy.context.active_object; band.scale = (1, 1, 1.2)
bm_ = band.modifiers.new('cut', 'BOOLEAN')
cutter = box('hp_cut', (1, 1, 0.6), (0, 0, ez - 0.27), P['hp']); cutter.hide_render = True; cutter.hide_viewport = True
bm_.object = cutter; finish(band, P['hp'], dr); cutter.parent = dr
for sx in (-1, 1):
    cyl('hp_cup', 0.085, 0.07, (sx * 0.33, 0, ez), P['hpcup'], rot=(0, D(90), 0), parent=dr)
    cyl('hp_pad', 0.07, 0.03, (sx * 0.305, 0, ez), P['hp'], rot=(0, D(90), 0), parent=dr)
# Doug arm sets: rig arms (for the tug) + "hands on headphones" arms
zc = doug['zc']
HP = {}
for sx, side in ((-1, 'L'), (1, 'R')):
    hpe = empty('hp_arm' + side, (0, 0, 0), dr)
    noodle('hp_arm' + side, [(sx * 0.30, 0, zc - 0.035), (sx * 0.5, 0.02, zc + 0.12), (sx * 0.39, -0.02, ez - 0.02)], 0.04, M['doug'], hpe)
    sphere('hp_hand' + side, 0.066, M['doug'], (sx * 0.39, -0.03, ez + 0.0), (1, 0.85, 1.1), parent=hpe)
    HP[side] = hpe
def vis(group_parent, f, on):
    for o in group_parent.children:
        o.hide_render = not on; o.keyframe_insert('hide_render', frame=f)
for o in doug['arms']['R'].children: o.hide_render = True
# bag + strap
bag = empty('bag')
box('bag_body', (0.1, 0.32, 0.26), (0, 0, 0), P['bag'], 0.03, bag)
box('bag_flap', (0.105, 0.33, 0.12), (0, 0, 0.07), mat('flap', hexc('#3a3e43'), 0.7), 0.02, bag)
strap_cu = bpy.data.curves.new('strap', 'CURVE'); strap_cu.dimensions = '3D'; strap_cu.bevel_depth = 0.018
strap_cu.bevel_resolution = 3; strap_cu.use_fill_caps = True
sp_ = strap_cu.splines.new('BEZIER'); sp_.bezier_points.add(2)
for b_ in sp_.bezier_points: b_.handle_left_type = b_.handle_right_type = 'AUTO'
strap = link(bpy.data.objects.new('strap', strap_cu)); strap.data.materials.append(P['bag'])
# stars for dizzy Ricky
STARS = []
for k in range(3):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.05)
    s = bpy.context.active_object; s.data.materials.append(P['star']); s.hide_render = True; STARS.append(s)

# ============================================================ CHOREOGRAPHY (global timeline)
def set_key(o, path, f, v): setattr(o, path, v); o.keyframe_insert(path, frame=f)
def doug_groove(f0, f1, x, y, heading=0, big=False):
    """dance in place: bounce on every beat, sway side to side, nod, alternate knee lifts."""
    b = 0
    for f in range(f0, f1 + 1, BEATF):
        s = 1 if b % 2 == 0 else -1
        set_key(dr, 'location', f, Vector((x + 0.04 * s, y, -0.03)))
        set_key(dr, 'rotation_euler', f, Euler((D(7), D(7 * s), D(heading))))
        mid = min(f + 7, f1)
        set_key(dr, 'location', mid, Vector((x, y, 0.025 if big else 0.012)))
        set_key(dr, 'rotation_euler', mid, Euler((D(-2), D(0), D(heading))))
        set_key(doug['legs'][0 if s > 0 else 1], 'rotation_euler', f, Euler((D(-20), 0, 0)))
        set_key(doug['legs'][1 if s > 0 else 0], 'rotation_euler', f, Euler((0, 0, 0)))
        set_key(doug['legs'][0], 'rotation_euler', mid, Euler((0, 0, 0)))
        set_key(doug['legs'][1], 'rotation_euler', mid, Euler((0, 0, 0)))
        b += 1

DX0, DY = 0.3, 2.5            # Doug's dance spot
RX = -1.35                    # Ricky's tug spot
# --- beats 1-6: Doug grooves toward camera, hands on headphones
walk(doug, 1, 90, (DX0, 5.2), (DX0, DY), 0, step_len=0.2, amp=28, hold_arm='LR', ease=(4, 10))
vis(doug['arms']['L'], 1, False)
for f in range(1, 91, BEATF):     # head-nod on each beat layered via the eyes/brows
    for i, bp in enumerate(doug['brows']):
        set_key(bp, 'location', f, bp.location.copy())
# --- beats 7-10: grooves in place; Ricky sneaks in and grabs the bag
doug_groove(bf(7), bf(11) - 1, DX0, DY)
walk(ricky, bf(7), bf(10) + 4, (-4.0, DY - 0.05), (RX + 0.05, DY), 90, step_len=0.15, amp=30, arm_amp=10, ease=(3, 6))
for f, lean in ((bf(7), 18), (bf(10) + 4, 18)):
    pass
GRAB = bf(10) + 8                 # frame 143
set_key(rr, 'location', GRAB - 4, Vector((RX + 0.05, DY, 0)))
set_key(rr, 'location', GRAB, Vector((RX + 0.15, DY, 0)))
for side in ('L', 'R'):
    set_key(ricky['arms'][side], 'rotation_euler', GRAB - 6, Euler((0, 0, 0)))
    set_key(ricky['arms'][side], 'rotation_euler', GRAB, Euler((D(-82), 0, D(6 if side == 'L' else -6))))
# --- beats 11-22: rhythmic tug-of-war that becomes a dance
vis(HP['L'], GRAB - 1, True); vis(HP['L'], GRAB, False)
vis(doug['arms']['L'], GRAB - 1, False); vis(doug['arms']['L'], GRAB, True)
set_key(doug['arms']['L'], 'rotation_euler', GRAB, Euler((0, D(78), 0)))
SPIN = bf(23)                     # frame 331
for b in range(11, 23):
    f = bf(b); m = f + 7
    pose = (b % 2 == 1)
    # on the beat: Ricky yanks (leans back), Doug gets pulled toward him
    set_key(rr, 'location', f, Vector((RX - 0.1, DY, 0)))
    set_key(rr, 'rotation_euler', f, Euler((D(-16), 0, D(90))))
    set_key(dr, 'location', f, Vector((DX0 - 0.06, DY, -0.03)))
    set_key(dr, 'rotation_euler', f, Euler((D(6), D(-12), D(0))))
    # off-beat: Doug pulls back with a groove, Ricky lurches forward
    set_key(rr, 'location', m, Vector((RX + 0.08, DY, 0.0)))
    set_key(rr, 'rotation_euler', m, Euler((D(14), 0, D(90))))
    set_key(dr, 'location', m, Vector((DX0 + 0.08, DY, 0.02)))
    set_key(dr, 'rotation_euler', m, Euler((D(-3), D(15), D(0))))
    set_key(doug['legs'][0], 'rotation_euler', f, Euler((D(-18), 0, 0)) if pose else Euler((0, 0, 0)))
    set_key(doug['legs'][1], 'rotation_euler', f, Euler((0, 0, 0)) if pose else Euler((D(-18), 0, 0)))
    set_key(doug['legs'][0], 'rotation_euler', m, Euler((0, 0, 0)))
    set_key(doug['legs'][1], 'rotation_euler', m, Euler((0, 0, 0)))
    for k, leg in enumerate(ricky['legs']):
        set_key(leg, 'rotation_euler', f, Euler((D(-25 if k == 0 else 15), 0, 0)))
        set_key(leg, 'rotation_euler', m, Euler((D(10 if k == 0 else -10), 0, 0)))
# Ricky's face: strained brows; Doug: eyes closed-ish vibing
RBZ = [bp.location.z for bp in ricky['brows']]
for i, bp in enumerate(ricky['brows']):
    sx = -1 if i == 0 else 1
    set_key(bp, 'location', GRAB, Vector((bp.location.x, bp.location.y, RBZ[i] - 0.02)))
    set_key(bp, 'rotation_euler', GRAB, Euler((0, sx * D(18), 0)))
DOUG_LIDS = [o for o in bpy.data.objects if o.name.startswith('doug_lid')]
for o in DOUG_LIDS:
    set_key(o, 'rotation_euler', 1, Euler((D(40), 0, 0)))          # blissful, half-closed the whole time
# --- beat 23: the spin; Ricky gets flung
set_key(dr, 'location', SPIN, Vector((DX0, DY, -0.02)))
set_key(dr, 'rotation_euler', SPIN, Euler((0, 0, 0)))
set_key(dr, 'location', SPIN + 7, Vector((DX0, DY, 0.06)))
set_key(dr, 'rotation_euler', SPIN + 14, Euler((0, 0, D(360))))
set_key(dr, 'location', SPIN + 14, Vector((DX0, DY, -0.02)))
RELEASE = SPIN + 4
path = [(SPIN, (RX - 0.1, DY, 0), (D(-16), 0, D(90))),
        (SPIN + 3, (RX + 0.25, DY - 0.35, 0.25), (D(-30), 0, D(150))),
        (SPIN + 8, (RX - 0.4, DY - 0.2, 0.7), (D(-70), 0, D(250))),
        (SPIN + 15, (RX - 1.1, DY + 0.1, 0.45), (D(-90), 0, D(400))),
        (SPIN + 19, (RX - 1.35, DY + 0.15, 0.27), (D(-90), 0, D(450))),
        (SPIN + 23, (RX - 1.45, DY + 0.15, 0.36), (D(-90), 0, D(450))),
        (SPIN + 27, (RX - 1.5, DY + 0.15, 0.27), (D(-90), 0, D(450)))]
for f, loc, rot in path:
    set_key(rr, 'location', f, Vector(loc)); set_key(rr, 'rotation_euler', f, Euler(rot))
for side in ('L', 'R'):
    set_key(ricky['arms'][side], 'rotation_euler', RELEASE + 6, Euler((D(-150), 0, D(30 if side == 'L' else -30))))
    set_key(ricky['arms'][side], 'rotation_euler', SPIN + 18, Euler((0, D(80 if side == 'L' else -80), 0)))
for k, leg in enumerate(ricky['legs']):
    set_key(leg, 'rotation_euler', RELEASE + 6, Euler((D(-40 if k else 20), 0, 0)))
vis(HP['L'], RELEASE + 2, False); vis(HP['L'], RELEASE + 3, True)
vis(doug['arms']['L'], RELEASE + 2, True); vis(doug['arms']['L'], RELEASE + 3, False)
# --- beats 24-28: Doug keeps grooving with his bag; Ricky dizzy on the ground
doug_groove(SPIN + 15, bf(29) - 1, DX0, DY, heading=360, big=True)
DIZZY0 = SPIN + 27
for e_i, e in enumerate(ricky['eyes']):
    for f in range(DIZZY0, 481, 3):
        a = (f - DIZZY0) / 6.0 * (1 if e_i else -1)
        set_key(e, 'rotation_euler', f, Euler((D(14) * math.sin(a), 0, D(14) * math.cos(a))))
for k, s in enumerate(STARS):
    s.hide_render = True; s.keyframe_insert('hide_render', frame=1)
    s.hide_render = False; s.keyframe_insert('hide_render', frame=DIZZY0)
# --- beats 29-32: turns and grooves away, hands back on headphones
TURN = bf(29)
set_key(dr, 'rotation_euler', TURN, Euler((0, 0, D(360))))
set_key(dr, 'location', TURN, Vector((DX0, DY, 0)))
walk(doug, TURN + 6, 480, (DX0, DY), (DX0 + 0.1, 5.2), 180 + 360, step_len=0.2, amp=28, hold_arm='LR', ease=(5, 2))
set_key(dr, 'rotation_euler', TURN + 5, Euler((0, 0, D(540))))

# ---------------------------------------------------------------- bake bag, strap, stars per frame
bpy.context.view_layer.update()
def wpos(o): return o.matrix_world.translation.copy()
handsR = [bpy.data.objects['ricky_handL'], bpy.data.objects['ricky_handR']]
dhandL = bpy.data.objects['doug_handL']
for f in range(1, 481):
    scene.frame_set(f)
    Mw = dr.matrix_world
    if GRAB <= f < RELEASE:
        bp = (wpos(handsR[0]) + wpos(handsR[1])) / 2 + Vector((0.05, 0, -0.08))
        brot = Euler((0, 0, D(90)))
        a = wpos(dhandL); c = bp + Vector((0, 0, 0.13))
        mid = (a + c) / 2 + Vector((0, 0, -0.03))
    else:
        bp = Mw @ Vector((-0.38, -0.02, 0.62))
        brot = Euler((0, 0, dr.matrix_world.to_euler().z))
        a = Mw @ Vector((0.22, -0.08, zc + 0.22)); c = Mw @ Vector((-0.36, -0.02, 0.75)); mid = Mw @ Vector((-0.05, -0.335, zc + 0.02))
    bag.location = bp; bag.rotation_euler = brot
    bag.keyframe_insert('location', frame=f); bag.keyframe_insert('rotation_euler', frame=f)
    for pt, v in zip(sp_.bezier_points, (a, mid, c)):
        pt.co = v; pt.keyframe_insert('co', frame=f)
        pt.handle_left_type = pt.handle_right_type = 'AUTO'
    if f >= DIZZY0:
        reyes = [o for o in bpy.data.objects if o.name.startswith('ricky_eye')]
        head = sum((wpos(o) for o in reyes), Vector()) / len(reyes) + Vector((0, 0, 0.3))
        for k, s in enumerate(STARS):
            ang = f / 5.0 + k * 2.094
            s.location = head + Vector((0.18 * math.cos(ang), 0.18 * math.sin(ang), 0.06 * math.sin(ang * 2)))
            s.rotation_euler = (f / 4, f / 3, 0)
            s.keyframe_insert('location', frame=f); s.keyframe_insert('rotation_euler', frame=f)
scene.frame_set(1)

# ============================================================ CAMERAS / SHOTS
SHOTS = {
    'R1': (1, 90), 'R2': (91, 150), 'R3': (151, 210), 'R4': (211, 300),
    'R5': (301, 375), 'R6': (376, 420), 'R7': (421, 480),
}
f0, f1 = SHOTS[SHOT]
cam_data.dof.aperture_fstop = 4.0
if SHOT == 'R1':     # in front, low, Doug grooving toward us
    for f, y in ((1, 0.2), (90, 0.6)):
        set_key(cam, 'location', f, Vector((DX0 + 0.3, y + 0.4, 0.95)))
    for f in range(1, 91, 6):
        scene.frame_set(f); set_key(target, 'location', f, wpos(dr) + Vector((0, 0, 1.15)))
        set_key(focus, 'location', f, wpos(dr) + Vector((0, -0.3, 1.1)))
    cam_data.lens = 26
elif SHOT in ('R2', 'R5'):   # wide 3/4
    if SHOT == 'R2':
        set_key(cam, 'location', f0, Vector((1.55, -0.35, 1.2))); set_key(cam, 'location', f1, Vector((1.4, -0.15, 1.18)))
        target.location = (-0.75, DY + 0.1, 0.8); focus.location = (-0.3, DY, 0.9); cam_data.lens = 24
    else:
        set_key(cam, 'location', f0, Vector((1.7, -0.9, 1.3))); set_key(cam, 'location', f1, Vector((1.55, -0.75, 1.28)))
        target.location = (-1.25, DY + 0.1, 0.7); focus.location = (-0.8, DY, 0.8); cam_data.lens = 21
elif SHOT == 'R3':   # low behind Ricky, looking up at Doug
    set_key(cam, 'location', f0, Vector((RX - 1.45, DY - 1.55, 0.45))); set_key(cam, 'location', f1, Vector((RX - 1.3, DY - 1.4, 0.45)))
    target.location = (DX0 - 0.15, DY, 1.2); focus.location = (DX0, DY, 1.1)
    cam_data.lens = 18; cam_data.dof.aperture_fstop = 5.0
elif SHOT == 'R4':   # side-on wide: synchronized push-pull
    set_key(cam, 'location', f0, Vector((-0.45, -1.9, 0.95))); set_key(cam, 'location', f1, Vector((-0.45, -1.7, 0.95)))
    target.location = (-0.45, DY, 0.85); focus.location = (-0.45, DY, 0.9)
    cam_data.lens = 26
elif SHOT == 'R6':   # Ricky dazed on the ground, Doug dancing behind
    scene.frame_set(DIZZY0 + 2); rp = wpos(rr)
    reyes = [o for o in bpy.data.objects if o.name.startswith('ricky_eye')]
    head = sum((wpos(o) for o in reyes), Vector()) / len(reyes)
    set_key(cam, 'location', f0, head + Vector((0.45, -0.75, 0.75))); set_key(cam, 'location', f1, head + Vector((0.4, -0.68, 0.7)))
    target.location = head + Vector((0.1, 0.05, 0.12)); focus.location = head
    cam_data.lens = 26; cam_data.dof.aperture_fstop = 3.2
elif SHOT == 'R7':   # from behind: Doug grooves away into the night
    set_key(cam, 'location', f0, Vector((DX0 - 0.35, 0.3, 1.0))); set_key(cam, 'location', f1, Vector((DX0 - 0.3, 0.8, 1.0)))
    for f in range(f0, f1 + 1, 6):
        scene.frame_set(f); set_key(target, 'location', f, wpos(dr) + Vector((0, 0, 1.0)))
        set_key(focus, 'location', f, wpos(dr) + Vector((0, 0, 1.0)))
    cam_data.lens = 24
scene.frame_set(f0)

# render this shot's frame range
FR = FR or f'{f0}-{f1}'
render(480)
