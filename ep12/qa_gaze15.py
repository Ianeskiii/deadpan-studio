rows = []
for f in range(F_CALL, F_LIFT1 + 1):
    scene.frame_set(f)
    pv = doug['eyes'][0]; P = pv.matrix_world.translation; d = (pv.matrix_world.to_3x3() @ V(0, -1, 0)).normalized()
    ang = lambda Q: math.degrees(d.angle((Q - P).normalized()))
    rows.append((f, ang(cup_pt()), ang(bari_face())))
def phase(r): return 'CUP' if r[1] + 3 < r[2] else ('BARISTA' if r[2] + 3 < r[1] else 'between')
cur = None; segs = []
for r in rows:
    p = phase(r)
    if p != cur: segs.append([p, r[0], r[0]]); cur = p
    else: segs[-1][2] = r[0]
for p, a, b in segs: print(f'GAZE {p:8s} frames {a}-{b}  ({(a-1)/30:.2f}s-{b/30:.2f}s, {(b-a+1)/30:.2f}s)')
print('GAZE head turned to her by', F_NOTICE1, 'smile', F_SMILE0, '-', F_SMILE1, 'shots', SHOTS)
# hand / cup contact
for f in range(F_TOUCH - 2, F_LIFT1 + 6, 2):
    scene.frame_set(f); h = wp(doug_r.hand['N']); c = cup.matrix_world.translation
    hz = h - c; print(f'GRIP f{f} hand-cup centre dist {hz.length:.3f} m  horiz {math.hypot(hz.x, hz.y):.3f}  dz {hz.z:+.3f}')
