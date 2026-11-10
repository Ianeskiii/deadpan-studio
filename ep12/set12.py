# ============================================================ COZY COFFEE SHOP (warm, daytime)
C_ = dict(
    floor=brick_mat('planks', hexc('#8a5a3a'), hexc('#7d5032'), hexc('#5e3a24'), 1.2, 1.6, 0.18, 0.37, 0.55),
    tile=brick_mat('subway', hexc('#f1ece2'), hexc('#ebe5da'), hexc('#c9c1b4'), 6.0, 0.5, 0.25, 0.5, 0.3, vertical=True),
    plaster=mat('plaster', hexc('#d9c6a5'), 0.9),
    green=mat('wallgreen', hexc('#2f5446'), 0.85),
    wood=mat('wood', hexc('#9b6a43'), 0.45, 0.2),
    wood_dk=mat('wood_dk', hexc('#5a3b26'), 0.5, 0.2),
    top=mat('ctop', hexc('#ece6da'), 0.25, 0.4),
    steel=mat('steel', hexc('#b9bec4'), 0.18, 0.6),
    black=mat('blk', hexc('#1c1c1e'), 0.4, 0.3),
    board=mat('board', hexc('#1f2421'), 0.85),
    chalk=mat('chalk', hexc('#f2efe6'), 0.8),
    chalk_y=mat('chalk_y', hexc('#f2c45a'), 0.8),
    cupw=mat('cupw', hexc('#fbfaf6'), 0.35, 0.3),
    sleeve=mat('sleeve', hexc('#a8733f'), 0.85),
    lid=mat('cuplid', hexc('#f3efe7'), 0.3, 0.2),
    ink=mat('ink', hexc('#111111'), 0.6),
    glass=mat('caseglass', hexc('#dfe9ee'), 0.05, 0.0),
    pastry=mat('pastry', hexc('#d08b3e'), 0.6, 0.2),
    pastry2=mat('pastry2', hexc('#7a4a2a'), 0.6, 0.2),
    lamp=mat('pend', (0, 0, 0), 0.4, 0, hexc('#ffd59a'), 14),
    shade=mat('shade', hexc('#2b2b2b'), 0.5, 0.3),
    window=mat('win', (0, 0, 0), 0.5, 0, hexc('#cfe6ff'), 2.2),
    plant=mat('leaf', hexc('#3f7d4a'), 0.6), pot=mat('tpot', hexc('#c0643c'), 0.6),
    mugs=[mat('mug1', hexc('#e07a5f'), 0.35, 0.4), mat('mug2', hexc('#81b29a'), 0.35, 0.4), mat('mug3', hexc('#f2cc8f'), 0.35, 0.4), mat('mug4', hexc('#3d405b'), 0.35, 0.4)],
    screen=mat('pos', (0, 0, 0), 0.3, 0, hexc('#8fd1ff'), 1.4),
    # barista
    bari=mat('bari', hexc('#b28ce6'), 0.38, 0.6),
    apron=mat('apron', hexc('#2f6b4f'), 0.8, 0.0, sheen=0.3),
    hair=mat('hair', hexc('#3b2230'), 0.7, 0.2, sheen=0.4),
    iris_b=mat('iris_b', hexc('#2e6f8f'), 0.3, 0.8),
    blush=mat('blush', hexc('#e48aa8'), 0.6),
    tag=mat('tag', hexc('#f6f2e8'), 0.5),
)
CT = 0.92                                     # counter top height
# floor + walls
box('floor', (12, 12, 0.1), (0, 1, -0.05), C_['floor'])
box('backwall', (12, 0.2, 4.0), (0, 2.75, 2.0), C_['tile'])
box('wainscot', (12, 0.06, 1.0), (0, 2.63, 0.5), C_['wood_dk'], 0.01)
box('rightwall', (0.2, 8, 4.0), (2.55, 0.5, 2.0), C_['green'])
box('leftwall', (0.2, 8, 4.0), (-3.3, 0.5, 2.0), C_['plaster'])
box('window', (0.05, 2.2, 1.6), (-3.18, 0.6, 1.65), C_['window'])
for wy in (-0.5, 0.6, 1.7):
    box('mullion', (0.08, 0.06, 1.7), (-3.15, wy, 1.65), C_['wood_dk'])
