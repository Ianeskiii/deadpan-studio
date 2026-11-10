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
B_EMO = [(1, (-26, 0.012, 0.012, -8, -8)),
         (F_AWE, (-36, 0.03, 0.03, -12, -12)),                    # bright "Awesome!"
         (F_Q + 20, (-32, 0.022, 0.022, -10, -10)),
         (F_DOUG + 14, (-30, 0.02, 0.02, -8, -8)),
         (F_DOUG + 20, (-20, -0.008, 0.045, 8, -12)),             # ...pause: one brow up, slight squint
         (F_B2 + 8, (-30, 0.015, 0.035, -4, -10)),
         (LET[0], (-10, 0.008, 0.008, -6, -6)),                   # concentrating on writing
         (LET[3] + 12, (-10, 0.008, 0.008, -6, -6)),
         (F_PERF + 4, (-40, 0.035, 0.035, -14, -14)),              # beaming, totally sure
         (F_M0 + 6, (-26, 0.012, 0.012, -6, -6)),
         (F_CALL, (-38, 0.04, 0.04, -14, -14)),                    # projecting the call
         (F_DOG + 10, (-36, 0.035, 0.035, -14, -14)),             # proud
         (F_D3, (-30, 0.025, 0.025, -10, -10)),
         (F_YEAH - 2, (-32, 0.04, 0.04, -12, -12)),               # innocent "Yeah?"
         (F_YEAH + 14, (-36, 0.035, 0.035, -14, -14)),
         (F_BYE, (-40, 0.04, 0.04, -14, -14)), (N, (-34, 0.03, 0.03, -12, -12))]
D_EMO = [(1, (22, 0.01, 0.01, -4, -4)),
         (T['b2']['fe'], (22, 0.01, 0.01, -4, -4)),
         (T['b2']['fe'] + 8, (26, 0.0, 0.0, 0, 0)),              # holds the look: flat
         (LET[0], (24, 0.005, 0.005, -2, -2)),
         (F_ASIDE1, (22, 0.01, 0.01, -4, -4)),
         (F_DOG, (18, 0.012, 0.012, -4, -4)),
         (F_TURN1, (28, 0.0, 0.0, -6, -6)),                      # the realisation, eyelids settle
         (F_BACK1 + 6, (32, 0.0, 0.0, -10, -10)),                # disappointed: inner brows up
         (F_D3E, (33, -0.003, -0.003, -10, -10)),
         (F_TAKE, (35, -0.005, -0.005, -8, -8)),                 # the stare
         (F_GO0 + 6, (26, 0.0, 0.0, -6, -6)),
         (F_STOP + 2, (28, 0.0, 0.0, -10, -10)),
         (F_STOP + 6, (90, 0.0, 0.0, -14, -14)),                 # eyes shut, silent disappointment
         (F_GO1 - 4, (90, 0.0, 0.0, -14, -14)),
         (F_GO1 + 2, (28, 0.0, 0.0, -8, -8)), (N, (28, 0.0, 0.0, -8, -8))]
B_BLINKS = [(18, 3), (64, 3), (F_DOUG + 17, 3), (F_DOUG + 23, 3), (176, 3), (F_PERF - 3, 3), (F_M1 + 2, 3), (F_CALL - 5, 3),
            (F_DOG + 18, 3), (F_BACK1 + 2, 3), (F_D3E + 6, 3), (F_YEAH + 12, 3), (F_BYE - 6, 3), (F_B6E + 12, 3)]
D_BLINKS = [(52, 3), (F_DOUG - 10, 3), (T['b2']['fe'] + 10, 6), (F_PERF + 10, 3), (F_ASIDE1 + 6, 3), (F_DOG - 12, 3),
            (F_TURN0 + 2, 5), (F_BACK1 + 10, 4), (F_D3E + 4, 3), (F_GO0 + 4, 3)]
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
    if F_AWE <= f < F_AWE + 12: return V(0.2, 0.6, CT + 0.15)                       # grabbing a cup
    if LET[0] - 2 <= f < LET[3] + 20:
        return doug_face() if any(c - 1 <= f < c + 5 for c in LET[1:]) else cup_pt() # writing, quick glances up at each letter
    if F_M0 + 4 <= f < F_M2 + 2: return V(1.7, 0.33, CT + 0.25)                     # the machine
    if F_CALL <= f < F_DOG + 6: return V(-1.6 + 0.4 * math.sin(f / 9), -2.5, 1.3)   # calling out to the whole shop
    if SHOTS['D'][0] - 2 <= f <= SHOTS['D'][1]: return cam_pos(f)                    # presents the cup proudly to the room
    if F_YEAH - 6 <= f < F_YEAH + 2: return cup_pt()                                 # "Yeah?" - looks at the cup... sees nothing wrong
    return doug_face()
def d_target(f):
    if f < 30: return bari_face() + V(0, 0, 0.1)
    if F_ASIDE0 <= f < F_ASIDE1: return ahead(doug_r)
    if F_ASIDE1 <= f < F_DOG:                                                        # idly reading the menu board
        return V(0.2 + 0.6 * math.sin(f / 31), 2.6, 2.45) if (f - F_ASIDE1) % 40 < 26 else ahead(doug_r)
    if F_DOG <= f < F_TURN0: return ahead(doug_r)                                    # freeze
    if F_TURN0 <= f < F_TURN1: return bari_face() if f > F_TURN0 + 4 else ahead(doug_r)   # eyes lead the head
    if F_BACK0 <= f < F_BACK1 + 6: return cup_pt()
    if F_BACK1 + 6 <= f < F_BACK1 + 11: return bari_face()                           # barista...
    if F_BACK1 + 11 <= f < F_D3 - 2: return cup_pt()                                 # ...cup...
    if F_D3 + 20 <= f < F_D3 + 30: return cup_pt()                                   # glance at it on "spelled it"
    if F_TAKE - 7 <= f < F_TAKE + 4: return cup_pt()
    if f >= F_GO0 - 4: return ahead(doug_r, 2.5, -0.15)
    return bari_face()
SAC = {}
def saccade(who, f):
    k = (who, f // 9)
    if k not in SAC: SAC[k] = V(_rng.uniform(-0.035, 0.035), 0, _rng.uniform(-0.025, 0.025))
    return SAC[k]
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
    smiling = B_QUIET[0] > 3 and not (F_DOUG + 18 <= f < F_B2)           # closed smile when not talking (not while confused)
    bari_mouth(f, o, w)
    bari_smile.hide_render = not smiling; bari_smile.keyframe_insert('hide_render', frame=f)
    bari['mouth'].hide_render = smiling; bari['mouth'].keyframe_insert('hide_render', frame=f)
    # ---- Doug
    lb, dzL, dzR, tL, tR = ease_tab(D_EMO, f)
    o, w = mtrack('doug', f)
    lids_set(D_LIDS, f, lb + (95 - lb) * blink_amt(f, D_BLINKS))
    brows_set(doug, DDBZ, f, dzL + 0.008 * o, dzR + 0.008 * o, tL, tR)
    for pv in doug['eyes']: aim(pv, d_target(f) + saccade('d', f))
    doug_mouth(f, o, w)
