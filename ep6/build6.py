"""Tube Town Ep6 - "Five minutes away".  usage: python3 build6.py SHOT OUTDIR [--still F] [--samples N] [--pct P] [--step S]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, '..', 'tubetown', 'lib.py')).read())
TEX = os.path.join(HERE, 'tex')
X0 = 30.0  # bathroom set offset

def objs_snapshot():
    return set(bpy.data.objects)

def img_node_mat(name, paths, strength=1.0):
    """Emissive image material; with two paths, a keyable mix between them (input 'Fac')."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes; l = nt.links
    n.remove(n['Principled BSDF'])
    em = n.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = strength
    imgs = []
    for p in paths:
        t = n.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(p); t.extension = 'CLIP'; imgs.append(t)
    if len(imgs) == 1:
        l.new(imgs[0].outputs['Color'], em.inputs['Color']); mix = None
    else:
        mix = n.new('ShaderNodeMixRGB'); mix.inputs['Fac'].default_value = 0
        l.new(imgs[0].outputs['Color'], mix.inputs['Color1']); l.new(imgs[1].outputs['Color'], mix.inputs['Color2'])
        l.new(mix.outputs['Color'], em.inputs['Color'])
    l.new(em.outputs[0], n['Material Output'].inputs['Surface'])
    return m, mix, em

