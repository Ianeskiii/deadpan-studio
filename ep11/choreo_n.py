# ============================================================ NEW SEGMENTS (global frames 481-750; spliced into the edit)
def combo(*Ls):
    def L(f):
        u, r_, bx, by = V(0, 0, 0), V(0, 0, 0), 0.0, 0.0
        for l in Ls:
            a_, b_, (x_, y_) = l(f); u += a_; r_ += b_; bx += x_; by += y_
        return u, r_, (bx, by)
    return L
def sing(f0, f1, step=7):
    for k, f in enumerate(range(f0, f1 + 1, step)): mouth_open(doug, f, (0.7, 0.2, 0.9, 0.35)[k % 4])
def eyes_r(f, x, z):
    for e in ricky['eyes']: key(e, 'rotation_euler', f, Euler((D(x), 0, D(z))))
burglar = {'N': ((-0.2, -0.36, 0.56), ('auto', (-1, 0.3, 0))), 'P': ((0.22, -0.38, 0.62), ('auto', (1, 0.3, 0)))}
stand_hp = lambda f: ST(doug_r, f, (0, 0, -0.02), (4, 0, 0), 1.0, hp2, 'stand')

# ---- N1 (481-510): Ricky sneaks in like a cartoon burglar, shifty eyes; Doug grooves in the background
doug_r.walk(481, 510, (DX, 4.75), (DX, 4.25), 0, steps=2, arms=hp2, lean=6, bob=0.045, sway=4, bendfun=lambda ph: (0, 32 * math.sin(ph) * doug_r.SIDE))
ricky_r.walk(481, 510, (-3.05, 4.85), (-2.7, 4.72), 70, steps=2, arms=burglar, crouch=0.13, lean=16, bob=0.05, lift=0.11, sway=6)
for k, f in enumerate(range(481, 511, 8)): eyes_r(f, 0, (28, -28)[k % 2]); eyes_r(f + 5, 0, (28, -28)[k % 2])
brows(ricky, 481, -0.025, 22, RBZ)
ricky_smile.hide_render = True; ricky_smile.keyframe_insert('hide_render', frame=1)
# ---- N2 (511-540): close insert: Ricky's hands snatch the bag off Doug's hip; sly grin
doug_r.place(511, (DX, DY), 0)
run(doug_r, 511, 540, [stand_hp(511), stand_hp(540)], kembot(doug_r, 511, amp=32))
SNATCH = 516
ricky_r.place(511, (-0.72, DY), 90)
ricky_r.pose(511, up=(0, 0, -0.12), rot=(16, 0, 0), arms=burglar, legs=LEGS['brace']())
ricky_r.pose(SNATCH, up=(0, 0, -0.08), rot=(14, 0, 0), arms=grab_arms, legs=LEGS['brace']())
ricky_r.pose(SNATCH + 8, up=(0, 0, -0.06), rot=(-10, 0, 10), arms=hold_bag, legs=LEGS['brace']())
ricky_r.pose(540, up=(0, 0, -0.06), rot=(-8, 0, 14), arms=hold_bag, legs=LEGS['brace']())
eyes_r(511, 0, 0); eyes_r(SNATCH + 6, -4, -18)
brows(ricky, 511, -0.025, 22, RBZ)
ricky_smile.hide_render = False; ricky_smile.keyframe_insert('hide_render', frame=SNATCH + 4)
ricky['mouth'].hide_render = False; ricky['mouth'].keyframe_insert('hide_render', frame=1)
ricky['mouth'].hide_render = True; ricky['mouth'].keyframe_insert('hide_render', frame=SNATCH + 4)
# ---- N3a (541-555): Ricky bolts with the bag... the strap is still over Doug's shoulder -> yanked back
ricky_r.place(541, (-0.72, DY), 90); ricky_r.place(544, (-0.75, DY), -90)
ricky_r.walk(544, 551, (-0.78, DY), (-1.45, DY), -90, steps=2.5, arms=hold_bag, crouch=0.06, lean=22, bob=0.03, lift=0.09)
SNAP = 552
ricky_r.place(SNAP, (-1.42, DY), -90); ricky_r.place(555, (-1.3, DY), -80)
ricky_r.pose(SNAP, up=(0, 0, -0.04), rot=(-28, 0, 0), sq=1.05, arms=hold_bag, legs=LEGS['brace']())
ricky_r.pose(555, up=(0, 0, -0.08), rot=(-18, 0, 0), arms=hold_bag, legs=LEGS['brace']())
eyes_r(SNAP, -6, 0); lids(ricky, SNAP - 1, 26); lids(ricky, SNAP, 0)
ricky_smile.hide_render = True; ricky_smile.keyframe_insert('hide_render', frame=SNAP)
ricky['mouth'].hide_render = False; ricky['mouth'].keyframe_insert('hide_render', frame=SNAP)
mouth_open(ricky, SNAP - 1, 0.0); mouth_open(ricky, SNAP, 1.0)
doug_r.place(541, (DX, DY), 0)
run(doug_r, 541, 585, [stand_hp(541), stand_hp(585)], kembot(doug_r, 541, amp=34, twist=10))
# ---- N3b (556-585): close-up on Doug's face: eyes closed, singing, totally oblivious
sing(556, 585)
ricky_r.pose(570, up=(0, 0, -0.1), rot=(-22, 0, 0), arms=hold_bag, legs=LEGS['brace']())
ricky_r.pose(585, up=(0, 0, -0.1), rot=(-22, 0, 0), arms=hold_bag, legs=LEGS['brace']())
# ---- N4 (586-615): Ricky's confused face while Doug vogues + kembots
ricky_r.place(586, (TR[0] + 0.15, DY), 90)
for k, f in enumerate(range(586, 616, 10)):
    ricky_r.pose(f, up=(0, 0, -0.03), rot=(-6, 0, 10 * (1 if k % 2 else -1)), arms=hold_bag, legs=LEGS['stand']())
    eyes_r(f, -4, (14, -10, 18)[k % 3])
