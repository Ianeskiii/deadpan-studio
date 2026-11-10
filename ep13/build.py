"""Tube Town - When you watch anime with subtitles.  usage: python3 build.py SHOT OUTDIR [opts]   (SHOT = W O M X | QA)"""
import os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'tubetown')
exec(open(os.path.join(LIB, 'lib.py')).read())
exec(open(os.path.join(LIB, 'helpers.py')).read())
from mathutils import Matrix
from PIL import Image as PILImage
def V(*a): return Vector(a)
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
BEAT = 15
T = json.load(open(os.path.join(HERE, 'vo', 'timing.json')))
SUB = {int(k): v for k, v in json.load(open(os.path.join(HERE, 'vo', 'subs_by_frame.json'))).items()}
FPS = 30; L = T['lines']
F_SILENCE = int(round(T['end_talk'] * FPS)) + 1          # first silent frame (1-based)
F_BLACK = int(round(T['black'] * FPS)) + 1
N = int(round(T['end'] * FPS))
NTV = len([f for f in os.listdir(os.path.join(HERE, 'tv')) if f.endswith('.png')])

# ============================================================ LIVING ROOM (night, lit by the TV)
tina['root'].location = (-80, 0, 0)
R_ = dict(
    floor=brick_mat('planks2', hexc('#6b4a33'), hexc('#5f412c'), hexc('#3f2a1c'), 1.2, 1.6, 0.18, 0.37, 0.55),
    wall=mat('lr_wall', hexc('#3b4a5c'), 0.9), wall2=mat('lr_wall2', hexc('#2f3b4a'), 0.9),
    couch=mat('couch', hexc('#5a6e5a'), 0.85, 0.0, sheen=0.5), cushion=mat('cushion', hexc('#667d66'), 0.85, 0.0, sheen=0.5),
    wood=mat('lr_wood', hexc('#4a3426'), 0.5, 0.2), black=mat('tvblack', hexc('#111214'), 0.3, 0.4),
    rug=mat('rug', hexc('#7a4d4a'), 0.95), bowl=mat('bowl', hexc('#d9e2ea'), 0.3, 0.2), pop=mat('popcorn', hexc('#f3e2b5'), 0.8),
    pop2=mat('popcorn2', hexc('#e8c879'), 0.8), can=mat('can', hexc('#c0392b'), 0.25, 0.7), night=mat('night', (0, 0, 0), 0.5, 0, hexc('#2b3f78'), 0.6),
    plant=mat('leaf2', hexc('#2f5e3a'), 0.6), pot=mat('pot2', hexc('#8a5a3c'), 0.6), frame=mat('pframe', hexc('#c9a26a'), 0.4, 0.4),
    art=mat('art', hexc('#a35a6a'), 0.8), lamp=mat('lamp2', (0, 0, 0), 0.4, 0, hexc('#ffcf8a'), 3.0),
)
box('lr_floor', (10, 10, 0.1), (0, 0, -0.05), R_['floor'])
box('lr_back', (10, 0.2, 3.2), (0, -2.15, 1.6), R_['wall'])          # wall behind the TV
box('lr_rear', (10, 0.2, 3.2), (0, 1.55, 1.6), R_['wall2'])          # wall behind the couch
box('lr_left', (0.2, 8, 3.2), (-2.6, 0, 1.6), R_['wall2'])
box('lr_right', (0.2, 8, 3.2), (2.6, 0, 1.6), R_['wall'])
box('lr_ceiling', (10, 10, 0.1), (0, 0, 3.2), R_['wall2'])
box('rug', (2.6, 2.0, 0.012), (0, -0.85, 0.006), R_['rug'], 0.004)
box('window', (0.05, 1.2, 1.1), (2.47, 0.2, 1.6), R_['night'])
for wy in (-0.4, 0.2, 0.8): box('win_mull', (0.06, 0.05, 1.15), (2.45, wy, 1.6), R_['wood'])
# couch (seat top at Doug's sitting height)
SEAT = 0.42
box('couch_base', (2.0, 0.85, SEAT - 0.12), (0, 0.15, (SEAT - 0.12) / 2), R_['couch'], 0.04)
for cx in (-0.48, 0.48): box('seat_cushion', (0.94, 0.8, 0.13), (cx, 0.12, SEAT - 0.065), R_['cushion'], 0.05)
box('couch_back', (2.0, 0.24, 0.62), (0, 0.5, SEAT + 0.22), R_['couch'], 0.08)
for cx in (-0.98, 0.98): box('arm_rest', (0.24, 0.9, 0.55), (cx, 0.15, 0.36), R_['couch'], 0.08)
# TV on a low cabinet, big and close (screen bottom carries the subtitles)
TVW, TVH, TVZ, TVY = 1.72, 0.97, 1.12, -1.95
box('cabinet', (2.1, 0.45, 0.5), (0, TVY + 0.02, 0.25), R_['wood'], 0.02)
box('tv_body', (TVW + 0.06, 0.06, TVH + 0.06), (0, TVY, TVZ), R_['black'], 0.01)
box('tv_foot', (0.5, 0.25, 0.04), (0, TVY + 0.02, 0.52), R_['black'])
img = bpy.data.images.load(os.path.join(HERE, 'tv', 'tv_0001.png')); img.source = 'SEQUENCE'
scr_m = bpy.data.materials.new('tv_screen'); scr_m.use_nodes = True; nt = scr_m.node_tree; nt.nodes.clear()
tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.image_user.frame_duration = NTV; tex.image_user.frame_start = 1
tex.image_user.frame_offset = 0; tex.image_user.use_auto_refresh = True; tex.extension = 'CLIP'
em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.35
out = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(tex.outputs['Color'], em.inputs['Color']); nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, TVY + 0.032, TVZ))
scr = bpy.context.active_object; scr.name = 'tv_screen'; scr.scale = (TVW, TVH, 1); scr.rotation_euler = (D(90), 0, 0)
scr.data.materials.append(scr_m)
# UVs: plane faces +y after the rotation; flip U so the picture reads correctly from the couch
for loop in scr.data.loops:
    uv = scr.data.uv_layers.active.data[loop.index].uv; uv.x = 1 - uv.x
