"""Tube Town - "Forgot my phone in the bathroom".  usage: python3 build9.py SHOT OUTDIR [--still F] [--samples N] [--pct P] [--step S]"""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
TEX = os.path.join(HERE, 'tex')
X0 = 30.0
GOLD = mat('gold2', hexc('#d8b25a'), 0.3)

# ============================================================ BATHROOM (same set as Ep6, no bubble bath)
B = dict(
    floor=brick_mat('bfloor', hexc('#e9e6e1'), hexc('#d9d5cf'), hexc('#b9b4ad'), 2.5, 0.5, 0.5, 0.0, 0.4),
    wall=brick_mat('bwall', hexc('#f2b8c6'), hexc('#efb0bf'), hexc('#fbe9ee'), 3.0, 0.5, 0.5, 0.0, 0.35, vertical=True),
    wall2=brick_mat('bwall2', hexc('#a9dcc9'), hexc('#a2d6c2'), hexc('#e8f6f0'), 3.0, 0.5, 0.5, 0.0, 0.35, vertical=True),
    tub=mat('tub', hexc('#fbfbf8'), 0.12, 0.8),
    porcelain=mat('porcelain', hexc('#fdfdfb'), 0.1, 0.9),
    chrome=mat('chrome', hexc('#d9dde2'), 0.12),
    tp=mat('tp', hexc('#fbfaf6'), 0.9),
    wax=mat('wax', hexc('#fff4e2'), 0.5),
    duck=mat('duck', hexc('#ffd23a'), 0.3, 0.6),
    beak=mat('beak', hexc('#ff8a2a'), 0.4),
    shelf=mat('shelf', hexc('#c99567'), 0.6),
    bottle=mat('sudz', hexc('#4fc3e0'), 0.18, 0.9),
    cap=mat('sudzcap', hexc('#ffffff'), 0.3, 0.5),
    water=mat('water', hexc('#cfe8f5'), 0.05, 1.0),
)
box('bfloor', (6, 6, 0.1), (X0, -1.0, -0.05), B['floor'])
box('bwall', (6, 0.1, 4), (X0, 1.1, 2), B['wall'])
box('bwall2', (0.1, 6, 4), (X0 - 1.6, -1.0, 2), B['wall2'])
box('bwall3', (0.1, 6, 4), (X0 + 2.35, -1.0, 2), B['wall2'])
box('tub', (1.75, 0.82, 0.62), (X0, 0.35, 0.31), B['tub'], 0.2)
box('tub_inner', (1.45, 0.55, 0.02), (X0, 0.35, 0.615), B['water'])
for fx in (-0.7, 0.7):
    for fy in (0.05, 0.65):
        sphere('foot', 0.07, GOLD, (X0 + fx, fy, 0.03))
sphere('duck_body', 0.07, B['duck'], (X0 - 0.45, 0.12, 0.69), (1.2, 1, 0.8))
sphere('duck_head', 0.045, B['duck'], (X0 - 0.4, 0.1, 0.77))
sphere('duck_beak', 0.022, B['beak'], (X0 - 0.35, 0.07, 0.765), (1.4, 0.8, 0.5))
box('shelf', (0.7, 0.18, 0.04), (X0 + 0.55, 1.0, 1.55), B['shelf'], 0.01)
capsule('bpot', 0.07, 0.05, M['pot'], (X0 + 0.4, 1.0, 1.66))
sphere('bplant', 0.1, M['plant'], (X0 + 0.4, 1.0, 1.8), (1, 1, 1.2))
for k, c in enumerate(('#7fc8f8', '#ffd6a5')):
    capsule('bottle', 0.035, 0.08, mat('bottle%d' % k, hexc(c), 0.2, 0.7), (X0 + 0.65 + k * 0.12, 1.0, 1.65))
# toilet
TX, TY = X0 + 1.5, 0.6
bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.15, radius2=0.2, depth=0.38, location=(TX, TY, 0.19))
bowl = bpy.context.active_object; bowl.scale = (1, 1.25, 1)
bowl.modifiers.new('b', 'BEVEL').width = 0.02; finish(bowl, B['porcelain'])
bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.035, location=(TX, TY, 0.405))
seat = bpy.context.active_object; seat.scale = (1, 1.25, 0.8); finish(seat, B['porcelain'])
lid = box('lid', (0.38, 0.03, 0.46), (TX, TY + 0.27, 0.64), B['porcelain'], 0.012); lid.rotation_euler = (D(-8), 0, 0)
box('tank', (0.48, 0.2, 0.42), (TX, TY + 0.4, 0.83), B['porcelain'], 0.04)
box('tank_lid', (0.52, 0.23, 0.04), (TX, TY + 0.4, 1.06), B['porcelain'], 0.015)
box('flush', (0.07, 0.02, 0.025), (TX - 0.16, TY + 0.285, 0.98), B['chrome'], 0.006)
# toilet paper on the back wall
box('tp_bar', (0.2, 0.05, 0.02), (TX + 0.48, 1.03, 0.78), B['chrome'], 0.006)
cyl('tp_roll', 0.065, 0.12, (TX + 0.48, 0.98, 0.72), B['tp'], rot=(0, D(90), 0))
for i, (cx, cy, h) in enumerate(((X0 - 0.95, 0.75, 0.22), (X0 - 1.12, 0.6, 0.15))):
    cyl('candle', 0.05, h, (cx, cy, h / 2), B['wax'])
