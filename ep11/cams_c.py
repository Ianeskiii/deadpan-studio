# ============================================================ CAMERAS (v3: 14 angles, handheld feel)
SHOTS = {
    'C1': (1, 45), 'C2': (46, 75), 'C3': (76, 90), 'C4': (91, 102), 'C5': (103, 150), 'C6': (151, 189),
    'C7': (190, 231), 'C8': (232, 273), 'C9': (274, 306), 'C10': (307, 339), 'C11': (340, 363),
    'C12': (364, 405), 'C13': (406, 450), 'C14': (451, 480)}
f0, f1 = SHOTS[SHOT]
def shake(f, amp):
    return V(amp * (math.sin(f * 0.37) + 0.5 * math.sin(f * 0.91 + 1.3)),
             amp * 0.6 * math.sin(f * 0.53 + 2.1),
             amp * (math.sin(f * 0.29 + 0.5) + 0.4 * math.sin(f * 1.13)))
def shoot(p0, p1, tgt, lens, fstop, amp=0.012, focus_fn=None):
    """camera moves p0->p1 with handheld shake; tgt: Vector or callable(f)->Vector"""
    cam_data.lens = lens; cam_data.dof.aperture_fstop = fstop
    for f in range(f0, f1 + 1, 2):
        t = (f - f0) / max(1, f1 - f0)
        key(cam, 'location', f, p0.lerp(p1, smooth(t)) + shake(f, amp))
        scene.frame_set(f)
        tp = tgt(f) if callable(tgt) else tgt
        key(target, 'location', f, tp + shake(f + 40, amp * 0.6))
        key(focus, 'location', f, focus_fn(f) if focus_fn else tp)
def dpos(z=0.95): return lambda f: wp(dr) + V(0, 0, z)
def dup_(z=0.95): return lambda f: wp(doug_r.upper) + V(0, 0, z)
if SHOT == 'C1':      # front, tracking the sassy walk
    shoot(V(DX + 0.25, 2.25, 0.95), V(DX + 0.22, 2.0, 0.95), dpos(0.95), 30, 3.2, focus_fn=lambda f: wp(dr) + V(0, -0.3, 0.9))
elif SHOT == 'C2':    # ground-level wide: Ricky sprints in and grabs
    shoot(V(-1.0, 1.55, 0.22), V(-0.85, 1.7, 0.24), V(-0.35, DY + 0.2, 0.75), 20, 4.0, amp=0.015)
elif SHOT == 'C3':    # punch-in close-up: arm fling, singing face
    shoot(V(0.95, 2.45, 0.95), V(0.88, 2.55, 0.97), V(0.28, DY, 1.42), 26, 2.8, amp=0.018)
elif SHOT == 'C4':    # over Ricky's shoulder: Doug turns, grabs the strap
    shoot(V(-1.75, 2.55, 1.15), V(-1.7, 2.65, 1.12), V(0.25, DY, 0.95), 24, 3.5)
elif SHOT == 'C5':    # SLOW-MO low angle behind Ricky, focus on Doug (Ricky soft in the foreground)
    shoot(V(TR[0] - 0.42, DY - 0.78, 0.3), V(TR[0] - 0.22, DY - 1.0, 0.33), V(TD[0] - 0.12, DY, 1.05), 22, 2.4, amp=0.006,
          focus_fn=lambda f: V(TD[0], DY, 1.0))
elif SHOT == 'C6':    # SLOW-MO waist-level close on the giling + arm whip
    shoot(V(TD[0] - 1.3, DY - 1.25, 0.8), V(TD[0] - 1.15, DY - 1.35, 0.85), dup_(0.6), 24, 2.6, amp=0.006)
elif SHOT == 'C7':    # 3/4 front of Doug: vogue hands + kembot, Ricky at the edge
    shoot(V(-0.85, 1.85, 1.1), V(-0.75, 1.95, 1.08), V(0.05, DY, 0.85), 22, 3.2, focus_fn=lambda f: wp(dr) + V(0, 0, 0.9))
elif SHOT == 'C8':    # Ricky's POV: fist pumps + giling straight at us
    shoot(V(TR[0] - 0.55, DY - 0.5, 1.38), V(TR[0] - 0.45, DY - 0.45, 1.35), V(TD[0] - 0.25, DY, 0.85), 24, 3.0, amp=0.014,
          focus_fn=lambda f: V(TD[0] - 0.2, DY, 0.9))
elif SHOT == 'C9':    # side-on wide: synchronized tug + hip thrusts
    shoot(V(-0.1, 0.75, 0.85), V(-0.1, 0.9, 0.85), V(-0.1, DY, 0.72), 17, 4.5)
elif SHOT == 'C10':   # reverse, low behind Doug looking at Ricky
    shoot(V(TD[0] + 1.0, DY + 0.85, 0.5), V(TD[0] + 0.9, DY + 0.75, 0.52), V(TR[0] + 0.1, DY, 0.75), 20, 3.5, amp=0.014)
elif SHOT == 'C11':   # low, close: the huge pull
    shoot(V(TD[0] + 1.25, DY - 1.55, 0.32), V(TD[0] + 1.15, DY - 1.45, 0.32), V(TD[0] - 0.5, DY, 0.8), 18, 4.0, amp=0.02)
elif SHOT == 'C12':   # high angle: Ricky falls, Doug lunges and yanks
    shoot(V(SITX + 0.75, DY - 1.35, 2.35), V(SITX + 0.7, DY - 1.2, 2.25), V(SITX + 0.65, DY, 0.35), 22, 4.0)
elif SHOT == 'C13':   # close-up: Ricky cringing
    fc = V(SITX, DY, 0.0) + V(0, 0, ricky_r.base - 0.38 + R_EZ)
    shoot(fc + V(1.0, -0.38, 0.14), fc + V(0.9, -0.34, 0.12), fc + V(0, 0.02, -0.06), 28, 2.8, amp=0.01, focus_fn=lambda f: fc + V(0.2, 0, 0))
elif SHOT == 'C14':   # front, tracking: grooves toward us again (loop)
    shoot(V(DX + 0.25, 3.05, 0.95), V(DX + 0.25, 2.25, 0.95), dpos(0.95), 30, 3.2, focus_fn=lambda f: wp(dr) + V(0, -0.3, 0.9))
scene.frame_set(f0)
FR = FR or f'{f0}-{f1}'
render(480)