# coffee table + props
box('coffee_table', (0.9, 0.5, 0.05), (0.15, -0.95, 0.38), R_['wood'], 0.01)
for lx in (-0.25, 0.55):
    for ly in (-1.15, -0.75): box('ct_leg', (0.04, 0.04, 0.36), (lx, ly, 0.18), R_['wood'])
cyl('soda', 0.033, 0.12, (0.45, -0.9, 0.465), R_['can'])
box('remote', (0.05, 0.17, 0.02), (-0.1, -0.88, 0.415), R_['black'], 0.006).rotation_euler = (0, 0, D(20))
# side decor
cyl('pot', 0.16, 0.32, (-1.9, -1.7, 0.16), R_['pot'])
for i in range(7):
    a_ = i * 2.3; sphere('leaf', 0.13, R_['plant'], (-1.9 + 0.1 * math.cos(a_), -1.7 + 0.1 * math.sin(a_), 0.5 + 0.06 * (i % 3)), (1, 0.5, 1.7), rot=(D(20) * math.cos(a_), D(20) * math.sin(a_), a_))
box('art_frame', (0.7, 0.04, 0.5), (1.4, -2.03, 1.75), R_['frame'], 0.01); box('art', (0.62, 0.02, 0.42), (1.4, -2.0, 1.75), R_['art'])
# a dim warm lamp in the far corner so the room is not pitch black
cyl('lamp_pole', 0.015, 1.4, (2.2, 1.25, 0.7), R_['black']); sphere('lamp_shade', 0.14, R_['lamp'], (2.2, 1.25, 1.45), (1, 1, 0.8))
pl = bpy.data.lights.new('corner', 'POINT'); pl.energy = 35; pl.color = hexc('#ffc27a'); pl.shadow_soft_size = 0.2
link(bpy.data.objects.new('corner', pl)).location = (2.2, 1.25, 1.42)
world(hexc('#1c2333'), 0.24)
area('tv_fill', (0.0, -1.5, 1.85), (D(62), 0, 0), 60, hexc('#e8eeff'), (1.4, 0.8))      # soft cool fill from the screen side
area('rim', (-1.2, 1.2, 2.1), (D(-55), 0, D(-140)), 70, hexc('#8fa6ff'), (1.0, 1.0))
area('moon', (2.3, 0.2, 1.6), (0, D(-90), 0), 25, hexc('#7f9cff'), (1.0, 1.0))
# TV glow: an area light at the screen whose colour/brightness follow the picture every frame
tvl = bpy.data.lights.new('tvglow', 'AREA'); tvl.shape = 'RECTANGLE'; tvl.size = TVW; tvl.size_y = TVH
tvl_o = link(bpy.data.objects.new('tvglow', tvl)); tvl_o.location = (0, TVY + 0.08, TVZ); tvl_o.rotation_euler = (D(-90), 0, 0)
tvl.cycles.is_caustics_light = False if hasattr(tvl.cycles, 'is_caustics_light') else None
for f in range(1, N + 1):
    if f < F_BLACK:
        im = PILImage.open(os.path.join(HERE, 'tv', f'tv_{min(f, NTV):04d}.png')).resize((16, 9)); a_ = np.asarray(im, dtype=np.float32) / 255
        c = a_.reshape(-1, 3).mean(0); lum = float(c @ np.array([0.3, 0.59, 0.11]))
        col = tuple(float(x) for x in (c / max(1e-3, c.max())))
    else:
        col, lum = (1, 1, 1), 0
    tvl.color = tuple(0.55 + 0.45 * x for x in col); tvl.energy = 520 * (0.35 + lum)
    tvl.keyframe_insert('color', frame=f); tvl.keyframe_insert('energy', frame=f)
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.name.startswith('area_'): pass

