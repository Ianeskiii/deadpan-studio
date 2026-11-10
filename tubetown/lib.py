"""Tube Town shared library: materials, helpers, Doug & Tina rigs, walk/lipsync, render.
usage: python3 build.py SHOT OUTDIR [--still F] [--samples N] [--pct P]
"""
import bpy, bmesh, math, sys, os, json, wave
import numpy as np
from mathutils import Vector, Euler

args = sys.argv[1:]
SHOT = args[0]; OUT = args[1]
def opt(name, default):
    return type(default)(args[args.index(name) + 1]) if name in args else default
STILL = opt('--still', -1)
SAMPLES = opt('--samples', 24)
PCT = opt('--pct', 100)
ENGINE = opt('--engine', 'eevee')
FR = opt('--frames', '')

D = math.radians
scene = bpy.context.scene
# clean
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# ---------------------------------------------------------------- materials
def mat(name, color, rough=0.4, coat=0.0, emit=None, strength=0.0, sheen=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = 0.15
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = strength
    return m

def hexc(h):
    h = h.lstrip('#')
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

M = dict(
    doug=mat('doug', hexc('#e8b52e'), 0.38, 0.6),
    tina=mat('tina', hexc('#2bb5a8'), 0.38, 0.6),
    white=mat('eyewhite', hexc('#f6f3ec'), 0.2, 0.8),
    iris_d=mat('iris_d', hexc('#6b3f1d'), 0.3, 0.8),
    iris_t=mat('iris_t', hexc('#7a3cc8'), 0.3, 0.8),
    pupil=mat('pupil', (0.005, 0.005, 0.005), 0.2, 1.0),
    hi=mat('hi', (1, 1, 1), 0.5, 0, (1, 1, 1), 6),
    brow=mat('brow', hexc('#3a2414'), 0.7),
    mouth=mat('mouth', hexc('#5a1e1e'), 0.5, 0.3),
    hat=mat('hat', hexc('#b9483f'), 0.95, 0, sheen=0.6),
    gold=mat('gold', hexc('#e9c46a'), 0.25),
    phone=mat('phone', hexc('#202024'), 0.3),
    screen=mat('screen', (0, 0, 0), 0.3, 0, hexc('#9fd3ff'), 2.5),
    floor=mat('floor', hexc('#5b3d2b'), 0.55),
    wall=mat('wall', hexc('#4d6470'), 0.85),
    wall2=mat('wall2', hexc('#3f525c'), 0.85),
    cab=mat('cab', hexc('#7fa37a'), 0.5, 0.2),
    top=mat('top', hexc('#e9dfcc'), 0.35),
    micro=mat('micro', hexc('#efe6d6'), 0.3, 0.4),
    panel=mat('panel', hexc('#16181a'), 0.25, 0.5),
    seg=mat('seg', (0, 0, 0), 0.4, 0, hexc('#6dffb0'), 9),
    segoff=mat('segoff', hexc('#0f2018'), 0.4),
    btn=mat('btn', hexc('#9aa0a6'), 0.35),
    frame=mat('frame', hexc('#e8e2d6'), 0.6),
    hall=mat('hall', (0, 0, 0), 0.5, 0, hexc('#ffc98a'), 1.6),
    window=mat('window', (0, 0, 0), 0.5, 0, hexc('#4a6fb5'), 0.7),
    fridge=mat('fridge', hexc('#d9dde0'), 0.3, 0.3),
    plant=mat('plant', hexc('#3f7d4a'), 0.6),
    pot=mat('pot', hexc('#c0643c'), 0.6),
    art=mat('art', hexc('#e07a5f'), 0.6),
)
# microwave interior glow with a mesh grid pattern
def glow_mat():
    m = bpy.data.materials.new('glow'); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes; l = nt.links
    n.remove(n['Principled BSDF'])
    out = n['Material Output']
    em = n.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*hexc('#ff9a3d'), 1)
    tc = n.new('ShaderNodeTexCoord'); ck = n.new('ShaderNodeTexChecker')
    ck.inputs['Scale'].default_value = 150
    ck.inputs['Color1'].default_value = (1, 1, 1, 1); ck.inputs['Color2'].default_value = (0.78, 0.78, 0.78, 1)
    mul = n.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 3.0
    l.new(tc.outputs['UV'], ck.inputs['Vector']); l.new(ck.outputs['Fac'], mul.inputs[0])
    mix = n.new('ShaderNodeMixRGB'); mix.inputs['Fac'].default_value = 1
    l.new(mul.outputs[0], em.inputs['Strength'])
    l.new(em.outputs[0], out.inputs['Surface'])
    return m
