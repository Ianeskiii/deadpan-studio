# ============================================================ CAMERAS: 6 shots, one side of the counter
FA = 178; FB = 262; FC = F_TURN1; FD = F_BACK1 - 1; FE = F_GO0 + 4
SHOTS = {'A': (1, FA), 'B': (FA + 1, FB), 'C': (FB + 1, FC), 'D': (FC + 1, FD), 'E': (FD + 1, FE), 'F': (FE + 1, N)}
def doug_face_pt(): return doug_r.upper.matrix_world @ V(0, -0.1, D_EZ - 0.08)
scene.frame_set(FC + 10)
_cupD = wp(bari_r.hand['P']) + bari_r.root.matrix_world.to_3x3().normalized() @ V(0, -0.055, 0) + V(0, 0, 0.04)
_bfD = bari_r.upper.matrix_world @ V(0, -0.2, B_EZ - 0.1)
_tD = _cupD.lerp(_bfD, 0.42)
SPEC = {
    'A': (V(-0.02, -2.8, 1.38), V(-0.02, -2.55, 1.37), lambda f: V(-0.02, 0.1, 1.2), 22, 4.0),
    'B': (V(0.12, -1.85, 1.48), V(0.1, -1.75, 1.47), lambda f: V(-0.78, 0.05, 1.3), 30, 2.8),
    'C': (V(-0.22, -3.2, 1.4), V(-0.22, -3.05, 1.39), lambda f: V(-0.22, 0.05, 1.18), 22, 4.0),
    'D': (_tD + V(-0.38, -0.86, 0.03), _tD + V(-0.34, -0.78, 0.02), lambda f: _tD, 38, 3.5),
    'E': (V(-0.15, -2.6, 1.42), V(-0.13, -2.45, 1.41), lambda f: V(-0.08, 0.05, 1.2), 22, 3.5),
    'F': (V(-2.95, -2.6, 1.38), V(-2.9, -2.52, 1.38), None, 24, 3.2),
}
def shot_of(f):
    for k, (a_, b_) in SHOTS.items():
        if a_ <= f <= b_: return k
    return 'F'
def cam_pos(f):
    k = shot_of(f); a_, b_ = SHOTS[k]; p0, p1 = SPEC[k][0], SPEC[k][1]
    return p0.lerp(p1, smooth((f - a_) / max(1, b_ - a_)))
def shake(f, amp):
    return V(amp * (math.sin(f * 0.37) + 0.5 * math.sin(f * 0.91 + 1.3)), amp * 0.6 * math.sin(f * 0.53 + 2.1),
             amp * (math.sin(f * 0.29 + 0.5) + 0.4 * math.sin(f * 1.13)))
def cam_setup(name, amp=0.004):
    fa, fb = SHOTS[name]; p0, p1, tgt, lens, fstop = SPEC[name]
    for f in range(fa, fb + 1):
        scene.frame_set(f)
        key(cam, 'location', f, cam_pos(f) + shake(f, amp))
        if tgt is None:   # F: follow Doug's face, softened
            tp = doug_face_pt() + V(0.25, 0.25, 0.0)
        else:
            tp = tgt(f)
        key(target, 'location', f, tp + shake(f + 40, amp * 0.6))
        fp = doug_face_pt() if name in ('B', 'F') else (_cupD if name == 'D' else tp)
        key(focus, 'location', f, fp)
        key(cam_data, 'lens', f, lens); key(cam_data.dof, 'aperture_fstop', f, fstop)