# ============================================================ DOUG on the couch with a bowl of popcorn
exec(open(os.path.join(HERE, '..', 'ep12', 'rig.py')).read())
doug['mouth'].location.y = -0.326
doug_r = Rig(doug, 'doug', M['doug'], M['doug'], lift=0.17)
D_EZ = doug_r.ez
SIT_LEGS = {'N': ((-0.17, -0.42, 0.0), (0, -1, 0.9)), 'P': ((0.17, -0.42, 0.0), (0, -1, 0.9))}
BOWL_ARMS = {'N': ((-0.19, -0.36, 0.13), ('auto', (-1, 0.1, -0.4))), 'P': ((0.19, -0.36, 0.13), ('auto', (1, 0.1, -0.4)))}
doug_r.place(1, (0, 0.05), 0)
for f in (1, N):
    doug_r.pose(f, up=(0, 0, 0.0), rot=(0, 0, 0), arms=BOWL_ARMS, legs=SIT_LEGS)
# bowl in his lap (parented to the upper body)
bm_ = bmesh.new(); bmesh.ops.create_uvsphere(bm_, u_segments=40, v_segments=20, radius=0.15)
bmesh.ops.bisect_plane(bm_, geom=bm_.verts[:] + bm_.edges[:] + bm_.faces[:], plane_co=(0, 0, 0), plane_no=(0, 0, 1), clear_outer=True)
me_ = bpy.data.meshes.new('bowl'); bm_.to_mesh(me_); bm_.free()
bowl = link(bpy.data.objects.new('bowl', me_)); bowl.modifiers.new('sol', 'SOLIDIFY').thickness = 0.012
finish(bowl, R_['bowl'], doug_r.upper); bowl.location = (0, -0.34, 0.19); bowl.scale = (1, 1, 0.62)
rr = random.Random(5)
for i in range(26):
    a_ = rr.uniform(0, 2 * math.pi); r_ = rr.uniform(0, 0.11)
    sphere('pop', rr.uniform(0.022, 0.03), R_['pop'] if i % 3 else R_['pop2'], (r_ * math.cos(a_), -0.34 + r_ * math.sin(a_), 0.19 + rr.uniform(-0.005, 0.03)), parent=doug_r.upper)