M['glow'] = glow_mat()

# ---------------------------------------------------------------- helpers
def link(o):
    bpy.context.collection.objects.link(o)
    return o

def finish(o, m, parent=None, smooth=True):
    if m: o.data.materials.append(m)
    if smooth and o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True
    if parent: o.parent = parent
    return o

def capsule(name, r, h, m, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, seg=48):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2 + 1, radius=r)
    for v in bm.verts:
        v.co.z += h / 2 if v.co.z > 0 else -h / 2
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me))
    o.location = loc; o.rotation_euler = rot; o.scale = scale
    return finish(o, m, parent)

def sphere(name, r, m, loc=(0, 0, 0), scale=(1, 1, 1), parent=None, half=False, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=r)
    if half:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, -0.0001),
                               plane_no=(0, 0, -1), clear_outer=True)
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me))
    o.location = loc; o.scale = scale; o.rotation_euler = rot
    if half:
        s = o.modifiers.new('s', 'SOLIDIFY'); s.thickness = 0.008
    return finish(o, m, parent)

def box(name, dims, loc, m, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = dims
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new('b', 'BEVEL'); b.width = bevel; b.segments = 4
        o.data.polygons.foreach_set('use_smooth', [False] * len(o.data.polygons))
    o.data.materials.append(m)
    if parent: o.parent = parent
    return o

def empty(name, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    e = link(bpy.data.objects.new(name, None)); e.location = loc; e.rotation_euler = rot
    if parent: e.parent = parent
    return e

def noodle(name, pts, r, m, parent):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = r; cu.bevel_resolution = 6; cu.use_fill_caps = True; cu.resolution_u = 16
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = link(bpy.data.objects.new(name, cu)); o.data.materials.append(m); o.parent = parent
    return o

# ---------------------------------------------------------------- characters
def character(name, body_m, r, h, iris_m, eye_r, eye_dx, lids=False):
    root = empty(name)
    zc = 0.25 + r + h / 2
    top = zc + h / 2 + r
    capsule(name + '_body', r, h, body_m, (0, 0, zc), parent=root)
    legs = []
    for sx in (-1, 1):
        hip = empty(name + '_hip', (sx * r * 0.42, 0, 0.28), root)
        capsule(name + '_leg', 0.055, 0.16, body_m, (0, 0, -0.11), parent=hip)
        sphere(name + '_foot', 0.075, body_m, (0, -0.04, -0.24), (0.9, 1.4, 0.55), parent=hip)
        legs.append(hip)
    ez = zc + h / 2 + r * 0.05
    C = dict(root=root, eyes=[], brows=[], arms={}, zc=zc, top=top, ez=ez, r=r, legs=legs)
    for sx in (-1, 1):
        ex = sx * eye_dx
        ey = -math.sqrt(max(r * r - ex * ex, 0)) + eye_r * 0.55
        sphere(name + '_eye', eye_r, M['white'], (ex, ey, ez), parent=root)
        pivot = empty(name + '_look', (ex, ey, ez), root)
        sphere(name + '_iris', eye_r * 0.55, iris_m, (0, -eye_r * 0.88, 0), (1, 0.45, 1), parent=pivot)
        sphere(name + '_pupil', eye_r * 0.3, M['pupil'], (0, -eye_r * 1.0, 0), (1, 0.4, 1), parent=pivot)
        sphere(name + '_hi', eye_r * 0.1, M['hi'], (eye_r * 0.2, -eye_r * 1.02, -eye_r * 0.12 if lids else eye_r * 0.22), parent=pivot)
        C['eyes'].append(pivot)
        if lids:
            sphere(name + '_lid', eye_r * 1.2, body_m, (ex, ey, ez), half=True, rot=(D(10), 0, 0), parent=root)
        bp = empty(name + '_browp', (ex, ey - eye_r * 0.4, ez + eye_r * 1.35), root)
        capsule(name + '_brow', 0.026 if lids else 0.016, eye_r * 1.2, M['brow'], (0, 0, 0),
                rot=(0, D(90), 0), parent=bp)
        bp.rotation_euler = (0, sx * D(-6), 0)
        C['brows'].append(bp)
    for sx, side in ((-1, 'L'), (1, 'R')):
        sh = empty(name + '_sh' + side, (sx * (r - 0.02), 0, zc - h * 0.05), root)
        noodle(name + '_arm' + side, [(0, 0, 0), (sx * 0.08, -0.02, -0.27), (sx * 0.06, 0, -0.56)], 0.04, body_m, sh)
        sphere(name + '_hand' + side, 0.065, body_m, (sx * 0.06, 0, -0.59), (1, 0.8, 1.1), parent=sh)
        C['arms'][side] = sh
    return C

doug = character('doug', M['doug'], 0.32, 0.7, M['iris_d'], 0.105, 0.125, lids=True)
doug['mouth'] = capsule('doug_mouth', 0.016, 0.06, M['mouth'], (0, -0.313, doug['ez'] - 0.17), rot=(0, D(90), 0), parent=doug['root'])
# bucket hat
hz = doug['top'] - 0.1
bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.345, radius2=0.28, depth=0.26, location=(0, 0, hz + 0.11))
crown = bpy.context.active_object; crown.name = 'hat_crown'
bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.47, radius2=0.335, depth=0.12, end_fill_type='NOTHING',
                                location=(0, 0, hz - 0.03))
