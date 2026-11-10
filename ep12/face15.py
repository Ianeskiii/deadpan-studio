# ============================================================ FACE PASS (per frame): gaze + saccades, blinks, lids, brows, audio-driven mouth
import soundfile as _sf
_rng = random.Random(12)
def _mouth_tracks():
    """per frame: open (loudness) and wide (bright 'ee' vs round 'oo', from spectral centroid), attack fast / release slower"""
    tr = {'doug': {}, 'bari': {}}
    for name, v in T.items():
        if not isinstance(v, dict): continue
        a, sr = _sf.read(os.path.join(VO, name + '.wav')); hop = sr // 30
        who = 'doug' if name.startswith('d') else 'bari'
        rms, cen = [], []
        for i in range(0, len(a) - hop, hop):
            seg = a[i:i + 2 * hop] * np.hanning(len(a[i:i + 2 * hop]))
            S = np.abs(np.fft.rfft(seg)); fr_ = np.fft.rfftfreq(len(seg), 1 / sr)
            rms.append(np.sqrt(np.mean(a[i:i + hop] ** 2))); band = (fr_ > 300) & (fr_ < 4000)
            cen.append(float((S[band] * fr_[band]).sum() / (S[band].sum() + 1e-9)))
        rms = np.array(rms) / (max(rms) + 1e-9); o_prev = 0.0
        for i, (r_, c_) in enumerate(zip(rms, cen)):
            o = max(0.0, min(1.0, (r_ - 0.06) / 0.5))
            o = o if o > o_prev else o_prev * 0.55 + o * 0.45; o_prev = o
            w = max(0.0, min(1.0, (c_ - 1100) / 1300)) if o > 0.08 else 0.5
            tr[who][v['f'] + i] = (o, w)
    return tr
MTR = _mouth_tracks()
def mtrack(who, f): return MTR[who].get(f, (0.0, 0.5))
def ease_tab(keys, f):
    if f <= keys[0][0]: return keys[0][1]
    if f >= keys[-1][0]: return keys[-1][1]
    for (fa, va), (fb, vb) in zip(keys, keys[1:]):
        if fa <= f <= fb:
            t = smooth((f - fa) / max(1, fb - fa)); return tuple(x + (y - x) * t for x, y in zip(va, vb))
# (lid_base, browL_dz, browR_dz, browL_tilt, browR_tilt)   tilt>0 = cross, tilt<0 = inner brows up
# barista: friendly, casual, confidently clueless (kept modest - no big mugging)
B_EMO = [(1, (-30, 0.01, 0.01, -6, -6)),
         (F_B1, (-34, 0.018, 0.018, -8, -8)),
         (F_D1E + 4, (-32, 0.015, 0.015, -6, -6)),
         (F_D1E + 12, (-24, -0.004, 0.03, 5, -8)),                 # hm? - one brow up, slight squint
         (F_B2 + 10, (-30, 0.012, 0.025, -2, -8)),
         (LET[0], (-32, 0.015, 0.015, -6, -6)),                    # listening, eye contact
         (F_D2E + 6, (-34, 0.018, 0.018, -8, -8)),
         (F_B3 + 4, (-38, 0.026, 0.026, -10, -10)),                # sure of herself
         (F_WRITE0 + 4, (-16, 0.006, 0.006, -4, -4)),               # looking down, writing
         (F_WRITE1, (-16, 0.006, 0.006, -4, -4)),
         (SH_D[0], (-22, 0.008, 0.008, -4, -4)),
         (F_CALL, (-34, 0.022, 0.022, -8, -8)),                    # friendly, casual announcement
         (F_FOR + 4, (-24, 0.015, 0.015, -6, -6)),                 # glancing down at the name
         (F_DOG, (-34, 0.025, 0.025, -9, -9)),
         (F_SET + 8, (-32, 0.02, 0.02, -8, -8)),
         (F_SMILE0, (-32, 0.02, 0.02, -8, -8)),
         (F_SMILE1, (-22, 0.034, 0.034, -12, -12)),                # smile reaches her eyes (cheeks push the lids up)
         (F_GO0, (-24, 0.03, 0.03, -11, -11)), (N, (-24, 0.03, 0.03, -11, -11))]