def brick_mat(name, c1, c2, mortar, scale=6, w=0.5, h=0.25, offset=0.5, rough=0.8, vertical=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes; l = nt.links
    b = n['Principled BSDF']; b.inputs['Roughness'].default_value = rough
    tc = n.new('ShaderNodeTexCoord'); bk = n.new('ShaderNodeTexBrick')
    bk.inputs['Color1'].default_value = (*c1, 1); bk.inputs['Color2'].default_value = (*c2, 1)
    bk.inputs['Mortar'].default_value = (*mortar, 1); bk.inputs['Scale'].default_value = scale
    bk.inputs['Brick Width'].default_value = w; bk.inputs['Row Height'].default_value = h
    bk.inputs['Mortar Size'].default_value = 0.015; bk.offset = offset
    mp = n.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (D(90) if vertical else 0, 0, 0)
    sep = n.new('ShaderNodeSeparateXYZ'); com = n.new('ShaderNodeCombineXYZ')
    l.new(tc.outputs['Object'], sep.inputs[0])
    if vertical:   # map wall faces: x -> u, z -> v (plus y so side walls also tile)
        add = n.new('ShaderNodeMath'); add.inputs[1].default_value = 0
        l.new(sep.outputs['X'], add.inputs[0]); 
        add2 = n.new('ShaderNodeMath'); l.new(add.outputs[0], add2.inputs[0]); l.new(sep.outputs['Y'], add2.inputs[1])
        l.new(add2.outputs[0], com.inputs['X']); l.new(sep.outputs['Z'], com.inputs['Y'])
    else:
        l.new(sep.outputs['X'], com.inputs['X']); l.new(sep.outputs['Y'], com.inputs['Y'])
    l.new(com.outputs[0], bk.inputs['Vector']); l.new(bk.outputs['Color'], b.inputs['Base Color'])
    return m

def text(body, size, loc, m, rot=(D(90), 0, 0), extrude=0.004, parent=None):
    cu = bpy.data.curves.new('txt', 'FONT'); cu.body = body; cu.size = size
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = extrude
    o = link(bpy.data.objects.new('txt', cu)); o.location = loc; o.rotation_euler = rot
    o.data.materials.append(m)
    if parent: o.parent = parent
    return o

def cyl(name, r, depth, loc, m, rot=(0, 0, 0), verts=48, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    return finish(o, m, parent)

E = dict(
    brick=brick_mat('brick', hexc('#8c3a34'), hexc('#7a302b'), hexc('#c9b8a6'), 4, 0.5, 0.18, vertical=True),
    sidewalk=brick_mat('sidewalk', hexc('#a9a49c'), hexc('#a29d95'), hexc('#7f7a73'), 0.6, 0.5, 0.5, 0.0, 0.9),
    asphalt=mat('asphalt', hexc('#2b2b30'), 0.9),
    curb=mat('curb', hexc('#bdb8af'), 0.85),
    cream=mat('cream', hexc('#f1e6cf'), 0.5, 0.2),
    gold=mat('gold2', hexc('#d8b25a'), 0.3),
    glass=mat('doorglass', hexc('#1c1a1a'), 0.1, 0.6, hexc('#ffb36b'), 0.4),
    board=mat('board', hexc('#fffaf0'), 0.5, 0, hexc('#fff3dc'), 1.2),
    letters=mat('letters', hexc('#1d1d22'), 0.5),
    red=mat('signred', hexc('#b8282e'), 0.4, 0.3),
    signlet=mat('signlet', (0, 0, 0), 0.5, 0, hexc('#fff1c9'), 4),
    bulb=mat('bulb', (0, 0, 0), 0.5, 0, hexc('#ffe2a3'), 3),
    pole=mat('pole', hexc('#24362c'), 0.4, 0.3),
    lamp=mat('lamp', (0, 0, 0), 0.5, 0, hexc('#ffc77a'), 0.2),
    bldg1=mat('bldg1', hexc('#3f6f73'), 0.8),
    bldg2=mat('bldg2', hexc('#c99a3e'), 0.8),
    win=mat('bwin', hexc('#22262e'), 0.15, 0.5, hexc('#ffd59a'), 0.0),
    can=mat('can', hexc('#3a4a40'), 0.5, 0.2),
)
P1, _, _ = img_node_mat('poster1', [os.path.join(TEX, 'poster1.png')], 1.4)
P2, _, _ = img_node_mat('poster2', [os.path.join(TEX, 'poster2.png')], 1.4)

# ============================================================ EXTERIOR (movie theater)
before = objs_snapshot()
box('sidewalk', (24, 8, 0.1), (0, 2.3, -0.05), E['sidewalk'])
box('curb', (24, 0.22, 0.2), (0, -1.81, -0.1), E['curb'])
box('street', (24, 12, 0.2), (0, -7.9, -0.25), E['asphalt'])
box('facade', (8, 0.3, 5.2), (0, 1.35, 2.6), E['brick'])
box('bldg_l', (5, 0.3, 6.5), (-6.5, 1.5, 3.25), E['bldg1'])
box('bldg_r', (5, 0.3, 5.8), (6.5, 1.5, 2.9), E['bldg2'])
for bx in (-6.5, 6.5):
    for i in range(3):
        for j in range(3):
            box('bwin', (0.7, 0.05, 0.9), (bx - 1.4 + i * 1.4, 1.34, 1.2 + j * 1.6), E['win'], 0.01)
# entrance
box('door_recess', (2.0, 0.1, 2.4), (0, 1.22, 1.2), E['letters'])
for dx in (-0.45, 0.45):
    box('door_frame', (0.86, 0.06, 2.18), (dx, 1.16, 1.09), E['gold'], 0.01)
    box('door_glass', (0.74, 0.07, 2.02), (dx, 1.15, 1.07), E['glass'])
    box('door_bar', (0.5, 0.04, 0.04), (dx, 1.1, 1.05), E['gold'], 0.01)
# marquee
box('marquee', (3.8, 0.75, 0.75), (0, 0.85, 2.78), E['cream'], 0.03)
box('board', (3.3, 0.02, 0.5), (0, 0.47, 2.78), E['board'])
text('NOW SHOWING', 0.13, (0, 0.455, 2.91), E['letters'])
text('ATTACK OF THE NOODLES', 0.15, (0, 0.455, 2.68), E['letters'])
for k in range(25):
    x = -1.8 + k * 0.15
    for z in (2.44, 3.12):
        sphere('bulb', 0.026, E['bulb'], (x, 0.46, z))
# vertical sign
box('vsign', (0.55, 0.16, 1.6), (0, 0.95, 4.05), E['red'], 0.02)
for i, ch in enumerate('CINEMA'):
    text(ch, 0.22, (0, 0.86, 4.65 - i * 0.24), E['signlet'])
# posters
for px, pm in ((-1.65, P1), (1.65, P2)):
    box('pframe', (0.72, 0.06, 1.02), (px, 1.18, 1.35), E['gold'], 0.01)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(px, 1.145, 1.35), rotation=(D(90), 0, 0))
    po = bpy.context.active_object; po.scale = (0.6, 0.9, 1); po.data.materials.append(pm)
# street lamp
cyl('pole', 0.045, 3.3, (1.85, -1.4, 1.65), E['pole'])
box('lamp_arm', (0.45, 0.06, 0.06), (1.65, -1.4, 3.25), E['pole'])
cyl('lamp_head', 0.12, 0.14, (1.45, -1.4, 3.18), E['pole'])
lamp_bulb = sphere('lamp_bulb', 0.08, E['lamp'], (1.45, -1.4, 3.08), (1, 1, 0.6))
cyl('trash', 0.22, 0.75, (-2.3, -1.2, 0.375), E['can'])
# lights
sun_d = bpy.data.lights.new('sun', 'SUN'); sun_d.energy = 3.2; sun_d.color = hexc('#ffd9b0'); sun_d.angle = D(3)
sun = link(bpy.data.objects.new('sun', sun_d)); sun.rotation_euler = (D(52), 0, D(-38))
marq_l = area('marquee_l', (0, 0.25, 2.35), (0, 0, 0), 0, hexc('#ffd59a'), (3.4, 0.5)); marq_l.rotation_euler = (D(180), 0, 0)
lamp_d = bpy.data.lights.new('lamp_pt', 'POINT'); lamp_d.energy = 0; lamp_d.color = hexc('#ffb866'); lamp_d.shadow_soft_size = 0.15
lamp_l = link(bpy.data.objects.new('lamp_pt', lamp_d)); lamp_l.location = (1.45, -1.4, 2.95)
door_l = area('door_l', (0, 0.9, 1.2), (D(90), 0, 0), 0, hexc('#ffb36b'), (1.6, 2.0))
ext_fill = area('ext_fill', (0.5, -3.0, 3.0), (D(55), 0, 0), 30, hexc('#cfd9ff'), (4, 2))
EXT = objs_snapshot() - before

# ============================================================ BATHROOM
before = objs_snapshot()
B = dict(
    floor=brick_mat('bfloor', hexc('#e9e6e1'), hexc('#d9d5cf'), hexc('#b9b4ad'), 2.5, 0.5, 0.5, 0.0, 0.4),
    wall=brick_mat('bwall', hexc('#f2b8c6'), hexc('#efb0bf'), hexc('#fbe9ee'), 3.0, 0.5, 0.5, 0.0, 0.35, vertical=True),
    wall2=brick_mat('bwall2', hexc('#a9dcc9'), hexc('#a2d6c2'), hexc('#e8f6f0'), 3.0, 0.5, 0.5, 0.0, 0.35, vertical=True),
    tub=mat('tub', hexc('#fbfbf8'), 0.12, 0.8),
    foam=mat('foam', hexc('#f4f7fb'), 0.45, 0.3),
    bubble=mat('bubble', hexc('#eef3fb'), 0.15, 0.9),
    mask=mat('mask', hexc('#c7e0b5'), 0.9),
    cuc_out=mat('cuc_out', hexc('#2f6b2f'), 0.5),
    cuc_in=mat('cuc_in', hexc('#cfe9a8'), 0.6, 0.3),
    towel=mat('towel', hexc('#f49ac1'), 0.95, 0, sheen=0.8),
    wax=mat('wax', hexc('#fff4e2'), 0.5),
    flame=mat('flame', (0, 0, 0), 0.5, 0, hexc('#ffb347'), 20),
    duck=mat('duck', hexc('#ffd23a'), 0.3, 0.6),
    beak=mat('beak', hexc('#ff8a2a'), 0.4),
    shelf=mat('shelf', hexc('#c99567'), 0.6),
)
box('bfloor', (6, 6, 0.1), (X0, -1.0, -0.05), B['floor'])
box('bwall', (6, 0.1, 4), (X0, 1.1, 2), B['wall'])
box('bwall2', (0.1, 6, 4), (X0 - 1.6, -1.0, 2), B['wall2'])
box('tub', (1.75, 0.82, 0.62), (X0, 0.35, 0.31), B['tub'], 0.2)
box('foam', (1.5, 0.62, 0.06), (X0, 0.35, 0.6), B['foam'], 0.03)
import random
rnd = random.Random(7)
for i in range(170):
    x = X0 + rnd.uniform(-0.74, 0.74); y = rnd.uniform(0.06, 0.66)
    if abs(x - X0) < 0.2 and y < 0.2: continue  # keep Tina's front clear-ish
    r = rnd.choice([0.035, 0.05, 0.06, 0.08, 0.1])
    sphere('bub', r, B['bubble'], (x, y, 0.6 + rnd.uniform(0.0, 0.07) + r * 0.3))
for fx in (-0.7, 0.7):
    for fy in (0.05, 0.65):
        sphere('foot', 0.07, E['gold'], (X0 + fx, fy, 0.03))
# duck
sphere('duck_body', 0.07, B['duck'], (X0 + 0.5, 0.15, 0.7), (1.2, 1, 0.8))
sphere('duck_head', 0.045, B['duck'], (X0 + 0.55, 0.13, 0.78))
sphere('duck_beak', 0.022, B['beak'], (X0 + 0.6, 0.1, 0.775), (1.4, 0.8, 0.5))
# candles
for i, (cx, cy, h) in enumerate(((X0 - 0.95, 0.75, 0.22), (X0 - 1.12, 0.6, 0.15), (X0 - 0.98, 0.45, 0.1))):
    cyl('candle', 0.05, h, (cx, cy, h / 2), B['wax'])
    sphere('flame', 0.018, B['flame'], (cx, cy, h + 0.03), (1, 1, 1.8))
cand = bpy.data.lights.new('candle_pt', 'POINT'); cand.energy = 12; cand.color = hexc('#ff9a3d'); cand.shadow_soft_size = 0.1
link(bpy.data.objects.new('candle_pt', cand)).location = (X0 - 1.0, 0.6, 0.35)
box('shelf', (0.7, 0.18, 0.04), (X0 + 0.9, 1.0, 1.55), B['shelf'], 0.01)
capsule('bpot', 0.07, 0.05, M['pot'], (X0 + 0.75, 1.0, 1.66))
sphere('bplant', 0.1, M['plant'], (X0 + 0.75, 1.0, 1.8), (1, 1, 1.2))
for k, c in enumerate(('#7fc8f8', '#ffd6a5')):
    capsule('bottle', 0.035, 0.08, mat('bottle%d' % k, hexc(c), 0.2, 0.7), (X0 + 1.0 + k * 0.12, 1.0, 1.65))
area('bath_key', (X0 + 0.6, -0.6, 2.6), (D(25), D(15), 0), 55, hexc('#ffe7cf'), (1.6, 1.6))
area('bath_fill', (X0 - 0.5, -2.0, 1.6), (D(80), 0, 0), 18, hexc('#ffd1e0'), (2, 1.2))
area('bath_rim', (X0 + 1.4, 0.9, 1.6), (D(-60), D(40), 0), 14, hexc('#bfe8ff'), (0.8, 0.8))
BATH = objs_snapshot() - before

# ---------------------------------------------------------------- Doug's phone (empty tracked to his eyes)
def make_phone(name, parent, loc, chat_paths, eye_target):
    pe = empty(name, loc, parent)
    box(name + '_body', (0.09, 0.012, 0.17), (0, 0, 0), M['phone'], 0.008, pe)
    sm, mix, em = img_node_mat(name + '_scr', chat_paths, 1.6)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.0075, 0), rotation=(D(90), 0, 0))
    sc = bpy.context.active_object; sc.scale = (0.08, 0.155, 1); sc.parent = pe; sc.data.materials.append(sm)
    c = pe.constraints.new('TRACK_TO'); c.target = eye_target; c.track_axis = 'TRACK_NEGATIVE_Y'; c.up_axis = 'UP_Z'
    return pe, mix