brim = bpy.context.active_object; brim.name = 'hat_brim'
for o in (crown, brim):
    s = o.modifiers.new('sol', 'SOLIDIFY'); s.thickness = 0.02
    b = o.modifiers.new('bev', 'BEVEL'); b.width = 0.012; b.segments = 3
    o.modifiers.new('sub', 'SUBSURF').levels = 1
    finish(o, M['hat'], doug['root'])

tina = character('tina', M['tina'], 0.29, 0.6, M['iris_t'], 0.125, 0.13)
tina['mouth'] = sphere('tina_mouth', 0.032, M['mouth'], (0, -0.283, tina['ez'] - 0.17), (1.2, 0.5, 0.8), parent=tina['root'])
for sx in (-1, 1):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.06, minor_radius=0.01, location=(sx * 0.295, -0.02, tina['ez'] - 0.12),
                                     rotation=(0, D(90), 0))
    finish(bpy.context.active_object, M['gold'], tina['root'])
ph = box('phone', (0.075, 0.012, 0.14), (0.06, -0.03, -0.6), M['phone'], 0.006, tina['arms']['R'])
box('screen', (0.065, 0.002, 0.125), (0.06, -0.037, -0.6), M['screen'], 0, tina['arms']['R'])


def area(name, loc, rot, power, color, size=(0.5, 0.5)):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = power; l.color = color
    l.shape = 'RECTANGLE'; l.size, l.size_y = size
    o = link(bpy.data.objects.new(name, l)); o.location = loc; o.rotation_euler = rot
    o.visible_camera = False; o.visible_glossy = False
    return o

cam_data = bpy.data.cameras.new('cam'); cam = link(bpy.data.objects.new('cam', cam_data)); scene.camera = cam
cam_data.dof.use_dof = True
target = empty('cam_target')
tc = cam.constraints.new('TRACK_TO'); tc.target = target; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
focus = empty('focus'); cam_data.dof.focus_object = focus

def key(o, path, frame, value):
    setattr(o, path, value); o.keyframe_insert(path, frame=frame)

def rot_doug(o, deg):  # yaw only
    o.rotation_euler = (0, 0, D(deg))