lids(ricky, 586, 26); mouth_open(ricky, 586, 0.25)
for i, bp in enumerate(ricky['brows']):
    key(bp, 'location', 586, V(bp.location.x, bp.location.y, RBZ[i] + (0.05 if i == 1 else -0.015)))
    key(bp, 'rotation_euler', 586, Euler((0, (-1 if i == 0 else 1) * D(-10 if i == 1 else 12), 0)))
doug_r.place(586, (0.35, DY), -90)
run(doug_r, 586, 615, [ST(doug_r, f, (0, 0, -0.02), (3, 0, 0), 1.0, (V1, V3, V2, V3)[k % 4], 'wide') for k, f in enumerate(range(586, 616, 7))],
    kembot(doug_r, 586, amp=34, twist=10, shift=0.05))
# ---- N5 (616-675): DANCE BREAK - both kembot in sync, Ricky dragged into the groove
N5 = 616; PH = 616 - 3     # keep the hip snaps on the music's beat after the splice
doug_r.place(N5, (0.45, DY), -90); ricky_r.place(N5, (-0.85, DY), 90)
wave_up = ((0.45, -0.1, D_EZ + 0.6), ('auto', (1, 0, 0)))
dN5 = [ST(doug_r, f, (0, 0, -0.04), (-6, 0, 0), 1.0, arms(N='pull', P=(wave_up if k % 2 == 0 else 'behind')), 'wide') for k, f in enumerate(range(N5, 676, 15))]
rN5 = [ST(ricky_r, f, (0, 0, -0.04), (-4, 0, 0), 1.0, arms(N='pull', P='pull'), 'wide') for f in range(N5, 676, 15)]
run(doug_r, N5, 675, dN5, kembot(doug_r, PH, amp=36, twist=10, shift=0.05))
run(ricky_r, N5, 675, rN5, kembot(ricky_r, PH, amp=26, twist=8, shift=0.04))
sing(N5, 675)
brows(ricky, N5, -0.02, 16, RBZ); lids(ricky, N5, 30)
# ---- N6 (676-705): faces mid-tug: Doug blissfully singing (a), Ricky straining (b)
N6 = 676
doug_r.place(N6, TD, -90); ricky_r.place(N6, TR, 90)
dN6, rN6 = [], []
for k, f in enumerate(range(N6, 706, 15)):
    m = f + 7
    dN6 += [ST(doug_r, f, (0, 0, -0.16), (-32, 0, 0), 0.96, arms(N='pull_hi', P='pull_hi'), 'brace_w'),
            ST(doug_r, m, (0, 0, -0.1), (-25, 0, 4), 1.03, arms(N='pull', P='pull'), 'brace_w')]
    rN6 += [ST(ricky_r, f, (0, 0, -0.14), (-26, 0, 0), 0.96, arms(N='pull_hi', P='pull_hi'), 'brace'),
            ST(ricky_r, m, (0, 0, -0.08), (-18, 0, 0), 1.03, arms(N='pull', P='pull'), 'brace')]
run(doug_r, N6, 705, dN6, combo(thrust(doug_r, N6 - 9, amp=26), kembot(doug_r, N6 - 9, amp=18)))
run(ricky_r, N6, 705, rN6, thrust(ricky_r, N6 - 9, amp=14))
sing(N6, 705)
brows(ricky, N6, -0.03, 24, RBZ); lids(ricky, N6, 70); mouth_open(ricky, N6, 0.8)
# ---- N7 (706-750): victory kembot with the bag held high; Ricky cringing on the ground behind
N7 = 706
doug_r.place(N7, (0.6, DY + 0.25), -25)
bag_up = ((0.4, -0.05, D_EZ + 0.62), ('auto', (1, 0, 0)))
dN7 = [ST(doug_r, f, (0, 0, -0.03), (2, 0, 0), 1.0, arms(N='hp', P=bag_up), 'wide') for f in range(N7, 751, 15)]
run(doug_r, N7, 750, dN7, kembot(doug_r, N7, amp=38, twist=12, shift=0.055))
sing(N7, 750); lids(doug, N7, 40)
ricky_r.place(N7, (SITX, DY), 90)
for k, f in enumerate(range(N7, 751, 8)):
    ricky_r.pose(f, up=(0, 0, -0.38 - 0.015 * (k % 2)), rot=(-10, 0, -18 + 6 * (k % 2)), arms=shield, legs=LEGS['sit']())
lids(ricky, N7, 95); mouth_open(ricky, N7, 0.9)

