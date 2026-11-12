"""Tube Town / Deadpan Doug ep19 - Mama mong mahilig maniwala sa fake news.  Doug + Mom (new) on the sofa.
usage: cd ep19 && python3 build.py SHOT OUTDIR [--still F] [--samples N] [--pct P] [--engine cycles] [--step S] [--frames a-b]
  SHOT = A B C O D E F  (film shots, beats.py)  |  QA (print checks)  |  LOOK (library stills: --still, env LOOKCAM=mom|doug|room)
Pipeline: vo19.py -> screen.py -> build.py QA -> render.sh -> overlays.py -> audio.py -> assemble.py
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
sys.path.insert(0, HERE)
import beats as BT
from mathutils import Matrix, Quaternion
def V(*a): return Vector(a)
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
SH = BT.SH; N = BT.N; FILE = BT.FILE
tina['root'].location = (-80, 0, 0)
for o in list(bpy.data.objects):
    if o.name.startswith(('phone', 'screen')) and o.parent and o.parent.name.startswith('tina'): o.hide_render = True
def ease_tab(keys, f):
    """keys [(frame, value or tuple)], smoothstep between keys"""
    if f <= keys[0][0]: return keys[0][1]
    if f >= keys[-1][0]: return keys[-1][1]
    for (fa, va), (fb, vb) in zip(keys, keys[1:]):
        if fa <= f <= fb:
            t = smooth((f - fa) / max(1, fb - fa))
            if isinstance(va, (tuple, list, Vector)): return tuple(a + (b - a) * t for a, b in zip(va, vb))
            return va + (vb - va) * t
def aimed_area(name, loc, tgt, power, color, size):
    q = (V(*tgt) - V(*loc)).to_track_quat('-Z', 'Y')
    return area(name, loc, q.to_euler(), power, color, size)

# ============================================================ FILIPINO LIVING ROOM (warm, daytime; the living-room set re-dressed)
R_ = dict(
    floor=brick_mat('tiles', hexc('#d9c9ae'), hexc('#d1bfa2'), hexc('#a8957a'), 1.6, 0.5, 0.5, 0.0, 0.35),
    wall=mat('ph_wall', hexc('#dcc49b'), 0.9), wall2=mat('ph_wall2', hexc('#c9a97c'), 0.9), trim=mat('ph_trim', hexc('#8a5a3a'), 0.6),
    sofa=mat('sofa', hexc('#7a4a36'), 0.7, 0.0, sheen=0.4), cushion=mat('sofa_cush', hexc('#86533c'), 0.75, 0.0, sheen=0.4),
    pillow=mat('pillow', hexc('#d9a441'), 0.9, sheen=0.6), pillow2=mat('pillow2', hexc('#4f8a7a'), 0.9, sheen=0.6),
    wood=mat('ph_wood', hexc('#6b4429'), 0.45, 0.2), wood_l=mat('ph_wood_l', hexc('#b07a45'), 0.45, 0.3), black=mat('tvblack', hexc('#141416'), 0.3, 0.4),
    tvscr=mat('tvscr', hexc('#1b1e24'), 0.15, 0.6),
    sky=mat('sky', (0, 0, 0), 0.5, 0, hexc('#fff1d6'), 2.2), curtain=mat('curtain', hexc('#c9d9b0'), 0.9, sheen=0.6),
    plant=mat('leaf2', hexc('#3f7d4a'), 0.6), pot=mat('pot2', hexc('#b0603a'), 0.6), frame=mat('pframe', hexc('#5a3a24'), 0.4, 0.3),
    fan=mat('fan', hexc('#e9ecef'), 0.35, 0.3), fanblade=mat('fanblade', hexc('#7fb3d9'), 0.3, 0.2), metal=mat('ph_metal', hexc('#b9bec4'), 0.3, 0.6),
    rug=mat('ph_rug', hexc('#b3563c'), 0.95), white=mat('ph_white', hexc('#f4efe6'), 0.6), red=mat('ph_red', hexc('#c0392b'), 0.6),
)
box('floor', (8, 8, 0.1), (0, 0, -0.05), R_['floor'])
box('rear_wall', (8, 0.2, 3.0), (0, 1.05, 1.5), R_['wall'])
box('front_wall', (8, 0.2, 3.0), (0, -2.4, 1.5), R_['wall'])
box('left_wall', (0.2, 8, 3.0), (-2.15, 0, 1.5), R_['wall2'])
box('right_wall', (0.2, 8, 3.0), (2.15, 0, 1.5), R_['wall2'])
box('ceiling', (8, 8, 0.1), (0, 0, 2.85), R_['wall'])
box('skirting', (4.3, 0.03, 0.1), (0, 0.94, 0.05), R_['trim'])
box('rug', (2.6, 1.7, 0.012), (0, -0.85, 0.006), R_['rug'], 0.004)
# the sofa (wider than ep14's couch: two people)
SEAT = 0.42
SOFA = [box('sofa_base', (2.5, 0.85, SEAT - 0.12), (0, 0.15, (SEAT - 0.12) / 2), R_['sofa'], 0.04)]
for cx in (-0.6, 0.6): SOFA.append(box('seat_cushion', (1.18, 0.8, 0.13), (cx, 0.12, SEAT - 0.065), R_['cushion'], 0.05))
SOFA.append(box('sofa_back', (2.5, 0.24, 0.6), (0, 0.5, SEAT + 0.21), R_['sofa'], 0.08))
for cx in (-1.23, 1.23): SOFA.append(box('arm_rest', (0.26, 0.9, 0.58), (cx, 0.15, 0.37), R_['sofa'], 0.08))
box('pillow_l', (0.38, 0.14, 0.34), (-1.0, 0.32, SEAT + 0.17), R_['pillow'], 0.06).rotation_euler = (D(-14), D(8), D(6))
box('pillow_r', (0.38, 0.14, 0.34), (1.0, 0.32, SEAT + 0.17), R_['pillow2'], 0.06).rotation_euler = (D(-14), D(-8), D(-6))
box('doily', (0.5, 0.26, 0.006), (0, 0.5, SEAT + 0.515), R_['white'], 0.002)          # crocheted runner on the sofa back
# coffee table
TABLE = V(0.0, -0.95, 0.405)
box('coffee_table', (1.0, 0.55, 0.05), (TABLE.x, TABLE.y, 0.38), R_['wood'], 0.01)
for lx in (-0.44, 0.44):
    for ly in (-1.17, -0.73): box('ct_leg', (0.045, 0.045, 0.36), (lx, ly, 0.18), R_['wood'])
cyl('glass', 0.035, 0.11, (0.25, -0.9, 0.46), mat('glass', hexc('#cfe6ee'), 0.05, 0.9))
cyl('bowl', 0.09, 0.05, (-0.2, -1.0, 0.43), R_['white'])
for i in range(4): sphere('pandesal', 0.035, mat('bread', hexc('#c98a4a'), 0.7), (-0.2 + 0.035 * math.cos(i * 1.6), -1.0 + 0.035 * math.sin(i * 1.6), 0.47), (1.2, 1, 0.7))
# rear wall (behind the sofa): giant wooden spoon & fork, family portrait, wall clock
def spoon_fork(x0, z0):
    cyl('spoon_handle', 0.035, 0.75, (x0, 0.93, z0 - 0.05), R_['wood_l'], rot=(0, 0, 0))
    sphere('spoon_bowl', 0.12, R_['wood_l'], (x0, 0.92, z0 + 0.42), (1, 0.35, 1.45))
    x1 = x0 + 0.32
    cyl('fork_handle', 0.035, 0.7, (x1, 0.93, z0 - 0.07), R_['wood_l'])
    box('fork_head', (0.2, 0.06, 0.12), (x1, 0.93, z0 + 0.33), R_['wood_l'], 0.02)
    for tx in (-0.07, 0.0, 0.07): box('fork_tine', (0.04, 0.05, 0.22), (x1 + tx, 0.93, z0 + 0.5), R_['wood_l'], 0.015)
spoon_fork(1.15, 1.55)
box('portrait_frame', (0.62, 0.04, 0.5), (-0.95, 0.93, 1.62), R_['frame'], 0.01)
box('portrait', (0.54, 0.02, 0.42), (-0.95, 0.91, 1.62), mat('portrait_bg', hexc('#a9c7d8'), 0.8))
capsule('pf_doug', 0.07, 0.12, M['doug'], (-0.85, 0.895, 1.56), parent=None)                 # a tiny family photo: Doug + Mom
capsule('pf_mom', 0.065, 0.1, mat('pf_mom', hexc('#ec8f7f'), 0.5), (-1.05, 0.895, 1.55))
cyl('pf_hat', 0.085, 0.04, (-0.85, 0.895, 1.715), M['hat'])
sphere('pf_hair', 0.075, mat('pf_hair', hexc('#2b1e19'), 0.8), (-1.05, 0.9, 1.64), (1, 1, 0.8))
cyl('clock', 0.17, 0.04, (-1.6, 0.93, 1.95), R_['white'], rot=(D(90), 0, 0))
cyl('clock_rim', 0.185, 0.03, (-1.6, 0.945, 1.95), R_['frame'], rot=(D(90), 0, 0))
box('clock_h', (0.012, 0.01, 0.09), (-1.6, 0.9, 1.985), R_['black']); box('clock_m', (0.01, 0.01, 0.13), (-1.56, 0.9, 1.95), R_['black']).rotation_euler = (0, D(-90), 0)
# left wall: window with curtains (daylight), stand fan, plant
box('window', (0.04, 1.0, 1.0), (-2.04, -0.25, 1.55), R_['sky'])
for wy in (-0.25,): box('win_mull', (0.05, 0.04, 1.0), (-2.02, wy, 1.55), R_['white'])
box('win_frame_t', (0.06, 1.08, 0.05), (-2.02, -0.25, 2.07), R_['white']); box('win_frame_b', (0.08, 1.08, 0.05), (-2.0, -0.25, 1.03), R_['white'])
for cy, w in ((-0.86, 0.32), (0.36, 0.32)): box('curtain', (0.06, w, 1.3), (-1.98, cy, 1.45), R_['curtain'], 0.02)
FAN = V(-1.62, 0.55, 0)
cyl('fan_base', 0.17, 0.04, (FAN.x, FAN.y, 0.02), R_['fan'])
cyl('fan_pole', 0.02, 1.05, (FAN.x, FAN.y, 0.55), R_['fan'])
fan_head = empty('fan_head', (FAN.x, FAN.y, 1.12)); fan_head.rotation_euler = (0, 0, D(-35))
sphere('fan_motor', 0.07, R_['fan'], (0, 0.09, 0), (1, 1.3, 1), parent=fan_head)
bpy.ops.mesh.primitive_torus_add(major_radius=0.2, minor_radius=0.008, location=(0, 0, 0), rotation=(D(90), 0, 0))
finish(bpy.context.active_object, R_['metal'], fan_head)
for k in range(8):
    a_ = k * math.pi / 8
    box('fan_wire', (0.4, 0.004, 0.004), (0, -0.01, 0), R_['metal'], 0, fan_head).rotation_euler = (0, a_, 0)
fan_rot = empty('fan_rot', (0, 0.0, 0), fan_head)
for k in range(3):
    b_ = sphere('fan_blade', 0.08, R_['fanblade'], (0.09 * math.cos(k * 2.094), 0, 0.09 * math.sin(k * 2.094)), (1.1, 0.12, 0.7), parent=fan_rot, rot=(0, -k * 2.094, 0))
fan_rot.rotation_euler = (0, 0, 0); fan_rot.keyframe_insert('rotation_euler', frame=1)
fan_rot.rotation_euler = (0, D(-360 * 0.4 * N), 0); fan_rot.keyframe_insert('rotation_euler', frame=N + 1)   # slow turn (blades a blur anyway)
for fc in fan_rot.animation_data.action.fcurves if hasattr(fan_rot.animation_data.action, 'fcurves') else []:
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
cyl('pot', 0.15, 0.3, (-1.75, -0.95, 0.15), R_['pot'])
for i in range(8):
    a_ = i * 2.3; sphere('leaf', 0.12, R_['plant'], (-1.75 + 0.1 * math.cos(a_), -0.95 + 0.1 * math.sin(a_), 0.45 + 0.07 * (i % 3)), (1, 0.5, 1.7), rot=(D(20) * math.cos(a_), D(20) * math.sin(a_), a_))
# right back corner: TV on a wooden cabinet (screen off), turned toward the sofa
tv = empty('tv_set', (1.72, 0.45, 0)); tv.rotation_euler = (0, 0, D(-58))
box('tv_cab', (1.0, 0.42, 0.55), (0, 0, 0.275), R_['wood'], 0.02, tv)
box('tv_cab_door', (0.44, 0.01, 0.38), (-0.24, -0.215, 0.28), R_['wood_l'], 0.01, tv); box('tv_cab_door2', (0.44, 0.01, 0.38), (0.24, -0.215, 0.28), R_['wood_l'], 0.01, tv)
box('tv_body', (0.95, 0.06, 0.56), (0, 0.02, 0.9), R_['black'], 0.01, tv)
box('tv_screen', (0.9, 0.01, 0.51), (0, -0.012, 0.9), R_['tvscr'], 0, tv)
box('tv_foot', (0.3, 0.18, 0.04), (0, 0.02, 0.57), R_['black'], 0, tv)
sphere('figurine', 0.05, R_['white'], (0.4, -0.05, 0.6), (1, 1, 1.6), parent=tv)
# lights: warm ceiling key from the front, window daylight from the left, soft rim from the back
world(hexc('#4a4038'), 0.32)
aimed_area('key', (0.2, -1.5, 2.6), (0, 0.1, 1.1), 165, hexc('#ffe6c8'), (1.6, 1.6))
aimed_area('window_l', (-1.9, -0.25, 1.6), (0, 0.0, 1.1), 75, hexc('#fff6ea'), (1.0, 1.0))
aimed_area('fill_r', (1.6, -1.2, 1.5), (0.2, 0.0, 1.1), 45, hexc('#ffe8cc'), (1.0, 1.0))
aimed_area('rim', (0.0, 0.85, 2.4), (0, 0.0, 1.2), 60, hexc('#ffe2b8'), (1.6, 0.6))
pl = bpy.data.lights.new('room', 'POINT'); pl.energy = 25; pl.color = hexc('#ffd59a'); pl.shadow_soft_size = 0.4
link(bpy.data.objects.new('room', pl)).location = (0, -0.6, 2.6)

# ============================================================ MOM (new): coral tube, curly perm, floral house dress ("duster")
MOM_C = hexc('#ec8f7f')
MM = dict(body=mat('mom', MOM_C, 0.38, 0.6), iris=mat('iris_m', hexc('#3b2414'), 0.3, 0.8),
          hair=mat('mom_hair', hexc('#2b1e19'), 0.75, 0.1, sheen=0.4), clip=mat('clip', hexc('#9b2f4f'), 0.3, 0.5),
          blush=mat('blush', hexc('#e0626a'), 0.6), case=mat('phone_case', hexc('#e86f9c'), 0.4, 0.2), gold=M['gold'])
def floral_mat():
    m = bpy.data.materials.new('duster'); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; l = nt.links
    b = n['Principled BSDF']; b.inputs['Roughness'].default_value = 0.85; b.inputs['Sheen Weight'].default_value = 0.4
    tc = n.new('ShaderNodeTexCoord'); vo = n.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 14
    vo.feature = 'F1'
    l.new(tc.outputs['Object'], vo.inputs['Vector'])
    cr = n.new('ShaderNodeValToRGB'); e = cr.color_ramp; e.interpolation = 'CONSTANT'
    e.elements[0].position = 0.0; e.elements[0].color = (*hexc('#f7f1e8'), 1)          # flower centre
    e.elements[1].position = 0.08; e.elements[1].color = (*hexc('#e05a7a'), 1)          # pink petals
    el = e.elements.new(0.26); el.color = (*hexc('#4f8fc9'), 1)                        # blue ground
    l.new(vo.outputs['Distance'], cr.inputs['Fac']); l.new(cr.outputs['Color'], b.inputs['Base Color'])
    return m
MM['dress'] = floral_mat()
mom = character('mom', MM['body'], 0.30, 0.52, MM['iris'], 0.1, 0.118, lids=True)
mr0 = mom['root']; mtop = mom['top']; mez = mom['ez']; mzc = mom['zc']
HEAD_C = mzc + 0.26                                    # centre of the head hemisphere (standing coords)
# hair: a puffy perm, cap tilted back so the brows and lids stay clear, ringed with curls
hair = sphere('mom_hair', 0.335, MM['hair'], (0, 0.05, HEAD_C), (1, 1, 1.0), parent=mr0, half=True, rot=(D(-42), 0, 0))
import random as _r; _rr = _r.Random(19)
for k in range(26):                                     # curls round the rim (sides + back), none across the face
    th = math.radians(-120 + 240 * k / 25)               # -120..120 deg around the back (0 = straight back)
    x = 0.32 * math.sin(th); y = 0.03 + 0.32 * math.cos(th)
    z = HEAD_C + 0.335 * math.sin(D(42)) * (-math.cos(th)) * 0.9 - 0.02 + _rr.uniform(-0.015, 0.015)
    if y < -0.12 and abs(x) < 0.25: continue
    sphere('curl', 0.07 + _rr.uniform(-0.008, 0.01), MM['hair'], (x, y, z), parent=mr0)
for k in range(22):                                     # perm bumps on top
    th = _rr.uniform(0, 2 * math.pi); ph = _rr.uniform(D(8), D(62))
    p = Matrix.Rotation(D(-42), 3, 'X') @ V(0.335 * math.sin(ph) * math.cos(th), 0.335 * math.sin(ph) * math.sin(th), 0.335 * math.cos(ph))
    q = V(0, 0.05, HEAD_C) + p
    if q.y < -0.2 and q.z < HEAD_C + 0.22: continue
    sphere('perm', 0.06 + _rr.uniform(-0.01, 0.01), MM['hair'], tuple(q), parent=mr0)
clip = empty('clip', (0, 0.3, HEAD_C + 0.05), mr0); clip.rotation_euler = (D(-20), 0, 0)
box('clip_bar', (0.2, 0.05, 0.045), (0, 0.04, 0), MM['clip'], 0.015, clip)
for tx in (-0.07, -0.023, 0.023, 0.07): box('clip_tooth', (0.022, 0.06, 0.08), (tx, 0.0, -0.05), MM['clip'], 0.008, clip)
# the duster: a floral wrap from the collar down, with a white collar trim
capsule('duster', 0.316, 0.36, MM['dress'], (0, 0, mzc - 0.29), parent=mr0)
bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.012, location=(0, 0, mzc - 0.29 + 0.18 + 0.1))
finish(bpy.context.active_object, R_['white'], mr0)
MOUTH_Z = mez - 0.18
mom['mouth'] = sphere('mom_mouth', 0.036, M['mouth'], (0, -0.288, MOUTH_Z), (1.3, 0.5, 0.6), parent=mr0)
for sx in (-1, 1):
    sphere('blush', 0.04, MM['blush'], (sx * 0.17, -0.245, mez - 0.12), (1.2, 0.3, 0.7), parent=mr0, rot=(0, 0, sx * D(35)))
    sphere('earring', 0.016, MM['gold'], (sx * 0.298, -0.02, mez - 0.1), parent=mr0)

# ============================================================ RIGS + PLACES
exec(open(os.path.join(HERE, '..', 'ep12', 'rig.py')).read())
doug['mouth'].location.y = -0.326
doug_r = Rig(doug, 'doug', M['doug'], M['doug'], lift=0.17)
mom_r = Rig(mom, 'mom', MM['body'], MM['body'], lift=0.17)
MOM_P, MOM_H = V(-0.6, 0.06, 0), 16           # Mom on the left cushion, turned a little toward Doug
DOUG_P, DOUG_H = V(0.62, 0.05, 0), -14         # Doug on the right cushion, turned a little toward Mom
KNEE = lambda sx: V(sx * 0.16, -0.50, SEAT + 0.075)
FOOT = lambda sx: V(sx * 0.18, -0.51, 0.03)
def upper_mat(P, H, rig, up, rot):
    return (Matrix.Translation(P) @ Matrix.Rotation(D(H), 4, 'Z') @ Matrix.Translation(V(0, 0, rig.base) + V(*up))
            @ Euler((D(rot[0]), D(rot[1]), D(rot[2]))).to_matrix().to_4x4())
D_EZ, M_EZ = doug_r.ez, mom_r.ez               # eye height in upper-local
D_EYE_L = V(0, -0.30, D_EZ); M_EYE_L = V(0, -0.27, M_EZ)

# ============================================================ ACTING CURVES (rot = (pitch fwd+, roll, yaw toward +X))
A0, A1 = BT.A_LEAN; T0, T1 = BT.A_TURN
F1_ = FILE['mom_dialogue_1']; F2_ = FILE['doug_dialogue_1']; F3_ = FILE['mom_dialogue_2']; F4_ = FILE['doug_dialogue_2']; F5_ = FILE['mom_dialogue_3']
CR0, CR1 = BT.C_RAISE; DL0, DL1 = BT.D_LEAN; EN0, EN1 = BT.E_NOD
M_ROT = [(1, (7, 0, -4)), (A0, (7, 0, -4)), (A1, (12, 0, -2)),                          # down at the phone -> leans in
         (T0, (11, 0, 0)), (T1, (1, -3, 22)), (F1_ + 40, (0, -3, 24)), (F1_ + 55, (2, 2, 22)), (SH['A'][1], (1, 0, 22)),
         (SH['C'][0], (1, 0, 22)), (CR0 + 6, (3, -3, 25)), (CR1, (5, -4, 27)), (BT.C_TAP, (6, -4, 26)), (BT.C_TAP + 8, (6, -2, 27)),
         (SH['C'][1], (5, -3, 26)), (SH['D'][1], (4, -3, 26)),
         (BT.E_BACK, (3, 0, 24)), (BT.E_BACK + 6, (-6, 3, 22)), (F5_ + 30, (-4, 3, 22)), (F5_ + 50, (1, 0, 23)),
         (EN0, (1, 0, 23)), (EN0 + 5, (7, 0, 23)), (EN0 + 10, (0, 0, 23)), (EN1, (4, 0, 23)), (N, (2, 0, 23))]
D_ROT = [(1, (6, 0, 0)), (BT.B_LOOKUP, (6, 0, 0)), (BT.B_LOOKUP + 8, (2, 1, -9)), (SH['B'][1], (2, 1, -9)),
         (DL0, (2, 1, -10)), (DL1, (9, 2, -18)), (F4_ + 30, (8, 2, -18)), (F4_ + 40, (5, 1, -15)), (SH['E'][1], (5, 1, -15)),
         (BT.TURN[0], (5, 1, -15)), (BT.TURN[1], (1, 0, 14)), (N, (1, 0, 14))]   # final: turns to the lens (camera F sits off his right)
def m_up(f): return (0, 0, 0.004 * math.sin(2 * math.pi * f / 90 + 0.5))
def d_up(f): return (0, 0, 0.003 * math.sin(2 * math.pi * f / 105))
def MU(f): return upper_mat(MOM_P, MOM_H, mom_r, m_up(f), ease_tab(M_ROT, f))
def DU(f): return upper_mat(DOUG_P, DOUG_H, doug_r, d_up(f), ease_tab(D_ROT, f))
def d_face_w(f): return DU(f) @ (D_EYE_L + V(0, 0, -0.04))
def m_face_w(f): return MU(f) @ (M_EYE_L + V(0, 0, -0.04))

# ============================================================ PHONES (parented to each upper body, keyed every frame)
PHW, PHT, PHH = 0.078, 0.011, 0.16
def make_phone(name, case_m, img):
    ph = box(name, (PHW, PHT, PHH), (0, 0, 0), case_m, 0.007); ph.rotation_mode = 'QUATERNION'
    sm_ = bpy.data.materials.new(name + '_scr'); sm_.use_nodes = True; nt = sm_.node_tree; nt.nodes.clear()
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.25
    out = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(os.path.join(HERE, 'screen', img)); tx.extension = 'CLIP'
    nt.links.new(tx.outputs['Color'], em.inputs['Color'])
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -PHT / 2 - 0.0008, 0.0))
    s = bpy.context.active_object; s.name = name + '_screen'; s.scale = (PHW - 0.007, PHH - 0.01, 1); s.rotation_euler = (D(90), 0, 0)
    s.data.materials.append(sm_); s.parent = ph
    cyl(name + '_lens', 0.008, 0.004, (0.022, PHT / 2 + 0.001, 0.06), mat(name + '_lensm', hexc('#08080a'), 0.1, 0.8), rot=(D(90), 0, 0), verts=24, parent=ph)
    return ph
m_phone = make_phone('mom_phone', MM['case'], 'mom_post.png'); m_phone.parent = mom_r.upper; m_phone.scale = (1.35, 1.35, 1.35)
d_phone = make_phone('doug_phone', M['phone'], 'doug_feed.png'); d_phone.parent = doug_r.upper
def face_quat(n, up=V(0, 0, 1), roll=0.0):
    """phone orientation whose screen (local -Y) faces along n (world/parent dir), long axis toward up"""
    ly = -n.normalized(); lz = (up - ly * up.dot(ly)).normalized(); lx = ly.cross(lz)
    return Matrix((lx, ly, lz)).transposed().to_quaternion() @ Quaternion(V(0, 1, 0), D(roll))
def look_q(p, tgt, roll=0.0): return face_quat(tgt - p, V(0, 0, 1), roll)
# Mom's phone, upper-local: READ (at her chest, facing her eyes) -> UP (raised, still hers) -> SHOW (pushed out to Doug, screen at his eyes)
M_EYES = M_EYE_L
def mom_phone_target(f, which):
    if which == 'me': return M_EYES
    return MU(f).inverted() @ d_face_w(f)                                   # Doug's eyes, in her upper-local
MP = dict(READ=V(0.05, -0.40, 0.40), UP=V(0.13, -0.44, 0.56), SHOW=V(0.40, -0.52, 0.60), HOLD=V(0.14, -0.43, 0.48))
MP_KEYS = [(1, 'READ', 'me'), (A0, 'READ', 'me'), (A1, 'READ', 'me'), (T0 + 2, 'UP', 'me'), (SH['A'][1], 'UP', 'me'),
           (CR0, 'UP', 'me'), (CR1, 'SHOW', 'him'), (SH['D'][1], 'SHOW', 'him'), (BT.E_BACK + 2, 'SHOW', 'him'), (BT.E_BACK + 14, 'HOLD', 'me'), (N, 'HOLD', 'me')]
def mom_phone(f):
    def st(k, w): p = MP[k]; return p, look_q(p, mom_phone_target(f, w), -8 if w == 'him' else 0)
    if f <= MP_KEYS[0][0]: return st(*MP_KEYS[0][1:])
    for (fa, ka, wa), (fb, kb, wb) in zip(MP_KEYS, MP_KEYS[1:]):
        if fa <= f <= fb:
            t = smooth((f - fa) / max(1, fb - fa)); pa, qa = st(ka, wa); pb, qb = st(kb, wb)
            jolt = V(0, 0, 0)
            if A0 <= f <= A0 + 8: jolt = V(0, -0.02, 0.012) * math.sin(math.pi * (f - A0) / 8)        # the little start when she sees it
            return pa.lerp(pb, t) + jolt, qa.slerp(qb, t)
    return st(*MP_KEYS[-1][1:])
D_PH = V(0.0, -0.50, 0.52)
def doug_phone(f):
    p = D_PH + V(0.003 * math.sin(f * 0.05), 0, 0.003 * math.sin(f * 0.04 + 1))
    if f >= BT.TURN[0]: p = p + V(0, 0.02, -0.06) * smooth((f - BT.TURN[0]) / 12)     # lowers it a touch as he turns away from her
    return p, look_q(p, D_EYE_L + V(0, 0, 0.02))
def PMAT(p, q): m = q.to_matrix().to_4x4(); m.translation = p; return m
GRIP = V(0.0, 0.03, -0.075)                     # fist behind the lower half of the phone (screen stays clear)
D_GRIP_N, D_GRIP_P = V(-0.035, 0.03, -0.085), V(0.035, 0.03, -0.085)
LAP = lambda sx: V(sx * 0.17, -0.42, 0.17)
CHEST = V(-0.06, -0.37, 0.42)
def tap_pt(f): p, q = mom_phone(f); return PMAT(p, q) @ V(-0.01, -0.06, 0.02)
def mom_free_hand(f):
    """her right hand (rig 'N' side, away from Doug): lap -> hand to chest in shock -> lap -> points/taps the screen -> chest again"""
    keys = [(1, LAP(-1)), (A0 + 1, LAP(-1)), (A0 + 7, CHEST), (F1_ + 50, CHEST), (F1_ + 64, LAP(-1)),
            (CR1 - 4, LAP(-1)), (BT.C_TAP - 6, None), (BT.C_TAP, None), (BT.C_TAP + 8, None), (BT.C_TAP + 18, LAP(-1)),
            (F5_ + 6, LAP(-1)), (F5_ + 14, V(-0.22, -0.46, 0.38)), (F5_ + 40, V(-0.2, -0.47, 0.42)), (F5_ + 62, CHEST + V(0, 0, 0.02)), (N, CHEST + V(0, 0, 0.02))]
    pts = []
    for fk, p in keys:
        if p is None:
            p = tap_pt(fk) + (V(0, -0.05, 0) if fk != BT.C_TAP else V(0, -0.012, 0))
        pts.append((fk, p))
    for (fa, pa), (fb, pb) in zip(pts, pts[1:]):
        if fa <= f <= fb:
            p = pa.lerp(pb, smooth((f - fa) / max(1, fb - fa)))
            if F5_ + 14 <= f <= F5_ + 40: p = p + V(0, 0, 0.012 * math.sin((f - F5_) * 0.9))          # small hand gesture with the words
            return p
    return pts[-1][1] if f > pts[-1][0] else pts[0][1]
M_SEAT_LEGS = {s: (tuple(FOOT(-1 if s == 'N' else 1)), (0, -1, 0.9)) for s in ('N', 'P')}
for f in range(1, N + 1):
    # ---- Mom
    mom_r.place(f, (MOM_P.x, MOM_P.y), MOM_H)
    p, q = mom_phone(f); m_phone.location = p; m_phone.rotation_quaternion = q
    m_phone.keyframe_insert('location', frame=f); m_phone.keyframe_insert('rotation_quaternion', frame=f)
    arms = {'P': (tuple(PMAT(p, q) @ GRIP), ('auto', (1, 0.3, -0.6))), 'N': (tuple(mom_free_hand(f)), ('auto', (-1, 0.2, -0.6)))}
    mom_r.pose(f, up=m_up(f), rot=ease_tab(M_ROT, f), arms=arms, legs=M_SEAT_LEGS)
    for s_ in ('N', 'P'):
        sx = -1 if s_ == 'N' else 1
        hip = V(0, 0, mom_r.base) + mom_r.hip_off[s_]
        mom_r.key_points(mom_r.leg[s_], f, (hip, KNEE(sx), FOOT(sx)))
        mom_r.foot[s_].location = FOOT(sx) + V(0, -0.035, 0.03); mom_r.foot[s_].keyframe_insert('location', frame=f)
    # ---- Doug
    doug_r.place(f, (DOUG_P.x, DOUG_P.y), DOUG_H)
    p, q = doug_phone(f); d_phone.location = p; d_phone.rotation_quaternion = q
    d_phone.keyframe_insert('location', frame=f); d_phone.keyframe_insert('rotation_quaternion', frame=f)
    Pm = PMAT(p, q)
    arms = {'N': (tuple(Pm @ D_GRIP_N), ('auto', (-1, 0.1, -0.5))), 'P': (tuple(Pm @ D_GRIP_P), ('auto', (1, 0.1, -0.5)))}
    doug_r.pose(f, up=d_up(f), rot=ease_tab(D_ROT, f), arms=arms, legs=M_SEAT_LEGS)
    for s_ in ('N', 'P'):
        sx = -1 if s_ == 'N' else 1
        hip = V(0, 0, doug_r.base) + doug_r.hip_off[s_]
        doug_r.key_points(doug_r.leg[s_], f, (hip, KNEE(sx), FOOT(sx)))
        doug_r.foot[s_].location = FOOT(sx) + V(0, -0.035, 0.03); doug_r.foot[s_].keyframe_insert('location', frame=f)

# ============================================================ FACES: mouths from the owner's recordings, lids, brows, gaze
import soundfile as _sf
def mouth_track(name, f0):
    a, sr = _sf.read(os.path.join(HERE, 'vo', name + '.wav')); hop = sr // 30
    rms, cen = [], []
    for i in range(0, len(a) - hop, hop):
        seg = a[i:i + 2 * hop] * np.hanning(len(a[i:i + 2 * hop]))
        S = np.abs(np.fft.rfft(seg)); fr_ = np.fft.rfftfreq(len(seg), 1 / sr)
        rms.append(np.sqrt(np.mean(a[i:i + hop] ** 2))); band = (fr_ > 300) & (fr_ < 4000)
        cen.append(float((S[band] * fr_[band]).sum() / (S[band].sum() + 1e-9)))
    rms = np.array(rms) / (np.percentile(rms, 97) + 1e-9); o_prev = 0.0; tr = {}
    for i, (r_, c_) in enumerate(zip(rms, cen)):
        o = max(0.0, min(1.0, (r_ - 0.07) / 0.55))
        o = o if o > o_prev else o_prev * 0.5 + o * 0.5; o_prev = o
        w = max(0.0, min(1.0, (c_ - 1100) / 1300)) if o > 0.08 else 0.5
        tr[f0 + i] = (o, w)
    return tr
MTR = {'doug': {}, 'mom': {}}
for k in BT.LINES: MTR['mom' if k.startswith('mom') else 'doug'].update(mouth_track(k, FILE[k]))
def mtrack(who, f): return MTR[who].get(f, (0.0, 0.5))
D_LIDS = [o for o in bpy.data.objects if o.name.startswith('doug_lid')]
M_LIDS = [o for o in bpy.data.objects if o.name.startswith('mom_lid')]
def lids_set(objs, f, deg):
    for o in objs: o.rotation_euler = (D(deg), 0, 0); o.keyframe_insert('rotation_euler', frame=f)
def blink_amt(f, blinks):
    for b_, dur in blinks:
        if abs(f - b_) <= dur: return 1 - abs(f - b_) / (dur + 1)
    return 0.0
M_BZ = [b.location.z - 0.018 for b in mom['brows']]
def m_brows(f, dz, tilt):
    for i, bp in enumerate(mom['brows']):
        sx = -1 if i == 0 else 1
        bp.location = (bp.location.x, bp.location.y, M_BZ[i] + dz); bp.keyframe_insert('location', frame=f)
        bp.rotation_euler = (0, sx * D(-tilt), 0); bp.keyframe_insert('rotation_euler', frame=f)
# Mom: relaxed scrolling (12) -> SNAP wide (-34) -> alarmed (-24) | defensive, confident (8, brows down) | surprised again (-34) -> concern (-14) -> sure (2)
M_LID = [(1, -8), (A0 - 1, -8), (A0 + 2, -46), (F1_ + 40, -40), (F1_ + 70, -32), (SH['B'][1], -28),
         (SH['C'][0], -14), (CR1, -10), (SH['C'][1], -12), (SH['D'][1], -16),
         (F5_ + 2, -16), (F5_ + 6, -46), (F5_ + 24, -44), (F5_ + 40, -30), (EN0, -26), (EN1, -18), (N, -18)]
M_BLINKS = [(A1 + 14, 2), (F1_ + 62, 2), (SH['C'][0] + 5, 2), (BT.C_TAP + 12, 2), (F5_ + 28, 2), (EN1 + 4, 2)]
# brows (dz, tilt): + tilt = inner ends down (stern), - tilt = inner ends up (worried)
M_BROW = [(1, (0.0, 0)), (A0 - 1, (0.0, 0)), (A0 + 2, (0.035, -4)), (F1_ + 60, (0.03, -8)), (SH['B'][1], (0.02, -6)),
          (SH['C'][0], (-0.01, 10)), (CR1, (-0.012, 12)), (SH['C'][1], (-0.008, 8)), (SH['D'][1], (0.0, 4)),
          (F5_ + 2, (0.0, 4)), (F5_ + 6, (0.04, -4)), (F5_ + 30, (0.032, -12)), (F5_ + 60, (0.025, -14)), (EN1, (0.012, -6)), (N, (0.012, -6))]
# Doug: deadpan 23, tired 26, reading squint 33, final stare half-lowered 30 + one slow blink
D_LID = [(1, 22), (BT.B_LOOKUP + 6, 23), (SH['B'][1], 23), (DL1, 26), (BT.D_READ + 10, 28), (F4_ + 30, 28), (F4_ + 40, 24),
         (SH['E'][1], 24), (BT.TURN[1], 24), (N, 25)]
D_BLINKS = [(BT.B_LOOKUP + 2, 2), (F2_ + 60, 2), (SH['D'][0] + 3, 2), (F4_ + 34, 2), (BT.TURN[0] + 1, 2), (BT.TURN[1] + 22, 4)]
SAC = {}; _rng = _r.Random(19)
def saccade(who, f, amp=1.0):
    k = (who, f // 11)
    if k not in SAC: SAC[k] = V(_rng.uniform(-0.03, 0.03), 0, _rng.uniform(-0.02, 0.02))
    return SAC[k] * amp
def aim(pivot, Tp, clamp_yaw=40, clamp_pitch=48):
    P = pivot.matrix_world.translation; Rp = pivot.parent.matrix_world.to_3x3().normalized()
    d = Rp.inverted() @ (Tp - P)
    yaw = math.degrees(math.atan2(d.x, -d.y)); pitch_ = -math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    yaw = max(-clamp_yaw, min(clamp_yaw, yaw)); pitch_ = max(-clamp_pitch, min(clamp_pitch, pitch_))
    pivot.rotation_euler = (D(pitch_), 0, D(yaw)); pivot.keyframe_insert('rotation_euler', frame=scene.frame_current)
def blend(keys, f):
    """keys [(frame, fn)] -> point; 4-frame eye moves between targets (eyes jump, they don't drift)"""
    cur = keys[0][1]()
    for i, (fk, fn) in enumerate(keys):
        if f >= fk:
            prev = keys[i - 1][1]() if i else fn(); t = smooth((f - fk) / 4.0); cur = prev.lerp(fn(), t)
    return cur
CUR = {}
def m_scr(): return m_phone.matrix_world @ V(0, -0.01, 0.01)
def m_date(): return m_phone.matrix_world @ V(0, -0.01, 0.05)
def d_scr(): return d_phone.matrix_world @ V(0, -0.01, 0.01)
def d_face(): return doug_r.upper.matrix_world @ (D_EYE_L + V(0, -0.02, -0.03))
def m_face(): return mom_r.upper.matrix_world @ (M_EYE_L + V(0, -0.02, -0.02))
def cam_pt(): return CUR['camF']
M_GAZE = [(1, m_scr), (T0 + 1, d_face), (BT.C_TAP - 8, m_scr), (BT.C_TAP + 6, d_face), (N, d_face)]
D_GAZE = [(1, d_scr), (BT.B_LOOKUP, m_face), (SH['B'][1] - 2, m_face), (DL0, m_scr), (BT.D_READ, m_date), (F4_ + 28, m_face),
          (BT.TURN[0], cam_pt), (N, cam_pt)]
# head shots: where the camera F sits (Doug's tight close-up, straight into the lens once he has turned)
scene.frame_set(N); bpy.context.view_layer.update()
DFN = d_face()
_fw = (doug_r.upper.matrix_world.to_3x3() @ V(0, -1, 0)).normalized()
CUR['camF'] = DFN + _fw * 1.45 + V(0, 0, 0.02)
for f in range(1, N + 1):
    scene.frame_set(f)
    # Mom
    o, w = mtrack('mom', f)
    lv = ease_tab(M_LID, f); lids_set(M_LIDS, f, lv + (95 - lv) * blink_amt(f, M_BLINKS) - 5 * o)
    dz, tl = ease_tab(M_BROW, f); m_brows(f, dz + 0.006 * o, tl)
    tgt = blend(M_GAZE, f) + saccade('m', f, 0.5)
    for pv in mom['eyes']: aim(pv, tgt)
    m = mom['mouth']
    m.scale = (1.3 * (1 + 0.18 * o) * (0.82 + 0.4 * w), 0.5, 0.55 * (1 + 2.6 * o) * (1.1 - 0.3 * w)); m.keyframe_insert('scale', frame=f)
    # Doug
    o, w = mtrack('doug', f)
    lv = ease_tab(D_LID, f); lids_set(D_LIDS, f, lv + (95 - lv) * blink_amt(f, D_BLINKS))
    still = f >= BT.TURN[1] + 2
    tgt = blend(D_GAZE, f) + saccade('d', f, 0.0 if still else 0.35)
    for pv in doug['eyes']: aim(pv, tgt)
    m = doug['mouth']
    m.scale = (1 + 2.0 * o, 1, (1 + 0.15 * o) * (0.82 + 0.36 * w)); m.keyframe_insert('scale', frame=f)

# ============================================================ CAMERAS
def rotz(v, deg):
    c, s = math.cos(D(deg)), math.sin(D(deg)); return V(v.x * c - v.y * s, v.x * s + v.y * c, v.z)
scene.frame_set(SH['A'][1]); bpy.context.view_layer.update(); MF = m_face()
scene.frame_set(SH['B'][0] + 20); bpy.context.view_layer.update(); DF = d_face()
scene.frame_set(SH['O'][0] + 16); bpy.context.view_layer.update(); PHN = m_scr(); PHD = m_date(); DFO = d_face()
md = (DF - MF); md.z = 0; md.normalize()                 # Mom -> Doug, flat
fwd_m = rotz(V(0, -1, 0), MOM_H); fwd_d = rotz(V(0, -1, 0), DOUG_H)
def cam_for(f):
    """-> (location, target, lens, fstop, focus)"""
    if f <= SH['A'][1]:            # Mom MCU, from just right of front (Doug's side)
        t = smooth((f - 1) / (SH['A'][1] - 1)); d0 = rotz(fwd_m, 24)
        return MF + d0 * (1.5 - 0.05 * t) + V(0, 0, -0.02), MF + V(0, 0, -0.08), 30, 4.0, MF
    if f <= SH['B'][1]:            # Doug MCU, from just left of front (Mom's side)
        d0 = rotz(fwd_d, -24); return DF + d0 * 1.95 + V(0, 0, -0.02), DF + V(0, 0, -0.1), 30, 4.0, DF
    if f <= SH['C'][1]:            # Mom medium: the phone pushed out toward Doug
        t = smooth((f - SH['C'][0]) / (SH['C'][1] - SH['C'][0])); d0 = rotz(fwd_m, 40)
        return MF + d0 * (1.6 - 0.06 * t) + V(0, 0, -0.06), MF + V(0.2, 0, -0.2), 30, 5.6, MF + V(0.1, 0, -0.1)
    if f <= SH['O'][1]:            # insert from just beside Doug's eyeline onto her phone: the date is readable
        t = smooth((f - SH['O'][0]) / (SH['O'][1] - SH['O'][0]))
        to_ph = (PHN - DFO); side = rotz(V(to_ph.x, to_ph.y, 0).normalized(), 90)
        p = DFO + to_ph * 0.42 + side * 0.035 + V(0, 0, -0.01)            # outside his head, under the brim
        if os.environ.get('DBG'): print('DBG O cam', tuple(round(x, 3) for x in p))
        tg = PHD + (PHN - PHD) * 0.55
        return p + (tg - p) * (0.08 * t), tg, 50, 8.0, tg
    if f <= SH['D'][1]:            # Doug CU while he reads and says it
        d0 = rotz(fwd_d, -26); return DF + d0 * 1.6 + V(0, 0, -0.03), DF + V(0, 0, -0.09), 32, 4.0, DF
    if f <= SH['E'][1]:            # Mom MCU, punchline: steady
        d0 = rotz(fwd_m, 22); return MF + d0 * 1.35 + V(0, 0, -0.03), MF + V(0, 0, -0.12), 31, 4.0, MF
    return CUR['camF'], DFN + V(0, 0, -0.02), 36, 4.0, DFN   # Doug tight CU, he turns into the lens
cam_data.clip_start = 0.02
scene.view_settings.exposure = -0.45
def cam_setup(name):
    a_, b_ = SH[name]
    for f in range(a_, b_ + 1):
        p, tgt, lens, fs, fp = cam_for(f)
        key(cam, 'location', f, p); key(target, 'location', f, tgt); key(focus, 'location', f, fp)
        key(cam_data, 'lens', f, lens); key(cam_data.dof, 'aperture_fstop', f, fs)
if SHOT == 'QA':
    print('MF', tuple(round(x, 3) for x in MF), 'DF', tuple(round(x, 3) for x in DF), 'camF', tuple(round(x, 3) for x in CUR['camF']))
    for f in (1, 20, 60, 200, 260, 290, 330, 420, 500, 540):
        scene.frame_set(f); bpy.context.view_layer.update()
        print(f, 'mom phone', tuple(round(x, 3) for x in m_phone.matrix_world.translation), 'mom hand N', tuple(round(x, 3) for x in mom_r.hand['N'].matrix_world.translation),
              'arm reach P', round((mom_r.hand['P'].location - mom_r.shoulder('P')).length, 3), 'N', round((mom_r.hand['N'].location - mom_r.shoulder('N')).length, 3))
    sys.exit(0)
if SHOT == 'LOOK':                 # library stills
    which = os.environ.get('LOOKCAM', 'mom'); f = STILL if STILL > 0 else 300; scene.frame_set(f); bpy.context.view_layer.update()
    if which == 'mom': p, tg, ln = m_face() + rotz(fwd_m, 10) * 1.6 + V(0, 0, -0.05), m_face() + V(0, 0, -0.2), 30
    elif which == 'doug': p, tg, ln = d_face() + rotz(fwd_d, -10) * 1.6 + V(0, 0, -0.05), d_face() + V(0, 0, -0.2), 30
    else: p, tg, ln = V(0.0, -2.25, 1.35), V(0, 0.2, 1.0), 18
    key(cam, 'location', f, p); key(target, 'location', f, tg); key(focus, 'location', f, tg); key(cam_data, 'lens', f, ln); key(cam_data.dof, 'aperture_fstop', f, 8.0)
    render(N)
else:
    cam_setup(SHOT); f0, f1 = SH[SHOT]; scene.frame_set(f0)
    FR = FR or f'{f0}-{f1}'
    render(N)
