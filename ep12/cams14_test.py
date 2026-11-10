# ============================================================ CAMERAS v3: same opening + montage; ending = two-shot -> Doug's OTS on the cup -> Doug close -> two-shot
SHOTS = {'A': (1, 180), 'B': (181, 300), 'C': (301, F_TOMACH1), 'D': SH_D, 'E': (SH_D[1] + 1, F_CALL - 1),
         'F': (F_CALL, SH_G[0] - 1), 'G': SH_G, 'H': (SH_G[1] + 1, F_D3E + 8), 'I': (F_D3E + 9, N)}
def doug_face_pt(): return doug_r.upper.matrix_world @ V(0, -0.1, D_EZ - 0.08)
# over Doug's shoulder at the cup in her hand (exactly his eyeline)
scene.frame_set((SH_G[0] + SH_G[1]) // 2)
_cupG = wp(bari_r.hand['P']) + bari_r.root.matrix_world.to_3x3().normalized() @ V(0, -0.055, 0) + V(0, 0, 0.012)
_R = doug_r.upper.matrix_world.to_3x3().normalized()
_dhead = doug_r.upper.matrix_world @ V(0, 0, D_EZ)
_camG = _dhead + _R @ V(0.62, 0.55, 0.12)              # behind and over his right shoulder
lerp_t = lambda a, b: (lambda t: a.lerp(b, t))
SPEC = {
    'A': (V(-0.02, -2.8, 1.38), V(-0.02, -2.6, 1.37), lerp_t(V(-0.02, 0.1, 1.2), V(-0.02, 0.1, 1.2)), 22, 4.0, None),
    'B': (V(0.12, -1.85, 1.48), V(0.1, -1.77, 1.47), lerp_t(V(-0.78, 0.05, 1.3), V(-0.78, 0.05, 1.3)), 30, 2.8, None),
    'C': (V(-0.02, -2.75, 1.38), V(-0.14, -3.25, 1.38), lerp_t(V(-0.02, 0.1, 1.2), V(-0.1, -0.3, 1.18)), 22, 4.0, None),
    'D': (V(1.62, -0.52, 1.17), V(1.62, -0.46, 1.16), lerp_t(CUP_TRAY + V(0, 0, 0.07), CUP_TRAY + V(0, 0, 0.06)), 40, 2.8, None),
    'E': (V(0.38, -1.64, 1.45), V(0.34, -1.56, 1.45), lerp_t(V(-0.8, PICK_Y, 1.26), V(-0.8, PICK_Y, 1.26)), 30, 2.8, None),
    'F': (V(-0.02, -3.45, 1.38), V(-0.02, -3.36, 1.38), lerp_t(V(-0.02, PICK_Y + 0.1, 1.2), V(-0.02, PICK_Y + 0.1, 1.2)), 22, 4.0, None),
    'G': (_camG, _camG + (_cupG - _camG).normalized() * 0.12, lerp_t(_cupG + V(0, 0, 0.0), _cupG + V(0, 0, 0.0)), 50, 2.4, None),
    'H': (V(0.36, -1.6, 1.45), V(0.3, -1.5, 1.45), lerp_t(V(-0.8, PICK_Y, 1.28), V(-0.8, PICK_Y, 1.28)), 32, 2.8, None),
    'I': (V(-0.02, -3.3, 1.38), V(-0.02, -3.05, 1.37), lerp_t(V(-0.02, PICK_Y + 0.1, 1.18), V(-0.04, PICK_Y + 0.05, 1.2)), 22, 4.0, F_DISAPP1),
}
SH_G = SHOTS['G']
def shot_of(f):
    for k, (a_, b_) in SHOTS.items():
        if a_ <= f <= b_: return k
    return 'I'
def shot_t(k, f):
    a_, b_ = SHOTS[k]; e_ = SPEC[k][5] or b_
    return smooth(min(1.0, max(0.0, (f - a_) / max(1, e_ - a_))))
def cam_pos(f):
    k = shot_of(f); return SPEC[k][0].lerp(SPEC[k][1], shot_t(k, f))
def shake(f, amp):
    return V(amp * (math.sin(f * 0.37) + 0.5 * math.sin(f * 0.91 + 1.3)), amp * 0.6 * math.sin(f * 0.53 + 2.1),
             amp * (math.sin(f * 0.29 + 0.5) + 0.4 * math.sin(f * 1.13)))
def cam_setup(name, amp=0.003):
    fa, fb = SHOTS[name]; p0, p1, tgt, lens, fstop, _ = SPEC[name]
    for f in range(fa, fb + 1):
        scene.frame_set(f); t = shot_t(name, f)
        key(cam, 'location', f, cam_pos(f) + shake(f, amp if name not in ('D', 'G') else amp * 0.5))
        tp = tgt(t); key(target, 'location', f, tp + shake(f + 40, amp * 0.6))
        fp = {'B': doug_face_pt(), 'E': doug_face_pt(), 'H': doug_face_pt(), 'G': _cupG, 'D': CUP_TRAY + V(0, 0, 0.05)}.get(name, tp)
        key(focus, 'location', f, fp)
        key(cam_data, 'lens', f, lens); key(cam_data.dof, 'aperture_fstop', f, fstop)