box('sill', (0.2, 2.4, 0.06), (-3.12, 0.6, 0.83), C_['wood_dk'])
# main counter (runs toward camera) with wood front and stone top
box('counter', (0.66, 2.9, CT - 0.04), (0, 0.25, (CT - 0.04) / 2), C_['wood'], 0.02)
box('countertop', (0.76, 3.0, 0.05), (0, 0.25, CT - 0.025), C_['top'], 0.01)
for yy in np.linspace(-1.1, 1.6, 10):
    box('slat', (0.68, 0.025, CT - 0.12), (0, yy, (CT - 0.04) / 2), C_['wood_dk'])
# register
box('pos_base', (0.22, 0.26, 0.08), (0.08, 0.95, CT + 0.04), C_['black'], 0.01)
pscr = box('pos_screen', (0.03, 0.26, 0.18), (0.14, 0.95, CT + 0.17), C_['black'], 0.01); pscr.rotation_euler = (0, D(-15), 0)
box('pos_glow', (0.005, 0.22, 0.14), (0.125, 0.95, CT + 0.17), C_['screen']).rotation_euler = (0, D(-15), 0)
# cup stack + spare lids
for i in range(6):
    cyl('stackcup', 0.05, 0.03, (0.18, 0.62, CT + 0.07 + i * 0.028), C_['cupw'])
cyl('stackbase', 0.042, 0.14, (0.18, 0.62, CT + 0.07), C_['cupw'])
# pastry case at the near end
box('case_base', (0.7, 0.5, 0.12), (0, 1.42, CT + 0.06), C_['wood_dk'], 0.01)
gl = box('case_glass', (0.66, 0.46, 0.3), (0, 1.42, CT + 0.27), C_['glass'], 0.01)
gm = gl.data.materials[0]; bs = gm.node_tree.nodes['Principled BSDF']; bs.inputs['Transmission Weight'].default_value = 1.0; bs.inputs['Alpha'].default_value = 0.35
gm.blend_method = 'BLEND' if hasattr(gm, 'blend_method') else None
for i, (px, py) in enumerate([(-0.18, 1.35), (0.0, 1.35), (0.18, 1.35), (-0.1, 1.5), (0.1, 1.5)]):
    o = sphere('pastry', 0.065, C_['pastry'] if i % 2 == 0 else C_['pastry2'], (px, py, CT + 0.17), (1.3, 1, 0.55))
# back counter + espresso machine (behind the barista)
box('backcounter', (0.6, 2.6, CT - 0.04), (1.95, 0.6, (CT - 0.04) / 2), C_['wood_dk'], 0.02)
box('backtop', (0.66, 2.7, 0.05), (1.95, 0.6, CT - 0.025), C_['top'], 0.01)
box('espresso', (0.48, 0.7, 0.42), (2.0, 0.35, CT + 0.21), C_['steel'], 0.03)
box('esp_top', (0.5, 0.72, 0.04), (2.0, 0.35, CT + 0.44), C_['black'], 0.01)
for gy in (0.18, 0.52):
    cyl('group', 0.045, 0.08, (1.74, gy, CT + 0.27), C_['black'])
    cyl('portafilter', 0.012, 0.16, (1.66, gy, CT + 0.22), C_['black'], rot=(0, D(90), 0))
box('esp_badge', (0.01, 0.3, 0.06), (1.755, 0.35, CT + 0.37), C_['chalk_y'])
cyl('grinder', 0.09, 0.32, (2.0, -0.25, CT + 0.16), C_['black'])
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.05, radius2=0.11, depth=0.2, location=(2.0, -0.25, CT + 0.42))
finish(bpy.context.active_object, C_['glass'])
# shelves with mugs on the right wall
for k, sz in enumerate((1.55, 2.0)):
    box('shelf', (0.25, 1.8, 0.04), (2.32, 0.7, sz), C_['wood'], 0.01)
    for j in range(7):
        cyl('mug', 0.05, 0.11, (2.32, 0.05 + j * 0.22, sz + 0.075), C_['mugs'][(j + k) % 4])
