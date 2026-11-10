# full-timeline QA for v6: blinks, gaze accuracy, lip-sync correlation
import json as _json
out = {}
def _lid(objs): return math.degrees(objs[0].rotation_euler.x)
blinks = {'doug': 0, 'ricky': 0}; prev = {'doug': False, 'ricky': False}
gaze_err = {'doug': [], 'ricky': []}; mouth = {'doug': [], 'ricky': []}; env = {'doug': [], 'ricky': []}
for f in range(1, 481):
    scene.frame_set(f)
    for who, L in (('doug', D_LIDS), ('ricky', R_LIDS)):
        closed = _lid(L) > 85
        if closed and not prev[who]: blinks[who] += 1
        prev[who] = closed
    for who, C, tf in (('ricky', ricky, r_target), ('doug', doug, d_target)):
        if who == 'doug' and not (REACT0 + 8 <= f < REACT1 - 5): continue
        T = tf(f)
        for pv in C['eyes']:
            g = (pv.matrix_world.to_3x3() @ V(0, -1, 0)).normalized(); d = (T - pv.matrix_world.translation).normalized()
            gaze_err[who].append(math.degrees(g.angle(d)))
    for who, C in (('doug', doug), ('ricky', ricky)):
        s = speech(who, f)
        if s > 0 or (who == 'ricky' and any(LINES[k] <= f < LINES[k] + 40 for k in ('g1', 'g2', 'g3', 'g4'))) or (who == 'doug' and LINES['d1'] <= f < LINES['d1'] + 30):
            sc = C['mouth'].scale; mouth[who].append(sc.x if who == 'doug' else sc.z); env[who].append(s)
for who in ('doug', 'ricky'):
    out[who] = {'blink_closures': blinks[who],
                'gaze_err_deg_median': round(float(np.median(gaze_err[who])), 1) if gaze_err[who] else None,
                'gaze_err_deg_p90': round(float(np.percentile(gaze_err[who], 90)), 1) if gaze_err[who] else None,
                'lipsync_corr': round(float(np.corrcoef(mouth[who], env[who])[0, 1]), 3) if len(env[who]) > 3 else None}
open(os.path.join(OUT, 'qa_full.json'), 'w').write(_json.dumps(out)); print('QAFULL', _json.dumps(out))
