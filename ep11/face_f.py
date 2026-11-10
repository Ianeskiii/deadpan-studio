# ============================================================ FACE PASS v6 (per frame): eye tracking, saccades, blinks, lids, brows, mouth
import soundfile as _sf
_rng = random.Random(11)
def _speech_env():
    env = {}
    for name, f0 in LINES.items():
        a, sr = _sf.read(os.path.join(VO, name + '.wav')); hop = sr // 30
        r = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)]); r /= (r.max() + 1e-9)
        for i, v in enumerate(r):
            env.setdefault('doug' if name == 'd1' else 'ricky', {})[f0 + i] = max(0.0, min(1.0, (v - 0.07) / 0.55))
    return env
SPEECH = _speech_env()
def speech(who, f): return SPEECH.get(who, {}).get(f, 0.0)
def ease_tab(keys, f):
    """keys: [(frame, value_tuple)] -> smoothly interpolated tuple"""
    if f <= keys[0][0]: return keys[0][1]
    if f >= keys[-1][0]: return keys[-1][1]
    for (fa, va), (fb, vb) in zip(keys, keys[1:]):
        if fa <= f <= fb:
            t = smooth((f - fa) / max(1, fb - fa)); return tuple(x + (y - x) * t for x, y in zip(va, vb))
# --- emotion tables: (lid_base, browL_dz, browR_dz, browL_tilt, browR_tilt, mouth_wide)
R_EMO = [(1, (24, -0.01, -0.01, 14, 14, 0.0)),          # sly, confident
         (64, (16, -0.02, -0.02, 20, 20, 0.0)),         # demanding
         (120, (6, -0.005, 0.05, 4, -10, 0.0)),         # confused (one brow up)
         (150, (10, -0.01, 0.04, 6, -6, 0.0)),
         (157, (50, -0.035, -0.035, 26, 26, 0.6)),      # straining
         (258, (40, -0.045, -0.045, 30, 30, 0.7)),      # annoyed
         (330, (40, -0.045, -0.045, 30, 30, 0.7)),
         (336, (-10, 0.05, 0.05, -12, -12, 0.0)),       # shocked mid-air
         (352, (30, 0.0, 0.0, 0, 0, 0.0)),              # dazed
         (357, (42, -0.03, -0.03, 24, 24, 0.2)),        # fed up
         (405, (48, 0.02, 0.02, -20, -20, 0.0)),        # defeated (inner brows up)
         (480, (50, 0.02, 0.02, -20, -20, 0.0))]
D_EMO = [(1, (44, 0.01, 0.01, -4, -4)), (58, (44, 0.01, 0.01, -4, -4)),
         (64, (82, 0.015, 0.015, -6, -6)),             # eyes shut, blissed out
         (REACT0 + 2, (82, 0.015, 0.015, -6, -6)),
         (REACT0 + 6, (14, -0.005, -0.005, 6, 6)),     # deadpan: eyes open, flat brows
         (REACT1 - 5, (14, -0.005, -0.005, 6, 6)),
         (REACT1, (82, 0.015, 0.015, -6, -6)), (480, (82, 0.015, 0.015, -6, -6))]
# --- blinks (frame of full closure)
R_BLINKS = [44, 70, 118, 140, 188, 230, 262, 300, 352, 355, 372, 400, 432, 458, 476]
D_BLINKS = [18, 47, 449]
def blink_amt(f, blinks, dur=3):
    for b in blinks:
        if abs(f - b) <= dur: return 1 - abs(f - b) / (dur + 1)
    return 0.0