doug_eye_t = empty('doug_eye_t', (0, -0.33, doug['ez']), doug['root'])

def doug_brows_low(amount=0.04):
    for i, bp in enumerate(doug['brows']):
        sx = -1 if i == 0 else 1
        bp.location.z -= amount; bp.rotation_euler = (0, sx * D(14), 0)

def set_visible(group, vis):
    for o in group:
        o.hide_render = not vis

def world(color, strength):
    w = scene.world or bpy.data.worlds.new('w'); scene.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (*color, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = strength

def night_mode():
    sun.hide_render = True
    world(hexc('#0b1022'), 0.9)
    marq_l.data.energy = 140; lamp_d.energy = 90; door_l.data.energy = 40; ext_fill.data.energy = 6
    for m_, s_ in ((E['bulb'], 14), (E['board'], 2.2), (E['signlet'], 9), (E['lamp'], 12), (E['glass'], 0.7), (E['win'], 1.0), (P1, 2.0), (P2, 2.0)):
        n = m_.node_tree.nodes
        node = n.get('Principled BSDF') or n.get('Emission')
        node.inputs['Emission Strength' if node.type == 'BSDF_PRINCIPLED' else 'Strength'].default_value = s_

def day_mode():
    world(hexc('#8fb3e8'), 0.9)

# ---------------------------------------------------------------- shots
N = 60
EXT_SHOTS = ('E1', 'E2', 'E5', 'E6', 'E7')
night = SHOT in ('E5', 'E6', 'E7')
dr = doug['root']; tr = tina['root']
if SHOT in EXT_SHOTS:
    set_visible(BATH, False); tr.location = (-50, 0, 0)
    dr.location = (-0.75, -0.35, 0); rot_doug(dr, 0)
    night_mode() if night else day_mode()
    hold = SHOT != 'E7'
    if hold:
        doug['arms']['R'].rotation_euler = (D(-62), 0, D(-38))
    paths = [os.path.join(TEX, p + '.png') for p in (('chat_c', 'chat_d') if night else ('chat_a', 'chat_b'))]
    if hold:
        bpy.context.view_layer.update()
        hw = bpy.data.objects['doug_handR'].matrix_world.translation.copy()
        ew = doug_eye_t.matrix_world.translation.copy()
        toward = (ew - hw).normalized()
        phone, pmix = make_phone('dphone', None, hw + toward * 0.05 + Vector((0, 0, 0.07)), paths, doug_eye_t)
else:
    set_visible(EXT, False); dr.location = (-50, 0, 0)
    world(hexc('#2a1f24'), 0.4)
    tr.location = (X0, 0.35, -0.3); rot_doug(tr, 0)
    tina['mouth'].location.y -= 0.03
    ez = tina['ez']
    sphere('mask', 1.0, B['mask'], (0, -0.262, ez - 0.03), (0.25, 0.045, 0.21), parent=tr)
    for e, sx in zip(tina['eyes'], (-1, 1)):
        ex = sx * 0.13
        cyl('cuc', 0.08, 0.016, (ex, -0.345, ez), B['cuc_out'], rot=(D(90), 0, 0), parent=tr)
        cyl('cuc_in', 0.068, 0.006, (ex, -0.356, ez), B['cuc_in'], rot=(D(90), 0, 0), parent=tr)
        for k in range(5):
            a = k * 2 * math.pi / 5
            sphere('seed', 0.008, B['wax'], (ex + 0.03 * math.cos(a), -0.36, ez + 0.03 * math.sin(a)), (1, 0.4, 1.4), parent=tr)
    top = tina['top']
    sphere('towel', 0.27, B['towel'], (0, 0, top - 0.02), (1, 1, 0.75), parent=tr)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.25, minor_radius=0.075, location=(0, 0, top - 0.09))
    finish(bpy.context.active_object, B['towel'], tr)