area('bath_key', (X0 + 1.0, -0.6, 2.6), (D(25), D(15), 0), 60, hexc('#ffe7cf'), (1.6, 1.6))
area('bath_fill', (X0 + 0.3, -2.0, 1.6), (D(80), 0, 0), 20, hexc('#ffd1e0'), (2, 1.2))
area('bath_rim', (X0 + 2.0, 0.9, 1.7), (D(-60), D(40), 0), 14, hexc('#bfe8ff'), (0.8, 0.8))
world(hexc('#2a1f24'), 0.4)

# ---------------------------------------------------------------- SUDZ bottle
def make_bottle(name, loc, track_target=None):
    be = empty(name, loc)
    box(name + '_body', (0.1, 0.056, 0.24), (0, 0, 0.12), B['bottle'], 0.026, be)
    cyl(name + '_cap', 0.032, 0.04, (0, 0, 0.26), B['cap'], parent=be)
    for side, img, w_, h_ in ((-1, 'label_front', 0.088, 0.152), (1, 'label_back', 0.088, 0.166)):
        lm, _, _ = img_node_mat(name + img, [os.path.join(TEX, img + '.png')], 1.0)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, side * 0.0295, 0.12),
                                         rotation=(D(90), 0, 0 if side < 0 else D(180)))
        p = bpy.context.active_object; p.scale = (w_, h_, 1); p.parent = be; p.data.materials.append(lm)
    if track_target:
        c = be.constraints.new('TRACK_TO'); c.target = track_target; c.track_axis = 'TRACK_Y'; c.up_axis = 'UP_Z'
    return be

# ---------------------------------------------------------------- Doug on the toilet
dr = doug['root']; tina['root'].location = (-50, 0, 0)
DX, DY, DZ = TX, TY - 0.05, 0.205
dr.location = (DX, DY, DZ); rot_doug(dr, 0)
for hip in doug['legs']:
    hip.rotation_euler = (D(-78), 0, 0)
eye_t = make_eye_target(doug, 'doug_eye_t')
HOLD = SHOT in ('T4', 'T5', 'T6')
if HOLD:
    armL = doug['arms']['L']; armL.rotation_euler = (D(-80), 0, D(36))
    bpy.context.view_layer.update()
    hw = bpy.data.objects['doug_handL'].matrix_world.translation.copy()
    ew = eye_t.matrix_world.translation.copy()
    bottle = make_bottle('sudz', hw + Vector((0.02, -0.03, -0.02)))
    bottle.rotation_euler = (D(28), 0, D(8))
else:
    bottle = make_bottle('sudz', (X0 + 0.74, 0.28, 0.6))
    bottle.rotation_euler = (0, 0, D(-12))

def eyes(f, x, z, interp=None):
    for e in doug['eyes']:
        key(e, 'rotation_euler', f, Euler((D(x), 0, D(z))))

def brows(f, dz, tilt):
    for i, bp in enumerate(doug['brows']):
        sx = -1 if i == 0 else 1
        if not hasattr(bp, '_z0'):
            pass
        z0 = BROW_Z0[i]
        key(bp, 'location', f, Vector((bp.location.x, bp.location.y, z0 + dz)))
        key(bp, 'rotation_euler', f, Euler((0, sx * D(tilt), 0)))
BROW_Z0 = [bp.location.z for bp in doug['brows']]

