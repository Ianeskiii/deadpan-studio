# per frame: is Doug's eye axis on the cup or on the barista's face?  (angles in degrees)
rows = []
for f in range(F_CALL, F_TAKE + 1):
    scene.frame_set(f)
    pv = doug['eyes'][0]; P = pv.matrix_world.translation; d = (pv.matrix_world.to_3x3() @ V(0, -1, 0)).normalized()
    ang = lambda Q: math.degrees(d.angle((Q - P).normalized()))
    rows.append((f, ang(cup_pt()), ang(bari_face()), [b for b in (F_D3, F_YEAH) if b == f]))
def phase(r): return 'CUP' if r[1] + 3 < r[2] else ('BARISTA' if r[2] + 3 < r[1] else 'between')
cur = None; segs = []
for r in rows:
    p = phase(r)
    if p != cur: segs.append([p, r[0], r[0]]); cur = p
    else: segs[-1][2] = r[0]
for p, a, b in segs: print(f'{p:8s} frames {a}-{b}  ({(a-1)/30:.2f}s-{b/30:.2f}s, {(b-a+1)/30:.2f}s)')
print('line starts', F_D3, f'({(F_D3-1)/30:.2f}s)', ' Yeah', F_YEAH, f'({(F_YEAH-1)/30:.2f}s)', ' head turn up', F_HEAD0, '-', F_HEAD1)
