# ============================================================ v2 additions to the cafe (same set, props only)
exec(open(os.path.join(HERE, 'set12.py')).read())
# pickup spot at the near end of the counter, with a little sign
PICK_Y = -0.72
sgn = empty('pickup_sign', (0.0, PICK_Y - 0.33, CT))
for sx in (-1, 1):
    b_ = box('sign_leg', (0.012, 0.012, 0.16), (sx * 0.07, 0, 0.075), C_['wood_dk'], 0.002, sgn)
pb = box('sign_board', (0.2, 0.012, 0.1), (0, 0, 0.12), C_['board'], 0.004, sgn)
_t = text('PICK UP', 0.034, (0, -0.008, 0.108), C_['chalk_y'], extrude=0.0, parent=sgn)
sgn.rotation_euler = (0, 0, D(-25))
# coffee stream for the espresso pour
stream = cyl('coffee_stream', 0.0055, 0.06, (1.705, 0.18, CT + 0.17), mat('espresso', hexc('#3b2212'), 0.25, 0.1))
stream.hide_render = True
crema = cyl('crema', 0.044, 0.004, (0, 0, 0.062), mat('crema', hexc('#b5793f'), 0.35), parent=cup)
cup_lids = [bpy.data.objects['cup_lid'], bpy.data.objects['cup_lid2']]
LID_Z = [o.location.z for o in cup_lids]
