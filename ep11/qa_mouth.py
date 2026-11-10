# generic per-shot geometric QA (works for v5 and v6): mouth visibility, screen direction, camera side
import json as _json
from bpy_extras.object_utils import world_to_camera_view as _w2c
_res = {'shot': SHOT, 'frames': 0, 'doug_mouth_facing': 0, 'doug_mouth_visible': 0, 'ricky_mouth_facing': 0, 'ricky_mouth_visible': 0,
        'both_in_view': 0, 'ricky_left_of_doug': 0, 'cam_front_side': 0}
def _vis(obj, body_root, cpos, dg):
    p = obj.matrix_world.translation; co = _w2c(scene, cam, p)
    if not (0 < co.x < 1 and 0 < co.y < 1 and co.z > 0): return None
    fwd = (body_root.matrix_world.to_3x3() @ V(0, -1, 0)).normalized()
    if fwd.dot((cpos - p).normalized()) < 0.25: return None          # face turned away: not expected to be visible
    d = (p - cpos); dist = d.length
    hit, loc, nrm, idx, ob, mtx = scene.ray_cast(dg, cpos, d.normalized(), distance=dist + 0.05)
    return bool(hit and (ob.name == obj.name or (loc - cpos).length >= dist - 0.012))
for _f in range(f0, f1 + 1):
    scene.frame_set(_f); dg = bpy.context.evaluated_depsgraph_get(); cpos = cam.matrix_world.translation.copy()
    _res['frames'] += 1
    for who, C, up in (('doug', doug, (doug_r.upper if 'doug_r' in globals() else dr)), ('ricky', ricky, (ricky_r.upper if 'ricky_r' in globals() else rr))):
        v = _vis(C['mouth'], up, cpos, dg)
        if v is not None:
            _res[who + '_mouth_facing'] += 1; _res[who + '_mouth_visible'] += int(v)
    a, b = _w2c(scene, cam, dr.matrix_world.translation + V(0, 0, 0.8)), _w2c(scene, cam, rr.matrix_world.translation + V(0, 0, 0.6))
    if 0 < a.x < 1 and 0 < b.x < 1 and a.z > 0 and b.z > 0:
        _res['both_in_view'] += 1; _res['ricky_left_of_doug'] += int(b.x < a.x)
    _res['cam_front_side'] += int(cpos.y < min(dr.matrix_world.translation.y, rr.matrix_world.translation.y) - 0.2)
open(os.path.join(OUT, f'qa_{SHOT}.json'), 'w').write(_json.dumps(_res))
print('QA', _json.dumps(_res))