def tap(hip, f0, f1, period, amp=12):
    for f in range(f0, f1 + 1, 2):
        v = max(0, math.sin((f - f0) / period * 2 * math.pi))
        hip.rotation_euler = (D(-amp) * v, 0, 0); hip.keyframe_insert('rotation_euler', frame=f)

if SHOT in ('E1', 'E5'):          # wide, outside the theater
    N = 72 if SHOT == 'E1' else 66
    key(cam, 'location', 1, Vector((1.45, -3.5, 1.25))); key(cam, 'location', N, Vector((1.32, -3.25, 1.24)))
    target.location = (-0.4, 0.2, 1.62); focus.location = (-0.75, -0.35, 1.2)
    cam_data.lens = 22; cam_data.dof.aperture_fstop = 4.0
    if SHOT == 'E1':
        tap(doug['legs'][0], 1, N, 10)
        for e in doug['eyes']:
            key(e, 'rotation_euler', 1, Euler((D(20), 0, 0))); key(e, 'rotation_euler', 26, Euler((D(20), 0, 0)))
            key(e, 'rotation_euler', 31, Euler((D(-4), 0, D(-30)))); key(e, 'rotation_euler', 48, Euler((D(-4), 0, D(-30))))
            key(e, 'rotation_euler', 53, Euler((D(20), 0, 0)))
    else:
        doug_brows_low()
        tap(doug['legs'][0], 1, N, 18, 8)
        dr.rotation_euler = (D(3), 0, 0)
        for e in doug['eyes']: e.rotation_euler = (D(20), 0, 0)