D_EMO = [(1, (22, 0.01, 0.01, -4, -4)),
         (F_B2E, (22, 0.01, 0.01, -4, -4)),
         (F_B2E + 8, (25, 0.0, 0.0, 0, 0)),                      # takes a beat
         (LET[0], (22, 0.006, 0.006, -2, -2)),
         (F_WAIT0, (23, 0.01, 0.01, -4, -4)),
         (F_DOG, (21, 0.01, 0.01, -4, -4)),
         (F_NOTICE1, (22, 0.008, 0.008, -4, -4)),
         (F_NOTICE1 + 8, (18, 0.0, 0.02, 2, -7)),                # disbelief: lids lift a touch, one brow up
         (F_EYES0, (18, 0.0, 0.02, 2, -7)),
         (F_HEAD1 + 2, (28, -0.004, -0.004, 3, 3)),              # calm, unimpressed
         (F_LG0, (29, -0.005, -0.005, 3, 3)),                    # the stare
         (F_LG1, (31, -0.004, -0.004, -6, -6)),
         (F_GIVEUP1, (36, -0.003, -0.003, -13, -13)),            # silently gives up: lids sink, inner brows up
         (F_TURN1, (30, 0.0, 0.0, -8, -8)), (N, (30, 0.0, 0.0, -8, -8))]
B_BLINKS = [(20, 3), (F_GRAB + 12, 3), (F_D1E + 6, 3), (F_D1E + 11, 3), (LET[1] + 6, 3), (F_D2E + 12, 3), (F_WRITE1 + 2, 3),
            (SH_D[1] - 4, 3), (F_CALL - 6, 3), (F_SET + 4, 3), (F_GO0 + 14, 3), (F_GO0 + 40, 3)]
D_BLINKS = [(46, 3), (F_D1 - 12, 3), (F_B2E + 12, 5), (LET[2] - 6, 3), (F_STEP1 + 3, 3), (SH_D[1] + 14, 3),
            (F_LG1 + 4, 6), (F_TURN0 + 2, 3)]
def blink_amt(f, blinks):
    for b, dur in blinks:
        if abs(f - b) <= dur: return 1 - abs(f - b) / (dur + 1)
    return 0.0
def doug_face(): return doug_r.upper.matrix_world @ V(0, -0.25, D_EZ - 0.05)
def bari_face(): return bari_r.upper.matrix_world @ V(0, -0.25, B_EZ - 0.05)
def cup_pt(): return cup.matrix_world.translation.copy() + V(0, 0, 0.03)
def ahead(rig, dist=2.0, dz=0.0):
    return rig.upper.matrix_world @ V(0, -dist, (D_EZ if rig is doug_r else B_EZ) + dz)
def b_target(f):
    if F_GRAB - 4 <= f < F_GRAB + 10: return V(0.2, 0.3, CT + 0.1)                     # picks up cup + marker
    if F_WRITE0 <= f < F_WRITE1: return cup_pt()                                        # writing
    if F_TOMACH0 <= f <= SH_D[1]: return CUP_TRAY + V(0, 0, 0.1)                         # machine
    if F_TOPICK0 < f < F_TOPICK1 - 4: return ahead(bari_r, 2.0, -0.2)
    if F_FOR + 1 <= f < F_DOG - 2: return cup_pt()                                      # reads the name off the cup
    return doug_face()
def d_target(f):
    if f < 30: return bari_face() + V(0, 0, 0.1)
    if F_B3E + 2 <= f < F_STEP0 + 2: return cup_pt()                                    # glance at the cup as she starts writing
    if F_STEP0 + 2 <= f < F_WAIT0: return ahead(doug_r)
    if F_WAIT0 <= f < F_CALL:                                                           # waiting: menu board, room, blank stare
        k = (f - F_WAIT0)
        if k < 14: return V(0.4, 2.6, 2.45)
        if k < 34: return ahead(doug_r, 3.0, 0.2) + V(-1.2, 0, 0)
        return ahead(doug_r, 2.5, -0.05)
    if F_CALL <= f < F_NOTICE0: return ahead(doug_r, 2.5, -0.05)                       # blank stare until he hears it
    if F_NOTICE0 <= f < F_EYES0: return cup_pt()                                        # eyes straight to the name
    if F_EYES0 <= f < F_EYES1: return cup_pt().lerp(bari_face(), smooth((f - F_EYES0) / (F_EYES1 - F_EYES0)))   # slowly up to her
    if F_EYES1 <= f < F_LG0: return bari_face()                                         # eye contact, her smile, the stare
    if F_LG0 <= f < F_LG1: return bari_face().lerp(cup_pt(), smooth((f - F_LG0) / (F_LG1 - F_LG0)))   # slowly back down
    if F_LG1 <= f < F_LIFT1: return cup_pt()
    if f >= F_LIFT1: return ahead(doug_r, 2.5, -0.15)
    return bari_face()