# ---------------------------------------------------------------- walk + lipsync
EVENTS = []
def walk(C, f0, f1, p0, p1, heading, step_len=0.26, amp=34, arm_amp=26, hold_arm=None, ease=(6, 8)):
    """Walk root from p0 to p1 (xy) over frames f0..f1 with leg/arm swing, bob, sway, lean."""
    root = C['root']; L = 0.24
    n = f1 - f0
    # eased progress
    def prog(t):
        a, b = ease[0] / n, ease[1] / n
        # trapezoid velocity profile
        v = 1 / (1 - a / 2 - b / 2)
        if t < a: return v * t * t / (2 * a)
        if t > 1 - b: return 1 - v * (1 - t) ** 2 / (2 * b)
        return v * (a / 2 + (t - a))
    total = math.dist(p0, p1)
    prev_ph = 0
    for f in range(f0, f1 + 1):
        t = (f - f0) / n
        d = prog(t) * total
        dn = prog(min(1, t + 1 / n)) * total
        speed = (dn - d) * 30 / max(total / n * 30, 1e-6)          # 0..~1.3
        A = D(amp) * min(1.0, speed)
        ph = math.pi * d / step_len
        if int(ph / math.pi) != int(prev_ph / math.pi) and f > f0:
            EVENTS.append(f)                                      # foot contact
        prev_ph = ph
        sw = math.sin(ph)
        x = p0[0] + (p1[0] - p0[0]) * d / max(total, 1e-6)
        y = p0[1] + (p1[1] - p0[1]) * d / max(total, 1e-6)
        z = -L * (1 - math.cos(A * sw)) + 0.018 * min(1, speed) * math.cos(ph) ** 2
        root.location = (x, y, z); root.keyframe_insert('location', frame=f)
        root.rotation_euler = (D(5) * min(1, speed), D(5) * sw * min(1, speed), D(heading))
        root.keyframe_insert('rotation_euler', frame=f)
        C['legs'][0].rotation_euler = (A * sw, 0, 0); C['legs'][0].keyframe_insert('rotation_euler', frame=f)
        C['legs'][1].rotation_euler = (-A * sw, 0, 0); C['legs'][1].keyframe_insert('rotation_euler', frame=f)
        for side, sgn in (('L', -1), ('R', 1)):
            if hold_arm and side in hold_arm: continue
            a = C['arms'][side]
            a.rotation_euler = (sgn * D(arm_amp) * sw * min(1, speed), 0, 0)
            a.keyframe_insert('rotation_euler', frame=f)

def lipsync(mouth, wav, f_start, axis, base, open_amt, step=1):
    with wave.open(wav) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float)
        if w.getnchannels() == 2: a = a[::2]
    hop = sr // 30
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)])
    rms = rms / (rms.max() + 1e-9)
    nf = len(rms)
    for i in range(-1, nf + 2):
        v = rms[i] if 0 <= i < nf else 0
        v = min(1, max(0, (v - 0.08) / 0.6))
        sc = list(mouth.scale); sc[axis] = base * (1 + open_amt * v)
        mouth.scale = sc; mouth.keyframe_insert('scale', frame=f_start + i)

# ---------------------------------------------------------------- render
def render(N):
    r = scene.render
    if ENGINE == 'eevee':
        r.engine = 'BLENDER_EEVEE'
        ee = scene.eevee
        ee.taa_render_samples = SAMPLES
        for k, v in (('use_raytracing', True), ('use_shadows', True), ('shadow_ray_count', 2), ('shadow_step_count', 8),
                     ('use_fast_gi', True)):
            try: setattr(ee, k, v)
            except Exception as ex: print('eevee opt', k, ex)
    else:
        r.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = SAMPLES
    scene.cycles.use_adaptive_sampling = True; scene.cycles.adaptive_threshold = 0.04
    scene.cycles.use_denoising = True
    try: scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    scene.cycles.max_bounces = 4; scene.cycles.diffuse_bounces = 2; scene.cycles.glossy_bounces = 2
    scene.cycles.transmission_bounces = 2; scene.cycles.caustics_reflective = False; scene.cycles.caustics_refractive = False
    r.resolution_x, r.resolution_y, r.resolution_percentage = 720, 1280, PCT
    r.fps = 30
    r.use_persistent_data = True
    scene.cycles.use_light_tree = False
    try: scene.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        try: scene.view_settings.look = 'Medium High Contrast'
        except Exception: pass
    r.image_settings.file_format = 'PNG'
    scene.frame_start, scene.frame_end = 1, N
    os.makedirs(OUT, exist_ok=True)
    if STILL > 0:
        scene.frame_set(STILL)
        r.filepath = os.path.join(OUT, f'{SHOT}_still_{STILL:03d}.png')
        bpy.ops.render.render(write_still=True)
    else:
        r.filepath = os.path.join(OUT, f'{SHOT}_')
        if FR:
            a, b = FR.split('-'); scene.frame_start, scene.frame_end = int(a), int(b)
        scene.frame_step = opt('--step', 1)
        bpy.ops.render.render(animation=True)
    json.dump(EVENTS, open(os.path.join(OUT, 'steps.json'), 'w'))
    print('DONE', SHOT, N)