elif SHOT in ('E2', 'E6'):        # phone close-up (Doug's POV)
    N = 48 if SHOT == 'E2' else 54
    if SHOT == 'E6': doug_brows_low()
    bpy.context.view_layer.update()
    pw = phone.matrix_world.translation.copy(); ew = doug_eye_t.matrix_world.translation.copy()
    d = (ew - pw).normalized()
    side = d.cross(Vector((0, 0, 1))).normalized()
    Mw = phone.matrix_world.to_3x3().normalized()
    nrm = -(Mw @ Vector((0, 1, 0))); up = Mw @ Vector((0, 0, 1))
    cam.constraints[0].mute = True
    zc_ = nrm.normalized(); yc_ = (up - zc_ * up.dot(zc_)).normalized(); xc_ = yc_.cross(zc_)
    from mathutils import Matrix
    cam.rotation_euler = Matrix((xc_, yc_, zc_)).transposed().to_euler()
    key(cam, 'location', 1, pw + nrm * 0.30 - up * 0.01); key(cam, 'location', N, pw + nrm * 0.27 - up * 0.01)
    focus.location = pw
    cam_data.lens = 52; cam_data.dof.aperture_fstop = 2.8
    fs = 14 if SHOT == 'E2' else 16
    pmix.inputs['Fac'].default_value = 0; pmix.inputs['Fac'].keyframe_insert('default_value', frame=fs - 1)
    pmix.inputs['Fac'].default_value = 1; pmix.inputs['Fac'].keyframe_insert('default_value', frame=fs)
