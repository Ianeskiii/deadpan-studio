"""Tube Town - "When you wake up 1 minute before your alarm".  usage: python3 build10.py SHOT OUTDIR [--still F] ..."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())

# ============================================================ BEDROOM
R_ = dict(
    floor=brick_mat('planks', hexc('#8a5a3c'), hexc('#7c5034'), hexc('#4f3322'), 1.2, 0.9, 0.12, 0.5, 0.55),
    wall=mat('bwall', hexc('#55658a'), 0.85),
    wood=mat('bedwood', hexc('#a8714a'), 0.45, 0.2),
    sheet=mat('sheet', hexc('#f2f1ee'), 0.8),
    pillow=mat('pillow', hexc('#fbfbfb'), 0.85, 0, sheen=0.5),
    blinds=mat('blinds', hexc('#e9e4da'), 0.6),
    dawn=mat('dawn', (0, 0, 0), 0.5, 0, hexc('#9fc0ff'), 0.9),
    clock=mat('clockbody', hexc('#1b1b1f'), 0.25, 0.6),
    seg=mat('redseg', (0, 0, 0), 0.4, 0, hexc('#ff3b2f'), 10),
    segoff=mat('redsegoff', hexc('#0c0303'), 0.95),
    frame=mat('frame', hexc('#e8e2d6'), 0.6),
    art=mat('art2', hexc('#f2a65a'), 0.7),
    lampshade=mat('shade', hexc('#f3e3c3'), 0.8),
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
box('sidewall2', (0.1, 8, 4), (2.4, 1.0, 2), R_['wall'])
# bed
box('bedframe', (1.36, 2.2, 0.3), (0, 1.05, 0.2), R_['wood'], 0.03)
box('mattress', (1.24, 2.05, 0.22), (0, 1.05, 0.44), R_['sheet'], 0.06)
box('headboard', (1.4, 0.08, 1.05), (0, 2.18, 0.6), R_['wood'], 0.03)
sphere('pillow', 1.0, R_['pillow'], (0, 1.78, 0.64), (0.48, 0.26, 0.1))
# blanket draped over Doug (procedural grid)
me = bpy.data.meshes.new('blanket'); bm = bmesh.new()
nx, ny = 40, 30; x0, x1, y0, y1 = -0.68, 0.68, -0.02, 1.40
verts = []
for j in range(ny + 1):
    row = []
    for i in range(nx + 1):
        x = x0 + (x1 - x0) * i / nx; y = y0 + (y1 - y0) * j / ny
        bump = 0.66 * math.sqrt(max(0.0, 1 - (x / 0.52) ** 2))
        taper = min(1.0, 0.55 + 0.45 * (y / 0.6)) if y < 0.6 else 1.0
        z = 0.58 + bump * taper
        if abs(x) > 0.6: z = 0.58 - (abs(x) - 0.6) * 2.2
        z += 0.012 * math.sin(x * 23) * math.sin(y * 17)
        row.append(bm.verts.new((x, y, z)))
    verts.append(row)
for j in range(ny):
    for i in range(nx):
        bm.faces.new((verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]))
bm.to_mesh(me); bm.free()
blanket = link(bpy.data.objects.new('blanket', me))
s_ = blanket.modifiers.new('sol', 'SOLIDIFY'); s_.thickness = 0.04
blanket.modifiers.new('sub', 'SUBSURF').levels = 1
finish(blanket, QUILT)
# nightstand + clock
NX, NY = 0.98, 1.72
box('nightstand', (0.5, 0.42, 0.56), (NX, NY, 0.28), R_['wood'], 0.02)
box('drawer_line', (0.44, 0.005, 0.01), (NX, NY - 0.212, 0.36), R_['clock'])
CX, CY, CZ = NX - 0.06, NY - 0.06, 0.56
clock = empty('clock', (CX, CY, CZ))
box('clock_body', (0.27, 0.11, 0.13), (0, 0, 0.065), R_['clock'], 0.02, clock)
box('clock_face', (0.235, 0.004, 0.09), (0, -0.056, 0.07), mat('cface', hexc('#0b0606'), 0.2, 0.8), 0, clock)
SEG = {'a': (0, 1), 'b': (1, .5), 'c': (1, -.5), 'd': (0, -1), 'e': (-1, -.5), 'f': (-1, .5), 'g': (0, 0)}
DIG = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc',
       '8': 'abcdefg', '9': 'abcdfg'}
dw, dh, th = 0.016, 0.026, 0.0065
DISP = []
for x0_ in (-0.068, -0.002, 0.052):
    segs = {}
    for sname, (sx, sz) in SEG.items():
        horiz = sname in 'adg'
        dims = (dw * 2 - th, 0.003, th) if horiz else (th, 0.003, dh - th)
        loc = (x0_ + sx * dw, -0.0595, 0.078 + sz * dh)
        box('segoff', dims, (loc[0], -0.0585, loc[2]), R_['segoff'], 0, clock)
        segs[sname] = box('seg', dims, loc, R_['seg'], 0, clock)
    DISP.append(segs)
COLON = [box('colon', (th, 0.003, th), (-0.035, -0.0595, z), R_['seg'], 0, clock) for z in (0.066, 0.09)]
alarm_txt = text('ALARM 7:00', 0.011, (0, -0.06, 0.035), R_['seg'], parent=clock)
def show_time(t, frame=None, blank=False):
    digits = t.replace(':', '')
    for segs, ch in zip(DISP, digits):
        for sname, o in segs.items():
            o.hide_render = blank or (sname not in DIG[ch])
            if frame is not None: o.keyframe_insert('hide_render', frame=frame)
    for o in COLON:
        o.hide_render = blank
        if frame is not None: o.keyframe_insert('hide_render', frame=frame)
clock_glow = bpy.data.lights.new('clock_glow', 'POINT'); clock_glow.energy = 1.5; clock_glow.color = hexc('#ff3b2f'); clock_glow.shadow_soft_size = 0.05
cg = link(bpy.data.objects.new('clock_glow', clock_glow)); cg.location = (CX - 0.05, CY - 0.4, CZ + 0.25)
# lamp (off), wall art
cyl('lamp_base', 0.05, 0.22, (NX + 0.14, NY + 0.08, 0.67), R_['clock'])
bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=0.12, radius2=0.07, depth=0.14, location=(NX + 0.14, NY + 0.08, 0.84), end_fill_type='NOTHING')
finish(bpy.context.active_object, R_['lampshade']).modifiers.new('s', 'SOLIDIFY').thickness = 0.005
box('artframe', (0.62, 0.04, 0.46), (1.3, 2.19, 1.75), R_['frame'], 0.01)
box('art', (0.54, 0.02, 0.38), (1.3, 2.17, 1.75), R_['art'])
# window with blinds behind/above the bed, dawn light through the slats
WX = -0.95
box('win_frame', (0.95, 0.06, 1.05), (WX, 2.2, 1.75), R_['frame'], 0.01)
box('win_glow', (0.85, 0.02, 0.95), (WX, 2.24, 1.75), R_['dawn'])
for k in range(14):
    b_ = box('slat', (0.86, 0.012, 0.052), (WX, 2.15, 1.3 + k * 0.066), R_['blinds'], 0.002); b_.rotation_euler = (D(12), 0, 0)
dawn_l = area('dawn_l', (WX, 2.6, 1.8), (D(-62), 0, D(8)), 140, hexc('#a9c4ff'), (0.9, 0.9))
area('fill_l', (0.8, -1.2, 2.6), (D(50), 0, D(20)), 45, hexc('#8fa6d9'), (2, 2))
area('face_l', (0.3, 1.2, 2.5), (D(-15), D(10), 0), 40, hexc('#dfe6ff'), (1.2, 1.2))
area('rim_l', (-1.6, 0.6, 2.2), (D(30), D(-50), 0), 10, hexc('#b8c8ff'), (1, 1))
world(hexc('#1c2438'), 0.8)

# ---------------------------------------------------------------- Doug in bed (on his back, face up)
dr = doug['root']; tina['root'].location = (-50, 0, 0)
dr.location = (0, 0.35, 0.87); dr.rotation_euler = (D(-90), 0, 0)
LIDS = [o for o in bpy.data.objects if o.name.startswith('doug_lid')]
mpos = doug['mouth'].location.copy()
smile_e = empty('smile_e', mpos, dr)
smile = noodle('smile', [(-0.06, 0, 0.02), (0, -0.004, -0.012), (0.06, 0, 0.02)], 0.013, M['mouth'], smile_e)
smile.hide_render = True
BROW_Z0 = [bp.location.z for bp in doug['brows']]

def lids(f, deg):
    for o in LIDS: key(o, 'rotation_euler', f, Euler((D(deg), 0, 0)))
def eyes(f, x, z):
    for e in doug['eyes']: key(e, 'rotation_euler', f, Euler((D(x), 0, D(z))))
def brows(f, dz, tilt):
    for i, bp in enumerate(doug['brows']):
        sx = -1 if i == 0 else 1
        key(bp, 'location', f, Vector((bp.location.x, bp.location.y, BROW_Z0[i] + dz)))
        key(bp, 'rotation_euler', f, Euler((0, sx * D(tilt), 0)))
def smile_on(f, on):
    smile.hide_render = not on; smile.keyframe_insert('hide_render', frame=f)
    doug['mouth'].hide_render = on; doug['mouth'].keyframe_insert('hide_render', frame=f)
def mouth_scale(f, sx, sz=1.0):
    key(doug['mouth'], 'scale', f, Vector((sx, 1, sz)))
def top_down_cam(height, dy=0.0, tilt=0.0):
    tc.mute = True
    cam.rotation_euler = (D(tilt), 0, 0)
    return Vector((0.0, 1.64 + dy, height))
def ring(f0, f1):   # alarm: digits flash, clock rattles, red light pulses
    for f in range(f0, f1 + 1, 2):
        on = ((f - f0) // 4) % 2 == 0
        show_time('7:00', f, blank=not on)
        clock_glow.energy = 4 if on else 0.6; clock_glow.keyframe_insert('energy', frame=f)
        clock.rotation_euler = (0, D(2.5) * (1 if (f // 2) % 2 else -1), D(3) * (1 if (f // 2) % 2 else -1))
        clock.keyframe_insert('rotation_euler', frame=f)

show_time('6:59'); lids(1, 95); eyes(1, 0, 0)
N = 60
if SHOT == 'A1':        # wide dawn: asleep, eyes open, glance at clock
    N = 72
    key(cam, 'location', 1, Vector((0.62, 0.72, 2.45))); key(cam, 'location', N, Vector((0.58, 0.8, 2.4)))
    target.location = (0.22, 1.64, 0.95); focus.location = (0.05, 1.5, 1.15)
    cam_data.lens = 26; cam_data.dof.aperture_fstop = 4.0
    lids(1, 95); lids(30, 95); lids(36, 55); lids(42, 70); lids(48, 30)
    eyes(1, 0, 0); eyes(48, 0, 0); eyes(54, 0, 38)
    brows(1, -0.01, 4)
elif SHOT in ('A2', 'A4'):   # clock close-up
    N = 48 if SHOT == 'A2' else 36
    cam.location = (CX + 0.03, CY - 0.55, CZ + 0.17)
    target.location = (CX, CY, CZ + 0.07); focus.location = (CX, CY - 0.06, CZ + 0.07)
    cam_data.lens = 45; cam_data.dof.aperture_fstop = 3.2
    if SHOT == 'A2':
        key(cam, 'location', 1, Vector((CX + 0.03, CY - 0.6, CZ + 0.17))); key(cam, 'location', N, Vector((CX + 0.03, CY - 0.53, CZ + 0.16)))
    else:
        show_time('6:59', 1); show_time('7:00', 4); ring(5, N)
        for f in range(5, N + 1, 2):
            cam.location = (CX + 0.03 + 0.004 * ((f // 2) % 2 * 2 - 1), CY - 0.52, CZ + 0.16); cam.keyframe_insert('location', frame=f)
elif SHOT == 'A3':      # content smile, eyes close slowly, snuggles
    N = 72
    key(cam, 'location', 1, top_down_cam(2.2)); key(cam, 'location', N, top_down_cam(2.08))
    focus.location = (0, 1.64, 1.2); cam_data.lens = 30; cam_data.dof.aperture_fstop = 2.8
    lids(1, 30); eyes(1, 0, 30); eyes(6, 0, 0)
    smile_on(1, False); smile_on(10, True)
    brows(1, 0, 0); brows(14, 0.02, -14)
    lids(16, 30); lids(40, 95)
    key(dr, 'rotation_euler', 30, Euler((D(-90), D(0), 0))); key(dr, 'rotation_euler', 44, Euler((D(-90), D(6), 0)))
    key(dr, 'rotation_euler', 58, Euler((D(-90), D(3), 0)))
    key(blanket, 'location', 30, Vector((0, 0, 0))); key(blanket, 'location', 44, Vector((0, 0.04, 0.01)))
elif SHOT == 'A5':      # snaps awake, then flat stare at the viewer while it rings
    N = 90
    p0 = top_down_cam(2.05)
    for f in range(1, N + 1, 2):
        j = 0.006 * ((f // 2) % 2 * 2 - 1) if f < 60 else 0.002 * ((f // 2) % 2 * 2 - 1)
        cam.location = p0 + Vector((j, 0, 0)); cam.keyframe_insert('location', frame=f)
    focus.location = (0, 1.64, 1.2); cam_data.lens = 30; cam_data.dof.aperture_fstop = 2.8
    smile_on(1, True); smile_on(3, False)
    lids(1, 95); lids(3, -28); lids(26, -28); lids(34, 16)
    eyes(1, 0, 0)
    brows(1, 0.02, -14); brows(3, 0.06, -26); brows(26, 0.06, -26); brows(34, -0.03, 12)
    mouth_scale(1, 1.0); mouth_scale(3, 3.2, 1.5); mouth_scale(24, 3.0, 1.5); mouth_scale(32, 1.0)
    ring(1, N)

render(N)
