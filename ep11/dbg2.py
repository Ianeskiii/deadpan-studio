import sys
sys.argv = ['x', 'E3', '/tmp/x', '--still', '1']
src = open('build11e.py').read().split('# ---------------------------------------------------------------- bag + strap')[0]
exec(compile(src, 'b', 'exec'))
for f in (136, 140, 150, 160):
    scene.frame_set(f)
    print(f, 'hand', [round(v, 2) for v in ricky_r.hand['P'].matrix_world.translation], 'root', [round(v, 2) for v in rr.location], round(math.degrees(rr.rotation_euler.z)))