elif SHOT == 'E7':                # Doug's flat stare into the camera
    N = 72
    ext_fill.data.energy = 22
    target.location = (-0.75, -0.35, 1.45); focus.location = (-0.75, -0.66, 1.3)
    cam_data.lens = 30; cam_data.dof.aperture_fstop = 2.2
    for i, bp in enumerate(doug['brows']):
        sx = -1 if i == 0 else 1
        z0 = bp.location.z
        key(bp, 'location', 6, Vector((bp.location.x, bp.location.y, z0 - 0.015)))
        key(bp, 'rotation_euler', 6, Euler((0, sx * D(4), 0)))
        key(bp, 'location', 44, Vector((bp.location.x, bp.location.y, z0 - 0.05)))
        key(bp, 'rotation_euler', 44, Euler((0, sx * D(16), 0)))
    for e in doug['eyes']: e.rotation_euler = (D(2), 0, 0)
    key(dr, 'location', 46, Vector((-0.75, -0.35, 0))); key(dr, 'location', 54, Vector((-0.75, -0.35, -0.025)))
    key(dr, 'location', 66, Vector((-0.75, -0.35, -0.02)))
    key(cam, 'location', 1, Vector((-0.72, -1.7, 1.3))); key(cam, 'location', N, Vector((-0.73, -1.6, 1.31)))
elif SHOT == 'E3':                # bath wide: Tina relaxing, phone up, cucumbers on
    N = 60
    key(cam, 'location', 1, Vector((X0 + 1.35, -2.15, 1.3))); key(cam, 'location', N, Vector((X0 + 1.2, -1.95, 1.27)))
    target.location = (X0 - 0.05, 0.3, 0.85); focus.location = (X0, 0.1, 0.85)
    cam_data.lens = 26; cam_data.dof.aperture_fstop = 3.2
    tina['arms']['R'].rotation_euler = (D(-118), 0, D(-22))
    for f in range(1, N + 1, 4):
        tr.rotation_euler = (0, D(3) * math.sin(f / 10), 0); tr.keyframe_insert('rotation_euler', frame=f)
elif SHOT == 'E4':                # close-up: dictates "Almost there, babe."
    N = 72
    key(cam, 'location', 1, Vector((X0 + 0.28, -0.88, 0.98))); key(cam, 'location', N, Vector((X0 + 0.25, -0.8, 0.98)))
    target.location = (X0 + 0.02, 0.3, 0.9); focus.location = (X0, 0.03, 0.9)
    cam_data.lens = 32; cam_data.dof.aperture_fstop = 2.4
    a = tina['arms']['R']
    key(a, 'rotation_euler', 1, Euler((D(-118), 0, D(-22)))); key(a, 'rotation_euler', 8, Euler((D(-128), 0, D(-48))))
    key(a, 'rotation_euler', 54, Euler((D(-128), 0, D(-48)))); key(a, 'rotation_euler', 62, Euler((D(-118), 0, D(-22))))
    lipsync(tina['mouth'], os.path.join(HERE, 'vo', 'tina.wav'), 12, 2, 0.8, 1.6)

render(N)