# menu boards on the back wall
for bx_, items in ((0.15, [('ESPRESSO', '3'), ('LATTE', '4.5'), ('CAPPUCCINO', '4.5')]), (1.45, [('DRIP COFFEE', '2.5'), ('COLD BREW', '4'), ('MOCHA', '5')])):
    box('menuboard', (1.15, 0.04, 0.78), (bx_, 2.63, 2.45), C_['board'], 0.01)
    box('menuframe', (1.22, 0.03, 0.85), (bx_, 2.645, 2.45), C_['wood_dk'], 0.01)
    for r_, (a_, p_) in enumerate(items):
        text(a_, 0.075, (bx_ - 0.18, 2.6, 2.62 - r_ * 0.17), C_['chalk'])
        text(p_, 0.08, (bx_ + 0.42, 2.6, 2.62 - r_ * 0.17), C_['chalk_y'])
text('TUBE TOWN COFFEE', 0.17, (0.8, 2.6, 3.2), C_['chalk_y'], extrude=0.01)
# pendant lamps over the counter
for py in (-0.3, 0.9):
    bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=0.17, radius2=0.04, depth=0.2, end_fill_type='NOTHING', location=(0.0, py, 2.55))
    s_ = bpy.context.active_object; s_.modifiers.new('sol', 'SOLIDIFY').thickness = 0.01; finish(s_, C_['shade'])
    sphere('bulb', 0.05, C_['lamp'], (0.0, py, 2.46))
    cyl('cord', 0.006, 1.4, (0.0, py, 3.35), C_['black'])
    pl = bpy.data.lights.new('pend', 'POINT'); pl.energy = 35; pl.color = hexc('#ffcf91'); pl.shadow_soft_size = 0.15
    link(bpy.data.objects.new('pend', pl)).location = (0.0, py, 2.4)
# plants
for px, py in ((-2.9, 2.3), (2.25, 2.3)):
    cyl('tpot', 0.18, 0.35, (px, py, 0.175), C_['pot'])
    for i in range(7):
        a_ = i * 2.4
        sphere('leaf', 0.13, C_['plant'], (px + 0.12 * math.cos(a_), py + 0.12 * math.sin(a_), 0.5 + 0.06 * (i % 3)), (1, 0.5, 1.6), rot=(D(20) * math.cos(a_), D(20) * math.sin(a_), a_))
# lighting: warm key, window fill, rim
area('key', (-1.2, -2.6, 2.9), (D(55), 0, D(-25)), 125, hexc('#fff2e2'), (1.6, 1.6))
area('win_fill', (-2.9, 0.4, 1.7), (0, D(-90), 0), 110, hexc('#d5e8ff'), (2.0, 1.4))
area('rim', (1.2, 2.2, 2.6), (D(-50), 0, D(160)), 110, hexc('#ffc890'), (1.2, 1.2))
area('ceiling', (0.3, 0.5, 3.4), (0, 0, 0), 50, hexc('#fff5ea'), (4, 4))
world(hexc('#3a2c22'), 0.22)
box('ceiling_slab', (12, 12, 0.1), (0, 1, 3.65), C_['plaster'])
for bx_ in np.linspace(-3, 2.4, 8): box('beam', (0.14, 8, 0.16), (bx_, 0.5, 3.55), C_['wood_dk'])

# ============================================================ BARISTA (new cast member)
tina['root'].location = (-80, 0, 0)
for o in bpy.data.objects:
    if o.name.startswith(('phone', 'screen')) and o.parent and o.parent.name.startswith('tina'): o.hide_render = True
bari = character('bari', C_['bari'], 0.27, 0.55, C_['iris_b'], 0.098, 0.112, lids=True)
br_ = bari['root']
bari['mouth'] = sphere('bari_mouth', 0.03, M['mouth'], (0, -0.278, bari['ez'] - 0.19), (1.3, 0.5, 0.5), parent=br_)
bse = empty('bsmile_e', (0, -0.268, bari['ez'] - 0.19), br_)
bari_smile = noodle('bari_smile', [(-0.065, 0, 0.022), (0.0, -0.004, -0.012), (0.065, 0, 0.022)], 0.011, M['mouth'], bse)
for sx in (-1, 1):
    sphere('blush', 0.035, C_['blush'], (sx * 0.17, -0.205, bari['ez'] - 0.14), (1.2, 0.35, 0.7), parent=br_).rotation_euler = (0, 0, D(sx * 38))
