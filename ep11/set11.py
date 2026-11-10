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
