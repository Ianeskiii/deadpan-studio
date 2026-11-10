# ---- QA: mouth visibility from the shot camera when the face is turned to camera, camera-side, text facing
from bpy_extras.object_utils import world_to_camera_view
import json as _j
res = {'doug': [0, 0], 'bari': [0, 0]}; hidden = {'doug': [], 'bari': []}; txt = []
dg = bpy.context.evaluated_depsgraph_get()
for f in range(f0, f1 + 1):
    scene.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
    cp = cam.matrix_world.translation.copy()
    for who, C, rig in (('doug', doug, doug_r), ('bari', bari, bari_r)):
        m = C['mouth']; mp = m.matrix_world.translation.copy()
        if who == 'bari' and m.hide_render: mp = bari_smile.matrix_world.translation.copy()
        fwd = (rig.upper.matrix_world.to_3x3() @ V(0, -1, 0)).normalized(); to_c = (cp - mp).normalized()
        ang = math.degrees(math.acos(max(-1, min(1, fwd.dot(to_c)))))
        co = world_to_camera_view(scene, cam, mp)
        if ang > 70 or not (0 < co.x < 1 and 0 < co.y < 1 and co.z > 0): continue
        if who == 'doug' and F_STOP + 4 <= f <= F_GO1: pass
        hit, loc, nrm, idx, ob, mw = scene.ray_cast(dg, cp, (mp - cp).normalized(), distance=(mp - cp).length + 0.02)
        ok = (not hit) or ob.name.startswith(('doug_mouth', 'bari_mouth', 'bari_smile', 'bsmile')) or (loc - mp).length < 0.03
        res[who][1] += 1; res[who][0] += ok
        if not ok: hidden[who].append((f, ob.name))
    if f >= TEXT_ON:
        cf = (cup.matrix_world.to_3x3() @ V(0, -1, 0)).normalized(); tc = (cp - cup.matrix_world.translation).normalized(); txt.append(math.degrees(math.acos(max(-1, min(1, cf.dot(tc))))))
from bpy_extras.object_utils import world_to_camera_view as _w
print('QA mouth visible (facing camera):', {k: f'{v[0]}/{v[1]}' for k, v in res.items()})
for k in hidden: print('hidden', k, hidden[k][:40])
print('cup text angle to camera median', round(float(np.median(txt)), 1))