# hair: bun + side tufts
btop = bari['top']
sphere('hair_cap', 0.282, C_['hair'], (0, 0.015, btop - 0.075), (1, 1, 0.62), parent=br_, half=True)
sphere('hair_bun', 0.11, C_['hair'], (0, 0.06, btop + 0.04), parent=br_)
# apron: front bib (half capsule cut flat below the mouth) + neck straps + name tag
def half_capsule(name, r, h, m, loc, ztop, parent):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=25, radius=r)
    for v in bm.verts: v.co.z += h / 2 if v.co.z > 0 else -h / 2
    g = lambda: bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=g(), plane_co=(0, 0.02, 0), plane_no=(0, 1, 0), clear_outer=True)
    bmesh.ops.bisect_plane(bm, geom=g(), plane_co=(0, 0, ztop - loc[2]), plane_no=(0, 0, 1), clear_outer=True)
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me)); o.location = loc
    s = o.modifiers.new('sol', 'SOLIDIFY'); s.thickness = 0.008
    return finish(o, m, parent)
zc_b = bari['zc']
half_capsule('apron', 0.286, 0.34, C_['apron'], (0, 0, zc_b - 0.24), zc_b + 0.02, br_)
for sx in (-1, 1):
    noodle('apron_strap', [(sx * 0.13, -0.258, zc_b + 0.012), (sx * 0.24, -0.15, zc_b + 0.04), (sx * 0.28, 0.02, zc_b + 0.05)], 0.008, C_['apron'], br_)
box('nametag', (0.08, 0.008, 0.04), (0.1, -0.29, zc_b - 0.07), C_['tag'], 0.004, br_)

# ============================================================ PROPS: cup (with the infamous name) + marker
cup = empty('cup')
bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.04, radius2=0.05, depth=0.14, location=(0, 0, 0))
finish(bpy.context.active_object, C_['cupw'], cup)
bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.0455, radius2=0.0495, depth=0.05, location=(0, 0, -0.01), end_fill_type='NOTHING')
_sl = bpy.context.active_object; _sl.scale = (1.035, 1.035, 1); finish(_sl, C_['sleeve'], cup)
cyl('cup_lid', 0.053, 0.016, (0, 0, 0.076), C_['lid'], parent=cup)
cyl('cup_lid2', 0.044, 0.012, (0, 0, 0.088), C_['lid'], parent=cup)
FONT = bpy.data.fonts.load(os.path.join(HERE, 'marker.ttf'))
tcu = bpy.data.curves.new('dogtxt', 'FONT'); tcu.body = 'DOG'; tcu.font = FONT; tcu.size = 0.036
tcu.align_x = 'CENTER'; tcu.align_y = 'CENTER'; tcu.extrude = 0.0
dog_txt = link(bpy.data.objects.new('dogtxt', tcu))
bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = dog_txt; dog_txt.select_set(True)
bpy.ops.object.convert(target='MESH'); dog_txt = bpy.context.active_object
# wrap the flat lettering onto the (slightly conical) cup wall: x -> angle around the cup, y -> height
_bm = bmesh.new(); _bm.from_mesh(dog_txt.data)
bmesh.ops.triangulate(_bm, faces=_bm.faces[:])
for _ in range(2): bmesh.ops.subdivide_edges(_bm, edges=[e for e in _bm.edges if e.calc_length() > 0.004], cuts=1, use_grid_fill=False)
bmesh.ops.triangulate(_bm, faces=_bm.faces[:])
for v in _bm.verts:
    x, y = v.co.x, v.co.y; z = 0.042 + y
    r = 0.04 + (z + 0.07) / 0.14 * 0.01 + 0.0009
    a = x / r
    v.co = Vector((r * math.sin(a), -r * math.cos(a), z))
_bm.to_mesh(dog_txt.data); _bm.free()
s_ = dog_txt.modifiers.new('sol', 'SOLIDIFY'); s_.thickness = 0.0006
dog_txt.data.materials.clear(); dog_txt.data.materials.append(C_['ink']); dog_txt.parent = cup
marker = empty('marker')
cyl('marker_body', 0.011, 0.12, (0, 0, 0), C_['black'], parent=marker)
cyl('marker_cap', 0.012, 0.035, (0, 0, 0.07), C_['black'], parent=marker)
cyl('marker_band', 0.0115, 0.012, (0, 0, -0.03), C_['chalk'], parent=marker)

scene.view_settings.exposure = -0.45