# --- gaze targets (world points), with held saccade offsets
def doug_face(): return doug_r.upper.matrix_world @ V(0, -0.25, D_EZ - 0.05)
def ricky_face(): return ricky_r.upper.matrix_world @ V(0, -0.25, R_EZ - 0.05)
def bag_pt(): return bag.matrix_world.translation.copy()
def cam_pt(): return cam.matrix_world.translation.copy() if cam.animation_data else V(0, 0, 1.2)
def r_target(f):
    if f < 61: return doug_face() if (f // 12) % 3 else bag_pt()          # sizing him up: face / bag
    if f < GRAB - 6: return doug_face()
    if f < SPIN: return bag_pt() if (f // 20) % 4 else doug_face()        # mostly on the bag, flicks to Doug
    if f < 352: return doug_face()
    if LINES['g4'] + 20 <= f < LINES['g4'] + 42: return ricky_face() + V(0.0, -0.4, 0.6)   # eye-roll on "you know what?"
    if LINES['g4'] + 50 <= f < REACT0 + 8: return ricky_face() + V(0.5, -0.6, -0.5)      # looks down on "forget it"
    return doug_face()
def d_target(f):
    if REACT0 + 4 <= f < REACT1 - 3: return ricky_face()
    return doug_face() + V(0.4 * math.sin(f / 23), -1.0, 0.1 * math.sin(f / 17))
SAC = {}
def saccade(who, f):
    k = (who, f // _rng.choice([8, 11, 14]) if False else f // 10)
    if k not in SAC: SAC[k] = V(_rng.uniform(-0.05, 0.05), 0, _rng.uniform(-0.035, 0.035))
    return SAC[k]
def aim(pivot, T, clamp_yaw=40, clamp_pitch=26):
    P = pivot.matrix_world.translation; Rp = pivot.parent.matrix_world.to_3x3().normalized()
    d = Rp.inverted() @ (T - P)
    yaw = math.degrees(math.atan2(d.x, -d.y)); pitch_ = -math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    yaw = max(-clamp_yaw, min(clamp_yaw, yaw)); pitch_ = max(-clamp_pitch, min(clamp_pitch, pitch_))
    pivot.rotation_euler = (D(pitch_), 0, D(yaw)); pivot.keyframe_insert('rotation_euler', frame=scene.frame_current)
D_LIDS = [o for o in bpy.data.objects if o.name.startswith('doug_lid')]
R_LIDS = [o for o in bpy.data.objects if o.name.startswith('ricky_lid')]
def lids_set(objs, f, deg):
    for o in objs: o.rotation_euler = (D(deg), 0, 0); o.keyframe_insert('rotation_euler', frame=f)
def brows_set(C, z0, f, dzL, dzR, tL, tR):
    for i, bp in enumerate(C['brows']):
        sx = -1 if i == 0 else 1
        bp.location = (bp.location.x, bp.location.y, z0[i] + (dzL if i == 0 else dzR)); bp.keyframe_insert('location', frame=f)
        bp.rotation_euler = (0, sx * D(tL if i == 0 else tR), 0); bp.keyframe_insert('rotation_euler', frame=f)
def beat_pulse(f): return max(0.0, math.cos(2 * math.pi * ((f - 1) % BEAT) / BEAT)) ** 4
def doug_mouth(f, open_):
    m = doug['mouth']; m.scale = (1 + 2.4 * open_, 1, 1 + 0.2 * open_); m.keyframe_insert('scale', frame=f)
def ricky_mouth(f, open_, wide):
    m = ricky['mouth']; m.scale = (1.3 * (1 + 0.25 * open_ + 0.5 * wide), 0.5, 0.5 * (1 + 2.3 * open_) * (1 - 0.35 * wide)); m.keyframe_insert('scale', frame=f)
SING = {}
def sing_open(f):
    k = f // 5
    if k not in SING: SING[k] = _rng.choice([0.0, 0.15, 0.3, 0.45, 0.2])
    return SING[k]
def face_pass(f):
    # ---- Ricky
    lb, dzL, dzR, tL, tR, wide = ease_tab(R_EMO, f)
    sp = speech('ricky', f)
    lids_set(R_LIDS, f, max(lb, -12) + (95 - lb) * blink_amt(f, R_BLINKS) - 10 * sp)
    brows_set(ricky, RBZ, f, dzL + 0.012 * sp, dzR + 0.012 * sp, tL, tR)
    for pv in ricky['eyes']: aim(pv, r_target(f) + saccade('r', f))
    ricky_mouth(f, sp, 0.0 if sp > 0.05 else wide)
    ricky_smile.hide_render = not (40 <= f < LINES['g1'] + 6); ricky_smile.keyframe_insert('hide_render', frame=f)
    ricky['mouth'].hide_render = not ricky_smile.hide_render and True; ricky['mouth'].keyframe_insert('hide_render', frame=f)
    # ---- Doug
    lb, dzL, dzR, tL, tR = ease_tab(D_EMO, f)
    reacting = REACT0 + 4 <= f < REACT1 - 3
    dsp = speech('doug', f)
    pulse = 0.0 if reacting else beat_pulse(f)
    lids_set(D_LIDS, f, lb + (95 - lb) * blink_amt(f, D_BLINKS) + (5 * pulse if lb > 60 else 0))
    brows_set(doug, DBZ, f, dzL + 0.012 * pulse, dzR + 0.012 * pulse, tL, tR)
    for pv in doug['eyes']: aim(pv, d_target(f) + saccade('d', f))
    if reacting or f < 61: doug_mouth(f, dsp)
    else: doug_mouth(f, sing_open(f) * (0.5 if SLOW0 <= f <= SLOW1 else 1.0))

