import sys, os
sys.argv = ['x', 'T', os.path.abspath('bendtest'), '--still', '1', '--samples', '6', '--pct', '40']
exec(open('../tubetown/lib.py').read())
tina['root'].location = (-50, 0, 0)
body = bpy.data.objects['doug_body']
me = body.data
# subdivide along height for smooth bending
import bmesh
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.3], cuts=12, use_grid_fill=True)
bm.to_mesh(me); bm.free()
org = empty('bend_org', (0, 0, doug['zc'] + 0.15), doug['root'])
mods = []
for axis in ('X', 'Y'):
    m = body.modifiers.new('bend' + axis, 'SIMPLE_DEFORM'); m.deform_method = 'BEND'; m.deform_axis = axis
    m.origin = org; m.limits = (0.0, 0.5); mods.append(m)
area('k', (0, -3, 3), (D(45), 0, 0), 300, (1, 1, 1), (3, 3))
cam.location = (0, -3.2, 1.0); target.location = (0, 0, 0.9); cam_data.lens = 35; focus.location = (0, 0, 0.9)
r = scene.render; r.engine = 'CYCLES'; scene.cycles.samples = 6; r.resolution_x, r.resolution_y, r.resolution_percentage = 720, 1280, 40
scene.cycles.device = 'CPU'
for i, (ax, ay) in enumerate(((0, 0), (35, 0), (-35, 0), (0, 35))):
    mods[0].angle = D(ax); mods[1].angle = D(ay)
    r.filepath = os.path.abspath(f'bendtest/b{i}.png'); bpy.ops.render.render(write_still=True)
print('ok')
