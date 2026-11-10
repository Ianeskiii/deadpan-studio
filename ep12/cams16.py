# ============================================================ CAMERAS v4: opening + montage unchanged; ending = OTS -> Doug -> her -> Doug -> his view -> wide
SHOTS = {'A': (1, 180), 'B': (181, 300), 'C': (301, F_TOMACH1), 'D': SH_D, 'E': (SH_D[1] + 1, F_CALL - 1),
         'F': SH1, 'FC': SHC, 'G': SH2, 'H': SH4, 'I': SH5, 'J': SH7, 'K': SH8}
def doug_face_pt(): return doug_r.upper.matrix_world @ V(0, -0.1, D_EZ - 0.08)
def _eye(f): scene.frame_set(f); return doug_r.upper.matrix_world @ V(0, -0.27, D_EZ)
def _bface(f): scene.frame_set(f); return bari_r.upper.matrix_world @ V(0, -0.22, B_EZ - 0.08)
# F: over Doug's shoulder (from behind him, his far side) at her and the cup she is holding
scene.frame_set(SH1[0] + 20)
_Rd = doug_r.upper.matrix_world.to_3x3().normalized()
_camF = _eye(SH1[0] + 20) + V(0.18, -0.4, 0.04)          # beside his head, camera side: her, the cup, the edge of him
_cupF = wp(bari_r.hand['P']) + bari_r.root.matrix_world.to_3x3().normalized() @ V(0, -0.055, 0)
_tF = _cupF.lerp(_bface(SH1[0] + 20), 0.45)
# H: her close-up, from just beside Doug's eyeline (she is looking at him = almost into the lens)
_mH = (SH4[0] + SH4[1]) // 2
_eH, _bH = _eye(_mH), _bface(_mH)
_camH = _eH + (_bH - _eH) * 0.12 + V(0.0, -0.06, 0.0)
# J: Doug's view down at the cup on the counter; his hand comes in and takes it
_eJ = _eye(SH7[0]); _cJ = CUP_PICK + V(0, 0, 0.02)
_camJ = _eJ + (_cJ - _eJ).normalized() * 0.12
# FC: the cup on the counter, from Doug's side at cup height so the name faces the lens
_eC = _eye(SHC[0]); _hz = (_eC - CUP_PICK); _hz.z = 0; _hz.normalize()
_camC0 = CUP_PICK + _hz * 0.46 + V(0, 0, 0.07)
lerp_t = lambda a, b: (lambda t: a.lerp(b, t))
DCU0, DCU1 = V(0.36, -1.6, 1.45), V(0.3, -1.5, 1.45)
SPEC = {
    'A': (V(-0.02, -2.8, 1.38), V(-0.02, -2.6, 1.37), lerp_t(V(-0.02, 0.1, 1.2), V(-0.02, 0.1, 1.2)), 22, 4.0, None),
    'B': (V(0.12, -1.85, 1.48), V(0.1, -1.77, 1.47), lerp_t(V(-0.78, 0.05, 1.3), V(-0.78, 0.05, 1.3)), 30, 2.8, None),
    'C': (V(-0.02, -2.75, 1.38), V(-0.14, -3.25, 1.38), lerp_t(V(-0.02, 0.1, 1.2), V(-0.1, -0.3, 1.18)), 22, 4.0, None),
    'D': (V(1.62, -0.52, 1.17), V(1.62, -0.46, 1.16), lerp_t(CUP_TRAY + V(0, 0, 0.07), CUP_TRAY + V(0, 0, 0.06)), 40, 2.8, None),
    'E': (V(0.38, -1.64, 1.45), V(0.34, -1.56, 1.45), lerp_t(V(-0.8, PICK_Y, 1.26), V(-0.8, PICK_Y, 1.26)), 30, 2.8, None),
    'F': (_camF, _camF + (_tF - _camF).normalized() * 0.05, lerp_t(_tF, _tF), 32, 4.0, None),
    'FC': (_camC0, _camC0 - _hz * 0.04, lerp_t(CUP_PICK + V(0, 0, 0.015), CUP_PICK + V(0, 0, 0.015)), 50, 3.5, None),
    'G': (DCU0, DCU0.lerp(DCU1, 0.4), lerp_t(V(-0.8, PICK_Y, 1.28), V(-0.8, PICK_Y, 1.28)), 32, 2.8, None),
    'H': (_camH, _camH + (_bH - _camH).normalized() * 0.03, lerp_t(_bH + V(0, 0, -0.04), _bH + V(0, 0, -0.04)), 45, 2.8, None),
    'I': (DCU0.lerp(DCU1, 0.4), DCU1, lerp_t(V(-0.8, PICK_Y, 1.28), V(-0.8, PICK_Y, 1.27)), 32, 2.8, None),
    'J': (_camJ, _camJ, lerp_t(_cJ, _cJ), 30, 4.0, None),
    'K': (V(-0.3, -3.25, 1.36), V(-0.36, -3.3, 1.36), lerp_t(V(-0.3, PICK_Y - 0.05, 1.15), V(-0.38, PICK_Y - 0.1, 1.15)), 19, 4.0, None),
}
def shot_of(f):
    for k, (a_, b_) in SHOTS.items():
        if a_ <= f <= b_: return k
    return 'K'
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
        a_ = amp * (0.4 if name in ('D', 'H', 'J', 'FC') else 1.0)
        key(cam, 'location', f, cam_pos(f) + shake(f, a_))
        tp = tgt(t); key(target, 'location', f, tp + shake(f + 40, a_ * 0.6))
        fp = {'B': doug_face_pt(), 'E': doug_face_pt(), 'G': doug_face_pt(), 'I': doug_face_pt(), 'D': CUP_TRAY + V(0, 0, 0.05),
              'F': tp, 'J': _cJ, 'FC': CUP_PICK + V(0, 0, 0.015)}.get(name, tp)
        key(focus, 'location', f, fp)
        key(cam_data, 'lens', f, lens); key(cam_data.dof, 'aperture_fstop', f, fstop)