SAC = {}
def saccade(who, f):
    k = (who, f // 9)
    if k not in SAC: SAC[k] = V(_rng.uniform(-0.035, 0.035), 0, _rng.uniform(-0.025, 0.025))
    return SAC[k] * (0.25 if (who == 'd' and f >= F_CALL) or (who == 'b' and f >= SH4[0]) else 1.0)   # steady, deliberate eyes in the ending
def aim(pivot, Tp, clamp_yaw=40, clamp_pitch=28):
    P = pivot.matrix_world.translation; Rp = pivot.parent.matrix_world.to_3x3().normalized()
    d = Rp.inverted() @ (Tp - P)
    yaw = math.degrees(math.atan2(d.x, -d.y)); pitch_ = -math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    yaw = max(-clamp_yaw, min(clamp_yaw, yaw)); pitch_ = max(-clamp_pitch, min(clamp_pitch, pitch_))
    pivot.rotation_euler = (D(pitch_), 0, D(yaw)); pivot.keyframe_insert('rotation_euler', frame=scene.frame_current)
D_LIDS = [o for o in bpy.data.objects if o.name.startswith('doug_lid')]
B_LIDS = [o for o in bpy.data.objects if o.name.startswith('bari_lid')]
def lids_set(objs, f, deg):
    for o in objs: o.rotation_euler = (D(deg), 0, 0); o.keyframe_insert('rotation_euler', frame=f)
def brows_set(C, z0, f, dzL, dzR, tL, tR):
    for i, bp in enumerate(C['brows']):
        sx = -1 if i == 0 else 1
        bp.location = (bp.location.x, bp.location.y, z0[i] + (dzL if i == 0 else dzR)); bp.keyframe_insert('location', frame=f)
        bp.rotation_euler = (0, sx * D(tL if i == 0 else tR), 0); bp.keyframe_insert('rotation_euler', frame=f)
def doug_mouth(f, o, w):
    m = doug['mouth']   # capsule lies along x: scale.x = height (open), scale.z = width
    m.scale = (1 + 2.3 * o, 1, (1 + 0.15 * o) * (0.82 + 0.36 * w)); m.keyframe_insert('scale', frame=f)
def bari_mouth(f, o, w):
    m = bari['mouth']; m.scale = (1.3 * (1 + 0.2 * o) * (0.8 + 0.45 * w), 0.5, 0.5 * (1 + 2.3 * o) * (1.1 - 0.3 * w)); m.keyframe_insert('scale', frame=f)
B_QUIET = [0]
def face_pass(f):
    # ---- barista
    lb, dzL, dzR, tL, tR = ease_tab(B_EMO, f)
    o, w = mtrack('bari', f)
    lids_set(B_LIDS, f, lb + (95 - lb) * blink_amt(f, B_BLINKS) - 6 * o)
    brows_set(bari, BBZ, f, dzL + 0.01 * o, dzR + 0.01 * o, tL, tR)
    for pv in bari['eyes']: aim(pv, b_target(f) + saccade('b', f))
    B_QUIET[0] = B_QUIET[0] + 1 if o < 0.04 else 0
    smiling = B_QUIET[0] > 3 and not (F_D1E + 10 <= f < F_B2)           # closed smile when not talking (not while confused)
    bari_mouth(f, o, w)
    bari_smile.hide_render = not smiling; bari_smile.keyframe_insert('hide_render', frame=f)
    sm = 1.0 if f < F_B4E else (0.3 + 0.7 * smooth(min(1, max(0, (f - F_SMILE0) / (F_SMILE1 - F_SMILE0)))))
    bse.scale = (0.86 + 0.18 * sm, 1, 0.12 + 0.95 * sm); bse.keyframe_insert('scale', frame=f)
    bari['mouth'].hide_render = smiling; bari['mouth'].keyframe_insert('hide_render', frame=f)
    # ---- Doug
    lb, dzL, dzR, tL, tR = ease_tab(D_EMO, f)
    o, w = mtrack('doug', f)
    lids_set(D_LIDS, f, lb + (95 - lb) * blink_amt(f, D_BLINKS))
    brows_set(doug, DDBZ, f, dzL + 0.008 * o, dzR + 0.008 * o, tL, tR)
    for pv in doug['eyes']: aim(pv, d_target(f) + saccade('d', f))
    doug_mouth(f, o, w)