# ============================================================ EYES: centre of the screen <-> subtitles, escalating
D_LIDS = [o for o in bpy.data.objects if o.name.startswith('doug_lid')]
scene.frame_set(1)
EYE = doug['eyes'][0].matrix_world.translation.copy()
TV_C = V(0, TVY, TVZ + 0.04)
d_ = TV_C - EYE
YAW_C = math.degrees(math.atan2(d_.x, -d_.y)); PITCH_C = -math.degrees(math.atan2(d_.z, math.hypot(d_.x, d_.y)))
PITCH_C = float(os.environ.get('PC', 14.0)); PITCH_DOWN = PITCH_C + float(os.environ.get('PD', 26.0))           # reading the subtitles at the bottom of the screen (exaggerated for readability)
def phase_of(i): return 0 if i == 0 else (1 if i < 4 else (2 if i < 10 else 3))
# build a per-frame target: 0 = centre, 1 = subtitles
look = {f: 0.0 for f in range(1, N + 1)}
moves = []   # (frame, target, duration)
for i, l in enumerate(L):
    a = int(round(l['t'] * FPS)) + 1
    nxt = int(round(L[i + 1]['t'] * FPS)) + 1 if i + 1 < len(L) else F_SILENCE
    ph = phase_of(i)
    if ph <= 1:      # natural: a beat to notice, read, look back up at the action
        lat, mv = (8, 7) if ph == 0 else (4 - min(i, 3) // 2, 6 - i)
        read = int(len(l['sub']) * 1.15) + 6
        down0 = a + lat; up0 = min(nxt - 4, down0 + mv + read)
        moves += [(down0, 1, mv), (up0, 0, mv)]
    elif ph == 2:    # escalation: quicker, more mechanical
        k = i - 4; lat = 2; mv = max(1, 3 - k // 2)
        down0 = a + lat; up0 = max(down0 + mv + 2, (a + nxt) // 2 + 1)
        moves += [(down0, 1, mv), (up0, 0, mv)]
    else:            # the barrage: vertical windshield wipers, 2 frames down / 2 frames up
        f = a
        while f + 4 <= nxt:
            moves += [(f, 1, 1), (f + 2, 0, 1)]; f += 4
moves.sort()
val = 0.0; mi = 0; cur_from, cur_to, cur_a, cur_d = 0.0, 0.0, 1, 1
for f in range(1, N + 1):
    while mi < len(moves) and moves[mi][0] <= f:
        cur_from = val; cur_a, cur_to, cur_d = moves[mi]; mi += 1
    t = min(1.0, (f - cur_a + 1) / max(1, cur_d))
    val = cur_from + (cur_to - cur_from) * (smooth(t) if cur_d > 2 else t)
    if f >= F_SILENCE: val = 0.0          # silence: pupils stop dead, centred
    look[f] = val
BLINKS = [(14, 3), (int(L[1]['t'] * FPS) - 6, 3), (int(L[3]['t'] * FPS) - 4, 3)]
def blink_amt(f):
    for b, dur in BLINKS:
        if abs(f - b) <= dur: return 1 - abs(f - b) / (dur + 1)
    return 0.0
LID = float(os.environ.get('LIDV', 12))
for f in range(1, N + 1):
    p = PITCH_C + (PITCH_DOWN - PITCH_C) * look[f]
    for pv in doug['eyes']:
        pv.rotation_euler = (D(p), 0, D(YAW_C)); pv.keyframe_insert('rotation_euler', frame=f)
    for o in D_LIDS: o.rotation_euler = (D(LID + (95 - LID) * blink_amt(f)), 0, 0); o.keyframe_insert('rotation_euler', frame=f)
# constant interpolation on the eyes so snaps are true snaps
for pv in doug['eyes']:
    for fc in (pv.animation_data.action.fcurves if hasattr(pv.animation_data.action, 'fcurves') else []):
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
json.dump({'look': look, 'moves': moves, 'F_SILENCE': F_SILENCE, 'F_BLACK': F_BLACK, 'N': N}, open(os.path.join(HERE, 'eyes.json'), 'w'))

# ============================================================ CAMERAS
F_X = int(round(L[10]['t'] * FPS)) + 1 - 2          # extreme close-up from the start of the final barrage
F_PUSH = int(round(L[4]['t'] * FPS)) + 1             # slow push-in through the escalation
SHOTS = {'W': (1, 20), 'O': (21, 45), 'M': (46, F_X - 1), 'X': (F_X, F_BLACK - 1)}
EYEC = EYE + V(0.0, 0, 0)
FACE = doug_r.upper.matrix_world @ V(0, -0.2, D_EZ - 0.08)
def cam_for(f):
    if f <= 20:   return V(1.95, 1.35, 1.8), V(-0.25, -1.0, 0.95), 22, 4.0
    if f <= 45:   return V(1.0, 1.0, 1.9), V(-0.2, TVY, TVZ - 0.1), 36, 4.5      # over his shoulder: anime + subtitles
    if f < F_X:
        t = 0.0 if f < F_PUSH else smooth((f - F_PUSH) / max(1, F_X - F_PUSH))
        p = V(0.42, -1.55, 1.4).lerp(V(0.24, -1.1, 1.44), t); lens = 30 + 12 * t
        return p, FACE + V(0, 0, 0.02), lens, 3.2
    return V(0.1, -1.42, 1.31), FACE + V(-0.02, 0, 0.1), 40, 5.6
def cam_setup(name):
    a_, b_ = SHOTS[name]
    for f in range(a_, b_ + 1):
        p, tgt, lens, fs = cam_for(f)
        key(cam, 'location', f, p); key(target, 'location', f, tgt); key(focus, 'location', f, FACE if name in ('M', 'X') else tgt)
        key(cam_data, 'lens', f, lens); key(cam_data.dof, 'aperture_fstop', f, fs)
if SHOT == 'QA':
    print('QA yaw', round(YAW_C, 1), 'pitch centre', round(PITCH_C, 1), 'down', round(PITCH_DOWN, 1), 'F_SILENCE', F_SILENCE, 'F_BLACK', F_BLACK, 'N', N, 'SHOTS', SHOTS)
    json.dump({'SHOTS': SHOTS, 'F_SILENCE': F_SILENCE, 'F_BLACK': F_BLACK, 'N': N}, open(os.path.join(HERE, 'beats.json'), 'w'))
else:
    cam_setup(SHOT); f0, f1 = SHOTS[SHOT]; scene.frame_set(f0)
    FR = FR or f'{f0}-{f1}'
    render(N)