N = 60
if SHOT == 'T1':        # wide: pats pockets, no phone
    N = 72
    key(cam, 'location', 1, Vector((X0 - 0.25, -1.95, 1.35))); key(cam, 'location', N, Vector((X0 - 0.1, -1.8, 1.33)))
    target.location = (X0 + 1.05, 0.45, 0.88); focus.location = (DX, DY - 0.3, 1.2)
    cam_data.lens = 22; cam_data.dof.aperture_fstop = 4.0
    for side, sgn in (('L', -1), ('R', 1)):
        a = doug['arms'][side]
        for k, f in enumerate((4, 10, 16, 22, 28, 34)):
            v = (k % 2 == 1)
            key(a, 'rotation_euler', f, Euler((D(-28) if v else D(-12), D(-sgn * 14) if v else 0, 0)))
        key(a, 'rotation_euler', 40, Euler((0, 0, 0)))
    eyes(1, 4, 0); eyes(5, 28, 0); eyes(34, 28, 0); eyes(39, 0, 0)
    brows(1, 0, -6); brows(36, 0, -6); brows(40, 0.035, -14); brows(60, 0.0, -2)
elif SHOT == 'T2':      # bored: looks around
    N = 72
    key(cam, 'location', 1, Vector((DX + 0.06, DY - 1.35, 1.42))); key(cam, 'location', N, Vector((DX + 0.05, DY - 1.25, 1.42)))
    target.location = (DX, DY, 1.46); focus.location = (DX, DY - 0.33, 1.5)
    cam_data.lens = 32; cam_data.dof.aperture_fstop = 2.4
    eyes(1, 2, 0); eyes(9, 2, 0); eyes(13, 0, 32); eyes(26, 0, 32); eyes(30, 0, -32); eyes(44, 0, -32)
    eyes(48, -24, 0); eyes(62, -24, 0); eyes(66, 4, 0)
    brows(1, -0.01, 4)
    for f in range(1, N + 1, 6):
        dr.rotation_euler = (0, D(1.5) * math.sin(f / 9), 0); dr.keyframe_insert('rotation_euler', frame=f)
elif SHOT == 'T3':      # reaches for the shampoo
    N = 60
    key(cam, 'location', 1, Vector((X0 + 0.85, -1.3, 1.08))); key(cam, 'location', N, Vector((X0 + 0.9, -1.15, 1.06)))
    target.location = (X0 + 1.1, 0.4, 0.88); focus.location = (X0 + 1.0, 0.35, 0.9)
    cam_data.lens = 26; cam_data.dof.aperture_fstop = 3.2
    eyes(1, 4, 0); eyes(8, 4, 0); eyes(13, 26, -38)
    a = doug['arms']['L']
    key(a, 'rotation_euler', 14, Euler((0, 0, 0))); key(a, 'rotation_euler', 44, Euler((D(-25), D(47), 0)))
elif SHOT == 'T4':      # the back label, slow pan down
    N = 72
    tc.mute = True
    l1, rot1, up = cam_align(bottle, (0, 1, 0), (0, 0, 1), 0.24, 0.0)
    bc = bottle.matrix_world.translation.copy()
    centre = bc + up * 0.12
    cam.rotation_euler = rot1
    nrm = (l1 - bc)
    key(cam, 'location', 1, centre + nrm + up * 0.045); key(cam, 'location', 14, centre + nrm + up * 0.045)
    key(cam, 'location', 58, centre + nrm - up * 0.03); key(cam, 'location', N, centre + nrm - up * 0.032)
    focus.location = centre
    cam_data.lens = 50; cam_data.dof.aperture_fstop = 9.0
elif SHOT in ('T5', 'T6'):  # reads aloud; then looks at the viewer
    key(cam, 'location', 1, Vector((DX + 0.12, DY - 1.45, 1.25)))
    target.location = (DX - 0.03, DY, 1.3); focus.location = (DX, DY - 0.33, 1.45)
    cam_data.lens = 30; cam_data.dof.aperture_fstop = 2.6
    if SHOT == 'T5':
        N = 96
        key(cam, 'location', N, Vector((DX + 0.11, DY - 1.32, 1.26)))
        # reading saccades: sweep right-to-left along lines
        f = 1
        for line in range(5):
            eyes(f, 38, 14); eyes(f + 12, 38, -14); f += 16
            eyes(f - 1, 38, -14)
        eyes(f, 38, 0)
        brows(1, -0.005, 2); brows(40, 0.015, -8); brows(80, 0.02, -10)
        lipsync(doug['mouth'], os.path.join(HERE, 'vo', 'doug1.wav'), 12, 0, 1.0, 2.2)
    else:
        N = 78
        key(cam, 'location', N, Vector((DX + 0.08, DY - 1.12, 1.32)))
        eyes(1, 38, 0); eyes(8, 38, 0); eyes(14, 2, 0)
        brows(1, 0.02, -10); brows(14, 0.02, -10); brows(22, 0.045, -22)
        lipsync(doug['mouth'], os.path.join(HERE, 'vo', 'doug2.wav'), 18, 0, 1.0, 2.2)

render(N)
